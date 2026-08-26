# Requirements Traceability Matrix

**Project:** RoamGenie — AI Travel Planner & Budget Optimizer  
**Course:** Database Management Systems (Semester 5 Theory & Project)  
**Baseline:** v1.0.0 Verified Functional & Non-Functional Specifications  
**Status:** **100% IMPLEMENTED & VERIFIED**

---

## 1. Functional Requirements Matrix

| Req ID | Requirement Description | API Endpoint(s) | Implementation Modules | Verification Evidence | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **FR-01** | User registration, login, logout, and token-authenticated profile access. | `POST /auth/register`<br>`POST /auth/login`<br>`GET /users/me` | `auth.py`, `auth_service.py`, `AuthContext.jsx` | `test_auth.py` (16 tests PASS) | **IMPLEMENTED** |
| **FR-02** | User travel preferences & normalized activity tags management. | `GET /users/me/preferences`<br>`PUT /users/me/preferences` | `users.py`, `auth_service.py`, `ProfilePage.jsx` | `test_auth.py` (PASS) | **IMPLEMENTED** |
| **FR-03** | Filtered and paginated browsing of destinations, hotels, dining, attractions, and transport. | `GET /destinations`<br>`GET /hotels`<br>`GET /restaurants`<br>`GET /attractions`<br>`GET /transport-options` | `catalogues.py`, `DestinationsPage.jsx` | `test_catalogues.py` (10 tests PASS) | **IMPLEMENTED** |
| **FR-04** | Trip CRUD lifecycle with user ownership isolation (IDOR protection). | `POST /trips`<br>`GET /trips`<br>`GET /trips/{id}`<br>`PATCH /trips/{id}`<br>`DELETE /trips/{id}` | `trips.py`, `trip_service.py`, `TripsPage.jsx` | `test_trips.py` (23 tests PASS) | **IMPLEMENTED** |
| **FR-05** | Strict trip parameter validation (`end_date >= start_date`, duration $\le 31$d, travellers 1-50, budget $> 0$). | `POST /trips`<br>`PATCH /trips/{id}` | `trip_validator.py`, `TripCreateRequest` | `test_trip_validation.py` (7 tests PASS) | **IMPLEMENTED** |
| **FR-06** | Day-wise itinerary generation grounded in verified catalogue data. | `POST /trips/{id}/generate` | `itinerary_scheduler.py`, `trip_service.py` | `test_scheduler.py` (4 tests PASS) | **IMPLEMENTED** |
| **FR-07** | Itemized category budget calculation (lodging, dining, transit, sights, other). | `POST /trips/{id}/generate` | `budget_service.py`, `PlanPage.jsx` | `test_budget_calculator.py` (4 tests PASS) | **IMPLEMENTED** |
| **FR-08** | Deficit detection and immediate warning triggers when `estimated_total > total_budget`. | `POST /trips/{id}/generate` | `budget_service.py`, `budget_optimizer.py` | `test_budget_optimizer.py` (3 tests PASS) | **IMPLEMENTED** |
| **FR-09** | Iterative budget optimization swapping expensive items with catalogue alternatives. | `POST /trips/{id}/generate` | `budget_optimizer.py` | `test_budget_optimizer.py` (3 tests PASS) | **IMPLEMENTED** |
| **FR-10** | Manual catalogue item swapping with atomic budget recalculation and rollback safety. | `PATCH /trips/{id}/itinerary/items/{item_id}` | `trips.py`, `trip_service.py`, `PlanPage.jsx` | `test_trips.py` (8 swap tests PASS) | **IMPLEMENTED** |
| **FR-11** | Multi-table transactional persistence committing itineraries, days, items, and allocations atomically. | `POST /trips/{id}/generate` | `trip_service.py` | `test_trips.py`, `test_database_integrity.py` | **IMPLEMENTED** |
| **FR-12** | Saved trip bookmarking and history list dashboard. | `POST /trips/{id}/save`<br>`GET /trips/saved` | `trips.py`, `trip_service.py`, `TripsPage.jsx` | `test_trips.py` (PASS) | **IMPLEMENTED** |
| **FR-13** | Saved trip inspection and complete itinerary reloading in planner wizard with zero row duplication. | `GET /trips/{id}` | `PlanPage.jsx`, `TripsPage.jsx` | `test_trips.py` (reload tests PASS) | **IMPLEMENTED** |
| **FR-14** | Catalogue-grounded in-memory guest preview with 0 database persistence. | `POST /plans/preview` | `plans.py`, `itinerary_scheduler.py` | `test_api.py` (6 tests PASS) | **IMPLEMENTED** |
| **FR-15** | Point-in-time weather forecast retrieval and snapshot caching. | `GET /trips/{id}/weather`<br>`GET /destinations/{id}/weather` | `weather_service.py`, `catalogues.py` | `test_weather_service.py` (5 tests PASS) | **IMPLEMENTED** |
| **FR-16** | Dynamic packing checklist with category tags, interactive add, toggle, and delete controls. | `GET /assistant/trips/{id}/packing`<br>`POST /assistant/trips/{id}/packing`<br>`PATCH /assistant/packing/{id}`<br>`DELETE /assistant/packing/{id}` | `assistant.py`, `PlanPage.jsx` | `test_assistant.py` (10 tests PASS) | **IMPLEMENTED** |
| **FR-17** | Contextually grounded AI travel copilot chat with multi-turn persistence and offline fallback. | `POST /assistant/chat` | `assistant.py`, `ai_orchestrator.py`, `ai_prompts.py` | `test_assistant.py`, `test_ai_orchestrator.py` (16 tests PASS) | **IMPLEMENTED** |
| **FR-18** | 18 analytical DBMS benchmark queries demonstrating syllabus concepts (joins, subqueries, aggregations, window functions). | `GET /reports/queries`<br>`GET /reports/queries/{id}` | `reports.py`, `report_service.py`, `ShowcasePage.jsx` | `test_reports.py` (43 tests PASS) | **IMPLEMENTED** |
| **FR-19** | PL/pgSQL row-level audit mutation tracking into `trip_audit` JSONB table. | `GET /reports/audit-logs` | `triggers/001_audit_trip.sql`, `reports.py` | `test_reports.py` (PASS) | **IMPLEMENTED** |
| **FR-20** | Read-only custom SQL editor secured with admin RBAC and sensitive table/credential blocking. | `POST /reports/execute-sql` | `reports.py`, `report_service.py` | `test_reports.py` (43 security tests PASS) | **IMPLEMENTED** |

