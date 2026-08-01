# Code Guide

Use snake_case, singular migration sequence, explicit columns, parameterized application queries, and comments stating purpose. Rules: positive budget/travellers; valid dates; rating 0–5; nonnegative expenses; safe child deletes; auditable important changes. Do not add decorative triggers.

- Prefer small named functions and consistent snake_case (Python/SQL) or camelCase (JavaScript).
- Validate at boundaries; log context without credentials or personal data.
- Keep configuration in environment variables documented in `.env.example`.
- Preserve working code. Stop and report overlapping or conflicting changes.
