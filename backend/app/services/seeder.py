from datetime import date, datetime, time, timezone
from decimal import Decimal
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.db.models import (
    ActivityPreference,
    AIConversation,
    AIMessage,
    Attraction,
    BudgetAllocation,
    Destination,
    Expense,
    Hotel,
    Itinerary,
    ItineraryDay,
    ItineraryItem,
    PackingItem,
    Restaurant,
    Review,
    SavedTrip,
    TransportOption,
    Trip,
    TripAudit,
    TripMember,
    User,
    UserPreference,
    WeatherSnapshot,
)
from app.services.auth_service import hash_password

logger = logging.getLogger("uvicorn.error")


def get_seed_dir() -> Optional[Path]:
    candidates = [
        Path(__file__).resolve().parent.parent.parent.parent / "database" / "seeds",
        Path(__file__).resolve().parent.parent.parent / "database" / "seeds",
        Path(__file__).resolve().parent.parent / "database" / "seeds",
        Path.cwd() / "database" / "seeds",
        Path.cwd().parent / "database" / "seeds",
    ]
    for c in candidates:
        if c.exists() and (c / "hotels_master_d3.json").exists():
            return c
    return None


def ensure_database_programmability(db: Session) -> None:
    """Creates DBMS views, analytical functions, procedures, and audit triggers on PostgreSQL."""
    dialect = db.bind.dialect.name if db.bind else "postgresql"
    if dialect != "postgresql":
        return

    try:
        # 1. Analytical Views
        db.execute(text("""
            CREATE OR REPLACE VIEW v_trip_budget_summary AS
            SELECT t.id AS trip_id, t.user_id, t.total_budget, t.estimated_total,
                   t.total_budget - t.estimated_total AS remaining_budget,
                   (t.estimated_total > t.total_budget) AS is_over_budget
            FROM trips t;
        """))
        db.execute(text("""
            CREATE OR REPLACE VIEW v_destination_catalogue AS
            SELECT d.id, d.city, d.country,
                   COUNT(DISTINCT h.id) AS hotel_count,
                   COUNT(DISTINCT r.id) AS restaurant_count,
                   COUNT(DISTINCT a.id) AS attraction_count
            FROM destinations d
            LEFT JOIN hotels h ON h.destination_id = d.id
            LEFT JOIN restaurants r ON r.destination_id = d.id
            LEFT JOIN attractions a ON a.destination_id = d.id
            GROUP BY d.id, d.city, d.country;
        """))

        # 2. Budget calculation functions
        db.execute(text("""
            CREATE OR REPLACE FUNCTION calculate_trip_estimated_total(p_trip_id bigint)
            RETURNS numeric LANGUAGE sql STABLE AS $$
              SELECT COALESCE((SELECT sum(amount) FROM budget_allocations WHERE trip_id = p_trip_id), 0)
                   + COALESCE((SELECT sum(amount) FROM expenses WHERE trip_id = p_trip_id), 0)
            $$;
        """))
        db.execute(text("""
            CREATE OR REPLACE FUNCTION remaining_trip_budget(p_trip_id bigint)
            RETURNS numeric LANGUAGE sql STABLE AS $$
              SELECT total_budget - calculate_trip_estimated_total(id) FROM trips WHERE id = p_trip_id
            $$;
        """))

        # 3. Trip total refresh procedure
        db.execute(text("""
            CREATE OR REPLACE PROCEDURE refresh_trip_total(p_trip_id bigint)
            LANGUAGE plpgsql AS $$
            BEGIN
              UPDATE trips SET estimated_total = calculate_trip_estimated_total(p_trip_id), updated_at = now() WHERE id = p_trip_id;
              IF NOT FOUND THEN RAISE EXCEPTION 'trip % does not exist', p_trip_id; END IF;
            END $$;
        """))

        # 4. Trip Audit Trigger
        db.execute(text("""
            CREATE OR REPLACE FUNCTION audit_trip_change() RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN
              INSERT INTO trip_audit(trip_id, action, old_row, new_row)
              VALUES(
                COALESCE(NEW.id, OLD.id),
                TG_OP,
                CASE WHEN TG_OP='INSERT' THEN NULL ELSE to_jsonb(OLD) END,
                CASE WHEN TG_OP='DELETE' THEN NULL ELSE to_jsonb(NEW) END
              );
              RETURN COALESCE(NEW, OLD);
            END $$;
        """))
        db.execute(text("""
            DROP TRIGGER IF EXISTS trg_trip_audit ON trips;
            CREATE TRIGGER trg_trip_audit AFTER INSERT OR UPDATE OR DELETE ON trips
            FOR EACH ROW EXECUTE FUNCTION audit_trip_change();
        """))
        db.commit()
        logger.info("Database views, functions, procedures, and audit triggers verified.")
    except Exception as e:
        db.rollback()
        logger.warning("Programmability verification notice: %s", e)


