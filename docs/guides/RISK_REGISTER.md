# Technical Risk Register

**Project:** RoamGenie — AI Travel Planner & Budget Optimizer  
**Course:** Database Management Systems (Semester 5 Theory & Project)  
**Execution Model:** Solo Developer  
**Status:** Reconciled Risk Inventory

---

## 1. Technical & Operational Risks

| Risk ID | Risk Description | Probability | Impact | Mitigation Strategy | Contingency Plan |
| :---: | :--- | :---: | :---: | :--- | :--- |
| **TR-01** | **Supabase Internet Dependency during Live Demo** | Medium | High | Rehearse offline fallback; preload demo seeds into database before presentation. | Switch to local PostgreSQL (`DATABASE_ENV=local`) or use verified live test evidence. |
| **TR-02** | **External AI API Rate Limit / Network Outage** | High | High | Enforce deterministic `MockAIService` / `DeterministicScheduler` as default; isolate real LLMs behind a 15-second timeout. | The orchestrator falls back automatically to `DeterministicScheduler` with zero user disruption. |
| **TR-03** | **Alembic Migration & DDL Schema Drift** | Medium | High | Treat Alembic as sole application DDL owner; do not execute manual ad-hoc DDL in Supabase Studio. | Reset dev schema from clean baseline and replay `python -m alembic upgrade head`. |
| **TR-04** | **Connection Pooling Incompatibility** | Medium | Medium | Use session-compatible connection pooling via SQLAlchemy `psycopg` pool (`pool_pre_ping=True`). | Connect via direct PostgreSQL URI for migrations if pooler drops session state. |
| **TR-05** | **Secret / Credential Leakage** | Low | Critical | Strict `.gitignore` on `.env`; verify zero credentials in client-side bundles. | Immediately rotate leaked Supabase/JWT secrets and purge git history. |
| **TR-06** | **Unauthenticated SQL Execution on Reports Endpoint** | Medium | High | Restrict `/reports/execute-sql` to authenticated admin users; block queries on `users` table. | Implemented in M1 remediation phase. |
| **TR-07** | **Large Catalogue Query Latency** | Low | Medium | Add composite B-Tree indexes on `hotels`, `restaurants`, `attractions`, and `transport_options`. | Implemented in `001_indexes.sql`. |
