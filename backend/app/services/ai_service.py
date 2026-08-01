from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from app.schemas.itinerary import (
    BudgetCategory,
    ItineraryDay,
    ItineraryItem,
    ItineraryProposal,
    TripPlanRequest,
)


class MockAIService:
    """Deterministic development fallback; it never reads or writes the database."""

    provider_name = "mock"

    def generate_itinerary(self, trip: TripPlanRequest) -> ItineraryProposal:
        day_count = (trip.end_date - trip.start_date).days + 1
        categories = {
            "accommodation": Decimal("0.35"),
            "transport": Decimal("0.20"),
            "food": Decimal("0.20"),
            "activities": Decimal("0.15"),
            "contingency": Decimal("0.10"),
        }
        split = [
            BudgetCategory(
                category=name,
                amount=(trip.total_budget * share).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            )
            for name, share in categories.items()
        ]
        daily_activity = split[3].amount / day_count
        days = [
            ItineraryDay(
                day_number=index + 1,
                date=trip.start_date + timedelta(days=index),
                items=[
                    ItineraryItem(
                        time="09:00",
                        title=f"Explore {trip.destination}: day {index + 1}",
                        category="activity",
                        estimated_cost=daily_activity.quantize(Decimal("0.01")),
                    )
                ],
            )
            for index in range(day_count)
        ]
        estimated_total = sum((item.amount for item in split), Decimal("0.00"))
        remaining = trip.total_budget - estimated_total
        preferences = ", ".join(trip.preferences) if trip.preferences else "general sightseeing"
        return ItineraryProposal(
            provider=self.provider_name,
            summary=f"A {day_count}-day starter plan for {trip.destination}, focused on {preferences}.",
            days=days,
            budget_split=split,
            estimated_total=estimated_total,
            remaining_budget=remaining,
            warnings=["Estimated cost exceeds the budget."] if remaining < 0 else [],
            packing_items=["identity documents", "weather-appropriate clothing", "medicines", "reusable water bottle"],
        )


def get_ai_service() -> MockAIService:
    # TODO(M4/Madhu): choose a real provider adapter when configured, validate its
    # JSON, use one bounded retry, and fall back to this implementation.
    return MockAIService()

