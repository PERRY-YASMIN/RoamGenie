# Team Responsibility Matrix

| Feature | Primary | Support | Reviewer | Dependency | M | Deliverable | Test owner | Status |
|---|---|---|---|---|---|---|---|---|
| UI/routes/forms | Mercy | Eunice | Yasmin | API v1 | 1–4 | responsive screens | Mercy | planned |
| Backend/auth/core | Yasmin | Eunice | Penitta | schema | 1–4 | FastAPI services | Yasmin | starter |
| ERD/schema/dictionary | Samyuktha | Sashtika | Yasmin | requirements | 1 | frozen design | Samyuktha | planned |
| SQL objects/reports | Sashtika | Samyuktha | Penitta | schema freeze | 2–5 | replayable SQL | Sashtika | starter |
| AI/fallback | Madhu | Yasmin | Eunice | trip contract | 1–5 | validated service | Madhu | starter |
| DB operations | Penitta | Sashtika | Yasmin | SQL/migrations | 1–6 | restore proof | Penitta | planned |
| API QA/demo | Eunice | all | Yasmin | integrated build | 1–6 | tests/presentation | Eunice | planned |
| Final release | Yasmin | all | team | all gates | 6 | v1.0.0 | Yasmin | planned |

<!-- SUPABASE_UPDATE_START -->
## Supabase ownership update

Yasmin owns connection/SQLAlchemy/Alembic/health; Samyuktha design and migration review; Sashtika versioned PostgreSQL course SQL; Penitta project access/migrations/backups/Dashboard/performance; Mercy FastAPI-only client; Madhu backend-only structured AI; Eunice connectivity/Dashboard/SQL/demo evidence. Each database feature requires relevant cross-review.
<!-- SUPABASE_UPDATE_END -->
