# Database Architecture

PostgreSQL is authoritative. Users own preferences, trips and saved references. Trips have travellers, allocations, expenses and itineraries; itineraries have ordered days/items. Catalogue records are referenced, not copied where identity matters. Weather and AI conversations are snapshots/history, not truth for booking. Use surrogate bigint keys, unique natural identifiers where stable, foreign keys, domain checks, UTC timestamps, migrations, least privilege and explicit delete rules. ERD: `../database/design/er-diagram.md`; dictionary: `data-dictionary.md`.

<!-- SUPABASE_UPDATE_START -->
## Source of truth and tools

Supabase hosts the central PostgreSQL database. GitHub migrations and SQL files—not Dashboard state—make it reproducible. Alembic creates/evolves application tables; reviewed scripts create or demonstrate views, functions, procedures, purposeful triggers, transactions, reports and indexes. Avoid duplicate DDL ownership. Every manual Table Editor or SQL Editor change must become a reviewed migration/script.
<!-- SUPABASE_UPDATE_END -->
