# Repository Audit — 2026-08-01

## Existing state

`RoamGenie/` contained only `.git`; it had no tracked files, manifests, application modules, branches visible to the sandbox, or documentation. Therefore there was no fixed stack or working code to replace.

The parent `../docs/` folder contains PDFs, a PowerPoint, images/screenshots and three SQL-related files. They are evidence/reference assets outside the target Git repository and were preserved unchanged. They were not copied because their provenance and desired versioning need team confirmation.

## Stack selected

React/Vite/JavaScript frontend; FastAPI/Pydantic/SQLAlchemy/Alembic backend; PostgreSQL; JWT/bcrypt during M2; provider-independent AI with deterministic mock; pytest and Vitest.

## Missing/incomplete

All production features were initially missing. This scaffold supplies documentation and safe starters only. Authentication, complete ORM model, all CRUD routes, migrations, full UI, production AI provider and deployment remain scheduled work.

## Conflicts and preservation

No working code conflicts exist. Do not overwrite parent course artifacts. Before importing their SQL, compare it with the approved schema and record provenance. Git reported a safe-directory ownership warning under the sandbox; team members using their normal accounts should confirm `git status` before changing global Git configuration.
