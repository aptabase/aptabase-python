# Aptabase Python SDK

Python SDK for [Aptabase](https://aptabase.com/) - privacy-first analytics for mobile, desktop and web applications.

## Features

- 🚀 **Fully async** - Built with `httpx` and `asyncio`
- 🔒 **Privacy-first** - No personal data collection
- 🏃 **Modern Python** - Requires Python 3.11+
- 🔄 **Auto-batching** - Efficient event batching and flushing
- ⚡ **Lightweight** - Minimal dependencies

## Installation

```bash
uv add aptabase
# or
pip install aptabase
```

## Quick Start

```python
import asyncio
from aptabase import Aptabase

async def main():
    async with Aptabase("A-EU-1234567890") as client:
        # Track a simple event
        await client.track("app_started")

        # Track an event with properties
        await client.track("user_action", {
            "action": "button_click",
            "button_id": "login",
            "screen": "home"
        })

        # Events are automatically flushed, but you can force it
        await client.flush()

asyncio.run(main())
```

## Configuration

```python
client = Aptabase(
    app_key="A-EU-1234567890",          # Your Aptabase app key
    app_version="1.2.3",                # Your app version
    is_debug=False,                     # Enable debug mode
    max_batch_size=25,                  # Max events per batch (max 25)
    flush_interval=10.0,                # Auto-flush interval in seconds
    timeout=30.0                        # HTTP timeout in seconds
)
```

## App Key Format

Your app key determines the server region:
- `A-EU-*` - European servers
- `A-US-*` - US servers

Get your app key from the [Aptabase dashboard](https://aptabase.com/).

## Event Tracking

### Simple Events

```python
await client.track("page_view")
```

### Events with Properties

```python
await client.track("purchase", {
    "product_id": "abc123",
    "price": 29.99,
    "currency": "USD"
})
```

## Lifecycle

### Context Manager

```python
async with Aptabase("A-EU-1234567890") as client:
    await client.track("event")
    # Automatically handles start/stop and flushing
```

### Manual Lifecycle

```python
client = Aptabase("A-EU-1234567890")
await client.start()
try:
    await client.track("event")
finally:
    await client.stop()  # Ensures all events are flushed
```

## Error Handling

```python
from aptabase import Aptabase, AptabaseError, NetworkError

try:
    async with Aptabase("A-EU-1234567890") as client:
        await client.track("event")
except NetworkError as e:
    print(f"Network error: {e}, status: {e.status_code}")
except AptabaseError as e:
    print(f"Aptabase error: {e}")
```

## Development

Install development dependencies:

```bash
uv sync --dev
```

Run tests:

```bash
uv run pytest
```

Code formatting:

```bash
uv run ruff check .
```

Type checking:

```bash
uv run mypy .
```

## License

MIT License - see [LICENSE](LICENSE) file for details.