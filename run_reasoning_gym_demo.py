#!/usr/bin/env python3
"""
Demo script showing how to use reasoning_gym_inference.py
"""

import os
import subprocess
import sys

def main():
    """Run a simple demo of the reasoning gym inference."""
    # Check if API key is set
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: Please set DEEPSEEK_API_KEY environment variable")
        print("Example: export DEEPSEEK_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Run inference on a subset of tasks with fewer examples for demo
    print("Running ReasoningGym inference demo...")
    print("This will run 5 examples on 2 tasks (fraction_simplification and base_conversion)")
    print("-" * 60)
    
    cmd = [
        sys.executable,
        "reasoning_gym_inference.py",
        "--num-tries", "5",
        "--max-tokens", "100",
        "--output", "demo_results.json",
        "--tasks", "fraction_simplification", "base_conversion"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n" + "-" * 60)
        print("Demo completed successfully!")
        print("Check the following files for results:")
        print("  - demo_results.json (detailed results)")
        print("  - demo_results_summary.txt (summary)")
    else:
        print(f"\nDemo failed with return code: {result.returncode}")

if __name__ == "__main__":
    main()