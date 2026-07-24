# Task Workflow Specification

## Task Lifecycle States
- `backlog`: Initial state for un-prioritized tasks.
- `ready`: Approved for active work.
- `in_progress`: Active execution.
- `blocked`: Blocked by dependencies or external factors.
- `review`: Code or QA review.
- `completed`: Successfully resolved.
- `cancelled`: Work cancelled.

## Transition Rules
- Reopening a `completed` task to `in_progress` requires a non-empty reason and clears `completed_at`.
- Reopening a `cancelled` task to `backlog` requires a non-empty reason and clears `completed_at`.
- Archiving is a separate read-only state triggered via `/v1/tasks/{id}/archive`.
