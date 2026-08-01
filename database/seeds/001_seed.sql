BEGIN;
INSERT INTO destinations(city,country,description,average_daily_cost) VALUES
('Mysuru','India','Palaces, markets and heritage',3500),('Kochi','India','Coastal history and food',4200),('Jaipur','India','Forts, crafts and cuisine',4000)
ON CONFLICT(city,country) DO NOTHING;
INSERT INTO hotels(destination_id,name,price_per_night,rating) SELECT id,'Heritage Garden Stay',2800,4.3 FROM destinations WHERE city='Mysuru' ON CONFLICT DO NOTHING;
INSERT INTO restaurants(destination_id,name,cuisine,average_cost_per_person,rating) SELECT id,'Mysuru Tiffin House','South Indian',350,4.5 FROM destinations WHERE city='Mysuru' ON CONFLICT DO NOTHING;
INSERT INTO attractions(destination_id,name,category,entry_fee,rating) SELECT id,'Mysuru Palace','heritage',120,4.7 FROM destinations WHERE city='Mysuru' ON CONFLICT DO NOTHING;
INSERT INTO transport_options(origin,destination_id,mode,provider,estimated_cost,duration_minutes) SELECT 'Chennai',id,'train','Demo Rail',950,540 FROM destinations WHERE city='Mysuru';
COMMIT;

