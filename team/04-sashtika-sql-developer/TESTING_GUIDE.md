# Testing Guide

## Preconditions

Install dependencies, copy `.env.example`, use mock AI, and load demo seed data where needed.

## Run and verify

Run scripts on an empty database; run `database/tests/001_constraints.sql`; use `EXPLAIN ANALYZE` before/after indexes.

Input one valid, boundary, and invalid case. Expected: valid succeeds; boundary obeys contract; invalid returns a clear safe error. A failure means this work is not ready for handoff. Save terminal output/screenshots and record the responsible owner: SASHTIKA S.

<!-- SUPABASE_UPDATE_START -->
## Supabase testing

Keep all SQL PostgreSQL-compatible and versioned. Test scripts in Supabase SQL Editor or compatible psql and supply verification queries/results. SQL Editor execution alone is incomplete. Coordinate DDL ownership so Alembic does not duplicate standalone course objects.

Test the relevant valid connection, invalid credentials/host, network outage/timeout/recovery, migration/schema/seed constraints, unauthorized and cross-user access, and offline demo fallback. Never print connection strings. Record target environment, Alembic revision, expected/actual result and evidence.
<!-- SUPABASE_UPDATE_END -->
