# Start Here

1. **Build:** provider abstraction, prompts, structured itinerary/recommendations/Q&A/packing, validation, timeouts, retry and mock fallback.
2. **Why:** this supplies the project's ai integration engineer deliverable and a tested link in the database → API → UI flow.
3. **Inputs:** validated trip DTO plus selected database records and weather snapshot.
4. **Outputs:** validated provider-independent JSON; deterministic no-key mock; malformed/timeout tests.
5. **Setup:** run `$env:AI_PROVIDER='mock'; cd backend; .\.venv\Scripts\Activate.ps1; pytest ../tests/ai` from the repository root (PowerShell).
6. **Implementation order:** Freeze JSON schema → write mock → prompts → provider interface → timeout/retry → validation → fallback → endpoint contract tests.
7. **Testing:** Test valid JSON, invalid JSON, missing fields, timeout, missing key, empty preferences, invalid destination, unrealistic budget and unknown IDs.
8. **Git:** use the commands in `GITHUB_GUIDE.md` on `ai/madhu`.
9. **Evidence:** sample request/response, mock output, fallback test, validation failure, sanitized logs.
10. **Final connection:** integrate the owned output on `develop`; the feature is incomplete until its upstream and downstream contracts both work.

<!-- SUPABASE_UPDATE_START -->
## Updated architecture

Primary path: React → FastAPI → SQLAlchemy → Supabase-hosted PostgreSQL. AI calls backend services and receives validated structured records. It never receives Supabase credentials, executes arbitrary SQL, changes tables or invents trusted IDs. FastAPI validates referenced IDs and persists accepted output. Preserve mock mode. Before starting, read `../../docs/SUPABASE_SETUP_GUIDE.md` and confirm the relevant contract/migration status.
<!-- SUPABASE_UPDATE_END -->
