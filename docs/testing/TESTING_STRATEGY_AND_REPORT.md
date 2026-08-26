# Testing Strategy, Pyramid & Verification Report

**Project:** RoamGenie — AI Travel Planner & Budget Optimizer  
**Course:** Database Management Systems (Semester 5 Theory & Project)  
**Status:** Reconciled Testing Baseline (172 Backend + 15 Frontend = 187 Total Tests)

---

## 1. Testing Pyramid & Layer Distribution

```
                  ┌────────────────────────┐
                  │    Integration Tests   │  End-to-End User Journeys
                  │     (pytest / E2E)     │  (Register -> Plan -> Save -> Swap -> Chat -> PG)
                  ├────────────────────────┤
                  │     Frontend Tests     │  Vitest Component Mounting, Toasts, Skeletons,
                  │  (Vitest + React Test) │  Session Expiry, Forms, API Mocks, Vite Build
                  ├────────────────────────┤
                  │     API / Auth Tests   │  FastAPI TestClient, JWT Auth,
                  │ (pytest + TestClient)  │  Validation, Error Envelopes, Swaps, AI Chat
                  ├────────────────────────┤
                  │    Database Integrity  │  PostgreSQL Foreign Keys,
                  │  (SQL + ORM Fixtures)  │  Cascades, Triggers, Views
                  ├────────────────────────┤
                  │       Unit Tests       │  Pydantic Models, Budget Math,
                  │   (pytest / Python)    │  Scheduler, Optimizer, AI Orchestrator
                  └────────────────────────┘
```

---

## 2. Test Suite Inventory & Results (172 Backend Tests)

| Test Module | Test File | Test Count | Focus Area | Status |
| :--- | :--- | :---: | :--- | :---: |
| **AI Orchestrator (M5)** | `backend/tests/test_ai_orchestrator.py` | 6 | Bounded retry, schema parsing, chat execution, deterministic fallback. | **PASS** |
| **AI Providers** | `backend/tests/test_ai_providers.py` | 6 | Gemini, OpenAI, Groq, Mock adapters, timeout handling. | **PASS** |
| **API & Guest Preview (M3)** | `backend/tests/test_api.py` | 6 | Health check, catalogue-grounded preview, zero-persistence guarantee, validation. | **PASS** |
| **Assistant & Copilot (M5)** | `backend/tests/test_assistant.py` | 10 | Contextual chat turns, multi-turn persistence, IDOR guards, budget & weather grounding, packing list CRUD. | **PASS** |
| **Authentication & Tokens (M2)** | `backend/tests/test_auth.py` | 16 | Argon2id hashing, JWT creation/decoding, expired/forged/malformed JWTs, profile prefs isolation. | **PASS** |
| **Budget Calculator** | `backend/tests/test_budget_calculator.py` | 4 | Category aggregations, deficits, remaining funds, utilization. | **PASS** |
| **Budget Optimizer** | `backend/tests/test_budget_optimizer.py` | 3 | Iterative catalogue swapping, deficit elimination, warnings. | **PASS** |
| **Catalogues** | `backend/tests/test_catalogues.py` | 10 | Destinations, hotels, dining, attractions, transport filters. | **PASS** |
| **Reports & SQL Security (M1)** | `backend/tests/test_reports.py` | 43 | Q01–Q18 queries, anonymous 401, traveller 403, admin 200, DDL/DML rejection, sensitive table protection. | **PASS** |
| **Scheduler** | `backend/tests/test_scheduler.py` | 4 | Deterministic day-wise scheduling, time allocation, pricing. | **PASS** |
| **Transport Dataset** | `backend/tests/test_transport_dataset.py` | 4 | D5 transport catalogue consistency, origin matching. | **PASS** |
| **Trip Validation** | `backend/tests/test_trip_validation.py` | 7 | Duration $\le 31$d, positive budget, traveller limits (1-50). | **PASS** |
| **Trip Lifecycle & Swap (M2–M4)** | `backend/tests/test_trips.py` | 23 | CRUD, saved trip reload, manual item swapping, IDOR protection, destination isolation, rollback safety. | **PASS** |
| **Weather Service** | `backend/tests/test_weather_service.py` | 5 | Open-Meteo geocoding, WMO mapping, snapshot persistence. | **PASS** |
| **Database Integrity** | `tests/backend/test_database_integrity.py`| 9 | Foreign key cascades, composite unique constraints. | **PASS** |
| **Mock AI Service** | `tests/ai/test_mock_service.py` | 1 | Fallback fixture conformance. | **PASS** |
| **Phase 1 Flow** | `tests/integration/test_phase1_database_flow.py` | 1 | Database session flow. | **PASS** |
| **Phase 2 Flow** | `tests/integration/test_phase2_trip_engine.py` | 3 | End-to-end trip engine persistence. | **PASS** |
| **Phase 3 Flow** | `tests/integration/test_phase3_ai_weather_flow.py` | 2 | AI and weather synergy flow. | **PASS** |
| **PostgreSQL Integration** | `tests/integration/test_supabase_postgres_flow.py` | 9 | Direct PostgreSQL multi-table transactions and pooling. | **PASS** |
| **TOTAL BACKEND** | — | **172** | Complete backend verification | **100% PASS** |

---

## 3. Frontend Test Suite (15 Vitest Tests)

| Test Module | Test File | Test Count | Focus Area | Status |
| :--- | :--- | :---: | :--- | :---: |
| **Toast System (M6)** | `frontend/src/context/ToastContext.test.jsx` | 3 | Toast types (success, error, warning, info), manual dismissal, auto-dismiss timers. | **PASS** |
| **API Client, Swap & Chat (M4/M5)** | `frontend/src/services/api.test.js` | 6 | REST client methods, error message extraction, swap payload dispatch, chatAssistant endpoint & IDOR handling. | **PASS** |
| **App, Routing & Session (M6)** | `frontend/src/App.test.jsx` | 6 | Shell rendering, navigation bar mounting, PlanPage new-trip mode, saved-trip query routing, 404 page, session expired toast. | **PASS** |
| **TOTAL FRONTEND** | — | **15** | Frontend unit & integration verification | **100% PASS** |

---

## 4. Test Execution Commands (PowerShell)

```powershell
# 1. Run full backend pytest suite (172 tests)
& .\backend\.venv\Scripts\python.exe -m pytest -v

# 2. Run frontend Vitest suite (15 tests)
cd frontend
npm test -- --run

# 3. Run frontend production build
npm run build

# 4. Unified verification runner
powershell -ExecutionPolicy Bypass -File scripts\test\all.ps1
```
