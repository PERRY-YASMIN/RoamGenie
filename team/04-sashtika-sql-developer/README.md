# SASHTIKA S — SQL Developer

## Responsibility

- Primary responsibility: PostgreSQL DDL/DML, sample data, 15+ queries, joins, views, routines, purposeful triggers, transactions, indexes, reports.
- Modules owned: PostgreSQL DDL/DML, sample data, 15+ queries, joins, views, routines, purposeful triggers, transactions, indexes, reports.
- Files owned: `database/schema`, `seeds`, `queries`, `views`, `functions`, `procedures`, `triggers`, `indexes`, `transactions`, `reports`, `tests`.
- May modify: data dictionary corrections through review.
- Do not modify without approval: ER model or ORM migrations without Samyuktha/Yasmin approval.
- Dependencies: frozen relational schema from Samyuktha.
- Expected deliverables: idempotent ordered SQL scripts, realistic seed data, verified result notes and DBMS demonstrations.
- Testing responsibility: Run scripts on an empty database; run `database/tests/001_constraints.sql`; use `EXPLAIN ANALYZE` before/after indexes.
- Integration responsibility: demonstrate the owned slice against `develop`, document contract mismatches, and support its reviewer.
- Branch: `sql/sashtika`.
- Pull request: target `develop`; link issue; list tests, evidence, limitations; obtain one relevant review and Yasmin's integration approval.
- Complete when: Code/docs exist; required tests pass; no secrets; contracts match; evidence is attached; reviewed PR is merged to `develop`; `PROJECT_STATUS.md` and progress log are updated.

<!-- SUPABASE_UPDATE_START -->
## Supabase responsibility

Keep all SQL PostgreSQL-compatible and versioned. Test scripts in Supabase SQL Editor or compatible psql and supply verification queries/results. SQL Editor execution alone is incomplete. Coordinate DDL ownership so Alembic does not duplicate standalone course objects.
<!-- SUPABASE_UPDATE_END -->
