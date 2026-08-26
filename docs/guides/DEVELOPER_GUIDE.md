# RoamGenie — Developer & Admin Reference Guide

This guide contains all essential developer reference details, administrative credentials, environment configurations, architecture conventions, database management commands, and development workflows for the RoamGenie platform.

---

## 1. 🔑 Pre-Seeded Developer & Admin Credentials

The database contains pre-configured developer, administrator, and demo traveller accounts:

| Role | Name | Email Address | Password | Permissions & Access Scope |
| :--- | :--- | :--- | :--- | :--- |
| **System Admin** | System Administrator | `admin@roamgenie.internal` | `AdminPass123!` | Full administrative access: execute custom SQL in DBMS Showcase, override trip IDOR guards, manage catalogue entries, view all audit logs. |
| **Demo Traveller 1** | Arun Kumar | `traveller@roamgenie.internal` | `TravellerPass123!` | Standard traveller account: create itineraries, save trips, toggle packing items, chat with AI Copilot. |
| **Demo Traveller 2** | Ananya Sharma | `ananya@roamgenie.internal` | `TravellerPass123!` | Standard traveller account: multi-user isolation and collaboration testing. |

> **Note on Authentication:** Passwords are encrypted in PostgreSQL using `bcrypt` / `argon2id` hash algorithms. JWT bearer tokens are issued upon login with HMAC-SHA256 signature.

---

## 2. 🌐 Service Endpoints & Local Ports

| Service / Tool | Local URL | Description |
| :--- | :--- | :--- |
| **Frontend Web App (Vite)** | `http://localhost:5173` | React 19 SPA client application. |
| **Backend REST API (FastAPI)**| `http://127.0.0.1:8000` | Asynchronous backend application server. |
| **Interactive API Docs (Swagger)**| `http://127.0.0.1:8000/docs` | OpenAPI 3.0 interactive API explorer and testing sandbox. |
| **Alternative API Docs (ReDoc)** | `http://127.0.0.1:8000/redoc` | Formatted technical endpoint reference. |
| **Database (Supabase PostgreSQL)**| Cloud / Local Connection Pool | PostgreSQL 15+ holding 23 normalized tables and 21,133 rows. |

---

## 3. ⚙️ Environment Variables Reference (`backend/.env`)

Below is the complete configuration manifest required in `backend/.env`:

```ini
# =============================================================================
# 1. DATABASE CONFIGURATION (PostgreSQL / Supabase)
# =============================================================================
DATABASE_URL=postgresql+psycopg://postgres:[YOUR_PASSWORD]@[YOUR_HOST]:5432/postgres

# =============================================================================
# 2. SECURITY & JWT AUTHENTICATION
# =============================================================================
SECRET_KEY=roamgenie-dev-secret-key-change-in-production-2026
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# =============================================================================
# 3. AI & LLM PROVIDERS (Optional - Deterministic Heuristic Engine Fallback)
# =============================================================================
GEMINI_API_KEY=your_google_gemini_api_key_here
GROQ_API_KEY=your_groq_cloud_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
AI_PROVIDER=gemini
AI_MODEL=gemini-1.5-flash

# =============================================================================
# 4. GOOGLE MAPS & STREET VIEW APIS (Optional)
# =============================================================================
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# =============================================================================
# 5. WEATHER INTEGRATION
# =============================================================================
WEATHER_API_URL=https://api.open-meteo.com/v1/forecast
```

### Frontend Environment Variables (`frontend/.env`):
```ini
VITE_API_URL=http://127.0.0.1:8000
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

---

## 4. 🛠️ Common Developer CLI Commands

### 4.1 Running Servers
```bash
# Start FastAPI Backend (with Hot-Reload)
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Start React Frontend (with Vite HMR)
cd frontend
npm run dev
```

### 4.2 Running Automated Test Suites
```bash
# Run Backend Pytest Suite (147 tests)
cd backend
pytest backend/tests/ -v

# Run Frontend Vitest Suite (15 tests)
cd frontend
npm test -- --run

# Run Production Frontend Build Gate
cd frontend
npm run build
```

### 4.3 Database Maintenance & Seeding Scripts
```bash
# Verify Live Database State, Row Counts & Foreign Key Integrity
python scripts/audit_database_state.py

# Seed All Master Datasets (D1 to D5)
python scripts/database/seed_destinations_d1.py
python scripts/database/seed_attractions_d2.py
python scripts/database/seed_hotels_d3.py
python scripts/database/seed_restaurants_d4.py
python scripts/database/seed_transport_d5.py

# Re-generate Destination Landmark Image Mapping
python scripts/generate_destination_images.py
```

---

## 5. 🧱 Core Architectural Conventions for Developers

### 5.1 IDOR & Authorization Rules
Whenever creating or modifying an endpoint that operates on user-scoped resources (`trips`, `itineraries`, `packing_items`, `ai_conversations`):
```python
from fastapi import Depends, HTTPException, status
from app.services.auth_service import get_current_user
from app.db.models.user import User

@router.get("/trips/{trip_id}")
def get_trip_details(
    trip_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    # IDOR Check: Ensure owner or admin
    if trip.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden to this trip")
        
    return trip
```

### 5.2 Transactional Atomicity Pattern
When saving itineraries or mutating multi-table schedules, always wrap dependent entity operations in a single atomic commit:
```python
try:
    db.add(trip)
    db.flush() # Generates trip.id for foreign keys
    
    itinerary = Itinerary(trip_id=trip.id, ...)
    db.add(itinerary)
    db.flush()
    
    for day in days_data:
        # add itinerary_days and itinerary_items
        ...
    db.commit() # Atomic ACID commit
except Exception as e:
    db.rollback()
    raise HTTPException(status_code=500, detail=str(e))
```

### 5.3 AI Multi-Provider & Offline Fallback Rule
Never make the application hard-dependent on an external AI API key. All generative features must gracefully delegate to the offline deterministic heuristic engine in [`backend/app/services/scheduler.py`](file:///D:/yasmin%20programs/SEM%205/DBMS%20Theory/Travel%20Planner/RoamGenie/backend/app/services/scheduler.py) if API keys are absent or network requests time out.
