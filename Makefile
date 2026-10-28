.PHONY: help bootstrap dev up down logs api web lint test eval clean models

help:
	@echo "Folio — common tasks"
	@echo "  make bootstrap   install backend + frontend deps"
	@echo "  make dev         run backend + frontend locally (no docker)"
	@echo "  make up          docker compose up -d"
	@echo "  make down        docker compose down"
	@echo "  make logs        tail compose logs"
	@echo "  make models      pull default Ollama models"
	@echo "  make lint        ruff + mypy + eslint"
	@echo "  make test        pytest + vitest"
	@echo "  make eval        run eval harness against golden set"
	@echo "  make clean       remove build/cache artifacts"

bootstrap:
	cd backend && uv venv && uv pip install -e ".[dev]"
	cd frontend && pnpm install

dev:
	@echo "Run in separate terminals:"
	@echo "  cd backend && uvicorn app.main:app --reload"
	@echo "  cd frontend && pnpm dev"

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

models:
	./scripts/pull-models.sh

lint:
	cd backend && ruff check . && mypy src
	cd frontend && pnpm lint

test:
	cd backend && pytest -q
	cd frontend && pnpm test --run

eval:
	cd backend && python -m app.eval.runner --config ../configs/folio.default.yaml

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf backend/.pytest_cache backend/.ruff_cache backend/.mypy_cache
	rm -rf frontend/.next frontend/node_modules/.cache
