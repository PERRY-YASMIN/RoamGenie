# Demo Guide

Preload non-sensitive seed data; use mock AI; keep a tested backup database and screenshots. Rehearse this 7-minute flow: problem (30s) → architecture/ERD (60s) → register/login (45s) → browse destination (30s) → create trip (45s) → generate itinerary/packing (60s) → budget warning (45s) → save/reopen (45s) → SQL view/function/trigger/transaction (60s) → tests/conclusion (40s). If a service fails, explain the fallback and continue from saved screenshots. Never debug secrets live.

<!-- SUPABASE_UPDATE_START -->
## Supabase database demonstration

Explain: “Supabase is our managed cloud platform for PostgreSQL. PostgreSQL is the DBMS. React calls FastAPI; FastAPI validates and uses SQLAlchemy to access it.” Show architecture → Dashboard core tables/FKs/sample rows → SQL Editor JOIN → aggregate budget query → view → function/procedure → trigger audit → transaction/index explanation → return to React full flow. Offline pack: database/SQL result/ERD/architecture/API/frontend screenshots and optional recording.
<!-- SUPABASE_UPDATE_END -->
