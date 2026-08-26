from datetime import date
from decimal import Decimal
import pytest

from app.db.models.catalogue import Attraction, Destination, Hotel, Restaurant, TransportOption
from app.services.budget_optimizer import BudgetOptimizer


@pytest.fixture
def optimizer_destination() -> Destination:
    dest = Destination(
        id=10,
        city="Kochi",
        country="India",
        description="Coastal Heritage City",
        average_daily_cost=Decimal("4200.00"),
        active=True,
    )
    dest.hotels = [
        Hotel(id=1, destination_id=10, name="Grand Luxury Fort Hotel", price_per_night=Decimal("6000.00"), rating=Decimal("4.9")),
        Hotel(id=2, destination_id=10, name="Budget Heritage Homestay", price_per_night=Decimal("1500.00"), rating=Decimal("4.2")),
    ]
    dest.restaurants = [
        Restaurant(id=1, destination_id=10, name="Fine Dining Seafood", cuisine="Seafood", average_cost_per_person=Decimal("800.00"), rating=Decimal("4.8")),
        Restaurant(id=2, destination_id=10, name="Local Coastal Cafe", cuisine="Kerala Meals", average_cost_per_person=Decimal("150.00"), rating=Decimal("4.3")),
    ]
    dest.attractions = [
        Attraction(id=1, destination_id=10, name="Fort Kochi Walk", category="heritage", entry_fee=Decimal("0.00"), rating=Decimal("4.7")),
        Attraction(id=2, destination_id=10, name="Mattancherry Palace", category="heritage", entry_fee=Decimal("25.00"), rating=Decimal("4.5")),
    ]
    dest.transport_options = [
        TransportOption(id=1, destination_id=10, origin="Bengaluru", mode="flight", provider="Air India", estimated_cost=Decimal("3500.00")),
        TransportOption(id=2, destination_id=10, origin="Bengaluru", mode="train", provider="Ernakulam Superfast", estimated_cost=Decimal("600.00")),
    ]
    return dest


def test_optimizer_already_within_budget(optimizer_destination: Destination):
    """When the initial schedule is within budget, no optimization modifications should occur."""
    optimizer = BudgetOptimizer()
    result = optimizer.optimize(
        destination=optimizer_destination,
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 3),
        traveller_count=1,
        starting_location="Bengaluru",
        total_budget=Decimal("50000.00"),  # Generous budget
    )
    assert result.optimization_applied is False
    assert result.budget_result.status == "within_budget"
    assert result.budget_result.deficit == Decimal("0.00")
    assert result.schedule_result.selected_hotel.name == "Grand Luxury Fort Hotel"


def test_optimizer_swaps_to_economical_options(optimizer_destination: Destination):
    """When budget is tight, optimizer swaps luxury hotel/flight for budget homestay/train."""
    optimizer = BudgetOptimizer()
    # Luxury trip cost would be ~ (3500 flight*2) + (6000 hotel*2) + food/attractions = > 20000
    # Budget of 8000 forces swap to 1500 hotel and 600 train
    result = optimizer.optimize(
        destination=optimizer_destination,
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 3),
        traveller_count=1,
        starting_location="Bengaluru",
        total_budget=Decimal("8000.00"),
    )
    assert result.optimization_applied is True
    assert result.budget_result.status in ("within_budget", "exact")
    assert result.budget_result.deficit == Decimal("0.00")
    assert result.schedule_result.selected_hotel.name == "Budget Heritage Homestay"
    assert result.schedule_result.selected_transport.mode == "train"


def test_optimizer_unavoidable_deficit(optimizer_destination: Destination):
    """When budget is impossibly low (e.g. 500 for a 3-day trip), report clear deficit without corrupting constraints."""
    optimizer = BudgetOptimizer()
    result = optimizer.optimize(
        destination=optimizer_destination,
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 3),
        traveller_count=2,
        starting_location="Bengaluru",
        total_budget=Decimal("500.00"),  # Impossibly low
    )
    # Trip dates, destination, traveller count must remain untouched
    assert result.schedule_result.day_count == 3
    assert result.schedule_result.traveller_count == 2
    assert result.budget_result.status == "over_budget"
    assert result.budget_result.deficit > Decimal("0.00")
    assert len(result.warnings) > 0
    assert any("Unavoidable deficit" in w for w in result.warnings)
