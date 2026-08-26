# RoamGenie — AI Travel Planner & Budget Optimizer

[![Release](https://img.shields.io/badge/release-v1.0.0-blue.svg)](docs/release/RELEASE_NOTES.md)
[![Status](https://img.shields.io/badge/status-RELEASE%20READY-success.svg)](docs/release/MVP_RELEASE_REPORT.md)
[![Backend Tests](https://img.shields.io/badge/backend%20tests-147%2F147%20PASS-brightgreen.svg)](docs/testing/TEST_RESULTS.md)
[![Frontend Tests](https://img.shields.io/badge/frontend%20tests-15%2F15%20PASS-brightgreen.svg)](docs/testing/TEST_RESULTS.md)
[![Database](https://img.shields.io/badge/database-PostgreSQL%2015%2B%20%7C%2021%2C133%20rows-336791.svg)](docs/database/DATABASE_DESIGN.md)
[![Course](https://img.shields.io/badge/course-DBMS%20Semester%205-orange.svg)](docs/requirements/PROBLEM_STATEMENT.md)

RoamGenie is an intelligent, relational database-backed travel itinerary planner and budget optimization platform developed for the Semester 5 Database Management Systems (DBMS) curriculum. The application centralizes normalized travel catalogue data across 500 destinations (6,000 accommodations, 6,000 restaurants, 2,517 attractions, and 6,000 transport options), accepts multi-dimensional trip constraints, and generates structured day-wise itineraries with itemized budget allocations, deficit warnings, weather context, dynamic packing checklists, manual catalogue entity swapping, and multi-turn AI travel assistant chat.

---

## 1. Project Status — v1.0.0 (Release Ready)

* **MVP Release Status:** **RELEASE READY (v1.0.0)**
* **All 12 Academic Milestones Completed (100%):** [docs/milestones/MILESTONE_COMPLETION_STATUS.md](docs/milestones/MILESTONE_COMPLETION_STATUS.md)
* **Automated Tests:** **162 / 162 PASS (100%)** — 147 Backend Pytest + 15 Frontend Vitest
* **Master Database:** **21,133 rows** across 23 base tables in PostgreSQL (Supabase) with 0 FK orphans.
* **Master Documentation Index:** [docs/README.md](docs/README.md)
* **Final Release Report:** [docs/release/MVP_RELEASE_REPORT.md](docs/release/MVP_RELEASE_REPORT.md)
* **Developer & Admin Reference:** [docs/guides/DEVELOPER_GUIDE.md](docs/guides/DEVELOPER_GUIDE.md)

---

## 2. 👨‍💻 For Developers & Evaluators (Quick Credentials)

For rapid evaluation and testing, the database includes pre-seeded administrator and demo traveller accounts:

| Account Type | Email Address | Password | Role & Scope |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin@roamgenie.internal` | `AdminPass123!` | Full administrative access, SQL showcase, IDOR bypass, catalogue management. |
| **Demo Traveller 1** | `traveller@roamgenie.internal` | `TravellerPass123!` | Standard traveller (Arun Kumar): itineraries, bookings, chat, packing. |
| **Demo Traveller 2** | `ananya@roamgenie.internal` | `TravellerPass123!` | Standard traveller (Ananya Sharma): multi-user testing & collaboration. |

> **Complete Developer Reference:** See [docs/guides/DEVELOPER_GUIDE.md](docs/guides/DEVELOPER_GUIDE.md) for full environment variables, CLI commands, database scripts, and security conventions.

---

## 3. Problem Statement & Academic Scope

Planning multi-day leisure travel across unfamiliar destinations is fragmented, time-consuming, and prone to budget overruns. Travellers typically consult disjointed sources for hotels, restaurants, sightseeing spots, and transit options without unified cost tracking or schedule coherence. 

RoamGenie solves this by combining **3NF/BCNF relational database engineering** with **deterministic scheduling algorithms** and a **bounded AI Travel Copilot**:
1. **Normalized Catalogue:** Centralizes 21,133 entities across 500 destinations with transparent cost baselines.
2. **Deterministic Scheduling & Budgeting:** Schedules daily activities within time slots and calculates 4-category budget splits (stay, transit, food, sights) with real-time deficit alerts.
3. **Interactive Manual Swapping:** Allows travellers to customize scheduled items with catalogue alternatives while recalculating budgets atomically.
4. **Contextually Grounded AI Copilot:** Answers travel inquiries using strictly authorized trip, budget, forecast, and catalogue context with guaranteed offline fallback.

---

## 3. Core Implemented Capabilities

Every capability documented below is fully implemented and verified by automated tests:

* **Authentication & User Profiles:** Bcrypt password hashing, expiring JWT bearer tokens, user profile customization.
* **Master Travel Catalogue Explorer:** Filtered browsing of 500 cities, 6,000 hotels, 6,000 dining spots, 2,517 attractions, and 6,000 transit routes with curated landmark photography and direct Google Maps exploration links.
* **Autocomplete Destination Search:** Interactive Google-search-style autocomplete in trip planner filtering across 500 active destinations with keyword suggestions.
* **Deterministic Itinerary Engine:** Day-by-day scheduler allocating morning, afternoon, and evening slots based on user dates and traveller count.
* **Itemized Budget Visualizer & Deficit Solver:** Category expense breakdown with colored progress bars and deficit warnings when $\text{estimated\cost} > \text{total\budget}$.
* **Manual Catalogue Swap:** Modal interface to replace individual itinerary items with catalogue alternatives, recalculating budgets atomically.
* **Weather Forecasting:** Open-Meteo live forecast integration (summary, temperature, conditions) with snapshot caching.
* **Dynamic Packing Checklist:** Contextual travel checklist items with interactive add, toggle packed, and delete controls.
* **Grounded AI Travel Copilot (Chatbot):** Multi-turn assistant chat grounded in trip parameters, budget allocations, forecast data, and catalogue entities (Gemini, OpenAI, Groq, and offline heuristic fallback).
* **Multi-Table Relational Persistence:** Atomic transactional commits across `trips`, `itineraries`, `itinerary_days`, `itinerary_items`, and `budget_allocations`.
* **Saved Trip Reload:** Instant hydration of persisted trips from `/plan?tripId=X` without re-generation or duplicate database rows.
* **Catalogue-Grounded Guest Preview:** In-memory preview generation for unauthenticated visitors with a verified 0-database-insert guarantee.
* **DBMS Showcase (10 Analytical SQL Queries):** Live execution of 10 analytical SQL queries (Q01–Q10) featuring window functions, multi-table joins, subqueries, and aggregations.

---

## 4. System Architecture & Security Boundaries

```
[ React 19 + Vite SPA ] (Port 5173)
       │ HTTP / JSON REST API (Port 8000)
       ▼
[ FastAPI Application Gateway ]
   ├── Pydantic v2 Request/Response Validation
   ├── Bcrypt Hashing & JWT Bearer Authentication
   ├── Deterministic Day-Wise Itinerary Scheduler
   ├── Iterative Budget Optimizer & Deficit Solver
   ├── Manual Item Swap & Atomic Recalculation Engine
   ├── Grounded AI Travel Copilot & Orchestrator (Gemini / OpenAI / Groq / Heuristic)
   ├── Open-Meteo Weather Client & Snapshot Caching
   └── SQLAlchemy 2.0 Repositories
        │ psycopg (Connection Pooling)
        ▼
[ Supabase-Hosted PostgreSQL 15+ ]
   ├── 23 Normalized Relational Tables (3NF Schema)
   ├── Database Views, Stored Procs & Functions
   ├── PL/pgSQL Audit Trigger (trg_trip_audit -> trip_audit)
   └── Composite B-Tree Indexes & Execution Plans
```

### Security Boundaries
1. **Zero Client Database Exposure:** The React frontend communicates exclusively via FastAPI JSON endpoints. No database passwords or Supabase service-role keys are exposed.
2. **Resource Ownership & IDOR Protection:** Strict ownership checks ensure User A cannot view, modify, or delete User B's trips, itineraries, packing items, or AI chat threads.
3. **Parameterized Queries:** All database interactions are mediated via SQLAlchemy ORM and typed Pydantic models to prevent SQL injection.
4. **Bounded AI Prompts:** AI services receive sanitized, allow-listed catalogue context and return schema-validated JSON. The AI has zero direct database write permissions.

---

## 5. Technology Stack

* **Frontend:** React 19, Vite 8.2, React Router DOM v7, Vanilla CSS Tokens, Vitest 4.1, Testing Library.
* **Backend:** Python 3.12, FastAPI 0.110+, Pydantic v2, Pydantic Settings, Uvicorn, PyJWT, Passlib (Bcrypt).
* **Database & ORM:** PostgreSQL 15+ (Hosted on Supabase), SQLAlchemy 2.0, psycopg v3 (Connection Pooling), Alembic.
* **AI & External Services:** Google Gemini SDK, OpenAI API, Groq Cloud, Deterministic Heuristic Scheduler, Open-Meteo weather client.

---

## 6. Repository Layout

```text
RoamGenie/
├── backend/                       # FastAPI Application & Business Logic
│   ├── app/
│   │   ├── config.py              # Centralized Pydantic Settings
│   │   ├── main.py                # FastAPI App Factory & Middleware
│   │   ├── db/                    # SQLAlchemy Models & Session Factory
│   │   ├── routers/               # auth, catalogues, trips, assistant, reports, weather
│   │   ├── schemas/               # Pydantic v2 Contracts
│   │   └── services/              # AI Orchestrator, Budget, Scheduler, Weather, Auth
│   ├── tests/                     # 147 Unit & Integration Pytest Suite
│   └── pyproject.toml             # Python Dependencies
├── frontend/                      # React SPA Client Application
│   ├── src/
│   │   ├── components/            # UI Components & Immersive Backgrounds
│   │   ├── context/               # AuthContext, ToastContext
│   │   ├── pages/                 # Home, Plan, Destinations, Trips, Showcase, Profile, Auth
│   │   ├── services/api.js        # Centralized REST Client
│   │   ├── utils/                 # Landmark photo & Google Maps resolvers
│   │   └── styles.css             # High-Contrast Minimalist Design Tokens
│   ├── package.json               # Frontend Dependencies & Scripts
│   └── vite.config.js             # Vite Configuration & Vitest Runner
├── database/                      # SQL Scripts & Seeding Data
│   ├── schema/                    # DDL Schema Definitions
│   ├── seeds/                     # Master SQL & JSON Seed Manifests
│   ├── queries/                   # 10 Complex Analytical Queries (Q01–Q10)
│   ├── procedures/                # Stored Procedures & Functions
│   └── triggers/                  # Audit Triggers
├── docs/                          # Comprehensive Project Documentation
│   ├── requirements/              # Problem Statement, SRS, Traceability Matrix
│   ├── architecture/              # System Architecture, Data Flow, Security
│   ├── database/                  # ER Diagram, Database Design, Schema, Dictionary
│   ├── ai/                        # AI Features & Orchestration Architecture
│   ├── testing/                   # Testing Strategy, Test Results, Regression Report
│   ├── datasets/                  # Dataset Documentation & Verification Report
│   ├── milestones/                # Milestone Completion Status (12/12 Complete)
│   ├── release/                   # Release Notes, MVP Release Report, Limitations
│   └── presentation/              # 15-Slide Deck Outline & 7-Min Viva Guide
└── scripts/                       # Database Seeding & Verification Scripts
```

---

## 7. Quickstart & Installation

### Prerequisites
* Python 3.12+
* Node.js 18+ & npm
* PostgreSQL 15+ (Local or Supabase instance)

### 7.1 Backend Setup
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .

# Configure environment variables
copy .env.example .env

# Run FastAPI backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 7.2 Frontend Setup
```bash
cd frontend
npm install

# Run Vite development server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 8. Running Automated Tests

```bash
# Run Backend Pytest Suite (147 tests)
cd backend
pytest backend/tests/ -v

# Run Frontend Vitest Suite (15 tests)
cd frontend
npm test -- --run

# Run Production Frontend Build Gate
npm run build
```

---

## 9. Documentation Directory Index

| Section | Link | Description |
| :--- | :--- | :--- |
| **Requirements** | [docs/requirements/](docs/requirements/) | Problem Statement, SRS, Traceability Matrix |
| **Architecture** | [docs/architecture/](docs/architecture/) | System Architecture, Data Flow, Security Architecture |
| **Database** | [docs/database/](docs/database/) | ER Diagram, 3NF Design, Relational Schema, Data Dictionary, Features |
| **AI Features** | [docs/ai/](docs/ai/) | AI Features Inventory, AI Orchestrator & Grounding Architecture |
| **Testing** | [docs/testing/](docs/testing/) | Testing Strategy, Verified Results (162/162 PASS), Regression Report |
| **Datasets** | [docs/datasets/](docs/datasets/) | Master Dataset Documentation & 21,133-Row Verification Report |
| **Milestones** | [docs/milestones/](docs/milestones/) | Milestone Completion Status (12 / 12 Complete) |
| **Release** | [docs/release/](docs/release/) | Release Notes, MVP Release Report, Known Limitations |
| **Presentation** | [docs/presentation/](docs/presentation/) | 15-Slide Presentation Outline & 7-Min Live Demo Script |
