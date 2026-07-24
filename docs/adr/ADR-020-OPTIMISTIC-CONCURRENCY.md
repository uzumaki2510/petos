# ADR-020: Optimistic Concurrency Control (OCC) for Tasks, Comments, and Labels

## Context
Concurrent task updates can cause race conditions or silent overwrites.

## Decision
We enforce an integer `version` field on `tasks`, `task_comments`, and `labels`. Mutation requests must pass `expected_version`. If the database row version does not match, HTTP 409 Conflict (`code: concurrency_conflict`) is returned.

## Consequences
Prevents lost updates without requiring long-lived database row locks.
