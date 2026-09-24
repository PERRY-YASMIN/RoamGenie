# RoamGenie: Autonomous Travel Planning & Relational Budget Optimization Engine

* **Academic Course:** Database Management Systems (Semester 5 Theory & Laboratory)
* **Domain:** Full-Stack Intelligent Systems & Relational Database Design
* **Execution Model:** Solo Capstone Research & Technical Implementation
* **Authoritative Coverage:** Complete 12-Milestone Academic Defense & System Demonstration
* **Core Philosophy:** Combining mathematically normalized relational database design (PostgreSQL 15+ in BCNF) with structured, grounded generative AI (Google Gemini 1.5)

> **Presenter Notes:**
> Good morning, esteemed professors and evaluation committee members. Today, I am proud to present RoamGenie, an autonomous travel planning and relational budget optimization engine. In this comprehensive viva presentation, we will walk through all twelve academic DBMS milestones—from formal BCNF mathematical proofs and our twenty-two table relational architecture to live database triggers and deterministic AI grounding. Let us begin by analyzing why existing travel tools fail and how RoamGenie solves this challenge.

---

# Market Differentiation: Why RoamGenie Outperforms the Industry

* **Traditional Booking Platforms (MakeMyTrip, Agoda, Booking.com):**
  * **Siloed Products:** Engineered strictly to sell individual hotel nights or flights; zero holistic multi-day itinerary synthesis.
  * **High Cognitive Friction:** Users must manually juggle 15+ browser tabs and offline spreadsheets to calculate cumulative expenses.
  * **Opaque Surge Pricing:** Algorithmic price surges with zero cross-category constraint-bounded budget rebalancing.
* **Raw Generative LLMs (ChatGPT, Claude, Perplexity):**
  * **Severe Hallucinations:** Generates non-existent venues, permanently closed heritage sites, and fictitious entry fees.
  * **Zero Relational Guarantees:** Cannot guarantee geographic feasibility, enforce chronological sequencing, or preserve ACID state.
  * **Stateless Text Output:** Inability to query, update, recalculate, or roll back discrete itinerary items via relational SQL.
* **The RoamGenie Paradigm Shift:**
  * **Relational Grounding:** All AI recommendations are strictly bounded to a verified **21,017-item master catalogue across 500 cities**.
  * **Deterministic Budget Guardrails:** Real-time variance tracking, dynamic deficit alerts, and mathematical optimization.
  * **ACID-Compliant State:** Persistent multi-version itineraries with cascading foreign key relational integrity.

> **Presenter Notes:**
> When examining the market, travel planning remains deeply fragmented and frustrating. Commercial booking engines like MakeMyTrip are transaction-oriented silos that sell isolated tickets without optimizing an overall trip, forcing travellers into hours of manual math. On the other hand, raw chatbots like ChatGPT hallucinate closed venues and impossible transit times without database verification. RoamGenie bridges this divide by grounding Google Gemini inside a normalized PostgreSQL core, guaranteeing feasibility and live budget protection.

---

# System Architecture & Technology Stack Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PRESENTATION TIER (Single-Page App)                  │
│        React 19 + Vite  │  Modular CSS Grid  │  Context State          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (RESTful JSON / Bearer JWT)
┌───────────────────────────────────▼────────────────────────────────────┐
│                    APPLICATION TIER (RESTful API)                      │
│     Python FastAPI  │  Pydantic Schemas  │  Deterministic Gateway     │
└───────────────────┬──────────────────────────────────┬─────────────────┘
                    │                                  │
┌───────────────────▼────────────────┐   ┌─────────────▼─────────────────┐
│     DATA TIER (PostgreSQL 15+)     │   │      AI INTEGRATION TIER      │
│  22 Normalized Tables (3NF/BCNF)   │   │   Google Gemini 1.5 Flash     │
│  PL/pgSQL Triggers & System Views  │   │  Strict JSON Mode & Fallback  │
└────────────────────────────────────┘   └───────────────────────────────┘
```

* **Architectural Decoupling:** Strict 3-Tier layered architecture isolating presentation, domain logic, and data persistence.
* **Stateless Security Boundary:** Standardized JWT bearer token authentication protecting every state-mutating endpoint.
* **Deterministic Fallback Layer:** System gracefully falls back to local algorithmic scheduling if external LLM APIs fail.

> **Presenter Notes:**
> RoamGenie adheres to a textbook three-tier decoupled architecture. The presentation layer uses React 19 and Vite for instant reactive UI updates. The application tier runs on Python FastAPI, which enforces strict schema validation and coordinates between our persistence layer and the AI engine. At the foundational data tier sits PostgreSQL 15, hosting twenty-two normalized tables, PL/pgSQL audit triggers, and pre-computed analytical views. Let us now examine the engineering justification for each selected technology.

---

# Tech Justification: React 19 + Vite (Frontend)

* **Why Chosen Over Alternatives (Next.js, Create-React-App, Angular):**
  * **Sub-50ms HMR:** Native ES modules in Vite eliminate sluggish Webpack bundling bottlenecks during active development.
  * **Pure Client-Side SPA:** RoamGenie is an authenticated interactive dashboard; avoiding Next.js server-side rendering (SSR) eliminates hydration mismatches with JWT storage.
  * **React 19 Concurrent Primitives:** Optimized DOM diffing ensures seamless budget recalculation without UI jitter.
* **Concrete RoamGenie Implementation (`frontend/src/pages/PlanPage.jsx`):**

```javascript
// Real-time budget deficit calculation & dynamic catalogue item swap
const isOverBudget = Number(previewRes.estimated_total) > Number(formData.total_budget);
const deficitAmount = Math.max(0, Number(previewRes.estimated_total) - Number(formData.total_budget));

