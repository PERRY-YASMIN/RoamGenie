# RoamGenie — Comprehensive Testing Strategy & Framework

## 1. Testing Philosophy & Quality Gate
RoamGenie enforces a multi-tiered automated testing strategy across both backend and frontend layers to ensure data integrity, API contract adherence, security boundary enforcement (IDOR & auth), and UI stability.

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Vitest Suite                    │
│ - Component Rendering & Navigation Tests (App.test.jsx)      │
│ - Global Context Provider Tests (ToastContext.test.jsx)     │
│ - API Service Layer & Mock Handling (api.test.js)           │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    Backend Pytest Suite                     │
│ - API Endpoint & Router Tests (FastAPI TestClient)          │
│ - Authentication, Password Hashing & JWT Verification       │
│ - IDOR & Ownership Protection Tests                         │
│ - AI Orchestrator, Provider & Heuristic Fallback Tests      │
│ - DBMS Showcase Analytical Query Accuracy (Q01–Q10)         │
│ - Dataset Constraint & Referential Integrity Validations    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Test Execution Commands

### Running Backend Pytest Suite:
```bash
cd backend
.\.venv\Scripts\python.exe -m pytest backend/tests/ -v
```

### Running Frontend Vitest Suite:
```bash
cd frontend
npm test -- --run
```

### Running Frontend Production Build Gate:
```bash
cd frontend
npm run build
```
