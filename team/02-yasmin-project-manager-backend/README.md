# SHAIK YASMIN — Project Manager & Backend Developer

## Responsibility

- Primary responsibility: FastAPI setup, auth, users, catalogues, trips, itineraries, budgets, saved trips, AI endpoints, final integration.
- Modules owned: FastAPI setup, auth, users, catalogues, trips, itineraries, budgets, saved trips, AI endpoints, final integration.
- Files owned: root/planning documents, `backend/`, integration tests and release coordination.
- May modify: all modules during reviewed integration.
- Do not modify without approval: another member's active feature without discussion; history rewriting on shared branches.
- Dependencies: approved schema from Samyuktha/Sashtika, AI contract from Madhu, frontend needs from Mercy.
- Expected deliverables: versioned validated API, JWT auth, service/repository boundaries, tests, reviewed milestone merges.
- Testing responsibility: Run `pytest`; inspect `/docs`; test 401/403/404/422 paths and full register-to-reopen journey.
- Integration responsibility: demonstrate the owned slice against `develop`, document contract mismatches, and support its reviewer.
- Branch: `backend/yasmin`.
- Pull request: target `develop`; link issue; list tests, evidence, limitations; obtain one relevant review and Yasmin's integration approval.
- Complete when: Code/docs exist; required tests pass; no secrets; contracts match; evidence is attached; reviewed PR is merged to `develop`; `PROJECT_STATUS.md` and progress log are updated.

<!-- SUPABASE_UPDATE_START -->
## Supabase responsibility

Own the Supabase–FastAPI connection, SQLAlchemy engine/session, Alembic, environment setup, migration review, `/api/health`, integration tests, schema-change coordination and final secret review. Ensure FastAPI remains React's normal database access layer.
<!-- SUPABASE_UPDATE_END -->
