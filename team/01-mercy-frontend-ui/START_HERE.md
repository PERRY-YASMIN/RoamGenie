# Start Here

1. **Build:** responsive UI, routing, forms, dashboard, API client, loading/empty/error states.
2. **Why:** this supplies the project's frontend/ui designer deliverable and a tested link in the database → API → UI flow.
3. **Inputs:** approved API contract from Yasmin, field names from Samyuktha, AI response schema from Madhu.
4. **Outputs:** 14 routed screens, reusable components, validation, API integration, responsive evidence.
5. **Setup:** run `cd frontend; npm install; Copy-Item .env.example .env; npm run dev` from the repository root (PowerShell).
6. **Implementation order:** Create shell/routes → shared components → auth pages → trip form → catalogue pages → itinerary/budget → saved trips/assistant → responsive polish.
7. **Testing:** Run `npm run lint`, `npm test -- --run`, and `npm run build`; manually check 360px, 768px, and 1440px widths plus Chrome/Edge.
8. **Git:** use the commands in `GITHUB_GUIDE.md` on `frontend/mercy`.
9. **Evidence:** landing, login errors, trip validation, loading/empty/error states, itinerary, budget warning, saved trip, assistant, mobile menu.
10. **Final connection:** integrate the owned output on `develop`; the feature is incomplete until its upstream and downstream contracts both work.

<!-- SUPABASE_UPDATE_START -->
## Updated architecture

Primary path: React → FastAPI → SQLAlchemy → Supabase-hosted PostgreSQL. React calls FastAPI only. Do not add the Supabase JavaScript client or any database/service-role credential. Use contract-matched mock API data while endpoints are pending. Dashboard is not the app UI; its screenshots are presentation evidence only. Before starting, read `../../docs/SUPABASE_SETUP_GUIDE.md` and confirm the relevant contract/migration status.
<!-- SUPABASE_UPDATE_END -->
