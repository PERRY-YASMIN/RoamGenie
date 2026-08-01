"""Generate the documentation-heavy RoamGenie student workspace.

Run from the repository root with: python scripts/setup/generate_workspace.py
Existing files are not overwritten unless --force is supplied.
"""
from __future__ import annotations

import argparse
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def write(path: str, content: str, force: bool = False) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not force:
        return
    target.write_text(content.strip() + "\n", encoding="utf-8")


def common_commands(area: str, branch: str) -> str:
    test = {
        "frontend": "cd frontend\nnpm install\nnpm run lint\nnpm test -- --run\nnpm run build",
        "backend": "cd backend\npython -m venv .venv\n.\\.venv\\Scripts\\Activate.ps1\npip install -r requirements.txt\npytest",
        "database": "psql -U roamgenie_app -d roamgenie -f database/schema/001_schema.sql\npsql -U roamgenie_app -d roamgenie -f database/tests/001_constraints.sql",
        "ai": "cd backend\n.\\.venv\\Scripts\\Activate.ps1\npytest ../tests/ai",
        "presentation": "cd backend\npytest ../tests/backend ../tests/integration",
    }[area]
    return f"""```powershell
git switch develop
git pull origin develop
git switch -c {branch}
{test}
git status
git add <owned-files>
git commit -m \"feat({area}): describe completed work\"
git push -u origin {branch}
```

Open a pull request into `develop`. Include summary, changed files, commands/results,
screenshots when visual, known limits, and the linked issue. Never commit `.env`."""


