
# ==============================================
# RapidKit Project Automation
# ==============================================
.DEFAULT_GOAL := help
.RECIPEPREFIX := >

COMPOSE_BASE ?= deploy/compose/base.yml
COMPOSE_LOCAL ?= deploy/compose/local.yml
COMPOSE_PRODUCTION ?= deploy/compose/production.yml

POETRY ?= poetry
PYTHON ?= python3

.PHONY: help install setup dev start lint format test coverage typecheck build docker-build docker-up docker-down docker-logs docker-up-prod docker-down-prod docker-logs-prod ci

help: ## Show available commands
> @echo "RapidKit project commands:"
> @echo ""
> @grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
> awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2}'

install: ## Install project dependencies
> @echo "[install] Installing dependencies"

> npm install


setup: ## Install dependencies and prepare tooling
> @$(MAKE) install


dev: ## Run the application in development mode
> @echo "[dev] Starting development server"

> npm run start:dev



start: ## Run the application with production settings
> @echo "[start] Starting production server"

> npm run start:prod



lint: ## Run static analysis checks

> npm run lint



format: ## Auto-format the codebase

> npm run format



test: ## Run unit tests

> npm run test



coverage: ## Run tests with coverage reporting

> npm run test:cov
 || npm run test
 -- --coverage


typecheck: ## Run static type checks

> npm run lint



build: ## Build distributable artifacts

> npm run build



ci: ## Run the CI pipeline locally
> @echo "[ci] Running CI pipeline"
> $(MAKE) lint
> $(MAKE) typecheck
> $(MAKE) test

# ==============================================
# Docker helpers
# ==============================================

docker-build: ## Build all Docker images
> docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_LOCAL) build

docker-up: ## Start local Docker services
> docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_LOCAL) --profile local up --remove-orphans

docker-up-prod: ## Start production-like Docker services
> docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_PRODUCTION) --profile production up -d --remove-orphans

docker-down: ## Stop local Docker services
> docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_LOCAL) --profile local down

docker-down-prod: ## Stop production-like Docker services
> docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_PRODUCTION) --profile production down

docker-logs: ## Tail logs from local services
> docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_LOCAL) --profile local logs -f

docker-logs-prod: ## Tail logs from production-like services
> docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_PRODUCTION) --profile production logs -f

