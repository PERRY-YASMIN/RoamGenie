from datetime import date, datetime, time, timezone
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
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
from app.db.session import database_status
from app.services.auth_service import hash_password, verify_password


EXPECTED_ENTITIES = [
    "users",
    "user_preferences",
    "activity_preferences",
    "destinations",
    "hotels",
    "restaurants",
    "attractions",
    "transport_options",
    "trips",
    "trip_members",
    "itineraries",
    "itinerary_days",
    "itinerary_items",
    "budget_allocations",
    "expenses",
    "saved_trips",
    "reviews",
    "packing_items",
    "ai_conversations",
    "ai_messages",
    "weather_snapshots",
    "trip_audit",
]


def test_1_database_connectivity_and_status(db_session: Session):
    """Verify database connection is reachable and executes basic queries."""
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_2_schema_availability_all_22_tables(db_session: Session):
    """Verify all 22 required domain, financial, AI, and audit entities are registered in ORM schema."""
    engine = db_session.get_bind()
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    for entity in EXPECTED_ENTITIES:
        assert entity in table_names, f"Table '{entity}' missing from database schema."


def test_3_user_creation_and_credential_security(db_session: Session):
    """Verify user creation, Argon2id password hashing, and user preference persistence."""
    email = "postgres_user@example.test"
    raw_password = "SecurePassword2026!"
    hashed = hash_password(raw_password)

    # Verify hash is never plaintext
    assert hashed != raw_password
    assert "$argon2id$" in hashed

    user = User(
        email=email,
        password_hash=hashed,
        full_name="PostgreSQL Integration Tester",
        role="traveller",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert verify_password(raw_password, user.password_hash) is True
    assert verify_password("WrongPassword!", user.password_hash) is False

    # User Preferences
    pref = UserPreference(
        user_id=user.id,
        hotel_preference="heritage",
        food_preference="Vegetarian",
        travel_style="cultural",
    )
    act = ActivityPreference(user_id=user.id, activity="palaces")
    db_session.add_all([pref, act])
    db_session.commit()

    saved_user = db_session.get(User, user.id)
    assert saved_user.preference.hotel_preference == "heritage"
    assert len(saved_user.activity_preferences) == 1


def test_4_destination_and_catalogue_retrieval(db_session: Session):
    """Verify catalogue insertion and relational lookups across hotels, dining, attractions, transit."""
    dest = Destination(
        city="Hampi",
        country="India",
        description="UNESCO World Heritage ancient ruins",
        average_daily_cost=Decimal("3000.00"),
        active=True,
    )
    db_session.add(dest)
    db_session.commit()
    db_session.refresh(dest)

    hotel = Hotel(destination_id=dest.id, name="Boulders Resort", price_per_night=Decimal("2500.00"), rating=Decimal("4.5"))
    rest = Restaurant(destination_id=dest.id, name="Mango Tree Restaurant", cuisine="South Indian", average_cost_per_person=Decimal("250.00"), rating=Decimal("4.6"))
    att = Attraction(destination_id=dest.id, name="Virupaksha Temple", category="heritage", entry_fee=Decimal("50.00"), rating=Decimal("4.9"))
    trans = TransportOption(origin="Bengaluru", destination_id=dest.id, mode="train", provider="Hampi Express", estimated_cost=Decimal("400.00"), duration_minutes=420)

    db_session.add_all([hotel, rest, att, trans])
    db_session.commit()

    queried_dest = db_session.get(Destination, dest.id)
    assert len(queried_dest.hotels) == 1
    assert len(queried_dest.restaurants) == 1
    assert len(queried_dest.attractions) == 1
    assert len(queried_dest.transport_options) == 1


def test_5_trip_and_versioned_itinerary_creation(db_session: Session):
    """Verify trip lifecycle, day scheduling, and multi-table transactional persistence."""
    u = User(email="trip_author@example.test", password_hash=hash_password("pw"), full_name="Trip Author")
    d = Destination(city="Coorg", country="India", description="Coffee hills", average_daily_cost=Decimal("4000.00"))
    db_session.add_all([u, d])
    db_session.commit()

    trip = Trip(
        user_id=u.id,
        destination_id=d.id,
        starting_location="Mysuru",
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 3),
        traveller_count=2,
        total_budget=Decimal("18000.00"),
        estimated_total=Decimal("14200.00"),
        status="planned",
    )
    db_session.add(trip)
    db_session.commit()
    db_session.refresh(trip)

    # Itinerary Version 1
    itin = Itinerary(trip_id=trip.id, version=1, summary="Coorg Coffee Plantation Tour", provider="engine-v2")
    db_session.add(itin)
    db_session.commit()

    day1 = ItineraryDay(itinerary_id=itin.id, day_number=1, itinerary_date=date(2026, 11, 1))
    db_session.add(day1)
    db_session.commit()

    item1 = ItineraryItem(itinerary_day_id=day1.id, item_order=1, start_time=time(10, 0), title="Estate Walk", category="attractions", estimated_cost=Decimal("300.00"))
    item2 = ItineraryItem(itinerary_day_id=day1.id, item_order=2, start_time=time(13, 0), title="Kodava Lunch", category="food", estimated_cost=Decimal("600.00"))
    db_session.add_all([item1, item2])
    db_session.commit()

    trip_record = db_session.get(Trip, trip.id)
    assert len(trip_record.itineraries) == 1
    assert len(trip_record.itineraries[0].days[0].items) == 2


