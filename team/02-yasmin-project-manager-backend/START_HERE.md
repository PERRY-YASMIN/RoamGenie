# Start Here

1. **Build:** FastAPI setup, auth, users, catalogues, trips, itineraries, budgets, saved trips, AI endpoints, final integration.
2. **Why:** this supplies the project's project manager & backend developer deliverable and a tested link in the database → API → UI flow.
3. **Inputs:** approved schema from Samyuktha/Sashtika, AI contract from Madhu, frontend needs from Mercy.
4. **Outputs:** versioned validated API, JWT auth, service/repository boundaries, tests, reviewed milestone merges.
5. **Setup:** run `cd backend; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; Copy-Item ..\.env.example .env; uvicorn app.main:app --reload` from the repository root (PowerShell).
6. **Implementation order:** Triage board daily → freeze contracts → config/database → auth → one destination vertical slice → remaining catalogues → trips/budget → itinerary/save → AI/weather → integration tests.
7. **Testing:** Run `pytest`; inspect `/docs`; test 401/403/404/422 paths and full register-to-reopen journey.
8. **Git:** use the commands in `GITHUB_GUIDE.md` on `backend/yasmin`.
9. **Evidence:** issue board, API docs, passing test output, auth flow, full journey, review approvals, milestone tags.
10. **Final connection:** integrate the owned output on `develop`; the feature is incomplete until its upstream and downstream contracts both work.

<!-- SUPABASE_UPDATE_START -->
## Updated architecture

Primary path: React → FastAPI → SQLAlchemy → Supabase-hosted PostgreSQL. Own the Supabase–FastAPI connection, SQLAlchemy engine/session, Alembic, environment setup, migration review, `/api/health`, integration tests, schema-change coordination and final secret review. Ensure FastAPI remains React's normal database access layer. Before starting, read `../../docs/SUPABASE_SETUP_GUIDE.md` and confirm the relevant contract/migration status.
<!-- SUPABASE_UPDATE_END -->
