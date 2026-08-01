# MERCY JOICE J — Frontend/UI Designer

## Responsibility

- Primary responsibility: responsive UI, routing, forms, dashboard, API client, loading/empty/error states.
- Modules owned: responsive UI, routing, forms, dashboard, API client, loading/empty/error states.
- Files owned: `frontend/`, `tests/frontend/`, frontend screenshots.
- May modify: API contract comments and frontend sections of docs.
- Do not modify without approval: database schema, backend routes, SQL and AI service code without owner approval.
- Dependencies: approved API contract from Yasmin, field names from Samyuktha, AI response schema from Madhu.
- Expected deliverables: 14 routed screens, reusable components, validation, API integration, responsive evidence.
- Testing responsibility: Run `npm run lint`, `npm test -- --run`, and `npm run build`; manually check 360px, 768px, and 1440px widths plus Chrome/Edge.
- Integration responsibility: demonstrate the owned slice against `develop`, document contract mismatches, and support its reviewer.
- Branch: `frontend/mercy`.
- Pull request: target `develop`; link issue; list tests, evidence, limitations; obtain one relevant review and Yasmin's integration approval.
- Complete when: Code/docs exist; required tests pass; no secrets; contracts match; evidence is attached; reviewed PR is merged to `develop`; `PROJECT_STATUS.md` and progress log are updated.

<!-- SUPABASE_UPDATE_START -->
## Supabase responsibility

React calls FastAPI only. Do not add the Supabase JavaScript client or any database/service-role credential. Use contract-matched mock API data while endpoints are pending. Dashboard is not the app UI; its screenshots are presentation evidence only.
<!-- SUPABASE_UPDATE_END -->
