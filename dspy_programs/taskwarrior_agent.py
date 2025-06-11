import os
import dspy
from dotenv import load_dotenv
from taskwarrior_dspy_definitions import TaskWarriorModule
from dspy.teleprompt import SIMBA
import json
import shlex
import subprocess
import time

# --- Configuration ---
load_dotenv()  # Load .env file if it exists

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OPTIMIZATION_DATA_FILE = "taskwarrior_optimization_data.json"

# --- DSPy Setup ---
def setup_dspy():
    """Configures DSPy to use the local Ollama model."""
    print(f"Configuring DSPy with model: {OLLAMA_MODEL} at {OLLAMA_BASE_URL}")
    try:
        llm = dspy.Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, max_tokens=2000)
        dspy.settings.configure(lm=llm)
        print("DSPy configured successfully.")
        return llm
    except Exception as e:
        print(f"Error configuring DSPy: {e}")
        print("Please ensure Ollama is running and the model '{OLLAMA_MODEL}' is available.")
        print(f"Attempted to connect to: {OLLAMA_BASE_URL}")
        print("If you're using a newer version of the 'ollama' Python package with dspy.Ollama,")
        print("the base_url should typically be just 'http://host:port' (e.g., 'http://localhost:11434').")
        raise

# --- Task Execution ---
def execute_taskwarrior_command(command_str):
    """Executes a Taskwarrior command and returns its output."""
    if not command_str.strip().startswith("task"):
        return "", "Error: Invalid command format. Command must start with 'task'."

    try:
        args = shlex.split(command_str)
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        return result.stdout, result.stderr
    except FileNotFoundError:
        return "", "Error: 'task' command not found. Is Taskwarrior installed?"
    except Exception as e:
        return "", f"An unexpected error occurred: {e}"

# --- Optimization ---
def save_optimization_data(data):
    """Save optimization data to file."""
    with open(OPTIMIZATION_DATA_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

def load_optimization_data():
    """Load optimization data from file."""
    try:
        with open(OPTIMIZATION_DATA_FILE, "r") as f:
            return [json.loads(line) for line in f]
    except FileNotFoundError:
        return []

def optimize_module(module, data):
    """Optimize the DSPy module using SIMBA."""
    if not data:
        print("No optimization data available yet")
        return module

    print(f"Optimizing module with {len(data)} examples...")
    trainset = [
        dspy.Example(user_request=ex["request"], taskwarrior_command=ex["command"])
        for ex in data
    ]
    
    optimizer = SIMBA(
        metric=lambda example, pred, trace=None: 1.0 if pred.taskwarrior_command == example.taskwarrior_command else 0.0,
        max_steps=12,
        max_demos=10
    )
    
    try:
        optimized_module = optimizer.compile(module, trainset=trainset)
        print("Optimization complete!")
        return optimized_module
    except Exception as e:
        print(f"Optimization failed: {e}")
        return module

# --- Main Agent Loop ---
def main():
    """Main loop for the Taskwarrior agent."""
    llm = setup_dspy()
    if not llm:
        return
    
    # Initialize module and load optimization data
    base_module = TaskWarriorModule()
    optimization_data = load_optimization_data()
    optimized_module = optimize_module(base_module, optimization_data)
    
    print("\nEnhanced TaskWarrior Assistant")
    print("Type 'exit' or 'quit' to end. Type 'optimize' to force optimization")

    while True:
        user_input = input("\nYour request: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting agent.")
            break
        if user_input.lower() == "optimize":
            optimized_module = optimize_module(optimized_module, optimization_data)
            continue

        print("Processing request...")
        start_time = time.time()
        
        try:
            # Get Taskwarrior command from DSPy module
            prediction = optimized_module.forward(user_request=user_input)
            generated_command = prediction.taskwarrior_command.strip()
            
            if not generated_command.startswith("task "):
                generated_command = f"task {generated_command}"
                
            print(f"\nGenerated command: {generated_command}")

            # Execute command
            stdout, stderr = execute_taskwarrior_command(generated_command)
            
            # Show results
            if stderr:
                print(f"\nError:\n{stderr}")
            if stdout:
                print(f"\nOutput:\n{stdout}")
            
            # Collect data for optimization
            execution_time = time.time() - start_time
            optimization_data.append({
                "request": user_input,
                "command": generated_command,
                "execution_time": execution_time,
                "success": stderr == ""
            })
            save_optimization_data(optimization_data[-1])
            
            print(f"\nExecution time: {execution_time:.2f}s")
            
        except Exception as e:
            print(f"Error during processing: {e}")

if __name__ == "__main__":
    main()
