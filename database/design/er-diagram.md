# ER Diagram v1 Draft

```mermaid
erDiagram
  USERS ||--o| USER_PREFERENCES : has
  USERS ||--o{ TRIPS : plans
  DESTINATIONS ||--o{ TRIPS : chosen_for
  DESTINATIONS ||--o{ HOTELS : contains
  DESTINATIONS ||--o{ RESTAURANTS : contains
  DESTINATIONS ||--o{ ATTRACTIONS : contains
  TRIPS ||--o{ TRIP_MEMBERS : includes
  TRIPS ||--o{ ITINERARIES : versions
  ITINERARIES ||--|{ ITINERARY_DAYS : contains
  ITINERARY_DAYS ||--o{ ITINERARY_ITEMS : schedules
  TRIPS ||--o{ EXPENSES : records
  TRIPS ||--o{ BUDGET_ALLOCATIONS : allocates
  USERS ||--o{ SAVED_TRIPS : saves
  TRIPS ||--o{ SAVED_TRIPS : bookmarked_as
  USERS ||--o{ AI_CONVERSATIONS : opens
  AI_CONVERSATIONS ||--o{ AI_MESSAGES : contains
  TRIPS ||--o{ PACKING_ITEMS : needs
  DESTINATIONS ||--o{ WEATHER_SNAPSHOTS : observed_at
  USERS ||--o{ ACTIVITY_PREFERENCES : prefers
```

Review open decisions at M1: polymorphic review target, itinerary item catalogue reference strategy, transport route normalization and whether user preferences remain one-to-one or become lookup tables.

