from typing import List, Optional, Union
from app.router.neuro import NeuroRouterEngine
from app.router.offloader import DatabaseOffloadPlanner, DatabaseRegistry
from app.router.schemas import (
    DatabaseOffloadTarget,
    DataPriority,
    RouteType,
    RouterInput,
    RoutingDecision,
)
from app.router.sorter import StructuredContextSorter
from app.router.symbolic import SymbolicGatekeeper


class NeuroSymbolicRouter:
    """
    Production-grade Neuro-Symbolic Router orchestrating deterministic linguistic
    gates, SLM reasoning, database offload planning, and structured I/O sorting.
    """

    def __init__(
        self,
        symbolic_confidence_threshold: float = 0.90,
        enable_slm_neuro_fallback: bool = True,
    ):
        self.symbolic = SymbolicGatekeeper()
        self.neuro = NeuroRouterEngine()
        self.planner = DatabaseOffloadPlanner()
        self.sorter = StructuredContextSorter()
        self.symbolic_threshold = symbolic_confidence_threshold
        self.enable_slm = enable_slm_neuro_fallback

    def route(self, user_input: Union[str, RouterInput], user_id: Optional[str] = None) -> RoutingDecision:
        """
        Main routing function taking either a raw query string or a structured RouterInput.
        """
        if isinstance(user_input, str):
            router_input = RouterInput(raw_query=user_input, user_id=user_id)
        else:
            router_input = user_input

        query = router_input.sanitized_query
        reasoning_trace: List[str] = []

        # Step 1: Symbolic Gatekeeper Pass
        symbolic_res = self.symbolic.analyze(query)
        primary_route = symbolic_res["primary_route"]
        confidence = symbolic_res["confidence"]
        intent_summary = symbolic_res["intent_summary"]
        sql_sub = symbolic_res["sql_subquery"]
        rag_sub = symbolic_res["rag_subquery"]
        matched_fields = symbolic_res["matched_personal_fields"]
        reasoning_trace.extend(symbolic_res["reasoning"])

        is_neuro_verified = False

        # Step 2: Neuro SLM Fallback/Refinement for ambiguous or borderline queries
        if self.enable_slm and (confidence < self.symbolic_threshold or primary_route == RouteType.UNKNOWN):
            reasoning_trace.append(
                f"Symbolic confidence {confidence:.2f} < {self.symbolic_threshold:.2f}. Invoking local SLM neuro reasoning..."
            )
            slm_res = self.neuro.classify_with_slm(query)
            if slm_res:
                primary_route = slm_res["route"]
                confidence = max(confidence, slm_res["confidence"])
                intent_summary = slm_res["intent_summary"]
                sql_sub = slm_res.get("sql_subquery") or sql_sub
                rag_sub = slm_res.get("rag_subquery") or rag_sub
                is_neuro_verified = True
                reasoning_trace.append(
                    f"SLM ({slm_res.get('model_used')}) verified route: {primary_route.value} (confidence={confidence:.2f})"
                )
            else:
                reasoning_trace.append("SLM unavailable or timed out; maintaining symbolic routing decision.")

        # Step 3: Database Offloading & Dispatch Plan
        offload_plan = self.planner.plan_offload(
            route=primary_route,
            router_input=router_input,
            sql_subquery=sql_sub,
            rag_subquery=rag_sub,
            matched_fields=matched_fields,
        )

        # Step 4: Execution Steps Assembly
        execution_steps = self._build_execution_steps(primary_route, offload_plan)

        return RoutingDecision(
            primary_route=primary_route,
            confidence=round(confidence, 2),
            intent_summary=intent_summary,
            offload_plan=offload_plan,
            execution_steps=execution_steps,
            reasoning_trace=reasoning_trace,
            is_neuro_verified=is_neuro_verified,
        )

    def _build_execution_steps(self, route: RouteType, plan: List[DatabaseOffloadTarget]) -> List[str]:
        steps = []
        if route == RouteType.SQL:
            steps.append("1. Validate user permissions & parameters for Personal Relational SQL DB.")
            steps.append("2. Offload query to Text-to-SQL Engine with self-correction.")
            steps.append("3. Format database rows into structured personal context.")
        elif route == RouteType.RAG:
            steps.append("1. Check Semantic Cache for identical/similar knowledge queries.")
            steps.append("2. Offload query to Institutional Common Knowledge Vector Store.")
            steps.append("3. Retrieve Top-K grounded document chunks.")
        elif route == RouteType.HYBRID:
            steps.append("1. Offload personal sub-query to Personal Relational SQL DB (Priority: HIGH).")
            steps.append("2. Simultaneously offload policy sub-query to Common Knowledge Vector DB.")
            steps.append("3. Sort and fuse multi-source contexts into prioritized synthesis batch.")
            steps.append("4. Pass merged contexts to Synthesis SLM for grounded comparative answer.")
        else:
            steps.append("1. Process direct response or route to conversational fallback.")
        return steps


# Global singleton router instance
_router_instance: Optional[NeuroSymbolicRouter] = None


def get_router() -> NeuroSymbolicRouter:
    global _router_instance
    if _router_instance is None:
        _router_instance = NeuroSymbolicRouter()
    return _router_instance
