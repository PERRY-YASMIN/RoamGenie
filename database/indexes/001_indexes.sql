CREATE INDEX IF NOT EXISTS idx_trips_user_dates ON trips(user_id,start_date DESC);
CREATE INDEX IF NOT EXISTS idx_trips_destination ON trips(destination_id);
CREATE INDEX IF NOT EXISTS idx_hotels_destination_price ON hotels(destination_id,price_per_night);
CREATE INDEX IF NOT EXISTS idx_attractions_destination_category ON attractions(destination_id,category);
CREATE INDEX IF NOT EXISTS idx_expenses_trip_category ON expenses(trip_id,category);
CREATE INDEX IF NOT EXISTS idx_itinerary_days_itinerary ON itinerary_days(itinerary_id,day_number);
-- Verify with EXPLAIN (ANALYZE,BUFFERS) on realistic data; remove unused indexes after evidence.

