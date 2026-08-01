-- Q01 active destinations ordered by daily cost
SELECT city,country,average_daily_cost FROM destinations WHERE active ORDER BY average_daily_cost;
-- Q02 INNER JOIN hotels with destination
SELECT d.city,h.name,h.price_per_night FROM destinations d JOIN hotels h ON h.destination_id=d.id;
-- Q03 LEFT JOIN destinations even without attractions
SELECT d.city,count(a.id) attraction_count FROM destinations d LEFT JOIN attractions a ON a.destination_id=d.id GROUP BY d.id;
-- Q04 RIGHT JOIN teaching example retaining every destination
SELECT d.city,r.name FROM restaurants r RIGHT JOIN destinations d ON d.id=r.destination_id ORDER BY d.city;
-- Q05 multi-table trip/user/destination join
SELECT t.id,u.email,d.city,t.total_budget FROM trips t JOIN users u ON u.id=t.user_id JOIN destinations d ON d.id=t.destination_id;
-- Q06 aggregate expense by trip/category
SELECT trip_id,category,sum(amount) spent FROM expenses GROUP BY trip_id,category ORDER BY trip_id,category;
-- Q07 trips over budget
SELECT id,total_budget,estimated_total,estimated_total-total_budget deficit FROM trips WHERE estimated_total>total_budget;
-- Q08 subquery: above-average hotel prices
SELECT name,price_per_night FROM hotels WHERE price_per_night>(SELECT avg(price_per_night) FROM hotels);
-- Q09 correlated subquery: destination's highest-rated attraction
SELECT d.city,a.name,a.rating FROM destinations d JOIN attractions a ON a.destination_id=d.id WHERE a.rating=(SELECT max(x.rating) FROM attractions x WHERE x.destination_id=d.id);
-- Q10 itinerary day/item schedule
SELECT i.trip_id,dy.day_number,it.item_order,it.title,it.estimated_cost FROM itineraries i JOIN itinerary_days dy ON dy.itinerary_id=i.id JOIN itinerary_items it ON it.itinerary_day_id=dy.id ORDER BY i.trip_id,dy.day_number,it.item_order;
-- Q11 saved trips per user
SELECT u.email,count(s.id) saved_count FROM users u LEFT JOIN saved_trips s ON s.user_id=u.id GROUP BY u.id;
-- Q12 average ratings by destination
SELECT d.city,round(avg(rv.rating),2) user_rating FROM destinations d LEFT JOIN reviews rv ON rv.destination_id=d.id GROUP BY d.id;
-- Q13 budget allocation percentage
SELECT trip_id,category,amount,round(amount*100/nullif(sum(amount) OVER(PARTITION BY trip_id),0),2) pct FROM budget_allocations;
-- Q14 packing progress
SELECT trip_id,count(*) FILTER(WHERE is_packed) packed,count(*) total FROM packing_items GROUP BY trip_id;
-- Q15 AI conversation message counts
SELECT c.id,c.user_id,count(m.id) messages FROM ai_conversations c LEFT JOIN ai_messages m ON m.conversation_id=c.id GROUP BY c.id;
-- Q16 transport choices under a budget
SELECT d.city,t.mode,t.provider,t.estimated_cost FROM transport_options t JOIN destinations d ON d.id=t.destination_id WHERE t.estimated_cost<=2000 ORDER BY t.estimated_cost;
-- Q17 dates with weather snapshots
SELECT d.city,w.observed_at,w.summary,w.temperature_c FROM weather_snapshots w JOIN destinations d ON d.id=w.destination_id ORDER BY w.observed_at DESC;
-- Q18 users preferring heritage
SELECT u.full_name FROM users u WHERE EXISTS(SELECT 1 FROM activity_preferences p WHERE p.user_id=u.id AND p.activity='heritage');

