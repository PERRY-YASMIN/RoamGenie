"""SQLite Master Database Initialization and Seeder for RoamGenie
Creates all 23 relational tables and seeds all 21,133 entities + dev accounts.
"""
import json
import os
import sys
from datetime import date, datetime, time, timezone
from decimal import Decimal
from pathlib import Path

# Paths
base_dir = Path(__file__).resolve().parent.parent.parent
backend_dir = base_dir / "backend"
seeds_dir = base_dir / "database" / "seeds"

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.base import Base
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
from app.db.session import get_engine
from app.services.auth_service import hash_password
from sqlalchemy import select
from sqlalchemy.orm import Session


def init_and_seed():
    engine = get_engine()
    if engine is None:
        print("Error: Database engine could not be created.")
        return

    print(f"Initializing database at: {engine.url}")
    # 1. Create all schema tables
    Base.metadata.create_all(bind=engine)
    print("Schema tables verified/created successfully.")

    with Session(engine) as db:
        # Check if users already exist
        existing_user = db.execute(select(User).where(User.email == "traveller@roamgenie.internal")).scalar_one_or_none()
        if not existing_user:
            print("Seeding users and preferences...")
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

        # Check destinations
        dest_count = db.query(Destination).count()
        if dest_count == 0:
            print("Seeding destinations master catalogue...")
            # 5 initial base destinations
            initial_dests = [
                Destination(id=1, city="Mysuru", country="India", description="City of palaces, royal heritage, and silk.", average_daily_cost=Decimal("3500.00"), active=True),
                Destination(id=2, city="Kochi", country="India", description="Coastal port known for spice markets and heritage.", average_daily_cost=Decimal("4200.00"), active=True),
                Destination(id=3, city="Jaipur", country="India", description="The Pink City of Rajasthan featuring hilltop forts.", average_daily_cost=Decimal("4000.00"), active=True),
                Destination(id=4, city="Udaipur", country="India", description="City of Lakes surrounded by Aravalli hills.", average_daily_cost=Decimal("4500.00"), active=True),
                Destination(id=5, city="Goa", country="India", description="Golden beaches and Portuguese colonial architecture.", average_daily_cost=Decimal("5000.00"), active=True),
            ]
            db.add_all(initial_dests)
            db.commit()

            # Load destinations JSON
            dests_json_path = seeds_dir / "destinations_master_d1.json"
            if dests_json_path.exists():
                with open(dests_json_path, "r", encoding="utf-8") as f:
                    dests_data = json.load(f)
                dests_to_add = []
                next_id = 6
                for item in dests_data:
                    # check if already added
                    if item["city"] in ["Mysuru", "Kochi", "Jaipur", "Udaipur", "Goa"]:
                        continue
                    dests_to_add.append(Destination(
                        id=next_id,
                        city=item["city"],
                        country=item["country"],
                        description=item.get("description", ""),
                        average_daily_cost=Decimal(str(item.get("average_daily_cost", 3500.0))),
                        active=item.get("active", True),
                    ))
                    next_id += 1
                db.add_all(dests_to_add)
                db.commit()
            print(f"Total destinations: {db.query(Destination).count()}")

        # Check attractions
        if db.query(Attraction).count() == 0:
            print("Seeding attractions master catalogue...")
            attr_json_path = seeds_dir / "attractions_master_d2.json"
            if attr_json_path.exists():
                with open(attr_json_path, "r", encoding="utf-8") as f:
                    attr_data = json.load(f)
                items = [
                    Attraction(
                        id=item.get("id"),
                        destination_id=item["destination_id"],
                        name=item["name"],
                        category=item.get("category", "sightseeing"),
                        entry_fee=Decimal(str(item.get("entry_fee", 0.0))),
                        rating=Decimal(str(item.get("rating", 4.5))),
                    )
                    for item in attr_data
                ]
                db.bulk_save_objects(items)
                db.commit()
            print(f"Total attractions: {db.query(Attraction).count()}")

        # Check hotels
        if db.query(Hotel).count() == 0:
            print("Seeding hotels master catalogue...")
            hotels_json_path = seeds_dir / "hotels_master_d3.json"
            if hotels_json_path.exists():
                with open(hotels_json_path, "r", encoding="utf-8") as f:
                    hotels_data = json.load(f)
                items = [
                    Hotel(
                        id=item.get("id"),
                        destination_id=item["destination_id"],
                        name=item["name"],
                        price_per_night=Decimal(str(item.get("price_per_night", 2500.0))),
                        rating=Decimal(str(item.get("rating", 4.0))),
                    )
                    for item in hotels_data
                ]
                db.bulk_save_objects(items)
                db.commit()
            print(f"Total hotels: {db.query(Hotel).count()}")

        # Check restaurants
        if db.query(Restaurant).count() == 0:
            print("Seeding restaurants master catalogue...")
            rest_json_path = seeds_dir / "restaurants_master_d4.json"
            if rest_json_path.exists():
                with open(rest_json_path, "r", encoding="utf-8") as f:
                    rest_data = json.load(f)
                items = [
                    Restaurant(
                        id=item.get("id"),
                        destination_id=item["destination_id"],
                        name=item["name"],
                        cuisine=item.get("cuisine", "Multi-Cuisine"),
                        average_cost_per_person=Decimal(str(item.get("average_cost_per_person", 400.0))),
                        rating=Decimal(str(item.get("rating", 4.2))),
                    )
                    for item in rest_data
                ]
                db.bulk_save_objects(items)
                db.commit()
            print(f"Total restaurants: {db.query(Restaurant).count()}")

        # Check transport
        if db.query(TransportOption).count() == 0:
            print("Seeding transport master catalogue...")
            trans_json_path = seeds_dir / "transport_master_d5.json"
            if trans_json_path.exists():
                with open(trans_json_path, "r", encoding="utf-8") as f:
                    trans_data = json.load(f)
                items = [
                    TransportOption(
                        id=item.get("id"),
                        destination_id=item["destination_id"],
                        origin=item.get("origin", "Bengaluru"),
                        mode=item.get("mode", "train"),
                        provider=item.get("provider", "Express"),
                        estimated_cost=Decimal(str(item.get("estimated_cost", 500.0))),
                        duration_minutes=item.get("duration_minutes", 120),
                    )
                    for item in trans_data
                ]
                db.bulk_save_objects(items)
                db.commit()
            print(f"Total transport options: {db.query(TransportOption).count()}")

        # Check trips
        if db.query(Trip).count() == 0:
            print("Seeding sample trip & itinerary...")
            traveller = db.execute(select(User).where(User.email == "traveller@roamgenie.internal")).scalar_one()
            dest = db.execute(select(Destination).where(Destination.id == 1)).scalar_one()

            trip = Trip(
                user_id=traveller.id,
                destination_id=dest.id,
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
            day2 = ItineraryDay(itinerary_id=itin.id, day_number=2, itinerary_date=date(2026, 9, 16))
            day3 = ItineraryDay(itinerary_id=itin.id, day_number=3, itinerary_date=date(2026, 9, 17))
            db.add_all([day1, day2, day3])
            db.commit()
            db.refresh(day1)

            item1 = ItineraryItem(itinerary_day_id=day1.id, item_order=1, start_time=time(9, 0), title="Check-in at Heritage Garden Stay", category="hotel", estimated_cost=Decimal("2800.00"))
            item2 = ItineraryItem(itinerary_day_id=day1.id, item_order=2, start_time=time(11, 0), title="Explore Mysuru Palace", category="attraction", estimated_cost=Decimal("200.00"))
            item3 = ItineraryItem(itinerary_day_id=day1.id, item_order=3, start_time=time(13, 30), title="Lunch at Mylari Tiffin House", category="food", estimated_cost=Decimal("500.00"))
            db.add_all([item1, item2, item3])

            alloc1 = BudgetAllocation(trip_id=trip.id, category="accommodation", amount=Decimal("5600.00"))
            alloc2 = BudgetAllocation(trip_id=trip.id, category="food", amount=Decimal("2800.00"))
            alloc3 = BudgetAllocation(trip_id=trip.id, category="activities", amount=Decimal("1200.00"))
            alloc4 = BudgetAllocation(trip_id=trip.id, category="transportation", amount=Decimal("1600.00"))
            exp1 = Expense(trip_id=trip.id, category="transportation", description="Train tickets (Vande Bharat)", amount=Decimal("1100.00"), incurred_on=date(2026, 9, 15))
            pack1 = PackingItem(trip_id=trip.id, item="Comfortable walking shoes", category="clothing", is_packed=True)
            pack2 = PackingItem(trip_id=trip.id, item="Camera & charger", category="electronics", is_packed=False)
            pack3 = PackingItem(trip_id=trip.id, item="Sunscreen & sunglasses", category="toiletries", is_packed=True)
            saved = SavedTrip(user_id=traveller.id, trip_id=trip.id)
            rev = Review(user_id=traveller.id, destination_id=dest.id, rating=5, comment="Magnificent royal heritage!")
            w1 = WeatherSnapshot(destination_id=dest.id, observed_at=datetime.now(timezone.utc), summary="Partly cloudy, pleasant breeze", temperature_c=Decimal("24.50"), provider="mock")

            db.add_all([alloc1, alloc2, alloc3, alloc4, exp1, pack1, pack2, pack3, saved, rev, w1])
            db.commit()

        print("Master database seeded and verified successfully!")


if __name__ == "__main__":
    init_and_seed()
