# Simple Counter - Textual + Aptabase

A minimal example demonstrating how to integrate [Aptabase](https://aptabase.com/) analytics into a [Textual](https://textual.textualize.io/) TUI application.

Perfect for learning the basics of adding privacy-first analytics to your terminal apps!

## 🎯 What It Does

This is a simple counter app that:
- Increments a counter when you click a button
- Resets the counter to zero
- Tracks all interactions with Aptabase analytics
- Shows notifications for user feedback

## 📸 Features

- **Clean UI**: Centered layout with large counter display
- **Two Buttons**: 
  - "Click Me!" - Increments the counter
  - "Reset" - Resets to zero
- **Analytics Tracking**:
  - App start/stop events
  - Button clicks with counter values
  - Reset actions with previous count
  - Session duration

## 🚀 Quick Start

### Installation

#### Using uv (recommended)

```bash
# Install dependencies
uv pip install textual aptabase

# Run the app
uv run counter.py
```

#### Using pip

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install textual aptabase

# Run the app
python counter.py
```

#### Using pyproject.toml

```bash
# If you have the pyproject.toml file
uv sync
uv run counter
```

## ⚙️ Configuration

Before running, you need to set your Aptabase app key:

1. Sign up at [aptabase.com](https://aptabase.com/)
2. Create a new app
3. Copy your app key (format: `A-EU-XXXXXXXXXX` or `A-US-XXXXXXXXXX`)
4. Update the key in `counter.py`:

```python
# Replace with your actual Aptabase app key
app = CounterApp(app_key="A-EU-XXXXXXXXXX")
```

## 📊 Tracked Events

The app automatically tracks:

### 1. **app_started**
Sent when the app launches.

```python
{
  "event": "app_started"
}
```

### 2. **button_clicked**
Sent when "Click Me!" is pressed.

```python
{
  "event": "button_clicked",
  "action": "increment",
  "count": 5  # Current counter value
}
```

### 3. **counter_reset**
Sent when "Reset" is pressed.

```python
{
  "event": "counter_reset",
  "previous_count": 10  # Value before reset
}
```

### 4. **app_closed**
Sent when the app exits.

```python
{
  "event": "app_closed",
  "final_count": 7  # Final counter value
}
```

## 🎮 Usage

1. **Start the app**: Run `python main.py`
2. **Click the button**: Press "Click Me!" to increment (or press `Enter` when focused)
3. **Reset**: Click "Reset" to set counter back to zero
4. **Quit**: Press `q` or `Ctrl+C`

## 💻 Code Structure

```python
class CounterApp(App):
    def __init__(self, app_key: str):
        # Initialize with your Aptabase key
        
    async def on_mount(self):
        # Start Aptabase when app starts
        
    async def on_unmount(self):
        # Stop Aptabase and send final events
        
    async def on_button_pressed(self, event):
        # Handle button clicks and track events
```

### Key Components

**Aptabase Initialization:**
```python
self.aptabase = Aptabase(
    app_key=self.app_key,
    app_version="1.0.0",
    is_debug=True  # Shows debug info
)
await self.aptabase.start()
```

**Tracking Events:**
```python
await self.aptabase.track("button_clicked", {
    "action": "increment",
    "count": self.counter
})
```

**Cleanup:**
```python
await self.aptabase.stop()  # Flushes pending events
```

## 🔧 Customization Ideas

Here are some ways to extend this app:

### Add More Buttons
```python
yield Button("Increment by 5", id="btn-plus5")
yield Button("Decrement", id="btn-decrement")
```

### Track Time Between Clicks
```python
import time

self.last_click = time.time()

# In button handler
time_since_last = time.time() - self.last_click
await self.aptabase.track("button_clicked", {
    "count": self.counter,
    "time_since_last_click": round(time_since_last, 2)
})
```

### Add Keyboard Shortcuts
```python
BINDINGS = [
    Binding("space", "increment", "Increment"),
    Binding("r", "reset", "Reset"),
]

async def action_increment(self):
    self.counter += 1
    await self.aptabase.track("keyboard_increment")
```

### Save High Score
```python
self.high_score = 0

if self.counter > self.high_score:
    self.high_score = self.counter
    await self.aptabase.track("new_high_score", {
        "score": self.high_score
    })
```

## 🐛 Troubleshooting

### "Analytics unavailable" message

**Cause**: Invalid app key or network issues.

**Solutions**:
1. Check your app key format: Must be `A-EU-*` or `A-US-*`
2. Verify network connectivity
3. Check Aptabase dashboard status
4. Look for error details in the console

### Import errors

```bash
ModuleNotFoundError: No module named 'textual'
```

**Solution**: Install dependencies
```bash
pip install textual aptabase
```

### App won't start

**Check Python version**:
```bash
python --version  # Must be 3.11+
```

### Events don't show

Make sure to check the Debug-mode dashboard (not Release-mode)

## 📚 Learn More

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

---

Built with ❤️ using [Textual](https://textual.textualize.io/) and [Aptabase](https://aptabase.com/)