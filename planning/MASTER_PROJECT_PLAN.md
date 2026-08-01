# Master Project Plan

## Outcome and scope

Build the v1 journey and DBMS evidence defined in `REQUIREMENTS.md`; bookings, payments and autonomous actions are out of scope. Architecture is React → FastAPI → services/repositories → PostgreSQL, with isolated AI/weather adapters.

## Eight-week timeline

| Time | Milestone | Exit checkpoint |
|---|---|---|
| Days 1–3 | M0 initialization | two machines set up; board/workflow; tag `milestone-0` |
| Week 1 | M1 requirements/contracts | ERD, schema, API, UI and AI schema v1 frozen; tag |
| Week 2 | M2 foundation/auth | Supabase PostgreSQL + register/login UI/API smoke test; tag |
| Weeks 3–4 | M3 catalogues | destination vertical slice, then all catalogues; tag |
| Weeks 5–6 | M4 trip/AI/budget | complete saved user journey; tag |
| Week 7 | M5 hardening | security/restore/fresh setup; `milestone-5-rc1` |
| Week 8 | M6 submission | clean demo, main merge and `v1.0.0` |

If official dates move, retain sequence/exit criteria and map Day 1 to the official start; never compress the M1 contract checkpoint or M5 test/restore gate.

## Work and dependencies

Mercy UI ← Yasmin API contracts; Yasmin backend ← Samyuktha schema; Sashtika SQL ← approved schema; Madhu AI ← trip/catalogue contract; Penitta operations ← SQL/migrations; Eunice tests/presentation ← stable integrated slices. See matrices.

## Checkpoints and acceptance

Review ERD/API/UI fields before M1 freeze; integrate destination first in M3; in M4 check trip save, AI validation, persistence and reopen separately. Owners unit-test; Eunice verifies APIs/demo; Yasmin owns integration/acceptance; Penitta verifies DB restore. Use GitHub flow, risk register and Definition of Done. Final acceptance requires clean setup, full journey, SQL demonstrations, mock fallback, tests/evidence, no secrets, reviewed main merge and tag.

<!-- SUPABASE_UPDATE_START -->
## Supabase milestone gates

M0: create Supabase project, safe access, environment/connection choice and empty-database health check. M1: approve Supabase-compatible ERD, SQLAlchemy model plan, Alembic/SQL ownership and API fields. M2: run initial migration/seeds, verify Table Editor and complete React auth → FastAPI → Supabase. M3: seed/query/index catalogues and complete one DB→API→React module. M4: transactionally store trip/AI-validated itinerary/expenses, verify Dashboard and reopen in React. M5: test invalid URL/password/host, timeout/outage/recovery, migrations/missing table/constraints, cross-user authorization, public exposure, secret scan, backup/restore and fresh recreation. M6: export backup and demonstrate tables, JOIN, aggregate, view, routine, trigger, transactions/indexes and complete React flow with offline evidence.
<!-- SUPABASE_UPDATE_END -->
