UV ?= uv
NPM ?= npm

.PHONY: setup backend-sync frontend-install api worker frontend-dev migrate \
	format format-check lint typecheck test migration-check build generate-api \
	contract-check check

setup: backend-sync frontend-install

backend-sync:
	$(UV) sync --project backend --locked --all-groups

frontend-install:
	$(NPM) --prefix frontend ci

api:
	$(UV) run --project backend uvicorn resale_monitor.main:app --reload

worker:
	$(UV) run --project backend resale-monitor-worker

frontend-dev:
	$(NPM) --prefix frontend run dev

migrate:
	$(UV) run --project backend alembic -c backend/alembic.ini upgrade head

format:
	$(UV) run --project backend ruff format backend
	$(UV) run --project backend ruff check --fix backend
	$(NPM) --prefix frontend run format

format-check:
	$(UV) run --project backend ruff format --check backend
	$(NPM) --prefix frontend run format:check

lint:
	$(UV) run --project backend ruff check backend
	$(NPM) --prefix frontend run lint

typecheck:
	$(UV) run --project backend mypy --config-file backend/pyproject.toml backend/src
	$(NPM) --prefix frontend run typecheck

test:
	$(UV) run --project backend pytest backend/tests
	$(NPM) --prefix frontend test

migration-check:
	$(UV) run --project backend pytest --no-cov backend/tests/test_migrations.py

build:
	$(NPM) --prefix frontend run build

generate-api:
	$(UV) run --project backend python backend/scripts/export_openapi.py
	$(NPM) --prefix frontend run generate:api

contract-check: generate-api
	git diff --exit-code -- backend/openapi.json frontend/src/api/schema.d.ts

check: format-check lint typecheck test migration-check build contract-check
