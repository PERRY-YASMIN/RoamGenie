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
