import logging
from datetime import datetime, time, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models.catalogue import Attraction, Hotel, Restaurant, TransportOption
from app.db.models.trip import Itinerary, ItineraryDay, Trip
from app.services.budget_service import BudgetCalculator
from app.services.itinerary_scheduler import ScheduledDay, ScheduledItem

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Gemini Tool Declarations (OpenAPI-compatible function declarations)
# ---------------------------------------------------------------------------

CHAT_TOOL_DECLARATIONS = [
    {
        "name": "get_travel_history",
        "description": "Retrieves the authenticated user's travel history including all past, current, and planned trips.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_itinerary_details",
        "description": "Fetches the complete day-by-day itinerary schedule, all activities/items, and current budget breakdown for a specific trip.",
        "parameters": {
            "type": "object",
            "properties": {
                "trip_id": {
                    "type": "integer",
                    "description": "The unique ID of the trip to inspect.",
                }
            },
            "required": ["trip_id"],
        },
    },
    {
        "name": "propose_itinerary_modification",
        "description": "Simulates a proposed modification to an itinerary item (such as swapping a hotel, restaurant, or attraction, or removing an activity) and calculates the exact budget impact (new estimated total, savings, deficit) without altering the database.",
        "parameters": {
            "type": "object",
            "properties": {
                "trip_id": {
                    "type": "integer",
                    "description": "The unique ID of the trip.",
                },
                "action": {
                    "type": "string",
                    "description": "The type of modification: 'swap', 'remove', 'clear_day', or 'add'.",
                    "enum": ["swap", "remove", "clear_day", "add"],
                },
                "item_id": {
                    "type": "integer",
                    "description": "The ID of the itinerary item being swapped or removed (optional when clearing an entire day).",
                },
                "day_number": {
                    "type": "integer",
                    "description": "The day number (1-based) to clear or add an activity to.",
                },
                "replacement_type": {
                    "type": "string",
                    "description": "The category of the catalogue replacement entity ('hotel', 'restaurant', 'attraction', 'transport').",
                    "enum": ["hotel", "restaurant", "attraction", "transport"],
                },
                "replacement_id": {
                    "type": "integer",
                    "description": "The database ID of the replacement entity from the destination catalogue.",
                },
                "title": {
                    "type": "string",
                    "description": "Optional title for the replacement activity.",
                },
            },
            "required": ["trip_id", "action"],
        },
    },
]


# ---------------------------------------------------------------------------
# Tool Executors
# ---------------------------------------------------------------------------

