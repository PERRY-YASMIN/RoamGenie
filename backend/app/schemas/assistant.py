from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.trip import TripDetailResponse


class AssistantChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User question or request to the travel assistant")
    trip_id: Optional[int] = Field(None, description="Optional trip ID to provide travel context")
    conversation_id: Optional[int] = Field(None, description="Optional existing conversation ID to continue a thread")


class ClarificationRequest(BaseModel):
    question: str = Field(..., description="The clarifying question to resolve ambiguity")
    options: List[str] = Field(default_factory=list, description="Specific selectable options derived from the trip context")
    allow_custom_input: bool = Field(default=True, description="Whether to show an 'Other' text box for custom input")


class AssistantChatResponse(BaseModel):
    conversation_id: int
    trip_id: Optional[int] = None
    reply: str
    provider: str
    suggested_actions: List[str] = Field(default_factory=list)
    proposed_changes: Optional[Dict[str, Any]] = Field(default=None, description="Structured proposal for itinerary/budget modifications requiring confirmation")
    clarification_request: Optional[ClarificationRequest] = Field(default=None, description="Interactive clarification choices for ambiguous requests")
    created_at: datetime


class ProposedItemPayload(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    estimated_cost: Optional[float] = None
    replacement_type: Optional[str] = None
    replacement_id: Optional[int] = None


class ExecuteProposalRequest(BaseModel):
    trip_id: int
    action: Optional[str] = Field(default="swap", description="Action to perform: 'swap', 'remove', 'clear_day', or 'add'")
    action_type: Optional[str] = Field(default=None, description="Alias for action")
    target_item_id: Optional[int] = Field(default=None, description="Target itinerary item ID for swap or remove")
    item_id: Optional[int] = Field(default=None, description="Alias for target_item_id")
    original_item_id: Optional[int] = Field(default=None, description="Alias for target_item_id")
    day_number: Optional[int] = Field(default=None, description="Day number for clearing all items in a day")
    target_day_number: Optional[int] = Field(default=None, description="Alias for day_number")
    replacement_type: Optional[str] = None
    replacement_id: Optional[int] = None
    new_item_id: Optional[int] = Field(default=None, description="Alias for replacement_id")
    title: Optional[str] = None
    proposed_item: Optional[ProposedItemPayload] = None
    proposal_id: Optional[str] = None


class ExecuteProposalResponse(BaseModel):
    success: bool
    message: str
    trip: TripDetailResponse
    proposal_id: Optional[str] = None


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
