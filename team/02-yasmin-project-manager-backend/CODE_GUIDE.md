# Code Guide

Daily: review blockers, PRs, contracts, status, and next checkpoint. End milestones only after fresh-clone smoke test. Endpoints use `/api/v1`; routers call services, services use repositories, and response schemas never expose password hashes.

- Prefer small named functions and consistent snake_case (Python/SQL) or camelCase (JavaScript).
- Validate at boundaries; log context without credentials or personal data.
- Keep configuration in environment variables documented in `.env.example`.
- Preserve working code. Stop and report overlapping or conflicting changes.
