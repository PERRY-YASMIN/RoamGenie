# System Architecture

See `../ARCHITECTURE.md` for the diagram. React owns presentation/state and calls only FastAPI. FastAPI routers validate transport concerns, services enforce rules, repositories use SQLAlchemy/PostgreSQL, and adapters isolate AI/weather providers. Accepted AI proposals become persistent only through services and a transaction. JWT protects user resources; admin role protects catalogue mutation.

<!-- SUPABASE_UPDATE_START -->
## Supabase deployment

The deployed path is React → FastAPI → Supabase-hosted PostgreSQL. SQLAlchemy owns application access and sessions; Alembic owns schema evolution; PostgreSQL SQL files demonstrate DBMS objects. Dashboard/Table Editor/SQL Editor/logs and optional psql/DBeaver/pgAdmin are administrative tools only.
<!-- SUPABASE_UPDATE_END -->
