# Security Design

Threats: credential theft, broken access control, injection, XSS, secret leakage, prompt injection and excessive data exposure. Controls: bcrypt password hashes; expiring JWT; ownership/admin checks; Pydantic validation; ORM/parameterized SQL; frontend escaping; CORS allow-list; generic client errors and sanitized logs; least-privilege DB roles; `.env` exclusion; dependency review; rate limiting before deployment; AI allow-list context and schema validation. Rotate any exposed key immediately and remove it from history through the project manager.

<!-- SUPABASE_UPDATE_START -->
## Supabase credentials and RLS

Store connection strings and database passwords only in backend secrets. `SUPABASE_SERVICE_ROLE_KEY` is backend-only and should remain unused unless a reviewed feature requires it; it bypasses RLS and is never a `VITE_*` variable. Do not expose public tables. FastAPI JWT/ownership checks remain authoritative because React has no direct table access. If direct client access is approved later, enable RLS first and test that user A cannot read/update user B's trips or itineraries.

Optional policy template for a future architecture using Supabase Auth—not applied now: `CREATE POLICY own_trips ON trips FOR SELECT USING (user_id = auth.uid());`. The current bigint user key/FastAPI JWT design is not compatible with that example without an approved identity mapping.
<!-- SUPABASE_UPDATE_END -->
