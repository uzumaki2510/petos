# Phase 4: Task Management and Workflow Foundation

## Architecture & Design Decisions

1. **Separation of Lifecycle Status and Archival State**:
   - Task lifecycle status is an operational enum (`backlog`, `ready`, `in_progress`, `blocked`, `review`, `completed`, `cancelled`).
   - Archival state is tracked separately via `archived_at: TIMESTAMPTZ`. Archived tasks become read-only and return `409 Conflict` (`code: task_archived`) for mutation requests.

2. **Immutable Project Keys & Task Display Identifiers**:
   - Each project has an immutable `key` (e.g. `PET`). Display task identifiers combine project key and sequence number: `PET-1`.

3. **Atomic Task-Number Allocation**:
   - Sequential task numbers are allocated inside the task creation transaction using `UPDATE projects SET next_task_number = next_task_number + 1 WHERE id = :id RETURNING next_task_number - 1`.

4. **Optimistic Concurrency Control (OCC)**:
   - Version checks on task, comment, and label mutations return `409 Conflict` (`code: concurrency_conflict`) if the version has drifted.

5. **Concurrency & Advisory Locking for Dependencies**:
   - Dependency graph additions use a transaction-level PostgreSQL advisory lock (`pg_advisory_xact_lock`) to serialize concurrent dependency creation and prevent cycles.

6. **Immutable Audit Log**:
   - All state mutations create JSONB activity log records (`task_activities`) in the same database transaction.
