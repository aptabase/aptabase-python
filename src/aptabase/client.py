"""Async Aptabase client implementation."""

from __future__ import annotations

import asyncio
import logging
from typing import Any
from urllib.parse import urljoin

import httpx

from .exceptions import ConfigurationError, NetworkError, ValidationError
from .models import Event, SystemProperties

logger = logging.getLogger(__name__)


class Aptabase:
    """Aptabase analytics client."""

    def __init__(
        self,
        app_key: str,
        *,
        app_version: str = "1.0.0",
        is_debug: bool = False,
        max_batch_size: int = 25,
        flush_interval: float = 10.0,
        timeout: float = 30.0,
    ) -> None:
        """
        Initialize the Aptabase client.

        Args:
            app_key: Your Aptabase app key (format: A-{REGION}-{ID})
            app_version: Version of your application
            is_debug: Whether to enable debug mode
            max_batch_size: Maximum number of events to batch (max 25)
            flush_interval: Interval in seconds to flush events
            timeout: HTTP request timeout in seconds
        """
        if not app_key or not isinstance(app_key, str):
            raise ConfigurationError("App key is required and must be a string")

        if not app_key.startswith(("A-EU-", "A-US-")):
            raise ConfigurationError(
                "Invalid app key format. Expected format: A-{REGION}-{ID}"
            )

        if max_batch_size > 25:
            raise ConfigurationError("Maximum batch size is 25 events")

        self._app_key = app_key
        self._base_url = self._get_base_url(app_key)
        self._system_props = SystemProperties(
            app_version=app_version,
            is_debug=is_debug,
        )
        self._max_batch_size = max_batch_size
        self._flush_interval = flush_interval
        self._timeout = timeout

        self._event_queue: list[Event] = []
        self._queue_lock = asyncio.Lock()
        self._client: httpx.AsyncClient | None = None
        self._flush_task: asyncio.Task | None = None
        self._session_id: str | None = None

    def _get_base_url(self, app_key: str) -> str:
        """Determine the base URL from the app key."""
        if app_key.startswith("A-EU-"):
            return "https://api-eu.aptabase.com/"
        elif app_key.startswith("A-US-"):
            return "https://api.aptabase.com/"
        else:
            raise ConfigurationError("Invalid app key region")

    async def __aenter__(self) -> Aptabase:
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.stop()

    async def start(self) -> None:
        """Start the client and begin periodic flushing."""
        if self._client is not None:
            return

        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self._timeout),
            headers={
                "App-Key": self._app_key,
                "Content-Type": "application/json",
            },
        )

        # Start the periodic flush task
        self._flush_task = asyncio.create_task(self._periodic_flush())

    async def stop(self) -> None:
        """Stop the client and flush any remaining events."""
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        # Flush any remaining events
        await self.flush()

        if self._client:
            await self._client.aclose()
            self._client = None

    async def track(
        self,
        event_name: str,
        props: dict[str, Any] | None = None,
        *,
        session_id: str | None = None,
    ) -> None:
        """
        Track an analytics event.

        Args:
            event_name: Name of the event to track
            props: Optional event properties
            session_id: Optional session ID (generated automatically if not provided)
        """
        if not event_name or not isinstance(event_name, str):
            raise ValidationError("Event name is required and must be a string")

        if props is not None and not isinstance(props, dict):
            raise ValidationError("Event properties must be a dictionary")

        event = Event(
            name=event_name,
            props=props,
            session_id=session_id or self._session_id,
        )

        async with self._queue_lock:
            self._event_queue.append(event)

            # Auto-flush if we reach the batch size
            if len(self._event_queue) >= self._max_batch_size:
                await self._flush_events()

    async def flush(self) -> None:
        """Manually flush all queued events."""
        async with self._queue_lock:
            await self._flush_events()

    async def _flush_events(self) -> None:
        """Internal method to flush events (must be called with lock held)."""
        if not self._event_queue or not self._client:
            return

        events_to_send = self._event_queue[: self._max_batch_size]
        self._event_queue = self._event_queue[self._max_batch_size :]

        try:
            await self._send_events(events_to_send)
        except Exception as e:
            logger.error(f"Failed to send events: {e}")
            # Re-add events to the front of the queue for retry
            self._event_queue = events_to_send + self._event_queue

    async def _send_events(self, events: list[Event]) -> None:
        """Send events to the Aptabase API."""
        if not events:
            return

        payload = [event.to_dict(self._system_props) for event in events]
        url = urljoin(self._base_url, "api/v0/events")

        try:
            response = await self._client.post(url, json=payload)
            response.raise_for_status()
            logger.debug(f"Successfully sent {len(events)} events")
        except httpx.HTTPStatusError as e:
            raise NetworkError(
                f"HTTP error {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {str(e)}") from e

    async def _periodic_flush(self) -> None:
        """Periodically flush events."""
        try:
            while True:
                await asyncio.sleep(self._flush_interval)
                await self.flush()
        except asyncio.CancelledError:
            pass

    def set_session_id(self, session_id: str) -> None:
        """Set the session ID for future events."""
        if not session_id or not isinstance(session_id, str):
            raise ValidationError("Session ID must be a non-empty string")
        self._session_id = session_id
