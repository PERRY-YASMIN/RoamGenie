import json
from unittest.mock import MagicMock, patch
import pytest

from app.config import Settings
from app.services.ai_providers import (
    GeminiLLMProvider,
    GroqLLMProvider,
    LLMProviderError,
    MockLLMProvider,
    OpenAILLMProvider,
    get_llm_provider,
)


def test_mock_llm_provider():
    """Verify MockLLMProvider returns valid JSON string without external network calls."""
    provider = MockLLMProvider()
    assert provider.provider_name == "mock"
    output = provider.generate("prompt", "system")
    parsed = json.loads(output)
    assert "summary" in parsed
    assert "days" in parsed
    assert len(parsed["days"]) >= 1


def test_gemini_llm_provider_mocked():
    """Verify GeminiLLMProvider formats request correctly and parses candidate text."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": '{"summary": "Gemini Tour", "days": []}'}]
                }
            }
        ]
    }

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        provider = GeminiLLMProvider(api_key="fake-gemini-key", model_name="gemini-1.5-flash")
        result = provider.generate("User query", "System instruction")
        assert result == '{"summary": "Gemini Tour", "days": []}'
        assert mock_post.called


def test_openai_llm_provider_mocked():
    """Verify OpenAILLMProvider formats request with JSON mode and parses content."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {"content": '{"summary": "OpenAI Tour", "days": []}'}
            }
        ]
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        provider = OpenAILLMProvider(api_key="fake-openai-key")
        result = provider.generate("User query", "System instruction")
        assert result == '{"summary": "OpenAI Tour", "days": []}'


def test_groq_llm_provider_mocked():
    """Verify GroqLLMProvider formats request and parses content."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {"content": '{"summary": "Groq Tour", "days": []}'}
            }
        ]
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        provider = GroqLLMProvider(api_key="fake-groq-key")
        result = provider.generate("User query", "System instruction")
        assert result == '{"summary": "Groq Tour", "days": []}'


def test_provider_error_handling():
    """Verify provider raises LLMProviderError on API failure."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized: Invalid API Key"

    with patch("httpx.Client.post", return_value=mock_resp):
        provider = GeminiLLMProvider(api_key="invalid-key")
        with pytest.raises(LLMProviderError) as exc_info:
            provider.generate("prompt", "sys")
        assert "401" in str(exc_info.value)


def test_provider_factory_selection():
    """Test get_llm_provider factory logic with API keys and fallback."""
    # 1. Configured Gemini with key
    cfg1 = Settings(ai_provider="gemini", gemini_api_key="test-key")
    p1 = get_llm_provider(cfg1)
    assert isinstance(p1, GeminiLLMProvider)

    # 2. Configured Gemini WITHOUT key -> defaults to mock
    cfg2 = Settings(ai_provider="gemini", gemini_api_key=None, ai_api_key=None)
    p2 = get_llm_provider(cfg2)
    assert isinstance(p2, MockLLMProvider)

    # 3. Configured OpenAI with key
    cfg3 = Settings(ai_provider="openai", openai_api_key="test-key")
    p3 = get_llm_provider(cfg3)
    assert isinstance(p3, OpenAILLMProvider)

    # 4. Default mock
    cfg4 = Settings(ai_provider="mock")
    p4 = get_llm_provider(cfg4)
    assert isinstance(p4, MockLLMProvider)


def test_mock_llm_provider_duration_query_not_rain():
    """Verify MockLLMProvider answers 'how many days trip is this' accurately and never leaks weather rain advice."""
    import json
    from app.services.ai_providers import MockLLMProvider
    provider = MockLLMProvider()
    prompt = '''USER QUERY: how many days trip is this

AUTHORIZED TRIP CONTEXT:
- Trip ID: 1
- Destination: Agartala (Capital of Tripura)
- Origin: Delhi
- Dates: 2026-10-27 to 2026-10-31 (5 days)
- Travellers: 2
- Total Budget: ₹45000.00
- Estimated Total: ₹45000.00
- Remaining Budget: ₹0.00 (Deficit: ₹0.00)

WEATHER FORECAST CONTEXT:
Current: Rain showers
- 2026-10-27: Rain, 22°C to 28°C (Rain prob: 0%)

JSON OUTPUT FORMAT:
{"reply": "...", "suggested_actions": []}'''

    output = provider.generate(prompt=prompt, system_prompt='You are RoamGenie AI Assistant')
    parsed = json.loads(output)
    assert 'reply' in parsed
    reply = parsed['reply']
    # Must report 5-day duration
    assert '5-day' in reply or '5 days' in reply or '5' in reply
    assert 'Agartala' in reply
    # Must NOT return canned rain advice
    assert 'indoor cultural sightseeing' not in reply.lower()
    assert 'encounter rain' not in reply.lower()


