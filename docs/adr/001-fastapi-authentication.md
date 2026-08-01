# ADR 001: Keep authentication in FastAPI

Status: accepted for v1.

FastAPI hashes passwords, creates/validates JWTs, checks resource ownership and stores users in PostgreSQL. React calls FastAPI auth endpoints. This demonstrates backend authentication, centralizes application rules, avoids mixing two identity systems and is easier to explain during course evaluation. Supabase Auth is a possible future enhancement, not part of v1. If implemented later, create a new ADR and identity/RLS migration; do not run both systems implicitly.
