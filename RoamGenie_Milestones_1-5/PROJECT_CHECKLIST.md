# RoamGenie — Project Progress & Milestone Checklist

This checklist tracks completed deliverables, current operational baselines, and upcoming tasks. You can edit the markdown checkboxes (`- [x]` for done, `- [ ]` for pending) as you and your team progress.

---

## 🎓 1. Academic Milestones (DBMS Semester 5)

### Milestone 1: Problem Statement
- [x] **Project Title & Domain Context:** Formulated problem background in leisure travel planning.
- [x] **Limitations of Existing Tools:** Documented fragmentation, budget overruns, and ungrounded LLM hallucinations.
- [x] **Proposed Solution & Objectives:** Defined 6 core relational and algorithmic objectives.
- [x] **Target Users & Personas:** Documented budget, family, and evaluator personas.

### Milestone 2: Software Requirements Specification (SRS)
- [x] **3-Tier Product Architecture:** Defined presentation (React), backend (FastAPI), and database (PostgreSQL) tiers.
- [x] **Functional Requirements (FR-01 to FR-18):** Specified all 18 core requirements.
- [x] **Non-Functional Requirements (NFR-01 to NFR-10):** Specified performance, security, and data integrity metrics.
- [x] **System Constraints & Use Cases:** Formalized date ranges, currency base (INR), and user flows.

### Milestone 3: Entity-Relationship (ER) Diagram
- [x] **Comprehensive Relational ER Diagram:** Built 22 domain tables + 1 audit ledger.
- [x] **Entity Descriptions:** Documented attributes, PKs, and FKs for every entity.
- [x] **Cardinality & Relationships:** Formalized $1:1$, $1:N$, and $N:M$ cardinalities and cascade rules.
- [x] **Visual ER Diagram Asset:** Generated high-resolution visual diagram (`ER_Diagram.png`).

### Milestone 4: Normalized Database Design
- [x] **Functional Dependency Analysis:** Formalized $X \rightarrow Y$ dependencies for all core tables.
- [x] **First Normal Form (1NF):** Decomposed repeating groups (`activity_preferences`, `itinerary_items`).
- [x] **Second Normal Form (2NF):** Eliminated partial key dependencies.
- [x] **Third Normal Form (3NF):** Eliminated transitive functional dependencies (e.g. hotel-destination).
- [x] **Boyce-Codd Normal Form (BCNF):** Proved superkey determinants across all relations.

### Milestone 5: Relational Schema
- [x] **Compact Mathematical Notation:** Formalized $\text{TABLE}(\underline{\text{PK}}, \text{attr}, \text{FK} \rightarrow \text{RefTable.PK})$.
- [x] **Physical Schema Definitions:** Documented SQL data types, nullability, defaults, and constraints.
- [x] **Referential Integrity Actions:** Implemented `ON DELETE CASCADE` and `ON DELETE SET NULL`.

### Milestone 6: Data Dictionary
- [x] **Comprehensive Data Dictionary:** Documented all 22 domain relations and attributes.
- [x] **Column Constraints & Types:** Checked numerical bounds, enums, and default timestamps.

### Milestone 7: SQL Scripts (DDL, DML, DCL, TCL)
- [x] **DDL Scripts:** Database schema creation script in `database/schema/001_schema.sql`.
- [x] **DML Seed Manifests:** Master seed manifests for D1–D5 datasets.
- [x] **TCL Transaction Scripts:** Atomic ACID multi-table persistence in `database/transactions/001_save_itinerary.sql`.
- [x] **DCL Policies & Trigger Audit:** Row-level security and `trip_audit` triggers.

### Milestone 8: Master Sample Dataset ($\ge 5,000$ Records)
- [x] **500 Destinations:** 144 Indian & 356 Global cities across 8 geographic zones.
- [x] **6,000 Accommodations:** Exactly 12 verified hotels per destination across budget tiers.
- [x] **6,000 Dining Venues:** Exactly 12 verified restaurants per destination with diverse cuisines.
- [x] **6,000 Transit Routes:** Exactly 12 multi-modal transport options per destination.
- [x] **2,517 Attractions:** Curated sightseeing landmarks and cultural monuments.
- [x] **Live Database Audit:** Verified **21,133 total rows** in PostgreSQL (Supabase).

