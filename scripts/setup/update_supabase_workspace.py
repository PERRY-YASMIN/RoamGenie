"""Apply the approved Supabase-hosted PostgreSQL architecture update in place."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
START = "<!-- SUPABASE_UPDATE_START -->"
END = "<!-- SUPABASE_UPDATE_END -->"


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.strip() + "\n", encoding="utf-8")


def upsert(path: str, heading: str, body: str) -> None:
    target = ROOT / path
    old = target.read_text(encoding="utf-8") if target.exists() else f"# {heading}\n"
    block = f"{START}\n## {heading}\n\n{body.strip()}\n{END}"
    if START in old and END in old:
        before, rest = old.split(START, 1)
        _, after = rest.split(END, 1)
        new = before.rstrip() + "\n\n" + block + after
    else:
        new = old.rstrip() + "\n\n" + block + "\n"
    target.write_text(new, encoding="utf-8")


ENV = """APP_NAME=RoamGenie
APP_ENV=development
APP_DEBUG=false
API_V1_PREFIX=/api/v1
SECRET_KEY=CHANGE_ME_WITH_A_LONG_RANDOM_LOCAL_VALUE
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Primary team database: copy the current connection string from Supabase Dashboard.
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@HOST:5432/postgres
# Optional disposable fallback. Do not activate both URLs implicitly.
LOCAL_DATABASE_URL=postgresql+psycopg://postgres:LOCAL_PASSWORD@localhost:5432/ai_travel_planner
DATABASE_ENV=supabase
DB_CONNECT_TIMEOUT_SECONDS=5

SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_ANON_KEY=YOUR_PUBLIC_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=NEVER_EXPOSE_THIS_TO_FRONTEND

CORS_ORIGINS=http://localhost:5173
AI_PROVIDER=mock
AI_API_KEY=
AI_MODEL=
AI_TIMEOUT_SECONDS=15
WEATHER_PROVIDER=mock
WEATHER_API_KEY=
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
"""
write(".env.example", ENV)
write("backend/.env.example", """# Copy to backend/.env or configure the process environment.
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@HOST:5432/postgres
DATABASE_ENV=supabase
DB_CONNECT_TIMEOUT_SECONDS=5
SECRET_KEY=CHANGE_ME_WITH_A_LONG_RANDOM_LOCAL_VALUE
CORS_ORIGINS=http://localhost:5173
AI_PROVIDER=mock
AI_API_KEY=
# Backend-only and normally unused. Never place this in VITE_* variables.
SUPABASE_SERVICE_ROLE_KEY=NEVER_EXPOSE_THIS_TO_FRONTEND
""")

ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
for pattern in [".env.*", "!.env.example", "!backend/.env.example", "frontend/.env", "backend/.env", ".supabase/", "database/backups/*", "!database/backups/.gitkeep"]:
    if pattern not in ignore.splitlines():
        ignore += pattern + "\n"
(ROOT / ".gitignore").write_text(ignore, encoding="utf-8")

upsert("README.md", "Supabase-hosted PostgreSQL decision", """The primary shared database is **PostgreSQL hosted by Supabase**. Supabase is the managed platform, not a second DBMS. React sends HTTP/JSON to FastAPI; FastAPI uses SQLAlchemy and `DATABASE_URL`; Alembic evolves the application schema. Supabase Dashboard supplies Table Editor, SQL Editor, logs and presentation evidence—not the user interface.

Start with `docs/SUPABASE_SETUP_GUIDE.md`. Copy `.env.example` to `.env`, replace only local placeholders, then from `backend` run `alembic current`, `alembic upgrade head`, and `uvicorn app.main:app --reload`. Verify `GET /api/health`. Local PostgreSQL is an optional disposable fallback created from the same migrations and seeds; it is never a second synchronized source of truth.""")

upsert("ARCHITECTURE.md", "Hosted database architecture", """```mermaid
flowchart LR
  R[React/Vite] -->|HTTP/JSON| F[FastAPI]
  F -->|SQLAlchemy + psycopg| S[(Supabase-hosted PostgreSQL)]
  A[Alembic migrations] --> S
  Q[GitHub PostgreSQL SQL scripts] --> S
  D[Supabase Dashboard\nTable Editor · SQL Editor · Logs] -. admin/demo .-> S
  T[psql · DBeaver · pgAdmin] -. optional admin .-> S
```

