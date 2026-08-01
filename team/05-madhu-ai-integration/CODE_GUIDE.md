# Code Guide

AI never executes SQL, invents database IDs, or persists data. Backend supplies allow-listed records. Validate response before returning. One retry only for transient failures; short timeout; fall back to mock. Keys belong only in environment variables.

- Prefer small named functions and consistent snake_case (Python/SQL) or camelCase (JavaScript).
- Validate at boundaries; log context without credentials or personal data.
- Keep configuration in environment variables documented in `.env.example`.
- Preserve working code. Stop and report overlapping or conflicting changes.
