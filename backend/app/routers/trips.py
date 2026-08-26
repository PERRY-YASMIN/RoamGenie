from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models.finance import SavedTrip
from app.db.models.trip import Trip
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.trip import (
    ItineraryDetailResponse,
    ItineraryItemSwapRequest,
    SavedTripResponse,
    TripCreateRequest,
    TripDetailResponse,
    TripPlanGenerateResponse,
    TripSummaryResponse,
    TripUpdateRequest,
)
from app.schemas.weather import DestinationWeatherResponse
from app.services.auth_service import get_current_user
from app.services.trip_service import TripService, get_trip_service

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post(
    "",
    response_model=TripDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new trip",
)
def create_trip(
    request: TripCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> TripDetailResponse:
    """Create a new trip record for the authenticated user."""
    trip = trip_service.create_trip(db=db, user_id=current_user.id, request=request)
    # Fetch with full relations for response DTO
    full_trip = trip_service.get_trip(db=db, user_id=current_user.id, trip_id=trip.id)
    return trip_service.build_trip_detail_response(full_trip, current_user.id)


@router.get(
    "",
    response_model=List[TripSummaryResponse],
    summary="List all trips for authenticated user",
)
def list_trips(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> List[TripSummaryResponse]:
    """Retrieve all trips owned by the authenticated user."""
    trips = trip_service.list_trips(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        is_admin=(current_user.role == "admin"),
    )
    return [
        TripSummaryResponse(
            id=t.id,
            user_id=t.user_id,
            destination_id=t.destination_id,
            destination_city=t.destination.city if t.destination else None,
            destination_country=t.destination.country if t.destination else None,
            starting_location=t.starting_location,
            start_date=t.start_date,
            end_date=t.end_date,
            traveller_count=t.traveller_count,
            total_budget=t.total_budget,
            estimated_total=t.estimated_total,
            status=t.status,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )
        for t in trips
    ]


@router.get(
    "/saved",
    response_model=List[SavedTripResponse],
    summary="List saved/bookmarked trips for authenticated user",
)
def list_saved_trips(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[SavedTripResponse]:
    """Retrieve bookmarked trips for the current user."""
    stmt = (
        select(SavedTrip)
        .where(SavedTrip.user_id == current_user.id)
        .options(selectinload(SavedTrip.trip).selectinload(Trip.destination))
        .order_by(SavedTrip.saved_at.desc())
    )
    saved_items = db.execute(stmt).scalars().all()
    results = []
    for item in saved_items:
        trip_dto = None
        if item.trip:
            trip_dto = TripSummaryResponse(
                id=item.trip.id,
                user_id=item.trip.user_id,
                destination_id=item.trip.destination_id,
                destination_city=item.trip.destination.city if item.trip.destination else None,
                destination_country=item.trip.destination.country if item.trip.destination else None,
                starting_location=item.trip.starting_location,
                start_date=item.trip.start_date,
                end_date=item.trip.end_date,
                traveller_count=item.trip.traveller_count,
                total_budget=item.trip.total_budget,
                estimated_total=item.trip.estimated_total,
                status=item.trip.status,
                created_at=item.trip.created_at,
                updated_at=item.trip.updated_at,
            )
        results.append(
            SavedTripResponse(
                id=item.id,
                user_id=item.user_id,
                trip_id=item.trip_id,
                saved_at=item.saved_at,
                trip=trip_dto,
            )
        )
    return results


@router.get(
    "/{trip_id}",
    response_model=TripDetailResponse,
    summary="Get trip details by ID",
)
def get_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> TripDetailResponse:
    """Retrieve full details of a specific trip (enforcing ownership/RBAC)."""
    trip = trip_service.get_trip(
        db=db,
        user_id=current_user.id,
        trip_id=trip_id,
        is_admin=(current_user.role == "admin"),
    )
    return trip_service.build_trip_detail_response(trip, current_user.id)


@router.patch(
    "/{trip_id}",
    response_model=TripDetailResponse,
    summary="Update trip details",
)
def update_trip(
    trip_id: int,
    request: TripUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> TripDetailResponse:
    """Update trip attributes with constraint re-validation."""
    trip = trip_service.update_trip(
        db=db,
        user_id=current_user.id,
        trip_id=trip_id,
        request=request,
        is_admin=(current_user.role == "admin"),
    )
    full_trip = trip_service.get_trip(
        db=db,
        user_id=current_user.id,
        trip_id=trip.id,
        is_admin=(current_user.role == "admin"),
    )
    return trip_service.build_trip_detail_response(full_trip, current_user.id)


@router.delete(
    "/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a trip",
)
def delete_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> None:
    """Delete a trip and cascade delete all associated itinerary and budget items."""
    trip_service.delete_trip(
        db=db,
        user_id=current_user.id,
        trip_id=trip_id,
        is_admin=(current_user.role == "admin"),
    )


@router.get(
    "/{trip_id}/weather",
    response_model=DestinationWeatherResponse,
    summary="Get destination weather forecast for the trip dates",
)
def get_trip_weather(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> DestinationWeatherResponse:
    """Retrieve weather forecast for the trip's destination and dates."""
    return trip_service.get_trip_weather(
        db=db,
        user_id=current_user.id,
        trip_id=trip_id,
        is_admin=(current_user.role == "admin"),
    )


@router.post(
    "/{trip_id}/generate",
    response_model=TripPlanGenerateResponse,
    summary="Generate and persist day-wise itinerary and budget",
)
def generate_trip_plan(
    trip_id: int,
    preferences: Optional[List[str]] = Query(None, description="Optional style preferences"),
    force_ai: bool = Query(False, description="Explicitly request external AI generation"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> TripPlanGenerateResponse:
    """Execute AI/deterministic scheduler, budget optimizer, and transactional persistence."""
    trip, itin, budget_res, opt_applied, warnings = trip_service.generate_and_persist_plan(
        db=db,
        user_id=current_user.id,
        trip_id=trip_id,
        preferences=preferences,
        force_ai=force_ai,
        is_admin=(current_user.role == "admin"),
    )

    full_trip = trip_service.get_trip(
        db=db,
        user_id=current_user.id,
        trip_id=trip.id,
        is_admin=(current_user.role == "admin"),
    )
    trip_detail = trip_service.build_trip_detail_response(full_trip, current_user.id)
    latest_itin = trip_detail.itineraries[0] if trip_detail.itineraries else None

    if not latest_itin:
        raise HTTPException(status_code=500, detail="Failed to load generated itinerary.")

    return TripPlanGenerateResponse(
        trip=trip_detail,
        itinerary=latest_itin,
        budget_summary=budget_res.to_summary_response(),
        optimization_applied=opt_applied,
        warnings=warnings,
    )


@router.post(
    "/{trip_id}/ai-plan",
    response_model=TripPlanGenerateResponse,
    summary="Generate AI-assisted plan explicitly",
)
def generate_ai_trip_plan(
    trip_id: int,
    preferences: Optional[List[str]] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> TripPlanGenerateResponse:
    """Explicitly generate an AI-assisted plan with automatic fallback."""
    return generate_trip_plan(
        trip_id=trip_id,
        preferences=preferences,
        force_ai=True,
        current_user=current_user,
        db=db,
        trip_service=trip_service,
    )


@router.post(
    "/{trip_id}/plan",
    response_model=TripPlanGenerateResponse,
    summary="Alias for plan generation",
)
def plan_trip_alias(
    trip_id: int,
    preferences: Optional[List[str]] = Query(None),
    force_ai: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> TripPlanGenerateResponse:
    """Alias for /trips/{trip_id}/generate."""
    return generate_trip_plan(
        trip_id=trip_id,
        preferences=preferences,
        force_ai=force_ai,
        current_user=current_user,
        db=db,
        trip_service=trip_service,
    )


@router.get(
    "/{trip_id}/itinerary",
    response_model=ItineraryDetailResponse,
    summary="Get latest active itinerary for trip",
)
def get_trip_itinerary(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> ItineraryDetailResponse:
    """Retrieve the latest active itinerary version for a trip."""
    trip = trip_service.get_trip(
        db=db,
        user_id=current_user.id,
        trip_id=trip_id,
        is_admin=(current_user.role == "admin"),
    )
    trip_detail = trip_service.build_trip_detail_response(trip, current_user.id)
    if not trip_detail.itineraries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No itinerary has been generated for this trip yet. Call POST /trips/{id}/generate first.",
        )
    return trip_detail.itineraries[0]


@router.post(
    "/{trip_id}/save",
    summary="Toggle bookmark/saved state for a trip",
)
def toggle_save_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> dict:
    """Save or unsave (bookmark) a trip for quick access."""
    saved = trip_service.toggle_saved_trip(
        db=db,
        user_id=current_user.id,
        trip_id=trip_id,
        is_admin=(current_user.role == "admin"),
    )
    return {
        "trip_id": trip_id,
        "is_saved": saved,
        "message": "Trip saved to bookmarks." if saved else "Trip removed from bookmarks.",
    }


@router.patch(
    "/{trip_id}/itinerary/items/{item_id}",
    response_model=TripDetailResponse,
    summary="Swap an itinerary item with an alternative catalogue entity",
)
def swap_trip_itinerary_item(
    trip_id: int,
    item_id: int,
    request: ItineraryItemSwapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> TripDetailResponse:
    """Manually replace an itinerary item with a catalogue alternative and recalculate budget."""
    return trip_service.swap_itinerary_item(
        db=db,
        user_id=current_user.id,
        trip_id=trip_id,
        item_id=item_id,
        swap_request=request,
        is_admin=(current_user.role == "admin"),
    )

