# M4 — Manual Catalogue Selection, Item Swap & Budget Re-optimization Phase

**Phase Identifier:** M4  
**Phase Name:** Manual Catalogue Selection, Item Swap & Budget Re-optimization  
**Target Milestone:** Interactive Constraint Customization & In-Place Swapping  
**Remediation Status:** **VERIFIED & COMPLETED** (2026-08-26)  
**Prerequisites:** M1 (Database Integrity), M2 (Auth & Trip Lifecycle), M3 (Itinerary Engine & Reload)  
**Execution Result:** 163/163 Backend Tests PASS · 8/8 Frontend Tests PASS · Zero Regressions  

---

## 1. Objective & Scope Summary

Transform the generated itinerary timeline from a static view-only display into an interactive management interface where users can manually swap hotels, restaurants, attractions, or transport options from the destination catalogue. Ensure that manual user selections enforce strict IDOR/ownership protection, category and destination compatibility, atomic budget recalculation, and seamless reload persistence without creating duplicate itinerary records.

---

## 2. Issues Remediated & Architectural Implementations

### 1. [P1 — MVP Required] Manual Catalogue Entity Swap Controls & Selection Modal
* **Root Cause:** Timeline cards in `PlanPage.jsx` were static read-only cards without controls to view or select alternative hotels, restaurants, sights, or transit options.
* **Remediation:**
  1. Added a `⇄ Swap` button on every scheduled timeline event card in [`PlanPage.jsx`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/frontend/src/pages/PlanPage.jsx#L830-L845).
  2. Implemented a dedicated Catalogue Swap Modal fetching real database options for the trip destination (`getHotels`, `getRestaurants`, `getAttractions`, `getTransportOptions`).
  3. Displays candidate metadata: pricing, star ratings, cuisines, transport modes, and entry fees.

### 2. [P0 — Security & Integrity] Validated Item Swap API & Atomic Budget Recalculation
* **Implementation:**
  1. Created `PATCH /api/v1/trips/{trip_id}/itinerary/items/{item_id}` in [`backend/app/routers/trips.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/routers/trips.py#L368-L390).
  2. Defined `ItineraryItemSwapRequest` schema in [`backend/app/schemas/trip.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/schemas/trip.py#L68-L76).
  3. Implemented `swap_itinerary_item` in [`backend/app/services/trip_service.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/services/trip_service.py#L510-L680) with:
     - **IDOR Protection:** `verify_trip_ownership(trip, user_id)` verifies parent trip ownership before modifying child items.
     - **Destination Isolation:** Enforces `entity.destination_id == trip.destination_id` (rejects cross-destination tampering with 400 Bad Request).
     - **Category Semantic Validation:** Rejects incompatible entity swaps (e.g. replacing a restaurant with a hotel).
     - **Non-Duplication Guarantee:** Updates `ItineraryItem` attributes in place without duplicating days, itineraries, or trips.
     - **Atomic Recalculation:** Re-aggregates category allocations across all days and updates `BudgetAllocation` and `Trip.estimated_total` rows in the same transaction.

---

## 3. Files Modified

* [`backend/app/schemas/trip.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/schemas/trip.py) (Added `ItineraryItemSwapRequest`)
* [`backend/app/routers/trips.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/routers/trips.py) (Added `PATCH /trips/{trip_id}/itinerary/items/{item_id}` endpoint)
* [`backend/app/services/trip_service.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/services/trip_service.py) (Implemented `swap_itinerary_item` method)
* [`frontend/src/services/api.js`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/frontend/src/services/api.js) (Added `swapItineraryItem` client function)
* [`frontend/src/pages/PlanPage.jsx`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/frontend/src/pages/PlanPage.jsx) (Added timeline swap button, swap modal, and budget state update)
* [`frontend/src/styles.css`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/frontend/src/styles.css) (Added `.swap-btn`, `.event-footer-row`, `.alt-select-btn` styles)
* [`backend/tests/test_trips.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/tests/test_trips.py) (Added 8 automated tests for item swapping, IDOR rejection, cross-destination rejection, budget updates, persistence, and rollback)
* [`frontend/src/services/api.test.js`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/frontend/src/services/api.test.js) (Added unit tests for `swapItineraryItem`)
* [`scripts/test/all.ps1`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/scripts/test/all.ps1) (Updated test summary banner to 163 backend and 8 frontend tests)

---

## 4. Test Evidence Summary

| Test Module | Test File | Test Count | Focus Area | Status |
| :--- | :--- | :---: | :--- | :---: |
| **Manual Swap & Lifecycle (M4)** | `backend/tests/test_trips.py` | 23 | Hotel/Dining/Attraction/Transport swaps, IDOR rejection, cross-destination rejection, category validation, persistence on reload, rollback on failure. | **PASS (100%)** |
| **Guest Preview & API (M3)** | `backend/tests/test_api.py` | 6 | Catalogue grounding, zero-persistence row count checks, input validation. | **PASS (100%)** |
| **Authentication & Tokens (M2)** | `backend/tests/test_auth.py` | 16 | Registration, Argon2id, JWT lifecycle, expired/forged tokens, preferences. | **PASS (100%)** |
| **Reports & SQL Security (M1)** | `backend/tests/test_reports.py` | 43 | Q01–Q18 queries, anonymous 401, traveller 403, admin 200, sensitive table blocking. | **PASS (100%)** |
| **Complete Backend Pytest Suite** | `backend/tests/` + `tests/` | **163** | All backend, database integrity, scheduler, optimizer, integration tests. | **PASS (100%)** |
| **Frontend Vitest Suite** | `frontend/src/` | **8** | API client methods, navigation, PlanPage routing, and item swap dispatch. | **PASS (100%)** |
| **Frontend Production Build** | `frontend/` | — | Vite client bundle build. | **PASS (Zero Errors)** |
