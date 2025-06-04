import os
import dspy
from dotenv import load_dotenv
from taskwarrior_dspy_definitions import TaskWarriorModule

# --- Configuration ---
load_dotenv() # Load .env file if it exists

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") # Ensure this is the correct API base if not default

# --- DSPy Setup ---
def setup_dspy():
    """Configures DSPy to use the local Ollama model."""
    print(f"Configuring DSPy with model: {OLLAMA_MODEL} at {OLLAMA_BASE_URL}")
    # Note: dspy.Ollama expects the base URL for the Ollama API, which is often just http://localhost:11434
    # The /api suffix is usually handled by the client or specific endpoints.
    # Let's try without /api first, as per common dspy.Ollama usage.
    # If Ollama is running on a different host or port, or if the model name in Ollama is different,
    # adjust OLLAMA_BASE_URL and OLLAMA_MODEL accordingly.
    try:
        llm = dspy.Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, max_tokens=2000) # Increased max_tokens for potentially complex commands
        dspy.settings.configure(lm=llm)
        print("DSPy configured successfully.")
    except Exception as e:
        print(f"Error configuring DSPy: {e}")
        print("Please ensure Ollama is running and the model '{OLLAMA_MODEL}' is available.")
        print(f"Attempted to connect to: {OLLAMA_BASE_URL}")
        # Provide more specific advice based on typical Ollama client setup in dspy
        print("If you're using a newer version of the 'ollama' Python package with dspy.Ollama,")
        print("the base_url should typically be just 'http://host:port' (e.g., 'http://localhost:11434').")
        print("If you are using an older dspy.Ollama or a direct HTTP call, it might need '/api'.")
        raise

# --- Task Execution ---
import shlex
import subprocess

def execute_taskwarrior_command(command_str):
    """Executes a Taskwarrior command and returns its output."""
    if not command_str.strip().startswith("task"):
        print(f"Error: Command does not start with 'task': {command_str}")
        return "", "Error: Invalid command format. Command must start with 'task'."

    print(f"\nExecuting command: {command_str}")
    
    try:
        # Split command into arguments
        args = shlex.split(command_str)
        
        # Run the command
        result = subprocess.run(
            args, 
            capture_output=True, 
            text=True,
            check=False
        )
        
        # Return output and error
        return result.stdout, result.stderr
        
    except FileNotFoundError:
        error_msg = "Error: 'task' command not found. Is Taskwarrior installed and in your PATH?"
        print(error_msg)
        return "", error_msg
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg)
        return "", error_msg

# --- Main Agent Loop ---
def main():
    """Main loop for the Taskwarrior agent."""
    try:
        setup_dspy()
    except Exception:
        return # Exit if DSPy setup fails

    task_module = TaskWarriorModule()

    print("\nTaskWarrior DSPy Assistant")
    print("Type 'exit' or 'quit' to end.")

    while True:
        user_input = input("\nYour request: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting agent.")
            break

        if not user_input.strip():
            continue

        # Get Taskwarrior command from DSPy module
        print("Asking LLM to generate Taskwarrior command...")
        try:
            prediction = task_module.forward(user_request=user_input)
            generated_command = prediction.taskwarrior_command.strip()
            # Basic validation of generated command
            if not generated_command.startswith("task "):
                print("Warning: Generated command doesn't start with 'task'")
                print(f"Raw command: {generated_command}")
                generated_command = f"task {generated_command}"
                
            print(f"LLM suggested command: {generated_command}")

            if not generated_command.lower().startswith("task"):
                print("Warning: LLM did not generate a valid 'task ...' command. Trying to be helpful but please verify.")
                # We could try to prepend 'task ' if it's missing and seems like a task query
                # but for now, let's just pass it as is and let execution handle it or user correct it.

            # At this point, Cascade would take the `generated_command`
            # and use the `run_command` tool to execute it after your approval.
            # For this script, we'll just print it and simulate the proposal.
            print(f"\nTo execute, you would run: {generated_command}")
            print("(In an integrated environment, this would be proposed for execution.)")

            # stdout, stderr = execute_taskwarrior_command(generated_command)
            # if stderr:
            #     print(f"\nTaskwarrior Error:\n{stderr}")
            # if stdout:
            #     print(f"\nTaskwarrior Output:\n{stdout}")

        except Exception as e:
            print(f"Error during LLM prediction or command processing: {e}")

if __name__ == "__main__":
    main()
