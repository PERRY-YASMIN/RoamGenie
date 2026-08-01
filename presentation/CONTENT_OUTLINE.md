# Slide Content Outline

1 title/team; 2 problem; 3 objectives/scope; 4 existing vs proposed; 5 architecture; 6 ERD; 7 schema/normalization; 8 modules/UI; 9 API; 10 SQL features; 11 AI validation/fallback; 12 security/testing; 13 demo/results; 14 limitations/future; 15 contributions/Q&A. Keep slides visual and show evidence, not source-code walls.

<!-- SUPABASE_UPDATE_START -->
## Supabase explanation

State exactly: “Supabase is used as the managed cloud platform for our PostgreSQL database. PostgreSQL remains the actual relational DBMS. Supabase provides hosting, a visual table editor, SQL editor, logs, and administrative tools. Our React frontend does not directly access the database. It sends requests to FastAPI, and FastAPI performs validated database operations using SQLAlchemy.” Include the Dashboard-to-SQL-Editor-to-React demonstration from `DEMO_GUIDE.md`.
<!-- SUPABASE_UPDATE_END -->