def _bulk_insert(db: Session, model: Any, records: List[Dict[str, Any]], conflict_cols: Optional[List[str]] = None) -> int:
    if not records:
        return 0
    dialect = db.bind.dialect.name if db.bind else "postgresql"
    inserted = 0

    chunk_size = 500
    for i in range(0, len(records), chunk_size):
        chunk = records[i : i + chunk_size]
        if dialect == "postgresql":
            from sqlalchemy.dialects.postgresql import insert as pg_insert

            stmt = pg_insert(model).values(chunk)
            if conflict_cols:
                stmt = stmt.on_conflict_do_nothing(index_elements=conflict_cols)
            else:
                stmt = stmt.on_conflict_do_nothing()
            res = db.execute(stmt)
            inserted += res.rowcount if res.rowcount and res.rowcount > 0 else len(chunk)
        elif dialect == "sqlite":
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert

            stmt = sqlite_insert(model).values(chunk)
            if conflict_cols:
                stmt = stmt.on_conflict_do_nothing(index_elements=conflict_cols)
            else:
                stmt = stmt.on_conflict_do_nothing()
            res = db.execute(stmt)
            inserted += res.rowcount if res.rowcount and res.rowcount > 0 else len(chunk)
        else:
            db.bulk_insert_mappings(model, chunk)
            inserted += len(chunk)

    db.commit()
    return inserted


def get_all_table_counts(db: Session) -> Dict[str, int]:
    """Returns row counts across all 22 domain tables."""
    return {
        "users": db.execute(select(func.count(User.id))).scalar() or 0,
        "user_preferences": db.execute(select(func.count(UserPreference.user_id))).scalar() or 0,
        "activity_preferences": db.execute(select(func.count(ActivityPreference.user_id))).scalar() or 0,
        "destinations": db.execute(select(func.count(Destination.id))).scalar() or 0,
        "hotels": db.execute(select(func.count(Hotel.id))).scalar() or 0,
        "restaurants": db.execute(select(func.count(Restaurant.id))).scalar() or 0,
        "attractions": db.execute(select(func.count(Attraction.id))).scalar() or 0,
        "transport_options": db.execute(select(func.count(TransportOption.id))).scalar() or 0,
        "trips": db.execute(select(func.count(Trip.id))).scalar() or 0,
        "trip_members": db.execute(select(func.count(TripMember.id))).scalar() or 0,
        "itineraries": db.execute(select(func.count(Itinerary.id))).scalar() or 0,
        "itinerary_days": db.execute(select(func.count(ItineraryDay.id))).scalar() or 0,
        "itinerary_items": db.execute(select(func.count(ItineraryItem.id))).scalar() or 0,
        "budget_allocations": db.execute(select(func.count(BudgetAllocation.id))).scalar() or 0,
        "expenses": db.execute(select(func.count(Expense.id))).scalar() or 0,
        "saved_trips": db.execute(select(func.count(SavedTrip.id))).scalar() or 0,
        "reviews": db.execute(select(func.count(Review.id))).scalar() or 0,
        "packing_items": db.execute(select(func.count(PackingItem.id))).scalar() or 0,
        "weather_snapshots": db.execute(select(func.count(WeatherSnapshot.id))).scalar() or 0,
        "ai_conversations": db.execute(select(func.count(AIConversation.id))).scalar() or 0,
        "ai_messages": db.execute(select(func.count(AIMessage.id))).scalar() or 0,
        "trip_audit": db.execute(select(func.count(TripAudit.id))).scalar() or 0,
    }


