# Makefile for MLOps Pipeline

.PHONY: help install train run test build docker-build docker-run clean lint format

help:
	@echo "MLOps Pipeline - Available Commands"
	@echo "===================================="
	@echo "make install      - Install dependencies"
	@echo "make train        - Train ML model"
	@echo "make run          - Run FastAPI server"
	@echo "make test         - Run unit tests"
	@echo "make build        - Install and train"
	@echo "make docker-build - Build Docker image"
	@echo "make docker-run   - Run Docker container"
	@echo "make clean        - Clean up generated files"
	@echo "make lint         - Run linters"
	@echo "make format       - Format code"
	@echo "make all          - Build everything and run tests"

install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt

train:
	@echo "Training ML model..."
	python model/train.py

run:
	@echo "Starting FastAPI server..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "Running unit tests..."
	pytest tests/ -v --tb=short

build: install train
	@echo "Build completed successfully!"

lint:
	@echo "Running flake8..."
	flake8 app/ model/ tests/ --max-line-length=100 --ignore=E203,W503 || true
	@echo "Running mypy..."
	mypy app/ model/ || true

format:
	@echo "Formatting code with black..."
	black app/ model/ tests/
	@echo "Sorting imports..."
	isort app/ model/ tests/

docker-build:
	@echo "Building Docker image..."
	docker build -t swarajwadkar/ml-api:latest .

docker-run: docker-build
	@echo "Running Docker container..."
	docker run -p 8000:8000 swarajwadkar/ml-api:latest

docker-compose-up:
	@echo "Starting Docker Compose..."
	docker-compose up -d

docker-compose-down:
	@echo "Stopping Docker Compose..."
	docker-compose down

clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -rf build/ dist/ *.egg-info 2>/dev/null || true
	@echo "Cleanup completed!"

all: clean install lint format test build
	@echo "All tasks completed!"

.DEFAULT_GOAL := help