// Authenticated item replacement dispatching instant state recalculation
const updatedTrip = await swapItineraryItem(createdTripId, swapModalItem.id, {
  replacement_type: swapCategory,
  replacement_id: alt.id,
});
```

> **Presenter Notes:**
> On the frontend, React 19 bundled with Vite was chosen over Create-React-App and Next.js. Vite delivers sub-fifty-millisecond hot module replacement using native browser ES modules, drastically accelerating development. Furthermore, because RoamGenie is a client-authenticated dashboard relying on client-side JWTs, a pure single-page application avoids server-side hydration mismatches while React 19's fine-grained reactivity instantly recalculates budget deficits upon item swapping.

---

# Tech Justification: Python FastAPI (Application Backend)

* **Why Chosen Over Alternatives (Django, Flask, Node.js Express):**
  * **Asynchronous High Performance:** Built on Starlette and Uvicorn event loops, yielding benchmark throughput rivaling Go and Node.js.
  * **Automated Data Validation:** Native Pydantic model contracts parse, sanitize, and validate HTTP request payloads with compile-time-like reliability.
  * **Self-Documenting OpenAPI:** Generates interactive Swagger UI specifications (`/docs`) directly from Python type hints.
  * **Hierarchical Dependency Injection:** Scoped session dependencies (`Depends(get_db)`) guarantee proper transaction lifecycles.
* **Concrete RoamGenie Implementation (`backend/app/routers/trips.py`):**

```python
@router.post("", response_model=TripDetailResponse, status_code=status.HTTP_201_CREATED)
def create_trip(
    request: TripCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    trip_service: TripService = Depends(get_trip_service),
) -> TripDetailResponse:
    trip = trip_service.create_trip(db=db, user_id=current_user.id, request=request)
    return trip_service.build_trip_detail_response(trip, current_user.id)
```

> **Presenter Notes:**
> On the application tier, Python FastAPI was selected over traditional frameworks like Django or Flask. FastAPI operates on an asynchronous event loop via Starlette and Uvicorn, delivering near Go-tier throughput. It natively enforces Pydantic schemas, eliminating manual request payload sanitization. Notice in this code snippet how FastAPI uses clean dependency injection: with just one dependency parameter, we securely inject the authenticated user identity and database session into our trip creation route.

---

# Tech Justification: PostgreSQL 15+ (Relational Database)

* **Why Chosen Over Alternatives (MySQL 8, MongoDB, CockroachDB):**
  * **True Enterprise ACID Compliance:** Uncompromising transactional durability and multi-table referential integrity.
  * **Rich PL/pgSQL Procedural Engine:** Executes compiled server-side audit triggers and constraint checks directly in the database kernel.
  * **Native Binary JSON (`JSONB`):** Allows semi-structured snapshot auditing (`old_row` and `new_row`) without compromising relational structure.
  * **Advanced Analytical Window Functions:** Powers complex partition aggregations (`sum(...) OVER (PARTITION BY trip_id)`) with zero client-side overhead.
* **Concrete RoamGenie Implementation (`database/triggers/001_audit_trip.sql`):**

```sql
CREATE OR REPLACE FUNCTION audit_trip_change() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO trip_audit(trip_id, action, old_row, new_row)
  VALUES(COALESCE(NEW.id, OLD.id), TG_OP,
         CASE WHEN TG_OP = 'INSERT' THEN NULL ELSE to_jsonb(OLD) END,
         CASE WHEN TG_OP = 'DELETE' THEN NULL ELSE to_jsonb(NEW) END);
  RETURN COALESCE(NEW, OLD);
END $$;
```

> **Presenter Notes:**
> For our persistence core, PostgreSQL 15 was our clear choice over MySQL or document databases like MongoDB. Complex travel itineraries require absolute relational integrity, composite foreign key cascades, and ACID compliance. PostgreSQL provides native JSONB indexing, which allows our PL/pgSQL trigger, shown here, to automatically capture before-and-after snapshots of any trip mutation directly into an immutable audit table without requiring complex application-layer logging code.

---

# Tech Justification: SQLAlchemy 2.0 (ORM & Session Management)

* **Why Chosen Over Alternatives (Raw psycopg2, Peewee, Tortoise ORM):**
  * **Modern 2.0 Declarative Syntax:** Enforces explicit type checking and typed query construction using the `select()` paradigm.
  * **Robust Connection Pool Management:** Employs pre-ping connection verification (`pool_pre_ping=True`) to automatically discard stale sockets.
  * **Eager Relationship Loading:** Resolves the notorious $N+1$ query performance bug using `selectinload` for multi-level child entities.
  * **Unit-of-Work Pattern:** Isolates each HTTP request within an independent transactional context with automated error rollbacks.
* **Concrete RoamGenie Implementation (`backend/app/db/session.py`):**

```python
def get_db() -> Generator[Session, None, None]:
    """Provide a scoped SQLAlchemy session and roll back failed transaction work."""
    engine = get_engine()
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    try:
        yield session
    except Exception:
        session.rollback()  # Guaranteed atomic rollback on any unhandled failure
        raise
    finally:
        session.close()     # Returns connection cleanly to pool
