# Relational Schema
## AI Travel Planner & Budget Optimizer — RoamGenie
### Academic Milestone 5: Relational Schema

---

## 1. Schema Overview

The RoamGenie database schema consists of **22 normalized relational domain tables** (plus one trigger audit ledger), organized into four cohesive architectural subsystems:
1. **User & Preference Subsystem:** `users`, `user_preferences`, `activity_preferences`.
2. **Master Travel Catalogue Subsystem:** `destinations`, `hotels`, `restaurants`, `attractions`, `transport_options`.
3. **Trip & Itinerary Transactional Subsystem:** `trips`, `trip_members`, `itineraries`, `itinerary_days`, `itinerary_items`, `budget_allocations`, `expenses`, `saved_trips`.
4. **AI, Climate & Feedback Subsystem:** `ai_conversations`, `ai_messages`, `weather_snapshots`, `packing_items`, `reviews`, `trip_audit`.

All tables utilize surrogate integer primary keys (`BIGINT IDENTITY`) paired with business candidate keys (`UNIQUE` constraints) and foreign key referential integrity with cascading rules.

---

## 2. Compact Relational Schema Notation

* **`USERS`** (<u>id</u>, email [UK], password_hash, full_name, role, created_at, updated_at)
* **`USER_PREFERENCES`** (<u>user_id</u> $\rightarrow$ `USERS.id`, hotel_preference, food_preference, transport_preference, travel_style, special_requirements)
* **`ACTIVITY_PREFERENCES`** (<u>user_id</u> $\rightarrow$ `USERS.id`, <u>activity</u>)
* **`DESTINATIONS`** (<u>id</u>, city, country, description, average_daily_cost, active, [UK: city, country])
* **`HOTELS`** (<u>id</u>, destination_id $\rightarrow$ `DESTINATIONS.id`, name, price_per_night, rating, [UK: destination_id, name])
* **`RESTAURANTS`** (<u>id</u>, destination_id $\rightarrow$ `DESTINATIONS.id`, name, cuisine, average_cost_per_person, rating, [UK: destination_id, name])
* **`ATTRACTIONS`** (<u>id</u>, destination_id $\rightarrow$ `DESTINATIONS.id`, name, category, entry_fee, rating, [UK: destination_id, name])
* **`TRANSPORT_OPTIONS`** (<u>id</u>, origin, destination_id $\rightarrow$ `DESTINATIONS.id`, mode, provider, estimated_cost, duration_minutes)
* **`TRIPS`** (<u>id</u>, user_id $\rightarrow$ `USERS.id`, destination_id $\rightarrow$ `DESTINATIONS.id`, starting_location, start_date, end_date, traveller_count, total_budget, estimated_total, status, created_at, updated_at)
* **`TRIP_MEMBERS`** (<u>id</u>, trip_id $\rightarrow$ `TRIPS.id`, display_name, age_group, special_requirements)
* **`ITINERARIES`** (<u>id</u>, trip_id $\rightarrow$ `TRIPS.id`, version, summary, provider, created_at, [UK: trip_id, version])
* **`ITINERARY_DAYS`** (<u>id</u>, itinerary_id $\rightarrow$ `ITINERARIES.id`, day_number, itinerary_date, [UK: itinerary_id, day_number])
* **`ITINERARY_ITEMS`** (<u>id</u>, itinerary_day_id $\rightarrow$ `ITINERARY_DAYS.id`, item_order, start_time, title, category, estimated_cost, notes, [UK: itinerary_day_id, item_order])
* **`BUDGET_ALLOCATIONS`** (<u>id</u>, trip_id $\rightarrow$ `TRIPS.id`, category, amount, [UK: trip_id, category])
* **`EXPENSES`** (<u>id</u>, trip_id $\rightarrow$ `TRIPS.id`, category, description, amount, incurred_on)
* **`SAVED_TRIPS`** (<u>id</u>, user_id $\rightarrow$ `USERS.id`, trip_id $\rightarrow$ `TRIPS.id`, saved_at, [UK: user_id, trip_id])
* **`REVIEWS`** (<u>id</u>, user_id $\rightarrow$ `USERS.id`, destination_id $\rightarrow$ `DESTINATIONS.id`, rating, comment, [UK: user_id, destination_id])
* **`AI_CONVERSATIONS`** (<u>id</u>, user_id $\rightarrow$ `USERS.id`, trip_id $\rightarrow$ `TRIPS.id` [Nullable], created_at)
* **`AI_MESSAGES`** (<u>id</u>, conversation_id $\rightarrow$ `AI_CONVERSATIONS.id`, role, content, created_at)
* **`WEATHER_SNAPSHOTS`** (<u>id</u>, destination_id $\rightarrow$ `DESTINATIONS.id`, observed_at, summary, temperature_c, provider)
* **`PACKING_ITEMS`** (<u>id</u>, trip_id $\rightarrow$ `TRIPS.id`, item, category, is_packed, [UK: trip_id, item])
* **`TRIP_AUDIT`** (<u>id</u>, trip_id, action, changed_at, changed_by, old_row, new_row)

