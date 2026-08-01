# Start Here

1. **Build:** conceptual model, entities, cardinality, keys, constraints, relational schema, normalization.
2. **Why:** this supplies the project's database designer deliverable and a tested link in the database → API → UI flow.
3. **Inputs:** requirements and API data needs.
4. **Outputs:** reviewed Mermaid ERD, relational schema, 1NF→2NF→3NF/BCNF analysis, data dictionary and handoff.
5. **Setup:** run `code database/design/er-diagram.md; code docs/data-dictionary.md` from the repository root (PowerShell).
6. **Implementation order:** Identify facts → separate entities → choose stable keys → draw cardinalities → list constraints → normalize → review API fields → freeze v1 → hand off.
7. **Testing:** Trace every foreign key; test optionality/deletion rules on paper; ask Sashtika to execute DDL and Penitta to review operations.
8. **Git:** use the commands in `GITHUB_GUIDE.md` on `database-design/samyuktha`.
9. **Evidence:** rendered ERD, normalization table, reviewed dictionary, signed schema-v1 checkpoint.
10. **Final connection:** integrate the owned output on `develop`; the feature is incomplete until its upstream and downstream contracts both work.

<!-- SUPABASE_UPDATE_START -->
## Updated architecture

Primary path: React → FastAPI → SQLAlchemy → Supabase-hosted PostgreSQL. Design PostgreSQL/Supabase-compatible schemas, record approval before implementation, review generated Alembic migrations against the ER model, confirm relationships in Dashboard and update the dictionary after every accepted migration. Never treat a manual Dashboard-only schema as delivered. Before starting, read `../../docs/SUPABASE_SETUP_GUIDE.md` and confirm the relevant contract/migration status.
<!-- SUPABASE_UPDATE_END -->
