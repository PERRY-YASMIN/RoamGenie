# Integration Guide

1. Confirm request fields, response fields, types, optionality, errors, and tables.
2. Pull `develop` and run baseline tests.
3. Integrate only the smallest owned vertical slice.
4. Check valid, invalid, unauthorized, empty, and dependency-failure cases.
5. Notify upstream/downstream owners of contract changes; do not silently rename fields.
6. Attach API test results, architecture/ERD/UI screenshots, timed script, speaker sheet, backup screenshots/video location.
7. Merge only after tests and relevant review pass.

<!-- SUPABASE_UPDATE_START -->
## Supabase integration

Test database connectivity and `/api/health`, verify records in Dashboard, capture Table Editor and SQL result evidence, and demonstrate React → FastAPI → Supabase PostgreSQL. Prepare offline database/ERD/architecture/API/frontend screenshots and an optional recording.

Verify the owned feature through Supabase object → SQLAlchemy/repository → service → FastAPI → React and attach migration/seed/test plus Dashboard evidence. Do not accept manual Dashboard state as integration.
<!-- SUPABASE_UPDATE_END -->
