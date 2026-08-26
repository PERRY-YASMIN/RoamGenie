"""Tests for D5 Transport Options Dataset and Generation Logic."""
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.catalogue import Destination, TransportOption
from scripts.database.seed_hotels_d3 import get_live_or_cached_destinations
from scripts.database.transport_data import (
    detect_environmental_features,
    generate_transport_catalog_for_destinations,
    get_destination_region,
)
from scripts.database.validate_transport_d5 import run_validation


def test_transport_catalog_generation_and_coverage() -> None:
    """Verify that transport catalog generates exactly 12 options for 500 destinations."""
    dest_tuples = get_live_or_cached_destinations(None)
    assert len(dest_tuples) == 500

    catalog = generate_transport_catalog_for_destinations(dest_tuples)
    assert len(catalog) == 500

    total_records = sum(len(v) for v in catalog.values())
    assert total_records == 6000

    for (city, country), trans_list in catalog.items():
        assert len(trans_list) == 12, f"Destination {city}, {country} has {len(trans_list)} transport options"
        for origin, mode, provider, cost, duration in trans_list:
            assert origin and len(origin) <= 100
            assert mode and len(mode) <= 40
            assert cost >= 0
            assert duration > 0


def test_transport_validation_script() -> None:
    """Run D5 validator and ensure status is PASS with zero issues."""
    report = run_validation()
    assert report["status"] == "PASS"
    assert len(report["issues"]) == 0
    assert report["metrics"]["total_transports"] == 6000
    assert report["checks"]["referential_integrity"]["passed"] is True
    assert report["checks"]["preserved_original_records"]["passed"] is True


def test_environmental_features_detection() -> None:
    """Test coastal and mountain environmental classifiers."""
    coastal = detect_environmental_features("Goa", "India", "Beaches, sea, and coastal palm groves")
    assert coastal["is_coastal"] is True

    mountain = detect_environmental_features("Manali", "India", "High altitude Himalayan snow peaks")
    assert mountain["is_mountain"] is True


def test_transport_options_api_filter_by_destination(client: TestClient, db_session: Session) -> None:
    """Test FastAPI transport-options endpoint filtering by destination_id and max_cost."""
    dest = Destination(
        city="Mysuru",
        country="India",
        description="Heritage city",
        average_daily_cost=Decimal("3500.00"),
        active=True,
    )
    db_session.add(dest)
    db_session.commit()
    db_session.refresh(dest)

    t1 = TransportOption(
        destination_id=dest.id,
        origin="Bengaluru",
        mode="train",
        provider="Vande Bharat",
        estimated_cost=Decimal("550.00"),
        duration_minutes=120,
    )
    t2 = TransportOption(
        destination_id=dest.id,
        origin="Bengaluru",
        mode="taxi",
        provider="Intercity Cab",
        estimated_cost=Decimal("2800.00"),
        duration_minutes=180,
    )
    db_session.add_all([t1, t2])
    db_session.commit()

    resp = client.get(f"/api/v1/transport-options?destination_id={dest.id}&max_cost=1000")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["mode"] == "train"
    assert items[0]["provider"] == "Vande Bharat"
