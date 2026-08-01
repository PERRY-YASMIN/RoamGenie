# EUNICE MERCY M — Backend & Presentation Coordinator

## Responsibility

- Primary responsibility: destination/hotel/restaurant/attraction route support, contract/error testing, slides, screenshots, demo and viva coordination.
- Modules owned: destination/hotel/restaurant/attraction route support, contract/error testing, slides, screenshots, demo and viva coordination.
- Files owned: assigned catalogue API support, API tests/docs, `presentation/`, demo evidence.
- May modify: backend catalogue routers/schemas assigned in an issue.
- Do not modify without approval: auth/core trip logic, schema, or another member's slides without review.
- Dependencies: assigned API contract and stable integrated builds.
- Expected deliverables: tested support endpoints, issue log, presentation outline, speakers, live/backup demo and viva pack.
- Testing responsibility: Test success plus 401/404/422/500-safe responses in `/docs`; run integration tests; rehearse demo twice on a clean setup.
- Integration responsibility: demonstrate the owned slice against `develop`, document contract mismatches, and support its reviewer.
- Branch: `backend-presentation/eunice`.
- Pull request: target `develop`; link issue; list tests, evidence, limitations; obtain one relevant review and Yasmin's integration approval.
- Complete when: Code/docs exist; required tests pass; no secrets; contracts match; evidence is attached; reviewed PR is merged to `develop`; `PROJECT_STATUS.md` and progress log are updated.

<!-- SUPABASE_UPDATE_START -->
## Supabase responsibility

Test database connectivity and `/api/health`, verify records in Dashboard, capture Table Editor and SQL result evidence, and demonstrate React → FastAPI → Supabase PostgreSQL. Prepare offline database/ERD/architecture/API/frontend screenshots and an optional recording.
<!-- SUPABASE_UPDATE_END -->
