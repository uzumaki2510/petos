.PHONY: setup start stop logs lint format format-check typecheck test test-integration \
        test-all openapi-export openapi-check generate-client e2e build migrate check

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
	cd apps/web && pnpm exec eslint src --max-warnings=0
	cd services/api && uv run --frozen ruff check .

# Developer-only: mutates files
format:
	cd apps/web && pnpm exec prettier --write src
	cd services/api && uv run --frozen ruff format .

# Non-mutating format check used in CI and make check
format-check:
	cd services/api && uv run --frozen ruff format --check .

typecheck:
	pnpm --filter "./apps/*" typecheck
	cd services/api && uv run --frozen mypy src

test:
	pnpm --filter "./apps/*" test
	cd services/api && uv run --frozen pytest tests/unit -v

test-integration:
	cd services/api && uv run --frozen pytest tests/integration -v

test-all:
	pnpm --filter "./apps/*" test
	cd services/api && uv run --frozen pytest tests -v

# Phase 3: OpenAPI export — read-only (no file mutation on source)
openapi-export:
	cd services/api && uv run --frozen python scripts/export_openapi.py

openapi-check: openapi-export
	@echo "Checking OpenAPI schema drift..."
	git diff --exit-code services/api/openapi.json apps/web/openapi/petos.openapi.json
	@echo "Checking generated TypeScript client drift..."
	cd apps/web && pnpm generate-client
	git diff --exit-code apps/web/src/lib/api/generated/

generate-client:
	cd apps/web && pnpm generate-client
	@echo "Client generated at apps/web/src/lib/api/generated/"

e2e:
	cd apps/web && pnpm exec playwright test --project=chromium

build:
	pnpm --filter "./apps/*" build

migrate:
	docker compose run --rm migrate

# make check must not modify any source files or lockfiles
check: lint format-check typecheck test openapi-export build
