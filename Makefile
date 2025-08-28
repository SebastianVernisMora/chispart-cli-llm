.PHONY: up down logs ps dev fmt lint test build

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200 orchestrator console worker

ps:
	docker compose ps

dev: up logs

fmt:
	npx prettier -w .

lint:
	npm run -w apps/orchestrator lint && npm run -w packages/workers lint

test:
	npm run -w apps/orchestrator test -- --watch=false && npm run -w packages/workers test -- --watch=false

build:
	npm run -w apps/orchestrator build && npm run -w apps/console build && npm run -w packages/workers build
