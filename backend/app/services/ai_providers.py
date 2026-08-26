import json
import logging
from abc import ABC, abstractmethod
from typing import Optional

import httpx

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class LLMProviderError(Exception):
    """Custom exception raised when an external LLM call fails."""
    pass


class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str, timeout_seconds: int = 15) -> str:
        """Invokes the external LLM and returns raw response string."""
        pass


class MockLLMProvider(BaseLLMProvider):
    @property
    def provider_name(self) -> str:
        return "mock"

    def generate(self, prompt: str, system_prompt: str, timeout_seconds: int = 15) -> str:
        # Check if chat / assistant copilot prompt
        if "copilot" in system_prompt.lower() or "assistant" in system_prompt.lower() or "user query:" in prompt.lower():
            dest_hint = ""
            for line in prompt.splitlines():
                if "Destination:" in line:
                    dest_hint = line.split("Destination:")[1].split("(")[0].strip()
                    break
            dest_text = f" for {dest_hint}" if dest_hint else ""

            # Check topic in prompt
            p_lower = prompt.lower()
            if "pack" in p_lower or "wear" in p_lower or "weather" in p_lower:
                reply = (
                    f"Based on the local forecast and your travel dates{dest_text}, I recommend packing lightweight breathable clothing, "
                    f"comfortable walking shoes, sunscreen, and an umbrella if rain is likely. Check your trip packing checklist to track packed items!"
                )
                actions = ["View Packing Checklist", "Check Live Weather Forecast", "Review Itinerary"]
            elif "budget" in p_lower or "cost" in p_lower or "deficit" in p_lower or "money" in p_lower:
                reply = (
                    f"I've analyzed your trip budget{dest_text}. To optimize expenses, consider choosing budget-friendly dining or exploring our alternative hotels. "
                    f"You can use the ⇄ Swap button on any itinerary event to replace it with a more economical option!"
                )
                actions = ["Review Budget Allocations", "Swap Itinerary Items", "Explore Free Attractions"]
            elif "food" in p_lower or "restaurant" in p_lower or "dining" in p_lower:
                reply = (
                    f"For dining{dest_text}, you have great authentic local restaurants in your destination catalogue. "
                    f"Check out the dining recommendations or swap a meal in your itinerary timeline!"
                )
                actions = ["Browse Restaurants", "Swap Dining Spot", "Check Itinerary"]
            else:
                reply = (
                    f"Hello! I am your RoamGenie AI Travel Copilot{dest_text}. I can assist you with optimizing your day-by-day itinerary, "
                    f"explaining budget allocations, checking weather forecasts, or providing local travel recommendations."
                )
                actions = ["What should I pack?", "How is my budget?", "Recommend local attractions"]

            return json.dumps({
                "reply": reply,
                "suggested_actions": actions,
            })

        # Returns structured mock json representation for itinerary planning
        return json.dumps({
            "summary": "AI Curated Cultural Experience",
            "days": [
                {
                    "day_number": 1,
                    "date": "2026-09-15",
                    "items": [
                        {
                            "time": "09:00",
                            "title": "Welcome Orientation & Palace Visit",
                            "category": "attractions",
                            "estimated_cost": 200.00,
                            "notes": "Enjoy the magnificent royal courtyards",
                        },
                        {
                            "time": "13:00",
                            "title": "Authentic Regional Lunch",
                            "category": "food",
                            "estimated_cost": 400.00,
                            "notes": "Sample traditional culinary delights",
                        },
                    ],
                }
            ],
            "budget_split": [
                {"category": "accommodation", "amount": 2800.00},
                {"category": "food", "amount": 1200.00},
                {"category": "attractions", "amount": 600.00},
            ],
            "warnings": [],
            "packing_items": [
                "Comfortable walking shoes",
                "Sun protection hat",
                "Light breathable cottons",
            ],
            "weather_advice": "Pleasant morning temperatures with moderate sunshine.",
        })


class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name or "gemini-1.5-flash"

    @property
    def provider_name(self) -> str:
        return "gemini"

    def generate(self, prompt: str, system_prompt: str, timeout_seconds: int = 15) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2,
            },
        }

        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                resp = client.post(url, json=payload)
                if resp.status_code != 200:
                    raise LLMProviderError(f"Gemini API returned HTTP {resp.status_code}: {resp.text[:200]}")
                data = resp.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    raise LLMProviderError("No response candidates returned by Gemini.")
                return candidates[0]["content"]["parts"][0]["text"]
        except httpx.RequestError as exc:
            raise LLMProviderError(f"Network error communicating with Gemini API: {exc}")


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name or "gpt-4o-mini"

    @property
    def provider_name(self) -> str:
        return "openai"

    def generate(self, prompt: str, system_prompt: str, timeout_seconds: int = 15) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code != 200:
                    raise LLMProviderError(f"OpenAI API returned HTTP {resp.status_code}: {resp.text[:200]}")
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except httpx.RequestError as exc:
            raise LLMProviderError(f"Network error communicating with OpenAI API: {exc}")


class GroqLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name or "llama-3.1-8b-instant"

    @property
    def provider_name(self) -> str:
        return "groq"

    def generate(self, prompt: str, system_prompt: str, timeout_seconds: int = 15) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code != 200:
                    raise LLMProviderError(f"Groq API returned HTTP {resp.status_code}: {resp.text[:200]}")
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except httpx.RequestError as exc:
            raise LLMProviderError(f"Network error communicating with Groq API: {exc}")


def get_llm_provider(settings: Optional[Settings] = None) -> BaseLLMProvider:
    """Factory creating appropriate LLM provider based on settings and available API keys."""
    cfg = settings or get_settings()
    provider_type = cfg.ai_provider.lower().strip()

    if provider_type == "gemini":
        key = cfg.gemini_api_key or cfg.ai_api_key
        if key:
            return GeminiLLMProvider(api_key=key, model_name=cfg.ai_model)
        logger.info("Gemini provider selected but no key configured; using mock provider.")
    elif provider_type == "openai":
        key = cfg.openai_api_key or cfg.ai_api_key
        if key:
            return OpenAILLMProvider(api_key=key, model_name=cfg.ai_model)
        logger.info("OpenAI provider selected but no key configured; using mock provider.")
    elif provider_type == "groq":
        key = cfg.groq_api_key or cfg.ai_api_key
        if key:
            return GroqLLMProvider(api_key=key, model_name=cfg.ai_model)
        logger.info("Groq provider selected but no key configured; using mock provider.")

    return MockLLMProvider()