---

## 3. Table-by-Table Schema Specification

### 3.1 Table: `users`
Represents registered user accounts.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `email`: `VARCHAR(254) NOT NULL` (UNIQUE)
  - `password_hash`: `TEXT NOT NULL`
  - `full_name`: `VARCHAR(120) NOT NULL`
  - `role`: `VARCHAR(20) NOT NULL DEFAULT 'traveller'` (CHECK: `role IN ('traveller','admin')`)
  - `created_at`: `TIMESTAMPTZ NOT NULL DEFAULT now()`
  - `updated_at`: `TIMESTAMPTZ NOT NULL DEFAULT now()`

### 3.2 Table: `user_preferences`
Stores 1:1 user profile customization options.
* **Attributes & Types:**
  - `user_id`: `BIGINT PRIMARY KEY`
  - `hotel_preference`: `VARCHAR(40)`
  - `food_preference`: `VARCHAR(80)`
  - `transport_preference`: `VARCHAR(40)`
  - `travel_style`: `VARCHAR(40)`
  - `special_requirements`: `TEXT`
* **Foreign Keys:** `user_id` $\rightarrow$ `users(id)` `ON DELETE CASCADE`

### 3.3 Table: `activity_preferences`
Stores multi-valued activity tags selected by users.
* **Attributes & Types:**
  - `user_id`: `BIGINT NOT NULL`
  - `activity`: `VARCHAR(60) NOT NULL`
* **Primary Key:** `(user_id, activity)` (composite)
* **Foreign Keys:** `user_id` $\rightarrow$ `users(id)` `ON DELETE CASCADE`

### 3.4 Table: `destinations`
Stores geographic destination records.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `city`: `VARCHAR(100) NOT NULL`
  - `country`: `VARCHAR(100) NOT NULL`
  - `description`: `TEXT NOT NULL DEFAULT ''`
  - `average_daily_cost`: `NUMERIC(12,2)` (CHECK: `average_daily_cost >= 0`)
  - `active`: `BOOLEAN NOT NULL DEFAULT true`
* **Constraints:** `UNIQUE(city, country)`

### 3.5 Table: `hotels`
Stores accommodations linked to specific destinations.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `destination_id`: `BIGINT NOT NULL`
  - `name`: `VARCHAR(150) NOT NULL`
  - `price_per_night`: `NUMERIC(12,2) NOT NULL` (CHECK: `price_per_night >= 0`)
  - `rating`: `NUMERIC(2,1)` (CHECK: `rating BETWEEN 0 AND 5`)
* **Foreign Keys:** `destination_id` $\rightarrow$ `destinations(id)` `ON DELETE CASCADE`
* **Constraints:** `UNIQUE(destination_id, name)`

### 3.6 Table: `restaurants`
Stores dining venues categorized by cuisine.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `destination_id`: `BIGINT NOT NULL`
  - `name`: `VARCHAR(150) NOT NULL`
  - `cuisine`: `VARCHAR(80)`
  - `average_cost_per_person`: `NUMERIC(12,2)` (CHECK: `average_cost_per_person >= 0`)
  - `rating`: `NUMERIC(2,1)` (CHECK: `rating BETWEEN 0 AND 5`)