### Milestone 9: Complex Analytical SQL Queries (DBMS Showcase)
- [x] **Q01: Destination Cost Rank:** Window function `RANK() OVER (ORDER BY cost)`.
- [x] **Q02: Budget vs. Actual Variance:** Aggregation, `SUM()`, and `CASE` variance detection.
- [x] **Q03: Top Rated Stays by Country:** Partitioning via `ROW_NUMBER() OVER (PARTITION BY ...)`.
- [x] **Q04: Cuisine Diversity Index:** Multi-table `JOIN` and `COUNT(DISTINCT cuisine)`.
- [x] **Q05: Multi-Modal Transit Coverage:** Grouped transit connectivity metrics.
- [x] **Q06: Activity Pace Distribution:** Temporal slot distribution analysis.
- [x] **Q07: Affordable Heritage Itineraries:** Filtered subqueries and regional cost averages.
- [x] **Q08: High-Value Dining Index:** Cost percentiles and customer ratings.
- [x] **Q09: Trip Member Collaboration Audit:** Self-joins and permission matrices.
- [x] **Q10: Seasonal Climate Correlation:** Weather cross-tabulation against travel dates.

### Milestone 10: Responsive Web Application
- [x] **React 19 SPA Client:** High-contrast, elegant minimalist user interface.
- [x] **Interactive Autocomplete:** Google-search-style destination keyword search.
- [x] **Timeline & Schedule Visualizer:** Day-by-day morning, afternoon, and evening activity cards.
- [x] **Budget Visualizer & Deficit Alerts:** Category progress bars and deficit warnings.
- [x] **Manual Activity Swapping Modal:** Real-time entity replacement and cost recalculation.
- [x] **Curated Landmark Photography:** 500 famous landmark photos and Google Maps links.

### Milestone 11: AI Integration & Grounding
- [x] **Multi-Provider LLM Gateway:** Google Gemini, Groq Cloud, OpenAI support.
- [x] **Deterministic Heuristic Fallback:** Offline scheduler ensuring 0% failure during API outages.
- [x] **Bounded Travel Copilot (Chatbot):** Interactive sliding chat drawer with trip grounding.
- [x] **Weather Forecast Grounding:** Open-Meteo live climate integration.
- [x] **Dynamic Packing Checklist:** Weather-aware packing recommendations.

### Milestone 12: Presentation & Live Demonstration
- [x] **15-Slide Presentation Outline:** Documented in presentation guide.
- [x] **7-Minute Live Demo Script:** Step-by-step presentation script prepared.
- [x] **Viva Questions & Answers:** Prepared theoretical and database defense answers.
- [ ] **Individual Team PPT Preparation:** Each team member creates individual slide deck.
- [ ] **Live Faculty Demonstration & Defense:** Conduct final project viva presentation.

---

## 🛠️ 2. Core Functional & Technical Checklist

- [x] **User Registration & Login (Bcrypt + JWT):** `backend/app/routers/auth.py`
- [x] **Role-Based Access Control (`admin` / `traveller`):** `backend/app/services/auth_service.py`
- [x] **IDOR Security Guards:** Verified across all trip, chat, and packing endpoints.
- [x] **Catalogue Browsing & Filtering:** `frontend/src/pages/DestinationsPage.jsx`
- [x] **Trip Planner Wizard:** `frontend/src/pages/PlanPage.jsx`
- [x] **Trip History & Bookmarks:** `frontend/src/pages/TripsPage.jsx`
- [x] **DBMS Showcase Dashboard:** `frontend/src/pages/ShowcasePage.jsx`
- [x] **Automated Backend Pytest Suite:** **147 / 147 PASS**
- [x] **Automated Frontend Vitest Suite:** **15 / 15 PASS**
- [x] **Frontend Production Build Gate:** **0 Errors, 0 Warnings**

---

## 🚀 3. Future Enhancements & Post-MVP Roadmap (To Do)

- [ ] **Multi-Currency Conversion:** Dynamic exchange rate conversion (USD, EUR, GBP, JPY, AED).
- [ ] **Real-Time Booking APIs:** Integration with live GDS / OTA booking engines (Amadeus, Skyscanner, Booking.com).
- [ ] **Group Collaboration WebSockets:** Real-time multi-user collaborative itinerary editing.
- [ ] **Mobile App / Progressive Web App (PWA):** Offline mobile app with SQLite synchronization.
- [ ] **User Avatar Upload:** Custom profile image upload to cloud storage.
- [ ] **PDF Itinerary Export:** One-click downloadable PDF itinerary and expense summary.
- [ ] **Social Sharing Links:** Public read-only shareable links for saved itineraries.