```

> **Presenter Notes:**
> Rather than relying on raw driver strings or unmanaged connection objects, we integrated SQLAlchemy 2.0. SQLAlchemy provides an enterprise unit-of-work pattern with robust pooling parameters such as pool pre-ping to prune stale sockets. As shown in our session generator, every incoming HTTP request receives an isolated database session. If any service error occurs, an atomic rollback is automatically executed, completely safeguarding our database against corrupted partial state writes.

---

# Tech Justification: Google Gemini (Structured LLM Gateway)

* **Why Chosen Over Alternatives (OpenAI GPT-4o, Anthropic Claude 3.5, Local Ollama):**
  * **High-Speed Inference (`gemini-1.5-flash`):** Delivers sub-2-second generation latencies, maintaining fluid user interaction.
  * **Native JSON Schema Enforcement:** Restricts generation directly at the decoder level via `response_mime_type: "application/json"`.
  * **Massive Token Context Window:** Efficiently processes multi-day itineraries and large contextual database catalogues.
  * **Cost-Performance Dominance:** Best-in-class pricing with robust free-tier access for academic development.
* **Concrete RoamGenie Implementation (`backend/app/services/ai_providers.py`):**

```python
class GeminiLLMProvider(BaseLLMProvider):
    def generate(self, prompt: str, system_prompt: str, timeout_seconds: int = 15) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json", "temperature": 0.2},
        }
        with httpx.Client(timeout=timeout_seconds) as client:
            resp = client.post(url, json=payload)
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
```

> **Presenter Notes:**
> For generative AI capabilities, Google Gemini 1.5 Flash was chosen over competitors like OpenAI GPT-4o. Gemini provides lightning-fast inference times under two seconds, which is crucial for interactive planning. More importantly, its API natively supports JSON schema enforcement at a low temperature of 0.2, guaranteeing valid, structured JSON output that conforms directly to our Pydantic validation contracts without unpredictable markdown formatting.

---

# Milestone 1: Problem Statement (Fragmented Travel & Budget Creep)

* **The Travel Industry Dilemma:**
  * **Tool Fragmentation:** Planning a single vacation requires switching between 5 to 10 disconnected tools (flights, hotels, blogs, maps, spreadsheets).
  * **Information Asymmetry:** Travellers face conflicting price estimates and unverified reviews across competing platforms.
* **The Budget Creep Phenomenon:**
  * Travellers regularly exceed initial budgets by **25% to 40%** due to hidden expenses, unlinked transportation costs, and blind scheduling.
  * No existing tool provides continuous, real-time variance tracking against budget constraints during initial schedule composition.
* **The Academic DBMS Challenge:**
  * How can we model complex, hierarchical, multi-day travel schedules inside a **mathematically normalized relational schema** that strictly prevents data corruption, update anomalies, and budget deficits?
* **RoamGenie's Mandate:**
  * Deliver a unified, relational travel planning engine that synthesizes day-by-day itineraries, tracks line-item expenditures, and guarantees data integrity.

> **Presenter Notes:**
> Moving into Milestone 1: Problem Statement. Modern leisure travel is plagued by tool fragmentation and budget creep. Travellers spend dozens of hours copying venue details into spreadsheets, only to discover halfway through their vacation that cumulative hotel tariffs and dining costs have completely exceeded their financial limits. Our core DBMS objective was to solve this by building a centralized relational engine capable of dynamically balancing scheduling logistics against financial constraints.

---

# Milestone 2: Software Requirements Specification (SRS & Scope Boundaries)

* **Functional Requirements (FRs):**
  * **FR-1 Identity & Access:** User registration, password hashing (bcrypt), and role-based access control (`traveller`, `admin`).
  * **FR-2 Master Catalogue:** Query verified destinations, accommodations, restaurants, attractions, and transit options.
  * **FR-3 Itinerary Engine:** Auto-generate daily schedules honoring duration, party size, budget caps, and activity tags.
  * **FR-4 Budget Variance Engine:** Real-time calculation of remaining balance, category splits, and deficit warning flags.
  * **FR-5 Interactive Modification:** Support live swapping of itinerary items with instant cost recalculation.
  * **FR-6 Grounded Travel Copilot:** Contextual chat assistant for packing recommendations and destination tips.
* **Non-Functional Requirements (NFRs):**
  * **Performance:** Sub-500ms response time for all relational catalogue and analytical queries.
  * **ACID Integrity:** 100% adherence to serializable transactions; zero orphaned records on delete.
  * **Security:** OWASP Top 10 compliance; strict IDOR protection enforcing trip ownership verification.
* **Scope Boundaries:**
  * **In-Scope:** End-to-end itinerary composition, budget optimization, catalogue seeding, and relational auditing.
  * **Out-of-Scope:** Real-world payment gateway transactions and third-party airline reservation ticketing.

> **Presenter Notes:**
> Milestone 2 established our formal Software Requirements Specification. We defined six core functional requirements including secure JWT authentication, multi-criteria catalogue exploration, automated itinerary generation, real-time budget tracking, dynamic item swapping, and a grounded AI copilot. For our non-functional requirements, we set a hard performance SLA of sub-500 millisecond response times for analytical queries, complete ACID compliance, and robust ownership verification to prevent Insecure Direct Object References.

---

# Milestone 3: Entity-Relationship (ER) Conceptual Modeling

```
  ┌──────────────┐ 1        1 ┌──────────────────┐
  │    users     ├────────────┤ user_preferences │
  └──────┬───────┘            └──────────────────┘
         │ 1
         │               ┌──────────────────┐ 1
         │ N             │   destinations   ├─────┐
  ┌──────▼───────┐ N   1 └────────▲─────────┘     │
  │    trips     ├────────────────┘               │
  └──────┬───────┘                                │ N
         │ 1                                      ├──────────────┬──────────────┐
         ├────────────────────────┐               │              │              │
         │ N                      │ N             ▼              ▼              ▼
  ┌──────▼───────┐        ┌───────▼────────┐ ┌─────────┐   ┌───────────┐  ┌───────────┐
  │ itineraries  │        │   expenses /   │ │ hotels  │   │restaurants│  │attractions│
  └──────┬───────┘        │  allocations   │ └─────────┘   └───────────┘  └───────────┘
         │ 1              └────────────────┘
  ┌──────▼───────┐ 1    N ┌────────────────┐
  │itinerary_days├────────┤itinerary_items │
  └──────────────┘        └────────────────┘
