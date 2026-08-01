# Testing Guide

Use `.env` with `AI_PROVIDER=mock` and a dedicated test database. Never point destructive tests at demo/production data.

| Area | Preconditions | Command | Input/expected | Failure owner |
|---|---|---|---|---|
| Backend | venv/deps | `cd backend; pytest` | valid + invalid API; expected 2xx/4xx, no trace | endpoint owner |
| Database | empty test DB | `psql -v ON_ERROR_STOP=1 -d roamgenie_test -f database/tests/001_constraints.sql` | invalid constraints rejected | Sashtika/Penitta |
| Frontend | npm deps | `cd frontend; npm test -- --run; npm run build` | routes/forms/states render | Mercy |
| AI | mock mode | `cd backend; pytest ../tests/ai` | valid/malformed/timeout/no-key/fallback | Madhu |
| Integration | services ready | `cd backend; pytest ../tests/integration` | register→login→trip→generate→budget→save→retrieve/edit/delete/logout | Yasmin/Eunice |

Also verify configuration, auth/authorization, CRUD, validation, error safety, foreign keys, seeds, views, routines, triggers, transactions, indexes, backup/restore, responsive layouts, protected routes, empty/error states, unrealistic budget and empty preferences. Record test input, expected/actual result, environment, commit and evidence.

<!-- SUPABASE_UPDATE_START -->
## Supabase PostgreSQL test matrix

**Connection:** valid URL, invalid password/host, network/database unavailable, timeout and recovery; health response must never expose URI. **Migration:** empty→head, existing→latest, current/history, safe downgrade/re-upgrade and documented idempotency limits. **Schema/data:** tables/types/PK/FK/unique/check/cascade, repeatable seeds and valid relationships. **Security:** `.env` ignored; Git history contains no password/service role; no service role in frontend; unauthorized API and cross-user trip access fail; public table access is not enabled. **Backup:** export, restore safely, compare migration revision/row counts. **Presentation:** Dashboard/tables/SQL work and offline screenshots remain usable during an outage.
<!-- SUPABASE_UPDATE_END -->