* **Foreign Keys:** `destination_id` $\rightarrow$ `destinations(id)` `ON DELETE CASCADE`
* **Constraints:** `UNIQUE(destination_id, name)`

### 3.7 Table: `attractions`
Stores sightseeing landmarks, monuments, and recreational activities.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `destination_id`: `BIGINT NOT NULL`
  - `name`: `VARCHAR(150) NOT NULL`
  - `category`: `VARCHAR(60)`
  - `entry_fee`: `NUMERIC(12,2) NOT NULL DEFAULT 0` (CHECK: `entry_fee >= 0`)
  - `rating`: `NUMERIC(2,1)` (CHECK: `rating BETWEEN 0 AND 5`)
* **Foreign Keys:** `destination_id` $\rightarrow$ `destinations(id)` `ON DELETE CASCADE`
* **Constraints:** `UNIQUE(destination_id, name)`

### 3.8 Table: `transport_options`
Stores inter-city and regional transit connection routes.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `origin`: `VARCHAR(100) NOT NULL`
  - `destination_id`: `BIGINT NOT NULL`
  - `mode`: `VARCHAR(40) NOT NULL`
  - `provider`: `VARCHAR(100)`
  - `estimated_cost`: `NUMERIC(12,2) NOT NULL` (CHECK: `estimated_cost >= 0`)
  - `duration_minutes`: `INTEGER` (CHECK: `duration_minutes > 0`)
* **Foreign Keys:** `destination_id` $\rightarrow$ `destinations(id)` `ON DELETE CASCADE`

### 3.9 Table: `trips`
Primary transactional entity storing multi-day travel itineraries.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `user_id`: `BIGINT NOT NULL`
  - `destination_id`: `BIGINT NOT NULL`
  - `starting_location`: `VARCHAR(120) NOT NULL`
  - `start_date`: `DATE NOT NULL`
  - `end_date`: `DATE NOT NULL`
  - `traveller_count`: `INTEGER NOT NULL` (CHECK: `traveller_count > 0`)
  - `total_budget`: `NUMERIC(12,2) NOT NULL` (CHECK: `total_budget > 0`)
  - `estimated_total`: `NUMERIC(12,2) NOT NULL DEFAULT 0` (CHECK: `estimated_total >= 0`)
  - `status`: `VARCHAR(20) NOT NULL DEFAULT 'draft'` (CHECK: `status IN ('draft','planned','completed','cancelled')`)
  - `created_at`: `TIMESTAMPTZ NOT NULL DEFAULT now()`
  - `updated_at`: `TIMESTAMPTZ NOT NULL DEFAULT now()`
* **Foreign Keys:** `user_id` $\rightarrow$ `users(id)` `ON DELETE CASCADE`; `destination_id` $\rightarrow$ `destinations(id)`
* **Constraints:** `CHECK (end_date >= start_date)`

### 3.10 Table: `trip_members`
Stores participants belonging to a multi-traveller trip.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `trip_id`: `BIGINT NOT NULL`
  - `display_name`: `VARCHAR(120) NOT NULL`
  - `age_group`: `VARCHAR(30)`
  - `special_requirements`: `TEXT`
* **Foreign Keys:** `trip_id` $\rightarrow$ `trips(id)` `ON DELETE CASCADE`

### 3.11 Table: `itineraries`
Container for generated and versioned multi-day itineraries.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `trip_id`: `BIGINT NOT NULL`
  - `version`: `INTEGER NOT NULL DEFAULT 1` (CHECK: `version > 0`)
  - `summary`: `TEXT NOT NULL DEFAULT ''`
  - `provider`: `VARCHAR(40) NOT NULL DEFAULT 'mock'`
  - `created_at`: `TIMESTAMPTZ NOT NULL DEFAULT now()`
* **Foreign Keys:** `trip_id` $\rightarrow$ `trips(id)` `ON DELETE CASCADE`
* **Constraints:** `UNIQUE(trip_id, version)`

### 3.12 Table: `itinerary_days`
Represents individual calendar days within an itinerary.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `itinerary_id`: `BIGINT NOT NULL`
  - `day_number`: `INTEGER NOT NULL` (CHECK: `day_number > 0`)
  - `itinerary_date`: `DATE NOT NULL`
