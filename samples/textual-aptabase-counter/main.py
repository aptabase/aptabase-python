"""
Minimal Textual + Aptabase Example

A simple counter app that tracks button clicks.
"""

from textual.app import App, ComposeResult
from textual.containers import Center
from textual.widgets import Button, Header, Footer, Static
from aptabase import Aptabase


class CounterApp(App):
    """A simple counter app with analytics"""

    CSS = """
    Screen {
        align: center middle;
    }

    #counter {
        width: 40;
        height: 10;
        content-align: center middle;
        border: solid green;
        margin: 1;
    }

    Button {
        margin: 1 2;
    }
    """

    def __init__(self, app_key: str = "A-EU-0000000000"):
        super().__init__()
        self.app_key = app_key
        self.aptabase: Aptabase | None = None
        self.counter = 0

    async def on_mount(self) -> None:
        """Initialize Aptabase"""
        try:
            self.aptabase = Aptabase(
                app_key=self.app_key,
                app_version="1.0.0",
                is_debug=True
            )
            await self.aptabase.start()
            await self.aptabase.track("app_started")
            self.notify("Analytics connected! ✅")
        except Exception as e:
            self.notify(f"Analytics unavailable: {e}", severity="warning")

    async def on_unmount(self) -> None:
        """Cleanup Aptabase"""
        if self.aptabase:
            await self.aptabase.track("app_closed", {"final_count": self.counter})
            await self.aptabase.stop()

    def compose(self) -> ComposeResult:
        """Create the UI"""
        yield Header()
        with Center():
            yield Static(f"[bold cyan]Count: {self.counter}[/bold cyan]", id="counter")
            yield Button("Click Me!", id="btn-increment", variant="primary")
            yield Button("Reset", id="btn-reset", variant="warning")
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "btn-increment":
            self.counter += 1
            if self.aptabase:
                await self.aptabase.track("button_clicked", {
                    "action": "increment",
                    "count": self.counter
                })
        elif event.button.id == "btn-reset":
            old_count = self.counter
            self.counter = 0
            if self.aptabase:
                await self.aptabase.track("counter_reset", {
                    "previous_count": old_count
                })

        # Update the counter display
        counter_widget = self.query_one("#counter", Static)
        counter_widget.update(f"[bold cyan]Count: {self.counter}[/bold cyan]")


if __name__ == "__main__":
    # Replace with your Aptabase app key
    app = CounterApp(app_key="A-EU-0000000000")
    app.run()