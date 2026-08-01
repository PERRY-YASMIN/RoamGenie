# PENITTA A — Database Administrator (DBA)

## Responsibility

- Primary responsibility: PostgreSQL setup, databases/roles, least privilege, migration runs, backups/restores, index checks and security.
- Modules owned: PostgreSQL setup, databases/roles, least privilege, migration runs, backups/restores, index checks and security.
- Files owned: database operational scripts, roles/permissions, backup/restore/runbooks, performance evidence.
- May modify: migration review and `.env.example` database variables.
- Do not modify without approval: logical schema changes without Samyuktha/Sashtika approval; real credentials in Git.
- Dependencies: approved SQL from Sashtika and migrations from Yasmin.
- Expected deliverables: repeatable local setup, app/read-only roles, backup/restore proof, migration log and performance review.
- Testing responsibility: Connect as app and read-only users; verify denied writes for read-only; restore into a separate `roamgenie_restore_test` database; compare row counts.
- Integration responsibility: demonstrate the owned slice against `develop`, document contract mismatches, and support its reviewer.
- Branch: `dba/penitta`.
- Pull request: target `develop`; link issue; list tests, evidence, limitations; obtain one relevant review and Yasmin's integration approval.
- Complete when: Code/docs exist; required tests pass; no secrets; contracts match; evidence is attached; reviewed PR is merged to `develop`; `PROJECT_STATUS.md` and progress log are updated.

<!-- SUPABASE_UPDATE_START -->
## Supabase responsibility

Own Supabase project/team access, connection-mode guidance, environment/secret runbook, reviewed migration application, Dashboard/log monitoring, permissions, backup/restore/reset, index/performance verification and the demo database. Export before major milestones and maintain offline evidence.
<!-- SUPABASE_UPDATE_END -->