roles = [
    dict(slug="01-mercy-frontend-ui", name="MERCY JOICE J", title="Frontend/UI Designer", area="frontend", branch="frontend/mercy",
         owned="`frontend/`, `tests/frontend/`, frontend screenshots", may="API contract comments and frontend sections of docs", blocked="database schema, backend routes, SQL and AI service code without owner approval",
         modules="responsive UI, routing, forms, dashboard, API client, loading/empty/error states",
         inputs="approved API contract from Yasmin, field names from Samyuktha, AI response schema from Madhu",
         outputs="14 routed screens, reusable components, validation, API integration, responsive evidence",
         setup="cd frontend; npm install; Copy-Item .env.example .env; npm run dev",
         order="Create shell/routes → shared components → auth pages → trip form → catalogue pages → itinerary/budget → saved trips/assistant → responsive polish",
         tests="Run `npm run lint`, `npm test -- --run`, and `npm run build`; manually check 360px, 768px, and 1440px widths plus Chrome/Edge.",
         evidence="landing, login errors, trip validation, loading/empty/error states, itinerary, budget warning, saved trip, assistant, mobile menu",
         milestone="M1 wireframes/contracts; M2 shell/auth; M3 catalogues; M4 trip/AI/budget; M5 tests/polish; M6 screenshots",
         specifics="Routes: `/`, `/register`, `/login`, `/profile`, `/plan`, `/destinations`, `/hotels`, `/restaurants`, `/attractions`, `/itineraries/:id`, `/budget/:tripId`, `/saved`, `/assistant`, and `*`. Keep API calls in `src/services/api.js`; never call PostgreSQL. Validate required locations, future dates, travellers > 0, and budget > 0."),
    dict(slug="02-yasmin-project-manager-backend", name="SHAIK YASMIN", title="Project Manager & Backend Developer", area="backend", branch="backend/yasmin",
         owned="root/planning documents, `backend/`, integration tests and release coordination", may="all modules during reviewed integration", blocked="another member's active feature without discussion; history rewriting on shared branches",
         modules="FastAPI setup, auth, users, catalogues, trips, itineraries, budgets, saved trips, AI endpoints, final integration",
         inputs="approved schema from Samyuktha/Sashtika, AI contract from Madhu, frontend needs from Mercy",
         outputs="versioned validated API, JWT auth, service/repository boundaries, tests, reviewed milestone merges",
         setup="cd backend; python -m venv .venv; .\\.venv\\Scripts\\Activate.ps1; pip install -r requirements.txt; Copy-Item ..\\.env.example .env; uvicorn app.main:app --reload",
         order="Triage board daily → freeze contracts → config/database → auth → one destination vertical slice → remaining catalogues → trips/budget → itinerary/save → AI/weather → integration tests",
         tests="Run `pytest`; inspect `/docs`; test 401/403/404/422 paths and full register-to-reopen journey.",
         evidence="issue board, API docs, passing test output, auth flow, full journey, review approvals, milestone tags",
         milestone="M0 governance; M1 contracts; M2 auth/database; M3 CRUD; M4 trip/AI; M5 release candidate; M6 final merge/tag",
         specifics="Daily: review blockers, PRs, contracts, status, and next checkpoint. End milestones only after fresh-clone smoke test. Endpoints use `/api/v1`; routers call services, services use repositories, and response schemas never expose password hashes."),
    dict(slug="03-samyuktha-database-designer", name="SAMYUKTHA KUMARAN", title="Database Designer", area="database", branch="database-design/samyuktha",
         owned="`database/design/`, `docs/data-dictionary.md`, ERD and normalization", may="schema review notes", blocked="executable production SQL or migrations without Sashtika/Yasmin review",
         modules="conceptual model, entities, cardinality, keys, constraints, relational schema, normalization",
         inputs="requirements and API data needs", outputs="reviewed Mermaid ERD, relational schema, 1NF→2NF→3NF/BCNF analysis, data dictionary and handoff",
         setup="code database/design/er-diagram.md; code docs/data-dictionary.md",
         order="Identify facts → separate entities → choose stable keys → draw cardinalities → list constraints → normalize → review API fields → freeze v1 → hand off",
         tests="Trace every foreign key; test optionality/deletion rules on paper; ask Sashtika to execute DDL and Penitta to review operations.",
         evidence="rendered ERD, normalization table, reviewed dictionary, signed schema-v1 checkpoint",
         milestone="M1 design/freeze; M2 implementation validation; M3 controlled refinements; M4 final ERD; M5 consistency audit; M6 viva evidence",
         specifics="Core entities: users, user_preferences, destinations, hotels, restaurants, attractions, transport_options, trips, trip_members, itineraries, itinerary_days, itinerary_items, expenses, budget_allocations, saved_trips, reviews, AI conversations/messages, weather_snapshots, packing_items, activity_preferences. Record PK, FK, nullability, domain, default, unique/check rules and delete behavior."),
    dict(slug="04-sashtika-sql-developer", name="SASHTIKA S", title="SQL Developer", area="database", branch="sql/sashtika",
         owned="`database/schema`, `seeds`, `queries`, `views`, `functions`, `procedures`, `triggers`, `indexes`, `transactions`, `reports`, `tests`", may="data dictionary corrections through review", blocked="ER model or ORM migrations without Samyuktha/Yasmin approval",
         modules="PostgreSQL DDL/DML, sample data, 15+ queries, joins, views, routines, purposeful triggers, transactions, indexes, reports",
         inputs="frozen relational schema from Samyuktha", outputs="idempotent ordered SQL scripts, realistic seed data, verified result notes and DBMS demonstrations",
         setup="cd backend; Copy-Item .env.example .env; alembic current; alembic upgrade head",
         order="DDL/constraints → seed data → 15 queries → views → functions/procedure → useful audit/total trigger → transactions → indexes → verification",
         tests="Run scripts on an empty database; run `database/tests/001_constraints.sql`; use `EXPLAIN ANALYZE` before/after indexes.",
         evidence="clean execution log, query outputs, constraint failures, transaction rollback, EXPLAIN output",
         milestone="M1 DDL mapping; M2 schema/seeds; M3 queries/views; M4 routines/triggers/transactions; M5 clean replay; M6 SQL demo",
         specifics="Use snake_case, singular migration sequence, explicit columns, parameterized application queries, and comments stating purpose. Rules: positive budget/travellers; valid dates; rating 0–5; nonnegative expenses; safe child deletes; auditable important changes. Do not add decorative triggers."),
    dict(slug="05-madhu-ai-integration", name="MADHUVARSHINI A", title="AI Integration Engineer", area="ai", branch="ai/madhu",
         owned="`ai/`, AI schemas/services/tests and AI contract docs", may="backend AI adapter/router with Yasmin review", blocked="raw database credentials, direct database writes, unrelated backend/frontend code",
         modules="provider abstraction, prompts, structured itinerary/recommendations/Q&A/packing, validation, timeouts, retry and mock fallback",
         inputs="validated trip DTO plus selected database records and weather snapshot", outputs="validated provider-independent JSON; deterministic no-key mock; malformed/timeout tests",
         setup="$env:AI_PROVIDER='mock'; cd backend; .\\.venv\\Scripts\\Activate.ps1; pytest ../tests/ai",
         order="Freeze JSON schema → write mock → prompts → provider interface → timeout/retry → validation → fallback → endpoint contract tests",
         tests="Test valid JSON, invalid JSON, missing fields, timeout, missing key, empty preferences, invalid destination, unrealistic budget and unknown IDs.",
         evidence="sample request/response, mock output, fallback test, validation failure, sanitized logs",
         milestone="M1 use cases/schemas; M2 mock; M3 structured recommendation context; M4 real adapter/fallback; M5 failure tests; M6 AI explanation",
         specifics="AI never executes SQL, invents database IDs, or persists data. Backend supplies allow-listed records. Validate response before returning. One retry only for transient failures; short timeout; fall back to mock. Keys belong only in environment variables."),
    dict(slug="06-penitta-database-administrator", name="PENITTA A", title="Database Administrator (DBA)", area="database", branch="dba/penitta",
         owned="database operational scripts, roles/permissions, backup/restore/runbooks, performance evidence", may="migration review and `.env.example` database variables", blocked="logical schema changes without Samyuktha/Sashtika approval; real credentials in Git",
         modules="PostgreSQL setup, databases/roles, least privilege, migration runs, backups/restores, index checks and security",
         inputs="approved SQL from Sashtika and migrations from Yasmin", outputs="repeatable local setup, app/read-only roles, backup/restore proof, migration log and performance review",
         setup="cd backend; Copy-Item .env.example .env; alembic current; alembic upgrade head; Invoke-RestMethod http://127.0.0.1:8000/api/health",
         order="Install/version check → roles/database → environment → schema/migrations → seed → connection → permissions → backup/restore drill → index/performance review",
         tests="Connect as app and read-only users; verify denied writes for read-only; restore into a separate `roamgenie_restore_test` database; compare row counts.",
         evidence="version, role privileges, migration log, backup file metadata, restored row counts, EXPLAIN results",
         milestone="M1 environment/role plan; M2 live DB/reset; M3 index review; M4 migration and restore; M5 security/performance; M6 demo backup",
         specifics="Use the Dashboard-recommended Supabase PostgreSQL connection in backend-only `DATABASE_URL`. Document pooler compatibility, grant minimum access, and never commit dumps or credentials. Back up before an approved reset."),
    dict(slug="07-eunice-backend-presentation", name="EUNICE MERCY M", title="Backend & Presentation Coordinator", area="presentation", branch="backend-presentation/eunice",
         owned="assigned catalogue API support, API tests/docs, `presentation/`, demo evidence", may="backend catalogue routers/schemas assigned in an issue", blocked="auth/core trip logic, schema, or another member's slides without review",
         modules="destination/hotel/restaurant/attraction route support, contract/error testing, slides, screenshots, demo and viva coordination",
         inputs="assigned API contract and stable integrated builds", outputs="tested support endpoints, issue log, presentation outline, speakers, live/backup demo and viva pack",
         setup="cd backend; .\\.venv\\Scripts\\Activate.ps1; uvicorn app.main:app --reload; Start-Process http://127.0.0.1:8000/docs",
         order="Confirm assigned routes → add schema/service tests → log mismatches → update API docs → collect milestone evidence → rehearse timed demo → prepare backup",
         tests="Test success plus 401/404/422/500-safe responses in `/docs`; run integration tests; rehearse demo twice on a clean setup.",
         evidence="API test results, architecture/ERD/UI screenshots, timed script, speaker sheet, backup screenshots/video location",
         milestone="M1 presentation/API test plan; M2 auth evidence; M3 CRUD contract tests; M4 journey demo; M5 rehearsal; M6 delivery",
         specifics="Slides cover problem, existing/proposed system, architecture, database and normalization, modules, DBMS features, AI boundaries, test results, demo, limitations and future work. Demo order: register → login → plan → generate → budget → save → reopen."),
]


