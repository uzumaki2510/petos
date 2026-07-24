# ADR-019: Task Lifecycle & Separation of Archival State

## Context
Task management systems require a clear state machine for operational workflow while maintaining historical records.

## Decision
We separate lifecycle status enum (`backlog`, `ready`, `in_progress`, `blocked`, `review`, `completed`, `cancelled`) from archival state (`archived_at`). Archiving makes a task read-only while preserving its lifecycle state.

## Consequences
Allows tasks to be hidden from standard views without destroying historical lifecycle state or timestamps.
