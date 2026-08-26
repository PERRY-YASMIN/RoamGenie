from datetime import date, time
from decimal import Decimal
import pytest

from app.db.models.catalogue import Attraction, Destination, Hotel, Restaurant, TransportOption
from app.services.itinerary_scheduler import DeterministicScheduler


@pytest.fixture
def populated_destination() -> Destination:
    dest = Destination(
        id=1,
        city="Mysuru",
        country="India",
        description="Heritage City",
        average_daily_cost=Decimal("3500.00"),
        active=True,
    )
    dest.hotels = [
        Hotel(id=1, destination_id=1, name="Royal Orchid", price_per_night=Decimal("4500.00"), rating=Decimal("4.7")),
        Hotel(id=2, destination_id=1, name="Heritage Garden Stay", price_per_night=Decimal("2500.00"), rating=Decimal("4.2")),
    ]
    dest.restaurants = [
        Restaurant(id=1, destination_id=1, name="Mylari Tiffin", cuisine="South Indian", average_cost_per_person=Decimal("250.00"), rating=Decimal("4.8")),
        Restaurant(id=2, destination_id=1, name="Gufha Cave", cuisine="North Indian", average_cost_per_person=Decimal("650.00"), rating=Decimal("4.3")),
    ]
    dest.attractions = [
        Attraction(id=1, destination_id=1, name="Mysuru Palace", category="heritage", entry_fee=Decimal("100.00"), rating=Decimal("4.9")),
        Attraction(id=2, destination_id=1, name="Chamundi Hill", category="temple", entry_fee=Decimal("0.00"), rating=Decimal("4.6")),
        Attraction(id=3, destination_id=1, name="Brindavan Gardens", category="nature", entry_fee=Decimal("50.00"), rating=Decimal("4.2")),
    ]
    dest.transport_options = [
        TransportOption(id=1, destination_id=1, origin="Bengaluru", mode="train", provider="Vande Bharat", estimated_cost=Decimal("550.00"), duration_minutes=120),
    ]
    return dest


def test_single_day_schedule(populated_destination: Destination):
    """Test generating schedule for a 1-day trip."""
    scheduler = DeterministicScheduler()
    result = scheduler.schedule(
        destination=populated_destination,
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 1),
        traveller_count=2,
        starting_location="Bengaluru",
    )
    assert result.day_count == 1
    assert len(result.days) == 1
    day1 = result.days[0]
    assert len(day1.items) >= 4
    # Check arrival and departure transit are present
    categories = [it.category for it in day1.items]
    assert "transportation" in categories
    assert "food" in categories
    assert "attractions" in categories


def test_multi_day_schedule(populated_destination: Destination):
    """Test generating schedule for a 3-day trip."""
    scheduler = DeterministicScheduler()
    result = scheduler.schedule(
        destination=populated_destination,
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 3),
        traveller_count=2,
        starting_location="Bengaluru",
        preferences=["heritage"],
    )
    assert result.day_count == 3
    assert len(result.days) == 3
    # First day has check-in, middle day has stay, final day has check-out
    assert any("Check-in" in it.title for it in result.days[0].items)
    assert any("Stay at" in it.title for it in result.days[1].items)
    assert any("Check-out" in it.title for it in result.days[2].items)


def test_empty_catalogue_graceful_handling():
    """Ensure scheduler does not crash when destination has no hotels/attractions/dining."""
    empty_dest = Destination(
        id=99,
        city="Remote Village",
        country="India",
        description="Remote location",
        active=True,
    )
    empty_dest.hotels = []
    empty_dest.restaurants = []
    empty_dest.attractions = []
    empty_dest.transport_options = []

    scheduler = DeterministicScheduler()
    result = scheduler.schedule(
        destination=empty_dest,
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 2),
        traveller_count=1,
        starting_location="Unknown City",
    )
    assert result.day_count == 2
    assert len(result.days) == 2


def test_deterministic_reproducibility(populated_destination: Destination):
    """Ensure two runs with identical inputs produce identical schedule outputs."""
    scheduler = DeterministicScheduler()
    res1 = scheduler.schedule(
        destination=populated_destination,
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 3),
        traveller_count=2,
        starting_location="Bengaluru",
    )
    res2 = scheduler.schedule(
        destination=populated_destination,
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 3),
        traveller_count=2,
        starting_location="Bengaluru",
    )
    assert len(res1.days) == len(res2.days)
    for d1, d2 in zip(res1.days, res2.days):
        assert len(d1.items) == len(d2.items)
        for i1, i2 in zip(d1.items, d2.items):
            assert i1.title == i2.title
            assert i1.estimated_cost == i2.estimated_cost
            assert i1.category == i2.category
