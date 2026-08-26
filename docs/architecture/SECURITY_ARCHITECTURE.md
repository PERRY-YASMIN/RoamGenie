# RoamGenie — Security Architecture & Controls

## 1. Authentication & Session Management
- **Stateless Bearer Tokens:** Authentication is mediated via JSON Web Tokens (JWT) signed with HMAC-SHA256.
- **Password Security:** User passwords are never stored in plaintext. They are salted and hashed using `bcrypt` (12 rounds).
- **Token Expiration:** JWT access tokens are issued with a strict expiration delta (`ACCESS_TOKEN_EXPIRE_MINUTES`).

---

## 2. Insecure Direct Object Reference (IDOR) Protections
To prevent unauthorized data access or tampering between distinct accounts, all transactional API endpoints enforce strict ownership checks:
- **Trip Inspection & Mutation (`/api/v1/trips/{trip_id}`):** Validates that `trip.user_id == current_user.id` unless the user possesses the `admin` role. Returns `HTTP 403 Forbidden` or `HTTP 404 Not Found` upon mismatch.
- **AI Conversation Isolation (`/api/v1/assistant/chat`):** Checks conversation ownership prior to loading history or appending turns.
- **Packing Item Mutability (`/api/v1/assistant/packing/{item_id}`):** Confirms that the target packing item belongs to a trip owned by the authenticated caller.

---

## 3. Database & Query Injection Defense
- **Parameterized Queries:** All application routes interact with the PostgreSQL database through SQLAlchemy 2.0 ORM and typed Pydantic models, eliminating SQL injection vulnerabilities.
- **Showcase Query Isolation:** The DBMS Showcase router executes pre-defined, read-only analytical queries with parameter bindings rather than unvalidated raw input strings.

---

## 4. Input Validation & Defense-in-Depth
- **Pydantic Validation:** All incoming payloads are strictly validated for type correctness, non-negative monetary amounts, valid date ranges (`start_date <= end_date`), and length bounds.
- **CORS Policy:** Strict Cross-Origin Resource Sharing (CORS) rules configured in `backend/app/config.py` restricting allowed origins to verified development and production hosts.
