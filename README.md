# RoamGenie — Autonomous Travel Planner & Relational Budget Optimization Engine

> "Where the mountains hold their breath. Find your way through a world of snow and sky."  
> **ROAMGENIE / 01** — An autonomous, relational travel planning and budget optimization engine with bounded generative AI.

---

## Executive Overview

RoamGenie is a full-stack, relational database-backed travel itinerary planner and budget optimization platform developed for the Semester 5 Database Management Systems (DBMS) curriculum.

Combining mathematically normalized relational engineering (3NF/BCNF PostgreSQL 15+) with structured, deterministic scheduling algorithms and a bounded multi-turn AI Travel Copilot, RoamGenie centralizes a master travel catalogue across 500 global destinations (6,000 accommodations, 6,000 restaurants, 2,517 attractions, and 6,000 transit options). The application accepts multi-dimensional traveller constraints and synthesizes day-by-day scheduled itineraries, dynamic budget allocations, real-time deficit warnings, live weather forecasts, dynamic packing checklists, interactive catalogue swapping, and synchronized dual-time-zone conversions.

---

## Core System Highlights

### 1. Atmospheric Arrival Experience & UI Theme
* **Cinematic Mountain Aesthetic:** High-resolution landscape photography of Kargil, Ladakh and Mount Fuji with tranquil particle effects.
* **Luminous Section 1 Hero:** Section 1 is styled ~20% brighter than the trip planning workspace, creating a serene, open aesthetic without heavy rectangular card boxes or text shadows.
* **Ambient Audio Soundscape:** Built-in ambient wind synthesizer and soundscape toggled from the bottom-left corner control.

### 2. Dual-Time-Zone Itinerary Engine
* **Dynamic Time-Zone Switching:** Instantly switch between **Origin Time** (e.g., IST, UTC+05:30) and **Destination Time** (e.g., GST, UTC+04:00) with dynamic location detection.
* **Calendar Synchronization & Date Shifts:** Automatically handles cross-midnight time conversions, dynamically tagging shifted events with `+1 Day` or `-1 Day` badges.
* **Transit & Arrival Alignment:** Synchronizes scheduled transfers, flight connections, check-ins, and daily activity cards without modifying stored database timestamps.

### 3. Autonomous Grounded AI Travel Copilot
* **Multi-Turn Tool Execution Loop:** Powered by Google Gemini (with fallbacks to OpenAI, Groq, and heuristic algorithms) via `AIPlanOrchestrator` and `chat_tools.py`.
* **Safe In-Memory Simulation:** The AI inspects travel history (`get_travel_history`) and simulates schedule swaps (`propose_itinerary_modification`) strictly in memory without unconfirmed database writes.
* **Interactive Visual Diff Cards:** Proposes changes via interactive React Diff Cards displaying exact itinerary additions, removals, and estimated financial impacts.
* **ACID-Compliant User Confirmation:** Changes persist only after explicit human approval via `/api/v1/assistant/execute-proposal`, enforcing strict IDOR protection (`trip.user_id == current_user.id`).

### 4. Master Travel Catalogue Explorer & Modals
* **Curated Global Dataset:** 21,133 verified catalogue records across 500 cities, with curated photography, price baselines, and direct Google Maps exploration links.
* **Deep Catalogue Modals:** Interactive modals for exploring attractions, hotels, dining, and transit options by destination with instant category filtering.
* **Zero-Insert Guest Preview:** Allows prospective travellers to preview full day-wise itineraries in-memory with a verified 0-database-insert guarantee.

### 5. Relational Budget Optimizer & Deficit Alerts
* **4-Category Expense Splits:** Itemizes expenses across Accommodation, Transport, Food, and Activities with dynamic progress bars.
* **Explicit Deficit Warning Panel:** Visually alerts travellers when estimated costs exceed budget with prominent alert banners and exact deficit amounts.
* **Deterministic Item Swapping:** Interactive modal to replace high-tariff items with budget alternatives, recalculating total trip costs atomically.

### 6. WCAG 2.2 AA Accessibility & Responsive Design
* **High-Contrast Input Surfaces:** Distinct, accessible input fields and persistent labels designed for effortless legibility over dark scenic gradients.
* **Keyboard Navigation & ARIA:** Full keyboard navigation support, visible focus rings, and explicit ARIA attributes across drawers, dialogs, and triggers.
* **Fluid Clamp Typography:** Responsive typography and layout constraints that remain stable across mobile (390px), tablet (768px), laptop (1280px), and ultrawide (1920px) viewports without clipping.

---

## Project Metadata & Verification Status

