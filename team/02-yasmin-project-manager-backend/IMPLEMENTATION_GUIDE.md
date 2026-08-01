# Implementation Guide

## Order

Triage board daily → freeze contracts → config/database → auth → one destination vertical slice → remaining catalogues → trips/budget → itinerary/save → AI/weather → integration tests.

## Role rules

Daily: review blockers, PRs, contracts, status, and next checkpoint. End milestones only after fresh-clone smoke test. Endpoints use `/api/v1`; routers call services, services use repositories, and response schemas never expose password hashes.

For every increment: define input/output and errors → implement smallest slice → test valid/invalid input → integrate with one adjacent layer → document result → commit. Mark unfinished production paths with `TODO` and never claim a template is complete.