def test_mock_llm_provider_various_grounded_queries():
    """Verify MockLLMProvider handles dates, budget, travellers, and rain queries accurately."""
    import json
    from app.services.ai_providers import MockLLMProvider
    provider = MockLLMProvider()
    base_prompt = '''USER QUERY: {query}

AUTHORIZED TRIP CONTEXT:
- Trip ID: 1
- Destination: Agartala (Capital of Tripura)
- Origin: Delhi
- Dates: 2026-10-27 to 2026-10-31 (5 days)
- Travellers: 2
- Total Budget: ₹45000.00
- Estimated Total: ₹42000.00
- Remaining Budget: ₹3000.00 (Deficit: ₹0.00)

WEATHER FORECAST CONTEXT:
Current: Partly cloudy
- 2026-10-27: Partly cloudy, 22°C to 28°C (Rain prob: 10%)

JSON OUTPUT FORMAT:
{{"reply": "...", "suggested_actions": []}}'''

    # 1. Dates
    out_dates = json.loads(provider.generate(prompt=base_prompt.format(query='what are the dates of my trip'), system_prompt='assistant'))
    assert '2026-10-27' in out_dates['reply']
    assert '2026-10-31' in out_dates['reply']

    # 2. Travellers
    out_trav = json.loads(provider.generate(prompt=base_prompt.format(query='how many people are travelling'), system_prompt='assistant'))
    assert '2 traveller' in out_trav['reply']

    # 3. Budget
    out_budget = json.loads(provider.generate(prompt=base_prompt.format(query='what is my budget and remaining balance'), system_prompt='assistant'))
    assert '45,000' in out_budget['reply'] or '45000' in out_budget['reply']

    # 4. Weather (when explicitly asked)
    out_weather = json.loads(provider.generate(prompt=base_prompt.format(query='what is the weather forecast'), system_prompt='assistant'))
    assert 'forecast' in out_weather['reply'].lower() or 'weather' in out_weather['reply'].lower()


def test_mock_llm_provider_singular_day_trip_query():
    """Verify MockLLMProvider answers 'how many day trip is this?' (singular day) accurately."""
    import json
    from app.services.ai_providers import MockLLMProvider
    provider = MockLLMProvider()
    prompt = '''USER QUERY: how many day trip is this?

AUTHORIZED TRIP CONTEXT:
- Trip ID: 1
- Destination: Abu Dhabi, United Arab Emirates
- Origin: Delhi
- Dates: 2026-10-27 to 2026-10-31 (5 days)
- Travellers: 2
- Total Budget: ₹45000.00
- Estimated Total: ₹77600.00
- Remaining Budget: ₹-32600.00 (Deficit: ₹32600.00)

WEATHER FORECAST CONTEXT:
Current: Sunny, 32°C
- 2026-10-27: Sunny, 26°C to 34°C (Rain prob: 0%)

JSON OUTPUT FORMAT:
{"reply": "...", "suggested_actions": []}'''

    output = provider.generate(prompt=prompt, system_prompt='You are RoamGenie AI Assistant')
    parsed = json.loads(output)
    assert 'reply' in parsed
    reply = parsed['reply']
    assert '5-day' in reply or '5 days' in reply
    assert 'Abu Dhabi' in reply
    assert 'indoor cultural sightseeing' not in reply.lower()


def test_mock_llm_provider_splurge_upgrade_intent():
    """Verify MockLLMProvider recognizes splurge/upgrade intent and suggests luxury enhancements."""
    import json
    from app.services.ai_providers import MockLLMProvider
    provider = MockLLMProvider()
    prompt = '''USER QUERY: then lets add some more expenses

AUTHORIZED TRIP CONTEXT:
- Trip ID: 1
- Destination: Agartala, India
- Origin: Delhi
- Dates: 2026-10-27 to 2026-10-31 (5 days)
- Travellers: 2
- Total Budget: ₹45000.00
- Estimated Total: ₹19550.00
- Remaining Budget: ₹25450.00 (Deficit: ₹0.00)

JSON OUTPUT FORMAT:
{"reply": "...", "suggested_actions": []}'''

    output = provider.generate(prompt=prompt, system_prompt='You are RoamGenie AI Assistant')
    parsed = json.loads(output)
    assert 'reply' in parsed
    reply = parsed['reply']
    assert '25,450' in reply or 'surplus' in reply.lower()
    assert 'luxury' in reply.lower() or 'fine' in reply.lower()
    assert 'economical option' not in reply.lower()
    assert len(parsed['suggested_actions']) >= 2


def test_mock_llm_provider_general_travel_engine():
    """Verify MockLLMProvider provides rich ChatGPT-grade answers for general travel queries."""
    import json
    from app.services.ai_providers import MockLLMProvider
    provider = MockLLMProvider()

    # 1. Weekend getaway from Delhi
    out_delhi = json.loads(provider.generate(prompt='USER QUERY: suggest a weekend getaway from Delhi', system_prompt='assistant'))
    assert 'Rishikesh' in out_delhi['reply'] or 'Jaipur' in out_delhi['reply']
    assert len(out_delhi['suggested_actions']) >= 2

    # 2. Tatkal booking tricks
    out_tatkal = json.loads(provider.generate(prompt='USER QUERY: how to book tatkal tickets on IRCTC', system_prompt='assistant'))
    assert '10:00 AM' in out_tatkal['reply']
    assert 'Master Passenger List' in out_tatkal['reply']

    # 3. Solo travel safety
    out_solo = json.loads(provider.generate(prompt='USER QUERY: what are the best tips for solo travel', system_prompt='assistant'))
    assert 'hostel' in out_solo['reply'].lower()
    assert 'safety' in out_solo['reply'].lower()

    # 4. Packing formula
    out_pack = json.loads(provider.generate(prompt='USER QUERY: what is the 5-4-3-2-1 packing rule', system_prompt='assistant'))
    assert '5' in out_pack['reply'] and 'Capsule' in out_pack['reply']
