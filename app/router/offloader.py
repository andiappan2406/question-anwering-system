from typing import Dict, List, Optional
from app.router.schemas import (
    DatabaseOffloadTarget,
    DatabaseTargetType,
    DataPriority,
    RouteType,
    RouterInput,
)


class DatabaseRegistry:
    """
    Maintains available database endpoints, schema profiles, and access policies.
    """
    TARGET_PERSONAL_SQL = "db_personal_students_sql"
    TARGET_CAMPUS_VECTOR = "db_campus_knowledge_vector"
    TARGET_SEMANTIC_CACHE = "db_semantic_cache"

    @staticmethod
    def get_database_profile(target_id: str) -> Dict:
        profiles = {
            DatabaseRegistry.TARGET_PERSONAL_SQL: {
                "name": "Personal Relational Database",
                "engine": DatabaseTargetType.RELATIONAL_SQL,
                "tables": ["students", "attendance", "grades", "semesters"],
                "privacy_level": "confidential",
                "cacheable": False,
                "cost_weight": 0.5,
            },
            DatabaseRegistry.TARGET_CAMPUS_VECTOR: {
                "name": "Institutional Common Knowledge Vector Store",
                "engine": DatabaseTargetType.VECTOR_STORE,
                "collections": ["faq", "policies", "curriculum", "campus_guide"],
                "privacy_level": "public",
                "cacheable": True,
                "cost_weight": 1.0,
            },
            DatabaseRegistry.TARGET_SEMANTIC_CACHE: {
                "name": "Semantic QA Cache",
                "engine": DatabaseTargetType.CACHE,
                "privacy_level": "public",
                "cacheable": True,
                "cost_weight": 0.1,
            },
        }
        return profiles.get(target_id, {})


class DatabaseOffloadPlanner:
    """
    Determines and schedules the exact database offload targets for a given routing decision.
    Produces an ordered plan sorted by execution priority.
    """

    def plan_offload(
        self,
        route: RouteType,
        router_input: RouterInput,
        sql_subquery: Optional[str] = None,
        rag_subquery: Optional[str] = None,
        matched_fields: Optional[List[str]] = None,
    ) -> List[DatabaseOffloadTarget]:
        plan: List[DatabaseOffloadTarget] = []
        user_id = router_input.user_id

        if route == RouteType.SQL or route == RouteType.HYBRID:
            # SQL offload target (Critical/High priority: fetch user metrics first)
            sql_query_text = sql_subquery or router_input.sanitized_query
            plan.append(
                DatabaseOffloadTarget(
                    target_id=DatabaseRegistry.TARGET_PERSONAL_SQL,
                    engine_type=DatabaseTargetType.RELATIONAL_SQL,
                    sub_query=sql_query_text,
                    required_parameters={
                        "user_id": user_id,
                        "fields": matched_fields or [],
                    },
                    priority=DataPriority.CRITICAL if route == RouteType.SQL else DataPriority.HIGH,
                    estimated_cost=0.5,
                    cacheable=False,
                    privacy_level="confidential",
                )
            )

        if route == RouteType.RAG or route == RouteType.HYBRID:
            # Vector store offload target
            rag_query_text = rag_subquery or router_input.sanitized_query
            plan.append(
                DatabaseOffloadTarget(
                    target_id=DatabaseRegistry.TARGET_CAMPUS_VECTOR,
                    engine_type=DatabaseTargetType.VECTOR_STORE,
                    sub_query=rag_query_text,
                    required_parameters={
                        "top_k": 3 if route == RouteType.HYBRID else 2,
                    },
                    priority=DataPriority.HIGH if route == RouteType.RAG else DataPriority.MEDIUM,
                    estimated_cost=1.0,
                    cacheable=True,
                    privacy_level="public",
                )
            )

        # Ensure offload plan is sorted deterministically by Priority (1 = Critical, 4 = Low)
        plan.sort(key=lambda t: (t.priority.value, t.estimated_cost))
        return plan
