from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AssistantChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User question or request to the travel assistant")
    trip_id: Optional[int] = Field(None, description="Optional trip ID to provide travel context")
    conversation_id: Optional[int] = Field(None, description="Optional existing conversation ID to continue a thread")


class AssistantChatResponse(BaseModel):
    conversation_id: int
    trip_id: Optional[int] = None
    reply: str
    provider: str
    suggested_actions: List[str] = Field(default_factory=list)
    created_at: datetime


class PackingItemToggleRequest(BaseModel):
    is_packed: bool


class PackingItemCreateRequest(BaseModel):
    item: str = Field(..., min_length=1, max_length=100)
    category: str = Field("General", min_length=1, max_length=50)


class PackingItemResponse(BaseModel):
    id: int
    trip_id: int
    item: str
    category: str
    is_packed: bool

    model_config = ConfigDict(from_attributes=True)