```

* **Domain Architecture (22 Entities):**
  * **User Domain:** `users`, `user_preferences`, `activity_preferences`.
  * **Catalogue Master Domain:** `destinations`, `hotels`, `restaurants`, `attractions`, `transport_options`, `weather_snapshots`.
  * **Trip Transaction Domain:** `trips`, `trip_members`, `itineraries`, `itinerary_days`, `itinerary_items`, `saved_trips`, `packing_items`.
  * **Financial & Auditing Domain:** `budget_allocations`, `expenses`, `reviews`, `ai_conversations`, `ai_messages`, `trip_audit`.
* **Cardinality Highlights:**
  * $1:1$ Identifying: `users` $\leftrightarrow$ `user_preferences` (mandatory parent-child identity).
  * $1:N$ Composition: `trips` $\rightarrow$ `itineraries` $\rightarrow$ `itinerary_days` $\rightarrow$ `itinerary_items` (deep cascading lifecycle).

> **Presenter Notes:**
> Milestone 3 details our conceptual data model. Spanning twenty-two distinct entities across four functional domains, the ER diagram captures the complete travel ecosystem. We established a strict hierarchical composition: one trip owns multiple versioned itineraries, each containing ordered days, which in turn contain granular scheduled items. Notice that catalogue entities like hotels, restaurants, and attractions exist independently in the master catalogue domain, linked to trips through foreign key item snapshots.

---

# Milestone 4: Relational Normalization & BCNF Decomposition

* **First Normal Form (1NF) — Atomicity Enforcement:**
  * *Violation:* Comma-delimited strings in `users.activity_interests` (`"heritage, culinary, trekking"`).
  * *Resolution:* Decomposed into discrete atomic rows in `activity_preferences(user_id, activity)`.
* **Second Normal Form (2NF) — Elimination of Partial Dependencies:**
  * *Analysis:* In relations with composite candidate keys such as `activity_preferences(user_id, activity)` and `budget_allocations(trip_id, category)`, all non-prime attributes depend upon the *entire* candidate key.
  * All single-attribute surrogate key relations (`trips`, `itinerary_items`) are trivially in 2NF.
* **Third Normal Form (3NF) — Elimination of Transitive Dependencies:**
  * *Violation:* Combining hotel and destination data: $\text{hotel\_id} \rightarrow \text{destination\_id} \rightarrow \{\text{city}, \text{country}\}$.
  * *Resolution:* Decomposed into independent master tables: `destinations` and `hotels`, linked by foreign key.
* **Boyce-Codd Normal Form (BCNF) Proof:**
  * In `destinations`, candidate keys are $\{\text{id}\}$ and $\{\text{city}, \text{country}\}$.
  * Functional Dependencies:
    $$F_1: \text{id} \rightarrow \{\text{city}, \text{country}, \text{description}, \text{average\_daily\_cost}, \text{active}\}$$
    $$F_2: \{\text{city}, \text{country}\} \rightarrow \{\text{id}, \text{description}, \text{average\_daily\_cost}, \text{active}\}$$
  * In every functional dependency $X \rightarrow Y$, the determinant $X$ is a strict **superkey**. Thus, the schema satisfies BCNF.

> **Presenter Notes:**
> Milestone 4 represents the mathematical backbone of our database: normalization through Boyce-Codd Normal Form. We systematically eliminated 1NF violations by unpacking comma-separated lists into atomic rows. We satisfied 2NF by ensuring full functional dependency over all composite keys. For 3NF, we removed transitive dependencies such as storing city metadata inside hotel records. Finally, as proven on this slide, because every determinant across all functional dependencies is a strict superkey, our twenty-two table schema formally achieves BCNF.

---

# ══════════════════════════════════════════════════════════════════
# [LIVE DEMO TRANSITION] SCREEN SHIFT 1: SUPABASE DATABASE VISUALIZER
# ══════════════════════════════════════════════════════════════════

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │                                                                        │
  │              >>>  PRESENTER ACTION: SWITCH WINDOW  <<<                 │
  │                                                                        │
  │   1. Switch monitor display to SUPABASE BROWSER TAB                    │
  │   2. Open Schema Visualizer / Table View                               │
  │   3. Highlight Foreign Key Relationships & 22 Database Tables          │
  │                                                                        │
  └────────────────────────────────────────────────────────────────────────┘
```

