# Entity-Relationship (ER) Diagram
## AI Travel Planner & Budget Optimizer — RoamGenie
### Academic Milestone 3: Entity-Relationship Diagram

---

## 1. Complete System ER Diagram (Mermaid)

```mermaid
erDiagram
    USERS ||--o{ TRIPS : "creates (1:N)"
    USERS ||--o{ USER_PREFERENCES : "configures (1:1)"
    USERS ||--o{ ACTIVITY_PREFERENCES : "selects (1:N)"
    USERS ||--o{ SAVED_TRIPS : "bookmarks (1:N)"
    USERS ||--o{ AI_CONVERSATIONS : "initiates (1:N)"
    USERS ||--o{ REVIEWS : "writes (1:N)"
    
    DESTINATIONS ||--o{ HOTELS : "contains (1:N)"
    DESTINATIONS ||--o{ RESTAURANTS : "contains (1:N)"
    DESTINATIONS ||--o{ ATTRACTIONS : "contains (1:N)"
    DESTINATIONS ||--o{ TRANSPORT_OPTIONS : "connects (1:N)"
    DESTINATIONS ||--o{ TRIPS : "destination_of (1:N)"
    DESTINATIONS ||--o{ WEATHER_SNAPSHOTS : "records (1:N)"
    DESTINATIONS ||--o{ REVIEWS : "reviewed_in (1:N)"
    
    TRIPS ||--o{ ITINERARIES : "generates (1:N)"
    TRIPS ||--o{ BUDGET_ALLOCATIONS : "allocates (1:N)"
    TRIPS ||--o{ EXPENSES : "incurs (1:N)"
    TRIPS ||--o{ PACKING_ITEMS : "requires (1:N)"
    TRIPS ||--o{ TRIP_MEMBERS : "includes (1:N)"
    TRIPS ||--o{ SAVED_TRIPS : "saved_in (1:N)"
    TRIPS ||--o{ AI_CONVERSATIONS : "context_for (1:N)"
    
    ITINERARIES ||--o{ ITINERARY_DAYS : "divides (1:N)"
    ITINERARY_DAYS ||--o{ ITINERARY_ITEMS : "schedules (1:N)"
    
    AI_CONVERSATIONS ||--o{ AI_MESSAGES : "logs (1:N)"

    USERS {
        bigint id PK
        varchar email UK
        text password_hash
        varchar full_name
        varchar role
        timestamptz created_at
        timestamptz updated_at
    }

    USER_PREFERENCES {
        bigint user_id PK_FK
        varchar hotel_preference
        varchar food_preference
        varchar transport_preference
        varchar travel_style
        text special_requirements
    }

    ACTIVITY_PREFERENCES {
        bigint user_id PK_FK
        varchar activity PK
    }

    DESTINATIONS {
        bigint id PK
        varchar city
        varchar country
        text description
        numeric average_daily_cost
        boolean active
    }

    HOTELS {
        bigint id PK
        bigint destination_id FK
        varchar name
        numeric price_per_night
        numeric rating
    }

    RESTAURANTS {
        bigint id PK
        bigint destination_id FK
        varchar name
        varchar cuisine
        numeric average_cost_per_person
        numeric rating
    }

    ATTRACTIONS {
        bigint id PK
        bigint destination_id FK
        varchar name
        varchar category
        numeric entry_fee
        numeric rating
    }

    TRANSPORT_OPTIONS {
        bigint id PK
        varchar origin
        bigint destination_id FK
        varchar mode
        varchar provider
        numeric estimated_cost
        integer duration_minutes
    }

    TRIPS {
        bigint id PK
        bigint user_id FK
        bigint destination_id FK
        varchar starting_location
        date start_date
        date end_date
        integer traveller_count
        numeric total_budget
        numeric estimated_total
        varchar status
        timestamptz created_at
        timestamptz updated_at
    }

    TRIP_MEMBERS {
        bigint id PK
        bigint trip_id FK
        varchar display_name
        varchar age_group
        text special_requirements
    }

    ITINERARIES {
        bigint id PK
        bigint trip_id FK
        integer version
        text summary
        varchar provider
        timestamptz created_at
    }

    ITINERARY_DAYS {
        bigint id PK
        bigint itinerary_id FK
        integer day_number
        date itinerary_date
    }

    ITINERARY_ITEMS {
        bigint id PK
        bigint itinerary_day_id FK
        integer item_order
        time start_time
        varchar title
        varchar category
        numeric estimated_cost
        text notes
    }

    BUDGET_ALLOCATIONS {
        bigint id PK
        bigint trip_id FK
        varchar category
        numeric amount
    }

    EXPENSES {
        bigint id PK
        bigint trip_id FK
        varchar category
        text description
        numeric amount
        date incurred_on
    }

    SAVED_TRIPS {
        bigint id PK
        bigint user_id FK
        bigint trip_id FK
        timestamptz saved_at
    }

    REVIEWS {
        bigint id PK
        bigint user_id FK
        bigint destination_id FK
        integer rating
        text comment
    }

    AI_CONVERSATIONS {
        bigint id PK
        bigint user_id FK
        bigint trip_id FK
        timestamptz created_at
    }

    AI_MESSAGES {
        bigint id PK
        bigint conversation_id FK
        varchar role
        text content
        timestamptz created_at
    }

    WEATHER_SNAPSHOTS {
        bigint id PK
        bigint destination_id FK
        timestamptz observed_at
        varchar summary
        numeric temperature_c
        varchar provider
    }

    PACKING_ITEMS {
        bigint id PK
        bigint trip_id FK
        varchar item
        varchar category
        boolean is_packed
    }

    TRIP_AUDIT {
        bigint id PK
        bigint trip_id
        varchar action
        timestamptz changed_at
        text changed_by
        jsonb old_row
        jsonb new_row
    }
```

