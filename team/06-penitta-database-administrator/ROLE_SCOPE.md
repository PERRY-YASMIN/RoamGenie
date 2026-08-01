# Role Scope

## Own

database operational scripts, roles/permissions, backup/restore/runbooks, performance evidence.

## Coordinate

- Inputs: approved SQL from Sashtika and migrations from Yasmin.
- Outputs: repeatable local setup, app/read-only roles, backup/restore proof, migration log and performance review.
- Must not change: logical schema changes without Samyuktha/Sashtika approval; real credentials in Git.
- Escalate contract conflicts to Yasmin before coding past the conflict.

<!-- SUPABASE_UPDATE_START -->
## Supabase boundary

Own Supabase project/team access, connection-mode guidance, environment/secret runbook, reviewed migration application, Dashboard/log monitoring, permissions, backup/restore/reset, index/performance verification and the demo database. Export before major milestones and maintain offline evidence.
<!-- SUPABASE_UPDATE_END -->
