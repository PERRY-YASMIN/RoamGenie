# AI Services

The runnable starter is `backend/app/services/ai_service.py`. Madhu owns extraction into a provider-neutral interface in M4: validated input → adapter with timeout/one retry → JSON parse/schema validation/known-ID check → mock fallback. This folder holds provider-independent contracts, not keys or direct database code.

