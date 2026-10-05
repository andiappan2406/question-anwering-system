from app.router.engine import NeuroSymbolicRouter, get_router
from app.router.neuro import NeuroRouterEngine
from app.router.offloader import DatabaseOffloadPlanner, DatabaseRegistry
from app.router.schemas import (
    CandidateMatchResult,
    CompanyOpeningSchema,
    ContextItem,
    DatabaseConnectionConfig,
    DatabaseDialect,
    DatabaseHealthStatus,
    DatabaseOffloadTarget,
    DatabaseTargetType,
    DataPriority,
    DynamicQueryPayload,
    PlacementMatchBatchResponse,
    RecommendedOpeningResult,
    RouterInput,
    RoutingDecision,
    RouteType,
    SortedContextBatch,
    StudentPlacementProfileSchema,
    StudentRoleRecommendationResponse,
)
from app.router.sorter import StructuredContextSorter
from app.router.symbolic import SymbolicGatekeeper


def classify_intent(question: str) -> str:
    """
    Backward-compatible helper function mapping new RouteType to legacy strings:
    - 'personal_sql' -> 'personal'
    - 'vector_rag' -> 'common'
    - 'hybrid' -> 'complex'
    """
    router = get_router()
    decision = router.route(question)
    if decision.primary_route == RouteType.SQL:
        return "personal"
    elif decision.primary_route == RouteType.HYBRID:
        return "complex"
    return "common"


__all__ = [
    "NeuroSymbolicRouter",
    "get_router",
    "classify_intent",
    "RouterInput",
    "RoutingDecision",
    "RouteType",
    "DatabaseOffloadTarget",
    "DatabaseTargetType",
    "DataPriority",
    "ContextItem",
    "SortedContextBatch",
    "SymbolicGatekeeper",
    "NeuroRouterEngine",
    "DatabaseOffloadPlanner",
    "DatabaseRegistry",
    "StructuredContextSorter",
    "DatabaseDialect",
    "DatabaseConnectionConfig",
    "DatabaseHealthStatus",
    "CompanyOpeningSchema",
    "StudentPlacementProfileSchema",
    "CandidateMatchResult",
    "PlacementMatchBatchResponse",
    "RecommendedOpeningResult",
    "StudentRoleRecommendationResponse",
    "DynamicQueryPayload",
]

