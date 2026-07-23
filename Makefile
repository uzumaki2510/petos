.PHONY: setup start stop logs lint format-check typecheck test test-integration build migrate check

setup:
	corepack enable
	pnpm install
	cd services/api && uv sync

start:
	docker compose up --build -d

stop:
	docker compose down

logs:
	docker compose logs -f

lint:
	pnpm --filter "./apps/*" lint
	cd services/api && uv run ruff check .

format-check:
	cd services/api && uv run ruff format --check .

typecheck:
	pnpm --filter "./apps/*" typecheck
	cd services/api && uv run mypy src

test:
	pnpm --filter "./apps/*" test
	cd services/api && uv run pytest -m "not integration"

test-integration:
	docker compose run --rm api uv run --frozen pytest -m "integration"

build:
	pnpm --filter "./apps/*" build

migrate:
	docker compose run --rm migrate

check: lint format-check typecheck test build
