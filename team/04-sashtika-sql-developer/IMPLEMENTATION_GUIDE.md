# Implementation Guide

## Order

DDL/constraints → seed data → 15 queries → views → functions/procedure → useful audit/total trigger → transactions → indexes → verification.

## Role rules

### Supabase SQL Editor procedure

1. Confirm the development project with Penitta; never assume the demo target.
2. Open Supabase Dashboard → **SQL Editor** → **New query**.
3. Copy the matching reviewed statement from `database/`.
4. Check that Alembic does not own the same DDL object.
5. Run pre-verification and use a transaction where supported.
6. Execute and capture sanitized results without URLs or credentials.
7. Verify the result and inspect relevant objects in Table Editor.
8. Save every final statement in Git; Dashboard history is not source of truth.
9. Record environment, Alembic revision, order and outcome in the PR.

For `psql`, use a securely supplied native PostgreSQL URI and `-v ON_ERROR_STOP=1`; never commit the URI.

Use snake_case, singular migration sequence, explicit columns, parameterized application queries, and comments stating purpose. Rules: positive budget/travellers; valid dates; rating 0–5; nonnegative expenses; safe child deletes; auditable important changes. Do not add decorative triggers.

For every increment: define input/output and errors → implement smallest slice → test valid/invalid input → integrate with one adjacent layer → document result → commit. Mark unfinished production paths with `TODO` and never claim a template is complete.
