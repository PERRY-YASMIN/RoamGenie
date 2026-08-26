# RoamGenie — AI Features & Capabilities

This document details the Artificial Intelligence (AI) capabilities implemented in RoamGenie v1.0.0.

---

## 1. Implemented AI Feature Inventory

| Feature | Primary Component / Module | Description | Verified Status |
| :--- | :--- | :--- | :--- |
| **Personalized Itinerary Generation** | [`backend/app/services/ai_orchestrator.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/services/ai_orchestrator.py) | Generates structured, day-wise morning/afternoon/evening schedules adhering to user budget, pace, and destination catalogue facts. | **VERIFIED PASS** |
| **Budget Optimizer & Constraint Solver** | [`backend/app/services/budget_optimizer.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/services/budget_optimizer.py) | Computes category-specific allocations (Stay 40%, Dining 25%, Sights 20%, Transit 15%) and flags deficit violations. | **VERIFIED PASS** |
| **Weather Grounding & Adaptive Advice** | [`backend/app/services/weather_service.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/services/weather_service.py) | Fetches 5-day weather forecasts to ground activity scheduling and provide dynamic climate-aware tips. | **VERIFIED PASS** |
| **Smart Packing Checklist Generator** | [`backend/app/routers/assistant.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/routers/assistant.py) | Automatically generates categorized packing items (Clothing, Electronics, Documents, Essentials) based on destination climate. | **VERIFIED PASS** |
| **Bounded Travel Assistant (Chatbot Copilot)** | [`backend/app/routers/assistant.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/routers/assistant.py)<br>[`frontend/src/pages/PlanPage.jsx`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/frontend/src/pages/PlanPage.jsx) | Interactive chat drawer providing bounded conversational assistance grounded in trip facts, weather snapshots, and database records. | **VERIFIED PASS** |

---

## 2. Supported LLM Providers & Fallback Engine

RoamGenie supports multiple pluggable LLM backends configured via environment variables, paired with a deterministic offline heuristic engine:

1. **Google Gemini (Default / Recommended):** `gemini-1.5-flash` / `gemini-1.5-pro` via Google GenAI SDK.
2. **Groq Cloud:** `llama-3.1-70b-versatile` / `mixtral-8x7b-32768` for ultra-low latency generation.
3. **OpenAI:** `gpt-4o-mini` / `gpt-4o`.
4. **Deterministic Heuristic Engine (Offline Resilient):** When external API keys are omitted or network errors occur, RoamGenie falls back to an algorithmic scheduler (`Scheduler`) that pulls real hotel, attraction, and dining rows directly from PostgreSQL and constructs a valid multi-day itinerary in `< 50ms`.

---

## 3. Grounding & Anti-Hallucination Controls

To guarantee that RoamGenie does not hallucinate fictional hotels or impossible schedules:
- **Catalogue Pre-Injection:** Relevant destination records (top attractions, hotels in budget tier, restaurants) are queried from PostgreSQL and passed into the LLM system prompt as verified grounding facts.
- **Strict Schema Enforcement:** LLM outputs must conform to Pydantic models (`AIPlanResponse`). Invalid JSON is caught, logged, and resolved via the deterministic fallback engine.
- **IDOR Guarded Context:** The AI Chatbot only receives context for trips explicitly owned by the authenticated user.
