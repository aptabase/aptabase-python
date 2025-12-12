#!/usr/bin/env python3
"""Example usage of the Aptabase Python SDK."""

import asyncio
import logging

from aptabase import Aptabase, AptabaseError

# Enable logging to see what's happening
logging.basicConfig(level=logging.DEBUG)


async def main():
    """Example demonstrating various SDK features."""

    # Replace with your actual app key
    app_key = "A-EU-0000000000"  # This is a fake key for demo purposes

    try:
        # Method 1: Using context manager (recommended)
        print("🚀 Starting Aptabase example...")

        async with Aptabase(
            app_key=app_key,
            app_version="1.0.0",
            is_debug=True,
            max_batch_size=10,
            flush_interval=5.0,
        ) as client:
            # Track simple events
            await client.track("app_started")
            await client.track("example_run")

            # Track events with properties
            await client.track(
                "user_action",
                {
                    "action": "button_click",
                    "button_id": "demo_button",
                    "screen": "main",
                    "timestamp": "2023-12-12T10:00:00Z",
                },
            )

            await client.track(
                "feature_used",
                {"feature": "analytics", "user_type": "developer", "success": True},
            )

            # Set a custom session ID
            client.set_session_id("demo-session-123")

            await client.track("session_event", {"event_type": "demo", "duration": 120})

            # Track multiple events quickly
            for i in range(5):
                await client.track(
                    "batch_event", {"batch_number": i, "data": f"item_{i}"}
                )

            # Manual flush (optional - happens automatically)
            print("📤 Flushing events...")
            await client.flush()

            # Wait a bit to see periodic flushing in action
            await asyncio.sleep(2)

            await client.track("final_event", {"status": "completed"})

        print("✅ Example completed successfully!")

    except AptabaseError as e:
        print(f"❌ Aptabase error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def manual_lifecycle_example():
    """Example showing manual client lifecycle management."""
    print("\n🔧 Manual lifecycle example...")

    client = Aptabase("A-EU-0000000000", app_version="1.0.0")

    try:
        await client.start()
        await client.track("manual_start")
        await client.track("manual_event", {"method": "manual"})
        print("📤 Manually flushing...")
        await client.flush()
    finally:
        await client.stop()

    print("✅ Manual lifecycle example completed!")


if __name__ == "__main__":
    print("Aptabase Python SDK Example")
    print("=" * 40)

    # Run the examples
    asyncio.run(main())
    asyncio.run(manual_lifecycle_example())
