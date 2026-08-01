# Testing Guide

## Preconditions

Install dependencies, copy `.env.example`, use mock AI, and load demo seed data where needed.

## Run and verify

Test valid JSON, invalid JSON, missing fields, timeout, missing key, empty preferences, invalid destination, unrealistic budget and unknown IDs.

Input one valid, boundary, and invalid case. Expected: valid succeeds; boundary obeys contract; invalid returns a clear safe error. A failure means this work is not ready for handoff. Save terminal output/screenshots and record the responsible owner: MADHUVARSHINI A.

<!-- SUPABASE_UPDATE_START -->
## Supabase testing

AI calls backend services and receives validated structured records. It never receives Supabase credentials, executes arbitrary SQL, changes tables or invents trusted IDs. FastAPI validates referenced IDs and persists accepted output. Preserve mock mode.

Test the relevant valid connection, invalid credentials/host, network outage/timeout/recovery, migration/schema/seed constraints, unauthorized and cross-user access, and offline demo fallback. Never print connection strings. Record target environment, Alembic revision, expected/actual result and evidence.
<!-- SUPABASE_UPDATE_END -->
