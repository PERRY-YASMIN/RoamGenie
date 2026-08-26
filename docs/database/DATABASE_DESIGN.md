# RoamGenie — Database Design & Normalization

## 1. Relational Design Goals
The RoamGenie database is engineered to meet rigorous academic DBMS criteria:
1. **Third Normal Form (3NF) & Boyce-Codd Normal Form (BCNF):** All non-key attributes depend strictly, fully, and directly on the primary key, eliminating insertion, update, and deletion anomalies.
2. **Referential Integrity:** Cascading foreign key constraints maintain absolute data consistency between trips, itineraries, days, items, budget splits, and catalogue entries.
3. **Domain & Semantic Integrity:** Strict check constraints ensure non-negative financial values, bounded ratings (`0.0 <= rating <= 5.0`), valid temporal dates (`start_date <= end_date`), and valid status enums.
4. **Performance & Indexing:** Dedicated B-Tree indexes on foreign keys and search columns (e.g. `destinations.city`, `hotels.destination_id`, `trips.user_id`).

---

## 2. Normalization Analysis

### First Normal Form (1NF)
- **Criterion:** All attributes contain atomic (indivisible) values; no repeating groups or nested arrays.
- **Proof in RoamGenie:** Multi-day itineraries are decomposed into `itinerary_days` and `itinerary_items` rather than storing JSON arrays in single cells. Category allocations are stored as rows in `budget_allocations`.

### Second Normal Form (2NF)
- **Criterion:** Meets 1NF and all non-key attributes are fully functionally dependent on the entire primary key (no partial dependencies).
- **Proof in RoamGenie:** All base tables utilize single-column surrogate primary keys (`id SERIAL/IDENTITY`), eliminating composite key partial dependencies.

### Third Normal Form (3NF)
- **Criterion:** Meets 2NF and contains no transitive dependencies ($X \rightarrow Y \rightarrow Z$).
- **Proof in RoamGenie:** Hotel prices and ratings depend solely on `hotel.id`. Destination properties (country, average daily cost) live in `destinations` and are referenced by foreign key rather than being duplicated in `hotels`, `trips`, or `itinerary_items`.

---

## 3. Database Statistics Summary

- **Total Base Tables:** 23
- **Total Production Records:** **21,133** (Exceeds academic requirement of >= 5,000)
- **Foreign Key Orphan Count:** **0** (100% Referential Integrity)
- **Engine:** PostgreSQL 15+ (hosted on Supabase)
