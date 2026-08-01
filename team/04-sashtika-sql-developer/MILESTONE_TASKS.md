# Milestone Tasks

M1 DDL mapping; M2 schema/seeds; M3 queries/views; M4 routines/triggers/transactions; M5 clean replay; M6 SQL demo.

At each milestone: pull `develop` → complete issue → run owned tests → test the integration boundary → attach evidence → PR to `develop` → resolve review → update progress log. Do not begin work that relies on an unfrozen contract.

<!-- SUPABASE_UPDATE_START -->
## Supabase milestones

M0: create Supabase project, safe access, environment/connection choice and empty-database health check. M1: approve Supabase-compatible ERD, SQLAlchemy model plan, Alembic/SQL ownership and API fields. M2: run initial migration/seeds, verify Table Editor and complete React auth → FastAPI → Supabase. M3: seed/query/index catalogues and complete one DB→API→React module. M4: transactionally store trip/AI-validated itinerary/expenses, verify Dashboard and reopen in React. M5: test invalid URL/password/host, timeout/outage/recovery, migrations/missing table/constraints, cross-user authorization, public exposure, secret scan, backup/restore and fresh recreation. M6: export backup and demonstrate tables, JOIN, aggregate, view, routine, trigger, transactions/indexes and complete React flow with offline evidence.

Role focus: Keep all SQL PostgreSQL-compatible and versioned. Test scripts in Supabase SQL Editor or compatible psql and supply verification queries/results. SQL Editor execution alone is incomplete. Coordinate DDL ownership so Alembic does not duplicate standalone course objects.
<!-- SUPABASE_UPDATE_END -->
