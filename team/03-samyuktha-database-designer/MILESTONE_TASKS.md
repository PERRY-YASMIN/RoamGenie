# Milestone Tasks

M1 design/freeze; M2 implementation validation; M3 controlled refinements; M4 final ERD; M5 consistency audit; M6 viva evidence.

At each milestone: pull `develop` → complete issue → run owned tests → test the integration boundary → attach evidence → PR to `develop` → resolve review → update progress log. Do not begin work that relies on an unfrozen contract.

<!-- SUPABASE_UPDATE_START -->
## Supabase milestones

M0: create Supabase project, safe access, environment/connection choice and empty-database health check. M1: approve Supabase-compatible ERD, SQLAlchemy model plan, Alembic/SQL ownership and API fields. M2: run initial migration/seeds, verify Table Editor and complete React auth → FastAPI → Supabase. M3: seed/query/index catalogues and complete one DB→API→React module. M4: transactionally store trip/AI-validated itinerary/expenses, verify Dashboard and reopen in React. M5: test invalid URL/password/host, timeout/outage/recovery, migrations/missing table/constraints, cross-user authorization, public exposure, secret scan, backup/restore and fresh recreation. M6: export backup and demonstrate tables, JOIN, aggregate, view, routine, trigger, transactions/indexes and complete React flow with offline evidence.

Role focus: Design PostgreSQL/Supabase-compatible schemas, record approval before implementation, review generated Alembic migrations against the ER model, confirm relationships in Dashboard and update the dictionary after every accepted migration. Never treat a manual Dashboard-only schema as delivered.
<!-- SUPABASE_UPDATE_END -->
