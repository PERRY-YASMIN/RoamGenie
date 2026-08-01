# Testing Guide

## Preconditions

Install dependencies, copy `.env.example`, use mock AI, and load demo seed data where needed.

## Run and verify

Run `pytest`; inspect `/docs`; test 401/403/404/422 paths and full register-to-reopen journey.

Input one valid, boundary, and invalid case. Expected: valid succeeds; boundary obeys contract; invalid returns a clear safe error. A failure means this work is not ready for handoff. Save terminal output/screenshots and record the responsible owner: SHAIK YASMIN.

<!-- SUPABASE_UPDATE_START -->
## Supabase testing

Own the Supabase–FastAPI connection, SQLAlchemy engine/session, Alembic, environment setup, migration review, `/api/health`, integration tests, schema-change coordination and final secret review. Ensure FastAPI remains React's normal database access layer.

Test the relevant valid connection, invalid credentials/host, network outage/timeout/recovery, migration/schema/seed constraints, unauthorized and cross-user access, and offline demo fallback. Never print connection strings. Record target environment, Alembic revision, expected/actual result and evidence.
<!-- SUPABASE_UPDATE_END -->
