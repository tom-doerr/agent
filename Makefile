# Project Makefile
.PHONY: help test test-all test-coverage test-watch test-fast nlco mlflow clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make test           - Run all tests"
	@echo "  make test-coverage  - Run tests with coverage report"
	@echo "  make test-watch     - Run tests in watch mode"
	@echo "  make test-fast      - Run only fast tests"
	@echo "  make test FILE=...  - Run specific test file"
	@echo "  make nlco           - Run NLCO iteration service"
	@echo "  make mlflow         - Start MLflow UI"
	@echo "  make clean          - Clean up containers and volumes"

# Test commands
test:
	docker compose -f docker/compose/test.yml run --rm test-all

test-all: test

test-coverage:
	docker compose -f docker/compose/test.yml run --rm test-coverage
	@echo "Coverage report: ./test-results/coverage/index.html"

test-watch:
	docker compose -f docker/compose/test.yml run --rm test-watch

test-fast:
	docker compose -f docker/compose/test.yml run --rm test-fast

# Run specific test file
ifdef FILE
test:
	docker compose -f docker/compose/test.yml run --rm test-file pytest $(FILE) -v
endif

# NLCO services
nlco:
	docker compose -f docker/compose/nlco.yml up -d

nlco-logs:
	docker compose -f docker/compose/nlco.yml logs -f

nlco-stop:
	docker compose -f docker/compose/nlco.yml down

# MLflow
mlflow:
	@echo "Starting MLflow on http://localhost:5004"
	docker compose -f docker/compose/nlco.yml up -d mlflow

# Cleanup
clean:
	docker compose -f docker/compose/test.yml down -v
	docker compose -f docker/compose/nlco.yml down -v
	rm -rf test-results/