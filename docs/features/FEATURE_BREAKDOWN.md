# RoamGenie Feature Implementation Breakdown

**Project:** RoamGenie — AI Travel Planner & Budget Optimizer  
**Course:** Database Management Systems (Semester 5 Theory & Project)  
**Status:** Reconciled Feature Breakdown

---

## 1. Core Feature Capabilities

### 1.1 Authentication & User Profiles
* **Implementation:** `Argon2id` password hashing via `pwdlib`, stateless expiring JWT tokens via `PyJWT`, profile metadata stored in `users`, default preferences in `user_preferences`, and normalized activity tags in `activity_preferences`.
* **Frontend:** `AuthPage.jsx` (Login / Register modes with JWT persistence in localStorage) and `ProfilePage.jsx` (preferences form and activity tag pills).
* **Status:** `IMPLEMENTED`

### 1.2 Destination Catalogue & Exploration
* **Implementation:** 500 destinations, 6,000 accommodations, 6,000 restaurants, 2,517 attractions, and 6,000 transport options.
* **Frontend:** `DestinationsPage.jsx` with search bar, daily cost tags, and an interactive catalogue modal inspecting accommodations, dining, and sights.
* **Status:** `IMPLEMENTED`

### 1.3 Trip Planning Wizard & Parameter Validation
* **Implementation:** `TripCreateRequest` enforcing start/end dates, max duration 31 days, traveller count 1–50, positive total budget, and origin/destination validation in `trip_validator.py`.
* **Frontend:** `PlanPage.jsx` left column form with date pickers, budget number input, traveller count, preference tag cloud, and AI toggle.
* **Status:** `IMPLEMENTED`

### 1.4 Day-Wise Itinerary Scheduling
* **Implementation:** `DeterministicScheduler` assigns arrival transit, hotel check-ins, lunch, afternoon excursions, dinner, middle-day sightseeing, hotel check-outs, and return transit with exact cost calculations per traveller.
* **Frontend:** `PlanPage.jsx` day tabs ("Day 1", "Day 2", ...) and activity timeline event cards with start times, category pills, titles, notes, and costs.
* **Status:** `IMPLEMENTED`

### 1.5 Budget Calculation & Constraint Optimization
* **Implementation:**
  - `BudgetCalculator` aggregates lodging, dining, transit, sights, and other spending; computes remaining balance, percentage utilization, deficit amount, and spending driver warnings.
  - `BudgetOptimizer` performs iterative constraint reduction (swapping expensive hotels $\rightarrow$ transit $\rightarrow$ dining $\rightarrow$ attractions with cheaper catalogue options) until deficit is resolved or unavoidable deficit warnings are generated.
* **Frontend:** Visualizer card with total budget, estimated total, deficit/surplus banner, animated progress bar (green under budget / red deficit), and category breakdown pills.
* **Status:** `IMPLEMENTED`

### 1.6 Transactional Multi-Table Persistence
* **Implementation:** `TripService._execute_plan_generation()` atomically commits `itineraries`, `itinerary_days`, `itinerary_items`, `budget_allocations`, `packing_items`, and updates `trips` with versioning and rollback safety.
* **Status:** `IMPLEMENTED`

### 1.7 Saved Trips & History Dashboard
* **Implementation:** `saved_trips` associative table, `/trips/saved` endpoint, and bookmark toggling.
* **Frontend:** `TripsPage.jsx` displaying trip cards, planned dates, budgets vs estimated costs, bookmark filters, and delete actions.
* **Status:** `PARTIAL` (History displays correctly; reloading saved trip into `PlanPage` is being addressed in M3).

### 1.8 Climate Intelligence & Dynamic Packing
* **Implementation:** Open-Meteo live API integration, geocoding coordinates, WMO code interpretation, temperature/precipitation extraction, snapshot persistence in `weather_snapshots`, and rule-based packing checklist suggestions in `packing_items`.
* **Frontend:** Weather forecast widget in `PlanPage.jsx` and interactive packing checklist with checkboxes, custom item addition, and item deletion.
* **Status:** `IMPLEMENTED`

### 1.9 AI Assistant Copilot
* **Implementation:** Multi-provider adapter (`ai_providers.py`) supporting Gemini, OpenAI, Groq, and Mock. Bounded retry and schema validation in `ai_orchestrator.py`. Chat turns persisted in `ai_conversations` and `ai_messages`.
* **Frontend:** Slide-out AI Copilot drawer in `PlanPage.jsx` with chat history and quick suggestion prompt buttons.
* **Status:** `PARTIAL` (Chat prompt pipeline is being upgraded to full LLM dispatch in M5).

### 1.10 DBMS Academic Showcase & Live SQL Playground
* **Implementation:** 18 pre-built SQL benchmark queries covering all major DBMS concepts, interactive query runner measuring execution time in milliseconds, and PL/pgSQL audit trigger log viewer.
* **Frontend:** `ShowcasePage.jsx` with interactive query buttons, custom SQL editor, and live `trip_audit` JSON delta inspector.
* **Status:** `IMPLEMENTED`
