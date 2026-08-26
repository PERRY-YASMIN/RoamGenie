"""Development Database Seed Script for RoamGenie (Phase 1)
Populates realistic sample data into the database configured by DATABASE_URL.
"""
import sys
from datetime import date, datetime, time, timezone
from decimal import Decimal
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.models import (  # noqa: E402
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
from app.db.session import get_engine  # noqa: E402
from app.services.auth_service import hash_password  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402


def seed_database() -> None:
    engine = get_engine()
    if engine is None:
        print("DATABASE_URL is not configured. Set DATABASE_URL or run in local mode.")
        sys.exit(1)

    print(f"Seeding database connected to: {engine.url.render_as_string(hide_password=True)}")

    with Session(engine) as db:
        # Check if already seeded
        existing_user = db.execute(select(User).where(User.email == "traveller@roamgenie.internal")).scalar_one_or_none()
        if existing_user:
            print("Development seed data already exists. Skipping insertion.")
            return

        print("Inserting development seed records...")

        # 1. Users
        admin = User(
            email="admin@roamgenie.internal",
            password_hash=hash_password("AdminPass123!"),
            full_name="System Administrator",
            role="admin",
        )
        traveller1 = User(
            email="traveller@roamgenie.internal",
            password_hash=hash_password("TravellerPass123!"),
            full_name="Arun Kumar",
            role="traveller",
        )
        traveller2 = User(
            email="ananya@roamgenie.internal",
            password_hash=hash_password("TravellerPass123!"),
            full_name="Ananya Sharma",
            role="traveller",
        )
        db.add_all([admin, traveller1, traveller2])
        db.commit()
        db.refresh(traveller1)
        db.refresh(traveller2)

        # 2. Preferences
        pref1 = UserPreference(
            user_id=traveller1.id,
            hotel_preference="heritage",
            food_preference="South Indian Vegetarian",
            transport_preference="train",
            travel_style="cultural",
            special_requirements="Near ground floor",
        )
        pref2 = UserPreference(
            user_id=traveller2.id,
            hotel_preference="boutique",
            food_preference="Local Seafood",
            transport_preference="flight",
            travel_style="relaxed",
        )
        db.add_all([pref1, pref2])

        act1 = ActivityPreference(user_id=traveller1.id, activity="heritage")
        act2 = ActivityPreference(user_id=traveller1.id, activity="palaces")
        act3 = ActivityPreference(user_id=traveller2.id, activity="coastal")
        act4 = ActivityPreference(user_id=traveller2.id, activity="photography")
        db.add_all([act1, act2, act3, act4])
        db.commit()

        # 3. Destinations
        dest1 = Destination(city="Mysuru", country="India", description="City of palaces, royal heritage, and silk.", average_daily_cost=Decimal("3500.00"), active=True)
        dest2 = Destination(city="Kochi", country="India", description="Coastal port known for spice markets and heritage.", average_daily_cost=Decimal("4200.00"), active=True)
        dest3 = Destination(city="Jaipur", country="India", description="The Pink City of Rajasthan featuring hilltop forts.", average_daily_cost=Decimal("4000.00"), active=True)
        dest4 = Destination(city="Udaipur", country="India", description="City of Lakes surrounded by Aravalli hills.", average_daily_cost=Decimal("4500.00"), active=True)
        dest5 = Destination(city="Goa", country="India", description="Golden beaches and Portuguese colonial architecture.", average_daily_cost=Decimal("5000.00"), active=True)
        db.add_all([dest1, dest2, dest3, dest4, dest5])
        db.commit()
        db.refresh(dest1)

        # 4. Catalogues for Mysuru
        hotel1 = Hotel(destination_id=dest1.id, name="Heritage Garden Stay", price_per_night=Decimal("2800.00"), rating=Decimal("4.3"))
        hotel2 = Hotel(destination_id=dest1.id, name="Royal Orchid Metropole", price_per_night=Decimal("4500.00"), rating=Decimal("4.7"))
        rest1 = Restaurant(destination_id=dest1.id, name="Mylari Tiffin House", cuisine="South Indian", average_cost_per_person=Decimal("250.00"), rating=Decimal("4.8"))
        rest2 = Restaurant(destination_id=dest1.id, name="Gufha Cave Dining", cuisine="North Indian & Mughlai", average_cost_per_person=Decimal("650.00"), rating=Decimal("4.3"))
        att1 = Attraction(destination_id=dest1.id, name="Mysuru Palace", category="heritage", entry_fee=Decimal("100.00"), rating=Decimal("4.9"))
        att2 = Attraction(destination_id=dest1.id, name="Chamundi Hill & Temple", category="temple", entry_fee=Decimal("0.00"), rating=Decimal("4.6"))
        att3 = Attraction(destination_id=dest1.id, name="Brindavan Gardens", category="nature", entry_fee=Decimal("50.00"), rating=Decimal("4.2"))
        trans1 = TransportOption(origin="Bengaluru", destination_id=dest1.id, mode="train", provider="Vande Bharat Express", estimated_cost=Decimal("550.00"), duration_minutes=120)
        trans2 = TransportOption(origin="Chennai", destination_id=dest1.id, mode="train", provider="Kaveri Express", estimated_cost=Decimal("850.00"), duration_minutes=480)
        db.add_all([hotel1, hotel2, rest1, rest2, att1, att2, att3, trans1, trans2])
        db.commit()

        # 5. Trip & Itinerary
        trip = Trip(
            user_id=traveller1.id,
            destination_id=dest1.id,
            starting_location="Bengaluru",
            start_date=date(2026, 9, 15),
            end_date=date(2026, 9, 17),
            traveller_count=2,
            total_budget=Decimal("15000.00"),
            estimated_total=Decimal("11200.00"),
            status="planned",
        )
        db.add(trip)
        db.commit()
        db.refresh(trip)

        m1 = TripMember(trip_id=trip.id, display_name="Arun Kumar", age_group="adult")
        m2 = TripMember(trip_id=trip.id, display_name="Suresh Kumar", age_group="senior")
        db.add_all([m1, m2])

        itin = Itinerary(trip_id=trip.id, version=1, summary="3-Day Cultural & Royal Heritage Tour of Mysuru", provider="mock")
        db.add(itin)
        db.commit()
        db.refresh(itin)

        day1 = ItineraryDay(itinerary_id=itin.id, day_number=1, itinerary_date=date(2026, 9, 15))
        db.add(day1)
        db.commit()
        db.refresh(day1)

        item1 = ItineraryItem(itinerary_day_id=day1.id, item_order=1, start_time=time(9, 0), title="Check-in at Heritage Garden Stay", category="hotel", estimated_cost=Decimal("2800.00"))
        item2 = ItineraryItem(itinerary_day_id=day1.id, item_order=2, start_time=time(11, 0), title="Explore Mysuru Palace", category="attraction", estimated_cost=Decimal("200.00"))
        item3 = ItineraryItem(itinerary_day_id=day1.id, item_order=3, start_time=time(13, 30), title="Lunch at Mylari Tiffin House", category="food", estimated_cost=Decimal("500.00"))
        db.add_all([item1, item2, item3])

        # 6. Allocations, Expenses, Packing, Review
        alloc1 = BudgetAllocation(trip_id=trip.id, category="accommodation", amount=Decimal("5600.00"))
        alloc2 = BudgetAllocation(trip_id=trip.id, category="food", amount=Decimal("2800.00"))
        alloc3 = BudgetAllocation(trip_id=trip.id, category="activities", amount=Decimal("1200.00"))
        exp1 = Expense(trip_id=trip.id, category="transportation", description="Train tickets (Vande Bharat)", amount=Decimal("1100.00"), incurred_on=date(2026, 9, 15))
        pack1 = PackingItem(trip_id=trip.id, item="Comfortable walking shoes", category="clothing", is_packed=True)
        saved = SavedTrip(user_id=traveller1.id, trip_id=trip.id)
        rev = Review(user_id=traveller1.id, destination_id=dest1.id, rating=5, comment="Magnificent royal heritage!")
        db.add_all([alloc1, alloc2, alloc3, exp1, pack1, saved, rev])

        # 7. Weather
        w1 = WeatherSnapshot(destination_id=dest1.id, observed_at=datetime.now(timezone.utc), summary="Partly cloudy, pleasant breeze", temperature_c=Decimal("24.50"), provider="mock")
        db.add(w1)

        db.commit()
        print("Successfully seeded all 19 entities with sample development data!")


if __name__ == "__main__":
    seed_database()
