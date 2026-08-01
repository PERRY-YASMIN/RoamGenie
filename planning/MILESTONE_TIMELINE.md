# Milestone Timeline

M0: scope, repo, standards, board, environments, initial architecture. M1: Mercy wireframes; Yasmin API/auth plan; Samyuktha ERD/schema/normalization; Sashtika DDL map; Madhu AI schemas/prompts; Penitta DB/roles plan; Eunice test/presentation plan. M2: UI/auth shell; FastAPI/auth/DB; DDL/seeds; mock AI; DB reset; auth tests. M3: catalogue UIs/APIs/seeds/joins/views/recommendations/index review/tests. M4: trip/itinerary/budget/save UI/API/schema/SQL routines/AI/weather/restore/full-flow test. M5: test, security, performance, polish, feature freeze. M6: final docs, report, evidence, rehearsal, backup, clean install, release.

Adjustable rule: assign actual start/end dates beside each milestone, preserve dependency order, reserve at least 20% of calendar for M5–M6, and tag only after exit criteria.

<!-- SUPABASE_UPDATE_START -->
## Supabase timeline update

M0: create Supabase project, safe access, environment/connection choice and empty-database health check. M1: approve Supabase-compatible ERD, SQLAlchemy model plan, Alembic/SQL ownership and API fields. M2: run initial migration/seeds, verify Table Editor and complete React auth → FastAPI → Supabase. M3: seed/query/index catalogues and complete one DB→API→React module. M4: transactionally store trip/AI-validated itinerary/expenses, verify Dashboard and reopen in React. M5: test invalid URL/password/host, timeout/outage/recovery, migrations/missing table/constraints, cross-user authorization, public exposure, secret scan, backup/restore and fresh recreation. M6: export backup and demonstrate tables, JOIN, aggregate, view, routine, trigger, transactions/indexes and complete React flow with offline evidence.
<!-- SUPABASE_UPDATE_END -->
