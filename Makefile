.PHONY: help setup dev test lint format clean migrate createsuperuser collectstatic

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup:  ## Set up the development environment
	@echo "Setting up development environment..."
	python -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -e ".[dev]"
	. venv/bin/activate && python manage.py migrate
	. venv/bin/activate && python manage.py collectstatic --noinput
	@echo "Development environment setup complete!"
	@echo "Activate with: source venv/bin/activate"
	@echo "Run with: make dev"

dev:  ## Start development server
	@echo "Starting development server..."
	. venv/bin/activate && python manage.py runserver &
	@echo "Development server running at http://localhost:8000"
	@echo "Admin at http://localhost:8000/admin/"
	@echo "Press Ctrl+C to stop"

test:  ## Run tests with coverage
	@echo "Running tests..."
	. venv/bin/activate && python -m pytest

test-watch:  ## Run tests in watch mode
	@echo "Running tests in watch mode..."
	. venv/bin/activate && python -m pytest --watch

lint:  ## Run linting and type checking
	@echo "Running ruff..."
	. venv/bin/activate && ruff check .
	@echo "Running mypy..."
	. venv/bin/activate && mypy content/ personal_site/

format:  ## Format code with ruff
	@echo "Formatting code..."
	. venv/bin/activate && ruff format .

check:  ## Run all checks (lint + test)
	@echo "Running all checks..."
	. venv/bin/activate && make lint
	. venv/bin/activate && make test

migrate:  ## Run database migrations
	@echo "Running migrations..."
	. venv/bin/activate && python manage.py migrate

makemigrations:  ## Create new migrations
	@echo "Creating migrations..."
	. venv/bin/activate && python manage.py makemigrations

createsuperuser:  ## Create a superuser
	@echo "Creating superuser..."
	. venv/bin/activate && python manage.py createsuperuser

collectstatic:  ## Collect static files
	@echo "Collecting static files..."
	. venv/bin/activate && python manage.py collectstatic --noinput

loaddata:  ## Load sample data
	@echo "Loading sample data..."
	. venv/bin/activate && python manage.py loaddata sample_data

clean:  ## Clean up generated files
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	@echo "Cleanup complete!"

reset-db:  ## Reset database (WARNING: This will delete all data!)
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f db.sqlite3; \
		. venv/bin/activate && python manage.py migrate; \
		. venv/bin/activate && python manage.py createsuperuser; \
		. venv/bin/activate && python manage.py loaddata sample_data; \
		echo "Database reset complete!"; \
	else \
		echo "Database reset cancelled."; \
	fi 