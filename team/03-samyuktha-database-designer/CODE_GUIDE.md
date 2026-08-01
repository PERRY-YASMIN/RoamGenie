# Code Guide

Core entities: users, user_preferences, destinations, hotels, restaurants, attractions, transport_options, trips, trip_members, itineraries, itinerary_days, itinerary_items, expenses, budget_allocations, saved_trips, reviews, AI conversations/messages, weather_snapshots, packing_items, activity_preferences. Record PK, FK, nullability, domain, default, unique/check rules and delete behavior.

- Prefer small named functions and consistent snake_case (Python/SQL) or camelCase (JavaScript).
- Validate at boundaries; log context without credentials or personal data.
- Keep configuration in environment variables documented in `.env.example`.
- Preserve working code. Stop and report overlapping or conflicting changes.
