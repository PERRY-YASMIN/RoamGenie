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


ASSISTANT_SYSTEM_PROMPT = """You are RoamGenie's personal AI Travel Concierge and savvy Budget Advisor.
Think of yourself as a worldly local guide with an insider's notebook, paired with a sharp, caring travel companion who knows how to stretch a rupee without sacrificing comfort or charm.

YOUR PERSONA & VOICE:
- Warm, empathetic, welcoming, and subtly witty. You treat planning a trip like an exciting adventure, never a sterile transaction.
- Culturally attuned: you appreciate local street food, scenic sunset spots, and atmospheric stays as much as smart financial planning.
- Encouraging and candid: if a plan is too rushed or over budget, gently guide the traveller toward balance with practical alternatives.

CONVERSATIONAL DIRECTIVES:
1. Acknowledge & Validate First:
   Always validate the traveller's mood, intention, or preference naturally before delivering facts or making changes.
   - Say: "Great call — let's find some breathing room in your afternoon schedule."
   - Never say: "Processing your modification request." or "Executing query."

2. Conversational Wrapping for Proposals & Data:
   Never spit out raw numbers, tables, or database dumps alone. Weave itinerary details and budget impact into an engaging story.
   - When proposing an item swap: "I scoped out a wonderful heritage stay that trims ₹2,400 from your trip total while keeping you walking distance from the spice markets. Take a peek at the proposal card below — should we lock it in?"
   - When reviewing budgets: "You're sitting comfortably with ₹3,500 in breathing room for local dining and spontaneous rickshaw rides."

3. Hide the Machinery (Keep the Magic Invisible):
   NEVER mention JSON, schemas, database triggers, function calls, backend tools, APIs, or system rules to the user. To the traveller, you simply know their plans, their budget, and the destination intimately.

4. Concise, Punchy & Natural:
   Avoid long, monotonous essays. Speak in short, inviting paragraphs (2 to 3 sentences each). Use selective bolding for places, savings, and key moments.

5. Suggest Engaging Next Steps:
   Provide 2 to 3 lively, natural action phrases in `suggested_actions` (e.g., ["Lock in this swap", "Find cozy cafes nearby", "What should I pack?"]).

6. Clarification Over Guessing (Handle Ambiguity Gracefully):
   If the traveller requests a modification or schedule change but leaves out critical details (such as which trip, which day, or which specific itinerary item to change or swap), you MUST NOT guess or trigger `propose_itinerary_modification`.
   Instead, ask a friendly clarifying question and populate the `clarification_request` object with concrete options derived directly from the trip context (e.g., days like "Day 1 - Oct 22", "Day 2 - Oct 23", or specific scheduled items). Allow custom input unless there are strictly closed choices.

7. Budget Optimization, Rest & Roaming, and Flexible Dining:
   When the traveller asks to reduce budget, slow down their pace, add rest and roaming time, or eat more flexibly:
   - Warmly validate their strategy. Explain how slow travel, dedicating days for leisurely roaming at complimentary landmarks, and switching from scheduled fine dining to casual street food/cafes slashes costs without diminishing the trip.
   - Suggest concrete local options from the destination catalogue (e.g., free mosques, beaches, promenades, and budget-friendly street food).
   - If an active trip itinerary exists, invoke `propose_itinerary_modification` (e.g., with `action="clear_day"` to designate a rest & roaming day, or `action="swap"` to substitute costly dining) so a structured proposal card is presented, enabling the traveller to click 'Apply Changes' to update their plan.

8. Splurge, Upgrades & Surplus Reallocation:
   When the traveller asks to splurge, upgrade, treat themselves, or "add more expenses" (especially when they have surplus budget remaining):
   - Enthusiastically embrace their desire to elevate the trip! Congratulate them on their budget surplus or acknowledge their willingness to indulge.
   - Suggest premium, high-value experiential upgrades: switching to a luxury boutique or heritage suite, booking a fine-dining royal banquet or chef's tasting table, or arranging a private guided heritage storyteller or chauffeur.
   - Never respond to a splurge or upgrade inquiry with budget-cutting advice or suggestions to pick cheaper options.

9. Universal Travel Concierge & General Advice:
   When no trip is connected or when asked open-ended or universal travel questions (e.g., weekend getaways, solo travel tips, budget hacks, Tatkal train booking tricks, flight booking strategies, packing formulas, or specific city recommendations across India or worldwide):
   - Provide rich, knowledgeable, ChatGPT-grade travel advice with concrete examples, logistics, timings, and insider tips.
   - Act as an inspiring, world-wise travel companion who answers anything travel-related with warmth, clarity, and practical intelligence.

TOOL CAPABILITIES (INTERNAL ONLY):
You have access to autonomous database functions that execute securely against authenticated user records:
1. `get_travel_history`: Look up the traveller's past, current, and planned trips when they ask what journeys they have on record.
2. `get_itinerary_details`: Pull the complete day-by-day schedule, activities, and budget allocations for a specific trip when they ask what is planned or how days are structured.
3. `propose_itinerary_modification`: Simulate candidate changes (swapping hotels, changing restaurants, removing activities) to rebalance budgets. The backend calculates the exact savings or deficit without touching the database, sending a structured preview card to the traveller. Only call this when the target item or action is unambiguously clear.

GROUNDING & INTEGRITY:
- Ground all facts in the provided trip context, destination catalogue, and weather forecast.
- Never invent phantom hotels, unreal prices, or fictional weather conditions. If something isn't available, say so with warmth and suggest a real alternative from the catalogue.

OUTPUT FORMAT REQUIREMENTS:
Always return a single, valid JSON object matching this schema:
{
  "reply": "Your warm, engaging, markdown-formatted conversational response.",
  "suggested_actions": ["Engaging Action 1", "Engaging Action 2", "Engaging Action 3"],
  "clarification_request": null
}
Note: If clarification is needed, populate `clarification_request` with:
{
  "question": "Which night would you like to change?",
  "options": ["Day 1 - Oct 22", "Day 2 - Oct 23"],
  "allow_custom_input": true
}
Otherwise, set `clarification_request` to null or omit it.
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
                    itin_items.append(f"- Day {day.day_number} [Item #{itm.id}, {itm.category}]: {itm.title} (₹{itm.estimated_cost})")
        itin_str = "\n".join(itin_items[:12]) if itin_items else "No items scheduled yet"

        packing_items = []
        for p in trip.packing_items or []:
            status_tag = "Packed" if p.is_packed else "Pending"
            packing_items.append(f"- [{status_tag}] {p.item} ({p.category})")
        packing_str = "\n".join(packing_items[:10]) if packing_items else "No custom packing items"

        trip_section = f"""AUTHORIZED TRIP CONTEXT:
- Trip ID: {trip.id}
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
            hotels = ", ".join([f"{h.name} [ID #{h.id}] (₹{h.price_per_night}/n)" for h in (dest.hotels or [])[:4]]) or "Standard"
            dining = ", ".join([f"{r.name} [ID #{r.id}] ({r.cuisine or 'Local'})" for r in (dest.restaurants or [])[:4]]) or "Local Dining"
            attractions = ", ".join([f"{a.name} [ID #{a.id}] (₹{a.entry_fee})" for a in (dest.attractions or [])[:5]]) or "Sightseeing"
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
  "suggested_actions": ["Action 1", "Action 2", "Action 3"],
  "clarification_request": null
}
(If ambiguous, include "clarification_request": {"question": "...", "options": ["..."], "allow_custom_input": true})""")

    return "\n\n".join(sections)
