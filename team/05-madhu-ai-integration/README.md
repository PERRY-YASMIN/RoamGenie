# MADHUVARSHINI A — AI Integration Engineer

## Responsibility

- Primary responsibility: provider abstraction, prompts, structured itinerary/recommendations/Q&A/packing, validation, timeouts, retry and mock fallback.
- Modules owned: provider abstraction, prompts, structured itinerary/recommendations/Q&A/packing, validation, timeouts, retry and mock fallback.
- Files owned: `ai/`, AI schemas/services/tests and AI contract docs.
- May modify: backend AI adapter/router with Yasmin review.
- Do not modify without approval: raw database credentials, direct database writes, unrelated backend/frontend code.
- Dependencies: validated trip DTO plus selected database records and weather snapshot.
- Expected deliverables: validated provider-independent JSON; deterministic no-key mock; malformed/timeout tests.
- Testing responsibility: Test valid JSON, invalid JSON, missing fields, timeout, missing key, empty preferences, invalid destination, unrealistic budget and unknown IDs.
- Integration responsibility: demonstrate the owned slice against `develop`, document contract mismatches, and support its reviewer.
- Branch: `ai/madhu`.
- Pull request: target `develop`; link issue; list tests, evidence, limitations; obtain one relevant review and Yasmin's integration approval.
- Complete when: Code/docs exist; required tests pass; no secrets; contracts match; evidence is attached; reviewed PR is merged to `develop`; `PROJECT_STATUS.md` and progress log are updated.

<!-- SUPABASE_UPDATE_START -->
## Supabase responsibility

AI calls backend services and receives validated structured records. It never receives Supabase credentials, executes arbitrary SQL, changes tables or invents trusted IDs. FastAPI validates referenced IDs and persists accepted output. Preserve mock mode.
<!-- SUPABASE_UPDATE_END -->
