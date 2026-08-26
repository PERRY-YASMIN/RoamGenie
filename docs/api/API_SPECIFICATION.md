# RoamGenie REST API Specification

**Project:** RoamGenie — AI Travel Planner & Budget Optimizer  
**Base URL:** `/api/v1`  
**Authentication Scheme:** `Bearer <JWT_TOKEN>` (HTTP Authorization header)  
**Format:** JSON (`Content-Type: application/json`)  
**Status:** Authoritative Endpoint Inventory

---

## 1. Authentication Endpoints (`/auth`)

### `POST /auth/register`
* **Description:** Creates a new user account with Argon2id password hashing.
* **Auth Required:** No
* **Request Body:**
  ```json
  {
    "email": "traveller@example.com",
    "password": "securepassword123",
    "full_name": "Yasmin S"
  }
  ```
* **Response:** `201 Created`
  ```json
  {
    "id": 1,
    "email": "traveller@example.com",
    "full_name": "Yasmin S",
    "role": "traveller",
    "created_at": "2026-08-25T10:00:00Z"
  }
  ```

### `POST /auth/login`
* **Description:** Authenticates user credentials and returns a signed expiring JWT access token.
* **Auth Required:** No
* **Request Body:**
  ```json
  {
    "email": "traveller@example.com",
    "password": "securepassword123"
  }
  ```
* **Response:** `200 OK`
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in_seconds": 3600,
    "user_id": 1,
    "email": "traveller@example.com",
    "role": "traveller"
  }
  ```

---

## 2. User & Preferences Endpoints (`/users`)

### `GET /users/me`
* **Description:** Retrieves the authenticated user's profile and travel preferences.
* **Auth Required:** Yes (`Bearer <token>`)
* **Response:** `200 OK`

### `GET /users/me/preferences`
* **Description:** Retrieves the current user's normalized travel preferences and activity tags.
* **Auth Required:** Yes
* **Response:** `200 OK`

### `PUT /users/me/preferences`
* **Description:** Updates travel style preferences and activity interest tags.
* **Auth Required:** Yes
* **Request Body:**
  ```json
  {
    "hotel_preference": "moderate",
    "food_preference": "vegetarian",
    "transport_preference": "train",
    "travel_style": "cultural",
    "special_requirements": "Wheelchair accessible",
    "activities": ["heritage", "culinary", "photography"]
  }
  ```
* **Response:** `200 OK`

---

## 3. Travel Catalogues Endpoints

### `GET /destinations`
* **Description:** Browse destinations with optional search and pagination (`search`, `active_only`, `skip`, `limit`).
* **Auth Required:** No

### `GET /destinations/{id}`
* **Description:** Retrieve destination details by ID.
* **Auth Required:** No

### `GET /destinations/{id}/weather`
* **Description:** Retrieve live/simulated weather forecast for destination.
* **Auth Required:** No

### `GET /hotels?destination_id={id}&max_price={p}&min_rating={r}`
* **Description:** Browse accommodations in a destination with optional budget and rating filters.
* **Auth Required:** No

### `GET /restaurants?destination_id={id}&cuisine={c}&max_cost={m}`
* **Description:** Browse dining venues in a destination.
* **Auth Required:** No

### `GET /attractions?destination_id={id}&category={cat}&max_fee={f}`
* **Description:** Browse sightseeing points of interest.
* **Auth Required:** No

### `GET /transport-options?origin={orig}&destination_id={id}&mode={m}`
* **Description:** Browse transportation connections between origins and destinations.
* **Auth Required:** No

---

## 4. Trip Planning & Lifecycle Endpoints (`/trips`)

### `POST /trips`
* **Description:** Creates a new trip container with validated date ranges, traveller counts, and budgets.
* **Auth Required:** Yes
* **Request Body:**
  ```json
  {
    "destination_id": 1,
    "starting_location": "Delhi",
    "start_date": "2026-09-10",
    "end_date": "2026-09-13",
    "traveller_count": 2,
    "total_budget": "25000.00"
  }
  ```
* **Response:** `201 Created` (Returns full `TripDetailResponse`)

### `GET /trips`
* **Description:** Lists all trips owned by the authenticated user.
* **Auth Required:** Yes
* **Response:** `200 OK` (Array of `TripSummaryResponse`)

### `GET /trips/saved`
* **Description:** Lists bookmarked trips for the authenticated user.
* **Auth Required:** Yes
* **Response:** `200 OK` (Array of `SavedTripResponse`)

### `GET /trips/{id}`
* **Description:** Retrieves complete trip details including itineraries, days, items, budget summary, and packing list (enforcing user ownership).
* **Auth Required:** Yes
* **Response:** `200 OK`

### `PATCH /trips/{id}`
* **Description:** Updates trip parameters with re-validation.
* **Auth Required:** Yes
* **Response:** `200 OK`

### `DELETE /trips/{id}`
* **Description:** Deletes trip and cascades deletion to all associated items.
* **Auth Required:** Yes
* **Response:** `204 No Content`

### `POST /trips/{id}/generate`
* **Description:** Runs itinerary scheduler, budget optimizer, and executes transactional multi-table persistence.
* **Auth Required:** Yes
* **Query Params:** `force_ai=false`, `preferences=["heritage","culinary"]`
* **Response:** `200 OK` (`TripPlanGenerateResponse`)

### `GET /trips/{id}/weather`
* **Description:** Fetches weather forecast for the specific trip destination and dates.
* **Auth Required:** Yes

### `POST /trips/{id}/save`
* **Description:** Toggles bookmark/saved state for a trip.
* **Auth Required:** Yes
* **Response:** `200 OK` (`{"trip_id": 1, "is_saved": true}`)

---

## 5. Assistant & Packing Endpoints (`/assistant`)

### `POST /assistant/chat`
* **Description:** Contextual travel chat with AI Copilot grounded in trip facts.
* **Auth Required:** Optional
* **Request Body:** `{"message": "What should I pack?", "trip_id": 1}`
* **Response:** `200 OK` (`AssistantChatResponse`)

### `GET /assistant/trips/{id}/packing`
* **Description:** Retrieves checklist items for a trip.
* **Auth Required:** Yes

### `POST /assistant/trips/{id}/packing`
* **Description:** Adds a custom packing item to a trip.
* **Auth Required:** Yes

### `PATCH /assistant/packing/{item_id}`
* **Description:** Updates packed status (`is_packed: true/false`).
* **Auth Required:** Yes

### `DELETE /assistant/packing/{item_id}`
* **Description:** Removes a packing checklist item.
* **Auth Required:** Yes

---

## 6. DBMS Reports & Showcase Endpoints (`/reports`)

### `GET /reports/queries`
* **Description:** Returns metadata for 18 pre-built DBMS benchmark queries (Q01 to Q18).
* **Auth Required:** No

### `GET /reports/queries/{query_id}`
* **Description:** Executes a pre-built query (e.g., Q01) and returns tabular results with execution duration in ms.
* **Auth Required:** No

### `POST /reports/execute-sql`
* **Description:** Interactive SQL playground query runner.
* **Auth Required:** Yes (Admin role required; restricted to read-only statements)
* **Request Body:** `{"sql": "SELECT city, country FROM destinations ORDER BY city;"}`

### `GET /reports/audit-logs`
* **Description:** Retrieves PL/pgSQL trigger before/after JSONB mutation logs from `trip_audit`.
* **Auth Required:** No