PostgreSQL remains the relational DBMS. FastAPI remains the normal and only database access layer for React and owns authentication, authorization, validation and business logic. Supabase does not replace it. Migrations and Git SQL files are reproducible truth: any Dashboard experiment must be recreated and reviewed as Alembic or version-controlled SQL.

No database password or service-role key reaches React. RLS is not the primary authorization mechanism in this server-mediated design; FastAPI enforces ownership. Keep public table exposure disabled. If direct browser access is explicitly introduced later, document the reason, expose at most a public anon key, enable/test ownership-based RLS first, and never expose the service-role key.""")

upsert("INTEGRATION_GUIDE.md", "Supabase integration policy", """The vertical path is **Supabase PostgreSQL → SQLAlchemy repository → service → FastAPI API → React → test**. Before work, agree on table/columns, ORM model, migration, request/response, errors and ownership rules. The database gate is not “visible in Dashboard”: migration, seed, constraints, FastAPI operation and React behavior must all pass.

First checkpoint: FastAPI connects to an empty Supabase development database and `GET /api/health` reports application `online` plus database `connected` without revealing host, password or URL. Then freeze the destination ER model + SQLAlchemy model + migration plan before building the first full vertical module.""")

upsert("REQUIREMENTS.md", "Database platform requirements", """NFR-DB1 Supabase-hosted PostgreSQL is the primary team database. NFR-DB2 FastAPI uses environment-only `DATABASE_URL` through SQLAlchemy/psycopg. NFR-DB3 Alembic is the main application schema evolution path; course SQL objects remain version controlled and PostgreSQL-compatible. NFR-DB4 manual Dashboard changes are incomplete until reproduced in Git. NFR-DB5 frontend and AI receive no database/service-role credentials. NFR-DB6 local PostgreSQL is an optional isolated fallback rebuilt from the same migrations/seeds.""")

upsert("docs/06-system-architecture.md", "Supabase deployment", """The deployed path is React → FastAPI → Supabase-hosted PostgreSQL. SQLAlchemy owns application access and sessions; Alembic owns schema evolution; PostgreSQL SQL files demonstrate DBMS objects. Dashboard/Table Editor/SQL Editor/logs and optional psql/DBeaver/pgAdmin are administrative tools only.""")
upsert("docs/07-database-architecture.md", "Source of truth and tools", """Supabase hosts the central PostgreSQL database. GitHub migrations and SQL files—not Dashboard state—make it reproducible. Alembic creates/evolves application tables; reviewed scripts create or demonstrate views, functions, procedures, purposeful triggers, transactions, reports and indexes. Avoid duplicate DDL ownership. Every manual Table Editor or SQL Editor change must become a reviewed migration/script.""")
upsert("docs/10-security-design.md", "Supabase credentials and RLS", """Store connection strings and database passwords only in backend secrets. `SUPABASE_SERVICE_ROLE_KEY` is backend-only and should remain unused unless a reviewed feature requires it; it bypasses RLS and is never a `VITE_*` variable. Do not expose public tables. FastAPI JWT/ownership checks remain authoritative because React has no direct table access. If direct client access is approved later, enable RLS first and test that user A cannot read/update user B's trips or itineraries.

Optional policy template for a future architecture using Supabase Auth—not applied now: `CREATE POLICY own_trips ON trips FOR SELECT USING (user_id = auth.uid());`. The current bigint user key/FastAPI JWT design is not compatible with that example without an approved identity mapping.""")
upsert("docs/12-deployment-plan.md", "Primary and fallback databases", """Primary: agreed Supabase project and its Dashboard-recommended connection mode. Optional local: isolated PostgreSQL for offline work or migration tests, selected explicitly with `DATABASE_ENV=local` and `LOCAL_DATABASE_URL`. Never switch silently or synchronize ad-hoc changes. Both environments are recreated from the same Alembic migrations and seeds; the final demo targets Supabase. Before major milestones export a backup, capture row counts and rehearse offline screenshots.""")

write("docs/adr/001-fastapi-authentication.md", """# ADR 001: Keep authentication in FastAPI

Status: accepted for v1.

