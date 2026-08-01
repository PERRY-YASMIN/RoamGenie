# Implementation Guide

## Order

Freeze JSON schema → write mock → prompts → provider interface → timeout/retry → validation → fallback → endpoint contract tests.

## Role rules

AI never executes SQL, invents database IDs, or persists data. Backend supplies allow-listed records. Validate response before returning. One retry only for transient failures; short timeout; fall back to mock. Keys belong only in environment variables.

For every increment: define input/output and errors → implement smallest slice → test valid/invalid input → integrate with one adjacent layer → document result → commit. Mark unfinished production paths with `TODO` and never claim a template is complete.
