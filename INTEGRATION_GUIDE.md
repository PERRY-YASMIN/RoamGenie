# Integration Guide

For every feature, move vertically: **database → ORM/repository → service → API → frontend → test**. Do not build entire layers in isolation.

Before implementation freeze request/response fields, types, optionality, errors and tables. Recheck whenever schema affects ORM, responses affect UI, AI output affects validation, triggers affect CRUD, migrations alter data, or auth protects pages.

## Feature checkpoint

- [ ] Database object/migration exists and rolls forward.
- [ ] Endpoint and documented errors work.
- [ ] Frontend calls it and shows loading/empty/error/success.
- [ ] Valid input succeeds; invalid and unauthorized input fail safely.
- [ ] AI/external dependency fallback works where applicable.
- [ ] Tests/docs/status updated; reviewed PR merged to `develop`.

First checkpoint: freeze destination fields, implement seeded destination row → repository → `GET /api/v1/destinations` → destination card → integration test. Use it as the pattern for other catalogues.

<!-- SUPABASE_UPDATE_START -->
## Supabase integration policy

The vertical path is **Supabase PostgreSQL → SQLAlchemy repository → service → FastAPI API → React → test**. Before work, agree on table/columns, ORM model, migration, request/response, errors and ownership rules. The database gate is not “visible in Dashboard”: migration, seed, constraints, FastAPI operation and React behavior must all pass.

First checkpoint: FastAPI connects to an empty Supabase development database and `GET /api/health` reports application `online` plus database `connected` without revealing host, password or URL. Then freeze the destination ER model + SQLAlchemy model + migration plan before building the first full vertical module.
<!-- SUPABASE_UPDATE_END -->
