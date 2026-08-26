-- RoamGenie Development Seed Dataset (Phase 1)
-- Populates representative sample data across all 19 domain entities
BEGIN;

-- 1. Users (password is 'Password123!' hashed with Argon2id)
INSERT INTO users (id, email, password_hash, full_name, role) OVERRIDING SYSTEM VALUE VALUES
(1, 'admin@roamgenie.internal', '$argon2id$v=19$m=65536,t=3,p=4$w6sX0U5o2z9a$k7Q8b9zY4X1...', 'System Administrator', 'admin'),
(2, 'traveller@roamgenie.internal', '$argon2id$v=19$m=65536,t=3,p=4$w6sX0U5o2z9a$k7Q8b9zY4X1...', 'Arun Kumar', 'traveller'),
(3, 'ananya@roamgenie.internal', '$argon2id$v=19$m=65536,t=3,p=4$w6sX0U5o2z9a$k7Q8b9zY4X1...', 'Ananya Sharma', 'traveller')
ON CONFLICT (email) DO NOTHING;

-- 2. User Preferences
INSERT INTO user_preferences (user_id, hotel_preference, food_preference, transport_preference, travel_style, special_requirements) VALUES
(2, 'heritage', 'South Indian Vegetarian', 'train', 'cultural', 'Near ground floor'),
(3, 'boutique', 'Local Seafood & Multi-cuisine', 'flight', 'relaxed', 'Window seating')
ON CONFLICT (user_id) DO NOTHING;

-- 3. Activity Preferences
INSERT INTO activity_preferences (user_id, activity) VALUES
(2, 'heritage'), (2, 'palaces'), (2, 'temples'),
(3, 'coastal'), (3, 'photography'), (3, 'culinary')
ON CONFLICT (user_id, activity) DO NOTHING;

-- 4. Destinations
INSERT INTO destinations (id, city, country, description, average_daily_cost, active) OVERRIDING SYSTEM VALUE VALUES
(1, 'Mysuru', 'India', 'City of palaces, royal heritage, silk, and aromatic sandalwood.', 3500.00, true),
(2, 'Kochi', 'India', 'Vibrant coastal port known for Fort Kochi, spice markets, and Chinese fishing nets.', 4200.00, true),
(3, 'Jaipur', 'India', 'The Pink City of Rajasthan featuring majestic hilltop forts and rich culinary traditions.', 4000.00, true),
(4, 'Udaipur', 'India', 'City of Lakes surrounded by the Aravalli hills and opulent marble palaces.', 4500.00, true),
(5, 'Goa', 'India', 'Golden beaches, Portuguese heritage architecture, and coastal seafood dining.', 5000.00, true)
ON CONFLICT (city, country) DO NOTHING;

-- 5. Hotels
INSERT INTO hotels (id, destination_id, name, price_per_night, rating) OVERRIDING SYSTEM VALUE VALUES
(1, 1, 'Heritage Garden Stay', 2800.00, 4.3),
(2, 1, 'Royal Orchid Metropole', 4500.00, 4.7),
(3, 2, 'Brunton Boatyard', 6500.00, 4.8),
(4, 2, 'Fort Kochi Heritage Inn', 3200.00, 4.2),
(5, 3, 'Umaid Bhawan Haveli', 3800.00, 4.5),
(6, 4, 'Lakeview Haveli', 4200.00, 4.6),
(7, 5, 'Candolim Beach Resort', 4800.00, 4.4)
ON CONFLICT (destination_id, name) DO NOTHING;

