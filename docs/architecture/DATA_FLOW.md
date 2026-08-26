# RoamGenie — Data Flow Architecture

## 1. End-to-End Itinerary Generation Flow

```
[User Form Submit: City, Dates, Budget, Travellers, Pace]
                     │
                     ▼
             [FastAPI Router] -> Validates request via Pydantic TripPlanRequest
                     │
                     ▼
          [AIPlanOrchestrator]
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
[Query Catalogue Data]    [Fetch Weather Forecast]
(Hotels, Sights, Food)    (Open-Meteo Service)
         │                       │
         └───────────┬───────────┘
                     ▼
     [Assemble Grounded Prompt / Constraints]
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
[External LLM Engine]     [Deterministic Scheduler Fallback]
 (Gemini / Groq / OpenAI)  (In-Memory Heuristic Engine)
         │                       │
         └───────────┬───────────┘
                     ▼
        [Structured JSON Itinerary Plan]
                     │
                     ▼
        [BudgetOptimizer & Deficit Check]
                     │
                     ▼
       [Return JSON Response to Frontend]
                     │
                     ▼
   [Render Dynamic Schedule, Timeline & Budget Bars]
```

---

## 2. Trip Persistence & Hydration Flow

1. **Persistence (Save Trip):**
   - User clicks `Save Trip` or toggles bookmark.
   - Frontend issues `POST /api/v1/trips` or `POST /api/v1/trips/{id}/save`.
   - Backend opens SQLAlchemy database transaction:
     - Inserts record into `trips` table.
     - Inserts record into `itineraries` table.
     - Inserts day slots into `itinerary_days`.
     - Inserts individual activities into `itinerary_items`.
     - Inserts budget categories into `budget_allocations`.
     - Generates initial packing checklist in `packing_items`.
   - Transaction commits atomically (ACID compliance).

2. **Hydration (Load Trip):**
   - User opens trip URL with `tripId=...`.
   - Frontend issues `GET /api/v1/trips/{id}`.
   - Backend verifies IDOR permissions (ensuring `trip.user_id == current_user.id`).
   - Performs relational joins across `trips`, `destinations`, `itineraries`, `itinerary_days`, `itinerary_items`, and `budget_allocations`.
   - Returns consolidated response to frontend to populate form constraints and day-wise timeline.

---

## 3. AI Copilot Chat Conversation Flow

1. **User Query Input:** User enters message in chat drawer (e.g. *"What should I pack for rainy days in Kochi?"*).
2. **Backend Authentication & IDOR Guard:** Validates user token and trip association.
3. **Context Assembly:** Fetches recent conversation history (last 6 turns from `ai_messages`), trip parameters, destination profile, and weather snapshot from `weather_snapshots`.
4. **LLM Generation with Fallback:** Passes grounded context to AI provider or uses domain heuristics if offline.
5. **Message Logging:** Persists user message and assistant reply into `ai_messages` table under the active `ai_conversations` record.
6. **Frontend Update:** Appends message bubble and renders suggested action buttons.
