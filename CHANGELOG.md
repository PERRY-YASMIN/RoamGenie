# Changelog

All notable changes to the RoamGenie project are documented in this file.

---

## [1.0.0] — 2026-08-26

### Final MVP Verification & Release (M1–M7 Complete)
* **Release Status:** **RELEASE READY (100% Verified MVP)**
* **All 12 Release Gates Passed:** Backend Pytest (172/172), Frontend Vitest (15/15), Vite Production Build, Authentication/Security, IDOR Authorization, Database Integrity, Guest Preview Zero-Persistence, Manual Catalogue Swap, AI Context Grounding, Frontend UX/Accessibility, Configuration Audit, and End-to-End Demo Journey.

### Added
* **Manual Catalogue Swap:** Interactive timeline item replacement modal allowing users to swap scheduled accommodations, dining, sightseeing, or transit options with verified destination catalogue alternatives (`PATCH /api/v1/trips/{id}/itinerary/items/{item_id}`).
* **Atomic Budget Synchronization:** Real-time 5-category budget recalculation and honest deficit tracking in the UI upon itinerary item replacement with transactional rollback safety.
* **Grounded AI Travel Copilot:** Contextually grounded multi-turn assistant chat (`POST /api/v1/assistant/chat`) integrating authorized trip parameters, budget balance/deficit, Open-Meteo weather forecasts, packing status, and catalogue entities into structured prompts.
* **Multi-Turn Chat Persistence:** Conversation threads persisted across `ai_conversations` and `ai_messages` with strict IDOR ownership verification.
* **Accessible Toast Notification Stack:** `ToastContext.jsx` and `ToastContainer.jsx` providing non-blocking feedback across trip creation, bookmarking, packing checklist updates, catalogue swaps, and network/auth errors.
* **Hydration Loading States:** Dedicated loading skeletons and hydrating cards across `PlanPage.jsx`, `TripsPage.jsx`, `DestinationsPage.jsx`, `ProfilePage.jsx`, `AuthPage.jsx`, and `ShowcasePage.jsx` preventing blank screens and duplicate form submissions.
* **Expanded Automated Test Suite:**
  - Added 10 tests for AI Copilot chat, IDOR guards, and context grounding (`test_assistant.py`).
  - Added 8 tests for manual item swap validation and transactional rollback (`test_trips.py`).
  - Added 3 Vitest tests for Toast notifications and timers (`ToastContext.test.jsx`).
  - Added 2 Vitest tests for 404 error routes and session-expired toasts (`App.test.jsx`).

### Changed
* **Saved Trip Reload:** Fixed `/plan?tripId=X` flow to hydrate exact persisted itineraries, days, items, and budget allocations from PostgreSQL without re-generating or creating duplicate database rows.
* **Guest Preview Isolation:** Grounded guest preview in real catalogue entities using `DeterministicScheduler` and `BudgetOptimizer` in-memory with a verified 0-database-insert guarantee.
* **Custom SQL Playground Security:** Enforced strict `admin` role authorization on `/api/v1/reports/execute-sql`, blocked multi-statement execution, blocked mutating DDL/DML keywords (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`), and blocked sensitive credential tables (`users`, `user_preferences`, `password_hash`).
* **Session Expiry Handling:** Bound `roamgenie:auth-expired` custom event in `App.jsx` to display an accessible warning toast and cleanly transition the user session without abrupt page crashes.

### Security
* Verified Argon2id password hashing and expiring JWT bearer authorization across all protected endpoints.
* Verified full IDOR isolation across trips, itineraries, packing items, user preferences, and AI chat threads.
* Blocked access to sensitive credential columns and system tables in the SQL playground.

---

## [Audit & Remediation Planning] - 2026-08-25

### Full-System MVP Audit & Roadmap
* **Definitive MVP Audit:** Performed exhaustive audit across Frontend, Backend, Database, Itinerary Engine, Budget Optimizer, AI Orchestrator, Weather Service, Security, and Automated Tests.
* **M1–M7 Remediation Backlog Established:** Authoritative engineering backlog created in `docs/phases/` (M1: Database/API Integrity, M2: Auth & Trip Lifecycle, M3: Itinerary Engine & Reload, M4: Budget Optimizer & Manual Selection, M5: AI & Weather Grounding, M6: Frontend Polish, M7: Final Verification & Release).
* **Documentation Reorganization:** Unified all documentation under `docs/` in 13 structured categories.

---

## [v1.0.0 Baseline] - 2026-08-20

### Complete Phase Rollout (Phases 1–5 Implemented & Baseline Verified)
* **Phase 1:** 22 normalized relational tables on PostgreSQL, SQLAlchemy 2.0 ORM models, Argon2id hashing, and JWT bearer auth.
* **Phase 2:** Trip CRUD, business validation engine, deterministic day-wise scheduler, budget calculator, budget optimizer, and multi-table transactional persistence.
* **Phase 3:** Multi-provider LLM adapters (Gemini, OpenAI, Groq, Mock), structured prompt schemas, Open-Meteo live weather client with geocoding and snapshot caching.
* **Phase 4:** React 18 single-page application, Destination Explorer with catalogue inspection modal, multi-step planner wizard, day-by-day timeline, visual budget bar with deficit alerts, dynamic packing checklist, AI copilot drawer, and 18-query DBMS showcase playground.
* **Phase 5:** Direct Supabase PostgreSQL pooling via SQLAlchemy `psycopg` pool, 21,017 master catalogue records across 500 global destinations.
