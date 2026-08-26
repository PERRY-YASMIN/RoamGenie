# Alembic Revisions

This directory contains version-controlled database migrations for RoamGenie.

* **Initial Schema Migration:** `001_initial_schema.py` defines the foundational 22-table PostgreSQL schema with identity columns, constraints, foreign key cascades, and indexes.

To apply migrations on an active PostgreSQL database instance:
```powershell
cd backend
python -m alembic upgrade head
```
