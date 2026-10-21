from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
from typing import Any, Dict, List, Optional
import pytest

from app.db.models.catalogue import Destination, Hotel, Attraction, Restaurant, TransportOption
from app.db.models.trip import Trip
from app.db.models.user import User
from app.services.ai_orchestrator import AIPlanOrchestrator
from app.services.ai_providers import BaseLLMProvider, LLMProviderError, LLMResponse


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
    def __init__(self, response_text: str = "", should_raise: bool = False, function_call: Optional[Dict[str, Any]] = None):
        self.response_text = response_text
        self.should_raise = should_raise
        self.function_call = function_call

    @property
    def provider_name(self) -> str:
        return "fake-llm"

    def generate(
        self,
        prompt: str,
        system_prompt: str,
        timeout_seconds: int = 15,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_config: Optional[Dict[str, Any]] = None,
        contents: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        if self.should_raise:
            raise LLMProviderError("Simulated LLM API network error")
        if self.function_call:
            return LLMResponse(content="", function_call=self.function_call)
        return LLMResponse(self.response_text)


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

    reply, actions, provider_name, proposed_changes, clarification = orchestrator.chat(
        user_message="What should I visit?",
        force_ai=True,
    )

    assert "Amber Fort" in reply
    assert len(actions) == 3
    assert provider_name == "ai-fake-llm"
    assert proposed_changes is None
    assert clarification is None


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

    reply, actions, provider_name, proposed_changes, clarification = orchestrator.chat(
        user_message="What should I pack for this trip?",
        trip=trip,
        force_ai=True,
    )

    assert "Jaipur" in reply
    assert "pack" in reply.lower() or "walking shoes" in reply.lower()
    assert len(actions) > 0
    assert provider_name == "ai-fallback"
    assert proposed_changes is None
    assert clarification is None


class SequenceLLMProvider(BaseLLMProvider):
    def __init__(self, responses: List[Any]):
        self.responses = list(responses)
        self.call_count = 0

    @property
    def provider_name(self) -> str:
        return "sequence-llm"

    def generate(
        self,
        prompt: str,
        system_prompt: str,
        timeout_seconds: int = 15,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_config: Optional[Dict[str, Any]] = None,
        contents: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        self.call_count += 1
        resp = self.responses.pop(0) if self.responses else "fallback"
        if isinstance(resp, LLMResponse):
            return resp
        if isinstance(resp, dict) and "function_call" in resp:
            return LLMResponse(content="", function_call=resp["function_call"])
        return LLMResponse(str(resp))


def test_orchestrator_chat_malformed_json_retry_success():
    """Step 2: Orchestrator recovers when initial response is malformed JSON and retry returns valid JSON."""
    valid_chat_json = """{
        "reply": "I recovered successfully after the prompt reminder.",
        "suggested_actions": ["Action A", "Action B"]
    }"""
    # 1st call: malformed plain text; 2nd call (retry): valid JSON
    provider = SequenceLLMProvider([
        "Sorry, I cannot return JSON right now, here is some plain text.",
        valid_chat_json,
    ])
    orchestrator = AIPlanOrchestrator(provider=provider)

    reply, actions, provider_name, proposed_changes, clarification = orchestrator.chat(
        user_message="Hello",
        force_ai=True,
    )

    assert "recovered successfully" in reply
    assert actions == ["Action A", "Action B"]
    assert provider.call_count == 2
    assert clarification is None


def test_orchestrator_chat_malformed_json_retry_exhausted():
    """Step 2: When all retries return malformed JSON, orchestrator returns hardcoded error fallback."""
    # 1st call + 2 retries = 3 calls total, all invalid
    provider = SequenceLLMProvider([
        "Malformed plain text 1",
        "Malformed plain text 2",
        "Malformed plain text 3",
    ])
    orchestrator = AIPlanOrchestrator(provider=provider)

    reply, actions, provider_name, proposed_changes, clarification = orchestrator.chat(
        user_message="Hello",
        force_ai=True,
    )

    assert "I encountered an error parsing the travel plan details" in reply
    assert provider_name == "ai-fallback"
    assert provider.call_count >= 2
    assert clarification is None


def test_orchestrator_chat_tool_failure_recovery():
    """Step 2: If a tool returns an error, orchestrator appends functionResponse error and loops back for LLM apology."""
    from unittest.mock import MagicMock
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 1

    apology_json = """{
        "reply": "I apologize, but trip #999 was not found in your records. Could you please specify a valid trip ID?",
        "suggested_actions": ["Show my trips", "Try again"]
    }"""

    # 1st turn: model calls tool with invalid trip_id 999; 2nd turn: model receives tool error and returns apology
    provider = SequenceLLMProvider([
        {"function_call": {"name": "get_itinerary_details", "args": {"trip_id": 999}}},
        apology_json,
    ])
    orchestrator = AIPlanOrchestrator(provider=provider)

    reply, actions, provider_name, proposed_changes, clarification = orchestrator.chat(
        user_message="Show details for trip 999",
        current_user=mock_user,
        db=mock_db,
        force_ai=True,
    )

    assert "apologize" in reply.lower() or "not found" in reply.lower()
    assert "Show my trips" in actions
    assert provider.call_count == 2
    assert clarification is None


def test_orchestrator_chat_clarification_request_structured():
    """Step 2: Orchestrator validates and passes structured clarification_request when LLM asks for clarification."""
    clarification_json = """{
        "reply": "I'd be glad to help adjust your plans! Which night would you like to change?",
        "suggested_actions": ["Day 1", "Day 2", "Cancel"],
        "clarification_request": {
            "question": "Which night would you like to change?",
            "options": ["Day 1 - Oct 22", "Day 2 - Oct 23"],
            "allow_custom_input": true
        }
    }"""
    provider = FakeLLMProvider(response_text=clarification_json)
    orchestrator = AIPlanOrchestrator(provider=provider)

    reply, actions, provider_name, proposed_changes, clarification = orchestrator.chat(
        user_message="Change my plans for tonight",
        force_ai=True,
    )

    assert "adjust your plans" in reply
    assert clarification is not None
    assert clarification.question == "Which night would you like to change?"
    assert clarification.options == ["Day 1 - Oct 22", "Day 2 - Oct 23"]
    assert clarification.allow_custom_input is True


def test_orchestrator_chat_ambiguous_fallback_clarification(sample_dest: Destination):
    """Step 2: Orchestrator deterministic fallback returns clarification_request for ambiguous modification query."""
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

    reply, actions, provider_name, proposed_changes, clarification = orchestrator.chat(
        user_message="Change my plans for tonight",
        trip=trip,
        force_ai=True,
    )

    assert "schedule" in reply.lower() or "adjust" in reply.lower()
    assert clarification is not None
    assert "night or day" in clarification.question.lower()
    assert len(clarification.options) > 0
    assert clarification.allow_custom_input is True


def test_orchestrator_chat_splurge_upgrade_intent(sample_dest: Destination):
    """Orchestrator fallback handles splurge / upgrade inquiry with surplus budget gracefully."""
    provider = FakeLLMProvider(should_raise=True)
    orchestrator = AIPlanOrchestrator(provider=provider)

    trip = Trip(
        destination=sample_dest,
        starting_location="Delhi",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 14),
        traveller_count=2,
        total_budget=Decimal("45000.00"),
        estimated_total=Decimal("19550.00"),
    )

    reply, actions, provider_name, proposed_changes, clarification = orchestrator.chat(
        user_message="then lets add some more expenses",
        trip=trip,
        force_ai=True,
    )

    assert "surplus" in reply.lower() or "25,450" in reply
    assert "luxury" in reply.lower() or "fine dining" in reply.lower()
    assert len(actions) >= 2


def test_orchestrator_chat_general_weekend_getaway():
    """Orchestrator general advice fallback handles open-ended travel questions comprehensively."""
    provider = FakeLLMProvider(should_raise=True)
    orchestrator = AIPlanOrchestrator(provider=provider)

    reply, actions, provider_name, proposed_changes, clarification = orchestrator.chat(
        user_message="suggest a weekend getaway from Delhi",
        trip=None,
        force_ai=True,
    )

    assert "Rishikesh" in reply or "Jaipur" in reply
    assert len(actions) >= 2

