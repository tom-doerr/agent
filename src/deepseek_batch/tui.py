from __future__ import annotations

def main() -> None:
    # Import Textual only when invoked; keeps install light and tests offline.
    from textual.app import App, ComposeResult
    from textual.widgets import Input, Button, Static
    from rich.text import Text
    import threading
    from . import batch_best

    class UI(App):
        CSS = """
        Screen { align: center middle; }
        #box { width: 80%; height: auto; border: round $accent; padding: 1; }
        #out { height: auto; margin-top: 1; }
        #title { color: cyan; }
        """

        def compose(self) -> ComposeResult:
            yield Static("DeepSeek Best-of-N", id="title")
            yield Input(placeholder="Type your prompt and press Enter", id="inp")
            yield Button("Run", id="run")
            yield Static("", id="out")

        def on_button_pressed(self, event) -> None:  # type: ignore[override]
            self._kick()

        def on_input_submitted(self, event) -> None:  # type: ignore[override]
            self._kick()

        def _kick(self) -> None:
            inp = self.query_one("#inp", Input).value.strip()
            if not inp:
                return
            self.query_one("#out", Static).update(Text("…running…", style="yellow"))

            def worker():
                try:
                    out = batch_best(inp)
                    render = Text("BEST: ", style="cyan") + Text(out, style="bold green")
                except Exception as e:  # minimal surfacing, no fallbacks
                    render = Text(f"error: {e}", style="bold red")
                self.call_from_thread(self.query_one("#out", Static).update, render)

            threading.Thread(target=worker, daemon=True).start()

    UI().run()

if __name__ == "__main__":
    main()