---

## 2. Entity Descriptions

### 2.1 User Management Entities
* **`users`:** Represents registered accounts in the system. Stores authentication credentials, display names, authorization roles (`traveller` / `admin`), and audit timestamps.
  - *Primary Key:* `id`
  - *Key Attributes:* `email` (UNIQUE), `password_hash`, `full_name`, `role`.
  - *Relationships:* Parent to `trips`, `user_preferences`, `activity_preferences`, `saved_trips`, `reviews`, and `ai_conversations`.
* **`user_preferences`:** Stores profile configuration options (hotel tier, food preferences, transit choices, travel pace).
  - *Primary Key:* `user_id` (Foreign Key referencing `users.id`).
  - *Relationships:* $1:1$ child of `users`.
* **`activity_preferences`:** Multi-valued activity interests associated with user accounts.
  - *Primary Key:* `(user_id, activity)` (composite key).
  - *Relationships:* Child of `users`.

### 2.2 Master Catalogue Entities
* **`destinations`:** Core geographic master entity representing cities available for travel planning.
  - *Primary Key:* `id`
  - *Key Attributes:* `city`, `country` (UNIQUE composite), `description`, `average_daily_cost`, `active`.
  - *Relationships:* Parent to `hotels`, `restaurants`, `attractions`, `transport_options`, `trips`, `weather_snapshots`, and `reviews`.
* **`hotels`:** Accommodations linked to destinations with pricing and quality ratings.
  - *Primary Key:* `id`
  - *Key Attributes:* `destination_id` (FK), `name`, `price_per_night`, `rating`.
  - *Relationships:* Child of `destinations`.
* **`restaurants`:** Dining venues categorized by cuisine, price per person, and guest ratings.
  - *Primary Key:* `id`
  - *Key Attributes:* `destination_id` (FK), `name`, `cuisine`, `average_cost_per_person`, `rating`.
  - *Relationships:* Child of `destinations`.
* **`attractions`:** Sightseeing landmarks, monuments, and cultural activities.
  - *Primary Key:* `id`
  - *Key Attributes:* `destination_id` (FK), `name`, `category`, `entry_fee`, `rating`.
  - *Relationships:* Child of `destinations`.
* **`transport_options`:** Inter-city transit routes connecting origins to destinations.
  - *Primary Key:* `id`
  - *Key Attributes:* `origin`, `destination_id` (FK), `mode`, `provider`, `estimated_cost`, `duration_minutes`.
  - *Relationships:* Child of `destinations`.

### 2.3 Trip & Itinerary Transactional Entities
* **`trips`:** Primary transactional entity recording travel plans, date envelopes, budget caps, and status.
  - *Primary Key:* `id`
  - *Key Attributes:* `user_id` (FK), `destination_id` (FK), `starting_location`, `start_date`, `end_date`, `traveller_count`, `total_budget`, `estimated_total`, `status`.
  - *Relationships:* Child of `users` and `destinations`; Parent to `itineraries`, `budget_allocations`, `expenses`, `packing_items`, `trip_members`, and `saved_trips`.
* **`trip_members`:** Participants associated with a multi-person travel group.
  - *Primary Key:* `id`
  - *Key Attributes:* `trip_id` (FK), `display_name`, `age_group`, `special_requirements`.
  - *Relationships:* Child of `trips`.
* **`itineraries`:** Versioned multi-day plan containers for a trip.
  - *Primary Key:* `id`
  - *Key Attributes:* `trip_id` (FK), `version`, `summary`, `provider`.
  - *Relationships:* Child of `trips`; Parent to `itinerary_days`.
* **`itinerary_days`:** Discrete calendar days within a generated itinerary.
  - *Primary Key:* `id`
  - *Key Attributes:* `itinerary_id` (FK), `day_number`, `itinerary_date`.
  - *Relationships:* Child of `itineraries`; Parent to `itinerary_items`.
* **`itinerary_items`:** Individual scheduled activities, hotels, or meals within a day slot.
  - *Primary Key:* `id`
  - *Key Attributes:* `itinerary_day_id` (FK), `item_order`, `start_time`, `title`, `category`, `estimated_cost`, `notes`.
  - *Relationships:* Child of `itinerary_days`.
* **`budget_allocations`:** Itemized financial allocations per category (Stay, Food, Sightseeing, Transport).
  - *Primary Key:* `id`
  - *Key Attributes:* `trip_id` (FK), `category`, `amount`.
  - *Relationships:* Child of `trips`.