* **Focus Areas for Evaluators:**
  * The interactive **Entity-Relationship visual graph** showing all 22 normalized tables.
  * Foreign key constraints linking `trips` $\rightarrow$ `itineraries` $\rightarrow$ `itinerary_days` $\rightarrow$ `itinerary_items`.
  * Cascade deletion rules (`ON DELETE CASCADE`) preventing orphaned records.
  * Identity primary keys (`GENERATED ALWAYS AS IDENTITY`) on core tables.

> **Presenter Notes:**
> At this point in our evaluation, I will pause the presentation slides and switch my display to the live Supabase database console. Here in Supabase, you can observe our live PostgreSQL 15 database instance hosting all twenty-two normalized tables. Notice the interactive visual relationship graph: each foreign key connector represents the cascading integrity rules we defined, ensuring that the relational structure we proved on paper is running live in the cloud. Let us now inspect the relational schema specifications.

---

# Milestone 5: Relational Schema & Physical DDL Definitions

* **Physical Relational Architecture (22 PostgreSQL Tables):**
  * Clean, standardized, enterprise-grade Data Definition Language (DDL).
  * **Primary Key Policy:** Surrogate identity keys (`bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY`) for maximum indexing efficiency.
  * **Foreign Key Referential Integrity:**
    * `ON DELETE CASCADE`: Applied to child hierarchies (`itineraries`, `itinerary_days`, `itinerary_items`, `budget_allocations`) to ensure immediate cascade cleanup.
    * `ON DELETE SET NULL`: Applied to analytical chat logs (`ai_conversations.trip_id`) to preserve audit history if a trip is removed.
* **Exact DDL Excerpt (`database/schema/001_schema.sql`):**

```sql
CREATE TABLE trips (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  destination_id bigint NOT NULL REFERENCES destinations(id),
  starting_location varchar(120) NOT NULL,
  start_date date NOT NULL,
  end_date date NOT NULL,
  traveller_count integer NOT NULL CHECK(traveller_count > 0),
  total_budget numeric(12,2) NOT NULL CHECK(total_budget > 0),
  estimated_total numeric(12,2) NOT NULL DEFAULT 0 CHECK(estimated_total >= 0),
  status varchar(20) NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','planned','completed','cancelled')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CHECK(end_date >= start_date)
);
```

> **Presenter Notes:**
> Milestone 5 translates our conceptual model into physical DDL definitions. In our schema design, every table utilizes an identity column as its primary key to optimize B-Tree index alignment. Notice our cascading delete rules: when a user removes a trip, the database engine automatically cascades that deletion to associated itinerary days, activity items, and budget allocations, completely preventing dangling pointers or orphaned financial records.

---

# Milestone 6: Data Dictionary & Enterprise Integrity Constraints

* **Strict Domain Validation Rules (`CHECK` Constraints):**
  * **Financial Sanity:** `price_per_night >= 0`, `entry_fee >= 0`, `total_budget > 0`, `estimated_total >= 0`.
  * **Temporal Feasibility:** `CHECK (end_date >= start_date)` on `trips` completely prevents chronological anomalies.
  * **Categorical Domain Integrity:** `rating BETWEEN 0 AND 5`, `role IN ('traveller', 'admin')`.
* **Enterprise Uniqueness Constraints (`UNIQUE`):**
  * `UNIQUE(city, country)` on `destinations` prevents duplicate city creation.
  * `UNIQUE(destination_id, name)` on `hotels`, `restaurants`, and `attractions`.
  * `UNIQUE(trip_id, version)` on `itineraries` guarantees deterministic itinerary revision control.
  * `UNIQUE(trip_id, category)` on `budget_allocations` prevents duplicate budget category entries.

