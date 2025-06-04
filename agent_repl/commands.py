import os
import re
import subprocess

def execute_commands(commands: str, update_output) -> None:
    """Execute shell commands including Firebase searches"""
    for command in commands.splitlines():
        if not command.strip():
            continue
            
        if command.startswith("firebase:"):
            update_output(f"🔍 Firebase search: {command[9:]}", "info")
            try:
                # In a real implementation, this would call Firebase SDK
                # For demo purposes, we'll simulate a search
                result = f"Firebase results for '{command[9:]}':\n- Result 1\n- Result 2"
                update_output(result)
            except Exception as e:
                update_output(f"Firebase error: {str(e)}", "error")
        else:
            update_output(f"$ {command}", "info")
            try:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    cwd=os.getcwd()
                )
                if result.stdout:
                    update_output(result.stdout)
                if result.stderr:
                    update_output(result.stderr, "error")
            except Exception as e:
                update_output(f"Command error: {str(e)}", "error")

def apply_edits(edits: str, update_output) -> None:
    """Apply SEARCH/REPLACE edits to files"""
    pattern = r"```(\w+)?\n([\s\S]*?)<<<<<<< SEARCH\n([\s\S]*?)=======\n([\s\S]*?)>>>>>>> REPLACE\n```"
    
    for match in re.finditer(pattern, edits):
        file_path = match.group(2).strip()
        search_content = match.group(3)
        replace_content = match.group(4)
        
        update_output(f"✏️ Editing {file_path}", "info")
        
        try:
            with open(file_path, "r") as f:
                content = f.read()
            
            if search_content in content:
                new_content = content.replace(search_content, replace_content, 1)
                with open(file_path, "w") as f:
                    f.write(new_content)
                update_output(f"✅ Applied changes to {file_path}", "success")
            else:
                update_output(f"⚠️ Search content not found in {file_path}", "warning")
        
        except Exception as e:
            update_output(f"Error editing {file_path}: {str(e)}", "error")
