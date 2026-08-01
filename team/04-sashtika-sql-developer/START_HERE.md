# Start Here

1. **Build:** PostgreSQL DDL/DML, sample data, 15+ queries, joins, views, routines, purposeful triggers, transactions, indexes, reports.
2. **Why:** this supplies the project's sql developer deliverable and a tested link in the database → API → UI flow.
3. **Inputs:** frozen relational schema from Samyuktha.
4. **Outputs:** idempotent ordered SQL scripts, realistic seed data, verified result notes and DBMS demonstrations.
5. **Setup:** copy `backend/.env.example` to `backend/.env`, configure backend-only `DATABASE_URL`, then run `cd backend; alembic current; alembic upgrade head`. Load reviewed course SQL through Supabase SQL Editor or compatible `psql` as documented in `database/README.md`.
6. **Implementation order:** DDL/constraints → seed data → 15 queries → views → functions/procedure → useful audit/total trigger → transactions → indexes → verification.
7. **Testing:** Run scripts on an empty database; run `database/tests/001_constraints.sql`; use `EXPLAIN ANALYZE` before/after indexes.
8. **Git:** use the commands in `GITHUB_GUIDE.md` on `sql/sashtika`.
9. **Evidence:** clean execution log, query outputs, constraint failures, transaction rollback, EXPLAIN output.
10. **Final connection:** integrate the owned output on `develop`; the feature is incomplete until its upstream and downstream contracts both work.

<!-- SUPABASE_UPDATE_START -->
## Updated architecture

Primary path: React → FastAPI → SQLAlchemy → Supabase-hosted PostgreSQL. Keep all SQL PostgreSQL-compatible and versioned. Test scripts in Supabase SQL Editor or compatible psql and supply verification queries/results. SQL Editor execution alone is incomplete. Coordinate DDL ownership so Alembic does not duplicate standalone course objects. Before starting, read `../../docs/SUPABASE_SETUP_GUIDE.md` and confirm the relevant contract/migration status.
<!-- SUPABASE_UPDATE_END -->
