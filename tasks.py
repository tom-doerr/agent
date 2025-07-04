"""Task runner using invoke"""
from invoke import task

@task
def test(c, file=None, coverage=False, watch=False, fast=False):
    """Run tests with various options"""
    compose_file = "docker/compose/test.yml"
    
    if coverage:
        service = "test-coverage"
    elif watch:
        service = "test-watch"
    elif fast:
        service = "test-fast"
    elif file:
        c.run(f"docker compose -f {compose_file} run --rm test-file pytest {file} -v")
        return
    else:
        service = "test-all"
    
    c.run(f"docker compose -f {compose_file} run --rm {service}")

@task
def nlco(c, logs=False):
    """Run NLCO iteration service"""
    compose_file = "docker/compose/nlco.yml"
    if logs:
        c.run(f"docker compose -f {compose_file} logs -f")
    else:
        c.run(f"docker compose -f {compose_file} up -d")
        print("NLCO service started. MLflow UI: http://localhost:5004")

@task
def clean(c):
    """Clean up containers and volumes"""
    c.run("docker compose -f docker/compose/test.yml down -v")
    c.run("docker compose -f docker/compose/nlco.yml down -v")
    c.run("rm -rf test-results/")

@task
def lint(c):
    """Run linting checks"""
    c.run("ruff check .")

@task
def format(c):
    """Format code with black and isort"""
    c.run("black .")
    c.run("isort .")