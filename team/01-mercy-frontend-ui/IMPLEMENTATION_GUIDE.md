# Implementation Guide

## Order

Create shell/routes → shared components → auth pages → trip form → catalogue pages → itinerary/budget → saved trips/assistant → responsive polish.

## Role rules

Routes: `/`, `/register`, `/login`, `/profile`, `/plan`, `/destinations`, `/hotels`, `/restaurants`, `/attractions`, `/itineraries/:id`, `/budget/:tripId`, `/saved`, `/assistant`, and `*`. Keep API calls in `src/services/api.js`; never call PostgreSQL. Validate required locations, future dates, travellers > 0, and budget > 0.

For every increment: define input/output and errors → implement smallest slice → test valid/invalid input → integrate with one adjacent layer → document result → commit. Mark unfinished production paths with `TODO` and never claim a template is complete.
