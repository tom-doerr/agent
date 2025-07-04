# Docker Setup

This directory contains Docker configurations for the project.

## Structure

```
docker/
├── compose/       # Docker Compose files
│   ├── nlco.yml  # NLCO iteration service with MLflow
│   └── test.yml  # Test runner configurations
├── Dockerfile.nlco   # NLCO service image
└── Dockerfile.tests  # Test runner image
```

## Running Tests

### Using Make (Recommended)
```bash
make test              # Run all tests
make test FILE=tests/test_config.py  # Run specific test
make test-coverage     # Run with coverage report
make test-watch        # Run in watch mode
make test-fast         # Run only fast tests
```

### Using Python task runner
```bash
# Install invoke first: pip install invoke
invoke test            # Run all tests
invoke test --file tests/test_config.py  # Run specific test
invoke test --coverage # Run with coverage
invoke test --watch    # Run in watch mode
```

### Using Docker Compose directly
```bash
docker compose -f docker/compose/test.yml run --rm test-all
docker compose -f docker/compose/test.yml run --rm test-coverage
docker compose -f docker/compose/test.yml run --rm test-file pytest tests/test_config.py -v
```

### Using tox
```bash
tox              # Run all environments
tox -e py311     # Run Python 3.11 tests
tox -e coverage  # Run with coverage
tox -e docker    # Run in Docker
```

## Running NLCO Service

```bash
make nlco         # Start NLCO with MLflow
make nlco-logs    # View logs
make nlco-stop    # Stop services
```

## Benefits of this structure

1. **Clean project root** - All Docker files organized in subdirectory
2. **Multiple interfaces** - Use Make, Python, or Docker directly
3. **Standard tools** - Make and tox are widely understood
4. **No shell scripts** - More portable and maintainable
5. **Flexible** - Easy to extend with new test configurations