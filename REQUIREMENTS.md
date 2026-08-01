# Requirements

## Functional

FR-01 register/login/logout and protected profile; FR-02 manage preferences; FR-03 browse/filter destinations, hotels, restaurants, attractions and transport; FR-04 create/edit/delete trips; FR-05 validate dates, travellers and budget; FR-06 generate a day-wise itinerary from approved records; FR-07 allocate and total category costs; FR-08 warn on deficit; FR-09 save/reopen itinerary history; FR-10 AI recommendations/Q&A/packing with mock fallback; FR-11 weather with fallback; FR-12 admin-safe catalogue management; FR-13 reports demonstrating SQL concepts; FR-14 auditable important changes.

## Non-functional

- Security: hashed passwords, JWT expiry, least privilege, input validation, no secrets/stack traces.
- Reliability: mock fallbacks; transactions for multi-step saves; backups tested.
- Performance: paginated lists; indexes verified with plans; target common API response under 2 s locally excluding external AI.
- Usability: responsive at 360/768/1440 px; accessible labels/keyboard focus; understandable errors.
- Maintainability: layered modules, migrations, contract versioning, small reviewed PRs.
- Portability: documented Windows PowerShell setup; environment-driven URLs.
- Data integrity: PostgreSQL PK/FK/unique/check constraints and UTC timestamps.
- Testability: unit, database, integration and acceptance commands run from a clean clone.

Out of scope for v1: bookings/payments, live navigation, visa guarantees, autonomous purchases, AI database access, and production-scale availability.

<!-- SUPABASE_UPDATE_START -->
## Database platform requirements

NFR-DB1 Supabase-hosted PostgreSQL is the primary team database. NFR-DB2 FastAPI uses environment-only `DATABASE_URL` through SQLAlchemy/psycopg. NFR-DB3 Alembic is the main application schema evolution path; course SQL objects remain version controlled and PostgreSQL-compatible. NFR-DB4 manual Dashboard changes are incomplete until reproduced in Git. NFR-DB5 frontend and AI receive no database/service-role credentials. NFR-DB6 local PostgreSQL is an optional isolated fallback rebuilt from the same migrations/seeds.
<!-- SUPABASE_UPDATE_END -->
