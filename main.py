from fastapi import FastAPI
from app.models import AskRequest, AskResponse, Source
from app.retrieval import DocumentRetriever
from app.sql_engine import answer_personal_query
from app.cache import SemanticCache
from app.router import classify_intent
from app.grounding import apply_grounding

app = FastAPI(title="AMYPO Local Database Question-Answering System")

# Loaded once, at startup
retriever = DocumentRetriever("data/documents.json")
cache = SemanticCache(retriever.vectorizer, similarity_threshold=0.85)


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/ask", response_model=AskResponse)
def ask(request: AskRequest):
    question = request.question
    intent = classify_intent(question)

    # ---------- Path 1: personal data (never cached) ----------
    if intent == "personal":
        if not request.user_id:
            return apply_grounding(None, [], 0.0)
        answer, source, confidence = answer_personal_query(question, request.user_id)
        sources = [Source(**source)] if source else []
        return apply_grounding(answer, sources, confidence)

    # ---------- Path 2: common/FAQ/course -> check cache first ----------
    cached = cache.lookup(question)
    if cached:
        return {
            "answer": cached["answer"],
            "sources": cached["sources"],
            "confidence": cached["confidence"],
        }

    # ---------- Path 3: cache miss -> vector search ----------
    results = retriever.search(question, top_k=1)
    if not results or results[0]["score"] < 0.05:
        return apply_grounding(None, [], 0.0)

    top = results[0]
    answer = f"According to {top['source']}: {top['snippet']}"
    sources = [Source(record_id=top["record_id"], snippet=top["snippet"])]
    confidence = min(top["score"] * 1.5, 0.99)

    result = apply_grounding(answer, sources, confidence)

    # Only cache confidently-grounded common answers
    if result["confidence"] >= 0.15:
        cache.store(question, result["answer"], result["sources"], result["confidence"])

    return result
