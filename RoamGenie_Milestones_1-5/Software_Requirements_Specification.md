# Software Requirements Specification (SRS)
## AI Travel Planner & Budget Optimizer — RoamGenie
### Academic Milestone 2: Software Requirements Specification

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) documents the functional, non-functional, data, and interface requirements for **RoamGenie**, an AI-driven travel planning and relational budget optimization platform. This document establishes the technical baseline for academic evaluation in Database Management Systems.

### 1.2 Scope
RoamGenie automates the generation of multi-day, budget-constrained travel itineraries. The system integrates a 22-table normalized relational database (PostgreSQL) containing destinations, accommodations, dining venues, sightseeing attractions, and transit options. It incorporates deterministic scheduling heuristics, real-time budget optimization, weather grounding, dynamic packing checklists, manual entity swapping, and a bounded conversational travel assistant.

### 1.3 Product Perspective
RoamGenie operates as a decoupled three-tier database application:
1. **Presentation Tier:** A responsive Single Page Application (SPA) built using React 19 and Vite.
2. **Application Tier:** An asynchronous REST API built using FastAPI (Python 3.12) and SQLAlchemy 2.0 ORM, handling business logic, authentication, constraint solving, and AI orchestration.
3. **Database Tier:** A normalized PostgreSQL 15+ relational database enforcing strict referential integrity, domain constraints, and ACID transactions.

### 1.4 Intended Audience
This document is prepared for academic evaluators, software engineering instructors, database architects, and developer team members.

---

## 2. System Overview

RoamGenie consolidates travel intelligence across the following core modules:
* **Authentication & Profile Subsystem:** Manages encrypted user credentials, session tokens, and travel preferences.
* **Master Catalogue Subsystem:** Manages structured destination records, hotels, restaurants, attractions, and transit routes.
* **Deterministic Itinerary Scheduler:** Solves multi-day temporal constraints, assigning morning, afternoon, and evening slots.
* **Budget Optimization Engine:** Itemizes expenditures across four categories (Stay 40%, Food 25%, Sights 20%, Transit 15%) and detects financial deficits.
* **Climate & Packing Assistant:** Retrieves weather forecasts and generates contextual packing checklists.
* **Bounded AI Copilot:** Coordinates context-grounded conversational travel guidance without generative hallucinations.

---

## 3. User Roles

The system explicitly supports two user roles:
1. **`traveller` (Standard User):**
   - Can register, log in, and maintain a travel profile.
   - Can search and explore destination catalogues.
   - Can generate, customize, save, and manage personal multi-day itineraries.
   - Can use the AI Copilot and manage packing checklists.
2. **`admin` (System Administrator):**
   - Possesses all `traveller` privileges.
   - Has permission to manage catalogue records and inspect system audit ledgers.
   - Has permission to execute administrative DBMS diagnostic queries.

---

## 4. Functional Requirements (FR)

| Req ID | Requirement Title | Detailed Functional Description |
| :--- | :--- | :--- |
| **FR-01** | **User Registration & Hashing** | The system shall allow new users to register using a valid email, display name, and password. Passwords must be securely salted and hashed using `bcrypt` / `argon2id` before database persistence. |
| **FR-02** | **Authentication & JWT Issuance** | The system shall authenticate user credentials and issue signed JSON Web Tokens (JWT) using HMAC-SHA256 with configured expiration periods. |
| **FR-03** | **User Preferences Management** | The system shall record and update user-specific travel preferences, including preferred hotel tier, dietary preferences, transit preferences, and travel pace in `user_preferences`. |
| **FR-04** | **Destination Catalogue Browsing** | The system shall provide searchable, paginated browsing of destination cities with associated country names, descriptions, and average daily cost baselines. |
| **FR-05** | **Autocomplete Destination Search** | The trip planner shall provide live keyword autocomplete search filtering across active destination records in the database. |
| **FR-06** | **Trip Creation & Parameter Input** | The system shall accept trip parameters: destination ID, starting location, start date, end date, traveller count ($>0$), and total budget ($>0$). |
| **FR-07** | **Deterministic Itinerary Scheduling** | The system shall compute the trip duration ($N = \text{end\_date} - \text{start\_date} + 1$) and allocate activities into morning, afternoon, and evening slots for each day. |
| **FR-08** | **Accommodation Recommendations** | The system shall query and assign verified hotels from the `hotels` table matching the destination and user budget constraints. |
| **FR-09** | **Dining Recommendations** | The system shall query and schedule dining venues from the `restaurants` table matching the destination, considering cuisine variety and average cost per person. |
| **FR-10** | **Attraction Scheduling** | The system shall query and sequence sightseeing landmarks from the `attractions` table based on category diversity and entry fees. |
| **FR-11** | **Transit Option Scheduling** | The system shall identify and display available transportation options from `transport_options` linking origin and destination. |
| **FR-12** | **Weather Forecast Integration** | The system shall retrieve 5-day temperature and weather condition forecasts for the destination and store snapshots in `weather_snapshots`. |
| **FR-13** | **Budget Optimization & Deficit Alerts** | The system shall calculate category budget distributions and trigger an `alert-deficit` state whenever total estimated costs exceed the user's allocated budget envelope. |
| **FR-14** | **Manual Activity Swapping** | The system shall permit users to replace any scheduled hotel, dining venue, or attraction with an alternative catalogue entity, dynamically updating schedule costs and budget totals atomically. |
| **FR-15** | **Transactional Trip Persistence** | The system shall persist trips via ACID-compliant multi-table transactions across `trips`, `itineraries`, `itinerary_days`, `itinerary_items`, and `budget_allocations`. |
| **FR-16** | **Bounded AI Travel Copilot** | The system shall provide an interactive conversational assistant that answers travel queries strictly grounded in trip parameters, destination catalogue entries, and weather snapshots. |
| **FR-17** | **Smart Packing Checklist** | The system shall generate climate-aware packing checklists with interactive item addition, deletion, and toggle packed status. |
| **FR-18** | **IDOR Access Control Enforcement** | The system shall enforce Insecure Direct Object Reference (IDOR) checks verifying that a requesting user is the owner of the targeted trip or possesses the `admin` role. |