def test_6_budget_allocations_and_expenses(db_session: Session):
    """Verify financial tracking with Decimal precision."""
    u = User(email="finance_user@example.test", password_hash=hash_password("pw"), full_name="Finance User")
    d = Destination(city="Ooty", country="India", description="Nilgiri Queen", average_daily_cost=Decimal("3500.00"))
    db_session.add_all([u, d])
    db_session.commit()

    trip = Trip(
        user_id=u.id,
        destination_id=d.id,
        starting_location="Coimbatore",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 2),
        traveller_count=1,
        total_budget=Decimal("6000.00"),
    )
    db_session.add(trip)
    db_session.commit()

    alloc1 = BudgetAllocation(trip_id=trip.id, category="accommodation", amount=Decimal("2500.00"))
    alloc2 = BudgetAllocation(trip_id=trip.id, category="food", amount=Decimal("1500.00"))
    exp1 = Expense(trip_id=trip.id, category="transportation", amount=Decimal("600.00"), incurred_on=date(2026, 12, 1))

    db_session.add_all([alloc1, alloc2, exp1])
    db_session.commit()

    allocs = db_session.execute(select(BudgetAllocation).where(BudgetAllocation.trip_id == trip.id)).scalars().all()
    assert len(allocs) == 2
    assert sum(a.amount for a in allocs) == Decimal("4000.00")


def test_7_foreign_key_integrity_and_cascades(db_session: Session):
    """Verify deletion cascades across multi-table hierarchies."""
    u = User(email="cascade_tester@example.test", password_hash=hash_password("pw"), full_name="Cascade Tester")
    d = Destination(city="Pondicherry", country="India", description="French colony")
    db_session.add_all([u, d])
    db_session.commit()

    trip = Trip(
        user_id=u.id,
        destination_id=d.id,
        starting_location="Chennai",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 2),
        traveller_count=1,
        total_budget=Decimal("5000.00"),
    )
    db_session.add(trip)
    db_session.commit()

    m = TripMember(trip_id=trip.id, display_name="Traveler")
    itin = Itinerary(trip_id=trip.id, version=1, summary="Pondy Trip")
    pack = PackingItem(trip_id=trip.id, item="Sun Hat", category="clothing")
    convo = AIConversation(user_id=u.id, trip_id=trip.id)
    db_session.add_all([m, itin, pack, convo])
    db_session.commit()

    trip_id = trip.id
    convo_id = convo.id

    # Delete Trip -> Cascade should clean up trip child entities, and SET NULL on convo.trip_id
    db_session.delete(trip)
    db_session.commit()

    assert db_session.get(Trip, trip_id) is None
    assert db_session.get(TripMember, m.id) is None
    assert db_session.get(Itinerary, itin.id) is None
    assert db_session.get(PackingItem, pack.id) is None

    # AI conversation should remain intact with trip_id set to None
    refreshed_convo = db_session.get(AIConversation, convo_id)
    assert refreshed_convo is not None
    assert refreshed_convo.trip_id is None


def test_8_transaction_rollback_guarantee(db_session: Session):
    """Verify atomic rollback when a constraint violation occurs mid-transaction."""
    u = User(email="rollback_user@example.test", password_hash=hash_password("pw"), full_name="Rollback User")
    db_session.add(u)
    db_session.commit()

    # Attempt inserting a valid destination AND an invalid duplicate destination in same transaction
    try:
        d1 = Destination(city="Kodaikanal", country="India", description="Princess of Hill stations")
        d2 = Destination(city="Kodaikanal", country="India", description="Duplicate!")  # triggers UNIQUE(city, country)
        db_session.add_all([d1, d2])
        db_session.commit()
    except IntegrityError:
        db_session.rollback()

    # Verify Kodaikanal was NOT inserted due to atomic rollback
    saved_dest = db_session.execute(
        select(Destination).where(Destination.city == "Kodaikanal")
    ).scalar_one_or_none()
    assert saved_dest is None


def test_9_api_to_database_e2e_flow(client: TestClient, traveller_headers: dict, db_session: Session):
    """Verify end-to-end API operations writing and reading from persistent database."""
    # 1. Destination
    dest = Destination(city="Rishikesh", country="India", description="Yoga Capital", average_daily_cost=Decimal("3000.00"), active=True)
    db_session.add(dest)
    db_session.commit()
    db_session.refresh(dest)

    hotel = Hotel(destination_id=dest.id, name="Ganga View Resort", price_per_night=Decimal("2200.00"), rating=Decimal("4.5"))
    db_session.add(hotel)
    db_session.commit()

    # 2. Trip creation via API
    payload = {
        "destination_id": dest.id,
        "starting_location": "Delhi",
        "start_date": "2026-10-10",
        "end_date": "2026-10-12",
        "traveller_count": 2,
        "total_budget": "15000.00",
        "generate_plan": True,
    }
    resp = client.post("/api/v1/trips", json=payload, headers=traveller_headers)
    assert resp.status_code == 201
    data = resp.json()
    trip_id = data["id"]
    assert data["destination_city"] == "Rishikesh"
    assert data["status"] == "planned"

    # 3. Read back via API
    get_resp = client.get(f"/api/v1/trips/{trip_id}", headers=traveller_headers)
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["id"] == trip_id
    assert len(get_data["itineraries"]) >= 1
    assert get_data["budget_summary"]["total_budget"] == "15000.00"
