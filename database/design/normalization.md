# Normalization

**UNF:** one trip record repeats traveller names, preferences, daily items, hotel/restaurant details and expenses. Repeating groups cause update and deletion anomalies.

**1NF:** one atomic value per column and one row per traveller, preference, itinerary item and expense. Arrays are not used for facts that must be queried relationally.

**2NF:** association tables use the full relationship key; attributes such as activity name do not depend on only part of `(user_id, activity)` and item details do not sit in a trip-item composite row.

**3NF:** destination facts move out of trips; hotel/restaurant/attraction facts depend on their own keys; user facts move out of trips; itinerary day date depends on itinerary/day number. Non-key facts no longer depend transitively on another non-key fact.

**BCNF:** current relations use candidate keys whose determinants are keys, such as `users.email`, `(city,country)`, `(itinerary_id,day_number)`, `(trip_id,category)` and `(user_id,trip_id)`. Recheck when transport routes, reviews and external provider identifiers are finalized. Deliberate snapshots (weather/provider response) preserve historical observations and are not catalogue duplication.

