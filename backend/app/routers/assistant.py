from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ai import AIConversation, AIMessage
from app.db.models.trip import PackingItem, Trip
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.assistant import (
    AssistantChatRequest,
    AssistantChatResponse,
    PackingItemCreateRequest,
    PackingItemResponse,
    PackingItemToggleRequest,
)
from app.services.ai_orchestrator import AIPlanOrchestrator, get_ai_orchestrator
from app.services.auth_service import get_current_user, get_current_user_optional
from app.services.weather_service import WeatherService, get_weather_service

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post(
    "/chat",
    response_model=AssistantChatResponse,
    summary="Interactive AI Travel Assistant Chat with Context",
)
def chat_with_assistant(
    request: AssistantChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai_orchestrator: AIPlanOrchestrator = Depends(get_ai_orchestrator),
    weather_service: WeatherService = Depends(get_weather_service),
) -> AssistantChatResponse:
    """Provides bounded AI contextual chat advice grounded in trip facts, weather forecasts, and catalogue records."""
    # 1. Validate trip and verify ownership (IDOR guard)
    trip = None
    if request.trip_id:
        trip = db.get(Trip, request.trip_id)
        if not trip:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")
        if trip.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this trip.",
            )

    # 2. Conversation retrieval / creation with ownership check
    conversation = None
    if request.conversation_id:
        conversation = db.get(AIConversation, request.conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found.",
            )
        if conversation.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation.",
            )
        if trip and conversation.trip_id != trip.id:
            conversation.trip_id = trip.id
            db.commit()

    if not conversation:
        conversation = AIConversation(
            user_id=current_user.id,
            trip_id=trip.id if trip else None,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 3. Log incoming user message
    user_msg = AIMessage(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)
    db.commit()

    # 4. Fetch recent conversation turns for context continuity
    stmt = (
        select(AIMessage)
        .where(AIMessage.conversation_id == conversation.id)
        .order_by(AIMessage.id.desc())
        .limit(6)
    )
    history = list(reversed(db.execute(stmt).scalars().all()))

    # 5. Fetch weather context if trip has destination
    weather = None
    if trip and trip.destination:
        try:
            weather = weather_service.get_destination_weather(
                db=db,
                destination=trip.destination,
                start_date=trip.start_date,
                end_date=trip.end_date,
            )
        except Exception:
            weather = None

    # 6. Execute AI Orchestrator chat
    reply_body, suggested_actions, provider_name = ai_orchestrator.chat(
        user_message=request.message,
        trip=trip,
        weather=weather,
        conversation_history=history,
    )

    # 7. Log assistant response to conversation
    ai_msg = AIMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=reply_body,
    )
    db.add(ai_msg)
    db.commit()

    return AssistantChatResponse(
        conversation_id=conversation.id,
        trip_id=request.trip_id,
        reply=reply_body,
        provider=provider_name,
        suggested_actions=suggested_actions,
        created_at=datetime.now(timezone.utc),
    )


@router.get(
    "/trips/{trip_id}/packing",
    response_model=List[PackingItemResponse],
    summary="Get packing items for a trip",
)
def get_packing_items(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[PackingItemResponse]:
    """Retrieves all checklist items for a trip owned by the current user."""
    trip = db.get(Trip, trip_id)
    if not trip or (trip.user_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")

    stmt = select(PackingItem).where(PackingItem.trip_id == trip_id).order_by(PackingItem.id)
    items = db.execute(stmt).scalars().all()
    return [PackingItemResponse.model_validate(item) for item in items]


@router.post(
    "/trips/{trip_id}/packing",
    response_model=PackingItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a custom packing item to a trip",
)
def add_packing_item(
    trip_id: int,
    request: PackingItemCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PackingItemResponse:
    """Adds a new custom item to the trip's packing checklist."""
    trip = db.get(Trip, trip_id)
    if not trip or (trip.user_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")

    item = PackingItem(
        trip_id=trip_id,
        item=request.item,
        category=request.category,
        is_packed=False,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return PackingItemResponse.model_validate(item)


@router.patch(
    "/packing/{item_id}",
    response_model=PackingItemResponse,
    summary="Toggle packed status of a checklist item",
)
def toggle_packing_item(
    item_id: int,
    request: PackingItemToggleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PackingItemResponse:
    """Updates the is_packed flag for a packing checklist item."""
    item = db.get(PackingItem, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Packing item not found.")

    trip = db.get(Trip, item.trip_id)
    if not trip or (trip.user_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    item.is_packed = request.is_packed
    db.commit()
    db.refresh(item)
    return PackingItemResponse.model_validate(item)


@router.delete(
    "/packing/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a packing checklist item",
)
def delete_packing_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Deletes a checklist item."""
    item = db.get(PackingItem, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Packing item not found.")

    trip = db.get(Trip, item.trip_id)
    if not trip or (trip.user_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    db.delete(item)
    db.commit()