* **`expenses`:** Actual realized expenditures logged during travel.
  - *Primary Key:* `id`
  - *Key Attributes:* `trip_id` (FK), `category`, `description`, `amount`, `incurred_on`.
  - *Relationships:* Child of `trips`.
* **`saved_trips`:** Bookmarked trips associated with user accounts.
  - *Primary Key:* `id`
  - *Key Attributes:* `user_id` (FK), `trip_id` (FK), `saved_at`.
  - *Relationships:* Junction entity linking `users` and `trips`.

### 2.4 Supporting AI & Contextual Entities
* **`ai_conversations`:** Multi-turn AI chat sessions linked to users and trips.
  - *Primary Key:* `id`
  - *Key Attributes:* `user_id` (FK), `trip_id` (FK nullable), `created_at`.
  - *Relationships:* Child of `users` and `trips`; Parent to `ai_messages`.
* **`ai_messages`:** Individual chat turns containing sender role and content.
  - *Primary Key:* `id`
  - *Key Attributes:* `conversation_id` (FK), `role`, `content`, `created_at`.
  - *Relationships:* Child of `ai_conversations`.
* **`weather_snapshots`:** Forecast records capturing destination climate observations.
  - *Primary Key:* `id`
  - *Key Attributes:* `destination_id` (FK), `observed_at`, `summary`, `temperature_c`, `provider`.
  - *Relationships:* Child of `destinations`.
* **`packing_items`:** Itemized packing checklist items per trip.
  - *Primary Key:* `id`
  - *Key Attributes:* `trip_id` (FK), `item`, `category`, `is_packed`.
  - *Relationships:* Child of `trips`.
* **`reviews`:** User feedback and numerical ratings for destinations.
  - *Primary Key:* `id`
  - *Key Attributes:* `user_id` (FK), `destination_id` (FK), `rating`, `comment`.
  - *Relationships:* Junction entity linking `users` and `destinations`.
* **`trip_audit`:** Trigger-managed audit log capturing historical modifications to trip records.
  - *Primary Key:* `id`
  - *Key Attributes:* `trip_id`, `action`, `changed_at`, `changed_by`, `old_row`, `new_row`.

---

## 3. Relationship Descriptions & Cardinality Matrix

| Parent Entity | Child Entity | Cardinality | Foreign Key & Referential Action | Business Logic / Meaning |
| :--- | :--- | :---: | :--- | :--- |
| `users` | `trips` | $1 : N$ | `trips.user_id -> users.id` (`ON DELETE CASCADE`) | One user can create multiple trips. |
| `users` | `user_preferences` | $1 : 1$ | `user_preferences.user_id -> users.id` (`CASCADE`)| One user maintains exactly one preference profile. |
| `users` | `activity_preferences` | $1 : N$ | `activity_preferences.user_id -> users.id` (`CASCADE`)| One user can select multiple activity interest tags. |
| `users` | `saved_trips` | $1 : N$ | `saved_trips.user_id -> users.id` (`CASCADE`) | One user can bookmark multiple saved trips. |
| `destinations` | `hotels` | $1 : N$ | `hotels.destination_id -> destinations.id` (`CASCADE`) | One destination hosts multiple accommodation options. |
| `destinations` | `restaurants` | $1 : N$ | `restaurants.destination_id -> destinations.id` (`CASCADE`) | One destination hosts multiple dining establishments. |
| `destinations` | `attractions` | $1 : N$ | `attractions.destination_id -> destinations.id` (`CASCADE`) | One destination contains multiple sightseeing landmarks. |
| `destinations` | `transport_options`| $1 : N$ | `transport_options.destination_id -> destinations.id` (`CASCADE`) | One destination has multiple transit connection routes. |
| `destinations` | `trips` | $1 : N$ | `trips.destination_id -> destinations.id` | Multiple trips can choose the same destination. |
| `trips` | `itineraries` | $1 : N$ | `itineraries.trip_id -> trips.id` (`CASCADE`) | One trip can generate multiple plan iterations/versions. |
| `itineraries` | `itinerary_days` | $1 : N$ | `itinerary_days.itinerary_id -> itineraries.id` (`CASCADE`)| One itinerary divides into multiple calendar days. |
| `itinerary_days`| `itinerary_items` | $1 : N$ | `itinerary_items.itinerary_day_id -> itinerary_days.id` (`CASCADE`)| One day slot schedules multiple ordered activities. |
| `trips` | `budget_allocations`| $1 : N$ | `budget_allocations.trip_id -> trips.id` (`CASCADE`)| One trip splits budget across multiple categories. |
| `trips` | `expenses` | $1 : N$ | `expenses.trip_id -> trips.id` (`CASCADE`) | One trip incurs multiple realized expense records. |
| `trips` | `packing_items` | $1 : N$ | `packing_items.trip_id -> trips.id` (`CASCADE`) | One trip maintains a dedicated packing checklist. |
| `ai_conversations`| `ai_messages` | $1 : N$ | `ai_messages.conversation_id -> ai_conversations.id` (`CASCADE`)| One conversation logs multiple sequential messages. |