FastAPI hashes passwords, creates/validates JWTs, checks resource ownership and stores users in PostgreSQL. React calls FastAPI auth endpoints. This demonstrates backend authentication, centralizes application rules, avoids mixing two identity systems and is easier to explain during course evaluation. Supabase Auth is a possible future enhancement, not part of v1. If implemented later, create a new ADR and identity/RLS migration; do not run both systems implicitly.
""")

write("docs/SUPABASE_SETUP_GUIDE.md", """# Supabase Setup Guide

Supabase is the managed host for the project's PostgreSQL database. The React UI still talks to FastAPI.

## Create and connect

1. Sign in to Supabase and create a project for RoamGenie.
2. Choose the nearest suitable region; record the decision.
3. Generate/store the database password in a password manager—never chat or GitHub.
4. Open the project Dashboard.
5. Open **Connect** or **Database settings** and locate PostgreSQL connection information.
6. Review the environment and choose an appropriate connection mode; do not guess.
7. Copy its PostgreSQL URI and change the scheme to `postgresql+psycopg://` for SQLAlchemy if necessary.
8. Copy `backend/.env.example` to `backend/.env`; place the URI in `DATABASE_URL`.
9. Run `python -m venv .venv`, activate it, then `pip install -r requirements.txt`.
10. Start FastAPI and call `GET http://127.0.0.1:8000/api/health`; expect `online/connected`.
11. Run `alembic current`, review pending migration, then `alembic upgrade head`.
12. Load version-controlled seeds using the Dashboard SQL Editor or `psql` with the approved URI.
13. Open Table Editor and verify tables, columns, keys and relationships.
14. Open SQL Editor and run version-controlled verification queries.
15. Test FastAPI APIs; never test application behavior by bypassing FastAPI.
16. Invite team members with the minimum required Supabase organization/project roles.
17. Share access through Supabase invitations/password manager, never source control/chat.
18. On failure check URL encoding, host, port, mode, IPv4/IPv6 support, project state and network; do not print the URI.
19. Reset only the named development project after backup and team approval, then replay migrations/seeds.
20. Before demo: apply reviewed migrations, seed safe data, run APIs/tests, export backup, capture Dashboard/SQL screenshots and freeze changes.

## Connection modes

- **Direct connection:** full PostgreSQL session; suitable when network supports it and for many administrative/migration operations.
- **Session pooler:** retains session behavior and is often compatible with migrations or long-running backend processes.
- **Transaction pooler:** efficient for serverless/short transactions but may not support session-dependent features or some migration operations.

Use the option currently recommended by the Supabase Dashboard for the deployment environment. Alembic and administrative SQL may require direct or session-compatible connections. Test before adopting a mode; record it without committing credentials.

## Dashboard demonstration

Table Editor: show users, destinations, hotels, restaurants, attractions, trips, itineraries/days/items, expenses, budget allocations and saved trips; point out keys/constraints and safe sample rows. SQL Editor: run a JOIN, aggregate budget query, view, function/procedure, trigger verification, rollback demonstration and index/`EXPLAIN`. Dashboard is a developer/admin/demo tool, never the React frontend.

## Optional local fallback

Set `DATABASE_ENV=local` and provide `LOCAL_DATABASE_URL` only in a local secret file. Run the same Alembic migrations and seed scripts. Local PostgreSQL is disposable and not synchronized truth. Switch back explicitly to `supabase` before integration/demo.
""")

write("database/MIGRATION_WORKFLOW.md", """# Schema and Migration Workflow

1. Samyuktha records and approves the design change.
2. Sashtika reviews required PostgreSQL objects and DDL ownership.
3. Yasmin updates SQLAlchemy models.
4. Create or hand-write: `alembic revision --autogenerate -m "describe change"`.
5. Review generated upgrade/downgrade—autogeneration is never trusted blindly.
6. Test on a safe empty/development database.
7. Check `alembic current`, `alembic history`, `alembic upgrade head`; test `alembic downgrade -1` when safe, then re-upgrade.
8. Apply the reviewed migration to Supabase using an appropriate direct/session connection.
9. Update course SQL scripts, dictionary, ERD, API/frontend contracts and status.
10. Run database/API/integration tests, capture Dashboard evidence, commit and merge.

Alembic owns application table evolution. Standalone SQL owns seed/demo queries and reviewed PostgreSQL objects not managed by ORM migration. Never create the same object independently in both paths.
""")

write("database/README.md", """# Supabase PostgreSQL Execution Order

