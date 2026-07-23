# Troubleshooting

## Database Connection Refused
If the API fails to connect to PostgreSQL:
1. Ensure the container is running: `docker compose ps`
2. Check the logs: `docker compose logs postgres`
3. Ensure no local PostgreSQL instances on your host machine are blocking port 5432.

## pnpm Install Fails
If `make setup` fails on the frontend:
- Ensure you are using `pnpm` version 11: `pnpm --version`.
- Clear the pnpm store: `pnpm store prune` and retry.

## uv Sync Fails
If the Python backend dependencies fail to install:
- Ensure you have Python 3.13 installed. `uv` will attempt to download it automatically, but if it fails, verify your system path.
- Try `uv sync --reinstall`.
