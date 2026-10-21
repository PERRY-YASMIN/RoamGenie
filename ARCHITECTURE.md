# System Architecture

> **Project:** RoamGenie — AI Travel Planner & Budget Optimizer  
> **Course:** Database Management Systems (Semester 5 Theory & Project)  
> **Architecture Style:** Decoupled 3-Tier Web Application with Autonomous Tool-Calling AI  
> **Authoritative Specification:** [docs/architecture/SYSTEM_ARCHITECTURE.md](docs/architecture/SYSTEM_ARCHITECTURE.md)

---

## 1. High-Level Architecture Topology

```mermaid
flowchart TD
  subgraph Frontend["Presentation Layer (React 19 + Vite)"]
    UI["Travel Copilot Drawer"]
    Card["Interactive Proposal Card (Diff Viewer + Financial Impact)"]
    Context["CopilotContext (State Dispatcher)"]
    UI --> Context
    Card -->|Explicit User Confirmation| Context
  end

  subgraph Backend["Application & Service Layer (FastAPI)"]
    Router["/api/v1/assistant/chat\n/api/v1/assistant/execute-proposal"]
    Orch["AIPlanOrchestrator\n(Multi-Turn Tool Execution Loop)"]
    Tools["Autonomous Chat Tools\n(chat_tools.py)"]
    TripSvc["TripService & BudgetCalculator"]
    
    Context -->|HTTP POST JSON| Router
    Router -->|User Message + Context| Orch
    Orch <-->|Function Calling (3 Turns)| Tools
    Router -->|Apply Changes (Execute)| TripSvc
  end

  subgraph AI["LLM Provider Gateway"]
    Gemini["Google Gemini API\n(Live Tool Calling)"]
    Mock["MockLLMProvider\n(Deterministic Fallback)"]
    Orch <--> Gemini
    Orch <--> Mock
  end

  subgraph DB["Relational Persistence Layer (PostgreSQL 15+)"]
    Tables[("23 Normalized Tables\ntrips, itineraries, budget_allocations")]
    Audit[("trip_audit Table\n(PL/pgSQL Trigger: trg_trip_audit)")]
    Tools -->|Read-Only Queries & In-Memory Simulation| Tables
    TripSvc -->|ACID Commit & Rollback on Error| Tables
    Tables -->|Trigger Execution| Audit
  end
```

---

## 2. Core Security & Decoupling Boundaries

