# Role Scope

## Own

`database/design/`, `docs/data-dictionary.md`, ERD and normalization.

## Coordinate

- Inputs: requirements and API data needs.
- Outputs: reviewed Mermaid ERD, relational schema, 1NF→2NF→3NF/BCNF analysis, data dictionary and handoff.
- Must not change: executable production SQL or migrations without Sashtika/Yasmin review.
- Escalate contract conflicts to Yasmin before coding past the conflict.

<!-- SUPABASE_UPDATE_START -->
## Supabase boundary

Design PostgreSQL/Supabase-compatible schemas, record approval before implementation, review generated Alembic migrations against the ER model, confirm relationships in Dashboard and update the dictionary after every accepted migration. Never treat a manual Dashboard-only schema as delivered.
<!-- SUPABASE_UPDATE_END -->
