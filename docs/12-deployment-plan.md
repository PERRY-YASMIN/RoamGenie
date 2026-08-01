# Deployment Plan

Development: Supabase project access (local PostgreSQL 15+ optional), backend venv, frontend npm, `.env`, mock AI. Apply reviewed schema/migrations then seeds; run backend on 8000 and frontend on 5173. Release: provision separate database/app user, inject secrets, run migrations once, build frontend, serve backend behind HTTPS, restrict CORS, enable backups/logging, run smoke tests. Roll back application artifact first; database rollback only through reviewed migration/restore procedure. Current repo is not production-ready.

<!-- SUPABASE_UPDATE_START -->
## Primary and fallback databases

Primary: agreed Supabase project and its Dashboard-recommended connection mode. Optional local: isolated PostgreSQL for offline work or migration tests, selected explicitly with `DATABASE_ENV=local` and `LOCAL_DATABASE_URL`. Never switch silently or synchronize ad-hoc changes. Both environments are recreated from the same Alembic migrations and seeds; the final demo targets Supabase. Before major milestones export a backup, capture row counts and rehearse offline screenshots.
<!-- SUPABASE_UPDATE_END -->
