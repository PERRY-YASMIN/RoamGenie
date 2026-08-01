-- Replace :trip_id through psql variables. Entire plan save succeeds or rolls back.
BEGIN;
INSERT INTO itineraries(trip_id,version,summary,provider)
VALUES(:trip_id,1,'Validated demo itinerary','mock') RETURNING id \gset
INSERT INTO itinerary_days(itinerary_id,day_number,itinerary_date)
SELECT :id,1,start_date FROM trips WHERE id=:trip_id RETURNING id \gset day_
INSERT INTO itinerary_items(itinerary_day_id,item_order,start_time,title,category,estimated_cost)
VALUES(:day_id,1,'09:00','Destination orientation','activity',0);
UPDATE trips SET status='planned',updated_at=now() WHERE id=:trip_id;
COMMIT;

-- Rollback demonstration (no row remains):
BEGIN;
INSERT INTO expenses(trip_id,category,description,amount) VALUES(:trip_id,'demo','rollback example',1);
ROLLBACK;

