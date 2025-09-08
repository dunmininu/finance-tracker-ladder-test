.PHONY: install run test lint fmt migrate superuser schema clean help docker-build docker-up docker-down docker-logs docker-shell

# Default target
help:
	@echo "Available commands:"
	@echo "  install       Install project dependencies"
	@echo "  run           Run the Django development server"
	@echo "  test          Run tests with pytest"
	@echo "  lint          Run ruff linter"
	@echo "  fmt           Format code with black"
	@echo "  migrate       Run Django migrations"
	@echo "  superuser     Create Django superuser"
	@echo "  schema        Generate OpenAPI schema"
	@echo "  clean         Clean up temporary files"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-up     Start Docker containers"
	@echo "  docker-down   Stop Docker containers"
	@echo "  docker-logs   Show Docker logs"
	@echo "  docker-shell  Access Docker container shell"
	@echo "  help          Show this help message"

# Install dependencies
install:
	pip install -e .

# Run development server
run:
	python manage.py runserver

# Run tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov=. --cov-report=html --cov-report=term

# Lint code
lint:
	ruff check .

# Format code
fmt:
	black .

# Run migrations
migrate:
	python manage.py makemigrations
	python manage.py migrate

# Create superuser
superuser:
	python manage.py createsuperuser

# Generate OpenAPI schema
schema:
	python manage.py spectacular --file openapi/schema.json

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-shell:
	docker-compose exec web bash

# Setup development environment
setup: install
	cp .env.example .env
	pre-commit install
	@echo "Development environment setup complete!"
	@echo "Don't forget to:"
	@echo "1. Edit .env with your settings"
	@echo "2. Run 'make migrate' to setup database"
	@echo "3. Run 'make superuser' to create admin user"
