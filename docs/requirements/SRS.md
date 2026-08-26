# RoamGenie — Software Requirements Specification (SRS)

## 1. Introduction
### 1.1 Purpose
This Software Requirements Specification (SRS) defines the functional and non-functional requirements for **RoamGenie v1.0.0**, an AI-driven Travel Planner and Relational Budget Optimizer developed for DBMS Academic Evaluation.

### 1.2 Scope of the System
RoamGenie provides automated multi-day itinerary generation, budget allocation and deficit auditing, interactive catalogue inspection across 500 destinations, interactive entity swapping, weather forecasting, packing checklist generation, and a bounded AI Copilot travel assistant.

---

## 2. Functional Requirements (FR)

| Req ID | Feature Area | Description | Implementation Status |
| :--- | :--- | :--- | :--- |
| **FR-01** | **User Authentication & RBAC** | Secure registration, login, JWT token issuance, password hashing via bcrypt, and role-based access (admin / traveller). | **IMPLEMENTED & VERIFIED** |
| **FR-02** | **Catalogue Explorer** | Paginated and searchable catalogue of 500 destinations with curated landmark photography, Google Maps exploration links, and modal entity inspection (hotels, dining, sights). | **IMPLEMENTED & VERIFIED** |
| **FR-03** | **Autocomplete Destination Selection** | Live Google-search-style autocomplete in trip planner filtering across 500 active destinations with keyword suggestions. | **IMPLEMENTED & VERIFIED** |
| **FR-04** | **Itinerary Generation Engine** | Multi-day schedule generation with temporal slotting (morning, afternoon, evening), budget allocation breakdown, and transit coordination. | **IMPLEMENTED & VERIFIED** |
| **FR-05** | **Budget Optimizer & Deficit Auditor** | Category-level allocation (40% Accommodation, 25% Food, 20% Sightseeing, 15% Transport), deficit detection (`alert-deficit` / `alert-ok`), and progress visualization. | **IMPLEMENTED & VERIFIED** |
| **FR-06** | **Manual Entity Swapping** | Ability to replace scheduled hotels, restaurants, and attractions with alternative database entities, dynamically recalculating total cost. | **IMPLEMENTED & VERIFIED** |
| **FR-07** | **Weather Grounding Service** | Fetch and cache 5-day temperature, rainfall, and condition snapshots per destination to guide indoor/outdoor scheduling. | **IMPLEMENTED & VERIFIED** |
| **FR-08** | **AI Travel Assistant / Copilot** | Contextual sliding chat drawer grounded in destination catalogue, trip parameters, and weather, with persisted conversation history in PostgreSQL. | **IMPLEMENTED & VERIFIED** |
| **FR-09** | **Packing Checklist Generator** | Weather- and destination-aware packing checklist with item toggling (packed state) and custom item addition. | **IMPLEMENTED & VERIFIED** |
| **FR-10** | **Trip History & Persistence** | Persist multi-day trips, budget snapshots, and day-wise item schedules to PostgreSQL with IDOR ownership validation. | **IMPLEMENTED & VERIFIED** |
| **FR-11** | **Saved Trip Bookmarks** | Bookmark and manage favorite trips with dedicated filtering tabs on user history dashboard. | **IMPLEMENTED & VERIFIED** |
| **FR-12** | **DBMS Analytical Showcase** | Interactive execution of 10 complex analytical queries (Q01–Q10) featuring window functions, aggregations, subqueries, and execution timing. | **IMPLEMENTED & VERIFIED** |

---

## 3. Non-Functional Requirements (NFR)

### 3.1 Performance & Response Time
- Catalogue filtering & search queries execute in `< 100ms`.
- Heuristic itinerary generation completes in `< 300ms`.
- AI LLM orchestration completes with fallback gracefully handling provider timeouts (`< 5.0s`).

### 3.2 Security & Data Protection
- Passwords hashed using industry-standard `bcrypt`.
- Authentication via signed `HMAC-SHA256` JWT tokens with expiry enforcement.
- Strict Insecure Direct Object Reference (IDOR) protection on all trip modification, chat, and packing endpoints.
- Parameterized SQL execution via SQLAlchemy ORM to prevent SQL Injection.

### 3.3 Reliability & Availability
- Database schema normalized to 3NF with foreign-key referential integrity (`ON DELETE CASCADE` where appropriate).
- Deterministic fallback algorithms ensure itinerary generation never fails even during external AI API outages.