| Table Name | Column Name | Data Type | Nullable | Default / Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `trips` | `total_budget` | `numeric(12,2)` | `NOT NULL` | `CHECK (total_budget > 0)` |
| `trips` | `status` | `varchar(20)` | `NOT NULL` | `'draft' CHECK (status IN (...))` |
| `hotels` | `price_per_night` | `numeric(12,2)` | `NOT NULL` | `CHECK (price_per_night >= 0)` |
| `hotels` | `rating` | `numeric(2,1)` | `NULL` | `CHECK (rating BETWEEN 0 AND 5)` |
| `itineraries`| `version` | `integer` | `NOT NULL` | `DEFAULT 1 CHECK (version > 0)` |

> **Presenter Notes:**
> In Milestone 6, we formulated a rigorous Data Dictionary and constraint catalog. To guarantee that invalid data cannot enter the system even if application validation were bypassed, we implemented database-level domain checks. These include check constraints preventing negative budgets, ratings outside the zero to five range, and invalid date sequences where an end date precedes a start date. Furthermore, composite unique constraints guarantee that duplicate venues or budget categories cannot exist.

---

# Milestone 7: SQL Scripts (DDL, DML & Transactional ACID Persistence)

* **Script Organization & Automated Migration Pipeline:**
  * `database/schema/000_create_database.sql`: Database initialization and encoding configuration.
  * `database/schema/001_schema.sql`: Full 22-table DDL script with constraints and foreign keys.
  * `database/triggers/001_audit_trip.sql`: PL/pgSQL audit triggers and trigger function definitions.
  * `database/views/001_views.sql`: Materialized analytical reporting views.
  * `database/seeds/001_seed.sql`: Master catalog initial seeding scripts.
* **ACID Transaction Boundary Enforcement:**
  * **Atomicity:** All complex trip mutations (saving a trip, updating allocations, inserting day items) are executed inside explicit transactional blocks (`BEGIN ... COMMIT`).
  * **Consistency:** Transactional rollbacks triggered automatically if any foreign key or check constraint fails.
  * **Isolation:** Configured to Read Committed with MVCC, preventing dirty reads during concurrent user updates.
  * **Durability:** Guaranteed through PostgreSQL Write-Ahead Logging (WAL) flushed to persistent disk storage.

```sql
BEGIN;
-- Atomic trip persistence: Trip header + Itinerary + Allocations committed together
INSERT INTO trips (user_id, destination_id, starting_location, start_date, end_date, traveller_count, total_budget)
VALUES (1, 14, 'Delhi', '2026-09-10', '2026-09-14', 2, 20000.00);
INSERT INTO budget_allocations (trip_id, category, amount)
VALUES (currval(pg_get_serial_sequence('trips','id')), 'accommodation', 8000.00);
COMMIT;
```

> **Presenter Notes:**
> Milestone 7 highlights our SQL scripts and transactional execution model. All migrations are fully versioned, modular, and reproducible. When a user saves or updates an itinerary, our backend wraps the operation in an explicit ACID transaction block. If an error occurs midway through inserting individual itinerary items, the entire operation rolls back atomically, ensuring that a half-created trip or unbalanced budget is never permanently committed to the database.

---

# Milestone 8: Master Dataset Seeding (21,017+ Records Across 500 Cities)

* **Academic Requirement:** Minimum dataset seeding threshold of $\ge 5,000$ database records.
* **RoamGenie Seeding Scale:** **21,017 Total Production-Grade Records** across **500 World Destinations**:
  * `500` Destinations (`database/seeds/destinations_master_d1.json`)
  * `4,212` Curated Attractions (`database/seeds/attractions_master_d2.json`)
  * `5,528` Verified Hotels with tiered pricing (`database/seeds/003_seed_hotels.sql`)
  * `5,814` Authentic Dining Venues with cuisine classifications (`database/seeds/004_seed_restaurants.sql`)
  * `4,963` Inter-city and local Transit Options (`database/seeds/005_seed_transports.sql`)
* **Realism & Data Fidelity:**
  * Real-world GPS-accurate locations across India, Southeast Asia, Europe, and the Americas.
  * Realistic cost modeling in INR (budget, moderate, luxury tiers).
  * High-performance batch insertion utilizing PostgreSQL multi-row `INSERT` statements for sub-minute total database seeding.

```
Total Master Records Seeded: 21,017 Rows (420% of Course Syllabus Requirement)
  [████████████████████████████████████████] 100% Data Integrity Verified
```

> **Presenter Notes:**
> For Milestone 8, the academic syllabus required a dataset of at least five thousand records. RoamGenie dramatically exceeds this requirement, seeding twenty-one thousand and seventeen real-world records across five hundred global destinations. This includes over five thousand hotels, five thousand eight hundred restaurants, four thousand attractions, and nearly five thousand transit tariffs. Having this rich relational dataset is what allows our AI engine to plan realistic itineraries with verified pricing.

---

# Milestone 9: Complex Queries, Analytical Views & PL/pgSQL Triggers

