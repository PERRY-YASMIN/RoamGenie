# Code Guide

Slides cover problem, existing/proposed system, architecture, database and normalization, modules, DBMS features, AI boundaries, test results, demo, limitations and future work. Demo order: register → login → plan → generate → budget → save → reopen.

- Prefer small named functions and consistent snake_case (Python/SQL) or camelCase (JavaScript).
- Validate at boundaries; log context without credentials or personal data.
- Keep configuration in environment variables documented in `.env.example`.
- Preserve working code. Stop and report overlapping or conflicting changes.
