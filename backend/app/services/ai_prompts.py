from datetime import date
from decimal import Decimal
from typing import Any, List, Optional

from app.db.models.catalogue import Destination
from app.schemas.weather import DestinationWeatherResponse


SYSTEM_PROMPT = """You are RoamGenie's AI Travel Curator and Budget Optimizer.
Your role is to produce a structured, high-quality, day-wise travel itinerary and budget breakdown based strictly on the provided destination, travel dates, budget, traveller count, and available catalogue items.

CRITICAL CONSTRAINTS:
1. Return ONLY a valid JSON object matching the requested schema. No markdown backticks, no markdown text outside the JSON.
2. The number of days must EXACTLY match the trip date range.
3. Every day must have its exact date (YYYY-MM-DD) and day_number starting at 1.
4. Item categories must be strictly one of: "transportation", "accommodation", "food", "attractions".
5. All costs must be nonnegative numbers in INR (₹).
6. Prioritize real catalogue attractions, hotels, and dining places listed in the context.
7. Incorporate the provided weather forecast for realistic scheduling and appropriate packing advice.
8. If the budget is constrained, choose budget-friendly options and note warnings instead of fabricating impossible prices.
"""


def build_user_prompt(
    destination: Destination,
    start_date: date,
    end_date: date,
    traveller_count: int,
    starting_location: str,
    total_budget: Decimal,
    preferences: Optional[List[str]] = None,
    weather: Optional[DestinationWeatherResponse] = None,
) -> str:
    day_count = (end_date - start_date).days + 1
    prefs_str = ", ".join(preferences) if preferences else "general cultural exploration, sightseeing, local food"

    # Catalogue summary
    hotels_str = "\n".join(
        [f"- {h.name}: ₹{h.price_per_night}/night (Rating: {h.rating or 'N/A'})" for h in (destination.hotels or [])]
    ) or "None listed (use destination standard estimate)"

    dining_str = "\n".join(
        [f"- {r.name} ({r.cuisine or 'Local'}): ~₹{r.average_cost_per_person or 300}/person" for r in (destination.restaurants or [])]
    ) or "None listed"

    attractions_str = "\n".join(
        [f"- {a.name} ({a.category or 'Sightseeing'}): Fee ₹{a.entry_fee}" for a in (destination.attractions or [])]
    ) or "None listed"

    transport_str = "\n".join(
        [f"- {t.origin} -> {destination.city} ({t.mode}): ~₹{t.estimated_cost}" for t in (destination.transport_options or [])]
    ) or "Self-arranged"

    # Weather summary
    weather_str = "No live forecast available."
    if weather and weather.forecasts:
        lines = [f"Current: {weather.current_summary}"]
        for f in weather.forecasts:
            lines.append(f"- {f.date}: {f.condition}, {f.min_temp_c}°C - {f.max_temp_c}°C (Rain: {f.precipitation_probability}%)")
        weather_str = "\n".join(lines)

    prompt = f"""TRIP SPECIFICATION:
- Destination: {destination.city}, {destination.country} ({destination.description})
- Origin: {starting_location}
- Start Date: {start_date}
- End Date: {end_date} (Total {day_count} days)
- Travellers: {traveller_count}
- Total Budget: ₹{total_budget}
- Traveller Preferences: {prefs_str}

WEATHER FORECAST:
{weather_str}

AVAILABLE DESTINATION CATALOGUE:
Hotels:
{hotels_str}

Dining:
{dining_str}

Attractions:
{attractions_str}

Transit:
{transport_str}

JSON OUTPUT SCHEMA REQUIREMENTS:
{{
  "summary": "String summary of the customized itinerary",
  "days": [
    {{
      "day_number": 1,
      "date": "{start_date}",
      "items": [
        {{
          "time": "09:00",
          "title": "Item title",
          "category": "transportation | accommodation | food | attractions",
          "estimated_cost": 500.00,
          "notes": "Helpful visitor context"
        }}
      ]
    }}
  ],
  "budget_split": [
    {{"category": "accommodation", "amount": 0.00}},
    {{"category": "transportation", "amount": 0.00}},
    {{"category": "food", "amount": 0.00}},
    {{"category": "attractions", "amount": 0.00}}
  ],
  "warnings": ["Warning messages if over budget"],
  "packing_items": ["Packing suggestions considering weather"],
  "weather_advice": "Advice regarding temperature/rain"
}}
"""
    return prompt


