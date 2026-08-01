# Project Status

Updated: 2026-08-01

| Milestone | Status | Exit evidence | Owner |
|---|---|---|---|
| M0 initialization | In progress | workspace scaffold created; two-system setup and GitHub board pending | Yasmin |
| M1 contracts/design | Not started | schema/API/UI/AI v1 freeze | All |
| M2 foundation/auth | Not started | PostgreSQL + auth + UI smoke test | Yasmin |
| M3 core data | Not started | destination vertical slice then catalogues | Yasmin |
| M4 trip/AI/budget | Not started | full saved journey | All |
| M5 hardening | Not started | RC tests/security/restore | All |
| M6 submission | Not started | clean demo, main merge, v1.0.0 | Yasmin/Eunice |

Use each member's `PROGRESS_LOG.md` for work detail. Update this table only with evidence links/PR numbers.

<!-- SUPABASE_UPDATE_START -->
## Supabase migration status

Architecture decision accepted: Supabase-hosted PostgreSQL is the primary shared/demo database; FastAPI auth/access remains. Documentation/environment/connection/Alembic starters updated. Pending team evidence: create project/access; choose connection mode; configure secret `DATABASE_URL`; run initial migration; validate `/api/health`; verify tables/seeds; backup/restore; confirm free-tier limits. Do not mark M0 complete until the empty-database connection gate passes.
<!-- SUPABASE_UPDATE_END -->
