# Setup Guide

## Preconditions

Git, VS Code, Supabase project access (local PostgreSQL 15+ optional), Python 3.11+, and Node 20+ are installed. Clone the repository and copy `.env.example` to `.env`; never commit `.env`.

## Commands

```powershell
git clone <repository-url> RoamGenie
cd RoamGenie
git switch develop
git pull origin develop
git switch -c dba/penitta
Copy-Item .env.example .env
alembic current
alembic upgrade head
Invoke-RestMethod http://127.0.0.1:8000/api/health
# Export through scripts/database/backup.ps1 after setting DATABASE_URL securely.
```

Expected: commands complete without secrets in output. If a contract/file is missing, record an issue and wait for its owner instead of inventing it.

<!-- SUPABASE_UPDATE_START -->
## Supabase setup

Own Supabase project/team access, connection-mode guidance, environment/secret runbook, reviewed migration application, Dashboard/log monitoring, permissions, backup/restore/reset, index/performance verification and the demo database. Export before major milestones and maintain offline evidence.

Never commit `.env`. Copy the relevant example, obtain access safely, and verify `GET /api/health`. Backend/database work runs `alembic current`, reviews migration, then `alembic upgrade head`. Use the Dashboard-recommended direct/session/transaction connection for the task; migration work may require direct or session compatibility. Optional local PostgreSQL uses the same migrations/seeds and is explicitly selected—not synchronized truth.
<!-- SUPABASE_UPDATE_END -->
