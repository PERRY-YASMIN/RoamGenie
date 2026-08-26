# Requirements Specification

> **Project:** RoamGenie — AI Travel Planner & Budget Optimizer  
> **Course:** Database Management Systems (Semester 5 Theory & Project)  
> **Authoritative Specification:** [docs/requirements/PROJECT_SPECIFICATION.md](docs/requirements/PROJECT_SPECIFICATION.md)  
> **Requirements Matrix:** [docs/requirements/REQUIREMENTS_MATRIX.md](docs/requirements/REQUIREMENTS_MATRIX.md)

---

## 1. Functional Requirements Summary

* **FR-01 (Authentication & User Profile):** User registration, login, logout, and token-authenticated profile access (`/auth/register`, `/auth/login`, `/users/me`).
* **FR-02 (User Preferences):** Management of travel preferences (accommodation tier, food preferences, transport modes, travel style, activity preferences, special requirements).
* **FR-03 (Catalogue Exploration):** Filtered and paginated browsing of 500 destinations, 6,000 hotels, 6,000 restaurants, 2,517 attractions, and 6,000 transport routes.
* **FR-04 (Trip Management CRUD):** Create, read, update, list, and delete trip records (`POST/GET /trips`, `GET/PATCH/DELETE /trips/{id}`).
* **FR-05 (Trip Parameter Validation):** Strict validation ensuring `end_date >= start_date`, trip duration $\le 31$ days, positive traveller count (1-50), and positive budget ($>0$).
* **FR-06 (Day-Wise Itinerary Generation):** Generate structured day-by-day scheduled itinerary items with allocated start times and categories linked to approved catalogue entities.
* **FR-07 (Budget Calculation Engine):** Compute category-wise expense splits (accommodation, transport, food, activities, contingency) and total estimated trip costs.
* **FR-08 (Deficit Detection & Warnings):** Compare total budget against estimated expenses; trigger explicit warnings when `estimated_total > total_budget`.
* **FR-09 (Iterative Budget Optimization):** Deterministically swap expensive catalogue stays, transit, dining, and attractions with budget alternatives until deficit is resolved.
* **FR-10 (Transactional Itinerary Persistence):** Atomically commit generated itineraries, days, items, and allocations to PostgreSQL; allow users to bookmark and review saved trip history.
* **FR-11 (AI Assistant with Deterministic Fallback):** Generate contextual recommendations and packing checklists using structured JSON prompts with guaranteed fallback.
* **FR-12 (Weather Context):** Provide destination weather snapshots and packing adjustments via Open-Meteo with mock fallback.
* **FR-13 (Analytical SQL Reports):** Execute 18 dedicated SQL queries demonstrating joins, subqueries, aggregations, window functions, and `EXISTS` for DBMS course evaluation.
* **FR-14 (Auditable Mutation Tracking):** Record all insert, update, and delete mutations on `trips` into `trip_audit` via PL/pgSQL database triggers.

---

## 2. Master Requirements Specification Reference

For the complete requirements specification, acceptance criteria, and DBMS syllabus mapping, see [docs/requirements/PROJECT_SPECIFICATION.md](docs/requirements/PROJECT_SPECIFICATION.md).
