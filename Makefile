.PHONY: help install install-dev test lint format type-check clean build docs
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"
	pre-commit install

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=src/sync_mcp_cfg --cov-report=html --cov-report=term

lint: ## Run linting
	ruff check src/ tests/

lint-fix: ## Run linting with auto-fix
	ruff check --fix src/ tests/

format: ## Format code
	black src/ tests/
	isort src/ tests/

format-check: ## Check code formatting
	black --check src/ tests/
	isort --check-only src/ tests/

type-check: ## Run type checking
	mypy src/

security: ## Run security checks
	bandit -r src/

quality: lint format-check type-check security ## Run all quality checks

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -name "*.pyc" -delete

build: clean ## Build package
	python -m build

docs: ## Build documentation
	mkdocs build

docs-serve: ## Serve documentation locally
	mkdocs serve

release-check: quality test ## Run all checks before release
	python -m build
	twine check dist/*

# Development workflow targets
dev-setup: install-dev ## Set up development environment
	@echo "Development environment ready!"

pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

update-deps: ## Update dependencies
	pip install --upgrade pip
	pip install --upgrade -e ".[dev]"

# CLI testing helpers
cli-help: ## Show CLI help
	sync-mcp-cfg --help

cli-status: ## Show client status
	sync-mcp-cfg status

cli-test: ## Run CLI with test data
	sync-mcp-cfg status --verbose