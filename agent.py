import tempfile
import subprocess
import os

def vim_input(prompt=""):
    """Get user input using Vim keybindings via external editor"""
    with tempfile.NamedTemporaryFile(suffix=".txt", mode='w+') as tmpfile:
        if prompt:
            tmpfile.write(f"# {prompt}\n")
            tmpfile.write("# Enter your request below. Save and exit when done.\n")
            tmpfile.flush()
        editor = os.environ.get('EDITOR', 'vim')
        subprocess.call([editor, tmpfile.name])
        tmpfile.seek(0)
        content = tmpfile.read()
        return content.strip()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        user_request = " ".join(sys.argv[1:])
    else:
        user_request = vim_input("Enter your request (Vim keybindings supported)")
    print(f"User request: {user_request}")