| Attribute | Specification | Verification Link |
| :--- | :--- | :--- |
| **Release** | v1.1.0 | [Release Notes](docs/release/RELEASE_NOTES.md) |
| **Status** | Production Ready (100% Release Verified) | [MVP Release Report](docs/release/MVP_RELEASE_REPORT.md) |
| **Backend Tests** | 203 / 203 PASS (100%) | [Test Results](docs/testing/TEST_RESULTS.md) |
| **Frontend Tests** | 51 / 51 PASS (100%, 9 Suites) | [Test Results](docs/testing/TEST_RESULTS.md) |
| **Database** | PostgreSQL 15+ (Supabase) \| 23 Tables \| 21,133 Records | [Database Design](docs/database/DATABASE_DESIGN.md) |
| **Accessibility** | WCAG 2.2 AA Compliant | [System Architecture](docs/architecture/SYSTEM_ARCHITECTURE.md) |
| **Course** | DBMS Semester 5 Theory & Laboratory (Solo Capstone) | [Problem Statement](docs/requirements/PROBLEM_STATEMENT.md) |

---

## Quick Evaluation Credentials

For rapid testing and academic evaluation, the database includes pre-seeded administrator and demo traveller accounts:

| Role | Email Address | Password | Permissions & Scope |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin@roamgenie.internal` | `AdminPass123!` | Full administrative access, SQL showcase, IDOR bypass, catalogue management. |
| **Demo Traveller 1** | `traveller@roamgenie.internal` | `TravellerPass123!` | Standard traveller (Arun Kumar): itineraries, bookings, chat, packing. |
| **Demo Traveller 2** | `ananya@roamgenie.internal` | `TravellerPass123!` | Standard traveller (Ananya Sharma): multi-user testing & collaboration. |

---

## System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER (React 19 + Vite)                 │
│  - Atmospheric Arrival Hero (20% Brighter Scenery, Ambient Audio)      │
│  - Dual-Time-Zone Selector & Date-Shift Timeline Engine                │
│  - Autonomous Travel Copilot Drawer with Interactive Proposal Cards    │
│  - Travel Catalogue Modals & WCAG 2.2 AA Accessible Planning Form      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / JSON REST API (Port 8000)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  APPLICATION SERVICE LAYER (FastAPI)                   │
│  - Pydantic v2 Request/Response Validation & Bcrypt JWT Auth           │
│  - AIPlanOrchestrator: Multi-Turn Function Calling Loop                │
│  - chat_tools.py: get_travel_history, get_itinerary_details            │
│  - Deterministic Day-Wise Scheduler & Budget Optimizer                │
│  - Open-Meteo Live Forecast Client & Snapshot Caching                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ psycopg3 Connection Pooling
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 RELATIONAL DATABASE LAYER (PostgreSQL 15+)             │
│  - 23 Normalized Tables (3NF/BCNF Schema, 21,133 Master Records)       │
│  - Composite B-Tree Indexes & Execution Plan Optimization              │
│  - PL/pgSQL Audit Triggers (trg_trip_audit -> trip_audit)              │
│  - Stored Procedures, Functions, and 10 Complex Analytical Views       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```text
RoamGenie/
├── backend/                       # FastAPI application & business logic
│   ├── app/
│   │   ├── config.py              # Centralized Pydantic application settings
│   │   ├── main.py                # FastAPI app factory, CORS, and router registration
│   │   ├── db/                    # SQLAlchemy 2.0 models, session management, base
│   │   ├── routers/               # assistant, auth, catalogues, health, plans, reports, trips, users
│   │   ├── schemas/               # Typed Pydantic v2 data contracts & validation
│   │   └── services/              # AI orchestrator, chat tools, budget optimizer, scheduler, weather
│   ├── tests/                     # 203 automated backend tests (Pytest)
│   ├── pyproject.toml             # Python package configuration
│   └── requirements.txt           # Python dependencies
├── frontend/                      # React 19 SPA client application
│   ├── public/                    # Static assets (cinematic mountain images, ambient soundscape)
│   ├── src/
│   │   ├── components/            # DualTimeZoneSelector, TravelCopilotDrawer, icons, toasts
│   │   ├── components/immersive/  # AmbientWorld, ImmersiveScene, environmentConfig
│   │   ├── context/               # AuthContext, CopilotContext, ToastContext
│   │   ├── pages/                 # HomePage, PlanPage, DestinationsPage, TripsPage, ShowcasePage, AuthPage
│   │   ├── services/api.js        # Centralized REST API client
│   │   ├── utils/                 # Timezone engine, destination image resolvers
│   │   └── styles.css             # Comprehensive design system, quiet luxury tokens, responsive layouts
│   ├── package.json               # Frontend dependencies & scripts
│   └── vite.config.js             # Vite configuration & Vitest test runner
├── database/                      # SQL scripts, schemas, and analytical queries
│   ├── schema/                    # 000_create_database.sql, 001_schema.sql (23 tables)
│   ├── seeds/                     # Master SQL and JSON seed manifests (D1 to D5 datasets)
│   ├── queries/                   # 10 complex analytical queries (Q01 to Q10)
│   ├── procedures/                # Stored procedures & refresh functions
│   └── triggers/                  # PL/pgSQL audit triggers
├── docs/                          # Comprehensive technical documentation suite
│   ├── architecture/              # System architecture, data flow, security architecture
│   ├── database/                  # ER diagrams, 3NF normalization proofs, schema definitions, dictionary
│   ├── api/                       # REST API endpoint specifications
│   ├── ai/                        # AI features inventory & grounding architecture
│   ├── testing/                   # Testing strategy, verified test results, regression reports
│   ├── datasets/                  # Catalogue dataset verification & row count proofs
│   ├── guides/                    # Developer guide, deployment guide, presentation & viva guide
│   └── release/                   # Release notes, MVP release report, known limitations
├── scripts/                       # Database seeding, verification, and backup scripts
├── tests/                         # Integration flows and database integrity test suites
├── RoamGenie_Milestones_1-5/      # Academic course submission deliverables (ER diagram, SRS, proofs)
├── ARCHITECTURE.md                # High-level architecture topology & security boundary overview
├── STARTUP_GUIDE.md               # Local development setup & Windows PowerShell instructions
└── README.md                      # Master project overview & feature showcase (This Document)
```

---

## Quickstart Guide

### Prerequisites
* **Python:** 3.12+ (Virtual environment recommended)
* **Node.js:** 18+ & **npm**
* **Database:** PostgreSQL 15+ (Local or Supabase)

---

### Step 1: Start the Backend (FastAPI)

In your first terminal:

```powershell
# Navigate to the backend directory
cd backend

