# Deployment & Operations Guide

**Project:** RoamGenie — AI Travel Planner & Budget Optimizer  
**Course:** Database Management Systems (Semester 5 Theory & Project)  
**Environment:** Windows (PowerShell) · Python 3.12 · Node 22 / React 18 · PostgreSQL 15+ (Supabase)  
**Status:** Authoritative Operations Guide

---

## 1. Environment Setup & Prerequisites

Ensure the following runtimes are available:
* **Python:** 3.12+ (`python --version`)
* **Node.js & npm:** Node 20+ / npm 10+ (`node -v`, `npm -v`)
* **PostgreSQL:** Direct Supabase instance or local PostgreSQL 15+ installation

---

## 2. Backend Setup & Startup (Terminal 1)

```powershell
# 1. Navigate to backend directory
cd backend

# 2. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
# Copy .env.example to .env and set your DATABASE_URL
Copy-Item .env.example .env

# 5. Apply Alembic database migrations
python -m alembic upgrade head

# 6. (Optional) Run development seed data
python ..\scripts\database\seed_dev.py

# 7. Start FastAPI server on port 8000
uvicorn app.main:app --reload --port 8000
```

* **Interactive API Documentation (Swagger):** `http://127.0.0.1:8000/docs`
* **Health Check:** `http://127.0.0.1:8000/api/health`

---

## 3. Frontend Setup & Startup (Terminal 2)

```powershell
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start Vite development server on port 5173
npm run dev
```

* **Web Application:** `http://localhost:5173`

---

## 4. Automated Testing & Verification

```powershell
# Run the unified test runner
powershell -ExecutionPolicy Bypass -File scripts\test\all.ps1

# Or run suites individually:
# Backend pytest suite (172 tests)
& .\backend\.venv\Scripts\python.exe -m pytest -v

# Frontend Vitest suite (15 tests)
cd frontend
npm test -- --run

# Frontend production build
npm run build
```

---

## 5. Environment Variables Reference (`.env`)

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+psycopg://user:pass@host:5432/dbname` | Primary Supabase PostgreSQL connection string |
| `LOCAL_DATABASE_URL` | `sqlite:///./roamgenie.db` | Local development fallback connection string |
| `DATABASE_ENV` | `supabase` (`supabase` or `local`) | Active database target selector |
| `SECRET_KEY` | (Secure random string) | Secret key for signing JWT tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT token validity duration |
| `AI_PROVIDER` | `mock` (`mock`, `gemini`, `openai`, `groq`) | Active LLM adapter |
| `GEMINI_API_KEY` | None | Google Gemini API Key |
| `OPENAI_API_KEY` | None | OpenAI API Key |
| `GROQ_API_KEY` | None | Groq API Key |
| `WEATHER_PROVIDER` | `open-meteo` (`open-meteo`, `mock`) | Weather data provider |
