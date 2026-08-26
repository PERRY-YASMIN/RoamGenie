# RoamGenie — Problem Statement

## 1. Context & Background
Planning multi-day leisure travel remains a fragmented, cognitively exhausting process for modern travellers. A typical user must consult dozens of disconnected services:
1. **Catalogue Aggregators:** Searching for tourist attractions, accommodations, and dining across separate portals.
2. **Transportation Services:** Estimating flight, train, and bus transit costs and schedules manually.
3. **Budget Trackers:** Performing manual spreadsheet calculations to ensure itineraries fit within strict spending limits.
4. **Weather Forecasts:** Manually cross-referencing regional climate conditions to pack appropriate clothing and schedule outdoor vs. indoor activities.
5. **AI Travel Generative Mocks:** Generic LLM prompts often hallucinate non-existent establishments, ignore financial constraints, or output unrealistic itineraries disconnected from verifiable relational data.

## 2. Problem Definition
Travellers lack an integrated, trustworthy platform that can take a natural language input such as:
> **"I have ₹30,000, 5 days, and I want to explore heritage and cuisine in Jaipur."**

...and immediately produce a **deterministic, relationally grounded, budget-optimized multi-day itinerary** backed by verified PostgreSQL records for hotels, dining venues, sightseeing attractions, and transit options.

## 3. Academic DBMS & AI Objectives
RoamGenie addresses this challenge by fusing **Relational Database Management System (DBMS)** principles with modern **Bounded Artificial Intelligence (AI)** orchestration:

1. **Relational Data Integrity:** Store a comprehensive catalogue (>20,000 records) of destinations, attractions, accommodations, restaurants, and transit options normalized in Third Normal Form (3NF).
2. **Deterministic Constraint Engine:** Enforce strict budget limits (e.g. 40% Stay, 25% Food, 20% Sightseeing, 15% Transit) with algorithmic budget tracking and deficit alerts.
3. **Weather-Grounded Scheduling:** Snapshot and ground trip itineraries with regional climate forecasts to guide indoor/outdoor scheduling.
4. **Bounded AI Copilot:** Provide an interactive conversational assistant that answers queries about packing, budget optimization, and sightseeing strictly grounded in verified database facts.
5. **Complex Analytical Reporting:** Provide 10 advanced DBMS SQL queries with aggregations, window functions, and multi-table joins to audit travel spending patterns and catalogue distributions.

## 4. Key Stakeholders & Personas
- **Solo & Budget Travellers:** Require strict cost-capped itineraries with budget-tier transit and hotels.
- **Family & Group Planners:** Require multi-person budget multiplication and diversified dining/activity scheduling.
- **Database Administrators / Evaluators:** Require normalized schemas, zero foreign-key orphans, transactional consistency (ACID), and robust analytical query execution.