-- 6. Restaurants
INSERT INTO restaurants (id, destination_id, name, cuisine, average_cost_per_person, rating) OVERRIDING SYSTEM VALUE VALUES
(1, 1, 'Mylari Tiffin House', 'South Indian', 250.00, 4.8),
(2, 1, 'Gufha Cave Dining', 'North Indian & Mughlai', 650.00, 4.3),
(3, 2, 'Seagull Fort Kochi', 'Seafood & Kerala', 600.00, 4.5),
(4, 2, 'Kashi Art Cafe', 'Continental & Bakery', 450.00, 4.6),
(5, 3, 'Laxmi Mishthan Bhandar (LMB)', 'Rajasthani Thali', 550.00, 4.7),
(6, 4, 'Ambrai Waterfront Restaurant', 'Rajasthani & Continental', 850.00, 4.8),
(7, 5, 'Fisherman''s Wharf', 'Goan Seafood', 750.00, 4.6)
ON CONFLICT (destination_id, name) DO NOTHING;

-- 7. Attractions
INSERT INTO attractions (id, destination_id, name, category, entry_fee, rating) OVERRIDING SYSTEM VALUE VALUES
(1, 1, 'Mysuru Palace', 'heritage', 100.00, 4.9),
(2, 1, 'Chamundi Hill & Temple', 'temple', 0.00, 4.6),
(3, 1, 'Brindavan Gardens', 'nature', 50.00, 4.2),
(4, 2, 'Fort Kochi Beach & Nets', 'nature', 0.00, 4.5),
(5, 2, 'Mattancherry Palace', 'heritage', 25.00, 4.3),
(6, 3, 'Amber Palace & Fort', 'heritage', 200.00, 4.8),
(7, 3, 'Hawa Mahal', 'heritage', 50.00, 4.6),
(8, 4, 'City Palace Udaipur', 'heritage', 300.00, 4.9),
(9, 4, 'Saheliyon-ki-Bari', 'nature', 50.00, 4.4),
(10, 5, 'Aguada Fort & Lighthouse', 'heritage', 50.00, 4.5)
ON CONFLICT (destination_id, name) DO NOTHING;

-- 8. Transport Options
INSERT INTO transport_options (id, origin, destination_id, mode, provider, estimated_cost, duration_minutes) OVERRIDING SYSTEM VALUE VALUES
(1, 'Bengaluru', 1, 'train', 'Vande Bharat Express', 550.00, 120),
(2, 'Bengaluru', 1, 'bus', 'KSRTC Airavat', 450.00, 180),
(3, 'Chennai', 1, 'train', 'Kaveri Express', 850.00, 480),
(4, 'Bengaluru', 2, 'flight', 'IndiGo', 3200.00, 65),
(5, 'Bengaluru', 2, 'train', 'Ernakulam Express', 1100.00, 580),
(6, 'Delhi', 3, 'train', 'Ajmer Shatabdi', 750.00, 240),
(7, 'Mumbai', 4, 'flight', 'Air India', 4500.00, 80),
(8, 'Mumbai', 5, 'train', 'Konkan Kanya Express', 950.00, 660)
ON CONFLICT DO NOTHING;

-- 9. Sample Trips
INSERT INTO trips (id, user_id, destination_id, starting_location, start_date, end_date, traveller_count, total_budget, estimated_total, status) OVERRIDING SYSTEM VALUE VALUES
(1, 2, 1, 'Bengaluru', '2026-09-15', '2026-09-17', 2, 15000.00, 11200.00, 'planned'),
(2, 3, 2, 'Bengaluru', '2026-10-01', '2026-10-04', 2, 25000.00, 19800.00, 'draft')
ON CONFLICT DO NOTHING;

-- 10. Trip Members
INSERT INTO trip_members (trip_id, display_name, age_group, special_requirements) VALUES
(1, 'Arun Kumar', 'adult', 'Lead traveller'),
(1, 'Suresh Kumar', 'senior', 'Ground floor room required'),
(2, 'Ananya Sharma', 'adult', 'Lead traveller'),
(2, 'Pooja Sharma', 'adult', NULL)
ON CONFLICT DO NOTHING;

