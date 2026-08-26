# Project Specification & Requirements

**Project:** RoamGenie — AI Travel Planner & Budget Optimizer  
**Course:** Database Management Systems (Semester 5 Theory & Project)  
**Execution Model:** Solo Developer  
**Target Release:** v1.0.0 (MVP Baseline)  
**Status:** Authoritative Specification (Reconciled Baseline)

---

## 1. Project Background & Theory

### 1.1 The Fragmented Travel Planning Problem
Traditional travel planning requires travellers to juggle disparate systems:
- Transit portals for schedules and fares.
- Hotel directories for accommodation tiers and nightly rates.
- Dining directories for food options and dietary needs.
- Sightseeing guides for ticket fees and visiting hours.
- Weather services for packing advice.
- Manual spreadsheets for tracking multi-category budgets.

This results in cognitive fatigue, unrealistic schedules, and frequent budget overruns.

### 1.2 The RoamGenie Solution
RoamGenie centralizes 21,000+ verified travel catalogue items across 500 destinations in a normalized PostgreSQL database. When a traveller specifies their trip constraints (origin, destination, dates, traveller count, total budget, preferences, and activity tags), RoamGenie:
1. Validates all constraints at the API gateway layer.
2. Synthesizes a structured, day-wise schedule with start times, transit arrival/departure legs, dining, and sightseeing.
3. Aggregates itemized category expenses (accommodation, food, transport, attractions, other).
4. Solves budget constraints iteratively via `BudgetOptimizer`, swapping expensive options with economical catalogue alternatives.
5. Emits clear budget deficit or surplus warnings.
6. Retrieves point-in-time weather forecasts and compiles dynamic packing checklists.
7. Commits the entire multi-day itinerary atomically across 6 relational tables to PostgreSQL.

---

## 2. System Scope & Boundaries

```
┌────────────────────────────────────────────────────────────────────────┐
│                          IN-SCOPE (MVP v1.0.0)                         │
├────────────────────────────────────────────────────────────────────────┤
│ • User Registration, Login & Stateless JWT Authentication              │
│ • User Travel Preferences & Multi-Valued Activity Tags                 │
│ • Normalized Travel Catalogue Exploration (500 Cities, Hotels, Dining) │
│ • Parameter Validation (Dates, Budget > 0, Travellers 1-50, Days <= 31)│
│ • Day-Wise Itinerary Generation Grounded in Database Catalogue         │
│ • Itemized Category Budget Calculation & Deficit Warning Engine        │
│ • Iterative Budget Optimization Swapping Catalogue Alternatives        │
│ • Multi-Table Transactional Itinerary Persistence to PostgreSQL        │
│ • Saved Trips Dashboard with Bookmark Toggling and Trip Reloading      │
│ • Bounded AI Gateway with JSON Schema Guardrails & Mock Fallback       │
│ • Weather Observation Snapshot Caching & Dynamic Packing Checklists    │
│ • 18 Analytical SQL Reports for DBMS Academic Evaluation               │
│ • PL/pgSQL Audit Triggers Tracking Row-Level Mutations on Trips       │
│ • Responsive React 18 User Interface (Mobile, Tablet, Desktop)         │
├────────────────────────────────────────────────────────────────────────┤
│                     EXPLICITLY OUT OF SCOPE (v1.0.0)                   │
├────────────────────────────────────────────────────────────────────────┤
│ × Real-time payment gateway processing (Stripe, Razorpay, etc.)        │
│ × Live booking reservations with airlines or third-party hotel APIs    │
│ × GPS turn-by-turn navigation or real-time transit telemetry           │
│ × Visa, passport, or legal immigration validation guarantees           │
│ × Autonomous AI agents with direct database read/write permissions     │
│ × Multi-region production Kubernetes cluster deployment                │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. DBMS Course Curriculum Mapping

| DBMS Curriculum Topic | Implementation Evidence in RoamGenie | Repository Artifact |
| :--- | :--- | :--- |
| **Relational Data Modeling** | 22 normalized relational tables with explicit PKs, FKs, Unique, and Check constraints. | `database/schema/001_schema.sql`, `backend/app/db/models/` |
| **Entity-Relationship Design** | Complete ER diagram with cardinalities (1:1, 1:N, M:N via associative entities). | `docs/database/ER_DIAGRAM.md`, `docs/database/DATABASE_ARCHITECTURE.md` |
| **Normalization Theory** | Formal mathematical proofs demonstrating schema conformance to 1NF, 2NF, 3NF, and BCNF. | `docs/database/NORMALIZATION.md`, `docs/database/DATABASE_ARCHITECTURE.md` |
| **Data Definition Language (DDL)** | Complete PostgreSQL table definitions, identity sequences, and cascade rules (`ON DELETE CASCADE`). | `database/schema/001_schema.sql` |
| **Data Manipulation (DML) & Seeds** | Master development seed datasets spanning 500 destinations and 21,000+ catalogue items. | `database/seeds/`, `scripts/database/` |
| **Complex SQL Queries** | 18 analytical queries demonstrating multi-table joins, subqueries, aggregations, window functions, and `EXISTS`. | `database/queries/001_reports.sql`, `backend/app/services/report_service.py` |
| **Database Views** | Parameter-free and summarized abstractions (`v_trip_budget_summary`, `v_destination_catalogue`). | `database/views/001_views.sql` |
| **Stored Functions & Procedures** | PL/pgSQL routines calculating remaining budget and transactionally updating trip totals. | `database/functions/`, `database/procedures/` |
| **Database Triggers** | `AFTER INSERT OR UPDATE OR DELETE` trigger on `trips` logging row-level JSONB deltas to `trip_audit`. | `database/triggers/001_audit_trip.sql` |
| **ACID Transactions** | Multi-table atomic persistence script saving itineraries, days, items, and allocations with rollback. | `backend/app/services/trip_service.py`, `database/transactions/001_save_itinerary.sql` |
| **Indexing & Optimization** | Composite B-Tree indexes on high-frequency query paths with `EXPLAIN ANALYZE` benchmarks. | `database/indexes/001_indexes.sql` |
| **Schema Evolution** | Version-controlled database migrations utilizing Alembic. | `backend/migrations/versions/001_initial_schema.py` |
| **Data Integrity & Security** | Argon2id password hashing, JWT authorization, parameterization preventing SQL injection, least-privilege access. | `backend/app/services/auth_service.py`, `docs/security/SECURITY_AUDIT_AND_CONTROLS.md` |
