# RoamGenie — Release Notes v1.0.0

**Release Version:** `v1.0.0`  
**Release Date:** 2026-08-26  
**Status:** **MVP RELEASE READY (PASS)**

---

## 1. What's New in RoamGenie v1.0.0

### Core Functional Capabilities
- **500-Destination Catalogue:** Complete catalogue covering 144 Indian and 356 global cities with dedicated famous landmark cover photography and direct Google Maps exploration links.
- **Interactive Autocomplete Planner:** Google-search-style autocomplete for destination selection with real-time keyword filtering.
- **Multi-Day Itinerary Engine:** Automated schedule generation with temporal morning/afternoon/evening slots and manual entity swapping.
- **Budget Optimizer & Deficit Warning System:** 4-category allocation solver with live visual progress bars and alert state triggers.
- **Bounded AI Travel Copilot (Chatbot):** Context-aware sliding chat assistant grounded in trip parameters, destination catalogue rows, and weather forecasts.
- **Smart Packing Checklist:** Weather-aware packing list generator with item toggles and custom additions.
- **Trip Persistence & Bookmarks:** PostgreSQL persistence with IDOR security checks and user history dashboard.
- **DBMS Showcase (10 Analytical SQL Queries):** Live query runner demonstrating window functions, aggregations, and subqueries.

---

## 2. Verified Quality & Stability Metrics

- **Backend Pytest:** **147 / 147 PASS (100%)**
- **Frontend Vitest:** **15 / 15 PASS (100%)**
- **Frontend Build:** **PASS** (0 errors, 0 warnings)
- **Live Database Records:** **21,133 rows** across 23 tables
- **Referential Integrity:** **0 foreign-key orphans**
