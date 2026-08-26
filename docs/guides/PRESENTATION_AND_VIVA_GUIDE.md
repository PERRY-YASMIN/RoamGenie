# Presentation, Live Demo & Viva Defense Guide

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
│ Slide 06: Relational Data Model: 22-Table ER Diagram & Cardinalities   │
│ Slide 07: Normalization Analysis: Mathematical Proofs (1NF to BCNF)    │
│ Slide 08: Relational Database Objects: Views, Functions & Procedures   │
│ Slide 09: PL/pgSQL Audit Triggers & ACID Transactional Persistence     │
│ Slide 10: Indexing Strategy & Query Optimization (EXPLAIN ANALYZE)     │
│ Slide 11: Bounded AI Gateway & Deterministic Scheduler Fallback        │
│ Slide 12: Application Modules: React Frontend, Wizard & Showcase UI    │
│ Slide 13: Master Catalogue Datasets (500 Cities, 21,017 Items)         │
│ Slide 14: Automated Testing Strategy & Test Results (187 Tests PASS)   │
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
    DBMS Showcase (18 Queries, Views, Triggers) :5:30, 1m00s
    Test Suite Evidence (187 Tests) & Viva QA   :6:30, 0m30s
```

### Live Demo Script Breakdown:
1. **0:00 – 0:45 (Introduction):** Introduce RoamGenie's core objective: solving fragmented travel planning using a centralized 22-table PostgreSQL database with constraint optimization.
2. **0:45 – 1:45 (Catalogue & Auth):** Log in as a registered user (`/login`). Browse the 500-destination catalogue on `/destinations`, demonstrating accommodation, dining, and attraction inspection cards.
3. **1:45 – 3:00 (Trip Engine & Budgeting):** Open `/plan`. Enter trip constraints (Jaipur, 4 days, 2 travellers, ₹20,000 budget). Click "Generate". Show day-wise scheduled timeline events, category budget breakdowns, and weather snapshot.
4. **3:00 – 4:00 (Manual Catalogue Swap):** Click "⇄ Swap" on Day 1 Hotel $\rightarrow$ select alternative accommodation from catalogue $\rightarrow$ observe instant budget visualizer recalculation, deficit alert handling, and toast notification.
5. **4:00 – 4:45 (Persistence & Reload):** Click "☆ Save to Bookmarks". Navigate to `/trips` ("My Trips") to show transactional persistence. Click "Open Itinerary →" to demonstrate instant saved-trip reload without re-generation or row duplication.
6. **4:45 – 5:30 (Grounded AI Copilot):** Open "💬 Ask AI Copilot" $\rightarrow$ click quick suggestion "What should I pack?" $\rightarrow$ ask follow-up budget optimization question, demonstrating authorized contextual grounding.
7. **5:30 – 6:30 (DBMS Academic Showcase):** Navigate to `/showcase`. Execute sample analytical queries (e.g., Q01, Q05 Window Functions, Q12 Correlated Subqueries). Show execution times in milliseconds, demonstrate custom SQL read-only security guards, and inspect the live PL/pgSQL `trip_audit` trigger log.
8. **6:30 – 7:00 (Conclusion & Testing):** Display terminal output showing all 172 backend tests and 15 frontend tests passing 100% (187 total tests).

---

## 3. High-Yield Viva Defense Q&A

### Q1: Why use PostgreSQL for an AI travel planner rather than a NoSQL/document database?
**Answer:** Travel itineraries require strict relational consistency across multi-table parent-child structures (`trips` $\rightarrow$ `itineraries` $\rightarrow$ `itinerary_days` $\rightarrow$ `itinerary_items` and `budget_allocations`). PostgreSQL provides ACID transactions, composite foreign key cascades, JSONB flexibility for audit triggers, and complex analytical window functions that ensure data integrity.

### Q2: How does RoamGenie prevent SQL injection in the Custom SQL Editor?
**Answer:** The custom SQL runner requires the `admin` role, validates queries using strict regex and AST parsing to reject multi-statement chaining (semicolons), blocks mutating keywords (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`), and explicitly blocks access to sensitive tables and columns (`users`, `user_preferences`, `password_hash`).

### Q3: How is the AI Copilot prevented from hallucinating non-existent catalogue data?
**Answer:** The AI Copilot uses a grounded prompt architecture (`ai_prompts.py`) that injects verified database entities (accommodations, dining venues, attractions, transport tariffs) into the prompt context. If external LLMs fail or are unavailable, a deterministic fallback service produces verified catalogue-grounded output.

### Q4: How is User Ownership and IDOR protection enforced?
**Answer:** Every protected API endpoint extracts the authenticated user ID from the verified JWT payload. Service layers execute ownership validation (`verify_trip_ownership`) before querying or mutating child entities (itineraries, packing items, chat threads), returning `403 Forbidden` for unauthorized attempts.
