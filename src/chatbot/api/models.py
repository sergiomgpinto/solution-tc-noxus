from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    message_id: int


class FeedbackRequest(BaseModel):
    message_id: int
    feedback_type: str


class FeedbackResponse(BaseModel):
    status: str
    feedback_id: int


class ConversationSummary(BaseModel):
    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int


class KnowledgeSourceRequest(BaseModel):
    name: str
    description: Optional[str] = None


class KnowledgeSourceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    document_count: int


class AddDocumentsRequest(BaseModel):
    documents: List[str]


class SearchRequest(BaseModel):
    query: str
    knowledge_source_ids: Optional[List[int]] = None
    n_results: int = 3


class SearchResult(BaseModel):
    document: str
    score: float
    metadata: dict