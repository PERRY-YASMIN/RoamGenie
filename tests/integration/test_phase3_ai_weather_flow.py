from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ai import WeatherSnapshot
from app.db.models.catalogue import Attraction, Destination, Hotel, Restaurant, TransportOption
from app.db.models.trip import Itinerary, ItineraryDay, ItineraryItem, PackingItem, Trip
from app.db.models.user import User
from app.services.auth_service import hash_password


@pytest.fixture
def p3_destination(db_session: Session) -> Destination:
    dest = Destination(
        city="Udaipur",
        country="India",
        description="City of Lakes and Royal Palaces",
        average_daily_cost=Decimal("4500.00"),
        active=True,
    )
    db_session.add(dest)
    db_session.commit()
    db_session.refresh(dest)

    hotel = Hotel(destination_id=dest.id, name="Lake Palace View", price_per_night=Decimal("3200.00"), rating=Decimal("4.6"))
    rest = Restaurant(destination_id=dest.id, name="Ambrai Waterfront", cuisine="North Indian & Mewari", average_cost_per_person=Decimal("600.00"), rating=Decimal("4.7"))
    att = Attraction(destination_id=dest.id, name="City Palace Udaipur", category="heritage", entry_fee=Decimal("300.00"), rating=Decimal("4.8"))
    trans = TransportOption(origin="Jaipur", destination_id=dest.id, mode="train", provider="Mewar Express", estimated_cost=Decimal("450.00"))

    db_session.add_all([hotel, rest, att, trans])
    db_session.commit()
    return dest


def test_phase3_end_to_end_planning_and_weather_flow(
    client: TestClient, traveller_headers: dict, p3_destination: Destination, db_session: Session
):
    """Verify complete Phase 3 flow: Trip creation -> AI/Deterministic planning -> Weather persistence."""
    # 1. Create Trip
    create_payload = {
        "destination_id": p3_destination.id,
        "starting_location": "Jaipur",
        "start_date": str(date.today() + timedelta(days=15)),
        "end_date": str(date.today() + timedelta(days=17)),
        "traveller_count": 2,
        "total_budget": "20000.00",
        "preferences": ["heritage", "lakes"],
        "generate_plan": True,
    }

    create_resp = client.post("/api/v1/trips", json=create_payload, headers=traveller_headers)
    assert create_resp.status_code == 201
    trip_data = create_resp.json()
    trip_id = trip_data["id"]

    assert trip_data["destination_city"] == "Udaipur"
    assert trip_data["status"] == "planned"
    assert len(trip_data["itineraries"]) >= 1

    # 2. Query Trip Weather endpoint
    weather_resp = client.get(f"/api/v1/trips/{trip_id}/weather", headers=traveller_headers)
    assert weather_resp.status_code == 200
    w_data = weather_resp.json()
    assert w_data["city"] == "Udaipur"
    assert len(w_data["forecasts"]) == 3
    assert len(w_data["packing_tips"]) > 0

    # 3. Verify Database Persistence across relational tables
    # Trips
    trip_db = db_session.get(Trip, trip_id)
    assert trip_db is not None
    assert trip_db.estimated_total > Decimal("0.00")

    # Itineraries
    itins = db_session.execute(select(Itinerary).where(Itinerary.trip_id == trip_id)).scalars().all()
    assert len(itins) >= 1

    # Days
    days = db_session.execute(select(ItineraryDay).where(ItineraryDay.itinerary_id == itins[0].id)).scalars().all()
    assert len(days) == 3

    # Items
    items = db_session.execute(
        select(ItineraryItem).where(ItineraryItem.itinerary_day_id.in_([d.id for d in days]))
    ).scalars().all()
    assert len(items) >= 9

    # Weather Snapshots
    snapshots = db_session.execute(
        select(WeatherSnapshot).where(WeatherSnapshot.destination_id == p3_destination.id)
    ).scalars().all()
    assert len(snapshots) >= 1

    # Packing items (including weather-adaptive recommendations)
    packs = db_session.execute(select(PackingItem).where(PackingItem.trip_id == trip_id)).scalars().all()
    assert len(packs) >= 5


def test_phase3_resilience_under_external_outage(
    client: TestClient, traveller_headers: dict, p3_destination: Destination
):
    """Ensure complete system resilience when external weather & LLM adapters experience outage."""
    with patch("app.services.weather_service.WeatherService._fetch_open_meteo", return_value=None), \
         patch("app.services.ai_providers.MockLLMProvider.generate", side_effect=Exception("External LLM API network failure")):

        # Request trip with explicit AI flag
        create_resp = client.post(
            "/api/v1/trips",
            json={
                "destination_id": p3_destination.id,
                "starting_location": "Jaipur",
                "start_date": str(date.today() + timedelta(days=20)),
                "end_date": str(date.today() + timedelta(days=22)),
                "traveller_count": 1,
                "total_budget": "12000.00",
                "generate_plan": True,
            },
            headers=traveller_headers,
        )

        assert create_resp.status_code == 201
        data = create_resp.json()
        assert data["status"] == "planned"
        assert len(data["itineraries"]) == 1

        # Check weather endpoint returns resilient fallback
        w_resp = client.get(f"/api/v1/trips/{data['id']}/weather", headers=traveller_headers)
        assert w_resp.status_code == 200
        assert w_resp.json()["provider"] == "mock"
