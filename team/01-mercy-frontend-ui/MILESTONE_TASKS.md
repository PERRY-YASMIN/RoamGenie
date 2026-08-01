# Milestone Tasks

M1 wireframes/contracts; M2 shell/auth; M3 catalogues; M4 trip/AI/budget; M5 tests/polish; M6 screenshots.

At each milestone: pull `develop` → complete issue → run owned tests → test the integration boundary → attach evidence → PR to `develop` → resolve review → update progress log. Do not begin work that relies on an unfrozen contract.

<!-- SUPABASE_UPDATE_START -->
## Supabase milestones

M0: create Supabase project, safe access, environment/connection choice and empty-database health check. M1: approve Supabase-compatible ERD, SQLAlchemy model plan, Alembic/SQL ownership and API fields. M2: run initial migration/seeds, verify Table Editor and complete React auth → FastAPI → Supabase. M3: seed/query/index catalogues and complete one DB→API→React module. M4: transactionally store trip/AI-validated itinerary/expenses, verify Dashboard and reopen in React. M5: test invalid URL/password/host, timeout/outage/recovery, migrations/missing table/constraints, cross-user authorization, public exposure, secret scan, backup/restore and fresh recreation. M6: export backup and demonstrate tables, JOIN, aggregate, view, routine, trigger, transactions/indexes and complete React flow with offline evidence.

Role focus: React calls FastAPI only. Do not add the Supabase JavaScript client or any database/service-role credential. Use contract-matched mock API data while endpoints are pending. Dashboard is not the app UI; its screenshots are presentation evidence only.
<!-- SUPABASE_UPDATE_END -->
