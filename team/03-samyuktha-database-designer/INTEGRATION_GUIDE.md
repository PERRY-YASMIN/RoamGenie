# Integration Guide

1. Confirm request fields, response fields, types, optionality, errors, and tables.
2. Pull `develop` and run baseline tests.
3. Integrate only the smallest owned vertical slice.
4. Check valid, invalid, unauthorized, empty, and dependency-failure cases.
5. Notify upstream/downstream owners of contract changes; do not silently rename fields.
6. Attach rendered ERD, normalization table, reviewed dictionary, signed schema-v1 checkpoint.
7. Merge only after tests and relevant review pass.

<!-- SUPABASE_UPDATE_START -->
## Supabase integration

Design PostgreSQL/Supabase-compatible schemas, record approval before implementation, review generated Alembic migrations against the ER model, confirm relationships in Dashboard and update the dictionary after every accepted migration. Never treat a manual Dashboard-only schema as delivered.

Verify the owned feature through Supabase object → SQLAlchemy/repository → service → FastAPI → React and attach migration/seed/test plus Dashboard evidence. Do not accept manual Dashboard state as integration.
<!-- SUPABASE_UPDATE_END -->
