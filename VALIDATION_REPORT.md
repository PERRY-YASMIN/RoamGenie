# Validation Report — 2026-08-01

## Passed

- 220 project files checked (excluding dependencies/build output); 163 Markdown documents scanned with no broken inline file links.
- Exactly seven team folders and 112 required handbook files (16 each).
- All seven official names and branch names appear exactly once in their role README.
- JSON manifests/schema/mock files parse successfully.
- `npm test -- --run`: 1 file, 2 tests passed.
- `npm run build`: Vite production build passed (27 modules).
- No committed `.env`; placeholder/example values only. Working output and dependencies are ignored.

## Environment-limited checks

- PostgreSQL/`psql` is not installed here, so SQL replay, constraints, routines, trigger, transaction and restore require Penitta's PostgreSQL environment.
- The Windows Python launcher became inaccessible to the sandbox after it ran the workspace generator, so backend pytest could not be executed here. Python dependencies were not installed.
- `npm install` reported two high-severity advisories, but the registry audit endpoint was blocked by sandbox policy. Do not run `npm audit fix --force`; review advisories and compatible upgrades in an authorized environment.

## Known starter boundaries

Only the health endpoint, mock plan preview, responsive landing/plan screens and API-client tests are runnable starter slices. Authentication, persistence/migrations, catalogues, saved trips, real AI/weather adapters, full UI and acceptance suite remain milestone work and are marked in `PROJECT_STATUS.md`/TODOs.

## Supabase update validation

- Backend suite now passes 5 tests, including safe invalid-URL handling and `/api/health` status shape.
- Frontend lint, 2 tests and production build pass.
- Every member's required start/setup/milestone/integration/testing/checklist/Codex files contains the hosted PostgreSQL decision.
- Live Supabase connection, migration, SQL object, Dashboard and backup/restore evidence requires the team project and backend-only credentials; it was not simulated or claimed.

