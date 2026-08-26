# RoamGenie — AI Orchestration Architecture

## 1. AI Layer Design

The AI architecture in RoamGenie decouples prompt construction, provider execution, validation, and database persistence into distinct modular components:

```
┌─────────────────────────────────────────────────────────────┐
│                    API Request Context                      │
│ (TripPlanRequest / AssistantChatRequest / PackingRequest)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     AIPlanOrchestrator                      │
│ - Fetches Grounding Entities (Hotels, Food, Sights from DB) │
│ - Fetches Climate Context (WeatherService)                  │
│ - Assembles Grounded System Prompts (ai_prompts.py)         │
└──────────────────────────────┬──────────────────────────────┘
                               │
         ┌─────────────────────┴─────────────────────┐
         ▼                                           ▼
┌─────────────────────────────┐             ┌────────────────────────┐
│     External AI Provider    │             │  Deterministic Engine  │
│  - Gemini / Groq / OpenAI   │             │ - Greedy Slotting      │
│  - Structured JSON Mode     │             │ - Real DB Entity Pull  │
└──────────────┬──────────────┘             └───────────┬────────────┘
               │ (On Success)                           │ (On Fallback)
               ▼                                        ▼
┌─────────────────────────────────────────────────────────────┐
│                Pydantic Validation & Coercion               │
│ - Validates Day Slotting (Day 1..N, Morning/Noon/Night)     │
│ - Validates Cost Categorization (Stay, Food, Sight, Transit)│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Budget Optimizer & Persistence                 │
│ - Calculates Total Estimated vs. Budget Envelopes           │
│ - Computes Deficit Alerts (`alert-deficit` vs `alert-ok`)   │
│ - Persists Itinerary, Days, Items, Allocations to PostgreSQL│
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Prompt Engineering & Grounding Architecture

Prompts reside in [`backend/app/services/ai_prompts.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/services/ai_prompts.py) and [`ai/prompts/itinerary_system.md`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/ai/prompts/itinerary_system.md).

### Grounding Rules Enforced:
1. **Fact-Bound Entity Usage:** The LLM is strictly instructed to schedule hotels, restaurants, and attractions provided in the grounding context payload.
2. **Cost Constraint Bounds:** Daily expenses must align with user budget tier ($Total Budget / Days$).
3. **Structured JSON Output:** Responses are constrained to valid JSON object schemas matching `AIPlanResponse`.
