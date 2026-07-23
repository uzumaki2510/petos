# ADR 002: PostgreSQL as the Source of Truth

**Status:** Accepted
**Date:** 2026-07-23

## Context
PetOS needs to store relational data (users, projects, tasks) and potentially unstructured or document-based data (agent memory, chat logs). We could use multiple databases (e.g., MongoDB for logs, Postgres for users).

## Decision
We will use **PostgreSQL** as the single source of truth for all durable state.

## Rationale
- **JSONB Support:** Modern PostgreSQL handles JSON data exceptionally well, negating the immediate need for a NoSQL document store for agent memory.
- **Operational Simplicity:** Managing one database is significantly easier than managing two.
- **ACID Transactions:** Ensures consistency across user actions and project updates.

## Consequences
- We will use Redis for strictly ephemeral data (caching, WebSocket pub/sub for the UI), but all long-term data must reside in Postgres.
- We must carefully index JSONB columns if we need to query deeply nested agent memories at scale.