def generate_role(role: dict, force: bool) -> None:
    base = f"team/{role['slug']}"
    completion = "Code/docs exist; required tests pass; no secrets; contracts match; evidence is attached; reviewed PR is merged to `develop`; `PROJECT_STATUS.md` and progress log are updated."
    readme = f"""# {role['name']} — {role['title']}

## Responsibility

- Primary responsibility: {role['modules']}.
- Modules owned: {role['modules']}.
- Files owned: {role['owned']}.
- May modify: {role['may']}.
- Do not modify without approval: {role['blocked']}.
- Dependencies: {role['inputs']}.
- Expected deliverables: {role['outputs']}.
- Testing responsibility: {role['tests']}
- Integration responsibility: demonstrate the owned slice against `develop`, document contract mismatches, and support its reviewer.
- Branch: `{role['branch']}`.
- Pull request: target `develop`; link issue; list tests, evidence, limitations; obtain one relevant review and Yasmin's integration approval.
- Complete when: {completion}
"""
    write(f"{base}/README.md", readme, force)
    write(f"{base}/ROLE_SCOPE.md", f"""# Role Scope

## Own

{role['owned']}.

## Coordinate

- Inputs: {role['inputs']}.
- Outputs: {role['outputs']}.
- Must not change: {role['blocked']}.
- Escalate contract conflicts to Yasmin before coding past the conflict.
""", force)
    write(f"{base}/START_HERE.md", f"""# Start Here

1. **Build:** {role['modules']}.
2. **Why:** this supplies the project's {role['title'].lower()} deliverable and a tested link in the database → API → UI flow.
3. **Inputs:** {role['inputs']}.
4. **Outputs:** {role['outputs']}.
5. **Setup:** run `{role['setup']}` from the repository root (PowerShell).
6. **Implementation order:** {role['order']}.
7. **Testing:** {role['tests']}
8. **Git:** use the commands in `GITHUB_GUIDE.md` on `{role['branch']}`.
9. **Evidence:** {role['evidence']}.
10. **Final connection:** integrate the owned output on `develop`; the feature is incomplete until its upstream and downstream contracts both work.
""", force)
    write(f"{base}/SETUP_GUIDE.md", f"""# Setup Guide

## Preconditions

Git, VS Code, Supabase project access (local PostgreSQL optional), Python 3.11+, and Node 20+ are available. Clone the repository and copy `.env.example` to `.env`; never commit `.env`.

## Commands

```powershell
git clone <repository-url> RoamGenie
cd RoamGenie
git switch develop
git pull origin develop
git switch -c {role['branch']}
{role['setup']}
```

Expected: commands complete without secrets in output. If a contract/file is missing, record an issue and wait for its owner instead of inventing it.
""", force)
    write(f"{base}/MILESTONE_TASKS.md", f"""# Milestone Tasks

{role['milestone']}.

At each milestone: pull `develop` → complete issue → run owned tests → test the integration boundary → attach evidence → PR to `develop` → resolve review → update progress log. Do not begin work that relies on an unfrozen contract.
""", force)
    write(f"{base}/FILE_OWNERSHIP.md", f"""# File Ownership

- **Own:** {role['owned']}.
- **Modify after coordination:** {role['may']}.
- **Approval required:** {role['blocked']}.
- Generated files, dependency locks, and shared contracts require owner review.
- When two branches touch the same file, agree on one editor and cherry-pick or rebase after review.
""", force)
    write(f"{base}/IMPLEMENTATION_GUIDE.md", f"""# Implementation Guide

## Order

{role['order']}.

## Role rules

{role['specifics']}

For every increment: define input/output and errors → implement smallest slice → test valid/invalid input → integrate with one adjacent layer → document result → commit. Mark unfinished production paths with `TODO` and never claim a template is complete.
""", force)
    write(f"{base}/CODE_GUIDE.md", f"""# Code Guide

{role['specifics']}

- Prefer small named functions and consistent snake_case (Python/SQL) or camelCase (JavaScript).
- Validate at boundaries; log context without credentials or personal data.
- Keep configuration in environment variables documented in `.env.example`.
- Preserve working code. Stop and report overlapping or conflicting changes.
""", force)
    write(f"{base}/TESTING_GUIDE.md", f"""# Testing Guide

## Preconditions

Install dependencies, copy `.env.example`, use mock AI, and load demo seed data where needed.

## Run and verify

{role['tests']}

Input one valid, boundary, and invalid case. Expected: valid succeeds; boundary obeys contract; invalid returns a clear safe error. A failure means this work is not ready for handoff. Save terminal output/screenshots and record the responsible owner: {role['name']}.
""", force)
    write(f"{base}/INTEGRATION_GUIDE.md", f"""# Integration Guide

1. Confirm request fields, response fields, types, optionality, errors, and tables.
2. Pull `develop` and run baseline tests.
3. Integrate only the smallest owned vertical slice.
4. Check valid, invalid, unauthorized, empty, and dependency-failure cases.
5. Notify upstream/downstream owners of contract changes; do not silently rename fields.
6. Attach {role['evidence']}.
7. Merge only after tests and relevant review pass.
""", force)
    write(f"{base}/GITHUB_GUIDE.md", f"# GitHub Guide\n\n{common_commands(role['area'], role['branch'])}\n", force)
    write(f"{base}/DELIVERABLE_CHECKLIST.md", f"""# Deliverable Checklist

- [ ] Owned work exists: {role['outputs']}.
- [ ] Valid, invalid, and dependency-failure cases pass.
- [ ] No secret or personal data is committed.
- [ ] Contracts and documentation match code.
- [ ] Evidence attached: {role['evidence']}.
- [ ] PR targets `develop`, links issue, and has relevant review.
- [ ] Progress/status updated and integration demonstrated.
""", force)
    write(f"{base}/COMMON_ERRORS.md", f"""# Common Errors

- **Out-of-date branch:** commit/stash owned work, fetch, then rebase or merge `origin/develop` on the feature branch.
- **Contract mismatch:** stop; compare the frozen contract; open an issue tagging both owners.
- **Missing environment variable:** add its name and safe example to `.env.example`; never add the value.
- **Dependency unavailable:** use documented mock/fixture; do not hide the failure.
- **Test passes alone but not integrated:** reproduce against `develop` and record request, response, logs, and responsible boundary.
- **Ownership conflict:** do not delete either change; ask Yasmin to assign the merge owner.
""", force)
    write(f"{base}/VIVA_PREPARATION.md", f"""# Viva Preparation

Be ready to explain: your role; one owned file; its input/output; one validation rule; one failed test you fixed; one dependency; one security control; and how your work reaches PostgreSQL/API/UI without bypassing layers.

Role question: Why is **{role['modules']}** separated from other modules? Demonstrate with {role['evidence']}.
""", force)
    prompt = f"""# Codex Prompt — {role['name']}

You are assisting the **AI Travel Planner & Budget Optimizer (RoamGenie)**, a DBMS course web application. It registers users; stores profiles, destinations, hotels, restaurants, attractions, transport and trips; creates day-wise itineraries; allocates budgets and warnings; saves plans; provides weather/packing help; and uses validated AI through a provider-independent service with mock fallback. Stack: React/Vite, FastAPI/Pydantic/SQLAlchemy/Alembic/JWT, PostgreSQL, pytest. Frontend never connects to PostgreSQL; AI never runs SQL or writes directly to the database.

I am **{role['name']}, {role['title']}**. My milestones are: {role['milestone']}. My owned work is {role['owned']}. I may modify {role['may']}. Do not modify {role['blocked']} without explicit owner approval.

First inspect the complete repository, Git status, existing architecture, contracts, and tests. Before coding, state concise assumptions, files to create/modify, dependencies, risks, and conflicts. Preserve working code. If ownership/contracts conflict, stop and report the conflict; never delete or replace working code to bypass it.

Implement complete, runnable source code for the assigned current milestone, using exact repository file paths. Keep incomplete future work clearly marked `TODO`. Put every configurable value name in `.env.example`; never hard-code passwords, secrets, tokens, API keys, or private URLs. Validate all input, handle errors safely without exposing stack traces, keep modules small, and follow current contracts. {role['specifics']}

Return: (1) files created/modified, (2) simple explanation, (3) exact setup/run/test commands, (4) sample valid and invalid inputs with expected outputs, (5) integration instructions and dependency handoffs, (6) completion checklist, (7) suggested Conventional Commit message, and (8) pull-request instructions targeting `develop`. Run relevant tests and report actual results; do not say production-ready if templates or TODOs remain.
"""
    write(f"{base}/CODEX_PROMPT.md", prompt, force)
    write(f"{base}/PROGRESS_LOG.md", f"""# Progress Log — {role['name']}

| Date | Milestone/issue | Work completed | Files | Tests/evidence | Blocker/dependency | PR/status | Next action |
|---|---|---|---|---|---|---|---|
| YYYY-MM-DD | M0 / # | Workspace reviewed | — | setup check | none | planned | claim first issue |
""", force)