ASSISTANT_SYSTEM_PROMPT = """You are RoamGenie's intelligent AI Travel Copilot and Budget Advisor.
Your role is to answer the traveller's questions with accurate, helpful, friendly, and grounded advice.

CRITICAL OPERATIONAL RULES:
1. Return ONLY a valid JSON object matching the requested schema:
   {
     "reply": "Your markdown-formatted response string",
     "suggested_actions": ["Short Action 1", "Short Action 2", "Short Action 3"]
   }
2. Ground all factual travel advice in the provided trip context, weather forecast, budget breakdown, and destination catalogue.
3. NEVER fabricate hotel names, prices, restaurant names, entry fees, or weather conditions that contradict the provided context.
4. Authoritative budget figures, itinerary schedules, and weather data are managed by the backend; explain them accurately without claiming to unilaterally modify them.
5. If the user asks what to pack, reference the provided weather conditions and existing checklist items.
6. If the user asks about budget, reference their total budget, estimated total, remaining budget/deficit, and category allocations.
7. Keep responses concise, well-structured, actionable, and formatted in clean markdown.
8. Suggest 2 to 3 relevant next actions for the traveller in `suggested_actions`.
"""


def build_assistant_user_prompt(
    user_message: str,
    trip: Optional[Any] = None,
    weather: Optional[DestinationWeatherResponse] = None,
    conversation_history: Optional[List[Any]] = None,
) -> str:
    sections = [f"USER QUERY: {user_message}"]

    if conversation_history:
        history_lines = []
        for msg in conversation_history[-5:]:
            role_label = "Traveller" if msg.role == "user" else "Copilot"
            history_lines.append(f"{role_label}: {msg.content}")
        sections.append("RECENT CONVERSATION HISTORY:\n" + "\n".join(history_lines))

    if trip:
        dest_name = f"{trip.destination.city}, {trip.destination.country}" if trip.destination else "Selected Destination"
        dest_desc = trip.destination.description if trip.destination else ""
        day_count = (trip.end_date - trip.start_date).days + 1 if trip.start_date and trip.end_date else 1
        rem_budget = trip.total_budget - trip.estimated_total
        deficit = max(Decimal("0.00"), trip.estimated_total - trip.total_budget)

        allocs = []
        for alloc in trip.budget_allocations or []:
            allocs.append(f"- {alloc.category.title()}: ₹{alloc.amount}")
        alloc_str = "\n".join(allocs) if allocs else "No itemized allocations"

        itin_items = []
        for itin in trip.itineraries or []:
            for day in itin.days:
                for itm in day.items:
                    itin_items.append(f"- Day {day.day_number} [{itm.category}]: {itm.title} (₹{itm.estimated_cost})")
        itin_str = "\n".join(itin_items[:12]) if itin_items else "No items scheduled yet"

        packing_items = []
        for p in trip.packing_items or []:
            status_tag = "Packed" if p.is_packed else "Pending"
            packing_items.append(f"- [{status_tag}] {p.item} ({p.category})")
        packing_str = "\n".join(packing_items[:10]) if packing_items else "No custom packing items"

        trip_section = f"""AUTHORIZED TRIP CONTEXT:
- Destination: {dest_name} ({dest_desc})
- Origin: {trip.starting_location}
- Dates: {trip.start_date} to {trip.end_date} ({day_count} days)
- Travellers: {trip.traveller_count}
- Total Budget: ₹{trip.total_budget}
- Estimated Total: ₹{trip.estimated_total}
- Remaining Budget: ₹{rem_budget} (Deficit: ₹{deficit})
- Budget Allocations:
{alloc_str}
- Scheduled Itinerary Preview:
{itin_str}
- Current Packing Checklist:
{packing_str}"""
        sections.append(trip_section)

        if trip.destination:
            dest = trip.destination
            hotels = ", ".join([f"{h.name} (₹{h.price_per_night}/n)" for h in (dest.hotels or [])[:4]]) or "Standard"
            dining = ", ".join([f"{r.name} ({r.cuisine or 'Local'})" for r in (dest.restaurants or [])[:4]]) or "Local Dining"
            attractions = ", ".join([f"{a.name} (₹{a.entry_fee})" for a in (dest.attractions or [])[:5]]) or "Sightseeing"
            cat_section = f"""DESTINATION CATALOGUE FACTS ({dest.city}):
- Hotels: {hotels}
- Dining: {dining}
- Attractions: {attractions}"""
            sections.append(cat_section)

    if weather and weather.forecasts:
        lines = [f"Current: {weather.current_summary}"]
        for f in weather.forecasts[:5]:
            lines.append(f"- {f.date}: {f.condition}, {f.min_temp_c}°C to {f.max_temp_c}°C (Rain prob: {f.precipitation_probability}%)")
        sections.append("WEATHER FORECAST CONTEXT:\n" + "\n".join(lines))

    sections.append("""JSON OUTPUT FORMAT:
{
  "reply": "Clear, grounded, helpful advice answering the user query.",
  "suggested_actions": ["Action 1", "Action 2", "Action 3"]
}""")

    return "\n\n".join(sections)

