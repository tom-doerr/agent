#!/usr/bin/env python3

from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Header, Footer, Input, Button, Static
from textual.reactive import reactive
from simpledspy import predict, configure
from model_map import MODEL_MAP
import asyncio
import threading

class InteractiveChat(App):
    """Interactive chat with async LLM responses."""
    CSS = """
    Screen {
        layout: vertical;
    }
    #output-container {
        height: 85%;
        border: solid $accent;
        padding: 1;
        overflow: auto;
    }
    #input-container {
        height: 15%;
        layout: horizontal;
    }
    #input-field {
        width: 70%;
    }
    #send-button {
        width: 15%;
    }
    #mic-button {
        width: 15%;
    }
    .user-msg {
        color: green;
        padding: 1;
    }
    .llm-msg {
        color: blue;
        padding: 1;
    }
    .error-msg {
        color: red;
        padding: 1;
    }
    """
    
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
    ]
    
    model_name = "dv3"
    llm = None
    predict_lock = threading.Lock()
    
    def __init__(self):
        super().__init__()
        # Configure DSPy with deepseek v3
        configure(model=self.model_name)
        self.llm = MODEL_MAP.get(self.model_name, self.model_name)
        self.recording = False
        self.recognizer = None
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
        except ImportError:
            pass
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(Static("", id="output-container"))
        with Container(id="input-container"):
            yield Input(placeholder="Type your message...", id="input-field")
            yield Button("Send", id="send-button")
            yield Button("🎤", id="mic-button", classes="mic-button")
        yield Footer()
    
    def on_mount(self) -> None:
        self.query_one("#input-field", Input).focus()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        await self._process_input()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send-button":
            await self._process_input()
        elif event.button.id == "mic-button":
            await self._record_voice()
    
    async def _process_input(self) -> None:
        input_field = self.query_one(Input)
        message = input_field.value.strip()
        if not message:
            return
        
        # Clear input
        input_field.value = ""
        
        # Add user message to output
        self._add_message(f"User: {message}", "user-msg")
        
        # Process request asynchronously
        asyncio.create_task(self._handle_request(message))
    
    def _add_message(self, text: str, style_class: str = "") -> None:
        output = self.query_one("#output-container", Static)
        new_block = f"[{style_class}]{text}[/]"

        existing_content = getattr(output, "renderable", None)
        if existing_content is None:
            existing_content = getattr(output, "_message_history", "")

        if existing_content:
            combined = f"{existing_content}\n{new_block}"
        else:
            combined = new_block

        output.update(combined)
        output.scroll_end()

        # Store the combined content so legacy tests inspecting ``renderable``
        # keep working even after Textual dropped the attribute in v6.
        output._message_history = combined  # type: ignore[attr-defined]
        setattr(output, "renderable", combined)
    
    async def _handle_request(self, message: str) -> None:
        try:
            # Use lock to ensure thread-safe predict calls
            with self.predict_lock:
                response = predict(message, model=self.llm)
            self._add_message(f"LLM: {response}", "llm-msg")
        except Exception as e:
            self._add_message(f"Error processing request: {str(e)}", "error-msg")
    
    async def _record_voice(self) -> None:
        if not self.recognizer:
            self._add_message("Voice input requires SpeechRecognition and PyAudio", "error-msg")
            return
            
        self.recording = True
        self._add_message("Listening...", "info")
        
        loop = asyncio.get_event_loop()
        try:
            with sr.Microphone() as source:
                audio = await loop.run_in_executor(None, self.recognizer.listen, source, 5)
                text = await loop.run_in_executor(None, self.recognizer.recognize_google, audio)
                input_field = self.query_one("#input-field")
                input_field.value = text
                self._add_message(f"Recognized: {text}", "info")
        except Exception as e:
            self._add_message(f"Voice error: {str(e)}", "error-msg")
        finally:
            self.recording = False

if __name__ == "__main__":
    app = InteractiveChat()
    app.run()
