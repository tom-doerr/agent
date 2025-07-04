#!/usr/bin/env python3
"""Test runner with Docker support"""
import argparse
import subprocess
import sys
from pathlib import Path

def run_docker_compose(service: str, extra_args: list = None):
    """Run a docker compose service"""
    compose_file = Path(__file__).parent.parent / "docker/compose/test.yml"
    cmd = ["docker", "compose", "-f", str(compose_file), "run", "--rm", service]
    if extra_args:
        cmd.extend(extra_args)
    
    result = subprocess.run(cmd)
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description="Run tests in Docker")
    parser.add_argument("target", nargs="?", default="all",
                      help="Test target: all, coverage, watch, fast, or specific file")
    parser.add_argument("--coverage", action="store_true", 
                      help="Run with coverage")
    parser.add_argument("--watch", action="store_true",
                      help="Run in watch mode")
    parser.add_argument("--fast", action="store_true",
                      help="Run only fast tests")
    
    args = parser.parse_args()
    
    if args.coverage:
        return run_docker_compose("test-coverage")
    elif args.watch:
        return run_docker_compose("test-watch")
    elif args.fast:
        return run_docker_compose("test-fast")
    elif args.target != "all":
        # Run specific test file
        return run_docker_compose("test-file", ["pytest", args.target, "-v"])
    else:
        return run_docker_compose("test-all")

if __name__ == "__main__":
    sys.exit(main())