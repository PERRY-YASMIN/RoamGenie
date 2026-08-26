# RoamGenie — Regression Test Report

## 1. Regression Test Execution Context
- **Scope:** Full regression verification of all core user workflows across authentication, catalogue browsing, autocomplete selection, heuristic & AI itinerary generation, budget calculation, entity swapping, weather grounding, chat assistant copilot, trip persistence, bookmarks, and analytical reports.
- **Backend Test Framework:** `pytest 8.4.1`, `anyio 4.14.2`, `Python 3.12`
- **Frontend Test Framework:** `vitest 4.1.10`, `jsdom`, `@testing-library/react 16.3`
- **Environment:** Windows, PostgreSQL (Supabase), FastAPI, Vite

---

## 2. Regression Suite Results

| Test Category | Suite Count | Pass Count | Fail Count | Regression Status |
| :--- | :---: | :---: | :---: | :---: |
| **Authentication & RBAC** | 16 | 16 | 0 | **ZERO REGRESSIONS** |
| **Catalogue & Search** | 16 | 16 | 0 | **ZERO REGRESSIONS** |
| **Trip & Itinerary Scheduling** | 34 | 34 | 0 | **ZERO REGRESSIONS** |
| **Budget Optimizer & Allocations** | 7 | 7 | 0 | **ZERO REGRESSIONS** |
| **AI Orchestration & Providers** | 12 | 12 | 0 | **ZERO REGRESSIONS** |
| **Weather Grounding** | 5 | 5 | 0 | **ZERO REGRESSIONS** |
| **AI Travel Copilot & Packing** | 10 | 10 | 0 | **ZERO REGRESSIONS** |
| **DBMS Showcase Reports (Q01–Q10)**| 43 | 43 | 0 | **ZERO REGRESSIONS** |
| **Transport Dataset Coverage** | 4 | 4 | 0 | **ZERO REGRESSIONS** |
| **Frontend Shell & Context** | 15 | 15 | 0 | **ZERO REGRESSIONS** |
| **TOTAL** | **162** | **162** | **0** | **ALL TESTS PASS** |
