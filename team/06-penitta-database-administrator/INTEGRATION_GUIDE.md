# Integration Guide

1. Confirm request fields, response fields, types, optionality, errors, and tables.
2. Pull `develop` and run baseline tests.
3. Integrate only the smallest owned vertical slice.
4. Check valid, invalid, unauthorized, empty, and dependency-failure cases.
5. Notify upstream/downstream owners of contract changes; do not silently rename fields.
6. Attach version, role privileges, migration log, backup file metadata, restored row counts, EXPLAIN results.
7. Merge only after tests and relevant review pass.

<!-- SUPABASE_UPDATE_START -->
## Supabase integration

Own Supabase project/team access, connection-mode guidance, environment/secret runbook, reviewed migration application, Dashboard/log monitoring, permissions, backup/restore/reset, index/performance verification and the demo database. Export before major milestones and maintain offline evidence.

Verify the owned feature through Supabase object → SQLAlchemy/repository → service → FastAPI → React and attach migration/seed/test plus Dashboard evidence. Do not accept manual Dashboard state as integration.
<!-- SUPABASE_UPDATE_END -->
