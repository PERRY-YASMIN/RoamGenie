# RoamGenie — Dataset Verification Report

**Verification Date:** 2026-08-26  
**Target Environment:** Live Supabase PostgreSQL Database  
**Auditor:** Automated DB Audit Script ([`scripts/audit_database_state.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/scripts/audit_database_state.py))

---

## 1. Actual Live Table Counts

| Table Name | Actual Row Count | Academic Min Requirement | Verification Status |
| :--- | :---: | :---: | :---: |
| `destinations` | **500** | $\ge 50$ | **PASS** |
| `hotels` | **6,000** | $\ge 1,000$ | **PASS** |
| `restaurants` | **6,000** | $\ge 1,000$ | **PASS** |
| `transport_options` | **6,000** | $\ge 1,000$ | **PASS** |
| `attractions` | **2,517** | $\ge 1,000$ | **PASS** |
| `users` | **5** | $\ge 1$ | **PASS** |
| `trips` | **3** | $\ge 1$ | **PASS** |
| `itineraries` | **3** | $\ge 1$ | **PASS** |
| `itinerary_days` | **9** | $\ge 1$ | **PASS** |
| `itinerary_items` | **41** | $\ge 1$ | **PASS** |
| `budget_allocations` | **11** | $\ge 1$ | **PASS** |
| `packing_items` | **19** | $\ge 1$ | **PASS** |
| `weather_snapshots` | **8** | $\ge 1$ | **PASS** |
| `ai_conversations` | **1** | $\ge 1$ | **PASS** |
| `ai_messages` | **4** | $\ge 1$ | **PASS** |
| `activity_preferences` | **4** | $\ge 1$ | **PASS** |
| `user_preferences` | **2** | $\ge 1$ | **PASS** |
| `trip_members` | **2** | $\ge 1$ | **PASS** |
| `saved_trips` | **1** | $\ge 1$ | **PASS** |
| `reviews` | **1** | $\ge 1$ | **PASS** |
| `expenses` | **1** | $\ge 1$ | **PASS** |
| `trip_audit` | **0** | $\ge 0$ | **PASS** |
| `alembic_version` | **1** | $\ge 1$ | **PASS** |
| **TOTAL DATABASE ROWS** | **21,133** | **$\ge 5,000$** | **PASS (422% of target)** |

---

## 2. Foreign Key Integrity Audit

| Relationship Checked | Orphan Records Found | Integrity Status |
| :--- | :---: | :---: |
| `hotels.destination_id -> destinations.id` | **0** | **100% CLEAN** |
| `restaurants.destination_id -> destinations.id` | **0** | **100% CLEAN** |
| `attractions.destination_id -> destinations.id` | **0** | **100% CLEAN** |
| `transport_options.destination_id -> destinations.id` | **0** | **100% CLEAN** |
| `trips.user_id -> users.id` | **0** | **100% CLEAN** |
| `trips.destination_id -> destinations.id` | **0** | **100% CLEAN** |
| `itineraries.trip_id -> trips.id` | **0** | **100% CLEAN** |
| `budget_allocations.trip_id -> trips.id` | **0** | **100% CLEAN** |
| `saved_trips.trip_id -> trips.id` | **0** | **100% CLEAN** |
| `ai_conversations.user_id -> users.id` | **0** | **100% CLEAN** |

---

## 3. Conclusion
- **Academic Requirement:** $\ge 5,000$ realistic records.
- **Actual Record Count:** **21,133**.
- **Audit Verdict:** **PASS (RELEASE READY)**.
