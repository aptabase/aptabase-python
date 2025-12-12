# Advanced Dashboard - Textual + Aptabase Demo App

A demonstration of integrating [Aptabase](https://aptabase.com/) analytics into a [Textual](https://textual.textualize.io/) TUI application.

## Features

This sample app demonstrates tracking various user interactions:

- 🎯 **Button clicks** - Track different button types and actions
- 📝 **Form inputs** - Monitor user input changes and submissions
- 🔀 **Tab navigation** - Track tab switches and navigation patterns
- 🎨 **Theme changes** - Monitor dark/light mode toggles
- 📊 **Session analytics** - Track app lifecycle and session duration
- 📈 **Real-time stats** - Display live statistics in the sidebar
- 📜 **Event log** - View recent tracked events

## Screenshots

The app includes:
- **Dashboard tab**: Interactive buttons with different variants
- **Form tab**: Input fields with submission tracking
- **Data Table tab**: Log of form submissions
- **Sidebar**: Real-time statistics and event log

## Installation

### Using uv (recommended)

```bash
# Add dependencies
uv add textual aptabase

# Run the app
uv run main.py
```

### Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install 

# Run the app
python main.py
```

## Configuration

Before running, update the `APP_KEY` in `main.py`:

```python
# Replace with your actual Aptabase app key
APP_KEY = "A-EU-XXXXXXXXXX"  # or A-US-XXXXXXXXXX
```

Get your app key from the [Aptabase dashboard](https://aptabase.com/).

## Usage

### Running the App

```bash
python main.py
```

### Keyboard Shortcuts

- `q` - Quit the application
- `d` - Toggle dark/light mode
- `r` - Reset statistics

### Tracked Events

The app tracks the following events:

1. **app_started** - When the app launches
   - Properties: `platform`, `theme`

2. **button_clicked** - When any button is pressed
   - Properties: `button_id`, `button_text`, `variant`, `total_clicks`

3. **input_changed** - When input fields are modified
   - Properties: `input_id`, `value_length`, `has_content`

4. **form_submitted** - When the form is submitted
   - Properties: `has_name`, `has_email`, `name_length`, `email_length`

5. **tab_switched** - When switching between tabs
   - Properties: `tab_id`, `tab_title`, `total_switches`

6. **theme_toggled** - When dark/light mode is changed
   - Properties: `new_theme`

7. **stats_reset** - When statistics are reset
   - Properties: `previous_clicks`, `previous_inputs`, `previous_tabs`

8. **app_closed** - When the app exits
   - Properties: `session_duration`, `total_clicks`, `total_inputs`, `total_tab_switches`

## Code Structure

```python
# Initialize Aptabase
self.aptabase = Aptabase(
    app_key=self.app_key,
    app_version="1.0.0",
    is_debug=True,
    max_batch_size=25,
    flush_interval=10.0,
)

# Track an event
await self.track_event("button_clicked", {
    "button_id": "my_button",
    "total_clicks": 5
})
```

## Key Implementation Details

### Async Context Management

The app properly manages Aptabase lifecycle:

```python
async def on_mount(self) -> None:
    """Initialize Aptabase when the app starts"""
    self.aptabase = Aptabase(...)
    await self.aptabase.start()

async def on_unmount(self) -> None:
    """Cleanup Aptabase when the app closes"""
    await self.aptabase.stop()
```

### Event Tracking Helper

A helper method simplifies event tracking throughout the app:

```python
async def track_event(self, event_name: str, properties: dict | None = None) -> None:
    """Helper method to track events with Aptabase"""
    if self.aptabase:
        await self.aptabase.track(event_name, properties or {})
```

### Real-time UI Updates

The app provides visual feedback for tracked events:

- Stats widget shows cumulative counts
- Event log displays recent events with timestamps
- Notifications confirm actions

## Extending the App

### Adding New Tracked Events

1. Create an async method to handle the event:

```python
async def on_custom_action(self, event) -> None:
    await self.track_event("custom_action", {
        "action_type": "something",
        "value": event.value
    })
```

2. Update the stats and UI as needed:

```python
self.stats["custom"] += 1
self.update_stats_display()
```

### Adding New Widgets

The app uses a flexible layout with sidebar and main content area. Add new widgets in the `compose()` method:

```python
with TabPane("New Tab", id="tab-new"):
    yield YourCustomWidget()
```

## Privacy Considerations

Aptabase is privacy-first analytics:

- No personal data is collected
- No IP addresses stored
- No cookies or tracking scripts
- GDPR compliant

This demo tracks only:
- Interaction counts and types
- Session duration
- UI navigation patterns
- Non-sensitive form metadata (lengths, not content)

## Troubleshooting

### Aptabase Connection Issues

If you see "Aptabase unavailable" in the event log:

1. Check your app key format: `A-EU-*` or `A-US-*`
2. Verify network connectivity
3. Check the Aptabase dashboard for service status
4. Review the console logs for detailed error messages

### Import Errors

If you get import errors:

```bash
# Ensure all dependencies are installed
pip install

# Or with uv
uv sync
```

## Resources

- [Aptabase Documentation](https://aptabase.com/docs)
- [Textual Documentation](https://textual.textualize.io/)
- [Aptabase Python SDK](https://github.com/aptabase/aptabase-python)

## License

MIT License - feel free to use this as a starting point for your own projects!

## Contributing

This is a demo app. Feel free to fork and modify for your needs!

## Questions?

- Aptabase: [https://aptabase.com/](https://aptabase.com/)
- Textual: [https://textual.textualize.io/](https://textual.textualize.io/)