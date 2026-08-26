from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
import pytest

from app.db.models.catalogue import Destination, Hotel, Attraction, Restaurant, TransportOption
from app.db.models.trip import Trip
from app.services.ai_orchestrator import AIPlanOrchestrator
from app.services.ai_providers import BaseLLMProvider, LLMProviderError


@pytest.fixture
def sample_dest() -> Destination:
    dest = Destination(
        id=5,
        city="Jaipur",
        country="India",
        description="The Pink City",
        average_daily_cost=Decimal("4000.00"),
        active=True,
    )
    dest.hotels = [Hotel(id=1, destination_id=5, name="Hotel Jaipur", price_per_night=Decimal("2000.00"), rating=Decimal("4.5"))]
    dest.restaurants = [Restaurant(id=1, destination_id=5, name="LMB", cuisine="Rajasthani", average_cost_per_person=Decimal("300.00"))]
    dest.attractions = [Attraction(id=1, destination_id=5, name="Amber Fort", category="heritage", entry_fee=Decimal("100.00"))]
    dest.transport_options = [TransportOption(id=1, destination_id=5, origin="Delhi", mode="train", estimated_cost=Decimal("600.00"))]
    return dest


class FakeLLMProvider(BaseLLMProvider):
    def __init__(self, response_text: str = "", should_raise: bool = False):
        self.response_text = response_text
        self.should_raise = should_raise

    @property
    def provider_name(self) -> str:
        return "fake-llm"

    def generate(self, prompt: str, system_prompt: str, timeout_seconds: int = 15) -> str:
        if self.should_raise:
            raise LLMProviderError("Simulated LLM API network error")
        return self.response_text


def test_orchestrator_valid_ai_response(sample_dest: Destination):
    """Test AI orchestrator successfully parsing valid structured LLM JSON."""
    valid_json = """{
        "summary": "AI Curated Heritage Expedition in Jaipur",
        "days": [
            {
                "day_number": 1,
                "date": "2026-09-10",
                "items": [
                    {
                        "time": "09:00",
                        "title": "Amber Fort Exploration",
                        "category": "attractions",
                        "estimated_cost": 100.00,
                        "notes": "Ascend to the hilltop palace courtyards"
                    },
                    {
                        "time": "13:00",
                        "title": "Traditional Thali at LMB",
                        "category": "food",
                        "estimated_cost": 300.00,
                        "notes": "Authentic vegetarian dishes"
                    }
                ]
            }
        ],
        "budget_split": [
            {"category": "attractions", "amount": 100.00},
            {"category": "food", "amount": 300.00}
        ],
        "warnings": [],
        "packing_items": ["Walking shoes", "Cotton scarf"],
        "weather_advice": "Sunny afternoon; carry water bottle."
    }"""

    provider = FakeLLMProvider(response_text=valid_json)
    orchestrator = AIPlanOrchestrator(provider=provider)

    schedule_res, is_ai, provider_name, packing, weather_adv, warnings = orchestrator.generate_plan(
        destination=sample_dest,
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 10),
        traveller_count=1,
        starting_location="Delhi",
        total_budget=Decimal("5000.00"),
        force_ai=True,
    )

    assert is_ai is True
    assert provider_name == "ai-fake-llm"
    assert schedule_res.day_count == 1
    assert len(schedule_res.days[0].items) == 2
    assert "Walking shoes" in packing
    assert weather_adv == "Sunny afternoon; carry water bottle."


def test_orchestrator_malformed_json_fallback(sample_dest: Destination):
    """Test AI orchestrator catching malformed JSON and cleanly activating deterministic fallback."""
    provider = FakeLLMProvider(response_text="Not valid JSON at all")
    orchestrator = AIPlanOrchestrator(provider=provider)

    schedule_res, is_ai, provider_name, packing, weather_adv, warnings = orchestrator.generate_plan(
        destination=sample_dest,
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 11),
        traveller_count=1,
        starting_location="Delhi",
        total_budget=Decimal("10000.00"),
        force_ai=True,
    )

    assert is_ai is False
    assert provider_name == "engine-v2-fallback"
    assert schedule_res.day_count == 2
    assert any("[AI Service Notice]" in w for w in warnings)


def test_orchestrator_schema_mismatch_fallback(sample_dest: Destination):
    """Test AI orchestrator rejecting response when day count does not match the trip date range."""
    # Returns 1 day for a 2-day trip
    invalid_days_json = """{
        "summary": "Mismatched Day Plan",
        "days": [
            {
                "day_number": 1,
                "date": "2026-09-10",
                "items": [{"time": "09:00", "title": "Sightseeing", "category": "attractions", "estimated_cost": 100}]
            }
        ],
        "budget_split": [],
        "warnings": [],
        "packing_items": []
    }"""

    provider = FakeLLMProvider(response_text=invalid_days_json)
    orchestrator = AIPlanOrchestrator(provider=provider)

    schedule_res, is_ai, provider_name, packing, weather_adv, warnings = orchestrator.generate_plan(
        destination=sample_dest,
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 11),  # 2 days requested
        traveller_count=1,
        starting_location="Delhi",
        total_budget=Decimal("10000.00"),
        force_ai=True,
    )

    assert is_ai is False
    assert provider_name == "engine-v2-fallback"
    assert schedule_res.day_count == 2


def test_orchestrator_provider_exception_fallback(sample_dest: Destination):
    """Test AI orchestrator handling provider network exceptions with seamless fallback."""
    provider = FakeLLMProvider(should_raise=True)
    orchestrator = AIPlanOrchestrator(provider=provider)

    schedule_res, is_ai, provider_name, packing, weather_adv, warnings = orchestrator.generate_plan(
        destination=sample_dest,
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 11),
        traveller_count=1,
        starting_location="Delhi",
        total_budget=Decimal("10000.00"),
        force_ai=True,
    )

    assert is_ai is False
    assert provider_name == "engine-v2-fallback"
    assert schedule_res.day_count == 2


def test_orchestrator_chat_valid_ai_response():
    """M5: Verify orchestrator parses structured JSON chat reply."""
    valid_chat_json = """{
        "reply": "For your trip to Jaipur, make sure to visit Amber Fort in the morning.",
        "suggested_actions": ["Explore Amber Fort", "View Budget", "Check Weather"]
    }"""
    provider = FakeLLMProvider(response_text=valid_chat_json)
    orchestrator = AIPlanOrchestrator(provider=provider)

    reply, actions, provider_name = orchestrator.chat(
        user_message="What should I visit?",
        force_ai=True,
    )

    assert "Amber Fort" in reply
    assert len(actions) == 3
    assert provider_name == "ai-fake-llm"


def test_orchestrator_chat_provider_exception_fallback(sample_dest: Destination):
    """M5: Verify orchestrator falls back to grounded deterministic response on provider failure."""
    provider = FakeLLMProvider(should_raise=True)
    orchestrator = AIPlanOrchestrator(provider=provider)

    trip = Trip(
        destination=sample_dest,
        starting_location="Delhi",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 12),
        traveller_count=2,
        total_budget=Decimal("20000.00"),
        estimated_total=Decimal("18000.00"),
    )

    reply, actions, provider_name = orchestrator.chat(
        user_message="What should I pack for this trip?",
        trip=trip,
        force_ai=True,
    )

    assert "Jaipur" in reply
    assert "pack" in reply.lower() or "walking shoes" in reply.lower()
    assert len(actions) > 0
    assert provider_name == "ai-fallback"