ROOT_DOCS = {
"README.md": """# RoamGenie — AI Travel Planner & Budget Optimizer

RoamGenie is a DBMS course project that turns trip dates, travellers, budget and preferences into a saved day-wise itinerary with category costs, warnings, weather context and packing suggestions.

## Status

This repository is an **implementation starter**, not a production release. Architecture, contracts, PostgreSQL examples, team handbooks, and runnable FastAPI/React starter shells are included. Catalogue, full authentication, persistence and real AI remain milestone work; mock AI is the default.

## Quick start (PowerShell)

```powershell
Copy-Item .env.example .env
cd backend
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` and API docs at `http://127.0.0.1:8000/docs`. The health endpoint and mock itinerary work without PostgreSQL or an AI key. See `docs/12-deployment-plan.md` for database setup.

## Read next

- New team member: `team/<your-folder>/START_HERE.md`
- Requirements: `REQUIREMENTS.md`
- Architecture: `ARCHITECTURE.md`
- Milestones: `planning/MASTER_PROJECT_PLAN.md`
- Integration: `INTEGRATION_GUIDE.md`
- Tests: `TESTING_GUIDE.md`
- Demo/submission: `DEMO_GUIDE.md`, `SUBMISSION_CHECKLIST.md`
""",
"REPOSITORY_AUDIT.md": """# Repository Audit — 2026-08-01

## Existing state

`RoamGenie/` contained only `.git`; it had no tracked files, manifests, application modules, branches visible to the sandbox, or documentation. Therefore there was no fixed stack or working code to replace.

The parent `../docs/` folder contains PDFs, a PowerPoint, images/screenshots and three SQL-related files. They are evidence/reference assets outside the target Git repository and were preserved unchanged. They were not copied because their provenance and desired versioning need team confirmation.

## Stack selected

React/Vite/JavaScript frontend; FastAPI/Pydantic/SQLAlchemy/Alembic backend; PostgreSQL; JWT/bcrypt during M2; provider-independent AI with deterministic mock; pytest and Vitest.

## Missing/incomplete

All production features were initially missing. This scaffold supplies documentation and safe starters only. Authentication, complete ORM model, all CRUD routes, migrations, full UI, production AI provider and deployment remain scheduled work.

## Conflicts and preservation

No working code conflicts exist. Do not overwrite parent course artifacts. Before importing their SQL, compare it with the approved schema and record provenance. Git reported a safe-directory ownership warning under the sandbox; team members using their normal accounts should confirm `git status` before changing global Git configuration.
""",
"REQUIREMENTS.md": """# Requirements

## Functional

FR-01 register/login/logout and protected profile; FR-02 manage preferences; FR-03 browse/filter destinations, hotels, restaurants, attractions and transport; FR-04 create/edit/delete trips; FR-05 validate dates, travellers and budget; FR-06 generate a day-wise itinerary from approved records; FR-07 allocate and total category costs; FR-08 warn on deficit; FR-09 save/reopen itinerary history; FR-10 AI recommendations/Q&A/packing with mock fallback; FR-11 weather with fallback; FR-12 admin-safe catalogue management; FR-13 reports demonstrating SQL concepts; FR-14 auditable important changes.

## Non-functional

- Security: hashed passwords, JWT expiry, least privilege, input validation, no secrets/stack traces.
- Reliability: mock fallbacks; transactions for multi-step saves; backups tested.
- Performance: paginated lists; indexes verified with plans; target common API response under 2 s locally excluding external AI.
- Usability: responsive at 360/768/1440 px; accessible labels/keyboard focus; understandable errors.
- Maintainability: layered modules, migrations, contract versioning, small reviewed PRs.
- Portability: documented Windows PowerShell setup; environment-driven URLs.
- Data integrity: PostgreSQL PK/FK/unique/check constraints and UTC timestamps.
- Testability: unit, database, integration and acceptance commands run from a clean clone.

Out of scope for v1: bookings/payments, live navigation, visa guarantees, autonomous purchases, AI database access, and production-scale availability.
""",
"ARCHITECTURE.md": """# Architecture

```mermaid
flowchart LR
  U[React browser] -->|HTTPS JSON /api/v1| A[FastAPI routers]
  A --> V[Pydantic validation/auth]
  V --> S[Services]
  S --> R[SQLAlchemy repositories]
  R --> P[(PostgreSQL)]
  S --> G[AI gateway]
  G --> M[Mock provider]
  G -. optional .-> X[External AI]
  S --> W[Weather adapter/mock]
```

Routes validate transport data. Services own business rules. Repositories alone access PostgreSQL. The AI gateway receives validated trip data plus allow-listed database records, returns schema-validated JSON, and never writes data. The backend transactionally saves accepted plans. React uses one API client and route-level loading/empty/error states.

Deployment units: static frontend, FastAPI process, PostgreSQL, and optional external providers. Configuration comes from environment variables. See `docs/06-system-architecture.md`, `docs/08-api-design.md`, and `docs/09-ai-integration-design.md`.
""",
"CONTRIBUTING.md": """# Contributing

Start from `develop`, use the branch in your team README, claim an issue, and make small Conventional Commits. Do not commit `.env`, dumps containing personal data, generated build folders, or credentials. Run owned tests, update docs/status, and open a PR to `develop` with summary, files, test output, screenshots, limitations and issue link. One relevant teammate reviews; Yasmin performs final integration review. See `planning/GITHUB_WORKFLOW.md` and `planning/DEFINITION_OF_DONE.md`.
""",
"PROJECT_STATUS.md": """# Project Status

Updated: 2026-08-01

| Milestone | Status | Exit evidence | Owner |
|---|---|---|---|
| M0 initialization | In progress | workspace scaffold created; two-system setup and GitHub board pending | Yasmin |
| M1 contracts/design | Not started | schema/API/UI/AI v1 freeze | All |
| M2 foundation/auth | Not started | PostgreSQL + auth + UI smoke test | Yasmin |
| M3 core data | Not started | destination vertical slice then catalogues | Yasmin |
| M4 trip/AI/budget | Not started | full saved journey | All |
| M5 hardening | Not started | RC tests/security/restore | All |
| M6 submission | Not started | clean demo, main merge, v1.0.0 | Yasmin/Eunice |

Use each member's `PROGRESS_LOG.md` for work detail. Update this table only with evidence links/PR numbers.
""",
"CHANGELOG.md": """# Changelog

## Unreleased

### Added

- Project audit, architecture, requirements, milestone and integration handbooks.
- Seven role-specific workspaces and standalone Codex prompts.
- FastAPI, React/Vite, PostgreSQL and mock-AI implementation starters.

No production release has been made.
""",
"INTEGRATION_GUIDE.md": """# Integration Guide

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
""",
"TESTING_GUIDE.md": """# Testing Guide

Use `.env` with `AI_PROVIDER=mock` and a dedicated test database. Never point destructive tests at demo/production data.

| Area | Preconditions | Command | Input/expected | Failure owner |
|---|---|---|---|---|
| Backend | venv/deps | `cd backend; pytest` | valid + invalid API; expected 2xx/4xx, no trace | endpoint owner |
| Database | empty test DB | `psql -v ON_ERROR_STOP=1 -d roamgenie_test -f database/tests/001_constraints.sql` | invalid constraints rejected | Sashtika/Penitta |
| Frontend | npm deps | `cd frontend; npm test -- --run; npm run build` | routes/forms/states render | Mercy |
| AI | mock mode | `cd backend; pytest ../tests/ai` | valid/malformed/timeout/no-key/fallback | Madhu |
| Integration | services ready | `cd backend; pytest ../tests/integration` | register→login→trip→generate→budget→save→retrieve/edit/delete/logout | Yasmin/Eunice |

Also verify configuration, auth/authorization, CRUD, validation, error safety, foreign keys, seeds, views, routines, triggers, transactions, indexes, backup/restore, responsive layouts, protected routes, empty/error states, unrealistic budget and empty preferences. Record test input, expected/actual result, environment, commit and evidence.
""",
"DEMO_GUIDE.md": """# Demo Guide

Preload non-sensitive seed data; use mock AI; keep a tested backup database and screenshots. Rehearse this 7-minute flow: problem (30s) → architecture/ERD (60s) → register/login (45s) → browse destination (30s) → create trip (45s) → generate itinerary/packing (60s) → budget warning (45s) → save/reopen (45s) → SQL view/function/trigger/transaction (60s) → tests/conclusion (40s). If a service fails, explain the fallback and continue from saved screenshots. Never debug secrets live.
""",
"SUBMISSION_CHECKLIST.md": """# Submission Checklist

- [ ] Clean clone works using README only on two systems.
- [ ] `.env`, credentials, personal data, caches and build output excluded.
- [ ] PostgreSQL schema/migrations/seeds replay and backup restores separately.
- [ ] Backend/frontend/AI/database/integration tests pass with evidence.
- [ ] Full demo works; backup screenshots/video available.
- [ ] Report includes theory, requirements, architecture, ERD, schema, normalization, API, SQL objects, AI safety, tests and limitations.
- [ ] Team roles, speaking order, contribution evidence and viva answers verified.
- [ ] All PRs reviewed; known issues documented; `develop` accepted.
- [ ] Merge `develop` to `main`; create annotated `v1.0.0` tag; build secret-free ZIP.
""",
".env.example": """APP_NAME=RoamGenie
APP_ENV=development
APP_DEBUG=false
API_V1_PREFIX=/api/v1
SECRET_KEY=replace-with-a-long-random-local-value
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@HOST:5432/postgres
CORS_ORIGINS=http://localhost:5173
AI_PROVIDER=mock
AI_API_KEY=
AI_MODEL=
AI_TIMEOUT_SECONDS=15
WEATHER_PROVIDER=mock
WEATHER_API_KEY=
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
""",
".gitignore": """.env
*.env.local
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
backend/.venv/
venv/
node_modules/
frontend/dist/
coverage/
.coverage
*.log
*.backup
*.dump
.DS_Store
.vscode/
.idea/
""",
}


