# Supabase PostgreSQL Execution Order

## 1. Environment

Follow `docs/SUPABASE_SETUP_GUIDE.md`; put the Dashboard-recommended connection URI in backend-only `DATABASE_URL`. Confirm the target project before any mutation. Optional local PostgreSQL is selected explicitly and rebuilt identically.

## 2. Initial migration

From `backend`: `alembic current`, `alembic history`, review, then `alembic upgrade head`. Alembic is the main application schema mechanism. Do not also run `schema/001_schema.sql` against the same database unless the migration plan explicitly treats it as verification/bootstrap instead of duplicate ownership.

## 3–6. Course objects and verification

Run seeds, then views → functions → procedures → triggers → indexes. Use Supabase SQL Editor or compatible `psql`, saving every executed statement in Git. Run `queries/001_reports.sql` and `tests/001_constraints.sql`. Scripts must be PostgreSQL-compatible, purposeful and reasonably idempotent. SQL Editor execution alone is not completion.

## 7. Reset, backup and restore

Back up before major milestones. Reset only the confirmed development project with team approval; replay Alembic then seeds/objects. Restore into a safe test target, compare schema/version and row counts, and record evidence. Never commit database dumps or credentials; see `backups/README.md` and `MIGRATION_WORKFLOW.md`.
