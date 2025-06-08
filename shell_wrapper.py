import asyncio
import os
import shlex
from typing import Tuple

class ShellWrapper:
    def __init__(self, shell: str = "/bin/bash"):
        self.shell = shell
        self.process = None
        self.lock = asyncio.Lock()
        self.cwd = os.getcwd()

    async def start(self):
        """Start the persistent shell process"""
        self.process = await asyncio.create_subprocess_shell(
            self.shell,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=self.cwd
        )
        # Set initial working directory
        await self._execute_internal(f"cd {shlex.quote(self.cwd)}")

    async def _execute_internal(self, command: str) -> Tuple[str, int]:
        """Low-level command execution with lock"""
        async with self.lock:
            # Write command with exit code marker
            self.process.stdin.write(f"{command}\necho __EXIT__$?\n".encode())
            await self.process.stdin.drain()
            
            # Read output until exit marker
            output = []
            while True:
                line = await self.process.stdout.readline()
                if not line:
                    break
                text = line.decode().rstrip()
                if text.startswith("__EXIT__"):
                    exit_code = int(text.split("__EXIT__")[1])
                    break
                output.append(text)
            
            return "\n".join(output), exit_code

    async def execute(self, command: str) -> Tuple[str, int]:
        """Execute a command with state preservation"""
        if command.strip().startswith("cd "):
            new_dir = command.strip()[3:].strip()
            try:
                # Update internal state
                new_path = os.path.abspath(os.path.expanduser(new_dir))
                if not os.path.isdir(new_path):
                    return f"cd error: Directory not found: {new_path}", 1
                self.cwd = new_path
                # Send to shell
                output, exit_code = await self._execute_internal(f"cd {shlex.quote(new_path)}")
                return f"Changed directory to {self.cwd}", exit_code
            except Exception as e:
                return f"cd error: {str(e)}", 1
        else:
            return await self._execute_internal(command)

    async def stop(self):
        """Gracefully stop the shell process"""
        if self.process:
            self.process.stdin.write("exit\n".encode())
            await self.process.stdin.drain()
            await self.process.wait()