* **Foreign Keys:** `itinerary_id` $\rightarrow$ `itineraries(id)` `ON DELETE CASCADE`
* **Constraints:** `UNIQUE(itinerary_id, day_number)`

### 3.13 Table: `itinerary_items`
Schedules specific temporal activity slots within a day.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `itinerary_day_id`: `BIGINT NOT NULL`
  - `item_order`: `INTEGER NOT NULL` (CHECK: `item_order > 0`)
  - `start_time`: `TIME`
  - `title`: `VARCHAR(180) NOT NULL`
  - `category`: `VARCHAR(50) NOT NULL`
  - `estimated_cost`: `NUMERIC(12,2) NOT NULL DEFAULT 0` (CHECK: `estimated_cost >= 0`)
  - `notes`: `TEXT`
* **Foreign Keys:** `itinerary_day_id` $\rightarrow$ `itinerary_days(id)` `ON DELETE CASCADE`
* **Constraints:** `UNIQUE(itinerary_day_id, item_order)`

### 3.14 Table: `budget_allocations`
Stores itemized category budget allocations.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `trip_id`: `BIGINT NOT NULL`
  - `category`: `VARCHAR(40) NOT NULL`
  - `amount`: `NUMERIC(12,2) NOT NULL` (CHECK: `amount >= 0`)
* **Foreign Keys:** `trip_id` $\rightarrow$ `trips(id)` `ON DELETE CASCADE`
* **Constraints:** `UNIQUE(trip_id, category)`

### 3.15 Table: `expenses`
Logs realized expenditures against a trip.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `trip_id`: `BIGINT NOT NULL`
  - `category`: `VARCHAR(40) NOT NULL`
  - `description`: `TEXT`
  - `amount`: `NUMERIC(12,2) NOT NULL` (CHECK: `amount >= 0`)
  - `incurred_on`: `DATE`
* **Foreign Keys:** `trip_id` $\rightarrow$ `trips(id)` `ON DELETE CASCADE`

### 3.16 Table: `saved_trips`
Junction table recording bookmarked trips per user.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `user_id`: `BIGINT NOT NULL`
  - `trip_id`: `BIGINT NOT NULL`
  - `saved_at`: `TIMESTAMPTZ NOT NULL DEFAULT now()`
* **Foreign Keys:** `user_id` $\rightarrow$ `users(id)` `ON DELETE CASCADE`; `trip_id` $\rightarrow$ `trips(id)` `ON DELETE CASCADE`
* **Constraints:** `UNIQUE(user_id, trip_id)`

### 3.17 Table: `reviews`
Stores destination reviews written by registered users.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `user_id`: `BIGINT NOT NULL`
  - `destination_id`: `BIGINT NOT NULL`
  - `rating`: `INTEGER NOT NULL` (CHECK: `rating BETWEEN 1 AND 5`)
  - `comment`: `TEXT`
* **Foreign Keys:** `user_id` $\rightarrow$ `users(id)` `ON DELETE CASCADE`; `destination_id` $\rightarrow$ `destinations(id)` `ON DELETE CASCADE`
* **Constraints:** `UNIQUE(user_id, destination_id)`

### 3.18 Table: `ai_conversations`
Tracks multi-turn chat sessions with the AI Copilot.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `user_id`: `BIGINT NOT NULL`
  - `trip_id`: `BIGINT` (Nullable)
  - `created_at`: `TIMESTAMPTZ NOT NULL DEFAULT now()`
* **Foreign Keys:** `user_id` $\rightarrow$ `users(id)` `ON DELETE CASCADE`; `trip_id` $\rightarrow$ `trips(id)` `ON DELETE SET NULL`

### 3.19 Table: `ai_messages`
Stores individual conversation messages.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `conversation_id`: `BIGINT NOT NULL`
  - `role`: `VARCHAR(20) NOT NULL` (CHECK: `role IN ('user','assistant','system')`)
  - `content`: `TEXT NOT NULL`
  - `created_at`: `TIMESTAMPTZ NOT NULL DEFAULT now()`
* **Foreign Keys:** `conversation_id` $\rightarrow$ `ai_conversations(id)` `ON DELETE CASCADE`

