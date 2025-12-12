"""
Textual Dashboard Demo with Aptabase Analytics

A sample application demonstrating how to integrate Aptabase tracking
into a Textual TUI application.
"""

from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    Header,
    Footer,
    Static,
    Input,
    Label,
    DataTable,
    TabbedContent,
    TabPane,
)
from textual.binding import Binding
from aptabase import Aptabase, AptabaseError


class StatsWidget(Static):
    """Widget to display app statistics"""

    def __init__(self) -> None:
        super().__init__()
        self.clicks = 0
        self.inputs = 0
        self.tab_switches = 0

    def update_stats(self, clicks: int, inputs: int, tabs: int) -> None:
        self.clicks = clicks
        self.inputs = inputs
        self.tab_switches = tabs
        self.update(self.render())

    def render(self) -> str:
        return f"""[bold cyan]Session Statistics[/bold cyan]
━━━━━━━━━━━━━━━━━━━━━━━━
Button Clicks: [green]{self.clicks}[/green]
Form Inputs: [yellow]{self.inputs}[/yellow]
Tab Switches: [magenta]{self.tab_switches}[/magenta]
"""


class EventLogWidget(Static):
    """Widget to display recent events"""

    def __init__(self) -> None:
        super().__init__()
        self.events: list[str] = []
        self.max_events = 8

    def add_event(self, event: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.events.insert(0, f"[dim]{timestamp}[/dim] {event}")
        if len(self.events) > self.max_events:
            self.events.pop()
        self.update(self.render())

    def render(self) -> str:
        header = "[bold cyan]Recent Events[/bold cyan]\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
        if not self.events:
            return header + "[dim]No events yet...[/dim]"
        return header + "\n".join(self.events)


class DashboardApp(App):
    """A Textual dashboard app with Aptabase analytics"""

    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        height: 100%;
        padding: 1 2;
    }

    #content-area {
        height: 1fr;
    }

    #sidebar {
        width: 35;
        height: 100%;
        border: solid $primary;
        padding: 1;
    }

    #main-content {
        width: 1fr;
        height: 100%;
        margin-left: 1;
    }

    .card {
        border: solid $accent;
        padding: 1 2;
        margin-bottom: 1;
        height: auto;
    }

    Button {
        margin: 1 2;
        min-width: 20;
    }

    Input {
        margin: 0 2 1 2;
    }

    DataTable {
        height: 1fr;
        margin: 1 2;
    }

    Label {
        padding: 0 2;
        color: $text-muted;
    }

    StatsWidget {
        height: 10;
        margin-bottom: 1;
    }

    EventLogWidget {
        height: 1fr;
    }

    TabbedContent {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("d", "toggle_dark", "Toggle Dark Mode"),
        Binding("r", "reset_stats", "Reset Stats"),
    ]

    def __init__(self, app_key: str = "A-EU-0000000000"):
        super().__init__()
        self.app_key = app_key
        self.aptabase: Aptabase | None = None
        self.stats = {"clicks": 0, "inputs": 0, "tabs": 0}
        self.session_start = datetime.now()

    async def on_mount(self) -> None:
        """Initialize Aptabase when the app starts"""
        try:
            # Initialize Aptabase with async context
            self.aptabase = Aptabase(
                app_key=self.app_key,
                app_version="1.0.0",
                is_debug=True,
                max_batch_size=25,
                flush_interval=10.0,
            )
            await self.aptabase.start()

            # Track app start
            await self.track_event("app_started", {
                "platform": "textual",
                "theme": "dark" if self.dark else "light"
            })

            # Update event log
            event_log = self.query_one(EventLogWidget)
            event_log.add_event("✅ [green]Aptabase connected[/green]")

        except Exception as e:
            self.notify(f"Analytics initialization failed: {e}", severity="warning")
            event_log = self.query_one(EventLogWidget)
            event_log.add_event("⚠️ [yellow]Aptabase unavailable[/yellow]")

    async def on_unmount(self) -> None:
        """Cleanup Aptabase when the app closes"""
        if self.aptabase:
            try:
                # Track session end with summary
                session_duration = (datetime.now() - self.session_start).total_seconds()
                await self.track_event("app_closed", {
                    "session_duration": round(session_duration, 2),
                    "total_clicks": self.stats["clicks"],
                    "total_inputs": self.stats["inputs"],
                    "total_tab_switches": self.stats["tabs"]
                })

                await self.aptabase.stop()
            except Exception as e:
                self.log(f"Error stopping Aptabase: {e}")

    def compose(self) -> ComposeResult:
        """Create the UI layout"""
        yield Header()

        with Container(id="main-container"):
            with Horizontal(id="content-area"):
                # Sidebar with stats and event log
                with Vertical(id="sidebar"):
                    yield StatsWidget()
                    yield EventLogWidget()

                # Main content area with tabs
                with Vertical(id="main-content"):
                    with TabbedContent():
                        with TabPane("Dashboard", id="tab-dashboard"):
                            yield Static(
                                "[bold]Welcome to Textual + Aptabase Demo![/bold]\n\n"
                                "This app demonstrates analytics tracking in a TUI.",
                                classes="card"
                            )
                            with Horizontal():
                                yield Button("Click Me! 🎯", id="btn-track", variant="primary")
                                yield Button("Success ✅", id="btn-success", variant="success")
                                yield Button("Warning ⚠️", id="btn-warning", variant="warning")

                        with TabPane("Form", id="tab-form"):
                            yield Label("Enter some data to track form interactions:")
                            yield Input(placeholder="Your name", id="input-name")
                            yield Input(placeholder="Your email", id="input-email")
                            yield Button("Submit Form", id="btn-submit", variant="primary")

                        with TabPane("Data Table", id="tab-table"):
                            table = DataTable()
                            table.add_columns("ID", "Action", "Timestamp")
                            yield table

        yield Footer()

    async def track_event(self, event_name: str, properties: dict | None = None) -> None:
        """Helper method to track events with Aptabase"""
        if self.aptabase:
            try:
                await self.aptabase.track(event_name, properties or {})
                
                # Update event log
                event_log = self.query_one(EventLogWidget)
                props_str = f" ({list(properties.keys())})" if properties else ""
                event_log.add_event(f"📊 Tracked: [cyan]{event_name}[/cyan]{props_str}")
                
            except AptabaseError as e:
                self.log(f"Error tracking event: {e}")

    def update_stats_display(self) -> None:
        """Update the stats widget"""
        stats_widget = self.query_one(StatsWidget)
        stats_widget.update_stats(
            self.stats["clicks"],
            self.stats["inputs"],
            self.stats["tabs"]
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        self.stats["clicks"] += 1
        self.update_stats_display()

        # Track different button types
        if button_id == "btn-track":
            await self.track_event("button_clicked", {
                "button_id": button_id,
                "button_text": "Click Me",
                "total_clicks": self.stats["clicks"]
            })
            self.notify("Button clicked! Event tracked. 🎯")

        elif button_id == "btn-success":
            await self.track_event("button_clicked", {
                "button_id": button_id,
                "variant": "success"
            })
            self.notify("Success action tracked! ✅", severity="information")

        elif button_id == "btn-warning":
            await self.track_event("button_clicked", {
                "button_id": button_id,
                "variant": "warning"
            })
            self.notify("Warning action tracked! ⚠️", severity="warning")

        elif button_id == "btn-submit":
            name_input = self.query_one("#input-name", Input)
            email_input = self.query_one("#input-email", Input)

            await self.track_event("form_submitted", {
                "has_name": bool(name_input.value),
                "has_email": bool(email_input.value),
                "name_length": len(name_input.value),
                "email_length": len(email_input.value)
            })

            # Add to data table
            table = self.query_one(DataTable)
            row_id = len(table.rows) + 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            table.add_row(str(row_id), "Form Submit", timestamp)

            self.notify(f"Form submitted! Data: {name_input.value or 'N/A'}", severity="information")

            # Clear inputs
            name_input.value = ""
            email_input.value = ""

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Track input field changes"""
        if event.value:  # Only track when there's content
            self.stats["inputs"] += 1
            self.update_stats_display()

            await self.track_event("input_changed", {
                "input_id": event.input.id,
                "value_length": len(event.value),
                "has_content": bool(event.value)
            })

    async def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Track tab switches"""
        self.stats["tabs"] += 1
        self.update_stats_display()

        await self.track_event("tab_switched", {
            "tab_id": event.pane.id,
            "tab_title": event.pane.title if hasattr(event.pane, 'title') else str(event.pane.id),
            "total_switches": self.stats["tabs"]
        })

    async def action_toggle_dark(self) -> None:
        """Toggle dark mode and track the action"""
        self.dark = not self.dark

        await self.track_event("theme_toggled", {
            "new_theme": "dark" if self.dark else "light"
        })

        self.notify(f"Switched to {'dark' if self.dark else 'light'} mode")

    async def action_reset_stats(self) -> None:
        """Reset statistics"""
        old_stats = self.stats.copy()
        self.stats = {"clicks": 0, "inputs": 0, "tabs": 0}
        self.update_stats_display()

        await self.track_event("stats_reset", {
            "previous_clicks": old_stats["clicks"],
            "previous_inputs": old_stats["inputs"],
            "previous_tabs": old_stats["tabs"]
        })

        self.notify("Statistics reset! 🔄")

    async def action_quit(self) -> None:
        """Quit the application"""
        await self.track_event("app_quit_requested", {
            "method": "keyboard_shortcut"
        })
        self.exit()


def main():
    """Run the dashboard app"""
    # Replace with your actual Aptabase app key
    # Format: A-EU-XXXXXXXXXX or A-US-XXXXXXXXXX
    APP_KEY = "A-EU-0000000000"  # Demo key - replace with yours!

    app = DashboardApp(app_key=APP_KEY)
    app.run()


if __name__ == "__main__":
    main()