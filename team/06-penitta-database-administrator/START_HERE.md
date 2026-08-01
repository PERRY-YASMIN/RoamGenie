# Start Here

1. **Build:** PostgreSQL setup, databases/roles, least privilege, migration runs, backups/restores, index checks and security.
2. **Why:** this supplies the project's database administrator (dba) deliverable and a tested link in the database → API → UI flow.
3. **Inputs:** approved SQL from Sashtika and migrations from Yasmin.
4. **Outputs:** repeatable local setup, app/read-only roles, backup/restore proof, migration log and performance review.
5. **Setup:** create/invite the team to the Supabase project, document the connection mode, configure `backend/.env`, run `cd backend; alembic current; alembic upgrade head`, then verify `/api/health` and Table Editor.
6. **Implementation order:** Install/version check → roles/database → environment → schema/migrations → seed → connection → permissions → backup/restore drill → index/performance review.
7. **Testing:** Connect as app and read-only users; verify denied writes for read-only; restore into a separate `roamgenie_restore_test` database; compare row counts.
8. **Git:** use the commands in `GITHUB_GUIDE.md` on `dba/penitta`.
9. **Evidence:** version, role privileges, migration log, backup file metadata, restored row counts, EXPLAIN results.
10. **Final connection:** integrate the owned output on `develop`; the feature is incomplete until its upstream and downstream contracts both work.

<!-- SUPABASE_UPDATE_START -->
## Updated architecture

Primary path: React → FastAPI → SQLAlchemy → Supabase-hosted PostgreSQL. Own Supabase project/team access, connection-mode guidance, environment/secret runbook, reviewed migration application, Dashboard/log monitoring, permissions, backup/restore/reset, index/performance verification and the demo database. Export before major milestones and maintain offline evidence. Before starting, read `../../docs/SUPABASE_SETUP_GUIDE.md` and confirm the relevant contract/migration status.
<!-- SUPABASE_UPDATE_END -->
