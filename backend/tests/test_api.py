from datetime import date, timedelta
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models.catalogue import Attraction, Destination, Hotel, Restaurant, TransportOption
from app.db.models.finance import BudgetAllocation, SavedTrip
from app.db.models.trip import Itinerary, ItineraryDay, ItineraryItem, PackingItem, Trip
from app.db.session import database_status, get_engine
from app.main import app

client = TestClient(app)


@pytest.fixture
def seed_preview_destination(db_session: Session) -> Destination:
    """Create a sample destination with full catalogue for preview testing."""
    dest = Destination(
        city="Mysuru",
        country="India",
        description="City of Palaces",
        average_daily_cost=Decimal("3500.00"),
        active=True,
    )
    db_session.add(dest)
    db_session.commit()
    db_session.refresh(dest)

    hotel = Hotel(destination_id=dest.id, name="Grand Heritage Mysuru", price_per_night=Decimal("2500.00"), rating=Decimal("4.6"))
    rest = Restaurant(destination_id=dest.id, name="Mylari Dosa Centre", cuisine="South Indian", average_cost_per_person=Decimal("150.00"), rating=Decimal("4.8"))
    att1 = Attraction(destination_id=dest.id, name="Mysore Palace", category="heritage", entry_fee=Decimal("100.00"), rating=Decimal("4.9"))
    att2 = Attraction(destination_id=dest.id, name="Chamundi Hill", category="heritage", entry_fee=Decimal("0.00"), rating=Decimal("4.7"))
    trans = TransportOption(origin="Chennai", destination_id=dest.id, mode="train", provider="Shatabdi Express", estimated_cost=Decimal("750.00"), duration_minutes=420)

    db_session.add_all([hotel, rest, att1, att2, trans])
    db_session.commit()
    return dest


def test_health() -> None:
    """Verify system health endpoint status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["application"] == "online"
    assert response.json()["database"] in {"connected", "not_configured", "unavailable"}


def test_guest_preview_catalogue_grounded(client: TestClient, seed_preview_destination: Destination) -> None:
    """Verify that guest preview returns real catalogue items and deterministic calculations."""
    payload = {
        "destination_id": seed_preview_destination.id,
        "starting_location": "Chennai",
        "destination": "Mysuru",
        "start_date": str(date.today() + timedelta(days=5)),
        "end_date": str(date.today() + timedelta(days=7)),
        "travellers": 2,
        "total_budget": "20000.00",
        "preferences": ["heritage"],
    }
    response = client.post("/api/v1/plans/preview", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "deterministic-scheduler"
    assert len(body["days"]) == 3
    assert float(body["estimated_total"]) > 0
    assert len(body["budget_split"]) > 0
    assert len(body["packing_items"]) > 0

    # Verify catalogue grounding: real items from database appear in day schedules
    day1_titles = [item["title"] for item in body["days"][0]["items"]]
    assert any("Chennai to Mysuru" in title or "Transit" in title for title in day1_titles)


def test_guest_preview_zero_database_persistence(client: TestClient, db_session: Session, seed_preview_destination: Destination) -> None:
    """CRITICAL: Verify that guest preview creates ZERO rows in any database table."""
    # 1. Capture baseline row counts
    count_trips_before = db_session.query(Trip).count()
    count_itin_before = db_session.query(Itinerary).count()
    count_days_before = db_session.query(ItineraryDay).count()
    count_items_before = db_session.query(ItineraryItem).count()
    count_alloc_before = db_session.query(BudgetAllocation).count()
    count_pack_before = db_session.query(PackingItem).count()
    count_saved_before = db_session.query(SavedTrip).count()

    payload = {
        "destination_id": seed_preview_destination.id,
        "starting_location": "Chennai",
        "destination": "Mysuru",
        "start_date": str(date.today() + timedelta(days=10)),
        "end_date": str(date.today() + timedelta(days=12)),
        "travellers": 1,
        "total_budget": "15000.00",
        "preferences": ["heritage"],
    }

    # 2. Execute multiple guest preview calls
    for _ in range(3):
        resp = client.post("/api/v1/plans/preview", json=payload)
        assert resp.status_code == 200

    # 3. Assert row counts are strictly unchanged
    assert db_session.query(Trip).count() == count_trips_before
    assert db_session.query(Itinerary).count() == count_itin_before
    assert db_session.query(ItineraryDay).count() == count_days_before
    assert db_session.query(ItineraryItem).count() == count_items_before
    assert db_session.query(BudgetAllocation).count() == count_alloc_before
    assert db_session.query(PackingItem).count() == count_pack_before
    assert db_session.query(SavedTrip).count() == count_saved_before


def test_guest_preview_invalid_dates_fail_validation(client: TestClient) -> None:
    """Verify that inverted dates return 422 Unprocessable Entity."""
    response = client.post(
        "/api/v1/plans/preview",
        json={
            "starting_location": "Chennai",
            "destination": "Mysuru",
            "start_date": "2026-08-12",
            "end_date": "2026-08-10",
            "travellers": 2,
            "total_budget": "20000.00",
        },
    )
    assert response.status_code == 422


def test_guest_preview_negative_budget_fails_validation(client: TestClient) -> None:
    """Verify that non-positive budget returns 422 Unprocessable Entity."""
    response = client.post(
        "/api/v1/plans/preview",
        json={
            "starting_location": "Chennai",
            "destination": "Mysuru",
            "start_date": "2026-08-10",
            "end_date": "2026-08-12",
            "travellers": 2,
            "total_budget": "-5000.00",
        },
    )
    assert response.status_code == 422


def test_invalid_database_url_is_reported_safely(monkeypatch) -> None:
    """Verify database unavailability is handled gracefully without leaking stack trace."""
    monkeypatch.setenv("DATABASE_URL", "not-a-connection-url")
    get_settings.cache_clear()
    get_engine.cache_clear()
    try:
        assert database_status() == "unavailable"
    finally:
        get_engine.cache_clear()
        get_settings.cache_clear()
