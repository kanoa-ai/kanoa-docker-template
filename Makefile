# Convenience wrappers around docker compose. Run `make` or `make help` for the list.
# Compose file selection (incl. local overrides) is driven by COMPOSE_FILE in .env.

.DEFAULT_GOAL := help
.PHONY: help up down restart logs ps pull build config shell db-shell clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

up: ## Start the stack in the background
	docker compose up -d

down: ## Stop and remove the containers
	docker compose down

restart: ## Restart the stack
	docker compose restart

logs: ## Tail logs from all services (use `make logs s=kanoa` for one)
	docker compose logs -f $(s)

ps: ## Show running services
	docker compose ps

pull: ## Pull the latest images
	docker compose pull

build: ## Build/refresh images
	docker compose build

config: ## Validate and print the merged compose config
	docker compose config

shell: ## Open a shell in the kanoa (Ignition) container
	docker compose exec kanoa bash

db-shell: ## Open a shell in the db container
	docker compose exec db bash

clean: ## Stop the stack and DELETE volumes (wipes the database)
	docker compose down -v
