# RoamGenie — System Architecture

## 1. High-Level Architectural Overview

RoamGenie is architected as a modern, decoupled client-server web application adhering to clean architectural boundaries:

```
┌─────────────────────────────────────────────────────────────┐
│                 React SPA Client (Vite)                     │
│  - React Router v7, Context API, Lucide Icons, Custom CSS   │
│  - Autocomplete Planner, Modal Inspector, Chat Copilot      │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / JSON REST API
┌──────────────────────────────▼──────────────────────────────┐
│                  FastAPI Backend Server                     │
│  - Python 3.12, Uvicorn, Pydantic v2 validation             │
│  - API Routers: auth, catalogues, trips, assistant, reports │
│  - Services: scheduler, budget_optimizer, weather, AI       │
└───────────────┬──────────────────────────────┬──────────────┘
                │ SQLAlchemy 2.0 ORM           │ HTTP Client
┌───────────────▼──────────────┐ ┌─────────────▼──────────────┐
│  PostgreSQL Database (Supabase)│ │   External Weather & LLM   │
│  - 23 Base Tables (3NF Schema) │ │ - Open-Meteo Weather API   │
│  - Foreign Keys, Cascade Del │ │ - Google Gemini / Groq API │
│  - 21,133 Production Rows    │ │ - Heuristic Fallback Engine│
└──────────────────────────────┘ └────────────────────────────┘
```

---

## 2. Component Layers

### 2.1 Presentation Layer (Frontend SPA)
- **Framework:** React 19 with Vite bundler.
- **Routing:** React Router v7 with browser history and authenticated route protection.
- **State Management:** React Context API (`AuthContext`, `ToastContext`) for unified global authentication and notification states.
- **Visual Design:** High-contrast, minimalist dark/light design system with zero text-shadows, responsive CSS grid layouts, and curated high-resolution landmark photography.

### 2.2 Application & Service Layer (FastAPI Backend)
- **API Framework:** FastAPI with asynchronous endpoint routing and automatic OpenAPI documentation.
- **Validation & Serialization:** Pydantic v2 BaseModel schemas with strict data coercion and constraints.
- **Core Domain Services:**
  - `AIPlanOrchestrator`: Coordinates prompt assembly, provider calls (Gemini/Groq/OpenAI), and deterministic heuristic fallback.
  - `Scheduler`: Implements greedy/heuristic entity assignment across morning, afternoon, and evening slots based on destination catalogue data.
  - `BudgetCalculator & BudgetOptimizer`: Calculates category-level distributions and enforces deficit warnings.
  - `WeatherService`: Fetches live Open-Meteo forecasts and persists snapshots for offline resilience.
  - `AuthService`: Generates bcrypt password hashes and HMAC-SHA256 JWT tokens.

### 2.3 Persistence Layer (PostgreSQL Database)
- **Database Engine:** PostgreSQL 15+ (hosted on Supabase).
- **ORM / Driver:** SQLAlchemy 2.0 with `psycopg3` binary driver.
- **Schema Design:** 23 base tables fully normalized to 3NF, enforcing referential integrity, check constraints, default timestamps, and cascading deletes.
- **Dataset Size:** 21,133 verified rows spanning 500 destinations, 6,000 hotels, 6,000 restaurants, 6,000 transit options, and 2,517 attractions.
