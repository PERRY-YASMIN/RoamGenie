# Setup Guide

## Preconditions

Git, VS Code, Supabase project access (local PostgreSQL 15+ optional), Python 3.11+, and Node 20+ are installed. Clone the repository and copy `.env.example` to `.env`; never commit `.env`.

## Commands

```powershell
git clone <repository-url> RoamGenie
cd RoamGenie
git switch develop
git pull origin develop
git switch -c database-design/samyuktha
code database/design/er-diagram.md; code docs/data-dictionary.md
```

Expected: commands complete without secrets in output. If a contract/file is missing, record an issue and wait for its owner instead of inventing it.

<!-- SUPABASE_UPDATE_START -->
## Supabase setup

Design PostgreSQL/Supabase-compatible schemas, record approval before implementation, review generated Alembic migrations against the ER model, confirm relationships in Dashboard and update the dictionary after every accepted migration. Never treat a manual Dashboard-only schema as delivered.

Never commit `.env`. Copy the relevant example, obtain access safely, and verify `GET /api/health`. Backend/database work runs `alembic current`, reviews migration, then `alembic upgrade head`. Use the Dashboard-recommended direct/session/transaction connection for the task; migration work may require direct or session compatibility. Optional local PostgreSQL uses the same migrations/seeds and is explicitly selected—not synchronized truth.
<!-- SUPABASE_UPDATE_END -->
