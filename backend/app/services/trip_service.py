from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from app.db.models.catalogue import Attraction, Destination, Hotel, Restaurant, TransportOption
from app.db.models.finance import BudgetAllocation, SavedTrip
from app.db.models.trip import Itinerary, ItineraryDay, ItineraryItem, PackingItem, Trip, TripMember
from app.schemas.trip import (
    BudgetAllocationResponse,
    BudgetSummaryResponse,
    ItineraryDayResponse,
    ItineraryDetailResponse,
    ItineraryItemResponse,
    ItineraryItemSwapRequest,
    PackingItemResponse,
    TripCreateRequest,
    TripDetailResponse,
    TripMemberResponse,
    TripSummaryResponse,
    TripUpdateRequest,
)
from app.schemas.weather import DestinationWeatherResponse
from app.services.ai_orchestrator import AIPlanOrchestrator, get_ai_orchestrator
from app.services.budget_optimizer import BudgetOptimizer, OptimizationResult
from app.services.budget_service import BudgetCalculationResult, BudgetCalculator
from app.services.trip_validator import (
    validate_trip_create,
    validate_trip_update,
    verify_trip_ownership,
)
from app.services.weather_service import WeatherService, get_weather_service


class TripService:
    """Core domain service for Trip lifecycle, AI-assisted & deterministic planning, and transactional persistence."""

    def __init__(
        self,
        optimizer: Optional[BudgetOptimizer] = None,
        calculator: Optional[BudgetCalculator] = None,
        weather_service: Optional[WeatherService] = None,
        ai_orchestrator: Optional[AIPlanOrchestrator] = None,
    ):
        self.optimizer = optimizer or BudgetOptimizer()
        self.calculator = calculator or BudgetCalculator()
        self.weather_service = weather_service or get_weather_service()
        self.ai_orchestrator = ai_orchestrator or get_ai_orchestrator()

    def create_trip(
        self, db: Session, user_id: int, request: TripCreateRequest
    ) -> Trip:
        destination = validate_trip_create(db, request)

        trip = Trip(
            user_id=user_id,
            destination_id=destination.id,
            starting_location=request.starting_location.strip(),
            start_date=request.start_date,
            end_date=request.end_date,
            traveller_count=request.traveller_count,
            total_budget=request.total_budget.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            estimated_total=Decimal("0.00"),
            status="draft",
        )
        db.add(trip)
        db.flush()

        # Add trip members if provided
        if request.members:
            for m in request.members:
                member = TripMember(
                    trip_id=trip.id,
                    display_name=m.display_name.strip(),
                    age_group=m.age_group,
                    special_requirements=m.special_requirements,
                )
                db.add(member)

        # Default packing items
        default_packs = [
            ("Government Photo ID & Tickets", "documents"),
            ("Weather-appropriate clothing", "clothing"),
            ("Personal medication & First-Aid", "health"),
            ("Phone charger & Power bank", "electronics"),
            ("Reusable water bottle", "essentials"),
        ]
        for item_name, cat in default_packs:
            db.add(
                PackingItem(
                    trip_id=trip.id,
                    item=item_name,
                    category=cat,
                    is_packed=False,
                )
            )

        if request.generate_plan:
            self._execute_plan_generation(
                db=db,
                trip=trip,
                destination=destination,
                preferences=request.preferences,
            )

        db.commit()
        db.refresh(trip)
        return trip

    def get_trip(
        self, db: Session, user_id: int, trip_id: int, is_admin: bool = False
    ) -> Trip:
        stmt = (
            select(Trip)
            .where(Trip.id == trip_id)
            .options(
                selectinload(Trip.destination),
                selectinload(Trip.members),
                selectinload(Trip.budget_allocations),
                selectinload(Trip.packing_items),
                selectinload(Trip.saved_trips),
                selectinload(Trip.itineraries)
                .selectinload(Itinerary.days)
                .selectinload(ItineraryDay.items),
            )
        )
        trip = db.execute(stmt).scalar_one_or_none()
        return verify_trip_ownership(trip, user_id, is_admin)

    def list_trips(
        self, db: Session, user_id: int, skip: int = 0, limit: int = 50, is_admin: bool = False
    ) -> List[Trip]:
        stmt = select(Trip).options(selectinload(Trip.destination))
        if not is_admin:
            stmt = stmt.where(Trip.user_id == user_id)
        stmt = stmt.order_by(Trip.created_at.desc()).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def update_trip(
        self,
        db: Session,
        user_id: int,
        trip_id: int,
        request: TripUpdateRequest,
        is_admin: bool = False,
    ) -> Trip:
        trip = self.get_trip(db, user_id, trip_id, is_admin)
        validate_trip_update(db, trip, request)

        if request.destination_id is not None:
            trip.destination_id = request.destination_id
        if request.starting_location is not None:
            trip.starting_location = request.starting_location.strip()
        if request.start_date is not None:
            trip.start_date = request.start_date
        if request.end_date is not None:
            trip.end_date = request.end_date
        if request.traveller_count is not None:
            trip.traveller_count = request.traveller_count
        if request.total_budget is not None:
            trip.total_budget = request.total_budget.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        if request.status is not None:
            trip.status = request.status

        trip.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(trip)
        return trip

    def delete_trip(
        self, db: Session, user_id: int, trip_id: int, is_admin: bool = False
    ) -> None:
        trip = self.get_trip(db, user_id, trip_id, is_admin)
        db.delete(trip)
        db.commit()

    def get_trip_weather(
        self, db: Session, user_id: int, trip_id: int, is_admin: bool = False
    ) -> DestinationWeatherResponse:
        """Retrieves destination weather forecast for the trip dates."""
        trip = self.get_trip(db, user_id, trip_id, is_admin)
        destination = db.get(Destination, trip.destination_id)
        return self.weather_service.get_destination_weather(
            db=db,
            destination=destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
        )

    def generate_and_persist_plan(
        self,
        db: Session,
        user_id: int,
        trip_id: int,
        preferences: Optional[List[str]] = None,
        force_ai: bool = False,
        is_admin: bool = False,
    ) -> Tuple[Trip, Itinerary, BudgetCalculationResult, bool, List[str]]:
        trip = self.get_trip(db, user_id, trip_id, is_admin)
        destination = db.get(Destination, trip.destination_id)

        try:
            budget_res, itinerary, opt_applied, warnings = self._execute_plan_generation(
                db=db,
                trip=trip,
                destination=destination,
                preferences=preferences,
                force_ai=force_ai,
            )
            db.commit()
            db.refresh(trip)
            return trip, itinerary, budget_res, opt_applied, warnings
        except Exception:
            db.rollback()
            raise

    def _execute_plan_generation(
        self,
        db: Session,
        trip: Trip,
        destination: Destination,
        preferences: Optional[List[str]] = None,
        force_ai: bool = False,
    ) -> Tuple[BudgetCalculationResult, Itinerary, bool, List[str]]:
        """Internal atomic plan generation and persistence with AI & Weather synergy."""
        # 1. Fetch weather forecast for destination
        weather = self.weather_service.get_destination_weather(
            db=db,
            destination=destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
        )

        # 2. Invoke AI Orchestrator (with automatic fallback to deterministic scheduler)
        (
            schedule_res,
            is_ai,
            provider_name,
            packing_items,
            weather_advice,
            ai_warnings,
        ) = self.ai_orchestrator.generate_plan(
            destination=destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            traveller_count=trip.traveller_count,
            starting_location=trip.starting_location,
            total_budget=trip.total_budget,
            preferences=preferences,
            weather=weather,
            force_ai=force_ai,
        )

        # 3. Calculate initial budget
        budget_res = self.calculator.calculate(
            total_budget=trip.total_budget,
            scheduled_days=schedule_res.days,
        )

        opt_applied = False
        final_warnings = list(ai_warnings)

        # 4. If deficit exists, optimize budget
        if budget_res.deficit > Decimal("0.00"):
            opt_res = self.optimizer.optimize(
                destination=destination,
                start_date=trip.start_date,
                end_date=trip.end_date,
                traveller_count=trip.traveller_count,
                starting_location=trip.starting_location,
                total_budget=trip.total_budget,
                preferences=preferences,
            )
            schedule_res = opt_res.schedule_result
            budget_res = opt_res.budget_result
            opt_applied = opt_res.optimization_applied
            final_warnings.extend(opt_res.warnings)

        # 5. Determine itinerary version
        stmt = (
            select(func.coalesce(func.max(Itinerary.version), 0))
            .where(Itinerary.trip_id == trip.id)
        )
        max_ver = db.execute(stmt).scalar() or 0
        new_version = max_ver + 1

        # 6. Insert Itinerary header
        itinerary = Itinerary(
            trip_id=trip.id,
            version=new_version,
            summary=schedule_res.summary,
            provider=provider_name,
        )
        db.add(itinerary)
        db.flush()

        # 7. Insert Days and Items
        for sched_day in schedule_res.days:
            day_record = ItineraryDay(
                itinerary_id=itinerary.id,
                day_number=sched_day.day_number,
                itinerary_date=sched_day.itinerary_date,
            )
            db.add(day_record)
            db.flush()

            for sched_item in sched_day.items:
                item_record = ItineraryItem(
                    itinerary_day_id=day_record.id,
                    item_order=sched_item.item_order,
                    start_time=sched_item.start_time,
                    title=sched_item.title,
                    category=sched_item.category,
                    estimated_cost=sched_item.estimated_cost,
                    notes=sched_item.notes,
                )
                db.add(item_record)

        # 8. Replace Budget Allocations for this trip
        db.execute(delete(BudgetAllocation).where(BudgetAllocation.trip_id == trip.id))
        for alloc in budget_res.allocations:
            db.add(
                BudgetAllocation(
                    trip_id=trip.id,
                    category=alloc.category,
                    amount=alloc.amount,
                )
            )

        # 9. Sync Packing Items (Weather + AI suggestions)
        if packing_items:
            existing_items_stmt = select(PackingItem.item).where(PackingItem.trip_id == trip.id)
            existing_items = set(db.execute(existing_items_stmt).scalars().all())
            for p_item in packing_items:
                if p_item not in existing_items:
                    db.add(
                        PackingItem(
                            trip_id=trip.id,
                            item=p_item,
                            category="recommendation",
                            is_packed=False,
                        )
                    )
                    existing_items.add(p_item)

        # 10. Update Trip header summary
        trip.estimated_total = budget_res.estimated_total
        trip.status = "planned"
        trip.updated_at = datetime.now(timezone.utc)
        db.flush()

        return budget_res, itinerary, opt_applied, final_warnings

    def build_trip_detail_response(
        self, trip: Trip, user_id: int
    ) -> TripDetailResponse:
        """Converts Trip ORM model to rich API response DTO."""
        dest_city = trip.destination.city if trip.destination else None
        dest_country = trip.destination.country if trip.destination else None

        # Build itineraries hierarchy
        itineraries_dto: List[ItineraryDetailResponse] = []
        for itin in sorted(trip.itineraries or [], key=lambda i: i.version, reverse=True):
            days_dto: List[ItineraryDayResponse] = []
            for d in sorted(itin.days or [], key=lambda day: day.day_number):
                items_dto: List[ItineraryItemResponse] = [
                    ItineraryItemResponse(
                        id=item.id,
                        itinerary_day_id=item.itinerary_day_id,
                        item_order=item.item_order,
                        start_time=item.start_time,
                        title=item.title,
                        category=item.category,
                        estimated_cost=item.estimated_cost,
                        notes=item.notes,
                    )
                    for item in sorted(d.items or [], key=lambda it: it.item_order)
                ]
                days_dto.append(
                    ItineraryDayResponse(
                        id=d.id,
                        itinerary_id=d.itinerary_id,
                        day_number=d.day_number,
                        itinerary_date=d.itinerary_date,
                        items=items_dto,
                    )
                )
            itineraries_dto.append(
                ItineraryDetailResponse(
                    id=itin.id,
                    trip_id=itin.trip_id,
                    version=itin.version,
                    summary=itin.summary,
                    provider=itin.provider,
                    created_at=itin.created_at,
                    days=days_dto,
                )
            )

        # Build allocations & budget summary
        allocations_dto: List[BudgetAllocationResponse] = [
            BudgetAllocationResponse(
                id=alloc.id,
                trip_id=alloc.trip_id,
                category=alloc.category,
                amount=alloc.amount,
            )
            for alloc in trip.budget_allocations or []
        ]

        remaining = trip.total_budget - trip.estimated_total
        deficit = max(Decimal("0.00"), trip.estimated_total - trip.total_budget)
        utilization = (
            ((trip.estimated_total / trip.total_budget) * Decimal("100.00")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            if trip.total_budget > Decimal("0.00")
            else Decimal("0.00")
        )
        if remaining > Decimal("0.00"):
            b_status = "within_budget"
        elif remaining == Decimal("0.00"):
            b_status = "exact"
        else:
            b_status = "over_budget"

        budget_summary = BudgetSummaryResponse(
            total_budget=trip.total_budget,
            estimated_total=trip.estimated_total,
            remaining_budget=remaining,
            deficit=deficit,
            utilization_percentage=utilization,
            status=b_status,
            categories=allocations_dto,
            warnings=[f"Trip exceeds budget by ₹{deficit}."] if deficit > Decimal("0.00") else [],
        )

        members_dto = [
            TripMemberResponse(
                id=m.id,
                trip_id=m.trip_id,
                display_name=m.display_name,
                age_group=m.age_group,
                special_requirements=m.special_requirements,
            )
            for m in trip.members or []
        ]

        packing_dto = [
            PackingItemResponse(
                id=p.id,
                trip_id=p.trip_id,
                item=p.item,
                category=p.category,
                is_packed=p.is_packed,
            )
            for p in trip.packing_items or []
        ]

        is_saved = any(s.user_id == user_id for s in trip.saved_trips or [])

        return TripDetailResponse(
            id=trip.id,
            user_id=trip.user_id,
            destination_id=trip.destination_id,
            destination_city=dest_city,
            destination_country=dest_country,
            starting_location=trip.starting_location,
            start_date=trip.start_date,
            end_date=trip.end_date,
            traveller_count=trip.traveller_count,
            total_budget=trip.total_budget,
            estimated_total=trip.estimated_total,
            status=trip.status,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
            members=members_dto,
            itineraries=itineraries_dto,
            budget_allocations=allocations_dto,
            budget_summary=budget_summary,
            packing_items=packing_dto,
            is_saved=is_saved,
        )

    def toggle_saved_trip(
        self, db: Session, user_id: int, trip_id: int, is_admin: bool = False
    ) -> bool:
        """Toggles bookmarking a trip for the current user. Returns True if now saved, False if unsaved."""
        self.get_trip(db=db, user_id=user_id, trip_id=trip_id, is_admin=is_admin)

        saved_stmt = select(SavedTrip).where(
            SavedTrip.user_id == user_id, SavedTrip.trip_id == trip_id
        )
        existing = db.execute(saved_stmt).scalar_one_or_none()
        if existing:
            db.delete(existing)
            db.commit()
            return False
        else:
            saved = SavedTrip(user_id=user_id, trip_id=trip_id)
            db.add(saved)
            db.commit()
            return True

    def swap_itinerary_item(
        self,
        db: Session,
        user_id: int,
        trip_id: int,
        item_id: int,
        swap_request: ItineraryItemSwapRequest,
        is_admin: bool = False,
    ) -> TripDetailResponse:
        """Manually swaps an itinerary item with an alternative catalogue entity, updating budget allocations atomically."""
        # 1. Fetch trip and verify ownership
        stmt = (
            select(Trip)
            .where(Trip.id == trip_id)
            .options(
                selectinload(Trip.members),
                selectinload(Trip.itineraries).selectinload(Itinerary.days).selectinload(ItineraryDay.items),
                selectinload(Trip.budget_allocations),
                selectinload(Trip.packing_items),
                selectinload(Trip.saved_trips),
                selectinload(Trip.destination),
            )
        )
        trip = db.execute(stmt).scalar_one_or_none()
        verify_trip_ownership(trip=trip, user_id=user_id, is_admin=is_admin)

        # 2. Find target itinerary item in trip hierarchy
        target_item = None
        target_itin = None
        for itin in trip.itineraries:
            for day in itin.days:
                for itm in day.items:
                    if itm.id == item_id:
                        target_item = itm
                        target_itin = itin
                        break
                if target_item:
                    break
            if target_item:
                break

        if not target_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Itinerary item #{item_id} not found on trip #{trip_id}.",
            )

        # 3. Validate and resolve replacement catalogue entity
        rep_type = swap_request.replacement_type.lower().strip()
        rep_id = swap_request.replacement_id

        if rep_type in ("hotel", "accommodation"):
            hotel = db.get(Hotel, rep_id)
            if not hotel:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Hotel #{rep_id} not found.")
            if hotel.destination_id != trip.destination_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Hotel #{rep_id} does not belong to trip destination #{trip.destination_id}.",
                )
            if target_item.category.lower().strip() not in ("hotel", "accommodation", "stay", "lodging"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot replace a '{target_item.category}' event with a hotel entity.",
                )
            target_item.title = swap_request.title or f"Overnight Stay at {hotel.name}"
            target_item.category = "accommodation"
            target_item.estimated_cost = hotel.price_per_night
            target_item.notes = f"Rating: {hotel.rating or 4.0}/5.0 · Tariff: ₹{hotel.price_per_night}/night"

        elif rep_type in ("restaurant", "dining", "food"):
            restaurant = db.get(Restaurant, rep_id)
            if not restaurant:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Restaurant #{rep_id} not found.")
            if restaurant.destination_id != trip.destination_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Restaurant #{rep_id} does not belong to trip destination #{trip.destination_id}.",
                )
            if target_item.category.lower().strip() not in ("food", "dining", "restaurant", "meal"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot replace a '{target_item.category}' event with a dining entity.",
                )
            avg_cost = restaurant.average_cost_per_person or Decimal("250.00")
            target_item.title = swap_request.title or f"Dining at {restaurant.name}"
            target_item.category = "food"
            target_item.estimated_cost = (avg_cost * trip.traveller_count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            target_item.notes = f"Cuisine: {restaurant.cuisine or 'Regional'} · Rating: {restaurant.rating or 4.0}/5.0"

        elif rep_type in ("attraction", "activity", "sightseeing"):
            attraction = db.get(Attraction, rep_id)
            if not attraction:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Attraction #{rep_id} not found.")
            if attraction.destination_id != trip.destination_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Attraction #{rep_id} does not belong to trip destination #{trip.destination_id}.",
                )
            if target_item.category.lower().strip() not in ("attraction", "attractions", "activity", "activities", "sightseeing", "sight"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot replace a '{target_item.category}' event with an attraction entity.",
                )
            entry = attraction.entry_fee or Decimal("0.00")
            target_item.title = swap_request.title or f"Visit {attraction.name}"
            target_item.category = "attraction"
            target_item.estimated_cost = (entry * trip.traveller_count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            target_item.notes = f"Category: {attraction.category.title() if attraction.category else 'Sight'} · Rating: {attraction.rating or 4.5}/5.0"

        elif rep_type in ("transport", "transportation"):
            transport = db.get(TransportOption, rep_id)
            if not transport:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transport option #{rep_id} not found.")
            if transport.destination_id != trip.destination_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Transport #{rep_id} does not belong to trip destination #{trip.destination_id}.",
                )
            if target_item.category.lower().strip() not in ("transport", "transportation", "transit"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot replace a '{target_item.category}' event with a transport entity.",
                )
            dest_city = trip.destination.city if trip.destination else "Destination"
            target_item.title = swap_request.title or f"Transit from {transport.origin} to {dest_city} ({transport.mode.title()})"
            target_item.category = "transportation"
            target_item.estimated_cost = (transport.estimated_cost * trip.traveller_count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            target_item.notes = f"Provider: {transport.provider or 'Direct'} | Duration: {transport.duration_minutes or 120} mins"

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported replacement type: '{rep_type}'.",
            )

        # 4. Atomic recalculation of budget allocations & trip total
        category_totals = {
            "accommodation": Decimal("0.00"),
            "transportation": Decimal("0.00"),
            "food": Decimal("0.00"),
            "attractions": Decimal("0.00"),
        }
        for day in target_itin.days:
            for itm in day.items:
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
        trip.estimated_total = total_est

        # Update budget allocation records
        for alloc in trip.budget_allocations or []:
            norm_cat = alloc.category.lower().strip()
            if norm_cat in category_totals:
                alloc.amount = category_totals[norm_cat]

        db.commit()
        db.refresh(trip)

        return self.build_trip_detail_response(trip, user_id)


_trip_service = TripService()


def get_trip_service() -> TripService:
    return _trip_service
