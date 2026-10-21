import logging
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.db.models.ai import AIConversation, AIMessage
from app.db.models.trip import Itinerary, ItineraryDay, ItineraryItem, PackingItem, Trip
from app.db.models.user import User
from app.db.session import get_db

logger = logging.getLogger(__name__)
from app.schemas.assistant import (
    AssistantChatRequest,
    AssistantChatResponse,
    ExecuteProposalRequest,
    ExecuteProposalResponse,
    PackingItemCreateRequest,
    PackingItemResponse,
    PackingItemToggleRequest,
)
from app.schemas.trip import ItineraryItemSwapRequest
from app.services.ai_orchestrator import AIPlanOrchestrator, get_ai_orchestrator
from app.services.auth_service import get_current_user
from app.services.trip_service import TripService, get_trip_service
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
    """Provides bounded AI contextual chat advice grounded in trip facts, weather forecasts, and autonomous database tools."""
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

    # 6. Execute AI Orchestrator chat with autonomous tool capabilities
    reply_body, suggested_actions, provider_name, proposed_changes, clarification_request = ai_orchestrator.chat(
        user_message=request.message,
        trip=trip,
        weather=weather,
        conversation_history=history,
        current_user=current_user,
        db=db,
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
        proposed_changes=proposed_changes,
        clarification_request=clarification_request,
        created_at=datetime.now(timezone.utc),
    )


@router.post(
    "/execute-proposal",
    response_model=ExecuteProposalResponse,
    summary="Execute Confirmed Itinerary Modification with ACID Transaction",
)
def execute_proposal(
    request: ExecuteProposalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> ExecuteProposalResponse:
    """
    Executes an explicit, user-confirmed itinerary modification proposal.
    Enforces user ownership, performs ACID-compliant transactional persistence,
    recalculates category budget allocations, and fires the PL/pgSQL audit trigger.
    """
    # 1. Ownership and existence verification
    trip = db.get(Trip, request.trip_id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip #{request.trip_id} not found.",
        )
    if trip.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this trip.",
        )

    action_clean = (request.action_type or request.action or "swap").lower().strip()
    target_item_id = request.target_item_id or request.item_id or request.original_item_id
    rep_type = request.replacement_type or (request.proposed_item.replacement_type if request.proposed_item else None)
    rep_id = request.replacement_id or request.new_item_id or (request.proposed_item.replacement_id if request.proposed_item else None)
    title = request.title or (request.proposed_item.title if request.proposed_item else None)

    try:
        if action_clean == "swap":
            if not target_item_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="target_item_id is required for a swap proposal.",
                )
            if not rep_type or not rep_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="replacement_type and replacement_id are required for a swap proposal.",
                )

            swap_req = ItineraryItemSwapRequest(
                replacement_type=rep_type,
                replacement_id=rep_id,
                title=title,
            )
            updated_trip_dto = trip_service.swap_itinerary_item(
                db=db,
                user_id=current_user.id,
                trip_id=request.trip_id,
                item_id=target_item_id,
                swap_request=swap_req,
                is_admin=(current_user.role == "admin"),
            )

        elif action_clean in ("remove", "clear_day", "clear"):
            req_day = request.day_number or request.target_day_number
            if not target_item_id and not req_day:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="target_item_id or day_number is required for a removal/cancellation proposal.",
                )

            stmt = (
                select(Trip)
                .where(Trip.id == request.trip_id)
                .options(
                    selectinload(Trip.itineraries).selectinload(Itinerary.days).selectinload(ItineraryDay.items),
                    selectinload(Trip.budget_allocations),
                )
            )
            trip_record = db.execute(stmt).scalar_one_or_none()
            target_itin = sorted(trip_record.itineraries, key=lambda i: i.version, reverse=True)[0] if trip_record.itineraries else None

            if not target_itin:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Trip #{request.trip_id} has no itinerary to modify.",
                )

            deleted_ids = set()
            if target_item_id:
                target_item = None
                for day in target_itin.days:
                    for itm in day.items:
                        if itm.id == target_item_id:
                            target_item = itm
                            break
                    if target_item:
                        break

                if not target_item:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Itinerary item #{target_item_id} not found on trip #{request.trip_id}.",
                    )

                deleted_ids.add(target_item.id)
                db.delete(target_item)
            else:
                target_day = None
                for day in target_itin.days:
                    if day.day_number == req_day:
                        target_day = day
                        break
                if not target_day:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Day {req_day} not found on trip #{request.trip_id}.",
                    )
                for itm in list(target_day.items):
                    deleted_ids.add(itm.id)
                    db.delete(itm)

            db.flush()

            # Recalculate category totals across remaining items
            category_totals = {
                "accommodation": Decimal("0.00"),
                "transportation": Decimal("0.00"),
                "food": Decimal("0.00"),
                "attractions": Decimal("0.00"),
            }
            for day in target_itin.days:
                for itm in day.items:
                    if itm.id in deleted_ids:
                        continue
                    cat = itm.category.lower().strip()
                    if cat in ("attraction", "attractions", "activity", "activities", "sightseeing"):
                        category_totals["attractions"] += itm.estimated_cost
                    elif cat in ("hotel", "accommodation", "stay", "lodging"):
                        category_totals["accommodation"] += itm.estimated_cost
                    elif cat in ("food", "dining", "restaurant", "meal"):
                        category_totals["food"] += itm.estimated_cost
                    elif cat in ("transport", "transportation", "transit"):
                        category_totals["transportation"] += itm.estimated_cost

            total_est = sum(category_totals.values()).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            trip_record.estimated_total = total_est
            trip_record.updated_at = datetime.now(timezone.utc)

            for alloc in (trip_record.budget_allocations or []):
                norm_cat = alloc.category.lower().strip()
                if norm_cat in category_totals:
                    alloc.amount = category_totals[norm_cat]

            db.commit()
            db.refresh(trip_record)
            full_trip = trip_service.get_trip(db=db, user_id=current_user.id, trip_id=request.trip_id)
            updated_trip_dto = trip_service.build_trip_detail_response(full_trip, current_user.id)

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported proposal action: '{action_clean}'.",
            )

        return ExecuteProposalResponse(
            success=True,
            message=f"Successfully executed '{action_clean}' on trip #{request.trip_id}.",
            trip=updated_trip_dto,
            proposal_id=request.proposal_id,
        )

    except IntegrityError as exc:
        db.rollback()
        logger.warning(f"IntegrityError executing proposal on trip #{request.trip_id}: {exc}")
        orig_msg = str(getattr(exc, "orig", exc))
        if "check_trip_est_total" in orig_msg or "estimated_total" in orig_msg:
            detail = "This change violates trip budget constraints: estimated total cannot be negative."
        elif "check_allocation_amount" in orig_msg or "check_trip_budget" in orig_msg or "budget" in orig_msg.lower():
            detail = "This change violates your budget constraints: allocated budget amounts must be valid positive values."
        elif "foreign key" in orig_msg.lower() or "foreignkey" in orig_msg.lower():
            detail = "The selected replacement entity does not exist in the catalogue or has invalid relational dependencies."
        elif "check" in orig_msg.lower():
            detail = "This change violates itinerary database constraints."
        else:
            detail = f"Database constraint violation during commit: {orig_msg}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.exception(f"Unexpected error executing proposal on trip #{request.trip_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to execute proposal: {str(exc)}",
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
