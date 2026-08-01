# Testing Guide

## Preconditions

Install dependencies, copy `.env.example`, use mock AI, and load demo seed data where needed.

## Run and verify

Trace every foreign key; test optionality/deletion rules on paper; ask Sashtika to execute DDL and Penitta to review operations.

Input one valid, boundary, and invalid case. Expected: valid succeeds; boundary obeys contract; invalid returns a clear safe error. A failure means this work is not ready for handoff. Save terminal output/screenshots and record the responsible owner: SAMYUKTHA KUMARAN.

<!-- SUPABASE_UPDATE_START -->
## Supabase testing

Design PostgreSQL/Supabase-compatible schemas, record approval before implementation, review generated Alembic migrations against the ER model, confirm relationships in Dashboard and update the dictionary after every accepted migration. Never treat a manual Dashboard-only schema as delivered.

Test the relevant valid connection, invalid credentials/host, network outage/timeout/recovery, migration/schema/seed constraints, unauthorized and cross-user access, and offline demo fallback. Never print connection strings. Record target environment, Alembic revision, expected/actual result and evidence.
<!-- SUPABASE_UPDATE_END -->
