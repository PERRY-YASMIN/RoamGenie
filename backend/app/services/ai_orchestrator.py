import json
import logging
from datetime import date, time
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field, ValidationError

from app.config import get_settings
from app.db.models.catalogue import Destination
from app.db.models.trip import Trip
from app.db.models.ai import AIMessage
from app.schemas.ai_plan import AIItineraryOutput
from app.schemas.weather import DestinationWeatherResponse
from app.services.ai_prompts import (
    ASSISTANT_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    build_assistant_user_prompt,
    build_user_prompt,
)
from app.services.ai_providers import BaseLLMProvider, LLMProviderError, get_llm_provider
from app.services.itinerary_scheduler import (
    DeterministicScheduler,
    ScheduledDay,
    ScheduledItem,
    ScheduleResult,
)
from app.services.weather_service import generate_packing_tips

logger = logging.getLogger(__name__)


class AIChatOutput(BaseModel):
    reply: str
    suggested_actions: List[str] = Field(default_factory=list)



class AIPlanOrchestrator:
    """Orchestrates AI-driven travel planning with bounded retry and seamless deterministic fallback."""

    def __init__(self, provider: Optional[BaseLLMProvider] = None):
        self.settings = get_settings()
        self.provider = provider or get_llm_provider(self.settings)
        self.fallback_scheduler = DeterministicScheduler()

    def generate_plan(
        self,
        destination: Destination,
        start_date: date,
        end_date: date,
        traveller_count: int,
        starting_location: str,
        total_budget: Decimal,
        preferences: Optional[List[str]] = None,
        weather: Optional[DestinationWeatherResponse] = None,
        force_ai: bool = False,
    ) -> Tuple[ScheduleResult, bool, str, List[str], Optional[str], List[str]]:
        """
        Attempts AI itinerary generation with bounded retry.
        Returns: (ScheduleResult, is_ai_generated, provider_name, packing_items, weather_advice, warnings)
        """
        day_count = (end_date - start_date).days + 1
        weather_packing = generate_packing_tips(weather.forecasts if weather else [])
        weather_advice = weather.current_summary if weather else None

        # Check if provider is configured for live AI or if mock/forced
        is_live_ai_capable = self.provider.provider_name != "mock" or force_ai

        if is_live_ai_capable:
            user_prompt = build_user_prompt(
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                traveller_count=traveller_count,
                starting_location=starting_location,
                total_budget=total_budget,
                preferences=preferences,
                weather=weather,
            )

            # Bounded retry: up to 2 attempts max
            for attempt in range(1, 3):
                try:
                    logger.info(
                        f"Attempting AI plan generation (Provider: {self.provider.provider_name}, Attempt: {attempt})"
                    )
                    raw_response = self.provider.generate(
                        prompt=user_prompt,
                        system_prompt=SYSTEM_PROMPT,
                        timeout_seconds=self.settings.ai_timeout_seconds,
                    )
                    ai_output = self._parse_and_validate_ai_response(raw_response, day_count)

                    if ai_output:
                        # Convert AI output to internal ScheduleResult
                        schedule_res = self._convert_ai_output_to_schedule(
                            destination=destination,
                            start_date=start_date,
                            end_date=end_date,
                            traveller_count=traveller_count,
                            ai_output=ai_output,
                        )
                        combined_packs = list(
                            dict.fromkeys((ai_output.packing_items or []) + weather_packing)
                        )
                        return (
                            schedule_res,
                            True,
                            f"ai-{self.provider.provider_name}",
                            combined_packs,
                            ai_output.weather_advice or weather_advice,
                            ai_output.warnings,
                        )
                except (LLMProviderError, ValidationError, json.JSONDecodeError) as exc:
                    logger.warning(
                        f"AI generation attempt {attempt} failed ({self.provider.provider_name}): {exc}"
                    )
                    if attempt == 2:
                        break

        # Fallback to deterministic scheduler
        logger.info("Activating deterministic scheduler fallback.")
        fallback_schedule = self.fallback_scheduler.schedule(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            traveller_count=traveller_count,
            starting_location=starting_location,
            preferences=preferences,
        )

        warnings = [
            f"[AI Service Notice] Generated using deterministic catalogue scheduler (Provider: {self.provider.provider_name})."
        ]

        return (
            fallback_schedule,
            False,
            "engine-v2-fallback",
            weather_packing,
            weather_advice,
            warnings,
        )

    def _parse_and_validate_ai_response(
        self, raw_text: str, expected_day_count: int
    ) -> Optional[AIItineraryOutput]:
        """Parses and verifies JSON output matches strict Pydantic AI schema."""
        # Strip potential markdown fences if present
        clean_text = raw_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        data = json.loads(clean_text)
        validated = AIItineraryOutput.model_validate(data)

        # Validate day count matches exactly
        if len(validated.days) != expected_day_count:
            logger.warning(
                f"AI returned {len(validated.days)} days, expected {expected_day_count}. Rejecting."
            )
            return None

        return validated

    def _convert_ai_output_to_schedule(
        self,
        destination: Destination,
        start_date: date,
        end_date: date,
        traveller_count: int,
        ai_output: AIItineraryOutput,
    ) -> ScheduleResult:
        """Translates validated AI plan to engine ScheduleResult."""
        days: List[ScheduledDay] = []

        for ai_day in ai_output.days:
            items: List[ScheduledItem] = []
            for order_idx, item in enumerate(ai_day.items, start=1):
                # Parse time
                time_parts = [int(p) for p in item.time.split(":")]
                item_time = time(time_parts[0], time_parts[1]) if len(time_parts) == 2 else time(9, 0)

                items.append(
                    ScheduledItem(
                        item_order=order_idx,
                        start_time=item_time,
                        title=item.title,
                        category=item.category,
                        estimated_cost=item.estimated_cost.quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP
                        ),
                        notes=item.notes,
                    )
                )

            days.append(
                ScheduledDay(
                    day_number=ai_day.day_number,
                    itinerary_date=ai_day.date,
                    items=items,
                )
            )

        return ScheduleResult(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            day_count=len(days),
            traveller_count=traveller_count,
            selected_hotel=destination.hotels[0] if destination.hotels else None,
            selected_transport=destination.transport_options[0] if destination.transport_options else None,
            days=days,
            summary=ai_output.summary,
        )

    def chat(
        self,
        user_message: str,
        trip: Optional[Trip] = None,
        weather: Optional[DestinationWeatherResponse] = None,
        conversation_history: Optional[List[AIMessage]] = None,
        force_ai: bool = False,
    ) -> Tuple[str, List[str], str]:
        """
        Orchestrates grounded assistant responses using the configured LLM provider adapter
        with bounded retry, schema validation, and deterministic grounded fallback.
        Returns: (reply_text, suggested_actions, provider_name)
        """
        is_live_ai_capable = self.provider.provider_name != "mock" or force_ai

        if is_live_ai_capable:
            user_prompt = build_assistant_user_prompt(
                user_message=user_message,
                trip=trip,
                weather=weather,
                conversation_history=conversation_history,
            )

            for attempt in range(1, 3):
                try:
                    logger.info(
                        f"Attempting AI Copilot chat (Provider: {self.provider.provider_name}, Attempt: {attempt})"
                    )
                    raw_response = self.provider.generate(
                        prompt=user_prompt,
                        system_prompt=ASSISTANT_SYSTEM_PROMPT,
                        timeout_seconds=self.settings.ai_timeout_seconds,
                    )
                    ai_chat = self._parse_and_validate_ai_chat_response(raw_response)
                    if ai_chat and ai_chat.reply.strip():
                        return (
                            ai_chat.reply,
                            ai_chat.suggested_actions,
                            f"ai-{self.provider.provider_name}",
                        )
                except (LLMProviderError, ValidationError, json.JSONDecodeError, Exception) as exc:
                    logger.warning(
                        f"AI Copilot chat attempt {attempt} failed ({self.provider.provider_name}): {exc}"
                    )
                    if attempt == 2:
                        break

        # Fallback to grounded deterministic response
        logger.info("Using grounded deterministic assistant response.")
        fallback_reply, fallback_actions = self._generate_grounded_fallback_chat(
            user_message=user_message,
            trip=trip,
            weather=weather,
        )
        provider_label = "mock-ai-copilot" if self.provider.provider_name == "mock" else "ai-fallback"
        return fallback_reply, fallback_actions, provider_label

    def _parse_and_validate_ai_chat_response(self, raw_text: str) -> Optional[AIChatOutput]:
        clean_text = raw_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        data = json.loads(clean_text)
        return AIChatOutput.model_validate(data)

    def _generate_grounded_fallback_chat(
        self,
        user_message: str,
        trip: Optional[Trip] = None,
        weather: Optional[DestinationWeatherResponse] = None,
    ) -> Tuple[str, List[str]]:
        dest_city = trip.destination.city if trip and trip.destination else None
        dest_prefix = f"For your trip to {dest_city}" if dest_city else "For your journey"
        clean_q = user_message.lower()

        if "pack" in clean_q or "wear" in clean_q or "clothes" in clean_q:
            weather_desc = ""
            if weather and weather.current_summary:
                weather_desc = f" (Forecast: {weather.current_summary})"
            reply = (
                f"{dest_prefix}{weather_desc}, we recommend comfortable walking shoes, weather-appropriate breathable fabrics, "
                f"a power bank, and required ID/prescriptions. Check the packing checklist on your trip dashboard to manage and toggle your packed items."
            )
            actions = ["View Packing Checklist", "Check Live Forecast", "Review Schedule"]
        elif "budget" in clean_q or "cost" in clean_q or "cheap" in clean_q or "deficit" in clean_q:
            budget_info = ""
            if trip:
                rem = trip.total_budget - trip.estimated_total
                budget_info = f" (Total Budget: ₹{trip.total_budget:,.2f} · Estimated Total: ₹{trip.estimated_total:,.2f} · Remaining: ₹{rem:,.2f})"
            reply = (
                f"{dest_prefix}{budget_info}, you can optimize your costs by reviewing category allocations or swapping individual "
                f"hotels, restaurants, and attractions using the ⇄ Swap button in your itinerary timeline."
            )
            actions = ["View Budget Breakdown", "Swap Itinerary Items", "Explore Free Attractions"]
        elif "food" in clean_q or "restaurant" in clean_q or "dining" in clean_q or "eat" in clean_q:
            dining_info = ""
            if trip and trip.destination and trip.destination.restaurants:
                names = ", ".join([r.name for r in trip.destination.restaurants[:3]])
                dining_info = f" Recommended local venues include {names}."
            reply = (
                f"{dest_prefix}, explore authentic local cuisine and verified dining spots in your destination catalogue.{dining_info} "
                f"You can also swap any meal in your itinerary timeline directly."
            )
            actions = ["Browse Restaurants", "Swap Dining Event", "View Itinerary"]
        elif "attraction" in clean_q or "sight" in clean_q or "visit" in clean_q or "places" in clean_q:
            att_info = ""
            if trip and trip.destination and trip.destination.attractions:
                names = ", ".join([a.name for a in trip.destination.attractions[:3]])
                att_info = f" Popular attractions include {names}."
            reply = (
                f"{dest_prefix}, ensure you check out the top verified cultural sights and experiences.{att_info} "
                f"Use the ⇄ Swap tool on any activity to customize your day."
            )
            actions = ["Explore Attractions", "Swap Sightseeing", "Check Itinerary"]
        else:
            trip_info = ""
            if trip and trip.destination:
                trip_info = f" to {trip.destination.city}, {trip.destination.country} ({trip.traveller_count} travellers, ₹{trip.total_budget:,.2f} budget)"
            reply = (
                f"I am your RoamGenie AI Travel Copilot. I can help optimize your day-by-day itinerary{trip_info}, "
                f"explain budget allocations, analyze weather forecasts, and suggest destination attractions and dining spots."
            )
            actions = ["What should I pack?", "How is my budget?", "Recommend local sights"]

        return reply, actions


_ai_orchestrator = AIPlanOrchestrator()


def get_ai_orchestrator() -> AIPlanOrchestrator:
    return _ai_orchestrator

