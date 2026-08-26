# RoamGenie — Relational Schema

This document formalizes the relational schema definitions, functional dependencies, primary keys (PK), and foreign keys (FK) for the RoamGenie database.

## Schema Definitions

### 1. User Management
* **`users`** (`id` [PK], `email` [UK], `hashed_password`, `full_name`, `role`, `created_at`, `updated_at`)
* **`user_preferences`** (`id` [PK], `user_id` [FK -> users.id], `preferred_pace`, `dietary_preference`, `default_budget_tier`, `created_at`, `updated_at`)
* **`activity_preferences`** (`id` [PK], `user_id` [FK -> users.id], `preference_type`, `weight`, `created_at`)

### 2. Catalogue Master Data
* **`destinations`** (`id` [PK], `city`, `country`, `description`, `average_daily_cost`, `active`)
* **`hotels`** (`id` [PK], `destination_id` [FK -> destinations.id], `name`, `price_per_night`, `rating`)
* **`restaurants`** (`id` [PK], `destination_id` [FK -> destinations.id], `name`, `cuisine`, `average_cost_per_person`, `rating`)
* **`attractions`** (`id` [PK], `destination_id` [FK -> destinations.id], `name`, `category`, `entry_fee`, `rating`)
* **`transport_options`** (`id` [PK], `destination_id` [FK -> destinations.id], `mode`, `provider`, `estimated_cost`, `duration`)

### 3. Trip & Itinerary Transactional Data
* **`trips`** (`id` [PK], `user_id` [FK -> users.id], `destination_id` [FK -> destinations.id], `starting_location`, `start_date`, `end_date`, `traveller_count`, `total_budget`, `estimated_total`, `status`, `created_at`, `updated_at`)
* **`trip_members`** (`id` [PK], `trip_id` [FK -> trips.id], `user_id` [FK -> users.id], `role`, `joined_at`)
* **`trip_audit`** (`id` [PK], `trip_id` [FK -> trips.id], `action`, `changed_by`, `old_values`, `new_values`, `created_at`)
* **`itineraries`** (`id` [PK], `trip_id` [FK -> trips.id], `summary`, `total_cost`, `provider`, `created_at`)
* **`itinerary_days`** (`id` [PK], `itinerary_id` [FK -> itineraries.id], `day_number`, `date`, `summary`)
* **`itinerary_items`** (`id` [PK], `day_id` [FK -> itinerary_days.id], `time_slot`, `activity_name`, `category`, `cost`, `notes`, `booking_reference`)
* **`budget_allocations`** (`id` [PK], `trip_id` [FK -> trips.id], `category`, `allocated_amount`, `spent_amount`)
* **`expenses`** (`id` [PK], `trip_id` [FK -> trips.id], `category`, `amount`, `description`, `expense_date`, `created_at`)
* **`saved_trips`** (`id` [PK], `user_id` [FK -> users.id], `trip_id` [FK -> trips.id], `saved_at`)

### 4. AI Copilot & Weather Snapshots
* **`ai_conversations`** (`id` [PK], `user_id` [FK -> users.id], `trip_id` [FK -> trips.id], `created_at`, `updated_at`)
* **`ai_messages`** (`id` [PK], `conversation_id` [FK -> ai_conversations.id], `role`, `content`, `created_at`)
* **`packing_items`** (`id` [PK], `trip_id` [FK -> trips.id], `item_name`, `category`, `is_packed`, `created_at`)
* **`weather_snapshots`** (`id` [PK], `destination_id` [FK -> destinations.id], `forecast_date`, `temperature_celsius`, `condition`, `precipitation_chance`, `created_at`)
* **`reviews`** (`id` [PK], `user_id` [FK -> users.id], `destination_id` [FK -> destinations.id], `rating`, `comment`, `created_at`)
