# Role Scope

## Own

`database/schema`, `seeds`, `queries`, `views`, `functions`, `procedures`, `triggers`, `indexes`, `transactions`, `reports`, `tests`.

## Coordinate

- Inputs: frozen relational schema from Samyuktha.
- Outputs: idempotent ordered SQL scripts, realistic seed data, verified result notes and DBMS demonstrations.
- Must not change: ER model or ORM migrations without Samyuktha/Yasmin approval.
- Escalate contract conflicts to Yasmin before coding past the conflict.

<!-- SUPABASE_UPDATE_START -->
## Supabase boundary

Keep all SQL PostgreSQL-compatible and versioned. Test scripts in Supabase SQL Editor or compatible psql and supply verification queries/results. SQL Editor execution alone is incomplete. Coordinate DDL ownership so Alembic does not duplicate standalone course objects.
<!-- SUPABASE_UPDATE_END -->