## 1. Environment

Follow `docs/SUPABASE_SETUP_GUIDE.md`; put the Dashboard-recommended connection URI in backend-only `DATABASE_URL`. Confirm the target project before any mutation. Optional local PostgreSQL is selected explicitly and rebuilt identically.

## 2. Initial migration

From `backend`: `alembic current`, `alembic history`, review, then `alembic upgrade head`. Alembic is the main application schema mechanism. Do not also run `schema/001_schema.sql` against the same database unless the migration plan explicitly treats it as verification/bootstrap instead of duplicate ownership.

## 3–6. Course objects and verification

Run seeds, then views → functions → procedures → triggers → indexes. Use Supabase SQL Editor or compatible `psql`, saving every executed statement in Git. Run `queries/001_reports.sql` and `tests/001_constraints.sql`. Scripts must be PostgreSQL-compatible, purposeful and reasonably idempotent. SQL Editor execution alone is not completion.

## 7. Reset, backup and restore

Back up before major milestones. Reset only the confirmed development project with team approval; replay Alembic then seeds/objects. Restore into a safe test target, compare schema/version and row counts, and record evidence. Never commit database dumps or credentials; see `backups/README.md` and `MIGRATION_WORKFLOW.md`.
""")
write("database/backups/README.md", """# Backups

Penitta exports a Supabase PostgreSQL backup before major milestones using the currently supported Dashboard/CLI/`pg_dump` method and an appropriate connection. Store encrypted/off-repository; record date, migration revision and row counts. Restore only into an explicitly named safe test project/database, verify counts and API smoke tests, then destroy the test copy through an approved operation. Free-tier backup capabilities must be confirmed in the current project plan.
""")
write("database/backups/.gitkeep", "")

upsert("planning/GITHUB_WORKFLOW.md", "Database change workflow", """Schema PR sequence: design issue → Samyuktha approval → SQLAlchemy model → reviewed Alembic migration → related SQL → safe development test → upgrade/downgrade where practical → dictionary/API/frontend updates → PR with exact migration steps → apply after review → status update. Dashboard-only changes are forbidden.

