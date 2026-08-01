# Code Guide

Use the Dashboard-recommended Supabase PostgreSQL connection in backend-only `DATABASE_URL`. Document pooler compatibility, grant minimum access, and never commit dumps or credentials. Confirm the development project and export a backup before an approved reset.

- Prefer small named functions and consistent snake_case (Python/SQL) or camelCase (JavaScript).
- Validate at boundaries; log context without credentials or personal data.
- Keep configuration in environment variables documented in `.env.example`.
- Preserve working code. Stop and report overlapping or conflicting changes.
