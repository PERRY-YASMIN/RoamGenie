from datetime import date, datetime, timezone
from decimal import Decimal
import pytest
from sqlalchemy import select
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
    TripMember,
    User,
    UserPreference,
    WeatherSnapshot,
)
from app.services.auth_service import hash_password


def test_unique_user_email_constraint(db_session: Session) -> None:
    u1 = User(
        email="unique@example.com",
        password_hash=hash_password("pw1"),
        full_name="User One",
    )
    db_session.add(u1)
    db_session.commit()

    u2 = User(
        email="unique@example.com",
        password_hash=hash_password("pw2"),
        full_name="User Two",
    )
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_unique_destination_city_country_constraint(db_session: Session) -> None:
    d1 = Destination(city="Jaipur", country="India", description="Pink City")
    db_session.add(d1)
    db_session.commit()

    d2 = Destination(city="Jaipur", country="India", description="Duplicate")
    db_session.add(d2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_user_role_check_constraint(db_session: Session) -> None:
    invalid_user = User(
        email="hacker@example.com",
        password_hash=hash_password("pw"),
        full_name="Hacker",
        role="superadmin",  # Invalid role
    )
    db_session.add(invalid_user)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_trip_date_and_budget_check_constraints(db_session: Session) -> None:
    u = User(
        email="traveller1@example.com",
        password_hash=hash_password("pw"),
        full_name="Traveller",
    )
    d = Destination(city="Kochi", country="India", description="Coastal")
    db_session.add_all([u, d])
    db_session.commit()

    # 1. Negative total budget should fail
    bad_budget_trip = Trip(
        user_id=u.id,
        destination_id=d.id,
        starting_location="Bangalore",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 5),
        traveller_count=2,
        total_budget=Decimal("-500.00"),
    )
    db_session.add(bad_budget_trip)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # 2. End date before start date should fail
    bad_dates_trip = Trip(
        user_id=u.id,
        destination_id=d.id,
        starting_location="Bangalore",
        start_date=date(2026, 9, 5),
        end_date=date(2026, 9, 1),
        traveller_count=2,
        total_budget=Decimal("5000.00"),
    )
    db_session.add(bad_dates_trip)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_hotel_and_restaurant_constraints(db_session: Session) -> None:
    d = Destination(city="Goa", country="India", description="Beaches")
    db_session.add(d)
    db_session.commit()

    # Negative hotel price should fail
    bad_hotel = Hotel(
        destination_id=d.id,
        name="Cheap Stay",
        price_per_night=Decimal("-100.00"),
    )
    db_session.add(bad_hotel)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Invalid rating > 5 should fail
    bad_rating_restaurant = Restaurant(
        destination_id=d.id,
        name="Super Cafe",
        average_cost_per_person=Decimal("200.00"),
        rating=Decimal("6.5"),
    )
    db_session.add(bad_rating_restaurant)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_review_rating_range_constraint(db_session: Session) -> None:
    u = User(
        email="reviewer@example.com",
        password_hash=hash_password("pw"),
        full_name="Reviewer",
    )
    d = Destination(city="Delhi", country="India", description="Capital")
    db_session.add_all([u, d])
    db_session.commit()

    # Rating 0 should fail (must be 1-5)
    bad_review = Review(user_id=u.id, destination_id=d.id, rating=0, comment="Bad")
    db_session.add(bad_review)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_foreign_key_cascades_on_user_delete(db_session: Session) -> None:
    u = User(
        email="cascade_user@example.com",
        password_hash=hash_password("pw"),
        full_name="Cascade User",
    )
    d = Destination(city="Agra", country="India", description="Taj")
    db_session.add_all([u, d])
    db_session.commit()

    # Add child records
    pref = UserPreference(user_id=u.id, travel_style="luxury")
    act = ActivityPreference(user_id=u.id, activity="monuments")
    trip = Trip(
        user_id=u.id,
        destination_id=d.id,
        starting_location="Delhi",
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 3),
        traveller_count=1,
        total_budget=Decimal("3000.00"),
    )
    db_session.add_all([pref, act, trip])
    db_session.commit()

    # Verify children exist
    assert db_session.get(UserPreference, u.id) is not None
    assert db_session.get(Trip, trip.id) is not None

    # Delete User -> cascade should remove preferences and trips
    db_session.delete(u)
    db_session.commit()

    assert db_session.get(UserPreference, u.id) is None
    assert db_session.get(Trip, trip.id) is None


def test_foreign_key_cascades_on_destination_delete(db_session: Session) -> None:
    d = Destination(city="Varanasi", country="India", description="Spiritual")
    db_session.add(d)
    db_session.commit()

    hotel = Hotel(destination_id=d.id, name="Ganga Stay", price_per_night=Decimal("2000.00"))
    attraction = Attraction(destination_id=d.id, name="Ghats", entry_fee=Decimal("0.00"))
    db_session.add_all([hotel, attraction])
    db_session.commit()

    hotel_id = hotel.id
    attraction_id = attraction.id

    # Delete destination -> cascade should remove hotel and attraction
    db_session.delete(d)
    db_session.commit()

    assert db_session.get(Hotel, hotel_id) is None
    assert db_session.get(Attraction, attraction_id) is None


def test_ai_conversation_set_null_on_trip_delete(db_session: Session) -> None:
    u = User(
        email="ai_user@example.com",
        password_hash=hash_password("pw"),
        full_name="AI User",
    )
    d = Destination(city="Shimla", country="India", description="Hills")
    db_session.add_all([u, d])
    db_session.commit()

    trip = Trip(
        user_id=u.id,
        destination_id=d.id,
        starting_location="Chandigarh",
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 4),
        traveller_count=2,
        total_budget=Decimal("8000.00"),
    )
    db_session.add(trip)
    db_session.commit()

    convo = AIConversation(user_id=u.id, trip_id=trip.id)
    db_session.add(convo)
    db_session.commit()

    convo_id = convo.id

    # Delete trip -> conversation should remain, but trip_id set to NULL
    db_session.delete(trip)
    db_session.commit()

    refreshed_convo = db_session.get(AIConversation, convo_id)
    assert refreshed_convo is not None
    assert refreshed_convo.trip_id is None
