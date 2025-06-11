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
        # Add timeout to prevent hanging commands
        result = subprocess.run(
            args, 
            capture_output=True, 
            text=True,
            check=False,
            timeout=10  # 10 second timeout
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "", "Error: Command timed out after 10 seconds"
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
    # Filter to only successful examples
    successful_data = [ex for ex in data if ex.get("success", False)]
    
    if not successful_data:
        print("No successful optimization data available yet")
        return module

    print(f"Optimizing module with {len(successful_data)} successful examples...")
    trainset = [
        dspy.Example(user_request=ex["request"], taskwarrior_command=ex["command"])
        for ex in successful_data
    ]
    
    # Use a more robust metric that handles partial matches
    def command_metric(example, pred, trace=None):
        gold_command = example.taskwarrior_command.lower().replace("  ", " ").strip()
        pred_command = pred.taskwarrior_command.lower().replace("  ", " ").strip()
        
        # Give partial credit for matching command structure
        if gold_command == pred_command:
            return 1.0
        elif gold_command.split()[0] == pred_command.split()[0]:
            return 0.5  # partial credit for matching command type
        else:
            return 0.0
    
    try:
        optimizer = SIMBA(
            metric=command_metric,
            max_steps=12,
            max_demos=min(10, len(trainset))
        )
        
        optimized_module = optimizer.compile(module, trainset=trainset)
        print("Optimization complete!")
        return optimized_module
    except Exception as e:
        print(f"Optimization failed: {e}")
        import traceback
        traceback.print_exc()
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
    print(f"Loaded {len(optimization_data)} optimization examples ({len([d for d in optimization_data if d.get('success', False)])} successful)")
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
            
            # Validate command format
            if not generated_command.startswith("task "):
                print("Error: Generated command must start with 'task'")
                continue
                
            # Confirm execution
            confirm = input("Execute command? [Y/n]: ").strip().lower()
            if confirm not in ['', 'y', 'yes']:
                print("Command execution canceled")
                continue
                
            # Execute command
            stdout, stderr = execute_taskwarrior_command(generated_command)
            
            # Show results
            if stderr:
                print(f"\nError:\n{stderr}")
            if stdout:
                print(f"\nOutput:\n{stdout}")
            
            # Collect data for optimization
            execution_time = time.time() - start_time
            success = stderr == ""
            data_point = {
                "request": user_input,
                "command": generated_command,
                "execution_time": execution_time,
                "success": success
            }
            
            # Only save successful commands for optimization
            if success:
                optimization_data.append(data_point)
                save_optimization_data(data_point)
                print(f"Saved optimization data point")
            else:
                # Allow retry for failed commands
                retry = input("Retry with new command? [Y/n]: ").strip().lower()
                if retry in ['', 'y', 'yes']:
                    # Generate new command
                    prediction = optimized_module.forward(user_request=user_input)
                    generated_command = prediction.taskwarrior_command.strip()
                    
                    if not generated_command.startswith("task "):
                        generated_command = f"task {generated_command}"
                        
                    print(f"\nRetry command: {generated_command}")
                    
                    # Execute retry command
                    stdout, stderr = execute_taskwarrior_command(generated_command)
                    
                    # Show results
                    if stderr:
                        print(f"\nError:\n{stderr}")
                    if stdout:
                        print(f"\nOutput:\n{stdout}")
                    
                    # Update success status
                    success = stderr == ""
                    data_point = {
                        "request": user_input,
                        "command": generated_command,
                        "execution_time": time.time() - start_time,
                        "success": success
                    }
                    
                    if success:
                        optimization_data.append(data_point)
                        save_optimization_data(data_point)
                        print(f"Saved optimization data point")
            
            print(f"\nExecution time: {execution_time:.2f}s")
            print(f"Command {'succeeded' if success else 'failed'}")
            
        except Exception as e:
            print(f"Error during processing: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