def get_travel_history(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Retrieves a summary of all trips (planned, ongoing, completed, draft)
    strictly belonging to the authenticated user.
    """
    stmt = (
        select(Trip)
        .where(Trip.user_id == user_id)
        .options(selectinload(Trip.destination))
        .order_by(Trip.start_date.desc())
    )
    trips = db.execute(stmt).scalars().all()
    results = []
    for t in trips:
        results.append({
            "id": t.id,
            "destination_city": t.destination.city if t.destination else None,
            "destination_country": t.destination.country if t.destination else None,
            "starting_location": t.starting_location,
            "start_date": str(t.start_date),
            "end_date": str(t.end_date),
            "traveller_count": t.traveller_count,
            "total_budget": float(t.total_budget),
            "estimated_total": float(t.estimated_total),
            "status": t.status,
        })
    return {
        "trips": results,
        "total_trips": len(results),
    }


def get_itinerary_details(db: Session, user_id: int, trip_id: int) -> Dict[str, Any]:
    """
    Fetches the full schedule, daily items, and current budget allocations
    for a trip, enforcing strict user ownership (IDOR prevention).
    """
    stmt = (
        select(Trip)
        .where(Trip.id == trip_id)
        .options(
            selectinload(Trip.destination),
            selectinload(Trip.budget_allocations),
            selectinload(Trip.itineraries).selectinload(Itinerary.days).selectinload(ItineraryDay.items),
        )
    )
    trip = db.execute(stmt).scalar_one_or_none()

    if not trip:
        return {"error": f"Trip #{trip_id} not found."}
    if trip.user_id != user_id:
        return {"error": "Access denied: You do not have permission to view this trip."}

    days_data = []
    if trip.itineraries:
        latest_itin = sorted(trip.itineraries, key=lambda i: i.version, reverse=True)[0]
        for d in sorted(latest_itin.days, key=lambda day: day.day_number):
            items_data = []
            for item in sorted(d.items, key=lambda itm: itm.item_order):
                items_data.append({
                    "id": item.id,
                    "item_order": item.item_order,
                    "time": item.start_time.strftime("%H:%M") if item.start_time else "09:00",
                    "title": item.title,
                    "category": item.category,
                    "estimated_cost": float(item.estimated_cost),
                    "notes": item.notes,
                })
            days_data.append({
                "day_number": d.day_number,
                "date": str(d.itinerary_date),
                "items": items_data,
            })

    allocations = {
        alloc.category: float(alloc.amount)
        for alloc in (trip.budget_allocations or [])
    }

    remaining = float(trip.total_budget - trip.estimated_total)
    deficit = float(max(Decimal("0.00"), trip.estimated_total - trip.total_budget))

    return {
        "trip_id": trip.id,
        "destination": f"{trip.destination.city}, {trip.destination.country}" if trip.destination else None,
        "start_date": str(trip.start_date),
        "end_date": str(trip.end_date),
        "traveller_count": trip.traveller_count,
        "total_budget": float(trip.total_budget),
        "estimated_total": float(trip.estimated_total),
        "remaining_budget": remaining,
        "deficit": deficit,
        "status": trip.status,
        "budget_allocations": allocations,
        "days": days_data,
    }


def propose_itinerary_modification(
    db: Session,
    user_id: int,
    trip_id: int,
    action: str,
    item_id: Optional[int] = None,
    replacement_type: Optional[str] = None,
    replacement_id: Optional[int] = None,
    title: Optional[str] = None,
    day_number: Optional[int] = None,
    new_category: Optional[str] = None,
    estimated_cost: Optional[float | Decimal] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Simulates a structured itinerary change (swap, remove, or add item) without committing
    to the database. Recalculates the new estimated_total, category allocations, and budget deficit.
    Returns a proposal dictionary ready for user confirmation.
    """
    # 1. Fetch trip and verify ownership
    stmt = (
        select(Trip)
        .where(Trip.id == trip_id)
        .options(
            selectinload(Trip.destination),
            selectinload(Trip.budget_allocations),
            selectinload(Trip.itineraries).selectinload(Itinerary.days).selectinload(ItineraryDay.items),
        )
    )
    trip = db.execute(stmt).scalar_one_or_none()

    if not trip:
        return {"error": f"Trip #{trip_id} not found."}
    if trip.user_id != user_id:
        return {"error": "Access denied: You do not have permission to modify this trip."}
    if not trip.itineraries:
        return {"error": f"Trip #{trip_id} has no generated itinerary to modify."}

    latest_itin = sorted(trip.itineraries, key=lambda i: i.version, reverse=True)[0]
    action_clean = action.lower().strip()

    # 2. Locate target item for swap, remove, or day clearing
    target_item = None
    target_day = None
    if action_clean in ("clear_day", "clear") or (action_clean == "remove" and day_number is not None and not item_id):
        action_clean = "clear_day"
        for d in latest_itin.days:
            if d.day_number == day_number:
                target_day = d
                break
        if not target_day:
            return {"error": f"Day {day_number} not found on trip #{trip_id}."}
        if not target_day.items:
            return {"error": f"Day {day_number} has no scheduled activities to cancel."}
    elif action_clean in ("swap", "remove"):
        if not item_id:
            return {"error": f"item_id is required for action '{action_clean}'."}
        for d in latest_itin.days:
            for itm in d.items:
                if itm.id == item_id:
                    target_item = itm
                    target_day = d
                    break
            if target_item:
                break
        if not target_item:
            return {"error": f"Itinerary item #{item_id} not found on trip #{trip_id}."}

    # 3. Resolve replacement entity if swapping
    rep_title = title or "Custom Item"
    rep_category = new_category or (target_item.category if target_item else "other")
    rep_cost = Decimal("0.00")
    rep_notes = notes or ""

    if action_clean == "swap":
        if replacement_type and replacement_id is not None:
            rep_type_clean = replacement_type.lower().strip()
            if rep_type_clean in ("hotel", "accommodation"):
                hotel = db.get(Hotel, replacement_id)
                if not hotel:
                    return {"error": f"Hotel #{replacement_id} does not exist in the catalogue. Please choose a valid accommodation."}
                if hotel.destination_id != trip.destination_id:
                    return {"error": f"Hotel #{replacement_id} does not belong to trip destination #{trip.destination_id}."}
                rep_title = title or f"Overnight Stay at {hotel.name}"
                rep_category = "accommodation"
                rep_cost = hotel.price_per_night
                rep_notes = f"Tariff: ₹{hotel.price_per_night}/night · Rating: {hotel.rating or 4.0}/5.0"

            elif rep_type_clean in ("restaurant", "food", "dining"):
                restaurant = db.get(Restaurant, replacement_id)
                if not restaurant:
                    return {"error": f"Restaurant #{replacement_id} does not exist in the catalogue. Please choose a valid dining option."}
                if restaurant.destination_id != trip.destination_id:
                    return {"error": f"Restaurant #{replacement_id} does not belong to trip destination #{trip.destination_id}."}
                avg_cost = restaurant.average_cost_per_person or Decimal("250.00")
                rep_title = title or f"Dining at {restaurant.name}"
                rep_category = "food"
                rep_cost = (avg_cost * trip.traveller_count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                rep_notes = f"Cuisine: {restaurant.cuisine or 'Regional'} · Rating: {restaurant.rating or 4.0}/5.0"

            elif rep_type_clean in ("attraction", "activity", "sightseeing"):
                attraction = db.get(Attraction, replacement_id)
                if not attraction:
                    return {"error": f"Attraction #{replacement_id} does not exist in the catalogue. Please choose a valid attraction."}
                if attraction.destination_id != trip.destination_id:
                    return {"error": f"Attraction #{replacement_id} does not belong to trip destination #{trip.destination_id}."}
                fee = attraction.entry_fee or Decimal("0.00")
                rep_title = title or f"Visit {attraction.name}"
                rep_category = "attractions"
                rep_cost = (fee * trip.traveller_count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                rep_notes = f"Entry Fee: ₹{fee}/person · Rating: {attraction.rating or 4.5}/5.0"

            elif rep_type_clean in ("transport", "transportation"):
                transport = db.get(TransportOption, replacement_id)
                if not transport:
                    return {"error": f"Transport option #{replacement_id} does not exist in the catalogue. Please choose a valid transport option."}
                if transport.destination_id != trip.destination_id:
                    return {"error": f"Transport #{replacement_id} does not belong to trip destination #{trip.destination_id}."}
                rep_title = title or f"Transit ({transport.mode.title()}) from {transport.origin}"
                rep_category = "transportation"
                rep_cost = (transport.estimated_cost * trip.traveller_count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                rep_notes = f"Provider: {transport.provider or 'Local'} · Duration: {transport.duration_minutes or 60}m"
            else:
                return {
                    "error": f"Invalid replacement category '{replacement_type}'. Supported categories are hotel, restaurant, attraction, or transport."
                }
        elif replacement_type and replacement_id is None:
            return {"error": f"A replacement_id is required when specifying replacement_type '{replacement_type}'."}
        elif estimated_cost is not None:
            rep_cost = Decimal(str(estimated_cost)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            rep_title = title or target_item.title
            rep_category = new_category or target_item.category

    # 4. Simulate the day-by-day schedule in memory without DB mutations
    simulated_days: List[ScheduledDay] = []
    for d in latest_itin.days:
        sim_items: List[ScheduledItem] = []
        if action_clean == "clear_day" and d.day_number == day_number:
            # Clear all scheduled items on this specific day
            pass
        else:
            for itm in d.items:
                if action_clean == "swap" and itm.id == item_id:
                    sim_items.append(
                        ScheduledItem(
                            item_order=itm.item_order,
                            start_time=itm.start_time or time(9, 0),
                            title=rep_title,
                            category=rep_category,
                            estimated_cost=rep_cost,
                            notes=rep_notes,
                        )
                    )
                elif action_clean == "remove" and itm.id == item_id:
                    continue
                else:
                    sim_items.append(
                        ScheduledItem(
                            item_order=itm.item_order,
                            start_time=itm.start_time or time(9, 0),
                            title=itm.title,
                            category=itm.category,
                            estimated_cost=itm.estimated_cost,
                            notes=itm.notes,
                        )
                    )

        if action_clean == "add" and d.day_number == (day_number or 1):
            add_cost = Decimal(str(estimated_cost or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            sim_items.append(
                ScheduledItem(
                    item_order=len(sim_items) + 1,
                    start_time=time(14, 0),
                    title=title or "New Activity",
                    category=new_category or "attractions",
                    estimated_cost=add_cost,
                    notes=notes or "",
                )
            )

        simulated_days.append(
            ScheduledDay(
                day_number=d.day_number,
                itinerary_date=d.itinerary_date,
                items=sim_items,
            )
        )

    # 5. Calculate new budget impact
    calculator = BudgetCalculator()
    calc_res = calculator.calculate(
        total_budget=trip.total_budget,
        scheduled_days=simulated_days,
    )

    cost_delta = calc_res.estimated_total - trip.estimated_total
    savings = max(Decimal("0.00"), -cost_delta)
    extra_cost = max(Decimal("0.00"), cost_delta)

    # Roll back session state to guarantee ZERO unintended flushes
    db.rollback()

    # 6. Build summary narrative
    if action_clean == "clear_day" and target_day:
        day_savings = sum((itm.estimated_cost for itm in target_day.items), Decimal("0.00"))
        summary = (
            f"Proposed cancellation of all {len(target_day.items)} plan(s) for Day {day_number} "
            f"(saving ₹{day_savings:,.2f}). New estimated total: ₹{calc_res.estimated_total:,.2f}."
        )
    elif action_clean == "swap" and target_item:
        if savings > Decimal("0.00"):
            impact_desc = f"reduces your trip total by ₹{savings:,.2f}"
        elif extra_cost > Decimal("0.00"):
            impact_desc = f"increases your trip total by ₹{extra_cost:,.2f}"
        else:
            impact_desc = "keeps your trip total unchanged"
        summary = (
            f"Proposed swap of '{target_item.title}' (₹{target_item.estimated_cost:,.2f}) "
            f"with '{rep_title}' (₹{rep_cost:,.2f}), which {impact_desc}. "
            f"New estimated total: ₹{calc_res.estimated_total:,.2f}."
        )
    elif action_clean == "remove" and target_item:
        summary = (
            f"Proposed removal of '{target_item.title}' (saving ₹{target_item.estimated_cost:,.2f}). "
            f"New estimated total: ₹{calc_res.estimated_total:,.2f}."
        )
    else:
        summary = f"Simulated {action_clean} on trip #{trip_id}. New estimated total: ₹{calc_res.estimated_total:,.2f}."

    proposal_data = {
        "proposal_id": f"prop-{trip_id}-{int(datetime.now(timezone.utc).timestamp())}",
        "trip_id": trip_id,
        "action": action_clean,
        "target_item_id": item_id,
        "target_day_number": day_number if action_clean == "clear_day" else (target_day.day_number if target_day else None),
        "day_number": day_number,
        "original_item": {
            "id": target_item.id,
            "title": target_item.title,
            "category": target_item.category,
            "estimated_cost": float(target_item.estimated_cost),
        } if target_item else None,
        "proposed_item": {
            "title": rep_title,
            "category": rep_category,
            "estimated_cost": float(rep_cost),
            "replacement_type": replacement_type,
            "replacement_id": replacement_id,
        } if action_clean not in ("remove", "clear_day") else None,
        "budget_impact": {
            "total_budget": float(trip.total_budget),
            "original_estimated_total": float(trip.estimated_total),
            "proposed_estimated_total": float(calc_res.estimated_total),
            "cost_delta": float(cost_delta),
            "savings": float(savings),
            "extra_cost": float(extra_cost),
            "original_deficit": float(max(Decimal("0.00"), trip.estimated_total - trip.total_budget)),
            "proposed_deficit": float(calc_res.deficit),
            "proposed_remaining_budget": float(calc_res.remaining_budget),
            "status": calc_res.status,
            "category_totals": {
                cat: float(val) for cat, val in calc_res.category_totals.items()
            },
        },
        "summary": summary,
        "requires_user_confirmation": True,
    }

    return proposal_data


def execute_chat_tool(
    name: str,
    args: Dict[str, Any],
    db: Session,
    user_id: int,
) -> Dict[str, Any]:
    """
    Central dispatcher routing LLM function calls to tool implementations
    with mandatory user_id scoping for IDOR prevention.
    """
    logger.info(f"Executing tool '{name}' for user_id={user_id} with args: {args}")
    try:
        if name == "get_travel_history":
            return get_travel_history(db=db, user_id=user_id)
        elif name == "get_itinerary_details":
            try:
                trip_id = int(args.get("trip_id", 0))
            except (ValueError, TypeError):
                return {"error": f"Invalid trip_id: {args.get('trip_id')}. Please provide a numeric trip ID."}
            return get_itinerary_details(db=db, user_id=user_id, trip_id=trip_id)
        elif name == "propose_itinerary_modification":
            try:
                trip_id = int(args.get("trip_id", 0))
            except (ValueError, TypeError):
                return {"error": f"Invalid trip_id: {args.get('trip_id')}. Please provide a numeric trip ID."}

            action = str(args.get("action", "swap"))

            try:
                item_id = int(args["item_id"]) if args.get("item_id") is not None else None
            except (ValueError, TypeError):
                return {"error": f"Invalid item_id: {args.get('item_id')}. Please provide a numeric item ID."}

            replacement_type = args.get("replacement_type")

            try:
                replacement_id = int(args["replacement_id"]) if args.get("replacement_id") is not None else None
            except (ValueError, TypeError):
                return {"error": f"Invalid replacement_id: {args.get('replacement_id')}. Please provide a numeric replacement ID."}

            title = args.get("title")

            try:
                day_number = int(args["day_number"]) if args.get("day_number") is not None else None
            except (ValueError, TypeError):
                day_number = None

            new_category = args.get("new_category")
            estimated_cost = args.get("estimated_cost")
            notes = args.get("notes")

            return propose_itinerary_modification(
                db=db,
                user_id=user_id,
                trip_id=trip_id,
                action=action,
                item_id=item_id,
                replacement_type=replacement_type,
                replacement_id=replacement_id,
                title=title,
                day_number=day_number,
                new_category=new_category,
                estimated_cost=estimated_cost,
                notes=notes,
            )
        else:
            return {"error": f"Unknown tool: '{name}'"}
    except Exception as exc:
        logger.exception(f"Error executing chat tool '{name}': {exc}")
        return {"error": f"Tool execution failed: {str(exc)}"}