DOCS = {
"docs/01-project-theory.md": """# Project Theory

Travellers currently combine many sites for places, stays, food, transport, weather and costs, increasing planning time and budget mistakes. RoamGenie centralizes normalized travel data and accepts origin, destination, dates, travellers, budget, preferences, travel style and special needs. It returns a day-wise plan, suggested places/services, category costs, remaining budget or deficit, warnings, weather context, packing suggestions and AI assistance. AI proposes; validated application logic and PostgreSQL remain authoritative. Core modules are auth/profile, catalogues, trip/itinerary, expense optimization, AI/weather/packing, saved history, administration and reports.
""",
"docs/02-problem-statement.md": """# Problem Statement

Planning across disconnected sources is slow, inconsistent and difficult to budget. The project must show that centralized relational data, validated APIs and bounded AI assistance can create, cost, save and retrieve a personalized plan without letting the frontend or AI bypass database controls.
""",
"docs/03-objectives-and-scope.md": """# Objectives and Scope

Deliver a secure teaching application demonstrating normalized PostgreSQL data; authenticated CRUD; itinerary and budget rules; saved history; structured AI with mock fallback; weather/packing help; and SQL joins, views, functions, procedures, triggers, transactions and indexes. Inputs/outputs are listed in `REQUIREMENTS.md`. Excluded: purchases/bookings, real-time navigation, guarantees about safety/visa/weather, autonomous agents and production-scale operations.
""",
"docs/04-functional-requirements.md": """# Functional Requirements

The numbered, testable functional requirements FR-01–FR-14 are the source of truth in `../REQUIREMENTS.md`. Acceptance focuses on the full journey: register, login, create trip, generate validated plan, calculate budget, save, reopen, edit/delete and logout. Each catalogue supports paginated browsing; admin mutation is protected. Optional providers must have mock fallback.
""",
"docs/05-non-functional-requirements.md": """# Non-functional Requirements

The source of truth is `../REQUIREMENTS.md`. Key measurable checks: hashed passwords; 30-minute configurable JWT; no committed secret; 360/768/1440 responsive layouts; safe 4xx/5xx envelopes; pagination; common local API responses under 2 seconds excluding providers; transactional itinerary save; tested restore; clean-clone setup; and all automated suites passing before release.
""",
"docs/06-system-architecture.md": """# System Architecture

See `../ARCHITECTURE.md` for the diagram. React owns presentation/state and calls only FastAPI. FastAPI routers validate transport concerns, services enforce rules, repositories use SQLAlchemy/PostgreSQL, and adapters isolate AI/weather providers. Accepted AI proposals become persistent only through services and a transaction. JWT protects user resources; admin role protects catalogue mutation.
""",
"docs/07-database-architecture.md": """# Database Architecture

PostgreSQL is authoritative. Users own preferences, trips and saved references. Trips have travellers, allocations, expenses and itineraries; itineraries have ordered days/items. Catalogue records are referenced, not copied where identity matters. Weather and AI conversations are snapshots/history, not truth for booking. Use surrogate bigint keys, unique natural identifiers where stable, foreign keys, domain checks, UTC timestamps, migrations, least privilege and explicit delete rules. ERD: `../database/design/er-diagram.md`; dictionary: `data-dictionary.md`.
""",
"docs/08-api-design.md": """# API Design v1 Draft

Base `/api/v1`; JSON uses snake_case; timestamps ISO-8601 UTC; money is decimal/string at boundaries. Error envelope: `{\"error\":{\"code\":\"validation_error\",\"message\":\"...\",\"details\":[]}}`.

| Resource | Core endpoints |
|---|---|
| auth | `POST /auth/register`, `/auth/login`; `GET /users/me` |
| catalogues | `GET /destinations`, `/hotels`, `/restaurants`, `/attractions`, `/transport-options` with page/filter |
| trips | `POST/GET /trips`, `GET/PATCH/DELETE /trips/{id}` |
| plan | `POST /trips/{id}/generate`, `GET /itineraries/{id}`, `POST /itineraries/{id}/save` |
| budget | `GET /trips/{id}/budget` |
| assistant | `POST /assistant/chat`, `GET /trips/{id}/packing`, `/weather` |

Freeze exact schemas with frontend/database/AI owners at M1. Status: 201 create, 200 read/update, 204 delete, 400 rule, 401 unauthenticated, 403 forbidden, 404 missing, 409 conflict, 422 validation, 503 unavailable with fallback status where relevant.
""",
"docs/09-ai-integration-design.md": """# AI Integration Design

Input: trip facts plus allow-listed catalogue IDs/names/costs and optional weather. Output: `{summary, days[], budget_split[], warnings[], packing_items[]}` validated by Pydantic. The service chooses `mock` by default or a configured adapter, applies a short timeout and at most one transient retry, parses JSON, rejects unknown IDs/missing fields/negative costs, and falls back to deterministic mock output. It does not expose credentials, query/write PostgreSQL or treat provider text as trusted SQL/HTML.
""",
"docs/10-security-design.md": """# Security Design

Threats: credential theft, broken access control, injection, XSS, secret leakage, prompt injection and excessive data exposure. Controls: bcrypt password hashes; expiring JWT; ownership/admin checks; Pydantic validation; ORM/parameterized SQL; frontend escaping; CORS allow-list; generic client errors and sanitized logs; least-privilege DB roles; `.env` exclusion; dependency review; rate limiting before deployment; AI allow-list context and schema validation. Rotate any exposed key immediately and remove it from history through the project manager.
""",
"docs/11-testing-strategy.md": """# Testing Strategy

Use a pyramid: pure unit tests for budget/AI validation; repository/database tests for constraints and SQL objects; API tests for auth/CRUD/errors; a small set of UI tests; full integration and manual acceptance journey. Every bug gets a failing regression test where practical. Test doubles are allowed for AI/weather, not for claiming PostgreSQL integration. Commands and ownership: `../TESTING_GUIDE.md`.
""",
"docs/12-deployment-plan.md": """# Deployment Plan

Development: Supabase-hosted PostgreSQL, backend venv, frontend npm, backend-only `.env`, mock AI; local PostgreSQL is optional and disposable. Apply reviewed migrations then seeds; inject secrets only at runtime and keep the starter labelled incomplete.
""",
"docs/13-presentation-outline.md": """# Presentation Outline

Problem → objectives/scope → existing vs proposed → architecture → ERD/cardinality → normalization/data dictionary → API/UI modules → SQL demonstrations → AI boundary/fallback → full user journey → tests/security → results/limitations/future work → Q&A. Use `../presentation/` for speaker and demo detail.
""",
"docs/dbms-course-mapping.md": """# DBMS Course Mapping

| Concept | Evidence |
|---|---|
| ER/cardinality/keys | `database/design/er-diagram.md` |
| normalization | `database/design/normalization.md` |
| DDL/DML/constraints | `database/schema`, `database/seeds` |
| joins/subqueries/aggregates | `database/queries/001_reports.sql` |
| views/functions/procedures | matching `database/` folders |
| trigger/audit | `database/triggers/001_audit_trip.sql` |
| transactions | `database/transactions/001_save_itinerary.sql` |
| indexes/plans | `database/indexes/001_indexes.sql` |
| security/backup | DBA handbook and deployment evidence |
""",
"docs/data-dictionary.md": """# Data Dictionary (Draft)

| Table | Purpose | Key fields and rules |
|---|---|---|
| users | account identity | id PK; email unique; password_hash; role; timestamps |
| user_preferences | one profile preference set | user_id PK/FK; arrays/text preferences |
| destinations | place catalogue | id PK; city/country; unique city+country |
| hotels/restaurants/attractions | destination offerings | id PK; destination_id FK; name; cost/rating checks |
| transport_options | route options | id PK; origin/destination; mode; nonnegative cost |
| trips | user request | id PK; user_id/destination_id FK; valid dates; travellers/budget positive; status |
| itineraries/days/items | ordered generated plan | trip FK; unique version/day/order; optional catalogue references |
| expenses/budget_allocations | actual/estimated category money | trip FK; category; amount nonnegative; unique allocation category |
| saved_trips | user bookmark/history | user_id+trip_id unique |
| reviews | user ratings | user/target; rating 1–5 |
| ai_conversations/messages | assistant history | user/trip; role/content; timestamps |
| weather_snapshots | time-bound provider result | destination, observed time, JSON payload |
| packing_items | plan checklist | trip, item, category, packed flag |
| activity_preferences | normalized activity labels | user, activity unique pair |

Samyuktha expands every column's type, nullability, default, domain, constraints and delete rule after schema-v1 review.
""",
}


