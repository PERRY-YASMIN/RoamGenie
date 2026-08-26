# Relational Normalization Proofs (1NF to BCNF)

**Project:** RoamGenie — AI Travel Planner & Budget Optimizer  
**Course:** Database Management Systems (Semester 5 Theory & Project)  
**Target:** Formal Mathematical Normalization Proofs for 22 Relational Tables

---

## 1. Normalization Summary Table

| Entity Relation | Functional Dependencies | Key Attributes | Violations Resolved | Normal Form Achieved |
| :--- | :--- | :--- | :--- | :---: |
| `users` | `id -> email, password_hash, full_name, role, created_at, updated_at`<br>`email -> id, ...` | `id` (PK), `email` (CK) | Atomic fields, no multi-valued attributes. | **BCNF** |
| `user_preferences` | `user_id -> hotel_pref, food_pref, transport_pref, travel_style, special_req` | `user_id` (PK) | 1:1 decomposition from `users`. | **BCNF** |
| `activity_preferences`| `(user_id, activity) -> {}` | `(user_id, activity)` (PK) | Multi-valued activity tags extracted into 1NF table. | **BCNF** |
| `destinations` | `id -> city, country, description, average_daily_cost, active`<br>`(city, country) -> id, ...` | `id` (PK), `(city, country)` (CK) | Eliminates duplicate city names across countries. | **BCNF** |
| `hotels` | `id -> destination_id, name, price_per_night, rating`<br>`(destination_id, name) -> id, ...` | `id` (PK), `(destination_id, name)` (CK) | Nightly price depends on hotel, not destination. | **BCNF** |
| `restaurants` | `id -> destination_id, name, cuisine, average_cost_per_person, rating`<br>`(destination_id, name) -> id, ...` | `id` (PK), `(destination_id, name)` (CK) | Cuisine & meal cost depend on restaurant. | **BCNF** |
| `attractions` | `id -> destination_id, name, category, entry_fee, rating`<br>`(destination_id, name) -> id, ...` | `id` (PK), `(destination_id, name)` (CK) | Entry fees depend on attraction. | **BCNF** |
| `transport_options` | `id -> origin, destination_id, mode, provider, estimated_cost, duration_minutes` | `id` (PK) | Transit route decoupled from trip. | **BCNF** |
| `trips` | `id -> user_id, destination_id, starting_location, start_date, end_date, traveller_count, total_budget, estimated_total, status, created_at, updated_at` | `id` (PK) | Trip dates & budget depend on trip ID. | **BCNF** |
| `trip_members` | `id -> trip_id, display_name, age_group, special_requirements` | `id` (PK) | Multi-person travellers decomposed into 1NF relation. | **BCNF** |
| `itineraries` | `id -> trip_id, version, summary, provider, created_at`<br>`(trip_id, version) -> id, ...` | `id` (PK), `(trip_id, version)` (CK) | Historical versions tracked independently. | **BCNF** |
| `itinerary_days` | `id -> itinerary_id, day_number, itinerary_date`<br>`(itinerary_id, day_number) -> id, ...` | `id` (PK), `(itinerary_id, day_number)` (CK) | Days partitioned from itinerary summary. | **BCNF** |
| `itinerary_items` | `id -> itinerary_day_id, item_order, start_time, title, category, estimated_cost, notes`<br>`(itinerary_day_id, item_order) -> id, ...` | `id` (PK), `(itinerary_day_id, item_order)` (CK) | Daily events sequenced without repeating groups. | **BCNF** |
| `budget_allocations` | `id -> trip_id, category, amount`<br>`(trip_id, category) -> id, ...` | `id` (PK), `(trip_id, category)` (CK) | Category budgets separated from trip header. | **BCNF** |
| `expenses` | `id -> trip_id, category, description, amount, incurred_on` | `id` (PK) | Incurred expenses logged independently. | **BCNF** |
| `saved_trips` | `id -> user_id, trip_id, saved_at`<br>`(user_id, trip_id) -> id, ...` | `id` (PK), `(user_id, trip_id)` (CK) | M:N association table between users and trips. | **BCNF** |
| `reviews` | `id -> user_id, destination_id, rating, comment`<br>`(user_id, destination_id) -> id, ...` | `id` (PK), `(user_id, destination_id)` (CK) | M:N association table between users and destinations. | **BCNF** |
| `packing_items` | `id -> trip_id, item, category, is_packed`<br>`(trip_id, item) -> id, ...` | `id` (PK), `(trip_id, item)` (CK) | Checklist items extracted to prevent comma-separated text. | **BCNF** |
| `ai_conversations` | `id -> user_id, trip_id, created_at` | `id` (PK) | Chat sessions decoupled from user credentials. | **BCNF** |
| `ai_messages` | `id -> conversation_id, role, content, created_at` | `id` (PK) | Ordered chat turns in 1NF. | **BCNF** |
| `weather_snapshots` | `id -> destination_id, observed_at, summary, temperature_c, provider` | `id` (PK) | Weather observations decoupled from destination metadata. | **BCNF** |
| `trip_audit` | `id -> trip_id, action, changed_at, changed_by, old_row, new_row` | `id` (PK) | Append-only audit table with JSONB delta columns. | **BCNF** |

---

## 2. Normalization Step Proofs

### First Normal Form (1NF)
* All attributes contain atomic, indivisible values.
* Multi-valued activity tags are placed into `activity_preferences` (one tag per row).
* Multi-valued packing checklist items are stored as discrete rows in `packing_items`.
* Day-wise itinerary items are sequenced as individual rows in `itinerary_items` rather than stored in unnormalized arrays.

### Second Normal Form (2NF)
* The schema is in 1NF.
* All non-prime attributes are fully functionally dependent on the entire primary key.
* For composite candidate keys (such as `(itinerary_day_id, item_order)`), attributes like `title`, `estimated_cost`, and `start_time` depend on the composite key as a whole, exhibiting zero partial key dependencies.

### Third Normal Form (3NF)
* The schema is in 2NF.
* No transitive functional dependencies exist ($X \rightarrow Y$ and $Y \rightarrow Z$).
* For example, destination city and country are stored in `destinations`. The `hotels` table references `destination_id` rather than storing duplicate destination country strings, eliminating transitive dependency anomalies.

### Boyce-Codd Normal Form (BCNF)
* The schema is in 3NF.
* For every non-trivial functional dependency $X \rightarrow Y$, the determinant $X$ is a superkey (either the primary key `id` or a defined candidate key with a unique constraint).
* Therefore, all 22 tables strictly satisfy **BCNF**.
