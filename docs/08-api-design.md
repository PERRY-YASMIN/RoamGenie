# API Design v1 Draft

Base `/api/v1`; JSON uses snake_case; timestamps ISO-8601 UTC; money is decimal/string at boundaries. Error envelope: `{"error":{"code":"validation_error","message":"...","details":[]}}`.

| Resource | Core endpoints |
|---|---|
| auth | `POST /auth/register`, `/auth/login`; `GET /users/me` |
| catalogues | `GET /destinations`, `/hotels`, `/restaurants`, `/attractions`, `/transport-options` with page/filter |
| trips | `POST/GET /trips`, `GET/PATCH/DELETE /trips/{id}` |
| plan | `POST /trips/{id}/generate`, `GET /itineraries/{id}`, `POST /itineraries/{id}/save` |
| budget | `GET /trips/{id}/budget` |
| assistant | `POST /assistant/chat`, `GET /trips/{id}/packing`, `/weather` |

Freeze exact schemas with frontend/database/AI owners at M1. Status: 201 create, 200 read/update, 204 delete, 400 rule, 401 unauthenticated, 403 forbidden, 404 missing, 409 conflict, 422 validation, 503 unavailable with fallback status where relevant.
