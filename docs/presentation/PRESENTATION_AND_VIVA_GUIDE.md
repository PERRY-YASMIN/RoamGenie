# RoamGenie — Presentation, Live Demo & Viva Defense Guide

**Project:** RoamGenie — AI Travel Planner & Budget Optimizer  
**Course:** Database Management Systems (Semester 5 Theory & Project)  
**Execution Model:** Solo Developer  
**Target Live Demo Duration:** 7 Minutes  
**Status:** **Authoritative Viva Guide (v1.0.0 Verified Baseline)**

---

## 1. 15-Slide Presentation Outline

```
┌────────────────────────────────────────────────────────────────────────┐
│                      15-SLIDE PRESENTATION STRUCTURE                   │
├────────────────────────────────────────────────────────────────────────┤
│ Slide 01: Title, Project Name, Student Details & Executive Summary     │
│ Slide 02: Problem Statement: Fragmented Travel Tools & Overspending    │
│ Slide 03: The RoamGenie Solution: Centralized Relational Travel Engine │
│ Slide 04: Project Scope: In-Scope Capabilities vs Scope Boundaries     │
│ Slide 05: System Architecture: 3-Tier Decoupling & Security Perimeter  │
│ Slide 06: Relational Data Model: 23-Table ER Diagram & Cardinalities   │
│ Slide 07: Normalization Analysis: Mathematical Proofs (1NF to 3NF)     │
│ Slide 08: Relational Database Objects: Views, Functions & Procedures   │
│ Slide 09: PL/pgSQL Audit Triggers & ACID Transactional Persistence     │
│ Slide 10: Indexing Strategy & Query Optimization                       │
│ Slide 11: Bounded AI Gateway & Deterministic Scheduler Fallback        │
│ Slide 12: Application Modules: React Frontend, Wizard & Showcase UI    │
│ Slide 13: Master Catalogue Datasets (500 Cities, 21,133 Total Rows)    │
│ Slide 14: Automated Testing Strategy & Test Results (162 Tests PASS)   │
│ Slide 15: Conclusion, Key Takeaways & Viva Q&A                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 7-Minute Live Demonstration Timeline & Script

```mermaid
gantt
    title 7-Minute Live Demonstration Schedule
    dateFormat  m:s
    axisFormat  %M:%S
    section Demo Flow
    Architecture & Problem Overview             :0:00, 0m45s
    User Auth & Catalogue Explorer              :0:45, 1m00s
    Trip Planning Wizard & Budget Visualizer    :1:45, 1m15s
    Manual Catalogue Item Swap & Deficit Check  :3:00, 1m00s
    Saved Trips Reload Persistence              :4:00, 0m45s
    Grounded AI Travel Copilot Chat             :4:45, 0m45s
    DBMS Showcase (10 Analytical SQL Queries)   :5:30, 1m00s
    Test Suite Evidence (162 Tests) & Viva QA   :6:30, 0m30s
```

### Live Demo Script Breakdown:
1. **0:00 – 0:45 (Introduction):** Introduce RoamGenie's core objective: solving fragmented travel planning using a centralized 23-table PostgreSQL database with constraint optimization.
2. **0:45 – 1:45 (Catalogue & Auth):** Log in as a registered user (`/login`). Browse the 500-destination catalogue on `/destinations`, demonstrating accommodation, dining, and attraction inspection cards with landmark photos and Google Maps links.
3. **1:45 – 3:00 (Trip Engine & Budgeting):** Open `/plan`. Enter trip constraints (Jaipur, 4 days, 2 travellers, ₹20,000 budget) via live autocomplete. Click "Generate". Show day-wise scheduled timeline events, category budget breakdowns, and weather snapshot.
4. **3:00 – 4:00 (Manual Catalogue Swap):** Click "⇄ Swap" on an activity $\rightarrow$ select alternative accommodation from catalogue $\rightarrow$ observe instant budget visualizer recalculation, deficit alert handling, and toast notification.
5. **4:00 – 4:45 (Persistence & Reload):** Click "☆ Save to Bookmarks". Navigate to `/trips` ("My Trips") to show transactional persistence. Click "Open Itinerary →" to demonstrate instant saved-trip reload without re-generation or row duplication.
6. **4:45 – 5:30 (AI Travel Copilot Chat):** Open the "🤖 AI Copilot" floating drawer. Ask: *"What should I pack for this trip?"* Show weather-grounded conversational response and the synchronized smart packing checklist.
7. **5:30 – 6:30 (DBMS Showcase):** Open `/showcase`. Execute complex analytical queries (e.g. Q01 Destination Cost Rank, Q03 Top Rated Stays with `ROW_NUMBER()`, Q04 Cuisine Diversity, Q10 Weather Correlation).
8. **6:30 – 7:00 (Verification & Conclusion):** Present test suite evidence (`147 backend + 15 frontend = 162 PASS`) and open for Viva Examiner questions.

---

## 3. High-Yield Viva Examiner Questions & Answers

### Q1: Why use a Relational Database (PostgreSQL) instead of NoSQL (MongoDB) for travel planning?
**Answer:** Travel planning requires strict **referential integrity** and **multi-entity transactions** (e.g., creating a trip atomically inserts records into `trips`, `itineraries`, `itinerary_days`, `itinerary_items`, and `budget_allocations`). If any step fails, the entire transaction rolls back via ACID compliance. Furthermore, our 10 analytical queries rely heavily on relational multi-table `JOIN`s, `GROUP BY`, and window functions (`RANK()`, `ROW_NUMBER()`) which PostgreSQL executes with high optimization.

### Q2: How did you achieve 3NF normalization?
**Answer:** Every base table has a single primary key. Non-key attributes depend strictly and exclusively on the primary key:
- In `hotels`, price and rating depend on `hotel.id`. Destination details (country, description) are stored separately in `destinations` and linked via foreign key `destination_id`, avoiding data redundancy and transitive dependencies.

### Q3: How do you prevent AI hallucinations in the generated itinerary?
**Answer:** We enforce **Bounded Relational Grounding**. Before invoking the AI orchestrator, the backend queries real PostgreSQL records for hotels, dining venues, and attractions matching the destination and budget tier. These real entities are passed into the LLM system prompt as explicit grounding facts. If the LLM produces invalid output or times out, our deterministic heuristic scheduler builds a verified itinerary directly from PostgreSQL.

### Q4: How is security handled against IDOR (Insecure Direct Object Reference)?
**Answer:** On every trip inspection, update, deletion, packing mutation, or AI chat request (`/api/v1/trips/{id}`, `/api/v1/assistant/chat`), the backend extracts the authenticated `user_id` from the JWT token and verifies that `trip.user_id == current_user.id` before executing the operation, raising `HTTP 403 Forbidden` if unauthorized.