Commit examples: `feat(database): configure Supabase PostgreSQL connection`; `feat(migrations): add initial travel schema`; `feat(sql): add itinerary reporting views`; `fix(database): correct trip foreign key`; `docs(supabase): add hosted PostgreSQL setup guide`; `test(database): verify Supabase constraints`; `chore(env): add safe database placeholders`.""")

upsert("planning/DEFINITION_OF_DONE.md", "Database Definition of Done", """A database task requires approved design; applicable SQLAlchemy model; reviewed Alembic migration; relevant SQL; successful migration; objects visible in Supabase; seed/test data; verified constraints; passing tests; updated dictionary/docs; no secrets; reviewed PR; FastAPI integration; relevant React behavior; captured evidence. A visible Dashboard table alone is not completion. The application flow must work.""")

upsert("TESTING_GUIDE.md", "Supabase PostgreSQL test matrix", """**Connection:** valid URL, invalid password/host, network/database unavailable, timeout and recovery; health response must never expose URI. **Migration:** empty→head, existing→latest, current/history, safe downgrade/re-upgrade and documented idempotency limits. **Schema/data:** tables/types/PK/FK/unique/check/cascade, repeatable seeds and valid relationships. **Security:** `.env` ignored; Git history contains no password/service role; no service role in frontend; unauthorized API and cross-user trip access fail; public table access is not enabled. **Backup:** export, restore safely, compare migration revision/row counts. **Presentation:** Dashboard/tables/SQL work and offline screenshots remain usable during an outage.""")

upsert("DEMO_GUIDE.md", "Supabase database demonstration", """Explain: “Supabase is our managed cloud platform for PostgreSQL. PostgreSQL is the DBMS. React calls FastAPI; FastAPI validates and uses SQLAlchemy to access it.” Show architecture → Dashboard core tables/FKs/sample rows → SQL Editor JOIN → aggregate budget query → view → function/procedure → trigger audit → transaction/index explanation → return to React full flow. Offline pack: database/SQL result/ERD/architecture/API/frontend screenshots and optional recording.""")

upsert("presentation/CONTENT_OUTLINE.md", "Supabase explanation", """State exactly: “Supabase is used as the managed cloud platform for our PostgreSQL database. PostgreSQL remains the actual relational DBMS. Supabase provides hosting, a visual table editor, SQL editor, logs, and administrative tools. Our React frontend does not directly access the database. It sends requests to FastAPI, and FastAPI performs validated database operations using SQLAlchemy.” Include the Dashboard-to-SQL-Editor-to-React demonstration from `DEMO_GUIDE.md`.""")
upsert("presentation/DEMO_FLOW.md", "Database sequence", """Open Dashboard → show core tables/FKs/rows → SQL Editor JOIN and aggregate → view → function/procedure → audit trigger → explain transaction/index → return to React and complete saved-itinerary flow. Use safe demo data and hide project URL/credentials. If internet fails, use numbered database/SQL/ERD/architecture/API/frontend screenshots or the approved recording.""")
upsert("presentation/EXPECTED_QUESTIONS.md", "Supabase viva answers", """- **Is Supabase another DBMS?** No; it hosts PostgreSQL, our relational DBMS.
- **Why Supabase?** Shared managed hosting, Dashboard, SQL Editor and logs reduce setup friction.
- **Does React connect directly?** No, it normally calls FastAPI only.
- **FastAPI/SQLAlchemy/Alembic?** API/business and authorization layer; ORM/session access; versioned schema evolution.
- **Why SQL files?** Reproducibility and DBMS demonstrations beyond ordinary ORM work.
- **What is RLS?** PostgreSQL row policies used when a client accesses exposed tables; FastAPI ownership is primary here.
- **Where are passwords?** Backend environment/secret manager, never Git or React.
- **Outage/backup?** Optional migration-built local fallback, exported backup and offline evidence.
- **How prevent cross-user reads?** Authenticated FastAPI ownership checks and tests; RLS before any approved direct access.""")

# Convert the most misleading local-primary phrases while preserving optional fallback instructions.
for path in ROOT.rglob("*.md"):
    if "node_modules" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    text = text.replace("PostgreSQL 15+", "Supabase project access (local PostgreSQL 15+ optional)")
    text = text.replace("test real PostgreSQL connectivity", "test Supabase PostgreSQL connectivity")
    text = text.replace("real PostgreSQL +", "Supabase PostgreSQL +")
    text = text.replace("against real PostgreSQL", "against Supabase PostgreSQL")
    path.write_text(text, encoding="utf-8")

role_data = {
"01-mercy-frontend-ui": ("Mercy", "React calls FastAPI only. Do not add the Supabase JavaScript client or any database/service-role credential. Use contract-matched mock API data while endpoints are pending. Dashboard is not the app UI; its screenshots are presentation evidence only."),
"02-yasmin-project-manager-backend": ("Yasmin", "Own the Supabase–FastAPI connection, SQLAlchemy engine/session, Alembic, environment setup, migration review, `/api/health`, integration tests, schema-change coordination and final secret review. Ensure FastAPI remains React's normal database access layer."),
"03-samyuktha-database-designer": ("Samyuktha", "Design PostgreSQL/Supabase-compatible schemas, record approval before implementation, review generated Alembic migrations against the ER model, confirm relationships in Dashboard and update the dictionary after every accepted migration. Never treat a manual Dashboard-only schema as delivered."),
"04-sashtika-sql-developer": ("Sashtika", "Keep all SQL PostgreSQL-compatible and versioned. Test scripts in Supabase SQL Editor or compatible psql and supply verification queries/results. SQL Editor execution alone is incomplete. Coordinate DDL ownership so Alembic does not duplicate standalone course objects."),
"05-madhu-ai-integration": ("Madhu", "AI calls backend services and receives validated structured records. It never receives Supabase credentials, executes arbitrary SQL, changes tables or invents trusted IDs. FastAPI validates referenced IDs and persists accepted output. Preserve mock mode."),
"06-penitta-database-administrator": ("Penitta", "Own Supabase project/team access, connection-mode guidance, environment/secret runbook, reviewed migration application, Dashboard/log monitoring, permissions, backup/restore/reset, index/performance verification and the demo database. Export before major milestones and maintain offline evidence."),
"07-eunice-backend-presentation": ("Eunice", "Test database connectivity and `/api/health`, verify records in Dashboard, capture Table Editor and SQL result evidence, and demonstrate React → FastAPI → Supabase PostgreSQL. Prepare offline database/ERD/architecture/API/frontend screenshots and an optional recording."),
}

milestones = """M0: create Supabase project, safe access, environment/connection choice and empty-database health check. M1: approve Supabase-compatible ERD, SQLAlchemy model plan, Alembic/SQL ownership and API fields. M2: run initial migration/seeds, verify Table Editor and complete React auth → FastAPI → Supabase. M3: seed/query/index catalogues and complete one DB→API→React module. M4: transactionally store trip/AI-validated itinerary/expenses, verify Dashboard and reopen in React. M5: test invalid URL/password/host, timeout/outage/recovery, migrations/missing table/constraints, cross-user authorization, public exposure, secret scan, backup/restore and fresh recreation. M6: export backup and demonstrate tables, JOIN, aggregate, view, routine, trigger, transactions/indexes and complete React flow with offline evidence."""

for slug, (person, rule) in role_data.items():
    base = f"team/{slug}"
    upsert(f"{base}/README.md", "Supabase responsibility", rule)
    upsert(f"{base}/ROLE_SCOPE.md", "Supabase boundary", rule)
    upsert(f"{base}/START_HERE.md", "Updated architecture", f"Primary path: React → FastAPI → SQLAlchemy → Supabase-hosted PostgreSQL. {rule} Before starting, read `../../docs/SUPABASE_SETUP_GUIDE.md` and confirm the relevant contract/migration status.")
    upsert(f"{base}/SETUP_GUIDE.md", "Supabase setup", f"{rule}\n\nNever commit `.env`. Copy the relevant example, obtain access safely, and verify `GET /api/health`. Backend/database work runs `alembic current`, reviews migration, then `alembic upgrade head`. Use the Dashboard-recommended direct/session/transaction connection for the task; migration work may require direct or session compatibility. Optional local PostgreSQL uses the same migrations/seeds and is explicitly selected—not synchronized truth.")
    upsert(f"{base}/MILESTONE_TASKS.md", "Supabase milestones", milestones + "\n\nRole focus: " + rule)
    upsert(f"{base}/INTEGRATION_GUIDE.md", "Supabase integration", f"{rule}\n\nVerify the owned feature through Supabase object → SQLAlchemy/repository → service → FastAPI → React and attach migration/seed/test plus Dashboard evidence. Do not accept manual Dashboard state as integration.")
    upsert(f"{base}/TESTING_GUIDE.md", "Supabase testing", f"{rule}\n\nTest the relevant valid connection, invalid credentials/host, network outage/timeout/recovery, migration/schema/seed constraints, unauthorized and cross-user access, and offline demo fallback. Never print connection strings. Record target environment, Alembic revision, expected/actual result and evidence.")
    upsert(f"{base}/DELIVERABLE_CHECKLIST.md", "Supabase completion", "- [ ] Primary flow uses FastAPI and Supabase PostgreSQL.\n- [ ] Applicable design/model/migration/SQL ownership agrees.\n- [ ] Constraints, API behavior and relevant UI pass.\n- [ ] No `.env`, password, project URL or service-role key is committed/exposed.\n- [ ] Dashboard plus offline evidence is captured.\n- [ ] Reviewed PR documents migration/rollback and updates status.")
    upsert(f"{base}/CODEX_PROMPT.md", "Mandatory Supabase context", f"The primary database is PostgreSQL hosted by Supabase; Supabase is not a separate DBMS. React normally calls FastAPI only. FastAPI uses SQLAlchemy/psycopg with backend-only `DATABASE_URL`; Alembic is the application schema migration mechanism; version-controlled PostgreSQL scripts demonstrate course objects. Dashboard is admin/demo tooling and manual changes must be reproduced in Git. FastAPI auth/JWT remains v1; do not introduce Supabase Auth. Never expose database passwords, full URLs or service-role keys; no service-role value may enter `VITE_*`. RLS is required before any explicitly approved direct frontend table access, but FastAPI ownership checks remain primary. {rule} Inspect existing files first, preserve working code, state assumptions/conflicts, use safe placeholders, run relevant Supabase/migration/fallback tests and return exact paths, commands, evidence, commit and PR steps.")

upsert("PROJECT_STATUS.md", "Supabase migration status", """Architecture decision accepted: Supabase-hosted PostgreSQL is the primary shared/demo database; FastAPI auth/access remains. Documentation/environment/connection/Alembic starters updated. Pending team evidence: create project/access; choose connection mode; configure secret `DATABASE_URL`; run initial migration; validate `/api/health`; verify tables/seeds; backup/restore; confirm free-tier limits. Do not mark M0 complete until the empty-database connection gate passes.""")
upsert("planning/MASTER_PROJECT_PLAN.md", "Supabase milestone gates", milestones)
upsert("planning/MILESTONE_TIMELINE.md", "Supabase timeline update", milestones)
upsert("planning/TEAM_RESPONSIBILITY_MATRIX.md", "Supabase ownership update", "Yasmin owns connection/SQLAlchemy/Alembic/health; Samyuktha design and migration review; Sashtika versioned PostgreSQL course SQL; Penitta project access/migrations/backups/Dashboard/performance; Mercy FastAPI-only client; Madhu backend-only structured AI; Eunice connectivity/Dashboard/SQL/demo evidence. Each database feature requires relevant cross-review.")
upsert("planning/DEPENDENCY_MATRIX.md", "Supabase dependencies", "Yasmin and Penitta need the selected Dashboard connection mode and secret delivery. Migrations wait for Samyuktha design approval and Sashtika DDL-ownership review. Mercy waits for FastAPI contracts, never database access. Madhu waits for backend-provided structured records. Eunice waits for migrated/seeded Supabase data and stable APIs.")
upsert("planning/INTEGRATION_CALENDAR.md", "Supabase checkpoints", "M0: empty Supabase DB health. M1: ERD/ORM/migration/SQL ownership review. M2: auth persisted and visible in Table Editor. M3: catalogue DB→API→React plus SQL/index evidence. M4: transactional itinerary save/reopen plus Dashboard verification. M5: outage/security/fresh recreation/restore. M6: online and offline database demo rehearsal.")

risk_rows = """| Supabase internet dependency | M | H | mock/offline plan and early checks | Penitta | optional migration-built local DB + screenshots |
| Incorrect connection string | M | H | Dashboard copy, URL encode, health check | Yasmin | rotate/reissue and use documented mode |
| Pooling incompatibility | M | H | test direct/session/transaction needs | Penitta | use direct/session-compatible migration URI |
| Service-role exposure | L | Critical | keep backend-only/unused, secret scan | Yasmin | revoke immediately and inspect history |
| Dashboard change missing from Git | M | H | no manual completion; PR gate | Samyuktha | reproduce migration/SQL then reset drift |
| Alembic/SQL DDL conflict | M | H | explicit object ownership | Yasmin/Sashtika | rebuild safe dev DB from reviewed source |
| Free-tier limit/pause | M | M | confirm current plan and activity | Penitta | export backup/local demo fallback |
| Migration mismatch | M | H | current/history in PR and status | Yasmin | reconcile revisions before integration |
| Public table exposure | L | Critical | exposure/permissions review | Penitta | disable access, rotate keys, investigate |
| Missing RLS after direct access | L | Critical | architecture review and policy tests | Yasmin | remove direct access until policies pass |
| Network demo failure | M | H | rehearsal and offline pack | Eunice | screenshots/API samples/recording/local fallback |"""
upsert("planning/RISK_REGISTER.md", "Supabase risks", risk_rows)

upsert("SUBMISSION_CHECKLIST.md", "Supabase release checks", "- [ ] Supabase project contains only reviewed migrations/SQL and safe demo rows.\n- [ ] `alembic current` is expected head; fresh recreation from migrations/seeds passes.\n- [ ] React accesses data only through FastAPI.\n- [ ] No credentials/project-specific URLs/service-role keys exist in repository or frontend build.\n- [ ] Backup/restore and outage fallback evidence is current.\n- [ ] Dashboard/SQL demonstration and complete app flow are rehearsed.")
upsert("WORKSPACE_REPORT.md", "Supabase architecture modification", "Existing workspace updated in place: hosted PostgreSQL decision, environment templates, backend connection/health, Alembic workflow, dashboard/RLS/auth guidance, milestones, roles, tests, risks and presentation. Original SQL/course planning remains and local PostgreSQL is retained only as optional isolated fallback.")

print("Supabase workspace update applied.")
