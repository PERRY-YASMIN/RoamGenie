# Data Dictionary (Draft)

| Table | Purpose | Key fields and rules |
|---|---|---|
| users | account identity | id PK; email unique; password_hash; role; timestamps |
| user_preferences | one profile preference set | user_id PK/FK; arrays/text preferences |
| destinations | place catalogue | id PK; city/country; unique city+country |
| hotels/restaurants/attractions | destination offerings | id PK; destination_id FK; name; cost/rating checks |
| transport_options | route options | id PK; origin/destination; mode; nonnegative cost |
| trips | user request | id PK; user_id/destination_id FK; valid dates; travellers/budget positive; status |
| itineraries/days/items | ordered generated plan | trip FK; unique version/day/order; optional catalogue references |
| expenses/budget_allocations | actual/estimated category money | trip FK; category; amount nonnegative; unique allocation category |
| saved_trips | user bookmark/history | user_id+trip_id unique |
| reviews | user ratings | user/target; rating 1–5 |
| ai_conversations/messages | assistant history | user/trip; role/content; timestamps |
| weather_snapshots | time-bound provider result | destination, observed time, JSON payload |
| packing_items | plan checklist | trip, item, category, packed flag |
| activity_preferences | normalized activity labels | user, activity unique pair |

Samyuktha expands every column's type, nullability, default, domain, constraints and delete rule after schema-v1 review.
