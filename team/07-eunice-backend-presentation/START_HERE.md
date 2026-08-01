# Start Here

1. **Build:** destination/hotel/restaurant/attraction route support, contract/error testing, slides, screenshots, demo and viva coordination.
2. **Why:** this supplies the project's backend & presentation coordinator deliverable and a tested link in the database → API → UI flow.
3. **Inputs:** assigned API contract and stable integrated builds.
4. **Outputs:** tested support endpoints, issue log, presentation outline, speakers, live/backup demo and viva pack.
5. **Setup:** run `cd backend; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload; Start-Process http://127.0.0.1:8000/docs` from the repository root (PowerShell).
6. **Implementation order:** Confirm assigned routes → add schema/service tests → log mismatches → update API docs → collect milestone evidence → rehearse timed demo → prepare backup.
7. **Testing:** Test success plus 401/404/422/500-safe responses in `/docs`; run integration tests; rehearse demo twice on a clean setup.
8. **Git:** use the commands in `GITHUB_GUIDE.md` on `backend-presentation/eunice`.
9. **Evidence:** API test results, architecture/ERD/UI screenshots, timed script, speaker sheet, backup screenshots/video location.
10. **Final connection:** integrate the owned output on `develop`; the feature is incomplete until its upstream and downstream contracts both work.

<!-- SUPABASE_UPDATE_START -->
## Updated architecture

Primary path: React → FastAPI → SQLAlchemy → Supabase-hosted PostgreSQL. Test database connectivity and `/api/health`, verify records in Dashboard, capture Table Editor and SQL result evidence, and demonstrate React → FastAPI → Supabase PostgreSQL. Prepare offline database/ERD/architecture/API/frontend screenshots and an optional recording. Before starting, read `../../docs/SUPABASE_SETUP_GUIDE.md` and confirm the relevant contract/migration status.
<!-- SUPABASE_UPDATE_END -->
