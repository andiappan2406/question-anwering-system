from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class AskRequest(BaseModel):
    question: str
    user_id: Optional[str] = None
    use_llm: Optional[bool] = False
    session_id: Optional[str] = None


class Source(BaseModel):
    record_id: str
    snippet: str
    priority: Optional[int] = 3
    relevance_score: Optional[float] = 1.0


class AskResponse(BaseModel):
    answer: str
    sources: List[Source]
    confidence: float
    route: Optional[str] = None
    offload_plan: Optional[List[Dict[str, Any]]] = None
    reasoning_trace: Optional[List[str]] = None
    execution_steps: Optional[List[str]] = None
