# File Ownership

- **Own:** database operational scripts, roles/permissions, backup/restore/runbooks, performance evidence.
- **Modify after coordination:** migration review and `.env.example` database variables.
- **Approval required:** logical schema changes without Samyuktha/Sashtika approval; real credentials in Git.
- Generated files, dependency locks, and shared contracts require owner review.
- When two branches touch the same file, agree on one editor and cherry-pick or rebase after review.
