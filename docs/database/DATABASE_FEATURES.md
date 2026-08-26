# RoamGenie — Database Advanced Features & SQL Showcase

This document details the advanced DBMS concepts implemented in the RoamGenie PostgreSQL database for academic evaluation.

---

## 1. SQL Language Subsets

### 1.1 Data Definition Language (DDL)
- **Source:** [`database/schema/001_schema.sql`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/database/schema/001_schema.sql)
- **Features Implemented:**
  - Table creation with strict data types (`INTEGER`, `VARCHAR`, `NUMERIC(10,2)`, `BOOLEAN`, `TIMESTAMPTZ`, `DATE`).
  - Primary keys (`id SERIAL/IDENTITY PRIMARY KEY`).
  - Foreign key constraints with referential action rules (`ON DELETE CASCADE`, `ON DELETE SET NULL`).
  - Column constraints (`NOT NULL`, `CHECK (price_per_night >= 0)`, `CHECK (rating >= 0 AND rating <= 5)`).
  - Explicit indexes on frequently joined columns (`CREATE INDEX idx_hotels_dest ON hotels(destination_id)`).

### 1.2 Data Manipulation Language (DML)
- **Source:** [`database/seeds/`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/database/seeds/) & SQLAlchemy CRUD operations in [`backend/app/routers/`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/routers/)
- **Features Implemented:**
  - Bulk insertion of master records (>20,000 rows across destinations, hotels, dining, attractions, transit).
  - Atomic updates (`UPDATE trips SET estimated_total = ... WHERE id = ...`).
  - Cascading deletions (`DELETE FROM trips WHERE id = ...`).

### 1.3 Data Control Language (DCL) & Security
- **Features Implemented:**
  - Role-based permissions and Row Level Security (`ENABLE ROW LEVEL SECURITY`).
  - Application user role separation (`admin` vs. `traveller`).

### 1.4 Transaction Control Language (TCL)
- **Source:** [`database/transactions/001_save_itinerary.sql`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/database/transactions/001_save_itinerary.sql)
- **Features Implemented:**
  - ACID-compliant transactions wrapping multi-table itinerary persistence:
  ```sql
  BEGIN;
  INSERT INTO trips (...) VALUES (...);
  INSERT INTO itineraries (...) VALUES (...);
  INSERT INTO itinerary_days (...) VALUES (...);
  INSERT INTO itinerary_items (...) VALUES (...);
  INSERT INTO budget_allocations (...) VALUES (...);
  COMMIT;
  ```

---

## 2. Advanced SQL Queries & Analytical Showcase

The platform exposes **10 complex DBMS analytical queries** live on the **DBMS Showcase** page (`/showcase`):

| Query ID | Title | SQL Concepts Demonstrated | Description / Purpose |
| :--- | :--- | :--- | :--- |
| **Q01** | **Destination Cost Rank** | `RANK() OVER (ORDER BY cost)`, `WHERE`, `ORDER BY` | Ranks all destinations by average daily budget. |
| **Q02** | **Budget vs. Actual Variance** | `JOIN`, `SUM()`, `GROUP BY`, `CASE`, `HAVING` | Compares allocated budget against estimated item costs to detect deficits. |
| **Q03** | **Top Rated Stays by Country** | `ROW_NUMBER() OVER (PARTITION BY country ORDER BY rating DESC)` | Computes top 3 highest-rated hotels in each country. |
| **Q04** | **Cuisine Diversity Analysis** | `COUNT(DISTINCT cuisine)`, `GROUP BY`, `JOIN` | Aggregates culinary diversity metrics across destinations. |
| **Q05** | **Multi-Modal Transit Coverage** | `JOIN`, `COUNT(DISTINCT mode)`, `GROUP BY` | Identifies destinations with full multi-modal transport connectivity. |
| **Q06** | **Activity Pace Distribution** | `JOIN`, Subqueries, Category Aggregations | Analyzes morning vs. afternoon vs. evening scheduled intensity. |
| **Q07** | **Affordable Heritage Itineraries** | `JOIN`, Filtered Aggregation, `AVG()` | Discovers heritage attractions with entry fees below regional average. |
| **Q08** | **High-Value Dining Index** | `WHERE rating >= 4.5`, Cost Percentiles | Indexes premium dining venues offering above-average cost-efficiency. |
| **Q09** | **Trip Member Collaborators** | Self-Joins, `trip_members` correlation | Audits multi-traveller permissions and shared itinerary collaborations. |
| **Q10** | **Seasonal Climate Correlation** | `weather_snapshots` cross-tabulation | Correlates precipitation and temperature against trip travel dates. |

---

## 3. Stored Functions & Triggers

### 3.1 Function: `refresh_trip_total(target_trip_id INT)`
- **Source:** [`database/procedures/001_refresh_trip_total.sql`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/database/procedures/001_refresh_trip_total.sql)
- **Logic:** Sums all scheduled `itinerary_items.cost` for a given trip and updates `trips.estimated_total`.

### 3.2 Trigger: `audit_trip_changes`
- **Source:** [`database/triggers/001_audit_trip.sql`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/database/triggers/001_audit_trip.sql)
- **Logic:** `AFTER UPDATE ON trips` automatically captures `OLD` and `NEW` budget/status values and logs an entry to `trip_audit`.
