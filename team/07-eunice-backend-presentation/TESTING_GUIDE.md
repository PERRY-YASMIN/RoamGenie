# Testing Guide

## Preconditions

Install dependencies, copy `.env.example`, use mock AI, and load demo seed data where needed.

## Run and verify

Test success plus 401/404/422/500-safe responses in `/docs`; run integration tests; rehearse demo twice on a clean setup.

Input one valid, boundary, and invalid case. Expected: valid succeeds; boundary obeys contract; invalid returns a clear safe error. A failure means this work is not ready for handoff. Save terminal output/screenshots and record the responsible owner: EUNICE MERCY M.

<!-- SUPABASE_UPDATE_START -->
## Supabase testing

Test database connectivity and `/api/health`, verify records in Dashboard, capture Table Editor and SQL result evidence, and demonstrate React → FastAPI → Supabase PostgreSQL. Prepare offline database/ERD/architecture/API/frontend screenshots and an optional recording.

Test the relevant valid connection, invalid credentials/host, network outage/timeout/recovery, migration/schema/seed constraints, unauthorized and cross-user access, and offline demo fallback. Never print connection strings. Record target environment, Alembic revision, expected/actual result and evidence.
<!-- SUPABASE_UPDATE_END -->