PLANNING = {
"planning/MASTER_PROJECT_PLAN.md": """# Master Project Plan

## Outcome and scope

Build the v1 journey and DBMS evidence defined in `REQUIREMENTS.md`; bookings, payments and autonomous actions are out of scope. Architecture is React → FastAPI → services/repositories → PostgreSQL, with isolated AI/weather adapters.

## Eight-week timeline

| Time | Milestone | Exit checkpoint |
|---|---|---|
| Days 1–3 | M0 initialization | two machines set up; board/workflow; tag `milestone-0` |
| Week 1 | M1 requirements/contracts | ERD, schema, API, UI and AI schema v1 frozen; tag |
| Week 2 | M2 foundation/auth | Supabase PostgreSQL + register/login UI/API smoke test; tag |
| Weeks 3–4 | M3 catalogues | destination vertical slice, then all catalogues; tag |
| Weeks 5–6 | M4 trip/AI/budget | complete saved user journey; tag |
| Week 7 | M5 hardening | security/restore/fresh setup; `milestone-5-rc1` |
| Week 8 | M6 submission | clean demo, main merge and `v1.0.0` |

If official dates move, retain sequence/exit criteria and map Day 1 to the official start; never compress the M1 contract checkpoint or M5 test/restore gate.

## Work and dependencies

Mercy UI ← Yasmin API contracts; Yasmin backend ← Samyuktha schema; Sashtika SQL ← approved schema; Madhu AI ← trip/catalogue contract; Penitta operations ← SQL/migrations; Eunice tests/presentation ← stable integrated slices. See matrices.

## Checkpoints and acceptance

Review ERD/API/UI fields before M1 freeze; integrate destination first in M3; in M4 check trip save, AI validation, persistence and reopen separately. Owners unit-test; Eunice verifies APIs/demo; Yasmin owns integration/acceptance; Penitta verifies DB restore. Use GitHub flow, risk register and Definition of Done. Final acceptance requires clean setup, full journey, SQL demonstrations, mock fallback, tests/evidence, no secrets, reviewed main merge and tag.
""",
"planning/MILESTONE_TIMELINE.md": """# Milestone Timeline

M0: scope, repo, standards, board, environments, initial architecture. M1: Mercy wireframes; Yasmin API/auth plan; Samyuktha ERD/schema/normalization; Sashtika DDL map; Madhu AI schemas/prompts; Penitta DB/roles plan; Eunice test/presentation plan. M2: UI/auth shell; FastAPI/auth/DB; DDL/seeds; mock AI; DB reset; auth tests. M3: catalogue UIs/APIs/seeds/joins/views/recommendations/index review/tests. M4: trip/itinerary/budget/save UI/API/schema/SQL routines/AI/weather/restore/full-flow test. M5: test, security, performance, polish, feature freeze. M6: final docs, report, evidence, rehearsal, backup, clean install, release.

Adjustable rule: assign actual start/end dates beside each milestone, preserve dependency order, reserve at least 20% of calendar for M5–M6, and tag only after exit criteria.
""",
"planning/TEAM_RESPONSIBILITY_MATRIX.md": """# Team Responsibility Matrix

| Feature | Primary | Support | Reviewer | Dependency | M | Deliverable | Test owner | Status |
|---|---|---|---|---|---|---|---|---|
| UI/routes/forms | Mercy | Eunice | Yasmin | API v1 | 1–4 | responsive screens | Mercy | planned |
| Backend/auth/core | Yasmin | Eunice | Penitta | schema | 1–4 | FastAPI services | Yasmin | starter |
| ERD/schema/dictionary | Samyuktha | Sashtika | Yasmin | requirements | 1 | frozen design | Samyuktha | planned |
| SQL objects/reports | Sashtika | Samyuktha | Penitta | schema freeze | 2–5 | replayable SQL | Sashtika | starter |
| AI/fallback | Madhu | Yasmin | Eunice | trip contract | 1–5 | validated service | Madhu | starter |
| DB operations | Penitta | Sashtika | Yasmin | SQL/migrations | 1–6 | restore proof | Penitta | planned |
| API QA/demo | Eunice | all | Yasmin | integrated build | 1–6 | tests/presentation | Eunice | planned |
| Final release | Yasmin | all | team | all gates | 6 | v1.0.0 | Yasmin | planned |
""",
"planning/DEPENDENCY_MATRIX.md": """# Dependency Matrix

| Consumer | Needs | Provider | Wait condition |
|---|---|---|---|
| Mercy | request/response/errors | Yasmin | API v1 freeze |
| Yasmin | keys/relations/constraints | Samyuktha | schema v1 approval |
| Sashtika | relational schema | Samyuktha | design review signed |
| Madhu | trip DTO and allow-listed records | Yasmin/Samyuktha | AI contract freeze |
| Penitta | reviewed SQL/migrations | Sashtika/Yasmin | clean replay passes |
| Eunice | stable endpoints/build | module owners | PR merged to develop |
| Everyone | current integration base | Yasmin/PR owners | timely `develop` merge |

While waiting, work only on mocks, tests, docs or fixtures matching the draft contract; do not silently freeze a dependency yourself.
""",
"planning/GITHUB_WORKFLOW.md": """# GitHub Workflow

Long-lived: `main` stable, `develop` integrated. Member branches: `frontend/mercy`, `backend/yasmin`, `database-design/samyuktha`, `sql/sashtika`, `ai/madhu`, `dba/penitta`, `backend-presentation/eunice`. Short-lived examples: `frontend/login-ui`, `backend/auth-api`, `sql/create-trip-tables`, `ai/itinerary-service`.

```powershell
git clone <repository-url> RoamGenie
cd RoamGenie
git switch develop
git pull origin develop
git switch -c frontend/login-ui
git status
git add frontend tests/frontend
git commit -m "feat(frontend): add trip input form"
git push -u origin frontend/login-ui
gh pr create --base develop --fill
git fetch origin
git rebase origin/develop
# resolve each marked file, then:
git add <resolved-file>
git rebase --continue
git log --oneline --graph --decorate -15
```

Never push unfinished work to `main`. Use small commits and test before push. PR: completed work, files, test commands/results, screenshots, limits and issue. Relevant teammate reviews; Yasmin performs integration review; resolve conflicts on the feature branch. After acceptance merge `develop` to `main` and tag: `git tag -a milestone-1 -m "Milestone 1 accepted"; git push origin milestone-1`.

Commit examples: `feat(auth): implement JWT login`, `feat(database): add itinerary tables`, `feat(ai): add itinerary prompt service`, `test(api): add trip endpoint tests`, `fix(sql): correct expense trigger`, `docs(plan): update milestone checklist`.
""",
"planning/INTEGRATION_CALENDAR.md": """# Integration Calendar

| Checkpoint | Participants | Contract/evidence | Gate |
|---|---|---|---|
| M0 day 2 | all | clone/setup on two systems | planning to develop |
| M1 midweek | Mercy/Yasmin/Samyuktha/Madhu | fields, errors, tables, AI JSON | v1 freeze |
| M2 midweek | Mercy/Yasmin/Penitta/Eunice | register/login + Supabase PostgreSQL | auth smoke |
| M3 week 3 | catalogue owners | destination DB→UI slice | pattern approved |
| M3 week 4 | catalogue owners | remaining modules in small batches | integration tests |
| M4 twice weekly | all relevant | trip save; AI validation; itinerary save/reopen | full journey |
| M5 start/end | all | feature freeze then RC tests/restore | rc1 |
| M6 mid/end | all | two rehearsals then clean clone | v1.0.0 |

Yasmin schedules meetings; owners bring contract diff, test output and blocker. Never defer all integration to milestone end.
""",
"planning/RISK_REGISTER.md": """# Risk Register

| Risk | Prob. | Impact | Prevention | Backup action | Owner |
|---|---|---|---|---|---|
| Merge conflicts | M | H | small PRs/file ownership | one merge owner, pair resolve | Yasmin |
| Late schema change | M | H | M1 freeze/migrations | impact review + versioned migration | Samyuktha |
| API mismatch | H | H | contract examples/tests | adapter or coordinated v2 | Yasmin/Mercy |
| Missing API key | H | M | mock default | deterministic mock demo | Madhu |
| AI unstable/invalid | M | H | schema validation/timeout | mock fallback | Madhu |
| PostgreSQL setup | M | H | versioned runbook | prepared demo DB/restore | Penitta |
| Frontend/backend connection | M | H | env URL/CORS smoke | documented local ports | Mercy/Yasmin |
| Incomplete seed data | M | M | seed checklist | minimal golden fixture | Sashtika |
| Member delay | M | H | weekly board/blockers | re-scope/support assignment | Yasmin |
| Insufficient tests | M | H | DoD/CI checklist | freeze features, test core flow | Eunice |
| Presentation failure | L | H | two rehearsals | screenshots/video/local backup | Eunice |
| Secret leakage | L | H | ignore/scanning/review | revoke/rotate/remove history | Yasmin |
| Last-minute features | H | H | M5 freeze | defer to future work | Yasmin |
""",
"planning/MEETING_TEMPLATE.md": """# Meeting Template

Date/time · attendees · milestone · facilitator. Review last actions and demo completed work (not verbal percent). For each blocker record owner, dependency and due date. Decide contract changes with old/new fields and affected files. List actions as owner/date/evidence. Confirm next integration checkpoint and update project status.
""",
"planning/WEEKLY_STATUS_TEMPLATE.md": """# Weekly Status

Week/milestone: · owner: · branch/PR: · completed deliverables: · files: · tests and evidence: · integration result: · blockers/dependencies: · risks changed: · next three actions: · decisions needed from Yasmin/team:.
""",
"planning/ISSUE_TEMPLATE.md": """# Issue Template

**Title:** `[M#][area] outcome`  
**Owner/reviewer:**  
**User value/requirement:**  
**Allowed files:**  
**Dependencies/contracts:**  
**Acceptance:** valid, invalid, unauthorized/dependency failure  
**Test command/evidence:**  
**Integration checkpoint/date:**  
**Security/data notes:**  
**Out of scope:**
""",
"planning/PULL_REQUEST_CHECKLIST.md": """# Pull Request Checklist

- [ ] Targets `develop`, links issue/milestone and stays within owned files.
- [ ] Summary, changed files, setup/migration notes and known limits provided.
- [ ] No secrets, personal data, build output or unsafe logs.
- [ ] Validation/error handling and contract docs updated.
- [ ] Unit/integration commands and actual results included.
- [ ] UI evidence or SQL result/plan attached where applicable.
- [ ] Upstream/downstream owner reviewed contract change.
- [ ] Status/progress/changelog updated; rollback note included for migrations.
""",
"planning/DEFINITION_OF_DONE.md": """# Definition of Done

A task is done only when source files exist and run; structure/rules are followed; no secrets exist; validation/errors are safe; relevant tests pass; docs/integration steps/evidence are updated; PR is opened/reviewed/resolved/merged to `develop`; status is updated.

A milestone is done only when all tasks and cross-module integration pass; fresh setup works; demonstrations run; known issues are recorded; checklist is approved; and an annotated milestone tag is pushed. A template or TODO is never counted as a completed feature.
""",
}


