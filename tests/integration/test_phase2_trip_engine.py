from datetime import date, timedelta
from decimal import Decimal
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.catalogue import Attraction, Destination, Hotel, Restaurant, TransportOption
from app.db.models.finance import BudgetAllocation
from app.db.models.trip import Itinerary, ItineraryDay, ItineraryItem, PackingItem, Trip
from app.db.models.user import User
from app.schemas.trip import TripCreateRequest
from app.services.auth_service import hash_password
from app.services.trip_service import TripService


@pytest.fixture
def integration_user(db_session: Session) -> User:
    user = User(
        email="integration_user@example.com",
        password_hash=hash_password("IntegrationPass123!"),
        full_name="Integration User",
        role="traveller",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def integration_dest(db_session: Session) -> Destination:
    dest = Destination(
        city="Goa",
        country="India",
        description="Golden beaches & colonial architecture",
        average_daily_cost=Decimal("5000.00"),
        active=True,
    )
    db_session.add(dest)
    db_session.commit()
    db_session.refresh(dest)

    hotel = Hotel(destination_id=dest.id, name="Goa Beach Resort", price_per_night=Decimal("3000.00"), rating=Decimal("4.5"))
    rest = Restaurant(destination_id=dest.id, name="Fisherman's Wharf", cuisine="Seafood", average_cost_per_person=Decimal("450.00"), rating=Decimal("4.6"))
    att = Attraction(destination_id=dest.id, name="Aguada Fort", category="heritage", entry_fee=Decimal("50.00"), rating=Decimal("4.6"))
    trans = TransportOption(origin="Mumbai", destination_id=dest.id, mode="flight", provider="IndiGo", estimated_cost=Decimal("2200.00"))

    db_session.add_all([hotel, rest, att, trans])
    db_session.commit()
    return dest


def test_transactional_multi_table_persistence(
    db_session: Session, integration_user: User, integration_dest: Destination
):
    """Verify that trip generation commits atomically across 6 relational tables."""
    service = TripService()
    req = TripCreateRequest(
        destination_id=integration_dest.id,
        starting_location="Mumbai",
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 3),
        traveller_count=2,
        total_budget=Decimal("25000.00"),
        preferences=["beach", "heritage"],
        generate_plan=True,
    )

    trip = service.create_trip(db_session, integration_user.id, req)
    assert trip.id > 0
    assert trip.status == "planned"
    assert trip.estimated_total > Decimal("0.00")

    # 1. Verify Itinerary
    itins = db_session.execute(select(Itinerary).where(Itinerary.trip_id == trip.id)).scalars().all()
    assert len(itins) == 1
    assert itins[0].version == 1

    # 2. Verify Itinerary Days
    days = db_session.execute(select(ItineraryDay).where(ItineraryDay.itinerary_id == itins[0].id)).scalars().all()
    assert len(days) == 3

    # 3. Verify Itinerary Items
    items = db_session.execute(
        select(ItineraryItem).where(ItineraryItem.itinerary_day_id.in_([d.id for d in days]))
    ).scalars().all()
    assert len(items) >= 9

    # 4. Verify Budget Allocations
    allocs = db_session.execute(select(BudgetAllocation).where(BudgetAllocation.trip_id == trip.id)).scalars().all()
    assert len(allocs) >= 4

    # 5. Verify Packing Items
    packs = db_session.execute(select(PackingItem).where(PackingItem.trip_id == trip.id)).scalars().all()
    assert len(packs) >= 5


def test_plan_regeneration_versioning(
    db_session: Session, integration_user: User, integration_dest: Destination
):
    """Regenerating a plan creates a new incremented itinerary version without corrupting previous history."""
    service = TripService()
    req = TripCreateRequest(
        destination_id=integration_dest.id,
        starting_location="Mumbai",
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 2),
        traveller_count=1,
        total_budget=Decimal("15000.00"),
        generate_plan=True,
    )
    trip = service.create_trip(db_session, integration_user.id, req)

    # First version
    itins_v1 = db_session.execute(select(Itinerary).where(Itinerary.trip_id == trip.id)).scalars().all()
    assert len(itins_v1) == 1
    assert itins_v1[0].version == 1

    # Regenerate plan
    service.generate_and_persist_plan(db_session, integration_user.id, trip.id)
    itins_v2 = db_session.execute(
        select(Itinerary).where(Itinerary.trip_id == trip.id).order_by(Itinerary.version)
    ).scalars().all()
    assert len(itins_v2) == 2
    assert itins_v2[1].version == 2


def test_transaction_rollback_on_failure(
    db_session: Session, integration_user: User, integration_dest: Destination
):
    """Ensure complete rollback if an error occurs during multi-table execution."""
    service = TripService()
    req = TripCreateRequest(
        destination_id=integration_dest.id,
        starting_location="Mumbai",
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 2),
        traveller_count=1,
        total_budget=Decimal("15000.00"),
        generate_plan=False,
    )
    trip = service.create_trip(db_session, integration_user.id, req)

    # Intentionally corrupt destination to trigger failure during generation
    trip.destination_id = 99999
    db_session.commit()

    with pytest.raises(Exception):
        service.generate_and_persist_plan(db_session, integration_user.id, trip.id)

    # Assert no partial itineraries were committed
    itins = db_session.execute(select(Itinerary).where(Itinerary.trip_id == trip.id)).scalars().all()
    assert len(itins) == 0
