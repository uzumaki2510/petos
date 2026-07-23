# PetOS

**PetOS** is a multi-agent AI software-engineering operating system where autonomous, specialist AI pets visually perform real development tasks inside an interactive pixel-art office. 

## Requirements
To develop PetOS locally, ensure you have the following installed:
- **Node.js 24 LTS**
- **pnpm 11**
- **Python 3.13**
- **uv** (Python package manager)
- **Docker** and **Docker Compose**

## Setup & Startup
1. **Environment Config**: Copy `.env.example` to `.env`.
   ```bash
   cp .env.example .env
   ```
2. **Install Dependencies**:
   ```bash
   make setup
   ```
3. **Start the Application**:
   ```bash
   make start
   ```
4. **Run Database Migrations**:
   ```bash
   make migrate
   ```

## Service URLs
- **Web App**: http://localhost:3000
- **API Server**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Postgres Database**: `localhost:5432`
- **Redis Cache**: `localhost:6379`

## Test Commands
- **Check Everything (Lint, Typecheck, Test, Build)**: `make check`
- **Frontend Tests**: `pnpm test`
- **Backend Tests**: `cd services/api && uv run pytest tests/`

## Repository Structure
- `apps/web/`: Next.js React frontend.
- `services/api/`: FastAPI Python backend.
- `docs/`: Comprehensive project documentation.
- `.github/workflows/`: CI/CD pipelines.

## Documentation Navigation
- **[Roadmap](docs/ROADMAP.md)**: Explore the 15-phase development plan.
- **[Local Setup](docs/development/LOCAL_SETUP.md)**: Detailed local development instructions.
- **[Product Documentation](docs/product/)**: Read about the vision, requirements (PRD), MVP scope, and more.
- **[Architecture](docs/architecture/)**: Dive into the system context, module boundaries, and tech stack.
- **[Security & UX](docs/security/)**: Read about the risk register and UX vision.
- **[Architecture Decision Records (ADRs)](docs/adr/)**: Explore the key architectural choices made.
