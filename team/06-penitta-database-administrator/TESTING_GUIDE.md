# Testing Guide

## Preconditions

Install dependencies, copy `.env.example`, use mock AI, and load demo seed data where needed.

## Run and verify

Connect as app and read-only users; verify denied writes for read-only; restore into a separate `roamgenie_restore_test` database; compare row counts.

Input one valid, boundary, and invalid case. Expected: valid succeeds; boundary obeys contract; invalid returns a clear safe error. A failure means this work is not ready for handoff. Save terminal output/screenshots and record the responsible owner: PENITTA A.

<!-- SUPABASE_UPDATE_START -->
## Supabase testing

Own Supabase project/team access, connection-mode guidance, environment/secret runbook, reviewed migration application, Dashboard/log monitoring, permissions, backup/restore/reset, index/performance verification and the demo database. Export before major milestones and maintain offline evidence.

Test the relevant valid connection, invalid credentials/host, network outage/timeout/recovery, migration/schema/seed constraints, unauthorized and cross-user access, and offline demo fallback. Never print connection strings. Record target environment, Alembic revision, expected/actual result and evidence.
<!-- SUPABASE_UPDATE_END -->
