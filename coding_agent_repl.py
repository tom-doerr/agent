import os
import re
import subprocess
import dspy
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, Input, Button
from textual.reactive import reactive

# --- DSPy Configuration ---
def configure_dspy():
    llm = dspy.LM(model="deepseek/deepseek-reasoner")
    dspy.settings.configure(lm=llm)
    return llm

# --- Core Agent ---
class CodingAgentSignature(dspy.Signature):
    """Execute coding tasks autonomously."""
    request = dspy.InputField(desc="User request for code changes")
    plan = dspy.OutputField(desc="Step-by-step plan to complete request")
    commands = dspy.OutputField(desc="Shell commands to execute")
    edits = dspy.OutputField(desc="File edits in SEARCH/REPLACE block format")
    done = dspy.OutputField(desc="'DONE' when task is complete, otherwise 'CONTINUE'")

class CodingAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.agent = dspy.ChainOfThought(CodingAgentSignature)
    
    def forward(self, request):
        return self.agent(request=request)

# --- Textual App ---
class CodingAgentREPL(App):
    CSS = """
    Container {
        layout: vertical;
        height: 1fr;
    }
    #output {
        height: 85%;
        border: solid $accent;
        padding: 1;
        overflow-y: auto;
    }
    #input-container {
        height: 15%;
        width: 100%;
        align: center top;
    }
    Input {
        width: 80%;
        margin: 1 0;
    }
    Button {
        width: 15%;
    }
    """
    
    current_state = reactive("")
    agent = CodingAgent()
    configure_dspy()
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Static(id="output")
            with Container(id="input-container"):
                yield Input(placeholder="Enter request", id="request-input")
                yield Button("Execute", id="execute-btn")
        yield Footer()
    
    def on_mount(self) -> None:
        self.query_one("#request-input").focus()
        self.update_output("🌟 Coding Agent REPL 🌟\nType '/exit' to quit\n")
    
    def update_output(self, text: str) -> None:
        self.current_state += text + "\n"
        self.query_one("#output").update(self.current_state)
    
    def execute_agent(self, request: str) -> None:
        """Execute agent on user request"""
        self.update_output(f"> {request}")
        
        try:
            response = self.agent(request=request)
            self.update_output(f"PLAN:\n{response.plan}")
            
            # Execute commands
            if response.commands.strip():
                self.execute_commands(response.commands)
            
            # Apply file edits
            if response.edits.strip():
                self.apply_edits(response.edits)
            
            # Check if done
            if "DONE" in response.done:
                self.update_output("✅ TASK COMPLETE")
            else:
                self.update_output("🔄 CONTINUING")
                
        except Exception as e:
            self.update_output(f"❌ Error: {str(e)}")
    
    def execute_commands(self, commands: str) -> None:
        """Execute shell commands"""
        for command in commands.splitlines():
            if not command.strip():
                continue
            self.update_output(f"$ {command}")
            try:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    cwd=os.getcwd()
                )
                if result.stdout:
                    self.update_output(result.stdout)
                if result.stderr:
                    self.update_output(result.stderr)
            except Exception as e:
                self.update_output(f"Command error: {str(e)}")
    
    def apply_edits(self, edits: str) -> None:
        """Apply SEARCH/REPLACE edits to files"""
        pattern = r"```(\w+)?\n([\s\S]*?)<<<<<<< SEARCH\n([\s\S]*?)=======\n([\s\S]*?)>>>>>>> REPLACE\n```"
        
        for match in re.finditer(pattern, edits):
            file_path = match.group(2).strip()
            search_content = match.group(3)
            replace_content = match.group(4)
            
            self.update_output(f"Editing {file_path}")
            
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                
                if search_content in content:
                    new_content = content.replace(search_content, replace_content, 1)
                    with open(file_path, "w") as f:
                        f.write(new_content)
                    self.update_output(f"✅ Applied changes to {file_path}")
                else:
                    self.update_output(f"⚠️ Search content not found in {file_path}")
            
            except Exception as e:
                self.update_output(f"Error editing {file_path}: {str(e)}")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "execute-btn":
            self.process_request()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.process_request()
    
    def process_request(self) -> None:
        request_input = self.query_one("#request-input")
        request = request_input.value.strip()
        request_input.value = ""
        
        if request.lower() == "/exit":
            self.exit()
            return
        
        if request:
            self.execute_agent(request)

if __name__ == "__main__":
    app = CodingAgentREPL()
    app.run()
