import subprocess
import shlex

def execute_taskwarrior_command(command_str):
    """Execute a Taskwarrior CLI command and return its output"""
    try:
        # Split command into arguments
        args = shlex.split(f"task {command_str}")
        
        # Execute command and capture output
        result = subprocess.run(
            args,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
