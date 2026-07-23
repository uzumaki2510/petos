# ADR 001: Modular Monolith Architecture

**Status:** Accepted
**Date:** 2026-07-23

## Context
PetOS requires a backend to handle user authentication, project management, agent orchestration (LangGraph), and GitHub interactions. As a complex system, there is a temptation to split these domains into microservices immediately (e.g., an auth service, an agent service, a git service).

## Decision
We will build PetOS as a **Modular Monolith** using FastAPI.

## Rationale
- **Simplicity:** Microservices introduce immense operational complexity (network latency, distributed tracing, complex deployments) that are detrimental in Phase 1.
- **Velocity:** A monolith allows for faster refactoring and type-checking across domains in a single repository.
- **Enforced Boundaries:** By strictly enforcing module boundaries (as defined in `MODULE_BOUNDARIES.md`), we retain the ability to split into microservices later if scaling demands it, without paying the operational tax upfront.

## Consequences
- We must be highly disciplined about imports and module dependencies.
- A failure in one module (e.g., a memory leak in LangGraph) could theoretically crash the entire API server. We mitigate this through rigorous testing and proper resource limits.
