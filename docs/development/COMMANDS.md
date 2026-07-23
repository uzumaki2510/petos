# Make Commands

We provide a `Makefile` to simplify common development tasks.

| Command | Description |
| :--- | :--- |
| `make setup` | Installs pnpm and uv dependencies for all projects. |
| `make start` | Starts the Docker Compose environment in the background. |
| `make stop` | Stops the Docker Compose environment. |
| `make logs` | Tails the logs of all Docker Compose services. |
| `make lint` | Runs ESLint for the frontend and Ruff for the backend. |
| `make typecheck` | Runs TypeScript compilation checks and mypy for Python. |
| `make test` | Runs Vitest for the frontend and Pytest for the backend. |
| `make build` | Builds the frontend Next.js application. |
| `make check` | Runs lint, typecheck, test, and build sequentially to verify CI readiness. |
| `make migrate` | Runs Alembic migrations against the database inside the API container. |
