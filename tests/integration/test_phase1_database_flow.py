from datetime import date, datetime, time, timezone
from decimal import Decimal
from sqlalchemy import select
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
)
from app.services.auth_service import hash_password


def test_full_phase1_relational_journey(db_session: Session) -> None:
    """Validate complete relational flow across all 19 domain entities in a real journey."""
    # 1. User Registration & Profile
    user = User(
        email="globetrotter@example.com",
        password_hash=hash_password("Pass123!"),
        full_name="Globe Trotter",
        role="traveller",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 2. Travel Preferences (1:1 & 1:N)
    pref = UserPreference(
        user_id=user.id,
        hotel_preference="heritage",
        food_preference="local cuisine",
        transport_preference="train",
        travel_style="cultural",
        special_requirements="Vegetarian meal option",
    )
    act1 = ActivityPreference(user_id=user.id, activity="palaces")
    act2 = ActivityPreference(user_id=user.id, activity="photography")
    db_session.add_all([pref, act1, act2])
    db_session.commit()

    # 3. Destination Catalogue & Offerings
    dest = Destination(
        city="Udaipur",
        country="India",
        description="City of Lakes",
        average_daily_cost=Decimal("4500.00"),
        active=True,
    )
    db_session.add(dest)
    db_session.commit()
    db_session.refresh(dest)

    hotel = Hotel(
        destination_id=dest.id,
        name="Lakeview Haveli",
        price_per_night=Decimal("3800.00"),
        rating=Decimal("4.6"),
    )
    restaurant = Restaurant(
        destination_id=dest.id,
        name="Tribute Lakeside Dining",
        cuisine="Rajasthani & North Indian",
        average_cost_per_person=Decimal("600.00"),
        rating=Decimal("4.7"),
    )
    attraction = Attraction(
        destination_id=dest.id,
        name="City Palace Udaipur",
        category="heritage",
        entry_fee=Decimal("300.00"),
        rating=Decimal("4.9"),
    )
    transport = TransportOption(
        origin="Jaipur",
        destination_id=dest.id,
        mode="train",
        provider="Chettinad Express",
        estimated_cost=Decimal("750.00"),
        duration_minutes=420,
    )
    db_session.add_all([hotel, restaurant, attraction, transport])
    db_session.commit()

    # 4. Trip Creation & Members
    trip = Trip(
        user_id=user.id,
        destination_id=dest.id,
        starting_location="Jaipur",
        start_date=date(2026, 12, 10),
        end_date=date(2026, 12, 13),
        traveller_count=2,
        total_budget=Decimal("20000.00"),
        estimated_total=Decimal("12500.00"),
        status="planned",
    )
    db_session.add(trip)
    db_session.commit()
    db_session.refresh(trip)

    member1 = TripMember(trip_id=trip.id, display_name="Globe Trotter", age_group="adult")
    member2 = TripMember(trip_id=trip.id, display_name="Companion", age_group="adult")
    db_session.add_all([member1, member2])
    db_session.commit()

    # 5. Itinerary, Days & Items
    itinerary = Itinerary(
        trip_id=trip.id,
        version=1,
        summary="3-day Udaipur heritage tour",
        provider="mock",
    )
    db_session.add(itinerary)
    db_session.commit()
    db_session.refresh(itinerary)

    day1 = ItineraryDay(
        itinerary_id=itinerary.id,
        day_number=1,
        itinerary_date=date(2026, 12, 10),
    )
    db_session.add(day1)
    db_session.commit()
    db_session.refresh(day1)

    item1 = ItineraryItem(
        itinerary_day_id=day1.id,
        item_order=1,
        start_time=time(9, 30),
        title="Check-in at Lakeview Haveli",
        category="hotel",
        estimated_cost=Decimal("3800.00"),
    )
    item2 = ItineraryItem(
        itinerary_day_id=day1.id,
        item_order=2,
        start_time=time(14, 0),
        title="Visit City Palace Udaipur",
        category="attraction",
        estimated_cost=Decimal("600.00"),
    )
    db_session.add_all([item1, item2])
    db_session.commit()

    # 6. Budget Allocations & Expenses
    alloc1 = BudgetAllocation(trip_id=trip.id, category="accommodation", amount=Decimal("7600.00"))
    alloc2 = BudgetAllocation(trip_id=trip.id, category="food", amount=Decimal("3600.00"))
    alloc3 = BudgetAllocation(trip_id=trip.id, category="activities", amount=Decimal("1200.00"))
    db_session.add_all([alloc1, alloc2, alloc3])
    db_session.commit()

    exp1 = Expense(
        trip_id=trip.id,
        category="transportation",
        description="Train tickets Jaipur to Udaipur",
        amount=Decimal("1500.00"),
        incurred_on=date(2026, 12, 10),
    )
    db_session.add(exp1)
    db_session.commit()

    # 7. Packing Checklist
    pack1 = PackingItem(trip_id=trip.id, item="Camera & lenses", category="electronics", is_packed=True)
    pack2 = PackingItem(trip_id=trip.id, item="Comfortable walking shoes", category="clothing", is_packed=False)
    db_session.add_all([pack1, pack2])
    db_session.commit()

    # 8. Saved Trip Bookmark & Review
    saved = SavedTrip(user_id=user.id, trip_id=trip.id)
    review = Review(user_id=user.id, destination_id=dest.id, rating=5, comment="Stunning city of lakes!")
    db_session.add_all([saved, review])
    db_session.commit()

    # 9. AI Assistant Conversation & Messages
    convo = AIConversation(user_id=user.id, trip_id=trip.id)
    db_session.add(convo)
    db_session.commit()
    db_session.refresh(convo)

    msg1 = AIMessage(conversation_id=convo.id, role="user", content="Suggest best spots for sunset photography.")
    msg2 = AIMessage(conversation_id=convo.id, role="assistant", content="Sajjangarh Monsoon Palace and Ambrai Ghat are top choices.")
    db_session.add_all([msg1, msg2])
    db_session.commit()

    # --- VERIFICATION ---
    # Query complete relational graph from user
    queried_user = db_session.get(User, user.id)
    assert queried_user is not None
    assert queried_user.preference.hotel_preference == "heritage"
    assert len(queried_user.activity_preferences) == 2
    assert len(queried_user.trips) == 1

    queried_trip = queried_user.trips[0]
    assert queried_trip.destination.city == "Udaipur"
    assert len(queried_trip.members) == 2
    assert len(queried_trip.itineraries) == 1
    assert len(queried_trip.itineraries[0].days) == 1
    assert len(queried_trip.itineraries[0].days[0].items) == 2
    assert len(queried_trip.budget_allocations) == 3
    assert len(queried_trip.expenses) == 1
    assert len(queried_trip.packing_items) == 2
    assert len(queried_user.saved_trips) == 1
    assert len(queried_user.reviews) == 1
    assert len(queried_user.ai_conversations) == 1
    assert len(queried_user.ai_conversations[0].messages) == 2
