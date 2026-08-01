# Role Scope

## Own

`frontend/`, `tests/frontend/`, frontend screenshots.

## Coordinate

- Inputs: approved API contract from Yasmin, field names from Samyuktha, AI response schema from Madhu.
- Outputs: 14 routed screens, reusable components, validation, API integration, responsive evidence.
- Must not change: database schema, backend routes, SQL and AI service code without owner approval.
- Escalate contract conflicts to Yasmin before coding past the conflict.

<!-- SUPABASE_UPDATE_START -->
## Supabase boundary

React calls FastAPI only. Do not add the Supabase JavaScript client or any database/service-role credential. Use contract-matched mock API data while endpoints are pending. Dashboard is not the app UI; its screenshots are presentation evidence only.
<!-- SUPABASE_UPDATE_END -->
