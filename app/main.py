import os
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from app.cache import SemanticCache
from app.db_manager import db_manager
from app.grounding import apply_grounding
from app.llm_engine import rephrase_answer, CHITCHAT_REPLIES
from app.models import AskRequest, AskResponse, Source
from app.placement_engine import (
    get_all_company_openings,
    get_student_skills_profile,
    suggest_openings_for_student,
    suggest_students_for_opening,
)
from app.retrieval import DocumentRetriever
from app.router import (
    ContextItem,
    DataPriority,
    DatabaseHealthStatus,
    DynamicQueryPayload,
    NeuroSymbolicRouter,
    RouteType,
    RouterInput,
    StructuredContextSorter,
    get_router,
)
from app.sql_engine import answer_personal_query

app = FastAPI(title="AMYPO Local Neuro-Symbolic Hybrid QA System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Singletons ────────────────────────────────────────────────────────────────
retriever = DocumentRetriever()
cache = SemanticCache(retriever.model, similarity_threshold=0.85)
router: NeuroSymbolicRouter = get_router()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_sources(items: List[ContextItem]) -> List[Source]:
    return [
        Source(
            record_id=item.source_id,
            snippet=item.snippet,
            priority=item.priority.value,
            relevance_score=item.relevance_score,
        )
        for item in items
    ]


def _make_context_item(
    source_id: str,
    target: str,
    snippet: str,
    score: float,
    priority: DataPriority,
) -> ContextItem:
    return ContextItem(
        source_id=source_id,
        database_target=target,
        snippet=snippet,
        relevance_score=score,
        priority=priority,
    )


# ── Health & Placement Endpoints ───────────────────────────────────────────────

@app.get("/api/v1/health")
def health():
    return {
        "status": "ok",
        "router": "neuro-symbolic",
        "retriever": "ready" if retriever.index is not None else "index_missing",
        "documents": len(retriever.documents),
        "database_engine": db_manager.active_engine_name,
        "database_dialect": db_manager.dialect.value,
    }


@app.get("/api/v1/database/status", response_model=DatabaseHealthStatus)
def database_status():
    """
    Returns live database health, connectivity status, active dialect (Supabase PostgreSQL / SQLite),
    roundtrip query latency, and record counts across institutional tables.
    """
    return db_manager.get_health_status()


@app.post("/api/v1/database/query")
def dynamic_database_query(payload: DynamicQueryPayload):
    """
    Versatile dynamic querying endpoint across authorized institutional tables.
    Supports equality filters, column projection, ordering, and pagination.
    """
    try:
        return db_manager.query_dynamic(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/database/sync")
def sync_database():
    """
    Synchronizes initial records from local SQLite data/students.db into
    PostgreSQL/Supabase if tables are newly created or empty.
    """
    try:
        db_manager.sync_seed_data_to_postgres()
        return {"status": "success", "message": "Database sync routine completed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync error: {e}")



@app.get("/api/v1/placement/openings")
def list_placement_openings():
    """Returns all verified company job openings and their skill/academic criteria."""
    openings = get_all_company_openings()
    return {"openings": openings, "total": len(openings)}


@app.get("/api/v1/placement/suggest-students")
def suggest_students_api(
    opening_id: Optional[str] = None,
    company: Optional[str] = None,
    role: Optional[str] = None,
    query: Optional[str] = None,
    department: Optional[str] = None,
    top_n: int = 5,
):
    """
    Ranks and suggests best matched students for a company opening to eliminate random recruitment.
    """
    search_term = query or opening_id or company or role or "Google"
    result = suggest_students_for_opening(search_term, top_n=top_n, department_filter=department)
    return result


@app.get("/api/v1/placement/suggest-roles")
def suggest_roles_api(student_id: str, top_n: int = 5):
    """
    Suggests suitable company openings for a student based on their skills and CGPA
    so they don't waste precious interview chances.
    """
    result = suggest_openings_for_student(student_id, top_n=top_n)
    return result


@app.get("/api/v1/placement/student-profile")
def student_skills_profile_api(student_id: str):
    """Returns a student's technical skills inventory, projects, and certifications."""
    profile = get_student_skills_profile(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"No student profile found for '{student_id}'.")
    return profile


# ── In-Memory Session Memory for Multi-Turn Continuity ────────────────────────
_SESSION_LAST_QUERY: dict = {}


# ── Main QA endpoint ───────────────────────────────────────────────────────────

@app.post("/api/v1/ask", response_model=AskResponse)
def ask(request: AskRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    session_key = request.session_id or request.user_id or "global"
    q_norm = question.lower().rstrip("?.! ")

    # Resolve multi-turn conversational ellipsis (e.g. "for me", "what about me", "mine")
    if q_norm in {"for me", "what about me", "and for me", "mine", "how about me", "tell me for me", "my details"}:
        prev_q = _SESSION_LAST_QUERY.get(session_key)
        if prev_q:
            question = f"{prev_q} for my profile"
    else:
        _SESSION_LAST_QUERY[session_key] = question

    router_input = RouterInput(
        raw_query=question,
        user_id=request.user_id,
        session_id=request.session_id,
    )
    decision = router.route(router_input)
    primary_route = decision.primary_route

    context_items: List[ContextItem] = []

    # ══════════════════════════════════════════════════════════════════════════
    # PATH 0: Chitchat / Greeting
    # ══════════════════════════════════════════════════════════════════════════
    if primary_route == RouteType.CHITCHAT:
        if request.use_llm:
            answer = rephrase_answer(question, "The user is saying hello or making small talk.", is_complex=False)
        else:
            answer = CHITCHAT_REPLIES[0]

        return AskResponse(
            answer=answer,
            sources=[],
            confidence=1.0,
            route=primary_route.value,
            offload_plan=[],
            reasoning_trace=decision.reasoning_trace + [
                "Detected conversational chitchat. Responding directly."
            ],
            execution_steps=decision.execution_steps,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # PATH 1: Personal SQL & Placement Skill Matching
    # ══════════════════════════════════════════════════════════════════════════
    elif primary_route == RouteType.SQL:
        q_lower = question.lower()
        is_opening_candidate_query = any(k in q_lower for k in [
            "suggest student", "suggest students", "recommend student", "recommend students",
            "candidates for", "students for", "who matches", "who is suitable", "best match for",
            "selection for company", "skill and role get match", "all company openings", "list openings",
            "what companies are hiring", "campus drives", "active openings", "student suggestion",
            "student suggestions"
        ]) or (
            any(comp in q_lower for comp in ["google", "microsoft", "amazon", "zoho", "bosch", "l&t", "tcs", "razorpay"])
            and any(w in q_lower for w in ["student", "students", "candidate", "candidates", "recommend", "suggest", "select", "hire", "opening", "role"])
        )

        if not request.user_id and not is_opening_candidate_query:
            return AskResponse(
                answer="Please select or provide your Student ID (e.g., U101, S101) or Staff ID (e.g., T101, T102) in the top bar to access your personal academic records or faculty records.",
                sources=[],
                confidence=0.90,
                route=primary_route.value,
                offload_plan=[t.model_dump() for t in decision.offload_plan],
                reasoning_trace=decision.reasoning_trace + [
                    "Personal query identified; requesting user authentication / ID selection (Student or Staff)."
                ],
                execution_steps=decision.execution_steps,
            )

        answer, source_dict, confidence = answer_personal_query(question, request.user_id or "")

        if answer and request.use_llm and not is_opening_candidate_query:
            rephrased = rephrase_answer(question, answer)
            if rephrased and len(rephrased.strip()) >= 30:
                answer = rephrased

        if source_dict:
            rec_id = source_dict.get("record_id", "")
            if rec_id.startswith("placement:"):
                target = "db_placement_openings_sql"
            elif rec_id.startswith("staff:"):
                target = "db_personal_staff_sql"
            else:
                target = "db_personal_students_sql"

            context_items.append(_make_context_item(
                source_id=rec_id or f"user:{request.user_id}",
                target=target,
                snippet=source_dict.get("snippet", answer or ""),
                score=confidence,
                priority=DataPriority.CRITICAL,
            ))

        sorted_batch = StructuredContextSorter.create_sorted_batch(
            query=question, route=primary_route, items=context_items,
        )
        sources = _build_sources(sorted_batch.items)
        grounded = apply_grounding(answer, sources, confidence)

        return AskResponse(
            answer=grounded["answer"],
            sources=sources,
            confidence=grounded["confidence"],
            route=primary_route.value,
            offload_plan=[t.model_dump() for t in decision.offload_plan],
            reasoning_trace=decision.reasoning_trace,
            execution_steps=decision.execution_steps,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # PATH 2: Hybrid (SQL + Vector)
    # ══════════════════════════════════════════════════════════════════════════
    elif primary_route == RouteType.HYBRID:
        sql_answer, sql_source, sql_conf = None, None, 0.0

        if request.user_id:
            sql_answer, sql_source, sql_conf = answer_personal_query(question, request.user_id)
            if sql_source:
                is_staff = sql_source.get("record_id", "").startswith("staff:")
                context_items.append(_make_context_item(
                    source_id=sql_source.get("record_id", f"user:{request.user_id}"),
                    target="db_personal_staff_sql" if is_staff else "db_personal_students_sql",
                    snippet=sql_source.get("snippet", sql_answer or ""),
                    score=sql_conf,
                    priority=DataPriority.CRITICAL,
                ))
        else:
            decision.reasoning_trace.append(
                "Hybrid query: User ID was not specified; answering using public campus policy records."
            )

        # Vector knowledge retrieval
        rag_target = next((t for t in decision.offload_plan if "vector" in t.target_id), None)
        rag_query = rag_target.sub_query if rag_target and len(rag_target.sub_query.split()) >= 3 else question
        vector_results = retriever.search(rag_query, top_k=3)
        if not vector_results and rag_query != question:
            vector_results = retriever.search(question, top_k=3)

        for res in vector_results:
            context_items.append(_make_context_item(
                source_id=res["record_id"],
                target="db_campus_knowledge_vector",
                snippet=res["snippet"],
                score=res["score"],
                priority=DataPriority.HIGH,
            ))

        sorted_batch = StructuredContextSorter.create_sorted_batch(
            query=question, route=primary_route, items=context_items,
        )
        sources = _build_sources(sorted_batch.items)
        combined_snippets = " | ".join(item.snippet for item in sorted_batch.items)

        if request.use_llm and combined_snippets:
            answer = rephrase_answer(question, combined_snippets, is_complex=True)
        elif sql_answer:
            policy = vector_results[0]["snippet"] if vector_results else "institutional guidelines"
            answer = f"Personal: {sql_answer}\nPolicy: {policy}"
        else:
            answer = combined_snippets or None

        confidence = max(sql_conf, vector_results[0]["score"] if vector_results else 0.0)
        grounded = apply_grounding(answer, sources, confidence)

        return AskResponse(
            answer=grounded["answer"],
            sources=sources,
            confidence=grounded["confidence"],
            route=primary_route.value,
            offload_plan=[t.model_dump() for t in decision.offload_plan],
            reasoning_trace=decision.reasoning_trace,
            execution_steps=decision.execution_steps,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # PATH 3: Vector RAG / FAQ / Cache
    # ══════════════════════════════════════════════════════════════════════════
    else:
        # 1. Check semantic cache first
        cached = cache.lookup(question, request.use_llm)
        if cached:
            return AskResponse(
                answer=cached["answer"],
                sources=[Source(**s) if isinstance(s, dict) else s for s in cached["sources"]],
                confidence=cached["confidence"],
                route="cache_hit",
                offload_plan=[t.model_dump() for t in decision.offload_plan],
                reasoning_trace=["Retrieved from semantic cache."],
                execution_steps=decision.execution_steps,
            )

        # 2. Vector search (min_score=0.30 enforced inside retriever.search)
        results = retriever.search(question, top_k=2)
        if not results:
            grounded = apply_grounding(None, [], 0.0)
            return AskResponse(
                answer=grounded["answer"],
                sources=[],
                confidence=grounded["confidence"],
                route=primary_route.value,
                offload_plan=[t.model_dump() for t in decision.offload_plan],
                reasoning_trace=decision.reasoning_trace + [
                    "No sufficiently similar documents found in knowledge base."
                ],
                execution_steps=decision.execution_steps,
            )

        for res in results:
            context_items.append(_make_context_item(
                source_id=res["record_id"],
                target="db_campus_knowledge_vector",
                snippet=res["snippet"],
                score=res["score"],
                priority=DataPriority.HIGH,
            ))

        sorted_batch = StructuredContextSorter.create_sorted_batch(
            query=question, route=primary_route, items=context_items,
        )
        sources = _build_sources(sorted_batch.items)

        top = results[0]
        if request.use_llm:
            answer = rephrase_answer(question, top["snippet"], is_complex=False)
        else:
            answer = f"According to {top['source']}: {top['snippet']}"

        confidence = min(top["score"], 0.99)
        grounded = apply_grounding(answer, sources, confidence)

        # 3. Cache successful answers
        if grounded["confidence"] >= 0.40:
            cache.store(question, grounded["answer"], sources, grounded["confidence"], request.use_llm)

        return AskResponse(
            answer=grounded["answer"],
            sources=sources,
            confidence=grounded["confidence"],
            route=primary_route.value,
            offload_plan=[t.model_dump() for t in decision.offload_plan],
            reasoning_trace=decision.reasoning_trace,
            execution_steps=decision.execution_steps,
        )
