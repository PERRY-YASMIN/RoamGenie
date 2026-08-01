# Role Scope

## Own

root/planning documents, `backend/`, integration tests and release coordination.

## Coordinate

- Inputs: approved schema from Samyuktha/Sashtika, AI contract from Madhu, frontend needs from Mercy.
- Outputs: versioned validated API, JWT auth, service/repository boundaries, tests, reviewed milestone merges.
- Must not change: another member's active feature without discussion; history rewriting on shared branches.
- Escalate contract conflicts to Yasmin before coding past the conflict.

<!-- SUPABASE_UPDATE_START -->
## Supabase boundary

Own the Supabase–FastAPI connection, SQLAlchemy engine/session, Alembic, environment setup, migration review, `/api/health`, integration tests, schema-change coordination and final secret review. Ensure FastAPI remains React's normal database access layer.
<!-- SUPABASE_UPDATE_END -->