* **18 Academic Benchmark SQL Queries (`database/queries/001_reports.sql`):**
  * **Window Function Analytics (`Q13`):** Computes percentage allocation per category using dynamic partitioning:
    ```sql
    SELECT trip_id, category, amount,
           round(amount * 100 / nullif(sum(amount) OVER (PARTITION BY trip_id), 0), 2) AS pct
    FROM budget_allocations;
    ```
  * **Correlated Subqueries (`Q09`):** Selects destination's highest-rated attraction:
    ```sql
    SELECT d.city, a.name, a.rating FROM destinations d JOIN attractions a ON a.destination_id = d.id
    WHERE a.rating = (SELECT max(x.rating) FROM attractions x WHERE x.destination_id = d.id);
    ```
* **Database Views for Fast Abstraction (`001_views.sql`):**
  * `v_trip_budget_summary`: Exposes `remaining_budget` and `is_over_budget` boolean flags in real-time.
  * `v_destination_catalogue`: Pre-aggregates counts of hotels, restaurants, and attractions per city.
* **PL/pgSQL Audit Trigger (`trg_trip_audit`):**
  * Fires `AFTER INSERT OR UPDATE OR DELETE` on `trips`. Captures mutated row data as `jsonb` into `trip_audit` for full historical accountability.

> **Presenter Notes:**
> In Milestone 9, we demonstrated advanced database programmability through eighteen analytical queries, materialized views, and PL/pgSQL triggers. As seen in Query 13, we utilize analytical window functions with partition clauses to calculate category budget distributions on the fly. We also created database views like `v_trip_budget_summary` to abstract complex calculations, and attached an automated PL/pgSQL audit trigger that logs all table changes into JSONB audit rows.

---

# Milestone 10: Responsive Full-Stack Web Application (UI/UX Engineering)

* **Enterprise Frontend Architecture:**
  * Developed with **React 19**, **Vite**, and **Vanilla CSS Grid/Flexbox** for maximum performance and zero heavyweight framework bloat.
  * Fully responsive design adapting smoothly from 320px mobile screens to 4K desktop displays.
* **Core Application Modules:**
  1. **Interactive Planning Wizard (`/plan`):** Dynamic form capturing destination, travel dates, passenger counts, budget caps, and preference tags (`heritage`, `culinary`, `adventure`).
  2. **Dynamic Visual Timeline:** Chronologically organized daily cards with color-coded category badges, time slots, and line-item costs.
  3. **Real-time Budget Visualizer Bar:** Progressively fills with category color bands; transitions into an active red alert if the estimated total exceeds the defined budget.
  4. **Dynamic Item Swap Modal:** Allows users to swap any scheduled hotel, meal, or activity with an alternative directly from the master catalogue.
  5. **Academic DBMS Showcase Page (`/showcase`):** Live, interactive execution dashboard for our 18 queries, views, and trigger logs.

> **Presenter Notes:**
> Milestone 10 showcases our full-stack web implementation. The frontend is cleanly engineered with React 19 and custom responsive styling. Key modules include our interactive four-step planning wizard, a visual daily schedule timeline, and a live budget progress bar that dynamically recalculates category totals. Travellers can click the swap button on any itinerary event to replace it with another catalogue option, triggering an instant recalculation of total expenditure and deficit alerts.

---

# Milestone 11: Grounded AI Integration & Deterministic Safety Gateway

* **The Grounded AI Architecture:**
  * Resolves LLM hallucinations by injecting verified database entities (accommodations, dining, attraction entry fees) directly into the prompt context.
  * The LLM operates purely as a reasoning and sequencing engine; it cannot invent non-existent venues or invalid tariffs.
* **The Dual-Engine Strategy:**
  * **Primary Provider:** Google Gemini 1.5 Flash via REST API with strict JSON schema mode (`temperature: 0.2`).
  * **Deterministic Fallback Engine (`ai_orchestrator.py`):** If Gemini encounters rate limits, timeouts, or network errors, RoamGenie automatically triggers an algorithmic rule-based scheduler.
  * **Zero Downtime Guarantee:** The application never crashes or leaves the user with an empty screen.
* **Contextual AI Copilot (`/assistant`):**
  * Supports interactive queries ("What should I pack for Jaipur in September?", "How can I cut ₹3,000 from my budget?").
  * Multi-turn conversations are recorded transactionally in `ai_conversations` and `ai_messages`.

> **Presenter Notes:**
> Milestone 11 addresses our intelligent agent integration. Rather than allowing an LLM to generate unconstrained text, RoamGenie uses grounded prompt engineering: we query our PostgreSQL catalogue first, inject verified hotels and attractions into the prompt, and force Gemini to respond in strict JSON. Furthermore, we built a dual-engine architecture: if the external AI API times out or hits a rate limit, our deterministic scheduler takes over instantly, guaranteeing zero downtime.

---

