.PHONY: help build up down logs test lint format clean install dev

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev          - Run development server"
	@echo "  make build        - Build Docker images"
	@echo "  make up           - Start all services"
	@echo "  make down         - Stop all services"
	@echo "  make logs         - View logs"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make type-check   - Run type checking"
	@echo "  make clean        - Clean temporary files"
	@echo "  make migrate      - Run database migrations"
	@echo "  make shell        - Open Python shell"

install:
	pip install -r requirements.txt
	pre-commit install

dev:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-watch:
	pytest-watch tests/ -v

lint:
	black --check .
	ruff check .

format:
	black .
	ruff check . --fix

type-check:
	mypy src --ignore-missing-imports

security-scan:
	bandit -r src/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov coverage.xml .coverage

migrate:
	python -c "from src.database import create_db_and_tables; create_db_and_tables()"

shell:
	python -i -c "from src.main import app; from src.database import engine"

celery-worker:
	celery -A src.celery_app worker --loglevel=info

celery-flower:
	celery -A src.celery_app flower --port=5555

docker-shell:
	docker-compose exec app /bin/bash

docker-logs-app:
	docker-compose logs -f app

docker-logs-celery:
	docker-compose logs -f celery_worker

docker-rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
