import os
import re
import subprocess
import dspy
import time
import threading
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, Input, Button
from textual.reactive import reactive
from textual import events
from textual import log
from dspy.utils import dotmap

# --- DSPy Configuration ---
def configure_dspy():
    llm = dspy.LM(model="openrouter/deepseek/deepseek-chat-v3-0324")
    dspy.settings.configure(lm=llm)
    return llm

# --- Core Agent ---
class CodingAgentSignature(dspy.Signature):
    """Execute coding tasks autonomously. You can search Firebase by using 'firebase:' prefix in commands."""
    request = dspy.InputField(desc="User request for code changes")
    plan = dspy.OutputField(desc="Step-by-step plan to complete request")
    commands = dspy.OutputField(desc="Shell commands to execute. Use 'firebase:query' for Firebase searches.")
    edits = dspy.OutputField(desc="File edits in SEARCH/REPLACE block format")
    done = dspy.OutputField(desc="'DONE' when task is complete, 'CONTINUE' to process next step autonomously")

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
    #output-container {
        height: 85%;
        border: solid $accent;
        padding: 1;
        overflow: hidden;
    }
    #output {
        overflow-y: auto;
        height: 100%;
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
    #loading {
        background: $accent;
        color: $text;
        text-align: center;
        padding: 1;
    }
    .hidden {
        display: none;
    }
    .success {
        color: green;
    }
    .error {
        color: red;
    }
    .warning {
        color: yellow;
    }
    .info {
        color: blue;
    }
    """
    
    current_state = reactive("")
    agent = CodingAgent()
    configure_dspy()
    LOG_FILE = "coding_agent_repl.log"
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Static("Thinking...", id="loading", classes="hidden")
            with Container(id="output-container"):
                yield Static(id="output")
            with Container(id="input-container"):
                yield Input(placeholder="Enter request", id="request-input")
                yield Button("Execute", id="execute-btn")
        yield Footer()
    
    def on_mount(self) -> None:
        self.vim_mode = "insert"
        self.set_focus(self.query_one("#request-input"))
        # Clear log file on startup
        with open(self.LOG_FILE, "w") as f:
            f.write("")
        self.update_output("🌟 Coding Agent REPL 🌟\nType '/exit' to quit\n")
        self.enable_input()
        
    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.vim_mode = "normal"
        elif event.key == "i" and self.vim_mode == "normal":
            self.vim_mode = "insert"
        elif event.key == ":" and self.vim_mode == "normal":
            self.vim_mode = "command"
            self.query_one("#request-input").value = ":"
        elif self.vim_mode == "insert":
            # Let the input handle the key
            return
        else:
            # Prevent key propagation in normal/command modes
            event.prevent_default()
    
    def update_output(self, text: str, style_class: str = "") -> None:
        # This method must be called from the main thread
        if threading.current_thread() == threading.main_thread():
            self._do_update_output(text, style_class)
        else:
            # Schedule the update on the main thread
            self.call_from_thread(self._do_update_output, text, style_class)
    
    def _do_update_output(self, text: str, style_class: str = "") -> None:
        # Add styling if provided
        styled_text = f"[{style_class}]{text}[/]" if style_class else text
        # Append to current state
        self.current_state += styled_text + "\n"
        # Update output widget
        output_widget = self.query_one("#output")
        output_widget.update(self.current_state)
        # Scroll to bottom
        output_container = self.query_one("#output-container")
        output_container.scroll_end(animate=False)
        
        # Append to log file
        with open(self.LOG_FILE, "a") as f:
            f.write(text + "\n")
            
        # Force UI refresh
        self.refresh(layout=True)
    
    def show_loading(self) -> None:
        self.query_one("#loading").remove_class("hidden")
    
    def hide_loading(self) -> None:
        self.query_one("#loading").add_class("hidden")
    
    def execute_agent(self, request: str) -> None:
        """Execute agent on user request in background thread"""
        # Cancel any existing agent thread
        if self.current_agent_thread and self.current_agent_thread.is_alive():
            self.agent_cancel_event.set()
            self.current_agent_thread.join(0.1)
            
        self.show_loading()
        self.disable_input()
        self.agent_cancel_event = threading.Event()
        
        # Run agent in background thread with step tracking
        self.current_agent_thread = threading.Thread(target=self._run_agent, args=(request, 0, []))
        self.current_agent_thread.start()
    
    def _run_agent(self, request: str, step: int, history: list) -> None:
        """Background thread for agent processing with multi-step capability"""
        if step >= 10:  # max_steps to prevent infinite loops
            self.update_output("⚠️ Max steps reached (10). Stopping autonomous processing.", "warning")
            self.hide_loading()
            self.enable_input()
            return
            
        try:
            # Include history in request
            full_request = request
            if history:
                full_request += "\n\n### Previous Steps:\n" + "\n".join(history)
                
            start_time = time.time()
            
            # Create DSPy stream listener
            stream_listener = dspy.streaming.StreamListener(signature_field_name="plan")
            
            # Wrap agent with streaming
            stream_agent = dspy.streamify(
                self.agent,
                stream_listeners=[stream_listener]
            )
            
            # Get streaming response
            response = stream_agent(request=full_request)
            elapsed = time.time() - start_time
            
            # Track step in history
            history.append(f"Step {step+1}:")
            history.append(f"Request: {request}")
            history.append(f"Plan: {response.plan}")
            
            self.update_output(f"⏱️ Agent response in {elapsed:.2f}s", "info")
            self.update_output(f"PLAN:\n{response.plan}", "info")
            
            # Execute commands
            if response.commands.strip():
                self.update_output("\n💻 EXECUTING COMMANDS:", "info")
                self.execute_commands(response.commands)
                history.append(f"Commands: {response.commands}")
            
            # Apply file edits
            if response.edits.strip():
                self.update_output("\n📝 APPLYING EDITS:", "info")
                self.apply_edits(response.edits)
                history.append(f"Edits: {response.edits}")
            
            # Check if done
            if "DONE" in response.done:
                self.update_output("\n✅ TASK COMPLETE", "success")
                self.hide_loading()
                self.enable_input()
            elif "CONTINUE" in response.done:
                self.update_output("\n🔄 CONTINUING AUTONOMOUSLY", "info")
                # Continue processing with updated context
                self._run_agent(request, step+1, history)
            else:
                self.update_output("\n🔄 UNKNOWN STATE, CONTINUING WITH USER INPUT", "warning")
                self.hide_loading()
                self.enable_input()
                
        except Exception as e:
            self.update_output(f"❌ Error: {str(e)}", "error")
            self.hide_loading()
            self.enable_input()
    
    def execute_commands(self, commands: str) -> None:
        """Execute shell commands including Firebase searches"""
        for command in commands.splitlines():
            if not command.strip():
                continue
                
            if command.startswith("firebase:"):
                self.update_output(f"🔍 Firebase search: {command[9:]}", "info")
                try:
                    # In a real implementation, this would call Firebase SDK
                    # For demo purposes, we'll simulate a search
                    result = f"Firebase results for '{command[9:]}':\n- Result 1\n- Result 2"
                    self.update_output(result)
                except Exception as e:
                    self.update_output(f"Firebase error: {str(e)}", "error")
            else:
                self.update_output(f"$ {command}", "info")
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
                        self.update_output(result.stderr, "error")
                except Exception as e:
                    self.update_output(f"Command error: {str(e)}", "error")
    
    def apply_edits(self, edits: str) -> None:
        """Apply SEARCH/REPLACE edits to files"""
        pattern = r"```(\w+)?\n([\s\S]*?)<<<<<<< SEARCH\n([\s\S]*?)=======\n([\s\S]*?)>>>>>>> REPLACE\n```"
        
        for match in re.finditer(pattern, edits):
            file_path = match.group(2).strip()
            search_content = match.group(3)
            replace_content = match.group(4)
            
            self.update_output(f"✏️ Editing {file_path}", "info")
            
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                
                if search_content in content:
                    new_content = content.replace(search_content, replace_content, 1)
                    with open(file_path, "w") as f:
                        f.write(new_content)
                    self.update_output(f"✅ Applied changes to {file_path}", "success")
                else:
                    self.update_output(f"⚠️ Search content not found in {file_path}", "warning")
            
            except Exception as e:
                self.update_output(f"Error editing {file_path}: {str(e)}", "error")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "execute-btn":
            self.process_request()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.process_request()
    
    def disable_input(self):
        self.query_one("#request-input").disabled = True
        self.query_one("#execute-btn").disabled = True

    def enable_input(self):
        self.query_one("#request-input").disabled = False
        self.query_one("#execute-btn").disabled = False

    def process_request(self) -> None:
        request_input = self.query_one("#request-input")
        request = request_input.value.strip()
        request_input.value = ""
        
        # Set focus back to input immediately
        self.set_focus(request_input)
        
        if request.lower() == "/exit":
            self.exit()
            return
        
        if request:
            self.execute_agent(request)

if __name__ == "__main__":
    app = CodingAgentREPL()
    app.run()