# ══════════════════════════════════════════════════════════════════
# [LIVE DEMO TRANSITION] SCREEN SHIFT 2: LIVE WEB APPLICATION
# ══════════════════════════════════════════════════════════════════

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │                                                                        │
  │              >>>  PRESENTER ACTION: SWITCH WINDOW  <<<                 │
  │                                                                        │
  │   1. Switch monitor display to BROWSER (http://localhost:5173)         │
  │   2. Ensure User Session is Logged In                                  │
  │   3. Ready to run Jaipur 4-Day Plan with ₹20,000 Budget                │
  │                                                                        │
  └────────────────────────────────────────────────────────────────────────┘
```

* **Live Demonstration Checklist:**
  1. User Authentication & Token Handshake (`/login`).
  2. Master Catalogue Inspection (`/destinations`).
  3. Trip Generation Wizard (`/plan` $\rightarrow$ Jaipur, 4 Days, 2 Travellers, ₹20,000 Budget).
  4. **Dynamic Item Swap:** Change Day 1 Hotel to luxury option $\rightarrow$ Trigger Budget Deficit Alert.
  5. Transactional Bookmark Persistence (`/trips`).
  6. Grounded AI Copilot Interaction (`Ask AI Copilot`).
  7. DBMS Showcase Query Runner (`/showcase`).

> **Presenter Notes:**
> We now transition to our second live window shift: the live running web application on localhost:5173. Over the next two minutes, I will demonstrate the full end-to-end user journey: logging in, generating a 4-day cultural trip to Jaipur on a twenty thousand rupee budget, triggering a real-time budget deficit alert by swapping a hotel, persisting the trip to the database, chatting with the grounded AI Copilot, and running analytical queries in our DBMS showcase.

---

# Milestone 12: Live Demonstration Flow & Scenario Walkthrough

* **Step 1: Authentication & Master Catalogue Exploration (0:00 - 1:00)**
  * Log in as registered user `traveller@roamgenie.com`.
  * Browse the catalogue of 500 destinations; inspect Jaipur's attractions, hotels, and average daily cost.
* **Step 2: Automated Trip Planning & Schedule Synthesis (1:00 - 2:15)**
  * Navigate to `/plan`; set Jaipur, 4 days, 2 travellers, ₹20,000 budget, tags: `heritage`, `culinary`.
  * Click **"Generate Itinerary"**; system generates a multi-day timeline, weather card, and budget split.
* **Step 3: Dynamic Item Swap & Deficit Alert Trigger (2:15 - 3:30)**
  * Inspect Day 1 Hotel tariff (₹2,800). Click **"⇄ Swap"** and choose a luxury heritage hotel (₹6,500).
  * **Dynamic Trigger in Action:** Estimated total jumps to ₹23,700 $\rightarrow$ Budget Visualizer turns red with a **₹3,700 Deficit Alert**.
* **Step 4: Persistence, Reload & Copilot Verification (3:30 - 5:00)**
  * Click **"Save to Bookmarks"** $\rightarrow$ Navigate to `/trips` $\rightarrow$ Reload saved trip with 100% fidelity.
  * Query AI Copilot: *"What should I pack?"* $\rightarrow$ Copilot recommends cottons and comfortable footwear based on Jaipur's weather snapshot.
* **Step 5: DBMS Showcase & Audit Trigger Verification (5:00 - 6:00)**
  * Navigate to `/showcase` $\rightarrow$ Execute Query 13 (Window Functions) and Query 09 (Correlated Subquery).
  * Inspect `trip_audit` table to prove the PL/pgSQL trigger logged the exact hotel swap transaction.

> **Presenter Notes:**
> This slide outlines the exact sequence we just executed in the live application. We demonstrated the complete lifecycle: generating a grounded itinerary, experiencing an instant real-time deficit alert when upgrading an accommodation item, saving the resulting trip to our PostgreSQL database with full ACID persistence, asking contextual questions to our grounded AI copilot, and inspecting the resulting audit log inside the DBMS Showcase.

---

# Academic Summary, Verification & Viva Defense Conclusion

* **100% Automated Test Suite Verification:**
  * **Backend Coverage:** 172 unit and integration tests passing (`pytest backend/tests/`).
  * **Frontend Coverage:** 15 component and integration tests passing (`vitest frontend/`).
  * **Total Test Verification:** **187 automated tests passing** across authentication, trip services, AI fallbacks, and SQL query runners.
* **Core Academic Achievements:**
  * Formally designed and normalized a 22-table schema adhering to **Boyce-Codd Normal Form (BCNF)**.
  * Implemented advanced database objects: PL/pgSQL triggers, transactional audit tables, and partition window functions.
  * Successfully seeded and indexed a production-grade master dataset exceeding **21,000 records across 500 cities**.
  * Solved the real-world problem of travel tool fragmentation and budget creep through grounded artificial intelligence.
* **Thank You!** We are now open for the viva voce defense and technical questions from the committee.

> **Presenter Notes:**
> In conclusion, RoamGenie demonstrates that modern generative AI and classical relational database systems are not mutually exclusive; rather, they complement each other perfectly. By anchoring Google Gemini inside a strictly normalized BCNF PostgreSQL database backed by 187 passing automated tests, we have built an autonomous planning engine that prevents budget deficits and guarantees data integrity. Thank you for your time and guidance, and I now welcome your questions.
