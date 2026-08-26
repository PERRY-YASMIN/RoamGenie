from datetime import date, timedelta
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.catalogue import Destination


@pytest.fixture
def sample_destination(db_session: Session) -> Destination:
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
    return dest


@pytest.fixture
def inactive_destination(db_session: Session) -> Destination:
    dest = Destination(
        city="Closed City",
        country="India",
        description="Under renovation",
        average_daily_cost=Decimal("2000.00"),
        active=False,
    )
    db_session.add(dest)
    db_session.commit()
    db_session.refresh(dest)
    return dest


def test_reject_end_date_before_start_date(client: TestClient, traveller_headers: dict, sample_destination: Destination):
    """Ensure trips with inverted date range are rejected."""
    payload = {
        "destination_id": sample_destination.id,
        "starting_location": "Delhi",
        "start_date": str(date.today() + timedelta(days=10)),
        "end_date": str(date.today() + timedelta(days=5)),
        "traveller_count": 2,
        "total_budget": "10000.00",
    }
    response = client.post("/api/v1/trips", json=payload, headers=traveller_headers)
    assert response.status_code == 422


def test_reject_trip_duration_exceeding_31_days(client: TestClient, traveller_headers: dict, sample_destination: Destination):
    """Ensure trips longer than 31 days are rejected."""
    payload = {
        "destination_id": sample_destination.id,
        "starting_location": "Delhi",
        "start_date": str(date.today() + timedelta(days=1)),
        "end_date": str(date.today() + timedelta(days=40)),
        "traveller_count": 1,
        "total_budget": "50000.00",
    }
    response = client.post("/api/v1/trips", json=payload, headers=traveller_headers)
    assert response.status_code == 422


def test_reject_invalid_travellers(client: TestClient, traveller_headers: dict, sample_destination: Destination):
    """Ensure zero or negative travellers are rejected."""
    payload_zero = {
        "destination_id": sample_destination.id,
        "starting_location": "Delhi",
        "start_date": str(date.today() + timedelta(days=1)),
        "end_date": str(date.today() + timedelta(days=3)),
        "traveller_count": 0,
        "total_budget": "10000.00",
    }
    assert client.post("/api/v1/trips", json=payload_zero, headers=traveller_headers).status_code == 422

    payload_huge = {
        "destination_id": sample_destination.id,
        "starting_location": "Delhi",
        "start_date": str(date.today() + timedelta(days=1)),
        "end_date": str(date.today() + timedelta(days=3)),
        "traveller_count": 100,
        "total_budget": "10000.00",
    }
    assert client.post("/api/v1/trips", json=payload_huge, headers=traveller_headers).status_code == 422


def test_reject_non_positive_budget(client: TestClient, traveller_headers: dict, sample_destination: Destination):
    """Ensure zero or negative budget is rejected."""
    payload = {
        "destination_id": sample_destination.id,
        "starting_location": "Delhi",
        "start_date": str(date.today() + timedelta(days=1)),
        "end_date": str(date.today() + timedelta(days=3)),
        "traveller_count": 2,
        "total_budget": "0.00",
    }
    assert client.post("/api/v1/trips", json=payload, headers=traveller_headers).status_code == 422


def test_reject_non_existent_destination(client: TestClient, traveller_headers: dict):
    """Ensure non-existent destination ID returns 404/422."""
    payload = {
        "destination_id": 99999,
        "starting_location": "Delhi",
        "start_date": str(date.today() + timedelta(days=1)),
        "end_date": str(date.today() + timedelta(days=3)),
        "traveller_count": 2,
        "total_budget": "10000.00",
    }
    response = client.post("/api/v1/trips", json=payload, headers=traveller_headers)
    assert response.status_code == 404


def test_reject_inactive_destination(client: TestClient, traveller_headers: dict, inactive_destination: Destination):
    """Ensure inactive destination returns 400."""
    payload = {
        "destination_id": inactive_destination.id,
        "starting_location": "Delhi",
        "start_date": str(date.today() + timedelta(days=1)),
        "end_date": str(date.today() + timedelta(days=3)),
        "traveller_count": 2,
        "total_budget": "10000.00",
    }
    response = client.post("/api/v1/trips", json=payload, headers=traveller_headers)
    assert response.status_code == 400


def test_patch_validation_constraints(client: TestClient, traveller_headers: dict, sample_destination: Destination):
    """Ensure PATCH re-validates date boundaries and budget constraints."""
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": sample_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=15)),
            "traveller_count": 2,
            "total_budget": "20000.00",
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]

    # Invalidate by moving start_date past end_date
    invalid_patch = client.patch(
        f"/api/v1/trips/{trip_id}",
        json={"start_date": str(date.today() + timedelta(days=20))},
        headers=traveller_headers,
    )
    assert invalid_patch.status_code == 422

    # Invalidate by setting invalid status
    invalid_status = client.patch(
        f"/api/v1/trips/{trip_id}",
        json={"status": "invalid_status_value"},
        headers=traveller_headers,
    )
    assert invalid_status.status_code == 422
