# Relational Schema Normalization Analysis (Phase 1)

## 1. Functional Dependencies by Relation

| Relation | Determinant (LHS) | Dependent Attributes (RHS) | Key Type |
| :--- | :--- | :--- | :--- |
| `users` | `id` | `email, password_hash, full_name, role, created_at, updated_at` | Primary Key |
| `users` | `email` | `id, password_hash, full_name, role, created_at, updated_at` | Candidate Key |
| `user_preferences` | `user_id` | `hotel_preference, food_preference, transport_preference, travel_style, special_requirements` | Primary Key |
| `activity_preferences`| `(user_id, activity)` | $\emptyset$ (All key attributes) | Primary Key |
| `destinations` | `id` | `city, country, description, average_daily_cost, active` | Primary Key |
| `destinations` | `(city, country)` | `id, description, average_daily_cost, active` | Candidate Key |
| `hotels` | `id` | `destination_id, name, price_per_night, rating` | Primary Key |
| `hotels` | `(destination_id, name)` | `id, price_per_night, rating` | Candidate Key |
| `restaurants` | `id` | `destination_id, name, cuisine, average_cost_per_person, rating` | Primary Key |
| `restaurants` | `(destination_id, name)`| `id, cuisine, average_cost_per_person, rating` | Candidate Key |
| `attractions` | `id` | `destination_id, name, category, entry_fee, rating` | Primary Key |
| `attractions` | `(destination_id, name)`| `id, category, entry_fee, rating` | Candidate Key |
| `transport_options` | `id` | `origin, destination_id, mode, provider, estimated_cost, duration_minutes` | Primary Key |
| `trips` | `id` | `user_id, destination_id, starting_location, start_date, end_date, traveller_count, total_budget, estimated_total, status, created_at, updated_at` | Primary Key |
| `trip_members` | `id` | `trip_id, display_name, age_group, special_requirements` | Primary Key |
| `itineraries` | `id` | `trip_id, version, summary, provider, created_at` | Primary Key |
| `itineraries` | `(trip_id, version)` | `id, summary, provider, created_at` | Candidate Key |
| `itinerary_days` | `id` | `itinerary_id, day_number, itinerary_date` | Primary Key |
| `itinerary_days` | `(itinerary_id, day_number)` | `id, itinerary_date` | Candidate Key |
| `itinerary_items` | `id` | `itinerary_day_id, item_order, start_time, title, category, estimated_cost, notes` | Primary Key |
| `itinerary_items` | `(itinerary_day_id, item_order)` | `id, start_time, title, category, estimated_cost, notes` | Candidate Key |
| `budget_allocations`| `id` | `trip_id, category, amount` | Primary Key |
| `budget_allocations`| `(trip_id, category)` | `id, amount` | Candidate Key |
| `expenses` | `id` | `trip_id, category, description, amount, incurred_on` | Primary Key |
| `saved_trips` | `id` | `user_id, trip_id, saved_at` | Primary Key |
| `saved_trips` | `(user_id, trip_id)` | `id, saved_at` | Candidate Key |
| `reviews` | `id` | `user_id, destination_id, rating, comment` | Primary Key |
| `reviews` | `(user_id, destination_id)` | `id, rating, comment` | Candidate Key |
| `packing_items` | `id` | `trip_id, item, category, is_packed` | Primary Key |
| `packing_items` | `(trip_id, item)` | `id, category, is_packed` | Candidate Key |

---

## 2. Step-by-Step Normalization Breakdown

### 2.1 First Normal Form (1NF)
* **Rule:** All column values must be atomic (no repeating groups, multi-valued attributes, or comma-separated lists stored in single columns).
* **Decompositions Made:**
  - `activity_preferences` was separated from `user_preferences` so that multiple travel activity interests (e.g. `palaces`, `culinary`, `photography`) are stored as distinct atomic rows.
  - `trip_members` was extracted from `trips` to prevent repeating member columns (`member_1_name`, `member_2_name`, etc.).
  - `itinerary_items` holds atomic events rather than composite plan text blocks.
* **Status:** Fully in 1NF.

### 2.2 Second Normal Form (2NF)
* **Rule:** The relation must be in 1NF and have NO partial dependencies (all non-prime attributes must be fully functionally dependent on the entire primary key).
* **Analysis:**
  - For tables with composite primary keys (`activity_preferences` on `(user_id, activity)`), there are no non-prime attributes.
  - For all other entities, synthetic surrogate primary keys (`id`) ensure that every attribute depends on the single-column primary key `id`.
* **Status:** Fully in 2NF.

### 2.3 Third Normal Form (3NF)
* **Rule:** The relation must be in 2NF and have NO transitive dependencies ($X \rightarrow Y$ and $Y \rightarrow Z$, where $Y$ is not a superkey).
* **Decompositions Made:**
  - Destination city, country, and daily cost are NOT stored in `trips`; `trips` references `destination_id`.
  - Hotel, restaurant, and attraction catalog attributes depend directly on `destinations(id)` and their own PK, not through intermediate foreign entities.
  - User details (e.g., `full_name`, `email`) are never duplicated across `trips`, `reviews`, or `saved_trips`.
* **Status:** Fully in 3NF.

### 2.4 Boyce-Codd Normal Form (BCNF)
* **Rule:** For every functional dependency $X \rightarrow Y$, $X$ must be a superkey (candidate key or primary key).
* **Analysis:**
  - In every relation, all determinants (e.g. `users.email`, `destinations(city, country)`, `itineraries(trip_id, version)`, `itinerary_days(itinerary_id, day_number)`, `budget_allocations(trip_id, category)`, `saved_trips(user_id, trip_id)`, `reviews(user_id, destination_id)`) are candidate keys protected by `UNIQUE` constraints.
* **Status:** Fully in BCNF.

---

## 3. Deliberate Schema Design Choices

1. **Snapshots for Historical Truth:**
   - `weather_snapshots` preserves point-in-time observed temperature and weather data rather than referencing dynamic state, ensuring generated itineraries reflect conditions at planning time.
   - `trip_audit` captures before/after JSON copies of trip modifications for compliance and debugging.
2. **Estimated Total on Trips:**
   - `trips.estimated_total` is cached on the `trips` record and maintained via transactional procedures (`refresh_trip_total`) and backend services for fast list and dashboard rendering without expensive recursive multi-table aggregate joins on every request.
