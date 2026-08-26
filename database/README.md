# RoamGenie Relational Database Management

> **Project:** RoamGenie — AI Travel Planner & Budget Optimizer  
> **Course:** Database Management Systems (Semester 5 Theory & Project)  
> **Database Platform:** PostgreSQL 15+ (Hosted on Supabase / Local Fallback)  
> **Authoritative Specification:** [docs/database/DATABASE_ARCHITECTURE.md](../docs/database/DATABASE_ARCHITECTURE.md)  
> **Data Dictionary:** [docs/database/DATA_DICTIONARY.md](../docs/database/DATA_DICTIONARY.md)

---

## 1. Directory Structure & SQL Artifacts

```
database/
├── schema/             # Active 22-table DDL script (001_schema.sql)
├── seeds/              # Master seed datasets (001_seed.sql, JSON manifests)
├── views/              # Database views (v_trip_budget_summary, v_destination_catalogue)
├── functions/          # Stored functions (calculate_trip_estimated_total, remaining_trip_budget)
├── procedures/         # Stored procedures (refresh_trip_total)
├── triggers/           # PL/pgSQL audit triggers on trips (trg_trip_audit -> trip_audit)
├── indexes/            # Composite B-Tree index creation scripts (001_indexes.sql)
├── queries/            # 18 Analytical SQL benchmark queries (001_reports.sql)
├── transactions/       # Multi-table atomic persistence & rollback scripts (001_save_itinerary.sql)
├── tests/              # Database integrity & constraint validation scripts (001_constraints.sql)
├── backups/            # Local logical backup dumps
├── reports/            # Detailed D1-D5 dataset seeding and validation reports
└── design/             # Entity-Relationship diagram and Normalization proofs
```

---

## 2. Execution Order for PostgreSQL Database Objects

When deploying or recreating database objects on PostgreSQL (via Supabase SQL Editor or `psql`):

1. **Alembic Baseline Migration (Primary Table DDL):**
   ```powershell
   cd backend
   python -m alembic upgrade head
   ```
2. **Seed Data:**
   Execute `database/seeds/001_seed.sql` or run seeding scripts in `scripts/database/`.
3. **Database Views:**
   Execute `database/views/001_views.sql`.
4. **Stored Functions:**
   Execute `database/functions/001_budget_functions.sql`.
5. **Stored Procedures:**
   Execute `database/procedures/001_refresh_trip_total.sql`.
6. **Audit Triggers:**
   Execute `database/triggers/001_audit_trip.sql`.
7. **Performance Indexes:**
   Execute `database/indexes/001_indexes.sql`.

---

## 3. Database Verification & Reports

* **Analytical Queries:** Execute `database/queries/001_reports.sql` for 18 demonstration queries.
* **Integrity & Constraints:** Run `database/tests/001_constraints.sql`.
* **Transaction Rollback:** Test atomic transaction failure handling via `database/transactions/001_save_itinerary.sql`.
* **Dataset Reports:** See [docs/datasets/CATALOGUE_DATASETS_REPORT.md](../docs/datasets/CATALOGUE_DATASETS_REPORT.md).
