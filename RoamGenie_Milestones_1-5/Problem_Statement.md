# AI Travel Planner & Budget Optimizer — RoamGenie
## Academic Milestone 1: Problem Statement

---

### 1. Project Title
**AI Travel Planner & Budget Optimizer — RoamGenie**

---

### 2. Background
Tourism and leisure travel planning are cognitively demanding processes requiring travellers to balance multiple interdependent logistical factors simultaneously:
* **Total Budget & Spending Limits:** Ensuring total expenditure does not exceed available funds while maintaining comfortable standards of accommodation, food, and sightseeing.
* **Trip Duration & Temporal Feasibility:** Structuring activities across available days without overloading daily schedules.
* **Geographic Destinations & Local Geography:** Selecting appropriate cities and understanding regional travel times.
* **Tourist Attractions & Landmarks:** Discovering authentic cultural, historical, and recreational spots.
* **Accommodation & Lodging:** Choosing hotels or resorts that fit budget tiers and quality expectations.
* **Restaurants & Regional Dining:** Selecting dining venues that accommodate dietary requirements (e.g., vegetarian, halal, regional specialties).
* **Transportation & Transit Modes:** Coordinating flights, express trains, inter-city buses, and local cabs.
* **Weather & Climate Conditions:** Factoring regional temperature, precipitation, and seasonal weather into indoor vs. outdoor scheduling.
* **User Preferences:** Aligning travel pace (relaxed vs. fast-paced) and activity interests (heritage, nature, culinary, adventure).

Currently, travellers perform this synthesis manually by toggling between disconnected hotel booking platforms, flight aggregators, review forums, map services, and personal spreadsheets.

---

### 3. Problem
Manual travel planning across multiple fragmented systems introduces critical challenges:
1. **Cognitive Overload & Fragmentation:** Users must manually aggregate information from dozens of disparate websites, leading to planning fatigue and fragmented reservations.
2. **Budget Miscalculation & Unnoticed Deficits:** Static booking sites do not provide unified, multi-category budget tracking. Travellers frequently experience cost overruns because accommodation, transit, and daily dining expenses are calculated independently.
3. **Generic & Hallucinatory AI Recommendations:** When using general-purpose Large Language Models (LLMs) for travel itineraries, models frequently hallucinate non-existent establishments, recommend permanently closed attractions, invent inaccurate prices, or generate geographically impossible daily schedules due to a lack of grounded relational database integration.
4. **Rigid & Inflexible Plans:** Pre-packaged holiday tours lack customization, while static manual spreadsheets cannot dynamically re-calculate downstream schedule impacts or budget deficits when an individual activity or hotel is modified.

---

### 4. Proposed Solution
**RoamGenie** solves this problem by combining **relational database management system (DBMS) engineering** with **algorithmic constraint scheduling** and **grounded artificial intelligence (AI)**:
* **Centralized Master Catalogue:** A normalized, 3NF-compliant PostgreSQL database storing structured records for destinations, accommodations, dining establishments, attractions, and multi-modal transit options.
* **Deterministic Itinerary & Budget Engine:** An algorithmic scheduler that takes natural user constraints (*"I have ₹30,000, 5 days, and want to explore Jaipur"*), divides the journey into morning, afternoon, and evening slots, and allocates expenses across dedicated budget envelopes.
* **Interactive Activity Swapping:** Allows travellers to customize scheduled items with verified catalogue alternatives while atomically recalculating budget totals and deficit warnings.
* **Grounded AI Travel Copilot:** An intelligent travel assistant that provides contextual advice grounded strictly in database facts and live weather forecasts, eliminating generative hallucinations.

---

### 5. Objectives
1. **Budget-Aware Travel Planning:** Enable travellers to define an overarching budget constraint and automatically compute itemized cost allocations across accommodation, dining, sightseeing, and transport.
2. **Personalized Day-Wise Itinerary Generation:** Automatically generate structured multi-day itineraries slotted into discrete morning, afternoon, and evening activities based on user-selected pace and destination.
3. **Centralized Travel Information:** Consolidate comprehensive destination profiles, hotel options, dining venues, sightseeing landmarks, and transit routes within a single relational database schema.
4. **Efficient Resource Utilization:** Prevent travel overspending through real-time deficit detection, alerting users whenever estimated itinerary costs exceed their total budget envelope.
5. **Database-Driven Recommendations:** Ground all scheduling and generative AI suggestions in verified database entities to ensure operational realism and zero hallucinations.
6. **Supporting Travel Decision-Making:** Provide an interactive, responsive user interface with climate awareness, smart packing suggestions, and manual entity swapping to assist travellers in making informed planning decisions.

---

### 6. Scope

#### In-Scope (Milestones 1–5):
* Formalization of domain problem statement and Software Requirements Specification (SRS).
* Relational database conceptual modeling and Entity-Relationship (ER) diagram design.
* Functional dependency analysis and database normalization up to 3NF/BCNF.
* Complete relational schema specification with primary keys, foreign keys, integrity constraints, and cascade actions across all 22 domain relations.
* Architectural definitions for user management, master catalogue data, trip planning, budget allocation, weather grounding, and AI assistance.

#### Out-of-Scope (Milestones 1–5):
* Real-world payment gateway execution and commercial banking integrations.
* Direct airline Global Distribution System (GDS) live ticket issuance.
* Complex analytical query optimization benchmarks (covered in Milestone 9).
* Web application deployment and live presentation demonstrations (covered in Milestones 10–12).

---

### 7. Target Users
* **Solo & Budget Travellers:** Individuals requiring strict financial capping, affordable transit options, and cost-effective lodging.
* **Family & Group Vacation Planners:** Groups requiring coordinated multi-person budget multiplication, diverse dining choices, and balanced daily itineraries.
* **Cultural & Leisure Tourists:** Travellers seeking curated heritage, monument, and culinary recommendations tailored to regional specialties.
* **Academic Evaluators:** Course instructors evaluating database normalization, referential integrity, and software engineering rigor.

---

### 8. Expected Outcome
The system produces a comprehensive, verified, and budget-optimized travel plan containing:
1. **Day-by-Day Activity Schedule:** Sequenced morning, afternoon, and evening activity slots.
2. **Itemized Budget Breakdown:** Transparent category distribution (Accommodation, Dining, Sightseeing, Transport) with clear deficit/surplus indicators.
3. **Verified Entity Details:** Specific hotel names, restaurant cuisines, attraction entry fees, and transit durations pulled directly from the relational database.
4. **Adaptive Contextual Guidance:** Climate-aware packing items and personalized travel recommendations.