# Activate virtual environment
.\.venv\Scripts\activate

# Install dependencies (if first time)
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

* API Docs (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

### Step 2: Start the Frontend (React + Vite)

In your second terminal:

```powershell
# Navigate to the frontend directory
cd frontend

# Install dependencies (if first time)
npm install

# Start Vite development server
npm run dev
```

* Web Application: [http://127.0.0.1:5173](http://127.0.0.1:5173)

---

## Running Automated Tests

Every layer of RoamGenie is covered by comprehensive automated tests:

```powershell
# 1. Run all Backend Pytest Suites (203 tests)
& "backend\.venv\Scripts\python.exe" -m pytest

# 2. Run all Frontend Vitest Suites (51 tests across 9 suites)
npm test --prefix frontend

# 3. Run Frontend Linter (0 errors)
npm run lint --prefix frontend

# 4. Run Frontend Production Build Gate
npm run build --prefix frontend
```

### Verified Test Summary:
* **Backend Pytest:** **203 / 203 PASS** (100%)
* **Frontend Vitest:** **51 / 51 PASS** (100%)
* **Total Automated Tests:** **254 / 254 PASS (100%)**

---

## Complete Documentation Index

| Domain | Document | Summary |
| :--- | :--- | :--- |
| **System Architecture** | [SYSTEM_ARCHITECTURE.md](docs/architecture/SYSTEM_ARCHITECTURE.md) | 3-tier decoupling, security perimeter, and AI loop |
| **Relational Schema** | [RELATIONAL_SCHEMA.md](docs/database/RELATIONAL_SCHEMA.md) | 23 normalized tables, data types, and foreign keys |
| **Data Dictionary** | [DATA_DICTIONARY.md](docs/database/DATA_DICTIONARY.md) | Attribute definitions, constraints, nullability, defaults |
| **Normalization Proofs** | [NORMALIZATION.md](docs/database/NORMALIZATION.md) | Formal mathematical proofs (1NF, 2NF, 3NF, BCNF) |
| **Database Features** | [DATABASE_FEATURES.md](docs/database/DATABASE_FEATURES.md) | Triggers, procedures, views, and 10 analytical queries |
| **AI Architecture** | [AI_ARCHITECTURE.md](docs/ai/AI_ARCHITECTURE.md) | Multi-provider orchestration, grounded prompting, tools |
| **API Specification** | [API_SPECIFICATION.md](docs/api/API_SPECIFICATION.md) | Endpoints, request schemas, and response envelopes |
| **Developer Reference** | [DEVELOPER_GUIDE.md](docs/guides/DEVELOPER_GUIDE.md) | Environment configuration, credentials, and CLI tools |
| **Presentation & Viva** | [PRESENTATION_AND_VIVA_GUIDE.md](docs/guides/PRESENTATION_AND_VIVA_GUIDE.md) | 15-slide presentation guide & 7-minute live demo script |

---

## Academic Credit & Course Context

* **Project Title:** RoamGenie — Autonomous Travel Planning & Relational Budget Optimization Engine
* **Course:** Database Management Systems (Semester 5 Theory & Laboratory)
* **Author / Developer:** Solo Developer Capstone Project
* **Core Philosophy:** Combining mathematically rigorous relational database normalization with deterministic budget algorithms and grounded generative AI.
