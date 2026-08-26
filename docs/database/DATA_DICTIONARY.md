# RoamGenie — Data Dictionary

This data dictionary defines the attributes, data types, constraints, nullability, and business descriptions for all core tables in the RoamGenie database.

---

## 1. Table: `destinations`
Stores geographic destination records across India and global territories.

| Column | Data Type | Nullable | Default | Constraints / References | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | NO | `nextval()` | **PRIMARY KEY** | Unique destination identifier. |
| `city` | `VARCHAR(100)` | NO | None | None | Destination city name (e.g. "Jaipur", "Tokyo"). |
| `country` | `VARCHAR(100)` | NO | None | None | Destination country name (e.g. "India", "Japan"). |
| `description` | `TEXT` | YES | `''` | Max 1000 chars | Overview of landmark sights, heritage, and atmosphere. |
| `average_daily_cost` | `NUMERIC(10,2)` | YES | None | `CHECK (average_daily_cost >= 0)` | Estimated daily cost per person in INR. |
| `active` | `BOOLEAN` | NO | `TRUE` | None | Operational flag indicating if destination is active for planning. |

---

## 2. Table: `hotels`
Stores accommodation options linked to specific destinations.

| Column | Data Type | Nullable | Default | Constraints / References | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | NO | `nextval()` | **PRIMARY KEY** | Unique hotel identifier. |
| `destination_id` | `INTEGER` | NO | None | **FOREIGN KEY** -> `destinations.id` | Reference to host destination (`ON DELETE CASCADE`). |
| `name` | `VARCHAR(150)` | NO | None | None | Hotel or resort establishment name. |
| `price_per_night` | `NUMERIC(10,2)` | NO | None | `CHECK (price_per_night >= 0)` | Nightly room rate in INR. |
| `rating` | `NUMERIC(3,2)` | YES | None | `CHECK (rating >= 0 AND rating <= 5)` | Aggregate guest rating out of 5.0. |

---

## 3. Table: `restaurants`
Stores dining establishments and culinary venues.

| Column | Data Type | Nullable | Default | Constraints / References | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | NO | `nextval()` | **PRIMARY KEY** | Unique restaurant identifier. |
| `destination_id` | `INTEGER` | NO | None | **FOREIGN KEY** -> `destinations.id` | Host destination reference (`ON DELETE CASCADE`). |
| `name` | `VARCHAR(150)` | NO | None | None | Restaurant name. |
| `cuisine` | `VARCHAR(80)` | YES | None | None | Primary cuisine category (e.g. "Rajasthani", "Seafood"). |
| `average_cost_per_person` | `NUMERIC(10,2)`| YES | None | `CHECK (average_cost_per_person >= 0)`| Estimated meal cost per person in INR. |
| `rating` | `NUMERIC(3,2)` | YES | None | `CHECK (rating >= 0 AND rating <= 5)` | Customer rating score out of 5.0. |

---

## 4. Table: `attractions`
Stores sightseeing landmarks, monuments, and activities.

| Column | Data Type | Nullable | Default | Constraints / References | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | NO | `nextval()` | **PRIMARY KEY** | Unique attraction identifier. |
| `destination_id` | `INTEGER` | NO | None | **FOREIGN KEY** -> `destinations.id` | Host destination reference (`ON DELETE CASCADE`). |
| `name` | `VARCHAR(150)` | NO | None | None | Attraction / landmark name. |
| `category` | `VARCHAR(60)` | YES | `'sightseeing'`| None | Activity category (e.g. "Heritage", "Fort", "Beach"). |
| `entry_fee` | `NUMERIC(10,2)` | YES | `0.00` | `CHECK (entry_fee >= 0)` | Ticket / admission cost in INR. |
| `rating` | `NUMERIC(3,2)` | YES | None | `CHECK (rating >= 0 AND rating <= 5)` | Tourist rating out of 5.0. |

---

## 5. Table: `transport_options`
Stores regional transit modes (bus, train, flight, taxi, ferry) per destination.

| Column | Data Type | Nullable | Default | Constraints / References | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | NO | `nextval()` | **PRIMARY KEY** | Unique transport option identifier. |
| `destination_id` | `INTEGER` | NO | None | **FOREIGN KEY** -> `destinations.id` | Destination connection (`ON DELETE CASCADE`). |
| `mode` | `VARCHAR(50)` | NO | None | None | Transit modality (e.g. "Flight", "Train", "Bus", "Taxi"). |
| `provider` | `VARCHAR(100)` | YES | None | None | Operating agency / carrier. |
| `estimated_cost` | `NUMERIC(10,2)` | NO | None | `CHECK (estimated_cost >= 0)` | Estimated ticket / transit cost in INR. |
| `duration` | `VARCHAR(50)` | YES | None | None | Formatted travel duration string (e.g. "2h 30m"). |

---

## 6. Table: `trips`
Stores planned travel journeys and financial envelopes.

| Column | Data Type | Nullable | Default | Constraints / References | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | NO | `nextval()` | **PRIMARY KEY** | Unique trip identifier. |
| `user_id` | `INTEGER` | YES | None | **FOREIGN KEY** -> `users.id` | Creator account (`ON DELETE SET NULL`). |
| `destination_id` | `INTEGER` | NO | None | **FOREIGN KEY** -> `destinations.id` | Target destination reference. |
| `starting_location` | `VARCHAR(100)` | YES | None | None | Traveller origin city. |
| `start_date` | `DATE` | NO | None | None | Trip commencement date. |
| `end_date` | `DATE` | NO | None | `CHECK (end_date >= start_date)` | Trip conclusion date. |
| `traveller_count` | `INTEGER` | NO | `1` | `CHECK (traveller_count >= 1)` | Number of participants. |
| `total_budget` | `NUMERIC(10,2)` | NO | None | `CHECK (total_budget >= 0)` | Overall spending cap in INR. |
| `estimated_total` | `NUMERIC(10,2)` | YES | `0.00` | `CHECK (estimated_total >= 0)` | Computed itinerary expense total in INR. |
| `status` | `VARCHAR(20)` | NO | `'planned'` | None | Lifecycle state (`planned`, `active`, `completed`). |
| `created_at` | `TIMESTAMPTZ` | NO | `NOW()` | None | Record creation timestamp. |
| `updated_at` | `TIMESTAMPTZ` | NO | `NOW()` | None | Record update timestamp. |
