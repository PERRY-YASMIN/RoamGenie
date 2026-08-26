from datetime import date, time
from decimal import Decimal
import pytest

from app.services.budget_service import BudgetCalculator
from app.services.itinerary_scheduler import ScheduledDay, ScheduledItem


def test_budget_within_limit():
    """Test budget calculation when total estimated cost is within budget."""
    calculator = BudgetCalculator()
    days = [
        ScheduledDay(
            day_number=1,
            itinerary_date=date(2026, 9, 1),
            items=[
                ScheduledItem(1, time(8, 0), "Train", "transportation", Decimal("550.00")),
                ScheduledItem(2, time(11, 0), "Hotel", "accommodation", Decimal("2500.00")),
                ScheduledItem(3, time(13, 0), "Lunch", "food", Decimal("400.00")),
                ScheduledItem(4, time(15, 0), "Museum", "attractions", Decimal("150.00")),
            ],
        )
    ]
    res = calculator.calculate(total_budget=Decimal("5000.00"), scheduled_days=days)
    assert res.total_budget == Decimal("5000.00")
    assert res.estimated_total == Decimal("3600.00")
    assert res.remaining_budget == Decimal("1400.00")
    assert res.deficit == Decimal("0.00")
    assert res.status == "within_budget"
    assert res.utilization_percentage == Decimal("72.00")
    assert len(res.warnings) == 0


def test_budget_exact_match():
    """Test budget calculation when total estimated cost matches total budget exactly."""
    calculator = BudgetCalculator()
    days = [
        ScheduledDay(
            day_number=1,
            itinerary_date=date(2026, 9, 1),
            items=[
                ScheduledItem(1, time(11, 0), "Hotel", "accommodation", Decimal("3000.00")),
                ScheduledItem(2, time(13, 0), "Lunch", "food", Decimal("2000.00")),
            ],
        )
    ]
    res = calculator.calculate(total_budget=Decimal("5000.00"), scheduled_days=days)
    assert res.estimated_total == Decimal("5000.00")
    assert res.remaining_budget == Decimal("0.00")
    assert res.deficit == Decimal("0.00")
    assert res.status == "exact"
    assert res.utilization_percentage == Decimal("100.00")


def test_budget_deficit_detection():
    """Test budget calculation when estimated cost exceeds available budget."""
    calculator = BudgetCalculator()
    days = [
        ScheduledDay(
            day_number=1,
            itinerary_date=date(2026, 9, 1),
            items=[
                ScheduledItem(1, time(11, 0), "Luxury Resort", "accommodation", Decimal("8000.00")),
                ScheduledItem(2, time(13, 0), "Gourmet Meal", "food", Decimal("3000.00")),
            ],
        )
    ]
    res = calculator.calculate(total_budget=Decimal("7000.00"), scheduled_days=days)
    assert res.estimated_total == Decimal("11000.00")
    assert res.remaining_budget == Decimal("-4000.00")
    assert res.deficit == Decimal("4000.00")
    assert res.status == "over_budget"
    assert res.utilization_percentage == Decimal("157.14")
    assert len(res.warnings) >= 1
    assert "₹4000.00" in res.warnings[0]


def test_monetary_decimal_precision():
    """Ensure floating point arithmetic errors (e.g. 0.1 + 0.2) do not occur."""
    calculator = BudgetCalculator()
    days = [
        ScheduledDay(
            day_number=1,
            itinerary_date=date(2026, 9, 1),
            items=[
                ScheduledItem(1, time(10, 0), "Item A", "food", Decimal("19.99")),
                ScheduledItem(2, time(11, 0), "Item B", "food", Decimal("20.01")),
                ScheduledItem(3, time(12, 0), "Item C", "attractions", Decimal("10.05")),
            ],
        )
    ]
    res = calculator.calculate(total_budget=Decimal("100.00"), scheduled_days=days)
    assert res.estimated_total == Decimal("50.05")
    assert res.remaining_budget == Decimal("49.95")
    assert isinstance(res.estimated_total, Decimal)
