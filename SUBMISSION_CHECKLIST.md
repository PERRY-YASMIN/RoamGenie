# Submission Checklist

- [ ] Clean clone works using README only on two systems.
- [ ] `.env`, credentials, personal data, caches and build output excluded.
- [ ] PostgreSQL schema/migrations/seeds replay and backup restores separately.
- [ ] Backend/frontend/AI/database/integration tests pass with evidence.
- [ ] Full demo works; backup screenshots/video available.
- [ ] Report includes theory, requirements, architecture, ERD, schema, normalization, API, SQL objects, AI safety, tests and limitations.
- [ ] Team roles, speaking order, contribution evidence and viva answers verified.
- [ ] All PRs reviewed; known issues documented; `develop` accepted.
- [ ] Merge `develop` to `main`; create annotated `v1.0.0` tag; build secret-free ZIP.

<!-- SUPABASE_UPDATE_START -->
## Supabase release checks

- [ ] Supabase project contains only reviewed migrations/SQL and safe demo rows.
- [ ] `alembic current` is expected head; fresh recreation from migrations/seeds passes.
- [ ] React accesses data only through FastAPI.
- [ ] No credentials/project-specific URLs/service-role keys exist in repository or frontend build.
- [ ] Backup/restore and outage fallback evidence is current.
- [ ] Dashboard/SQL demonstration and complete app flow are rehearsed.
<!-- SUPABASE_UPDATE_END -->
