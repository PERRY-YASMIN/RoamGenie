# SAMYUKTHA KUMARAN — Database Designer

## Responsibility

- Primary responsibility: conceptual model, entities, cardinality, keys, constraints, relational schema, normalization.
- Modules owned: conceptual model, entities, cardinality, keys, constraints, relational schema, normalization.
- Files owned: `database/design/`, `docs/data-dictionary.md`, ERD and normalization.
- May modify: schema review notes.
- Do not modify without approval: executable production SQL or migrations without Sashtika/Yasmin review.
- Dependencies: requirements and API data needs.
- Expected deliverables: reviewed Mermaid ERD, relational schema, 1NF→2NF→3NF/BCNF analysis, data dictionary and handoff.
- Testing responsibility: Trace every foreign key; test optionality/deletion rules on paper; ask Sashtika to execute DDL and Penitta to review operations.
- Integration responsibility: demonstrate the owned slice against `develop`, document contract mismatches, and support its reviewer.
- Branch: `database-design/samyuktha`.
- Pull request: target `develop`; link issue; list tests, evidence, limitations; obtain one relevant review and Yasmin's integration approval.
- Complete when: Code/docs exist; required tests pass; no secrets; contracts match; evidence is attached; reviewed PR is merged to `develop`; `PROJECT_STATUS.md` and progress log are updated.

<!-- SUPABASE_UPDATE_START -->
## Supabase responsibility

Design PostgreSQL/Supabase-compatible schemas, record approval before implementation, review generated Alembic migrations against the ER model, confirm relationships in Dashboard and update the dictionary after every accepted migration. Never treat a manual Dashboard-only schema as delivered.
<!-- SUPABASE_UPDATE_END -->
