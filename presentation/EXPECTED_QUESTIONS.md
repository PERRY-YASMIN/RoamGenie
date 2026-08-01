# Expected Questions

- Why PostgreSQL? Integrity, relational queries, transactions and DBMS object support.
- Why 3NF/BCNF? Reduce update anomalies while preserving meaningful dependencies.
- Why AI plus database? Database supplies trusted facts; AI structures suggestions; validation keeps authority in the app.
- How is overspending handled? Decimal totals compare with positive budget and return deficit/warning.
- How is security handled? Hashing, expiring JWT, ownership, validation, parameterization, least privilege and secret isolation.
- Why a trigger? Audit important trip changes consistently; business logic otherwise stays in services.
- What if AI/weather fails? Time out and return documented mock/fallback.
- What is incomplete? State actual `PROJECT_STATUS.md`; do not claim TODOs.

<!-- SUPABASE_UPDATE_START -->
## Supabase viva answers

- **Is Supabase another DBMS?** No; it hosts PostgreSQL, our relational DBMS.
- **Why Supabase?** Shared managed hosting, Dashboard, SQL Editor and logs reduce setup friction.
- **Does React connect directly?** No, it normally calls FastAPI only.
- **FastAPI/SQLAlchemy/Alembic?** API/business and authorization layer; ORM/session access; versioned schema evolution.
- **Why SQL files?** Reproducibility and DBMS demonstrations beyond ordinary ORM work.
- **What is RLS?** PostgreSQL row policies used when a client accesses exposed tables; FastAPI ownership is primary here.
- **Where are passwords?** Backend environment/secret manager, never Git or React.
- **Outage/backup?** Optional migration-built local fallback, exported backup and offline evidence.
- **How prevent cross-user reads?** Authenticated FastAPI ownership checks and tests; RLS before any approved direct access.
<!-- SUPABASE_UPDATE_END -->