### 3.20 Table: `weather_snapshots`
Caches regional climate forecasts.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `destination_id`: `BIGINT NOT NULL`
  - `observed_at`: `TIMESTAMPTZ NOT NULL`
  - `summary`: `VARCHAR(160) NOT NULL`
  - `temperature_c`: `NUMERIC(5,2)`
  - `provider`: `VARCHAR(40) NOT NULL DEFAULT 'mock'`
* **Foreign Keys:** `destination_id` $\rightarrow$ `destinations(id)` `ON DELETE CASCADE`

### 3.21 Table: `packing_items`
Dynamic packing checklist items per trip.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `trip_id`: `BIGINT NOT NULL`
  - `item`: `VARCHAR(120) NOT NULL`
  - `category`: `VARCHAR(40)`
  - `is_packed`: `BOOLEAN NOT NULL DEFAULT false`
* **Foreign Keys:** `trip_id` $\rightarrow$ `trips(id)` `ON DELETE CASCADE`
* **Constraints:** `UNIQUE(trip_id, item)`

### 3.22 Table: `trip_audit`
Audit ledger populated automatically via PL/pgSQL trigger.
* **Attributes & Types:**
  - `id`: `BIGINT GENERATED ALWAYS AS IDENTITY` (PK)
  - `trip_id`: `BIGINT`
  - `action`: `VARCHAR(10) NOT NULL`
  - `changed_at`: `TIMESTAMPTZ NOT NULL DEFAULT now()`
  - `changed_by`: `TEXT NOT NULL DEFAULT current_user`
  - `old_row`: `JSONB`
  - `new_row`: `JSONB`

---

## 4. Relationship Summary

| Relationship | Type | Parent Key | Child Key | Referential Action |
| :--- | :---: | :--- | :--- | :--- |
| `users` $\rightarrow$ `user_preferences` | $1:1$ | `users.id` | `user_preferences.user_id` | `ON DELETE CASCADE` |
| `users` $\rightarrow$ `activity_preferences`| $1:N$| `users.id` | `activity_preferences.user_id` | `ON DELETE CASCADE` |
| `users` $\rightarrow$ `trips` | $1:N$ | `users.id` | `trips.user_id` | `ON DELETE CASCADE` |
| `destinations` $\rightarrow$ `hotels` | $1:N$ | `destinations.id` | `hotels.destination_id` | `ON DELETE CASCADE` |
| `destinations` $\rightarrow$ `restaurants` | $1:N$ | `destinations.id` | `restaurants.destination_id` | `ON DELETE CASCADE` |
| `destinations` $\rightarrow$ `attractions` | $1:N$ | `destinations.id` | `attractions.destination_id` | `ON DELETE CASCADE` |
| `destinations` $\rightarrow$ `transport_options` | $1:N$ | `destinations.id` | `transport_options.destination_id` | `ON DELETE CASCADE` |
| `destinations` $\rightarrow$ `trips` | $1:N$ | `destinations.id` | `trips.destination_id` | Restrict Delete |
| `trips` $\rightarrow$ `itineraries` | $1:N$ | `trips.id` | `itineraries.trip_id` | `ON DELETE CASCADE` |
| `itineraries` $\rightarrow$ `itinerary_days` | $1:N$ | `itineraries.id` | `itinerary_days.itinerary_id` | `ON DELETE CASCADE` |
| `itinerary_days` $\rightarrow$ `itinerary_items` | $1:N$ | `itinerary_days.id` | `itinerary_items.itinerary_day_id` | `ON DELETE CASCADE` |
| `trips` $\rightarrow$ `budget_allocations` | $1:N$ | `trips.id` | `budget_allocations.trip_id` | `ON DELETE CASCADE` |
| `trips` $\rightarrow$ `expenses` | $1:N$ | `trips.id` | `expenses.trip_id` | `ON DELETE CASCADE` |
| `trips` $\rightarrow$ `packing_items` | $1:N$ | `trips.id` | `packing_items.trip_id` | `ON DELETE CASCADE` |
| `ai_conversations` $\rightarrow$ `ai_messages` | $1:N$ | `ai_conversations.id`| `ai_messages.conversation_id` | `ON DELETE CASCADE` |
