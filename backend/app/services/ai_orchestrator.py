import inspect
import json
import logging
import re
from datetime import date, time
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models.catalogue import Destination
from app.db.models.trip import Trip
from app.db.models.ai import AIMessage
from app.db.models.user import User
from app.schemas.ai_plan import AIItineraryOutput
from app.schemas.assistant import ClarificationRequest
from app.schemas.weather import DestinationWeatherResponse
from app.services.ai_prompts import (
    ASSISTANT_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    build_assistant_user_prompt,
    build_user_prompt,
)
from app.services.ai_providers import (
    BaseLLMProvider,
    LLMProviderError,
    answer_general_travel_query,
    get_llm_provider,
)
from app.services.chat_tools import CHAT_TOOL_DECLARATIONS, execute_chat_tool
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
    clarification_request: Optional[ClarificationRequest] = None


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
        current_user: Optional[User] = None,
        db: Optional[Session] = None,
        force_ai: bool = False,
    ) -> Tuple[str, List[str], str, Optional[Dict[str, Any]], Optional[ClarificationRequest]]:
        """
        Orchestrates grounded, autonomous assistant responses using the configured LLM provider adapter
        with multi-turn tool calling, bounded retry, schema validation, and deterministic grounded fallback.
        Returns: (reply_text, suggested_actions, provider_name, proposed_changes, clarification_request)
        """
        tools = CHAT_TOOL_DECLARATIONS if (db is not None and current_user is not None) else None
        proposed_changes: Optional[Dict[str, Any]] = None
        last_tool_error: Optional[str] = None

        user_prompt = build_assistant_user_prompt(
            user_message=user_message,
            trip=trip,
            weather=weather,
            conversation_history=conversation_history,
        )

        contents: List[Dict[str, Any]] = [
            {"role": "user", "parts": [{"text": user_prompt}]}
        ]

        try:
            # Check provider signature to support any custom mock providers gracefully
            sig = inspect.signature(self.provider.generate)

            # Multi-turn tool execution loop (up to 3 tool call iterations)
            for loop_step in range(3):
                logger.info(
                    f"AI Copilot turn {loop_step + 1} (Provider: {self.provider.provider_name})"
                )
                call_kwargs: Dict[str, Any] = {
                    "prompt": user_prompt,
                    "system_prompt": ASSISTANT_SYSTEM_PROMPT,
                    "timeout_seconds": self.settings.ai_timeout_seconds,
                }
                if "tools" in sig.parameters:
                    call_kwargs["tools"] = tools
                if "contents" in sig.parameters:
                    call_kwargs["contents"] = contents

                raw_response = self.provider.generate(**call_kwargs)

                # Check if LLM requested a tool execution
                func_call = getattr(raw_response, "function_call", None)
                if func_call and db is not None and current_user is not None:
                    tool_name = func_call.get("name")
                    tool_args = func_call.get("args") or {}

                    logger.info(f"AI requested tool execution: '{tool_name}' with args {tool_args}")

                    # Fallback trip_id to active trip context if omitted
                    if "trip_id" not in tool_args and trip:
                        tool_args["trip_id"] = trip.id

                    try:
                        tool_result = execute_chat_tool(
                            name=tool_name,
                            args=tool_args,
                            db=db,
                            user_id=current_user.id,
                        )
                    except Exception as tool_exc:
                        logger.warning(f"Exception during tool execution '{tool_name}': {tool_exc}")
                        tool_result = {
                            "error": f"Tool execution failed for '{tool_name}': {str(tool_exc)}. Please clarify your request or provide valid parameters."
                        }

                    if "error" in tool_result:
                        last_tool_error = tool_result["error"]

                    # Capture proposed modifications for frontend confirmation card
                    if tool_name == "propose_itinerary_modification" and "proposal_id" in tool_result:
                        proposed_changes = tool_result

                    # Append model turn and functionResponse turn to contents
                    contents.append({
                        "role": "model",
                        "parts": [{"functionCall": func_call}],
                    })
                    contents.append({
                        "role": "user",
                        "parts": [{
                            "functionResponse": {
                                "name": tool_name,
                                "response": tool_result,
                            }
                        }],
                    })
                    continue

                # Final synthesized textual response
                ai_chat = None
                try:
                    ai_chat = self._parse_and_validate_ai_chat_response(str(raw_response))
                except (json.JSONDecodeError, ValidationError, ValueError, Exception) as parse_err:
                    logger.warning(
                        f"Initial AI chat response was not valid JSON ({parse_err}). Attempting recovery retry."
                    )

                if ai_chat and ai_chat.reply and ai_chat.reply.strip():
                    return (
                        ai_chat.reply,
                        ai_chat.suggested_actions,
                        f"ai-{self.provider.provider_name}",
                        proposed_changes,
                        ai_chat.clarification_request,
                    )

                # Malformed JSON recovery: Retry loop (max 2 retries) with a stricter prompt reminder
                for retry_idx in range(1, 3):
                    logger.info(
                        f"Malformed JSON recovery retry {retry_idx}/2 (Provider: {self.provider.provider_name})"
                    )
                    stricter_prompt = (
                        "CRITICAL INSTRUCTION: Your previous response was not valid JSON matching our schema. "
                        "You MUST respond ONLY with a raw JSON object containing 'reply' and 'suggested_actions' keys. "
                        'Example: {"reply": "Your conversational response", "suggested_actions": ["Option 1", "Option 2"], "clarification_request": null}. '
                        "Do NOT include markdown formatting, backticks, or any conversational preamble outside the JSON."
                    )
                    contents.append({"role": "user", "parts": [{"text": stricter_prompt}]})
                    retry_kwargs = {
                        "prompt": stricter_prompt,
                        "system_prompt": ASSISTANT_SYSTEM_PROMPT,
                        "timeout_seconds": self.settings.ai_timeout_seconds,
                    }
                    if "contents" in sig.parameters:
                        retry_kwargs["contents"] = contents

                    try:
                        retry_resp = self.provider.generate(**retry_kwargs)
                        retry_chat = self._parse_and_validate_ai_chat_response(str(retry_resp))
                        if retry_chat and retry_chat.reply and retry_chat.reply.strip():
                            return (
                                retry_chat.reply,
                                retry_chat.suggested_actions,
                                f"ai-{self.provider.provider_name}",
                                proposed_changes,
                                retry_chat.clarification_request,
                            )
                    except Exception as retry_err:
                        logger.warning(f"Malformed JSON retry attempt {retry_idx} failed: {retry_err}")

                # After max 2 retries fail, return hardcoded error message fallback
                logger.error("Exhausted all retries for malformed AI chat response. Returning hardcoded fallback message.")
                return (
                    "I encountered an error parsing the travel plan details. Could you please rephrase your request?",
                    ["What is my remaining budget?", "What should I pack?", "Review my itinerary"],
                    "ai-fallback",
                    proposed_changes,
                    None,
                )
        except (LLMProviderError, ValidationError, json.JSONDecodeError, Exception) as exc:
            logger.warning(
                f"AI Copilot chat execution failed ({self.provider.provider_name}): {exc}"
            )
            if last_tool_error:
                apology_reply = (
                    f"I apologize, but I wasn't able to complete that modification: {last_tool_error} "
                    "Could you please clarify your request or specify which day or activity you would like to adjust?"
                )
                return apology_reply, ["Review my itinerary", "Show my trips", "What is my budget?"], "ai-fallback", proposed_changes, None

        # Fallback to grounded deterministic response
        logger.info("Using grounded deterministic assistant response.")
        fallback_reply, fallback_actions, fallback_clarification = self._generate_grounded_fallback_chat(
            user_message=user_message,
            trip=trip,
            weather=weather,
        )
        provider_label = "ai-fallback"
        return fallback_reply, fallback_actions, provider_label, proposed_changes, fallback_clarification

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
        if not isinstance(data, dict):
            raise ValueError("Parsed JSON must be an object/dict")
        return AIChatOutput.model_validate(data)

    def _generate_grounded_fallback_chat(
        self,
        user_message: str,
        trip: Optional[Trip] = None,
        weather: Optional[DestinationWeatherResponse] = None,
    ) -> Tuple[str, List[str], Optional[ClarificationRequest]]:
        dest_city = trip.destination.city if trip and trip.destination else None
        dest_prefix = f"For your trip to {dest_city}" if dest_city else "For your journey"
        clean_q = user_message.lower()

        clarification_request: Optional[ClarificationRequest] = None

        if any(c in clean_q for c in ("cancel", "clear", "delete", "remove all", "drop all")):
            m = re.search(r"day\s*(\d+)", clean_q)
            target_day_num = int(m.group(1)) if m else None

            if target_day_num is not None:
                reply = (
                    f"{dest_prefix}, I've reviewed your schedule for Day {target_day_num}. "
                    f"Would you like to clear all activities for Day {target_day_num} or rebalance with new options?"
                )
                actions = [f"Clear Day {target_day_num}", "Swap individual items", "Keep current plans"]
                clarification_request = ClarificationRequest(
                    question=f"How would you like to handle Day {target_day_num}?",
                    options=[f"Clear all activities on Day {target_day_num}", f"Swap an item on Day {target_day_num}", "Keep Day as is"],
                    allow_custom_input=True,
                )
                return reply, actions, clarification_request
            else:
                day_options = []
                if trip and trip.itineraries:
                    for itin in trip.itineraries:
                        for day in getattr(itin, "days", []):
                            d_str = f"Day {day.day_number}"
                            if getattr(day, "date", None):
                                d_str += f" - {day.date}"
                            day_options.append(d_str)
                if not day_options:
                    day_options = ["Day 1", "Day 2", "Day 3"]

                clarification_request = ClarificationRequest(
                    question="Which day's plans would you like to cancel?",
                    options=day_options,
                    allow_custom_input=True,
                )
                reply = (
                    f"{dest_prefix}, I can help you cancel those activities. "
                    f"Which specific day's plans would you like to clear?"
                )
                actions = ["Cancel Day 1", "Cancel Day 2", "Keep current plans"]
                return reply, actions, clarification_request

        if any(amb in clean_q for amb in ("change my plan", "change plans", "plans for tonight", "modify tonight", "change tonight", "change something", "change my schedule")):
            day_options: List[str] = []
            if trip and trip.itineraries:
                for itin in trip.itineraries:
                    for day in getattr(itin, "days", []):
                        d_str = f"Day {day.day_number}"
                        if getattr(day, "date", None):
                            d_str += f" - {day.date}"
                        day_options.append(d_str)
            if not day_options:
                day_options = ["Day 1 - Evening", "Day 2 - Evening", "Day 3 - Evening"]

            clarification_request = ClarificationRequest(
                question="Which night or day would you like to modify?",
                options=day_options,
                allow_custom_input=True,
            )
            reply = (
                f"{dest_prefix}, I'd love to help update your schedule! "
                f"Which specific day or evening would you like to adjust?"
            )
            actions = ["Keep current plans", "View Full Schedule", "Explore Cafes"]
            return reply, actions, clarification_request

        # Duration & Length Query ("how many day trip is this", "how many days", "how long", etc.)
        if any(d in clean_q for d in (
            "how many day", "how many days", "how many night", "how many nights",
            "how long", "duration", "trip length", "number of day", "number of days",
            "length of this trip", "length of my trip", "length of the trip", "total day", "total days",
            "day trip", "days trip", "days is this", "day is this", "days is my", "day is my",
            "how long is", "trip duration", "how long will", "how long do we"
        )) or re.search(r"how\s+many\s+days?", clean_q) or re.search(r"days?\s+(is|for|in|of)\s+(this|my|the)", clean_q):
            if trip and trip.start_date and trip.end_date:
                day_cnt = (trip.end_date - trip.start_date).days + 1
                reply = (
                    f"{dest_prefix} is a **{day_cnt}-day** journey, running from **{trip.start_date}** to **{trip.end_date}** "
                    f"for **{trip.traveller_count} traveller(s)**! 🎒\n\n"
                    f"Would you like me to walk you through Day 1's activities or review your budget allocations?"
                )
                actions = ["View Day 1 Schedule", "What is my budget?", "What should I pack?"]
            else:
                reply = f"{dest_prefix}, please select or connect a confirmed trip to see its exact duration, daily schedule, and timeline."
                actions = ["Plan Trip", "View My Trips", "What should I pack?"]
            return reply, actions, None

        # Dates & Timing Query
        if any(dt in clean_q for dt in ("when is my trip", "what are the dates", "dates of my trip", "start date", "end date", "departure date", "return date", "when do we leave", "when are we going", "travel dates", "when does it start")):
            if trip and trip.start_date and trip.end_date:
                day_cnt = (trip.end_date - trip.start_date).days + 1
                origin_txt = f", departing from **{trip.starting_location}**" if trip.starting_location else ""
                reply = (
                    f"{dest_prefix} is scheduled from **{trip.start_date}** to **{trip.end_date}** "
                    f"({day_cnt} days total){origin_txt}. Let me know if you would like to inspect the schedule or check the weather forecast!"
                )
                actions = ["Check Live Forecast", "View Day 1 Schedule", "What is my budget?"]
            else:
                reply = f"Please select a confirmed trip to view your departure and return travel dates."
                actions = ["View My Trips", "Plan Trip", "Explore Destinations"]
            return reply, actions, None

        # Travellers & Group Count Query
        if any(tc in clean_q for tc in ("how many people", "how many travellers", "who is travelling", "group size", "number of people", "traveller count", "who is coming", "travelers")):
            count = trip.traveller_count if trip else 1
            reply = (
                f"{dest_prefix} is planned for **{count} traveller(s)**. All estimated accommodation tariffs, dining allowances, "
                f"and entry tickets are calculated for this group size!"
            )
            actions = ["What is my budget?", "View Itinerary", "What should I pack?"]
            return reply, actions, None

        # Specific Day Schedule Query
        day_match = re.search(r"day\s*(\d+)", clean_q)
        if day_match and trip and trip.itineraries:
            target_d = int(day_match.group(1))
            matched_items = []
            for itin in trip.itineraries:
                for day in getattr(itin, "days", []):
                    if day.day_number == target_d:
                        matched_items = getattr(day, "items", [])
                        break
                if matched_items:
                    break
            if matched_items:
                items_bullets = "\n".join([f"- **{itm.title}** ({itm.category.title()}, ₹{itm.estimated_cost:,.2f})" for itm in matched_items])
                reply = (
                    f"Here is your lineup for **Day {target_d}** {dest_prefix.lower()}:\n\n"
                    f"{items_bullets}\n\n"
                    f"Would you like to swap any of these activities or check alternative dining spots?"
                )
                actions = [f"Clear Day {target_d}", "Swap an activity", "Check Weather Forecast"]
                return reply, actions, None

        # Hotel & Accommodation Query
        if any(h in clean_q for h in ("hotel", "stay", "accommodation", "resort", "lodging", "where am i staying", "where do we stay", "room")):
            hotel_info = ""
            if trip and trip.destination and trip.destination.hotels:
                names = ", ".join([f"{h.name} (₹{h.price_per_night}/n)" for h in trip.destination.hotels[:3]])
                hotel_info = f" Available catalogue accommodations include: {names}."
            reply = (
                f"{dest_prefix}, your itinerary includes comfortable accommodation tailored to your budget.{hotel_info} "
                f"You can use the ⇄ Swap button to switch to any alternative hotel in our catalogue!"
            )
            actions = ["Swap Hotel", "Review Budget Allocations", "View Schedule"]
            return reply, actions, None

        if "rain" in clean_q or "storm" in clean_q or "monsoon" in clean_q or "weather" in clean_q or "forecast" in clean_q:
            weather_desc = f" (Current forecast: {weather.current_summary})" if weather and weather.current_summary else ""
            reply = (
                f"{dest_prefix}{weather_desc}, if it rains, we recommend shifting to indoor attractions such as museums, "
                f"royal palace galleries, and indoor culinary experiences. Be sure to pack a compact umbrella, rain poncho, "
                f"and waterproof pouch for electronics. You can swap any open-air itinerary item using the ⇄ Swap button."
            )
            actions = ["Swap Itinerary Items", "Check Live Forecast", "View Packing Checklist"]
        elif "itinerary" in clean_q or "improve" in clean_q or "schedule" in clean_q or "timeline" in clean_q or "pacing" in clean_q:
            itin_info = ""
            if trip and trip.itineraries:
                itin = trip.itineraries[0]
                day_cnt = len(itin.days)
                items_cnt = sum(len(d.items) for d in itin.days)
                itin_info = f" Your current schedule spans {day_cnt} days with {items_cnt} scheduled activities."
            reply = (
                f"{dest_prefix},{itin_info} To improve your itinerary pacing, schedule high-energy outdoor sights during the cool "
                f"morning hours, reserved regional dining for midday, and scenic views or relaxed markets in the evening. "
                f"You can rebalance any day by clicking ⇄ Swap on individual items to select alternative activities or dining."
            )
            actions = ["Swap Itinerary Items", "View Budget Breakdown", "What should I pack?"]
        elif any(k in clean_q for k in ("know before", "things to know", "before travelling", "before traveling", "before visiting", "local culture", "local etiquette", "local customs", "visitor tips", "what to know")):
            desc = f" {trip.destination.description}." if trip and trip.destination and trip.destination.description else ""
            reply = (
                f"{dest_prefix}:{desc} Key things to know before travelling: carry a government photo ID, keep local currency "
                f"or UPI ready for regional vendors, pre-check opening hours for heritage sites, and dress modestly at religious monuments. "
                f"Check your packing checklist and local weather forecast before you head out."
            )
            actions = ["View Packing Checklist", "Check Weather Forecast", "Review Schedule"]
        elif any(k in clean_q for k in ("5-4-3-2-1", "capsule", "packing formula", "packing rule", "how to pack light", "packing tips")) or (
            ("pack" in clean_q or "wear" in clean_q or "clothes" in clean_q) and trip is None
        ):
            reply, actions = answer_general_travel_query(clean_q, dest_name=dest_city)
            return reply, actions, None
        elif "pack" in clean_q or "wear" in clean_q or "clothes" in clean_q:
            weather_desc = ""
            if weather and weather.current_summary:
                weather_desc = f" (Forecast: {weather.current_summary})"
            reply = (
                f"{dest_prefix}{weather_desc}, we recommend comfortable walking shoes, weather-appropriate breathable fabrics, "
                f"a power bank, and required ID/prescriptions. Check the packing checklist on your trip dashboard to manage and toggle your packed items."
            )
            actions = ["View Packing Checklist", "Check Live Forecast", "Review Schedule"]
        elif any(k in clean_q for k in (
            "add some more expense", "add more expense", "add some more expenses", "add more expenses",
            "more expense", "more expenses", "splurge", "upgrade", "treat ourselves", "treat myself",
            "luxury", "higher budget", "more spending", "spend more", "fine dining", "upscale",
            "fancier", "fancy hotel", "luxury hotel", "pamper", "splurge a bit", "splurge more",
            "add expense", "add expenses", "increase spending", "increase budget", "elevate"
        )):
            if trip:
                rem = trip.total_budget - trip.estimated_total
                deficit = max(Decimal("0.00"), trip.estimated_total - trip.total_budget)
                if rem > 0:
                    reply = (
                        f"I love the way you think! You currently have a comfortable surplus of **₹{rem:,.2f}** remaining in your budget {dest_prefix.lower()}, "
                        f"which gives us plenty of room to elevate your experience in style! 🥂✨\n\n"
                        f"**Here are my top high-value upgrade recommendations:**\n\n"
                        f"1. **Luxury Accommodation Upgrade:** Switch to a premier boutique resort or heritage suite for extra comfort, scenic views, and top-tier hospitality.\n"
                        f"2. **Fine Dining & Regional Royal Banquets:** Reserve signature chef's tasting dinners, royal regional thalis, or an atmospheric rooftop culinary experience.\n"
                        f"3. **Curated VIP & Private Tours:** Book a dedicated private heritage storyteller/guide or private chauffeured cab for effortless sightseeing and exclusive access.\n\n"
                        f"Would you like me to upgrade your hotel stay or swap in a fine-dining experience on one of your evenings?"
                    )
                    actions = ["Upgrade Hotel to Luxury", "Add Fine Dining Banquet", "Book Private Heritage Tour"]
                elif deficit > 0:
                    reply = (
                        f"We're currently tracking **₹{deficit:,.2f}** over your original budget, but if you want to treat yourselves to memorable upgrades, "
                        f"we can easily balance the books! 🌟\n\n"
                        f"We can swap a couple of high-cost daytime activities for scenic viewpoints or cultural strolls to unlock funds for an upgraded luxury stay "
                        f"or a celebratory fine-dining dinner. Which part of your trip would you like to elevate first?"
                    )
                    actions = ["Upgrade Hotel", "Add Fine Dining Banquet", "Rebalance Itinerary"]
                else:
                    reply = (
                        f"Ready to treat yourselves? {dest_prefix}, you can elevate your trip with "
                        f"boutique heritage stays, exclusive guided cultural tours, and memorable fine-dining banquets. "
                        f"Let me know which day you'd like to make extra special!"
                    )
                    actions = ["Upgrade Hotel", "Add Fine Dining Banquet", "Explore Premier Tours"]
            else:
                reply, actions = answer_general_travel_query(clean_q, dest_name=dest_city)
            return reply, actions, None
        elif "budget" in clean_q or "cost" in clean_q or "cheap" in clean_q or "deficit" in clean_q or "activities fit" in clean_q:
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
        elif "attraction" in clean_q or "sight" in clean_q or "visit" in clean_q or "places" in clean_q or "activity" in clean_q:
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
            if clean_q.strip() in ("hi", "hello", "hey", "greetings", "good morning", "good evening"):
                if trip and trip.destination:
                    trip_info = f" to {trip.destination.city}, {trip.destination.country} ({trip.traveller_count} travellers, ₹{trip.total_budget:,.2f} budget)"
                    reply = (
                        f"Hello! I am RoamGenie AI, your personalized travel assistant. I can help optimize your day-by-day itinerary{trip_info}, "
                        f"explain budget allocations, analyze weather forecasts, and suggest destination attractions and dining spots."
                    )
                else:
                    reply = (
                        "Hello! I am RoamGenie AI, your personal travel copilot. You can ask general travel questions, or connect a confirmed trip "
                        "to receive personalized recommendations grounded in your destination, itinerary pacing, and budget."
                    )
                actions = ["What should I pack?", "How is my budget?", "Recommend local sights"]
            else:
                reply, actions = answer_general_travel_query(clean_q, dest_name=dest_city)

        return reply, actions, None


_ai_orchestrator = AIPlanOrchestrator()


def get_ai_orchestrator() -> AIPlanOrchestrator:
    return _ai_orchestrator
