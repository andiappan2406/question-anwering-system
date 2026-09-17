from pydantic import BaseModel
from typing import List, Optional


class AskRequest(BaseModel):
    question: str
    user_id: Optional[str] = None
    use_llm: Optional[bool] = False


class Source(BaseModel):
    record_id: str
    snippet: str


class AskResponse(BaseModel):
    answer: str
    sources: List[Source]
    confidence: float
