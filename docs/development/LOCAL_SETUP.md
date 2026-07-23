# PetOS Local Setup

## Requirements
- **Node.js**: v24 LTS
- **pnpm**: v11
- **Python**: v3.13
- **uv**: Package manager for Python
- **Docker** and **Docker Compose**

## Initial Setup
1. Clone the repository.
2. Copy the example environment variables:
   ```bash
   cp .env.example .env
   ```
3. Install all dependencies:
   ```bash
   make setup
   ```
   This will run `pnpm install` for the frontend and `uv sync` for the backend.

## Starting the Application
You can start the full development environment using Docker Compose:
```bash
make start
```
This runs `docker compose up --build -d`.

Alternatively, you can run the services locally (without Docker for the app code):
1. Start infrastructure: `docker compose up -d postgres redis`
2. Start API: `cd services/api && uv run uvicorn petos_api.main:app --reload`
3. Start Web: `cd apps/web && pnpm dev`

## Accessing Services
- **Web App**: http://localhost:3000
- **API Server**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Postgres Database**: `localhost:5432`
- **Redis Cache**: `localhost:6379`
