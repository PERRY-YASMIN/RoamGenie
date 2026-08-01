# Implementation Guide

## Order

Install/version check → roles/database → environment → schema/migrations → seed → connection → permissions → backup/restore drill → index/performance review.

## Role rules

Use the Dashboard-recommended Supabase PostgreSQL connection in backend-only `DATABASE_URL`. Document pooler compatibility, grant minimum access, and never commit dumps or credentials. Confirm the development project and export a backup before an approved reset.

For every increment: define input/output and errors → implement smallest slice → test valid/invalid input → integrate with one adjacent layer → document result → commit. Mark unfinished production paths with `TODO` and never claim a template is complete.
