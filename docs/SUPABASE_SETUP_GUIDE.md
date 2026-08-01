# Supabase Setup Guide

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
