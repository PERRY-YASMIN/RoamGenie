# Role Scope

## Own

`ai/`, AI schemas/services/tests and AI contract docs.

## Coordinate

- Inputs: validated trip DTO plus selected database records and weather snapshot.
- Outputs: validated provider-independent JSON; deterministic no-key mock; malformed/timeout tests.
- Must not change: raw database credentials, direct database writes, unrelated backend/frontend code.
- Escalate contract conflicts to Yasmin before coding past the conflict.

<!-- SUPABASE_UPDATE_START -->
## Supabase boundary

AI calls backend services and receives validated structured records. It never receives Supabase credentials, executes arbitrary SQL, changes tables or invents trusted IDs. FastAPI validates referenced IDs and persists accepted output. Preserve mock mode.
<!-- SUPABASE_UPDATE_END -->
