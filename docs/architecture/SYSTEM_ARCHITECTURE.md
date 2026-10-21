# RoamGenie — System Architecture

## 1. High-Level Architectural Overview

RoamGenie is architected as a modern, decoupled client-server web application adhering to clean architectural boundaries:

```
┌─────────────────────────────────────────────────────────────┐
│                 React SPA Client (Vite)                     │
│  - React 19, Context API, Lucide Icons, Custom Editorial CSS│
│  - Autocomplete Planner, Modal Inspector, Travel Copilot    │
│  - Interactive AI Proposal Cards (Diff Viewer & Impact)     │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / JSON REST API
┌──────────────────────────────▼──────────────────────────────┐
│                  FastAPI Backend Server                     │
│  - Python 3.12, Uvicorn, Pydantic v2 validation             │
│  - API Routers: auth, catalogues, trips, assistant, reports │
│  - Autonomous Tool Loop: get_travel_history, modify_proposal │
│  - Services: scheduler, budget_optimizer, weather, AI       │
└───────────────┬──────────────────────────────┬──────────────┘
                │ SQLAlchemy 2.0 ORM           │ HTTP Client
┌───────────────▼──────────────┐ ┌─────────────▼──────────────┐
│  PostgreSQL Database (Supabase)│ │   External Weather & LLM   │
│  - 23 Base Tables (3NF Schema) │ │ - Open-Meteo Weather API   │
│  - PL/pgSQL Audit Triggers   │ │ - Google Gemini / Groq API │
│  - 21,133 Production Rows    │ │ - Heuristic Fallback Engine│
└──────────────────────────────┘ └────────────────────────────┘
```

---

## 2. Component Layers

### 2.1 Presentation Layer (Frontend SPA)
- **Framework:** React 19 with Vite bundler.
- **Routing:** React Router v7 with browser history and authenticated route protection.
- **State Management:** React Context API (`AuthContext`, `CopilotContext`, `ToastContext`) for unified authentication, AI chat state, and notification states.
- **Visual Design:** High-contrast, minimalist editorial design system with zero text-shadows, responsive CSS grid layouts, and curated landmark photography.

### 2.2 Application & Service Layer (FastAPI Backend)
- **API Framework:** FastAPI with asynchronous endpoint routing and automatic OpenAPI documentation.
- **Validation & Serialization:** Pydantic v2 BaseModel schemas with strict data coercion and constraints.
- **Core Domain Services:**
  - `AIPlanOrchestrator`: Coordinates prompt assembly, multi-turn autonomous tool execution loops (Gemini/Groq/OpenAI), and deterministic heuristic fallback.
  - `ChatTools`: Autonomous, IDOR-protected database tools (`get_travel_history`, `get_itinerary_details`, `propose_itinerary_modification`) providing safe read access and in-memory change simulation.
  - `Scheduler`: Implements greedy/heuristic entity assignment across morning, afternoon, and evening slots based on destination catalogue data.
  - `BudgetCalculator & BudgetOptimizer`: Calculates category-level distributions and enforces deficit warnings.
  - `WeatherService`: Fetches live Open-Meteo forecasts and persists snapshots for offline resilience.
  - `AuthService`: Generates bcrypt password hashes and HMAC-SHA256 JWT tokens.

### 2.3 Persistence Layer (PostgreSQL Database)
- **Database Engine:** PostgreSQL 15+ (hosted on Supabase).
- **ORM / Driver:** SQLAlchemy 2.0 with `psycopg3` binary driver.
- **Schema Design:** 23 base tables fully normalized to 3NF, enforcing referential integrity, check constraints, default timestamps, and cascading deletes.
- **Dataset Size:** 21,133 verified rows spanning 500 destinations, 6,000 hotels, 6,000 restaurants, 6,000 transit options, and 2,517 attractions.
- **Audit Logging:** PL/pgSQL database triggers (`trg_trip_audit`) capture JSONB before/after deltas for every trip mutation into `trip_audit`.

---

## 3. Grounded Autonomous AI Copilot Architecture

The AI assistant operates via an autonomous tool-calling loop that connects the React drawer interface to the PostgreSQL database with strict authorization boundaries:

```
[ User Prompt ]
      │
      ▼
POST /api/v1/assistant/chat
      │
      ▼
AIPlanOrchestrator ──(Multi-Turn Tool Loop)──► chat_tools.py
      │                                             │
      │ ◄─── functionResponse (Data / Proposal) ───┘
      │
      ▼
AssistantChatResponse { reply, proposed_changes, suggested_actions }
      │
      ▼
[ React TravelCopilotDrawer ] ──► [ Interactive Proposal Card ]
                                  - Visual Diff (Original vs. Replacement)
                                  - Financial Gauge (Savings / Deficit)
                                  - Buttons: "Apply Changes" & "Reject"
                                         │
                                         ▼ (User Clicks "Apply Changes")
                          POST /api/v1/assistant/execute-proposal
                          ├── IDOR Guard: trip.user_id == current_user.id
                          ├── Atomic Mutation via TripService.swap_itinerary_item
                          ├── Recalculate Category Budget Allocations
                          └── Atomic db.commit() / Rollback on Error
```

### 3.1 Autonomous Query Tools
1. **`get_travel_history(db, user_id)`**: Chronologically summarizes all trips for the authenticated user ID.
2. **`get_itinerary_details(db, user_id, trip_id)`**: Retrieves day-by-day scheduled activities and itemized budget allocations after validating user ownership.

### 3.2 In-Memory Simulation Without Mutation
3. **`propose_itinerary_modification(...)`**: Simulates candidate replacements (hotels, dining, attractions, transport) purely in memory. Computes new estimated totals, savings, and deficits via `BudgetCalculator`. Triggers `db.rollback()` to guarantee zero database writes during simulation.

### 3.3 Safe Database Commits & ACID Compliance
- **Execution Route (`POST /api/v1/assistant/execute-proposal`)**: Requires explicit user action from the frontend UI.
- **IDOR Protection**: Strictly blocks unauthorized access (`trip.user_id != current_user.id` yields `403 Forbidden`).
- **Integrity Enforcement**: Catches `IntegrityError` and check constraint violations during commit, executes `db.rollback()`, and returns user-friendly `HTTP 400 Bad Request` responses.
