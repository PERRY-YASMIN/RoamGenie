CREATE OR REPLACE VIEW v_trip_budget_summary AS
SELECT t.id trip_id,t.user_id,t.total_budget,t.estimated_total,
       t.total_budget-t.estimated_total remaining_budget,
       (t.estimated_total>t.total_budget) is_over_budget
FROM trips t;

CREATE OR REPLACE VIEW v_destination_catalogue AS
SELECT d.id,d.city,d.country,count(DISTINCT h.id) hotel_count,
       count(DISTINCT r.id) restaurant_count,count(DISTINCT a.id) attraction_count
FROM destinations d LEFT JOIN hotels h ON h.destination_id=d.id
LEFT JOIN restaurants r ON r.destination_id=d.id
LEFT JOIN attractions a ON a.destination_id=d.id GROUP BY d.id;

