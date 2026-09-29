-- ============================================================================
-- RoamGenie — Transaction Control Language (TCL) Demonstrations
-- Demonstrates: BEGIN, COMMIT, ROLLBACK, SAVEPOINT, ROLLBACK TO SAVEPOINT
-- Valid PostgreSQL 15+ syntax for atomic itinerary saving and safe rollback
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Demonstration 1: Multi-entity Atomic Itinerary Persistence (BEGIN / COMMIT)
-- Ensures itinerary header, scheduled day, and item entries succeed together.
-- ----------------------------------------------------------------------------
BEGIN;

-- Insert itinerary record
INSERT INTO itineraries (trip_id, version, summary, provider)
VALUES (1, 1, 'Golden Triangle Exploration', 'engine-v2')
ON CONFLICT (trip_id, version) DO UPDATE SET summary = EXCLUDED.summary;

-- Insert day 1
INSERT INTO itinerary_days (itinerary_id, day_number, itinerary_date)
VALUES (
    (SELECT id FROM itineraries WHERE trip_id = 1 AND version = 1),
    1,
    '2026-10-15'
)
ON CONFLICT (itinerary_id, day_number) DO NOTHING;

-- Insert item
INSERT INTO itinerary_items (itinerary_day_id, item_order, start_time, title, category, estimated_cost, notes)
VALUES (
    (SELECT id FROM itinerary_days WHERE itinerary_id = (SELECT id FROM itineraries WHERE trip_id = 1 AND version = 1) AND day_number = 1),
    1,
    '09:00',
    'Amber Fort Guided Heritage Walk',
    'attractions',
    250.00,
    'Ascend to royal courtyards and palace chambers'
)
ON CONFLICT (itinerary_day_id, item_order) DO UPDATE SET estimated_cost = EXCLUDED.estimated_cost;

-- Mark trip as planned atomically with itinerary persistence
UPDATE trips SET status = 'planned', updated_at = now() WHERE id = 1;

COMMIT;

-- ----------------------------------------------------------------------------
-- Demonstration 2: Full Transaction Abort (BEGIN / ROLLBACK)
-- Simulates an invalid operation rolling back without leaving orphaned rows.
-- ----------------------------------------------------------------------------
BEGIN;

INSERT INTO expenses (trip_id, category, description, amount, incurred_on)
VALUES (1, 'attractions', 'Temporary unverified ticket booking', 999.00, '2026-10-15');

-- Rollback the transaction: verify that no dirty reads or orphaned records remain
ROLLBACK;

-- ----------------------------------------------------------------------------
-- Demonstration 3: Nested Transaction Checkpoints (SAVEPOINT / ROLLBACK TO)
-- Demonstrates partial rollback: a core expense is saved, a speculative booking
-- triggers an issue and rolls back to savepoint, then valid data commits.
-- ----------------------------------------------------------------------------
BEGIN;

-- Step 3a: Core valid expense record
INSERT INTO expenses (trip_id, category, description, amount, incurred_on)
VALUES (1, 'transportation', 'Confirmed Express Train Transit', 850.00, '2026-10-15');

-- Step 3b: Set a transactional checkpoint
SAVEPOINT speculative_activity_booking;

-- Step 3c: Insert tentative / speculative activity expense
INSERT INTO expenses (trip_id, category, description, amount, incurred_on)
VALUES (1, 'attractions', 'Speculative Balloon Safari Reservation', 12000.00, '2026-10-15');

-- Step 3d: Weather or budget check detects deficit -> rollback speculative branch only
ROLLBACK TO SAVEPOINT speculative_activity_booking;

-- Step 3e: Release savepoint and commit valid core transit transaction
RELEASE SAVEPOINT speculative_activity_booking;

COMMIT;
