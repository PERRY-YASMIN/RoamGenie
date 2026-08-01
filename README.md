# RoamGenie — AI Travel Planner & Budget Optimizer

RoamGenie is a DBMS course project that turns trip dates, travellers, budget and preferences into a saved day-wise itinerary with category costs, warnings, weather context and packing suggestions.

## Status

This repository is an **implementation starter**, not a production release. Architecture, contracts, PostgreSQL examples, team handbooks, and runnable FastAPI/React starter shells are included. Catalogue, full authentication, persistence and real AI remain milestone work; mock AI is the default.

## Quick start (PowerShell)

```powershell
Copy-Item .env.example .env
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
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

<!-- SUPABASE_UPDATE_START -->
## Supabase-hosted PostgreSQL decision

The primary shared database is **PostgreSQL hosted by Supabase**. Supabase is the managed platform, not a second DBMS. React sends HTTP/JSON to FastAPI; FastAPI uses SQLAlchemy and `DATABASE_URL`; Alembic evolves the application schema. Supabase Dashboard supplies Table Editor, SQL Editor, logs and presentation evidence—not the user interface.

Start with `docs/SUPABASE_SETUP_GUIDE.md`. Copy `.env.example` to `.env`, replace only local placeholders, then from `backend` run `alembic current`, `alembic upgrade head`, and `uvicorn app.main:app --reload`. Verify `GET /api/health`. Local PostgreSQL is an optional disposable fallback created from the same migrations and seeds; it is never a second synchronized source of truth.
<!-- SUPABASE_UPDATE_END -->