---

## 2. Non-Functional Requirements Matrix

| Req ID | NFR Area | Specification | Implementation Evidence | Status |
| :--- | :--- | :--- | :--- | :---: |
| **NFR-01** | **Password Security** | Passwords must be hashed using Argon2id with unique salt. | `pwdlib` Argon2id hasher in `auth_service.py` | **VERIFIED** |
| **NFR-02** | **Session Management** | Stateless JWT bearer tokens with standard claims (`sub`, `exp`, `iat`) and configurable expiration. | `PyJWT` in `auth_service.py` (`access_token_expire_minutes = 30`) | **VERIFIED** |
| **NFR-03** | **Data Isolation & IDOR** | Strict resource ownership checks; cross-user IDOR attempts must be blocked with 403 Forbidden. | `verify_trip_ownership()` in `trip_validator.py` and `assistant.py` | **VERIFIED** |
| **NFR-04** | **Offline Resilience** | Complete functionality maintained when external AI/weather APIs are unreachable. | Deterministic catalogue scheduler fallback and Mock LLM provider | **VERIFIED** |
| **NFR-05** | **Relational Integrity** | Normalization to 3NF/BCNF; foreign keys with `ON DELETE CASCADE`; `CHECK` constraints on budgets/ratings/dates. | PostgreSQL DDL in `001_schema.sql` and SQLAlchemy models | **VERIFIED** |
| **NFR-06** | **SQL Injection Protection** | Block multi-statements, DDL/DML mutation keywords, and sensitive table access in custom SQL runner. | `report_service.py` AST/regex validation and admin role check | **VERIFIED** |
| **NFR-07** | **Frontend UX & Accessibility** | Non-blocking Toast notifications, loading skeletons, ARIA roles, and responsive layouts across 360px–1280px+. | `ToastContext.jsx`, `styles.css`, Vitest component suite | **VERIFIED** |
