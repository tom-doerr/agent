#!/bin/bash
set -e

echo "🧪 Running all tests..."
echo "========================"

# Create test results directory
mkdir -p test-results/{backend,frontend,e2e}

# Run all tests
echo "1. Running backend tests..."
docker compose -f docker-compose.test.yml run --rm backend-test

echo -e "\n2. Running frontend tests..."
docker compose -f docker-compose.test.yml run --rm frontend-test

echo -e "\n3. Running E2E tests..."
docker compose -f docker-compose.test.yml run --rm e2e-test

echo -e "\n✅ All tests completed!"
echo "Test results saved in ./test-results/"