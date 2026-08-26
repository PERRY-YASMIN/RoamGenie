from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.catalogue import Destination
from app.db.session import get_db
from app.schemas.itinerary import (
    BudgetCategory,
    ItineraryDay,
    ItineraryItem,
    ItineraryProposal,
    TripPlanRequest,
)
from app.services.budget_optimizer import BudgetOptimizer, get_budget_optimizer

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("/preview", response_model=ItineraryProposal)
def preview_plan(
    trip: TripPlanRequest,
    db: Session = Depends(get_db),
    budget_optimizer: BudgetOptimizer = Depends(get_budget_optimizer),
) -> ItineraryProposal:
    """Return an unsaved catalogue-grounded deterministic proposal for in-memory guest preview."""
    # 1. Resolve destination from database
    destination = None
    if trip.destination_id:
        destination = db.get(Destination, trip.destination_id)
    if not destination and trip.destination:
        stmt = select(Destination).where(
            func.lower(Destination.city) == trip.destination.strip().lower(),
            Destination.active == True,
        )
        destination = db.execute(stmt).scalar_one_or_none()
        if not destination:
            stmt = select(Destination).where(
                Destination.city.ilike(f"%{trip.destination.strip()}%"),
                Destination.active == True,
            )
            destination = db.execute(stmt).scalar_one_or_none()

    if not destination:
        stmt = select(Destination).where(Destination.active == True).limit(1)
        destination = db.execute(stmt).scalar_one_or_none()

    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found in catalogue.",
        )

    # 2. Run deterministic optimization & scheduling in memory
    opt_result = budget_optimizer.optimize(
        destination=destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
        traveller_count=trip.travellers,
        starting_location=trip.starting_location,
        total_budget=trip.total_budget,
        preferences=trip.preferences,
    )
    sched_result = opt_result.schedule_result
    budget_summary = opt_result.budget_result
    warnings = list(opt_result.warnings)

    # 3. Map into ItineraryProposal schema (Zero database persistence)
    days_proposal = []
    for day in sched_result.days:
        items_proposal = [
            ItineraryItem(
                time=item.start_time.strftime("%H:%M") if item.start_time else "09:00",
                title=item.title,
                category=item.category,
                estimated_cost=item.estimated_cost,
            )
            for item in day.items
        ]
        days_proposal.append(
            ItineraryDay(
                day_number=day.day_number,
                date=day.itinerary_date,
                items=items_proposal,
            )
        )

    budget_split = [
        BudgetCategory(category=cat, amount=amt)
        for cat, amt in budget_summary.category_totals.items()
    ]

    packing_items = [
        "Government Issued Photo ID",
        "Weather-appropriate clothing",
        "Personal medications & first aid",
        "Phone charger & power bank",
        "Reusable water bottle",
    ]

    return ItineraryProposal(
        provider="deterministic-scheduler",
        summary=sched_result.summary,
        days=days_proposal,
        budget_split=budget_split,
        estimated_total=budget_summary.estimated_total,
        remaining_budget=budget_summary.remaining_budget,
        warnings=warnings,
        packing_items=packing_items,
    )
