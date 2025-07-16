# Docker Compose commands
COMPOSE = docker-compose
SERVICE = agent-runner

# Help message (default target)
.DEFAULT_GOAL := help

## Start the application using Docker Compose
up: ## Start the application in detached mode
	$(COMPOSE) up -d

## Stop the application
down: ## Stop all running containers
	$(COMPOSE) down

## Rebuild the Docker images
build: ## Build or rebuild Docker images
	$(COMPOSE) build

## Restart the service
restart: ## Restart the service
	$(COMPOSE) restart $(SERVICE)

## Run tests inside the container
test: ## Run tests inside the Docker container
	$(COMPOSE) exec $(SERVICE) pytest -v

## Run lint checks inside the container
lint: ## Run linting with flake8
	$(COMPOSE) exec $(SERVICE) flake8 .

## Show help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "🛠  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