def get_catalogue_counts(db: Session) -> Dict[str, int]:
    return {
        "destinations": db.execute(select(func.count(Destination.id))).scalar() or 0,
        "hotels": db.execute(select(func.count(Hotel.id))).scalar() or 0,
        "restaurants": db.execute(select(func.count(Restaurant.id))).scalar() or 0,
        "attractions": db.execute(select(func.count(Attraction.id))).scalar() or 0,
        "transport_options": db.execute(select(func.count(TransportOption.id))).scalar() or 0,
    }


def seed_master_catalogues(db: Session, force: bool = False) -> Dict[str, Any]:
    """Populates master catalog files (Destinations, Hotels, Restaurants, Attractions, Transports)."""
    seed_dir = get_seed_dir()
    if not seed_dir:
        logger.warning("Seed directory not found. Master catalogue seeding skipped.")
        return {"status": "error", "message": "Seed directory not found", "counts": get_catalogue_counts(db)}

    stats: Dict[str, Any] = {}

    # 0. Destinations (Must be seeded before child catalogues)
    dest_count = db.execute(select(func.count(Destination.id))).scalar() or 0
    if dest_count < 100 or force:
        d_path = seed_dir / "destinations_master_d1.json"
        if d_path.exists():
            with open(d_path, "r", encoding="utf-8") as f:
                raw_dests = json.load(f)
            records = [
                {
                    "city": d["city"].strip(),
                    "country": d["country"].strip(),
                    "description": d.get("description", ""),
                    "average_daily_cost": Decimal(str(d.get("average_daily_cost", 3500))),
                    "active": d.get("active", True),
                }
                for d in raw_dests
            ]
            stats["destinations_seeded"] = _bulk_insert(db, Destination, records, conflict_cols=["city", "country"])
            logger.info("Seeded %d master destinations.", len(records))

    # Destination mapping cache
    dests = db.execute(select(Destination.id, Destination.city, Destination.country)).all()
    dest_map = {(d.city.strip().lower(), d.country.strip().lower()): d.id for d in dests}
    dest_id_set = {d.id for d in dests}

    # 1. Hotels
    hotel_count = db.execute(select(func.count(Hotel.id))).scalar() or 0
    if hotel_count < 100 or force:
        h_path = seed_dir / "hotels_master_d3.json"
        if h_path.exists():
            with open(h_path, "r", encoding="utf-8") as f:
                raw_hotels = json.load(f)
            records = []
            for h in raw_hotels:
                d_id = dest_map.get((h.get("city", "").strip().lower(), h.get("country", "").strip().lower()))
                if not d_id and h.get("destination_id") in dest_id_set:
                    d_id = h.get("destination_id")
                if d_id:
                    records.append({
                        "destination_id": d_id,
                        "name": h["name"],
                        "price_per_night": Decimal(str(h["price_per_night"])),
                        "rating": Decimal(str(h["rating"])) if h.get("rating") is not None else None,
                    })
            stats["hotels_seeded"] = _bulk_insert(db, Hotel, records, conflict_cols=["destination_id", "name"])
            logger.info("Seeded %d master hotels.", len(records))

    # 2. Restaurants
    rest_count = db.execute(select(func.count(Restaurant.id))).scalar() or 0
    if rest_count < 100 or force:
        r_path = seed_dir / "restaurants_master_d4.json"
        if r_path.exists():
            with open(r_path, "r", encoding="utf-8") as f:
                raw_rests = json.load(f)
            records = []
            for r in raw_rests:
                d_id = dest_map.get((r.get("city", "").strip().lower(), r.get("country", "").strip().lower()))
                if not d_id and r.get("destination_id") in dest_id_set:
                    d_id = r.get("destination_id")
                if d_id:
                    records.append({
                        "destination_id": d_id,
                        "name": r["name"],
                        "cuisine": r.get("cuisine"),
                        "average_cost_per_person": Decimal(str(r["average_cost_per_person"])) if r.get("average_cost_per_person") is not None else None,
                        "rating": Decimal(str(r["rating"])) if r.get("rating") is not None else None,
                    })
            stats["restaurants_seeded"] = _bulk_insert(db, Restaurant, records, conflict_cols=["destination_id", "name"])
            logger.info("Seeded %d master restaurants.", len(records))

    # 3. Attractions
    attr_count = db.execute(select(func.count(Attraction.id))).scalar() or 0
    if attr_count < 100 or force:
        a_path = seed_dir / "attractions_master_d2.json"
        if a_path.exists():
            with open(a_path, "r", encoding="utf-8") as f:
                raw_attrs = json.load(f)
            records = []
            for a in raw_attrs:
                d_id = dest_map.get((a.get("city", "").strip().lower(), a.get("country", "").strip().lower()))
                if not d_id and a.get("destination_id") in dest_id_set:
                    d_id = a.get("destination_id")
                if d_id:
                    records.append({
                        "destination_id": d_id,
                        "name": a["name"],
                        "category": a.get("category"),
                        "entry_fee": Decimal(str(a.get("entry_fee", 0))),
                        "rating": Decimal(str(a["rating"])) if a.get("rating") is not None else None,
                    })
            stats["attractions_seeded"] = _bulk_insert(db, Attraction, records, conflict_cols=["destination_id", "name"])
            logger.info("Seeded %d master attractions.", len(records))

    # 4. Transport Options
    trans_count = db.execute(select(func.count(TransportOption.id))).scalar() or 0
    if trans_count < 100 or force:
        t_path = seed_dir / "transport_master_d5.json"
        if t_path.exists():
            with open(t_path, "r", encoding="utf-8") as f:
                raw_trans = json.load(f)
            records = []
            for t in raw_trans:
                d_id = dest_map.get((t.get("city", "").strip().lower(), t.get("country", "").strip().lower()))
                if not d_id and t.get("destination_id") in dest_id_set:
                    d_id = t.get("destination_id")
                if d_id:
                    records.append({
                        "destination_id": d_id,
                        "origin": t["origin"],
                        "mode": t["mode"],
                        "provider": t.get("provider"),
                        "estimated_cost": Decimal(str(t["estimated_cost"])),
                        "duration_minutes": int(t["duration_minutes"]) if t.get("duration_minutes") is not None else None,
                    })
            stats["transport_seeded"] = _bulk_insert(db, TransportOption, records)
            logger.info("Seeded %d master transport options.", len(records))

    stats["counts"] = get_catalogue_counts(db)
    stats["status"] = "ok"
    return stats


