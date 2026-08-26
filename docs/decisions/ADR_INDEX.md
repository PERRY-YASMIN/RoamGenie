# Architectural Decision Records (ADR Index)

**Project:** RoamGenie — AI Travel Planner & Budget Optimizer  
**Course:** Database Management Systems (Semester 5 Theory & Project)  
**Status:** Authoritative Architectural Record

---

## Index of Architectural Decisions

* [ADR-001: Backend-Managed Argon2id & JWT Authentication](#adr-001-backend-managed-argon2id--jwt-authentication)
* [ADR-002: Dual Database Dialect Support with Auto-Normalizing URL Driver Prefix](#adr-002-dual-database-dialect-support-with-auto-normalizing-url-driver-prefix)
* [ADR-003: Bounded AI Gateway with Strict Pydantic Schema & Deterministic Fallback](#adr-003-bounded-ai-gateway-with-strict-pydantic-schema--deterministic-fallback)
* [ADR-004: Relational Master Data Seeding Strategy (500 Destinations & 21,000+ Items)](#adr-004-relational-master-data-seeding-strategy-500-destinations--21000-items)

---

### ADR-001: Backend-Managed Argon2id & JWT Authentication
* **Status:** Accepted & Implemented
* **Context:** Supabase provides client-side GoTrue authentication, but academic DBMS guidelines require evaluating backend authentication design, password salting/hashing, user authorization, and resource ownership enforcement.
* **Decision:** Implement password hashing directly in FastAPI using `Argon2id` (via `pwdlib`) and issue stateless HS256 JWT bearer tokens containing standard claims (`sub`, `email`, `role`, `exp`). Store credentials in the normalized `users` table.
* **Consequences:** Provides complete ownership isolation (`verify_trip_ownership`) and enables zero client-side database credential exposure.

---

### ADR-002: Dual Database Dialect Support with Auto-Normalizing URL Driver Prefix
* **Status:** Accepted & Implemented
* **Context:** In production, RoamGenie connects to PostgreSQL 15+ hosted on Supabase using the modern `psycopg` (v3) driver. However, local rapid unit testing benefits from in-memory SQLite instances.
* **Decision:** Use SQLAlchemy 2.0 with driver auto-normalization in `config.py` that translates legacy `postgres://` or standard `postgresql://` connection strings to `postgresql+psycopg://`. Connection pooling uses `pool_pre_ping=True`, `pool_size=10`, and `max_overflow=20`.
* **Consequences:** All 105 automated tests run rapidly in any environment without external network latency, while direct PostgreSQL verification tests run against live PostgreSQL instances.

---

### ADR-003: Bounded AI Gateway with Strict Pydantic Schema & Deterministic Fallback
* **Status:** Accepted & Implemented
* **Context:** Generative AI models can suffer from latency, rate limits, malformed JSON outputs, and hallucinations.
* **Decision:** Isolate all LLM adapters behind `AIPlanOrchestrator`. Inject only sanitized catalogue facts into prompts. Validate responses strictly against `AIItineraryOutput`. Allow a maximum of 2 retry attempts, and automatically fall back to the catalogue-grounded `DeterministicScheduler` on any failure.
* **Consequences:** 100% offline resilience and zero dependency on paid API keys for core travel planning.

---

### ADR-004: Relational Master Data Seeding Strategy (500 Destinations & 21,000+ Items)
* **Status:** Accepted & Implemented
* **Context:** The initial prototype had only 5 cities. An authentic global travel planner requires realistic geographic variety and diverse pricing tiers across continents.
* **Decision:** Curate a verified master dataset spanning 500 global destinations (93 countries) across India, Asia, Europe, Americas, Oceania, and Africa, populated with 2,517 attractions, 6,000 hotels, 6,000 restaurants, and 6,000 transport options. Retain original 5 seed destination IDs to preserve historical foreign key integrity.
* **Consequences:** Enables comprehensive itinerary generation and budget optimization across domestic and international journeys with authentic pricing.
