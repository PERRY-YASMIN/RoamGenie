from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.catalogue import Destination
from app.db.models.trip import Trip
from app.schemas.trip import TripCreateRequest, TripUpdateRequest


class TripValidationError(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY):
        super().__init__(status_code=status_code, detail=detail)


def validate_trip_create(db: Session, request: TripCreateRequest) -> Destination:
    """Validate all constraints before creating a new trip."""
    # 1. Date constraints
    if request.end_date < request.start_date:
        raise TripValidationError("End date must be on or after start date.")
    
    duration = (request.end_date - request.start_date).days + 1
    if duration < 1 or duration > 31:
        raise TripValidationError("Trip duration must be between 1 and 31 days.")

    # 2. Traveller constraints
    if request.traveller_count <= 0 or request.traveller_count > 50:
        raise TripValidationError("Traveller count must be between 1 and 50.")

    # 3. Budget constraints
    if request.total_budget <= Decimal("0.00"):
        raise TripValidationError("Total budget must be greater than zero.")

    # 4. Destination validation
    dest = db.get(Destination, request.destination_id)
    if not dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination ID {request.destination_id} does not exist.",
        )
    if not dest.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Destination '{dest.city}' is currently inactive for booking/planning.",
        )

    return dest


def validate_trip_update(
    db: Session, trip: Trip, update_data: TripUpdateRequest
) -> Optional[Destination]:
    """Validate constraints against the merged current and proposed trip state."""
    new_start = update_data.start_date if update_data.start_date is not None else trip.start_date
    new_end = update_data.end_date if update_data.end_date is not None else trip.end_date

    if new_end < new_start:
        raise TripValidationError("End date must be on or after start date.")

    duration = (new_end - new_start).days + 1
    if duration < 1 or duration > 31:
        raise TripValidationError("Trip duration must be between 1 and 31 days.")

    new_travellers = (
        update_data.traveller_count
        if update_data.traveller_count is not None
        else trip.traveller_count
    )
    if new_travellers <= 0 or new_travellers > 50:
        raise TripValidationError("Traveller count must be between 1 and 50.")

    new_budget = (
        update_data.total_budget
        if update_data.total_budget is not None
        else trip.total_budget
    )
    if new_budget <= Decimal("0.00"):
        raise TripValidationError("Total budget must be greater than zero.")

    dest = None
    if update_data.destination_id is not None and update_data.destination_id != trip.destination_id:
        dest = db.get(Destination, update_data.destination_id)
        if not dest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destination ID {update_data.destination_id} does not exist.",
            )
        if not dest.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Destination '{dest.city}' is currently inactive.",
            )

    return dest


def verify_trip_ownership(trip: Optional[Trip], user_id: int, is_admin: bool = False) -> Trip:
    """Ensure the trip exists and the requesting user is the owner or an admin."""
    if trip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found.",
        )
    if trip.user_id != user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access or modify this trip.",
        )
    return trip