PRESENTATION = {
"presentation/CONTENT_OUTLINE.md": """# Slide Content Outline

1 title/team; 2 problem; 3 objectives/scope; 4 existing vs proposed; 5 architecture; 6 ERD; 7 schema/normalization; 8 modules/UI; 9 API; 10 SQL features; 11 AI validation/fallback; 12 security/testing; 13 demo/results; 14 limitations/future; 15 contributions/Q&A. Keep slides visual and show evidence, not source-code walls.
""",
"presentation/SPEAKER_ASSIGNMENTS.md": """# Speaker Assignments

Mercy: UI/user flow. Yasmin: opening, architecture/backend/release. Samyuktha: ERD/normalization. Sashtika: SQL objects/query demo. Madhu: AI boundary/mock. Penitta: roles/backup/performance. Eunice: transitions, testing, live demo, conclusion/Q&A coordination. Confirm equal course-required time and one backup speaker per segment during M6.
""",
"presentation/DEMO_FLOW.md": """# Demo Flow

Eunice checks database/backend/frontend/mock AI, then: register → login → browse seeded destination → enter valid trip → generate plan → show day items and packing → show category budget/warning → save → reopen → edit/delete as time allows → show one join/view, function, audit trigger and rollback → show tests. Rehearse under 7 minutes. Backup: local database plus numbered screenshots; never depend on live external AI.
""",
"presentation/EXPECTED_QUESTIONS.md": """# Expected Questions

- Why PostgreSQL? Integrity, relational queries, transactions and DBMS object support.
- Why 3NF/BCNF? Reduce update anomalies while preserving meaningful dependencies.
- Why AI plus database? Database supplies trusted facts; AI structures suggestions; validation keeps authority in the app.
- How is overspending handled? Decimal totals compare with positive budget and return deficit/warning.
- How is security handled? Hashing, expiring JWT, ownership, validation, parameterization, least privilege and secret isolation.
- Why a trigger? Audit important trip changes consistently; business logic otherwise stays in services.
- What if AI/weather fails? Time out and return documented mock/fallback.
- What is incomplete? State actual `PROJECT_STATUS.md`; do not claim TODOs.
""",
"presentation/SCREENSHOT_CHECKLIST.md": """# Screenshot Checklist

- [ ] landing/mobile navigation; register/login errors; profile/trip validation
- [ ] destination/hotel/restaurant/attraction loading, empty and results
- [ ] itinerary, budget warning, saved/reopened trip, AI/packing fallback
- [ ] ERD/schema/API docs; SQL join/view/function/trigger/rollback
- [ ] test summary, backup/restore proof and clean setup

Name files `M#-feature-state-date.png`; blur emails/tokens and store only approved evidence.
""",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    for path, content in {**ROOT_DOCS, **DOCS, **PLANNING, **PRESENTATION}.items():
        write(path, content, args.force)
    for role in roles:
        generate_role(role, args.force)
    for folder in [
        "database/migrations", "database/reports", "ai/tests", "tests/frontend",
        "tests/database", "tests/acceptance", "scripts/database", "scripts/run",
        "scripts/test", "scripts/demo"
    ]:
        write(f"{folder}/.gitkeep", "", args.force)
    # Keep a newly regenerated workspace aligned with the accepted hosted-database ADR.
    runpy.run_path(str(ROOT / "scripts/setup/update_supabase_workspace.py"))
    print("RoamGenie workspace documentation generated with Supabase updates.")


if __name__ == "__main__":
    main()
