# Phase 2: Engineering Foundation

## Overview
Phase 2 establishes the monorepo architecture and base boilerplate for PetOS. The architecture relies on an explicit separation between the frontend UI (`apps/web`) and the backend API (`services/api`), tied together via `pnpm` workspaces and Docker Compose for local development.

## Key Technical Decisions
- **Next.js App Router**: Used for its robust Server Components model, enabling fast initial loads and secure backend API fetching.
- **FastAPI + uv**: Python 3.13 combined with `uv` for lightning-fast dependency management. FastAPI provides auto-generated OpenAPI schemas which will be crucial for agent tool generation later.
- **pgvector**: We initialized a `pgvector` enabled database immediately to support future vector embeddings and semantic search of agent memories.
- **Asynchronous Data Access**: `asyncpg` and SQLAlchemy 2 async are used to ensure the FastAPI application remains non-blocking during database operations.
- **Testing**: A strict split between fast unit tests (mocked dependencies) and integration tests (real containerized dependencies) ensures both velocity and confidence.
