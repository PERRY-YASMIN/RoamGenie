# Integration Guide

1. Confirm request fields, response fields, types, optionality, errors, and tables.
2. Pull `develop` and run baseline tests.
3. Integrate only the smallest owned vertical slice.
4. Check valid, invalid, unauthorized, empty, and dependency-failure cases.
5. Notify upstream/downstream owners of contract changes; do not silently rename fields.
6. Attach issue board, API docs, passing test output, auth flow, full journey, review approvals, milestone tags.
7. Merge only after tests and relevant review pass.

<!-- SUPABASE_UPDATE_START -->
## Supabase integration

Own the Supabase–FastAPI connection, SQLAlchemy engine/session, Alembic, environment setup, migration review, `/api/health`, integration tests, schema-change coordination and final secret review. Ensure FastAPI remains React's normal database access layer.

Verify the owned feature through Supabase object → SQLAlchemy/repository → service → FastAPI → React and attach migration/seed/test plus Dashboard evidence. Do not accept manual Dashboard state as integration.
<!-- SUPABASE_UPDATE_END -->
