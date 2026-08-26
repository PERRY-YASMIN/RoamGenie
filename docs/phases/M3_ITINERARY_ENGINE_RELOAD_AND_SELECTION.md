# M3 — Itinerary Engine & Trip Reload Remediation Phase

**Phase Identifier:** M3  
**Phase Name:** Itinerary Engine & Trip Reload  
**Target Milestone:** Core User Journey Completion (MVP Blocker Fix)  
**Remediation Status:** **VERIFIED & COMPLETED** (2026-08-26)  
**Prerequisites:** M1 (Database Integrity), M2 (Auth & Trip Lifecycle)  
**Execution Result:** 155/155 Backend Tests PASS · 6/6 Frontend Tests PASS · Zero Regressions  

---

## 1. Objective & Scope Summary

Resolve the primary MVP blocker: enable seamless reloading and inspection of saved trips in `PlanPage.jsx`, connect unauthenticated guest previews to real destination catalogue data via `DeterministicScheduler` and `BudgetOptimizer` without database persistence, and ensure complete end-to-end continuity between trip creation, generation, saving, and reopening.

---

## 2. Issues Remediated

### 1. [P0 — MVP Blocker] Saved Trip Reload in `PlanPage.jsx`
* **Root Cause:** `PlanPage.jsx` extracted `destinationId` from query parameters but completely ignored `tripId`, leaving the component in `status === "idle"` and showing an empty placeholder card when navigating from "My Trips".
* **Remediation:**
  1. Extracted `tripIdParam = queryParams.get("tripId")` in [`PlanPage.jsx`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/frontend/src/pages/PlanPage.jsx#L33-L140).
  2. Implemented dedicated hydration `useEffect` watching `[tripIdParam, isAuthenticated]`.
  3. Fetched the saved trip via `getTrip(id)` and hydrated form parameters (`destination_id`, `starting_location`, `start_date`, `end_date`, `traveller_count`, `total_budget`).
  4. Restored persisted `itineraries[0]` into `generatedPlan.itinerary`, mapped `budget_summary` category allocations, restored `packing_items`, loaded `weather` snapshot, and set `status = "success"`.
  5. **Data Integrity Rule:** Loading an existing trip strictly reads persisted database rows. It **never** re-triggers generation or database mutations.

### 2. [P1 — MVP Required] Catalogue-Grounded In-Memory Guest Preview
* **Root Cause:** `POST /api/v1/plans/preview` called `MockAIService`, returning synthetic strings like `"Explore Mysuru: day 1"` and fixed 35/20/20/15/10 budget splits.
* **Remediation:**
  1. Updated [`backend/app/schemas/itinerary.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/schemas/itinerary.py#L1-L25) to accept optional `destination_id`.
  2. Refactored `preview_plan` in [`backend/app/routers/plans.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/routers/plans.py#L21-L135) to resolve `Destination` from PostgreSQL and invoke `DeterministicScheduler`, `BudgetService`, and `BudgetOptimizer` in memory.
  3. Returns real catalogue hotels, attractions, dining spots, transit options, and calculated budget splits.
  4. **Zero-Persistence Guarantee:** Verified through automated tests that guest previews create **zero** rows in `trips`, `itineraries`, `itinerary_days`, `itinerary_items`, `budget_allocations`, `packing_items`, or `saved_trips`.

---

## 3. Files Modified

* [`frontend/src/pages/PlanPage.jsx`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/frontend/src/pages/PlanPage.jsx) (Added `tripIdParam` detection, saved trip hydration hook, weather/packing restore, catalogue preview shaping)
* [`backend/app/routers/plans.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/routers/plans.py) (Connected guest preview to `DeterministicScheduler` and `BudgetOptimizer`)
* [`backend/app/schemas/itinerary.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/schemas/itinerary.py) (Added optional `destination_id` to `TripPlanRequest`)
* [`backend/app/services/budget_optimizer.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/services/budget_optimizer.py) (Added `get_budget_optimizer` singleton provider)
* [`backend/tests/test_api.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/tests/test_api.py) (Added guest preview catalogue grounding and zero-persistence verification tests)
* [`backend/tests/test_trips.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/tests/test_trips.py) (Added saved trip reload structure and non-duplication tests)
* [`frontend/src/App.test.jsx`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/frontend/src/App.test.jsx) (Added PlanPage new-trip and saved-trip query routing tests)
* [`scripts/test/all.ps1`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/scripts/test/all.ps1) (Updated test count summary to 155 backend and 6 frontend tests)

---

## 4. Test Evidence Summary

| Test Module | Test File | Test Count | Focus Area | Status |
| :--- | :--- | :---: | :--- | :---: |
| **Guest Preview & API (M3)** | `backend/tests/test_api.py` | 6 | Catalogue grounding, zero-persistence row count checks, input validation. | **PASS (100%)** |
| **Trip Reload & Lifecycle (M3)** | `backend/tests/test_trips.py` | 15 | Saved trip hydration structure, non-duplication on reload, IDOR matrix, cascades. | **PASS (100%)** |
| **Authentication & Tokens (M2)** | `backend/tests/test_auth.py` | 16 | Registration, Argon2id, JWT lifecycle, expired/forged tokens, preferences. | **PASS (100%)** |
| **Reports & SQL Security (M1)** | `backend/tests/test_reports.py` | 43 | Q01–Q18 queries, anonymous 401, traveller 403, admin 200, sensitive table blocking. | **PASS (100%)** |
| **Complete Backend Pytest Suite** | `backend/tests/` + `tests/` | **155** | All backend, database integrity, scheduler, optimizer, integration tests. | **PASS (100%)** |
| **Frontend Vitest Suite** | `frontend/src/` | **6** | API client, navigation, and PlanPage query routing. | **PASS (100%)** |
| **Frontend Production Build** | `frontend/` | — | Vite client bundle build. | **PASS (Zero Errors)** |