-- 11. Itineraries
INSERT INTO itineraries (id, trip_id, version, summary, provider) OVERRIDING SYSTEM VALUE VALUES
(1, 1, 1, '3-Day Cultural & Royal Heritage Tour of Mysuru', 'mock')
ON CONFLICT (trip_id, version) DO NOTHING;

-- 12. Itinerary Days
INSERT INTO itinerary_days (id, itinerary_id, day_number, itinerary_date) OVERRIDING SYSTEM VALUE VALUES
(1, 1, 1, '2026-09-15'),
(2, 1, 2, '2026-09-16'),
(3, 1, 3, '2026-09-17')
ON CONFLICT (itinerary_id, day_number) DO NOTHING;

-- 13. Itinerary Items
INSERT INTO itinerary_items (itinerary_day_id, item_order, start_time, title, category, estimated_cost, notes) VALUES
(1, 1, '09:00', 'Check-in at Heritage Garden Stay', 'hotel', 2800.00, 'Confirm reservation under Arun Kumar'),
(1, 2, '11:00', 'Explore Mysuru Palace', 'attraction', 200.00, 'Audio guide included'),
(1, 3, '13:30', 'Lunch at Mylari Tiffin House', 'food', 500.00, 'Try traditional Mylari dosas'),
(1, 4, '16:00', 'Visit Chamundi Hill & Temple', 'attraction', 0.00, 'Scenic panoramic view of the city'),
(2, 1, '10:00', 'Brindavan Gardens Walk & Musical Fountains', 'attraction', 100.00, 'Evening illumination'),
(2, 2, '19:30', 'Dinner at Gufha Cave Dining', 'food', 1300.00, 'Themed ambiance')
ON CONFLICT (itinerary_day_id, item_order) DO NOTHING;

-- 14. Budget Allocations
INSERT INTO budget_allocations (trip_id, category, amount) VALUES
(1, 'accommodation', 5600.00),
(1, 'food', 2800.00),
(1, 'activities', 1200.00),
(1, 'transportation', 1600.00)
ON CONFLICT (trip_id, category) DO NOTHING;

-- 15. Expenses
INSERT INTO expenses (trip_id, category, description, amount, incurred_on) VALUES
(1, 'transportation', 'Train tickets (Vande Bharat return)', 1100.00, '2026-09-15'),
(1, 'food', 'Breakfast at station', 220.00, '2026-09-15')
ON CONFLICT DO NOTHING;

-- 16. Saved Trips
INSERT INTO saved_trips (user_id, trip_id) VALUES
(2, 1)
ON CONFLICT (user_id, trip_id) DO NOTHING;

-- 17. Reviews
INSERT INTO reviews (user_id, destination_id, rating, comment) VALUES
(2, 1, 5, 'Magnificent heritage city, peaceful atmosphere and amazing food!'),
(3, 2, 5, 'Spectacular coastal heritage and wonderful local cafes.')
ON CONFLICT (user_id, destination_id) DO NOTHING;

-- 18. Packing Items
INSERT INTO packing_items (trip_id, item, category, is_packed) VALUES
(1, 'Comfortable sandals/shoes for palace walk', 'clothing', true),
(1, 'Camera & memory cards', 'electronics', true),
(1, 'Prescription medicines', 'essentials', false)
ON CONFLICT (trip_id, item) DO NOTHING;

-- 19. Weather Snapshots
INSERT INTO weather_snapshots (destination_id, observed_at, summary, temperature_c, provider) VALUES
(1, now(), 'Partly cloudy with pleasant evening breeze', 24.5, 'mock'),
(2, now(), 'Humid coastal sunshine with light sea breeze', 29.0, 'mock'),
(3, now(), 'Dry sunny day with warm afternoon', 32.0, 'mock'),
(4, now(), 'Clear skies over lake waters', 27.5, 'mock'),
(5, now(), 'Tropical sunshine with moderate humidity', 30.0, 'mock')
ON CONFLICT DO NOTHING;

COMMIT;