---

## 5. Non-Functional Requirements (NFR)

### 5.1 Performance
* **NFR-01 (Search Latency):** Destination autocomplete and catalogue search queries shall execute and return responses within $< 100\text{ ms}$.
* **NFR-02 (Itinerary Generation Time):** Deterministic heuristic itinerary scheduling shall complete within $< 250\text{ ms}$.

### 5.2 Usability & Design
* **NFR-03 (UI Contrast & Legibility):** The interface shall maintain strict high-contrast typography across dark and light surfaces, avoiding blurry text drop-shadows.
* **NFR-04 (Responsive Layouts):** The application layout shall adapt seamlessly across desktop, tablet, and mobile viewport widths.

### 5.3 Reliability & Availability
* **NFR-05 (Offline Fallback):** If third-party AI or weather APIs are unreachable, the system shall seamlessly fall back to deterministic database heuristics without crashing.
* **NFR-06 (Transactional ACID Guarantees):** Multi-table trip saving operations shall execute within atomic transactions; failures during any step must trigger a full rollback.

### 5.4 Security
* **NFR-07 (Password Protection):** Passwords shall never be stored in plaintext and must be hashed using industry-standard salted `bcrypt` / `argon2id`.
* **NFR-08 (SQL Injection Defense):** All database operations shall use parameterized queries and typed ORM models to prevent SQL injection vulnerabilities.
* **NFR-09 (Resource Authorization):** Endpoints modifying trips, itineraries, packing items, or chat logs shall verify user ownership before performing mutations.

### 5.5 Data Integrity
* **NFR-10 (Referential Integrity):** The database shall enforce foreign key constraints with explicit cascading delete actions where appropriate, ensuring zero orphan records.

---

## 6. Data Requirements

The system manages four primary categories of data:
1. **Master Catalogue Data:** Static and semi-static travel information across destinations, accommodations, dining establishments, attractions, and transit options.
2. **User & Profile Data:** Account credentials, security roles, travel styles, and dietary preferences.
3. **Trip & Itinerary Transactional Data:** User-created travel plans, versioned itineraries, discrete day slots, scheduled activity items, budget allocations, and realized expenses.
4. **Contextual & Climate Data:** Weather snapshots, packing checklists, destination reviews, and AI conversation logs.

---

## 7. System Constraints
* **Monetary Unit:** All financial quantities are stored and computed in Indian Rupees (₹ / INR).
* **Trip Span Limits:** Maximum trip duration supported by the scheduler is 30 days; $\text{start\_date} \le \text{end\_date}$ is strictly enforced.
* **Guest Preview Isolation:** Unauthenticated users may generate in-memory itinerary previews with a guaranteed 0-database-insert constraint until registration/login.

---

## 8. Assumptions and Dependencies
* The client device runs a modern HTML5/ES6-compliant web browser.
* The PostgreSQL database server maintains active connectivity for transactional operations.
* External weather and AI endpoints are treated as optional enhancements with guaranteed fallback to internal database heuristics.

---

## 9. Major Use Cases

### Use Case UC-01: Generate Multi-Day Itinerary
* **Actor:** Registered Traveller / Guest User
* **Precondition:** User selects a valid destination from the autocomplete catalogue.
* **Flow:**
  1. User inputs dates, traveller count, and total budget.
  2. User submits the planning form.
  3. System validates input constraints.
  4. Scheduler queries destination hotels, restaurants, and attractions from PostgreSQL.
  5. System generates day-wise morning, afternoon, and evening slots.
  6. Budget optimizer calculates category allocations and checks for deficits.
  7. System renders timeline and budget progress visualizers.

### Use Case UC-02: Manual Catalogue Activity Swapping
* **Actor:** Authenticated Traveller
* **Precondition:** Itinerary is generated and displayed on screen.
* **Flow:**
  1. User clicks "⇄ Swap" on a scheduled activity.
  2. System queries destination catalogue for alternative entities in that category.
  3. User selects a replacement entity.
  4. System replaces the activity title, category, and cost.
  5. System recalculates daily expenses, total estimated cost, and category allocations atomically.

### Use Case UC-03: Grounded AI Copilot Consultation
* **Actor:** Authenticated Traveller
* **Precondition:** User opens the AI Copilot chat drawer with an active trip.
* **Flow:**
  1. User submits a travel question (e.g., *"What should I pack for rainy weather?"*).
  2. Backend loads trip parameters, destination details, and weather snapshots from PostgreSQL.
  3. Orchestrator passes grounded context to the AI engine.
  4. System returns bounded advice and appends message turns to `ai_messages`.

---

## 10. Requirements Summary

RoamGenie's requirements establish a balanced, cohesive system combining rigorous relational database engineering (22 domain tables in 3NF), deterministic constraint scheduling, and bounded AI assistance. All 18 functional requirements and 10 non-functional requirements are grounded directly in the actual implementation.