def seed_all_domain_entities(db: Session, force: bool = False) -> Dict[str, Any]:
    """Ensures all 22 domain tables are connected and populated with rich relational sample data."""
    # 1. Verify PostgreSQL views, functions, triggers
    ensure_database_programmability(db)

    # 2. Seed Master Catalogues first (destinations, hotels, restaurants, etc.)
    seed_master_catalogues(db, force=force)

    # 3. Seed Users
    user_count = db.execute(select(func.count(User.id))).scalar() or 0
    if user_count < 5 or force:
        starter_users = [
            ("admin@roamgenie.internal", "AdminPass123!", "System Administrator", "admin"),
            ("traveller@roamgenie.internal", "TravellerPass123!", "Arun Kumar", "traveller"),
            ("ananya@roamgenie.internal", "TravellerPass123!", "Ananya Sharma", "traveller"),
            ("david@roamgenie.internal", "TravellerPass123!", "David Miller", "traveller"),
            ("priya@roamgenie.internal", "TravellerPass123!", "Priya Patel", "traveller"),
        ]
        for email, pwd, name, role in starter_users:
            existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
            if not existing:
                db.add(User(
                    email=email,
                    password_hash=hash_password(pwd),
                    full_name=name,
                    role=role,
                ))
        db.commit()

    # Query user mapping
    user_rows = db.execute(select(User.id, User.email)).all()
    user_map = {u.email: u.id for u in user_rows}
    u_arun = user_map.get("traveller@roamgenie.internal")
    u_ananya = user_map.get("ananya@roamgenie.internal")
    u_david = user_map.get("david@roamgenie.internal")
    u_priya = user_map.get("priya@roamgenie.internal")

    # 4. User Preferences
    pref_count = db.execute(select(func.count(UserPreference.user_id))).scalar() or 0
    if pref_count < 4 or force:
        prefs = [
            (u_arun, "heritage", "South Indian Vegetarian", "train", "cultural", "Near ground floor"),
            (u_ananya, "boutique", "Local Seafood & Multi-cuisine", "flight", "relaxed", "Window seating"),
            (u_david, "luxury", "Continental & Local", "flight", "adventure", "High floor, mountain view"),
            (u_priya, "budget", "Vegetarian Street Food", "train", "backpacking", "Late check-in"),
        ]
        for uid, hotel_p, food_p, trans_p, style_p, reqs in prefs:
            if uid:
                existing = db.execute(select(UserPreference).where(UserPreference.user_id == uid)).scalar_one_or_none()
                if not existing:
                    db.add(UserPreference(
                        user_id=uid,
                        hotel_preference=hotel_p,
                        food_preference=food_p,
                        transport_preference=trans_p,
                        travel_style=style_p,
                        special_requirements=reqs,
                    ))
        db.commit()

    # 5. Activity Preferences (Critical for Q18: Heritage-Focused Travellers)
    act_count = db.execute(select(func.count(ActivityPreference.user_id))).scalar() or 0
    if act_count < 6 or force:
        activity_data = [
            (u_arun, "heritage"),
            (u_arun, "palaces"),
            (u_arun, "temples"),
            (u_ananya, "coastal"),
            (u_ananya, "photography"),
            (u_ananya, "culinary"),
            (u_david, "heritage"),
            (u_david, "wildlife"),
            (u_david, "hiking"),
            (u_priya, "heritage"),
            (u_priya, "local markets"),
            (u_priya, "architecture"),
        ]
        for uid, act in activity_data:
            if uid:
                existing = db.execute(select(ActivityPreference).where(
                    ActivityPreference.user_id == uid,
                    ActivityPreference.activity == act,
                )).scalar_one_or_none()
                if not existing:
                    db.add(ActivityPreference(user_id=uid, activity=act))
        db.commit()

    # Map destinations for trips
    dests = db.execute(select(Destination.id, Destination.city)).all()
    dest_name_map = {d.city.strip().lower(): d.id for d in dests}
    m_dest = dest_name_map.get("mysuru") or dest_name_map.get("mysore") or (dests[0].id if dests else 1)
    k_dest = dest_name_map.get("kochi") or (dests[1].id if len(dests) > 1 else m_dest)
    j_dest = dest_name_map.get("jaipur") or (dests[2].id if len(dests) > 2 else m_dest)
    u_dest = dest_name_map.get("udaipur") or (dests[3].id if len(dests) > 3 else m_dest)
    g_dest = dest_name_map.get("goa") or (dests[4].id if len(dests) > 4 else m_dest)

    # 6. Sample Trips (including one with explicit budget deficit for Q07)
    trip_count = db.execute(select(func.count(Trip.id))).scalar() or 0
    if trip_count < 4 or force:
        trips_to_seed = [
            # Trip 1: In-budget planned trip
            {
                "user_id": u_arun or 1,
                "destination_id": m_dest,
                "starting_location": "Bengaluru",
                "start_date": date(2026, 9, 15),
                "end_date": date(2026, 9, 17),
                "traveller_count": 2,
                "total_budget": Decimal("15000.00"),
                "estimated_total": Decimal("11200.00"),
                "status": "planned",
            },
            # Trip 2: Draft trip
            {
                "user_id": u_ananya or 1,
                "destination_id": k_dest,
                "starting_location": "Bengaluru",
                "start_date": date(2026, 10, 1),
                "end_date": date(2026, 10, 4),
                "traveller_count": 2,
                "total_budget": Decimal("25000.00"),
                "estimated_total": Decimal("19800.00"),
                "status": "draft",
            },
            # Trip 3: Budget Deficit Trip (estimated > budget, deficit = 4,500) for Q07
            {
                "user_id": u_david or 1,
                "destination_id": j_dest,
                "starting_location": "Delhi",
                "start_date": date(2026, 11, 10),
                "end_date": date(2026, 11, 13),
                "traveller_count": 2,
                "total_budget": Decimal("20000.00"),
                "estimated_total": Decimal("24500.00"),
                "status": "planned",
            },
            # Trip 4: Completed trip
            {
                "user_id": u_priya or 1,
                "destination_id": u_dest,
                "starting_location": "Mumbai",
                "start_date": date(2026, 12, 5),
                "end_date": date(2026, 12, 8),
                "traveller_count": 1,
                "total_budget": Decimal("18000.00"),
                "estimated_total": Decimal("17200.00"),
                "status": "completed",
            },
        ]
        for t_data in trips_to_seed:
            db.add(Trip(**t_data))
        db.commit()

    all_trips = db.execute(select(Trip.id, Trip.user_id, Trip.destination_id)).all()
    t_ids = [t.id for t in all_trips]

    # 7. Trip Members
    if t_ids and (db.execute(select(func.count(TripMember.id))).scalar() or 0) < 4:
        db.add_all([
            TripMember(trip_id=t_ids[0], display_name="Arun Kumar", age_group="adult", special_requirements="Lead traveller"),
            TripMember(trip_id=t_ids[0], display_name="Suresh Kumar", age_group="senior", special_requirements="Ground floor room required"),
            TripMember(trip_id=t_ids[1], display_name="Ananya Sharma", age_group="adult", special_requirements="Lead traveller"),
            TripMember(trip_id=t_ids[1], display_name="Pooja Sharma", age_group="adult", special_requirements=None),
            TripMember(trip_id=t_ids[2], display_name="David Miller", age_group="adult", special_requirements="Lead traveller"),
            TripMember(trip_id=t_ids[2], display_name="Sarah Miller", age_group="adult", special_requirements="Vegetarian meal request"),
        ])
        db.commit()

    # 8. Itineraries, Itinerary Days, and Itinerary Items (Critical for Q10)
    itin_count = db.execute(select(func.count(Itinerary.id))).scalar() or 0
    if t_ids and itin_count < 2:
        itin1 = Itinerary(trip_id=t_ids[0], version=1, summary="3-Day Cultural & Royal Heritage Tour of Mysuru", provider="mock")
        itin2 = Itinerary(trip_id=t_ids[1], version=1, summary="4-Day Coastal Spice & Heritage Journey in Fort Kochi", provider="mock")
        db.add_all([itin1, itin2])
        db.commit()
        db.refresh(itin1)
        db.refresh(itin2)

        d1 = ItineraryDay(itinerary_id=itin1.id, day_number=1, itinerary_date=date(2026, 9, 15))
        d2 = ItineraryDay(itinerary_id=itin1.id, day_number=2, itinerary_date=date(2026, 9, 16))
        d3 = ItineraryDay(itinerary_id=itin1.id, day_number=3, itinerary_date=date(2026, 9, 17))
        kd1 = ItineraryDay(itinerary_id=itin2.id, day_number=1, itinerary_date=date(2026, 10, 1))
        db.add_all([d1, d2, d3, kd1])
        db.commit()
        db.refresh(d1)
        db.refresh(d2)
        db.refresh(d3)
        db.refresh(kd1)

        db.add_all([
            ItineraryItem(itinerary_day_id=d1.id, item_order=1, start_time=time(9, 0), title="Check-in at Heritage Garden Stay", category="hotel", estimated_cost=Decimal("2800.00"), notes="Confirm room on ground floor"),
            ItineraryItem(itinerary_day_id=d1.id, item_order=2, start_time=time(11, 0), title="Explore Mysuru Palace & Durbar Hall", category="attraction", estimated_cost=Decimal("200.00"), notes="Audio guide included"),
            ItineraryItem(itinerary_day_id=d1.id, item_order=3, start_time=time(13, 30), title="Lunch at Mylari Tiffin House", category="food", estimated_cost=Decimal("500.00"), notes="Famous butter dosas"),
            ItineraryItem(itinerary_day_id=d1.id, item_order=4, start_time=time(16, 0), title="Visit Chamundi Hill & Temple", category="attraction", estimated_cost=Decimal("0.00"), notes="Panoramic view over Mysuru"),
            ItineraryItem(itinerary_day_id=d2.id, item_order=1, start_time=time(10, 0), title="Brindavan Gardens Walk & Fountains", category="attraction", estimated_cost=Decimal("100.00"), notes="Evening lighting"),
            ItineraryItem(itinerary_day_id=d2.id, item_order=2, start_time=time(19, 30), title="Dinner at Gufha Cave Dining", category="food", estimated_cost=Decimal("1300.00"), notes="Cave themed ambiance"),
            ItineraryItem(itinerary_day_id=d3.id, item_order=1, start_time=time(10, 30), title="Silk & Sandalwood Market Walk", category="shopping", estimated_cost=Decimal("1500.00"), notes="Devaraja Market"),
            ItineraryItem(itinerary_day_id=kd1.id, item_order=1, start_time=time(10, 0), title="Fort Kochi Chinese Fishing Nets", category="attraction", estimated_cost=Decimal("0.00"), notes="Morning fisherman view"),
            ItineraryItem(itinerary_day_id=kd1.id, item_order=2, start_time=time(13, 0), title="Lunch at Kashi Art Cafe", category="food", estimated_cost=Decimal("600.00"), notes="Art gallery dining"),
        ])
        db.commit()

    # 9. Budget Allocations (Critical for Q13: Window Function PARTITION BY)
    alloc_count = db.execute(select(func.count(BudgetAllocation.id))).scalar() or 0
    if t_ids and alloc_count < 8:
        for tid in t_ids[:3]:
            existing_for_trip = db.execute(select(func.count(BudgetAllocation.id)).where(BudgetAllocation.trip_id == tid)).scalar() or 0
            if existing_for_trip == 0:
                db.add_all([
                    BudgetAllocation(trip_id=tid, category="accommodation", amount=Decimal("5600.00")),
                    BudgetAllocation(trip_id=tid, category="food", amount=Decimal("2800.00")),
                    BudgetAllocation(trip_id=tid, category="activities", amount=Decimal("1200.00")),
                    BudgetAllocation(trip_id=tid, category="transportation", amount=Decimal("1600.00")),
                ])
        db.commit()

    # 10. Expenses (Critical for Q06: Grouping & Aggregations)
    exp_count = db.execute(select(func.count(Expense.id))).scalar() or 0
    if t_ids and exp_count < 4:
        for idx, tid in enumerate(t_ids[:3]):
            existing_exp = db.execute(select(func.count(Expense.id)).where(Expense.trip_id == tid)).scalar() or 0
            if existing_exp == 0:
                db.add_all([
                    Expense(trip_id=tid, category="transportation", description="Train & Transit Tickets", amount=Decimal("1100.00"), incurred_on=date(2026, 9, 15)),
                    Expense(trip_id=tid, category="food", description="Station Meals & Coffee", amount=Decimal("350.00"), incurred_on=date(2026, 9, 15)),
                    Expense(trip_id=tid, category="accommodation", description="Hotel Advance Deposit", amount=Decimal("2800.00"), incurred_on=date(2026, 9, 16)),
                    Expense(trip_id=tid, category="activities", description="Museum & Heritage Entry Pass", amount=Decimal("450.00"), incurred_on=date(2026, 9, 16)),
                ])
        db.commit()

    # 11. Saved Trips (Critical for Q11: Bookmarks per User)
    saved_count = db.execute(select(func.count(SavedTrip.id))).scalar() or 0
    if t_ids and saved_count < 4:
        bookmarks = [
            (u_arun or 1, t_ids[0]),
            (u_arun or 1, t_ids[1] if len(t_ids) > 1 else t_ids[0]),
            (u_ananya or 1, t_ids[1] if len(t_ids) > 1 else t_ids[0]),
            (u_david or 1, t_ids[2] if len(t_ids) > 2 else t_ids[0]),
        ]
        for uid, tid in bookmarks:
            existing = db.execute(select(SavedTrip).where(SavedTrip.user_id == uid, SavedTrip.trip_id == tid)).scalar_one_or_none()
            if not existing:
                db.add(SavedTrip(user_id=uid, trip_id=tid))
        db.commit()

    # 12. Reviews (Critical for Q12: Destination Review Ratings)
    review_count = db.execute(select(func.count(Review.id))).scalar() or 0
    if review_count < 4:
        reviews_to_seed = [
            (u_arun or 1, m_dest, 5, "Magnificent heritage city, peaceful atmosphere and amazing royal architecture!"),
            (u_ananya or 1, k_dest, 5, "Spectacular coastal scenery, colonial spice warehouses, and wonderful local cafes."),
            (u_david or 1, j_dest, 5, "Opulent hilltop forts, intricate havelis, and unmatched Rajasthani hospitality."),
            (u_priya or 1, u_dest, 5, "City of Lakes surrounded by majestic Aravalli hills, truly royal."),
        ]
        for uid, did, rating, comment in reviews_to_seed:
            existing = db.execute(select(Review).where(Review.user_id == uid, Review.destination_id == did)).scalar_one_or_none()
            if not existing:
                db.add(Review(user_id=uid, destination_id=did, rating=rating, comment=comment))
        db.commit()

    # 13. Packing Items (Critical for Q14: Conditional Aggregates)
    packing_count = db.execute(select(func.count(PackingItem.id))).scalar() or 0
    if t_ids and packing_count < 4:
        for tid in t_ids[:2]:
            existing_pack = db.execute(select(func.count(PackingItem.id)).where(PackingItem.trip_id == tid)).scalar() or 0
            if existing_pack == 0:
                db.add_all([
                    PackingItem(trip_id=tid, item="Comfortable Walking Shoes", category="clothing", is_packed=True),
                    PackingItem(trip_id=tid, item="Camera & Extra Battery", category="electronics", is_packed=True),
                    PackingItem(trip_id=tid, item="Essential Travel Medicines", category="essentials", is_packed=False),
                    PackingItem(trip_id=tid, item="Lightweight Linen Shirt", category="clothing", is_packed=False),
                ])
        db.commit()

    # 14. Weather Snapshots (Critical for Q17: Destination Weather Observations)
    weather_count = db.execute(select(func.count(WeatherSnapshot.id))).scalar() or 0
    if weather_count < 5:
        now_utc = datetime.now(timezone.utc)
        snapshots = [
            (m_dest, "Partly cloudy with pleasant evening breeze", Decimal("24.5")),
            (k_dest, "Humid coastal sunshine with light sea breeze", Decimal("29.0")),
            (j_dest, "Dry sunny day with warm afternoon", Decimal("32.0")),
            (u_dest, "Clear skies over lake waters", Decimal("27.5")),
            (g_dest, "Tropical sunshine with moderate humidity", Decimal("30.0")),
        ]
        for did, summ, temp in snapshots:
            db.add(WeatherSnapshot(
                destination_id=did,
                observed_at=now_utc,
                summary=summ,
                temperature_c=temp,
                provider="mock",
            ))
        db.commit()

    # 15. AI Conversations & Messages (Critical for Q15: AI Interaction Volume)
    conv_count = db.execute(select(func.count(AIConversation.id))).scalar() or 0
    if conv_count < 3:
        c1 = AIConversation(user_id=u_arun or 1, trip_id=t_ids[0] if t_ids else None)
        c2 = AIConversation(user_id=u_ananya or 1, trip_id=t_ids[1] if len(t_ids) > 1 else None)
        c3 = AIConversation(user_id=u_david or 1, trip_id=t_ids[2] if len(t_ids) > 2 else None)
        db.add_all([c1, c2, c3])
        db.commit()
        db.refresh(c1)
        db.refresh(c2)
        db.refresh(c3)

        db.add_all([
            AIMessage(conversation_id=c1.id, role="user", content="Can you recommend heritage sights near Mysuru Palace?"),
            AIMessage(conversation_id=c1.id, role="assistant", content="Certainly! Sri Chamarajendra Art Gallery, Jaganmohan Palace, and Chamundi Hill are all within a 20-minute drive."),
            AIMessage(conversation_id=c2.id, role="user", content="What is the best time to see the Chinese Fishing Nets in Fort Kochi?"),
            AIMessage(conversation_id=c2.id, role="assistant", content="Sunset around 5:30 PM offers golden hour lighting and scenic maritime views."),
            AIMessage(conversation_id=c3.id, role="user", content="How should I budget for Amber Fort and Hawa Mahal in Jaipur?"),
            AIMessage(conversation_id=c3.id, role="assistant", content="The Rajasthan Tourism composite ticket covers Amber Fort, Hawa Mahal, and Jantar Mantar at a bundled discount."),
        ])
        db.commit()

    logger.info("All 22 domain relational entities verified and populated successfully.")
    return {
        "status": "ok",
        "counts": get_all_table_counts(db),
    }
