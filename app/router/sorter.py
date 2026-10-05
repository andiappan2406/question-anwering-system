from typing import List, Optional
from app.router.schemas import ContextItem, DataPriority, RouteType, SortedContextBatch


class StructuredContextSorter:
    """
    Guarantees deterministic, prioritized ordering of input and output data packets.
    Sorting hierarchy:
    1. Priority Rank (CRITICAL=1 -> HIGH=2 -> MEDIUM=3 -> LOW=4)
    2. Relevance Score (Descending: 1.0 -> 0.0)
    3. Recency / Timestamp (Descending: newest -> oldest)
    4. Source ID (Alphabetical tie-breaker)
    """

    @staticmethod
    def sort_context_items(items: List[ContextItem]) -> List[ContextItem]:
        """
        Sorts context items according to strict production hierarchy.
        """
        return sorted(
            items,
            key=lambda x: (
                x.priority.value,
                -round(x.relevance_score, 4),
                -x.timestamp,
                x.source_id,
            ),
        )

    @classmethod
    def create_sorted_batch(
        cls,
        query: str,
        route: RouteType,
        items: List[ContextItem],
        summary: Optional[str] = None,
    ) -> SortedContextBatch:
        """
        Constructs and sorts a complete context batch.
        """
        sorted_items = cls.sort_context_items(items)
        return SortedContextBatch(
            query=query,
            route=route,
            items=sorted_items,
            total_items=len(sorted_items),
            summary=summary,
        )
