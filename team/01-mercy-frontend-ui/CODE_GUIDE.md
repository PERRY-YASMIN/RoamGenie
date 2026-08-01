# Code Guide

Routes: `/`, `/register`, `/login`, `/profile`, `/plan`, `/destinations`, `/hotels`, `/restaurants`, `/attractions`, `/itineraries/:id`, `/budget/:tripId`, `/saved`, `/assistant`, and `*`. Keep API calls in `src/services/api.js`; never call PostgreSQL. Validate required locations, future dates, travellers > 0, and budget > 0.

- Prefer small named functions and consistent snake_case (Python/SQL) or camelCase (JavaScript).
- Validate at boundaries; log context without credentials or personal data.
- Keep configuration in environment variables documented in `.env.example`.
- Preserve working code. Stop and report overlapping or conflicting changes.