1. **Zero Direct Client Database Access:** The React frontend communicates strictly with FastAPI over HTTP/JSON. No database connection strings, database passwords, or Supabase service-role keys are exposed to the client.
2. **Backend Authentication & IDOR Enforcement:** FastAPI manages password hashing, JWT creation/validation, and resource ownership enforcement (User A cannot view, query, or mutate User B's trips).
3. **Autonomous Read vs. Explicit Mutation Boundary:** The LLM is granted read-only autonomous database tools for querying history and simulating changes. The AI has zero direct database write permissions. All mutations require explicit, authenticated user confirmation.
4. **Deterministic Fallback & Error Recovery:** Bounded retries, structured error feedback, and deterministic catalog scheduling guarantee 100% functionality even during LLM provider rate limits or external network outages.

---

## 3. Grounded AI Tool Calling Architecture

The RoamGenie AI Copilot operates via a secure, state-aware tool-calling loop integrated directly into `AIPlanOrchestrator` and backed by `chat_tools.py`:

```
User Prompt ──> Assistant Router ──> Orchestrator Turn 1
                                             │
      ┌──────────────────────────────────────┴──────────────────────────────────────┐
      │ LLM Function Call:                                                          │
      │ 1. get_travel_history(user_id)           ──> Chronological trip summaries   │
      │ 2. get_itinerary_details(trip_id, user_id) ──> Full days & budget split       │
      │ 3. propose_itinerary_modification(...)   ──> In-memory change simulation    │
      └──────────────────────────────────────┬──────────────────────────────────────┘
                                             │ functionResponse payload
                                     Orchestrator Turn 2
                                             │
                                     Final Conversational Reply
                                     + proposed_changes JSON payload
                                             │
                                             ▼
                                     React Proposal Card
                                     (Diff Viewer & Financial Impact)
                                             │
                              [User Clicks "Apply Changes"]
                                             │
                                             ▼
                      POST /api/v1/assistant/execute-proposal
                      ├── IDOR Guard: trip.user_id == current_user.id
                      ├── ACID Mutation via TripService.swap_itinerary_item
                      ├── Category Budget Recalculation
                      └── Atomic db.commit() or db.rollback() on Error
```

### 3.1 Authenticated Read Operations (`get_travel_history` & `get_itinerary_details`)
* **`get_travel_history(db, user_id)`**: Queries trips strictly scoped to `Trip.user_id == current_user.id`, returning planned, ongoing, and completed journeys with destination cities and total budgets. User ID is injected by backend JWT dependencies, preventing cross-user data leaks.
* **`get_itinerary_details(db, user_id, trip_id)`**: Verifies trip ownership before fetching all `itinerary_days`, scheduled items, and `budget_allocations`. Returns the full schedule and current budget status (aligned vs. deficit).

### 3.2 In-Memory Simulation Without Mutation (`propose_itinerary_modification`)
* Simulates swapping a catalogue entity (e.g., higher-tariff hotel for a budget hotel, or fine dining for casual food) or removing an itinerary item.
* Uses `BudgetCalculator` to compute the simulated day schedules, new `estimated_total`, revised category allocations, and budget impact (`savings` vs. `deficit`).
* **Zero Mutation Guarantee:** Explicitly triggers a session `db.rollback()` at the conclusion of simulation to ensure no dirty objects or simulated items persist into PostgreSQL.
* Generates a structured proposal JSON containing `proposal_id`, `original_item`, `proposed_item`, `budget_impact`, and `requires_user_confirmation: true`.

### 3.3 Safe Database Execution Endpoint (`POST /api/v1/assistant/execute-proposal`)
* **Explicit Human-in-the-Loop:** Modifications are never written to the database until the user inspects the visual diff and clicks "Apply Changes" on the interactive Proposal Card.
* **IDOR Protection:** The route validates `trip.user_id == current_user.id` (with administrative override for `role == 'admin'`). Mismatched requests fail immediately with `HTTP 403 Forbidden`.
* **ACID Transaction & Rollback:** Mutations execute atomically via `TripService.swap_itinerary_item` or safe deletion. If any relational constraint or `IntegrityError` is violated, `db.rollback()` fires immediately and returns an `HTTP 400 Bad Request` with a user-friendly error description.
* **Audit Trail Integration:** Successful commits trigger the PL/pgSQL `trg_trip_audit` trigger, logging the before/after state delta into the `trip_audit` table.

---

## 4. Authoritative Architectural References

* **Complete System Architecture & Design:** [docs/architecture/SYSTEM_ARCHITECTURE.md](docs/architecture/SYSTEM_ARCHITECTURE.md)
* **Architecture Overview:** [docs/architecture/ARCHITECTURE_OVERVIEW.md](docs/architecture/ARCHITECTURE_OVERVIEW.md)
* **Relational Database Architecture:** [docs/database/DATABASE_ARCHITECTURE.md](docs/database/DATABASE_ARCHITECTURE.md)
* **22-Table Data Dictionary:** [docs/database/DATA_DICTIONARY.md](docs/database/DATA_DICTIONARY.md)
* **Architectural Decision Records:** [docs/decisions/ADR_INDEX.md](docs/decisions/ADR_INDEX.md)


---

## 5. Dual-Time-Zone & Immersive Scenic Architecture

### 5.1 Dual-Time-Zone Itinerary Engine
* **Dynamic Timezone Switching:** `DualTimeZoneSelector` detects origin and destination IANA time zones dynamically from trip parameters without hardcoded assumptions.
* **Deterministic Conversion:** All stored timestamps remain canonical in the database; conversions to Origin Time (e.g., IST UTC+05:30) or Destination Time (e.g., GST UTC+04:00) occur deterministically on the client with zero database mutation risk.
* **Date Shift Synchronization:** Automatically tags events crossing calendar days with `+1 Day` or `-1 Day` badges and synchronizes transfer and departure schedules.

### 5.2 Immersive Scenic Interface & Accessibility
* **Dual-Zone Scrim Architecture:** Section 1 (`.arrival-scene`) uses a subtle atmospheric vignette (~20% brighter) highlighting cinematic mountain landscape photography, while Section 2 (`.discovery-section`) activates an independent high-contrast dark scrim for trip planning workspace ergonomics.
* **Clean Typography:** Zero heavy bounding boxes or muddy text shadows; uses clean high-contrast lettering and responsive clamp typography.
* **Ambient Soundscape:** Built-in ambient audio synthesizer toggle (`🎧`) at the bottom-left corner with accessible screen-reader controls.
