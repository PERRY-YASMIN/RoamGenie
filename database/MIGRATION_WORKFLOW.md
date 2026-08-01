# Schema and Migration Workflow

1. Samyuktha records and approves the design change.
2. Sashtika reviews required PostgreSQL objects and DDL ownership.
3. Yasmin updates SQLAlchemy models.
4. Create or hand-write: `alembic revision --autogenerate -m "describe change"`.
5. Review generated upgrade/downgrade—autogeneration is never trusted blindly.
6. Test on a safe empty/development database.
7. Check `alembic current`, `alembic history`, `alembic upgrade head`; test `alembic downgrade -1` when safe, then re-upgrade.
8. Apply the reviewed migration to Supabase using an appropriate direct/session connection.
9. Update course SQL scripts, dictionary, ERD, API/frontend contracts and status.
10. Run database/API/integration tests, capture Dashboard evidence, commit and merge.

Alembic owns application table evolution. Standalone SQL owns seed/demo queries and reviewed PostgreSQL objects not managed by ORM migration. Never create the same object independently in both paths.
