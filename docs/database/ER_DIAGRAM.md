# RoamGenie — Entity-Relationship (ER) Diagram

## 1. Complete System ER Diagram (Mermaid)

```mermaid
erDiagram
    USERS ||--o{ TRIPS : creates
    USERS ||--o{ USER_PREFERENCES : configures
    USERS ||--o{ SAVED_TRIPS : bookmarks
    USERS ||--o{ AI_CONVERSATIONS : conducts
    USERS ||--o{ REVIEWS : writes
    
    DESTINATIONS ||--o{ HOTELS : contains
    DESTINATIONS ||--o{ RESTAURANTS : contains
    DESTINATIONS ||--o{ ATTRACTIONS : contains
    DESTINATIONS ||--o{ TRANSPORT_OPTIONS : connects
    DESTINATIONS ||--o{ TRIPS : destination_of
    DESTINATIONS ||--o{ WEATHER_SNAPSHOTS : records
    DESTINATIONS ||--o{ REVIEWS : reviews
    
    TRIPS ||--o{ ITINERARIES : generates
    TRIPS ||--o{ BUDGET_ALLOCATIONS : splits
    TRIPS ||--o{ EXPENSES : logs
    TRIPS ||--o{ PACKING_ITEMS : requires
    TRIPS ||--o{ TRIP_MEMBERS : includes
    TRIPS ||--o{ TRIP_AUDIT : audits
    TRIPS ||--o{ SAVED_TRIPS : saved_as
    TRIPS ||--o{ AI_CONVERSATIONS : references
    
    ITINERARIES ||--o{ ITINERARY_DAYS : divides
    ITINERARY_DAYS ||--o{ ITINERARY_ITEMS : schedules
    
    AI_CONVERSATIONS ||--o{ AI_MESSAGES : contains

    USERS {
        int id PK
        string email UK
        string hashed_password
        string full_name
        string role
        datetime created_at
    }

    DESTINATIONS {
        int id PK
        string city
        string country
        string description
        decimal average_daily_cost
        boolean active
    }

    HOTELS {
        int id PK
        int destination_id FK
        string name
        decimal price_per_night
        decimal rating
    }

    RESTAURANTS {
        int id PK
        int destination_id FK
        string name
        string cuisine
        decimal average_cost_per_person
        decimal rating
    }

    ATTRACTIONS {
        int id PK
        int destination_id FK
        string name
        string category
        decimal entry_fee
        decimal rating
    }

    TRANSPORT_OPTIONS {
        int id PK
        int destination_id FK
        string mode
        string provider
        decimal estimated_cost
        string duration
    }

    TRIPS {
        int id PK
        int user_id FK
        int destination_id FK
        date start_date
        date end_date
        int traveller_count
        decimal total_budget
        decimal estimated_total
        string status
        datetime created_at
    }

    ITINERARIES {
        int id PK
        int trip_id FK
        string summary
        decimal total_cost
        string provider
    }

    ITINERARY_DAYS {
        int id PK
        int itinerary_id FK
        int day_number
        date date
        string summary
    }

    ITINERARY_ITEMS {
        int id PK
        int day_id FK
        string time_slot
        string activity_name
        string category
        decimal cost
    }

    BUDGET_ALLOCATIONS {
        int id PK
        int trip_id FK
        string category
        decimal allocated_amount
        decimal spent_amount
    }

    AI_CONVERSATIONS {
        int id PK
        int user_id FK
        int trip_id FK
        datetime created_at
    }

    AI_MESSAGES {
        int id PK
        int conversation_id FK
        string role
        string content
        datetime created_at
    }

    PACKING_ITEMS {
        int id PK
        int trip_id FK
        string item_name
        string category
        boolean is_packed
    }

    WEATHER_SNAPSHOTS {
        int id PK
        int destination_id FK
        date forecast_date
        decimal temperature_celsius
        string condition
        decimal precipitation_chance
    }
```

---

## 2. Cardinality & Relationship Breakdown

1. **User → Trips (1 : N):** One registered user can create and persist multiple multi-day travel trips.
2. **Destination → Catalogue Entities (1 : N):** Each destination hosts multiple hotels, restaurants, attractions, and transport options.
3. **Trip → Itineraries (1 : N):** A trip generates one active itinerary (and optional historical iterations).
4. **Itinerary → Days → Items (1 : N : M):** An itinerary breaks down into discrete day slots, which host temporal activity items (morning, afternoon, evening).
5. **Trip → Budget Allocations (1 : N):** A trip manages category-specific allocations (Stay, Food, Sightseeing, Transport).
6. **Conversation → Messages (1 : N):** An AI chat conversation logs individual user queries and assistant responses.
