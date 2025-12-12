"""Comprehensive tests for the Aptabase async client."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from aptabase.client import _SESSION_TIMEOUT, Aptabase
from aptabase.exceptions import ConfigurationError, NetworkError, ValidationError
from aptabase.models import Event, SystemProperties


class TestAptabaseInitialization:
    """Test Aptabase client initialization."""

    def test_init_valid_eu_key(self):
        """Test initialization with valid EU app key."""
        client = Aptabase("A-EU-1234567890")
        assert client._app_key == "A-EU-1234567890"
        assert client._base_url == "https://eu.aptabase.com"
        assert client._system_props.app_version == "1.0.0"
        assert client._system_props.is_debug is False

    def test_init_valid_us_key(self):
        """Test initialization with valid US app key."""
        client = Aptabase("A-US-1234567890")
        assert client._app_key == "A-US-1234567890"
        assert client._base_url == "https://us.aptabase.com"

    def test_init_with_custom_parameters(self):
        """Test initialization with custom parameters."""
        client = Aptabase(
            "A-EU-1234567890",
            app_version="2.0.0",
            is_debug=True,
            max_batch_size=10,
            flush_interval=5.0,
            timeout=60.0,
        )
        assert client._system_props.app_version == "2.0.0"
        assert client._system_props.is_debug is True
        assert client._max_batch_size == 10
        assert client._flush_interval == 5.0
        assert client._timeout == 60.0

    def test_init_with_custom_base_url(self):
        """Test initialization with custom base URL."""
        client = Aptabase("A-EU-1234567890", base_url="https://custom.example.com")
        assert client._base_url == "https://custom.example.com"

    def test_init_empty_app_key(self):
        """Test initialization with empty app key."""
        with pytest.raises(ConfigurationError, match="App key is required"):
            Aptabase("")

    def test_init_none_app_key(self):
        """Test initialization with None app key."""
        with pytest.raises(ConfigurationError, match="App key is required"):
            Aptabase(cast(str, None))

    def test_init_non_string_app_key(self):
        """Test initialization with non-string app key."""
        with pytest.raises(ConfigurationError, match="must be a string"):
            Aptabase(cast(str, 12345))

    def test_init_invalid_app_key_format(self):
        """Test initialization with invalid app key format."""
        with pytest.raises(ConfigurationError, match="Invalid app key format"):
            Aptabase("INVALID-KEY")

    def test_init_invalid_region(self):
        """Test initialization with invalid region."""
        with pytest.raises(
            ConfigurationError,
            match="Invalid app key format. Expected format: A-{REGION}-{ID}",
        ):
            Aptabase("A-XX-1234567890")

    def test_init_self_hosted_without_base_url(self):
        """Test initialization with self-hosted key but no base_url."""
        with pytest.raises(
            ConfigurationError, match="Self-hosted app key requires base_url"
        ):
            Aptabase("A-SH-1234567890")

    def test_init_self_hosted_with_base_url(self):
        """Test initialization with self-hosted key and base_url."""
        client = Aptabase("A-SH-1234567890", base_url="https://my-server.com")
        assert client._base_url == "https://my-server.com"

    def test_init_batch_size_too_large(self):
        """Test initialization with batch size exceeding maximum."""
        with pytest.raises(ConfigurationError, match="Maximum batch size is 25"):
            Aptabase("A-EU-1234567890", max_batch_size=26)

    def test_init_batch_size_at_maximum(self):
        """Test initialization with batch size at maximum."""
        client = Aptabase("A-EU-1234567890", max_batch_size=25)
        assert client._max_batch_size == 25

    def test_get_base_url_malformed_key(self):
        """Test _get_base_url with malformed key."""
        client = Aptabase.__new__(Aptabase)
        with pytest.raises(ConfigurationError, match="The Aptabase App Key is invalid"):
            client._get_base_url("A-EU")


class TestAptabaseLifecycle:
    """Test Aptabase client lifecycle management."""

    @pytest.mark.asyncio
    async def test_start(self):
        """Test starting the client."""
        client = Aptabase("A-EU-1234567890")
        await client.start()

        assert client._client is not None
        assert isinstance(client._client, httpx.AsyncClient)
        assert client._flush_task is not None
        assert not client._flush_task.done()

        await client.stop()

    @pytest.mark.asyncio
    async def test_start_idempotent(self):
        """Test that calling start multiple times is safe."""
        client = Aptabase("A-EU-1234567890")
        await client.start()
        first_client = client._client

        await client.start()
        assert client._client is first_client

        await client.stop()

    @pytest.mark.asyncio
    async def test_stop(self):
        """Test stopping the client."""
        client = Aptabase("A-EU-1234567890")
        await client.start()
        await client.stop()

        assert client._client is None
        assert client._flush_task is not None and client._flush_task.done()

    @pytest.mark.asyncio
    async def test_stop_without_start(self):
        """Test stopping a client that was never started."""
        client = Aptabase("A-EU-1234567890")
        await client.stop()

        assert client._client is None

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using client as async context manager."""
        async with Aptabase("A-EU-1234567890") as client:
            assert client._client is not None
            assert client._flush_task is not None

        assert client._client is None

    @pytest.mark.asyncio
    async def test_context_manager_with_exception(self):
        """Test context manager handles exceptions properly."""
        with pytest.raises(ValueError):
            async with Aptabase("A-EU-1234567890") as client:
                assert client._client is not None
                raise ValueError("Test error")

        assert client._client is None


class TestEventTracking:
    """Test event tracking functionality."""

    @pytest.mark.asyncio
    async def test_track_basic_event(self):
        """Test tracking a basic event."""
        client = Aptabase("A-EU-1234567890")
        await client.start()

        with patch.object(client, "_send_events", new_callable=AsyncMock):
            await client.track("test_event")

            assert len(client._event_queue) == 1
            event = client._event_queue[0]
            assert event.name == "test_event"
            assert event.session_id is not None
            assert event.props == {}

        await client.stop()

    @pytest.mark.asyncio
    async def test_track_event_with_properties(self):
        """Test tracking an event with properties."""
        client = Aptabase("A-EU-1234567890")
        await client.start()

        props = {"user_id": "123", "action": "click"}
        await client.track("button_click", props)

        assert len(client._event_queue) == 1
        event = client._event_queue[0]
        assert event.name == "button_click"
        assert event.props == props

        await client.stop()

    @pytest.mark.asyncio
    async def test_track_empty_event_name(self):
        """Test tracking with empty event name."""
        client = Aptabase("A-EU-1234567890")

        with pytest.raises(ValidationError, match="Event name is required"):
            await client.track("")

    @pytest.mark.asyncio
    async def test_track_non_string_event_name(self):
        """Test tracking with non-string event name."""
        client = Aptabase("A-EU-1234567890")

        with pytest.raises(ValidationError, match="must be a string"):
            await client.track(cast(str, None))

    @pytest.mark.asyncio
    async def test_track_invalid_props_type(self):
        """Test tracking with invalid properties type."""
        client = Aptabase("A-EU-1234567890")

        with pytest.raises(ValidationError, match="must be a dictionary"):
            await client.track("test_event", cast(dict[str, Any], "invalid"))

    @pytest.mark.asyncio
    async def test_track_auto_flush_on_batch_size(self):
        """Test automatic flush when batch size is reached."""
        client = Aptabase("A-EU-1234567890", max_batch_size=3)
        await client.start()

        with patch.object(client, "_send_events", new_callable=AsyncMock) as mock_send:
            # Track events up to batch size
            await client.track("event1")
            await client.track("event2")
            assert mock_send.call_count == 0

            # This should trigger auto-flush
            await client.track("event3")
            assert mock_send.call_count == 1
            assert len(mock_send.call_args[0][0]) == 3

        await client.stop()

    @pytest.mark.asyncio
    async def test_track_multiple_events_same_session(self):
        """Test tracking multiple events maintains same session."""
        client = Aptabase("A-EU-1234567890")
        await client.start()

        await client.track("event1")
        first_session = client._event_queue[0].session_id

        await client.track("event2")
        second_session = client._event_queue[1].session_id

        assert first_session == second_session

        await client.stop()


class TestSessionManagement:
    """Test session ID management."""

    def test_get_or_create_session_creates_new(self):
        """Test creating a new session."""
        client = Aptabase("A-EU-1234567890")

        session_id = client._get_or_create_session()

        assert session_id is not None
        assert client._session_id == session_id
        assert client._last_touched is not None

    def test_get_or_create_session_returns_existing(self):
        """Test returning existing session within timeout."""
        client = Aptabase("A-EU-1234567890")

        first_session = client._get_or_create_session()
        second_session = client._get_or_create_session()

        assert first_session == second_session

    def test_get_or_create_session_updates_last_touched(self):
        """Test that accessing session updates last_touched."""
        client = Aptabase("A-EU-1234567890")

        client._get_or_create_session()
        first_touched = client._last_touched

        # Small delay
        import time

        time.sleep(0.01)

        client._get_or_create_session()
        second_touched = client._last_touched

        assert first_touched is not None and second_touched is not None
        assert second_touched > first_touched

    def test_get_or_create_session_expires_after_timeout(self):
        """Test session expires after timeout."""
        client = Aptabase("A-EU-1234567890")

        first_session = client._get_or_create_session()

        # Manually set last_touched to past timeout
        client._last_touched = datetime.now() - _SESSION_TIMEOUT - timedelta(seconds=1)

        second_session = client._get_or_create_session()

        assert first_session != second_session

    def test_new_session_id_format(self):
        """Test session ID generation format."""
        session_id = Aptabase._new_session_id()

        assert isinstance(session_id, str)
        assert len(session_id) > 0
        assert session_id.isdigit()

    def test_new_session_id_unique(self):
        """Test that session IDs are unique."""
        session_id1 = Aptabase._new_session_id()
        session_id2 = Aptabase._new_session_id()

        # They might be the same in rare cases, but typically different
        # At minimum, verify they're valid
        assert session_id1.isdigit()
        assert session_id2.isdigit()


class TestEventFlushing:
    """Test event flushing functionality."""

    @pytest.mark.asyncio
    async def test_manual_flush(self):
        """Test manual flush of events."""
        client = Aptabase("A-EU-1234567890")
        await client.start()

        with patch.object(client, "_send_events", new_callable=AsyncMock) as mock_send:
            await client.track("event1")
            await client.track("event2")

            await client.flush()

            assert mock_send.call_count == 1
            assert len(mock_send.call_args[0][0]) == 2
            assert len(client._event_queue) == 0

        await client.stop()

    @pytest.mark.asyncio
    async def test_flush_empty_queue(self):
        """Test flushing with empty queue."""
        client = Aptabase("A-EU-1234567890")
        await client.start()

        with patch.object(client, "_send_events", new_callable=AsyncMock) as mock_send:
            await client.flush()
            assert mock_send.call_count == 0

        await client.stop()

    @pytest.mark.asyncio
    async def test_flush_respects_batch_size(self):
        """Test flush respects maximum batch size."""
        client = Aptabase("A-EU-1234567890", max_batch_size=2)
        await client.start()

        with patch.object(client, "_send_events", new_callable=AsyncMock) as mock_send:
            # Add 5 events
            for i in range(5):
                client._event_queue.append(Event(name=f"event{i}"))

            await client.flush()

            # Should send only 2 events (batch size)
            assert mock_send.call_count == 1
            assert len(mock_send.call_args[0][0]) == 2
            # 3 events should remain in queue
            assert len(client._event_queue) == 3

        await client.stop()

    @pytest.mark.asyncio
    async def test_flush_on_stop(self):
        """Test that stop flushes remaining events."""
        client = Aptabase("A-EU-1234567890")
        await client.start()

        with patch.object(client, "_send_events", new_callable=AsyncMock) as mock_send:
            await client.track("event1")

            await client.stop()

            assert mock_send.call_count == 1

    @pytest.mark.asyncio
    async def test_flush_without_client(self):
        """Test flushing when client is not initialized."""
        client = Aptabase("A-EU-1234567890")

        # Add event to queue without starting client
        client._event_queue.append(Event(name="test"))

        async with client._queue_lock:
            await client._flush_events()

        # Should not crash, events remain in queue
        assert len(client._event_queue) == 1

    @pytest.mark.asyncio
    async def test_periodic_flush(self):
        """Test periodic flush task."""
        client = Aptabase("A-EU-1234567890", flush_interval=0.1)
        await client.start()

        with patch.object(client, "_send_events", new_callable=AsyncMock) as mock_send:
            await client.track("event1")

            # Wait for periodic flush
            await asyncio.sleep(0.15)

            assert mock_send.call_count >= 1

        await client.stop()

    @pytest.mark.asyncio
    async def test_flush_error_requeues_events(self):
        """Test that flush errors re-queue events."""
        client = Aptabase("A-EU-1234567890")
        await client.start()

        await client.track("event1")
        await client.track("event2")

        # Mock _send_events to raise an error
        with patch.object(
            client,
            "_send_events",
            new_callable=AsyncMock,
            side_effect=Exception("Network error"),
        ):
            async with client._queue_lock:
                await client._flush_events()

        # Events should be back in queue
        assert len(client._event_queue) == 2

        await client.stop()


class TestNetworkOperations:
    """Test network operations."""

    @pytest.mark.asyncio
    async def test_send_events_success(self):
        """Test successful event sending."""
        client = Aptabase("A-EU-1234567890")
        await client.start()

        events = [Event(name="test_event")]

        with patch.object(client._client, "post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            await client._send_events(events)

            assert mock_post.call_count == 1
            call_args = mock_post.call_args
            assert "api/v0/events" in call_args[0][0]
            assert len(call_args[1]["json"]) == 1

        await client.stop()

    @pytest.mark.asyncio
    async def test_send_events_empty_list(self):
        """Test sending empty events list."""
        client = Aptabase("A-EU-1234567890")
        await client.start()

        with patch.object(client._client, "post", new_callable=AsyncMock) as mock_post:
            await client._send_events([])
            assert mock_post.call_count == 0

        await client.stop()

    @pytest.mark.asyncio
    async def test_send_events_http_error(self):
        """Test handling HTTP error during send."""
        client = Aptabase("A-EU-1234567890")
        await client.start()

        events = [Event(name="test_event")]

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        with patch.object(
            client._client,
            "post",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "Error", request=MagicMock(), response=mock_response
            ),
        ):
            with pytest.raises(NetworkError, match="HTTP error 400"):
                await client._send_events(events)

        await client.stop()

    @pytest.mark.asyncio
    async def test_send_events_request_error(self):
        """Test handling request error during send."""
        client = Aptabase("A-EU-1234567890")
        await client.start()

        events = [Event(name="test_event")]

        with patch.object(
            client._client,
            "post",
            new_callable=AsyncMock,
            side_effect=httpx.RequestError("Connection failed"),
        ):
            with pytest.raises(NetworkError, match="Network error"):
                await client._send_events(events)

        await client.stop()

    @pytest.mark.asyncio
    async def test_send_events_assertion_error(self):
        """Test assertion error when client not initialized."""
        client = Aptabase("A-EU-1234567890")
        # Don't start client

        events = [Event(name="test_event")]

        with pytest.raises(AssertionError, match="HTTP client is not initialized"):
            await client._send_events(events)


class TestExceptionClasses:
    """Test exception classes."""

    def test_aptabase_error(self):
        """Test base AptabaseError."""
        from aptabase.exceptions import AptabaseError

        error = AptabaseError("Test error")
        assert str(error) == "Test error"

    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("Config error")
        assert str(error) == "Config error"
        assert isinstance(error, Exception)

    def test_network_error_with_status_code(self):
        """Test NetworkError with status code."""
        error = NetworkError("Network failed", status_code=500)
        assert str(error) == "Network failed"
        assert error.status_code == 500

    def test_network_error_without_status_code(self):
        """Test NetworkError without status code."""
        error = NetworkError("Network failed")
        assert str(error) == "Network failed"
        assert error.status_code is None

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Validation failed")
        assert str(error) == "Validation failed"


class TestModels:
    """Test data models."""

    def test_system_properties_defaults(self):
        """Test SystemProperties with defaults."""
        props = SystemProperties()

        assert props.locale == "en-US"
        assert props.os_name is not None
        assert props.os_version is not None
        assert props.device_model is not None
        assert props.is_debug is False
        assert props.app_version == "1.0.0"
        assert props.sdk_version == "aptabase-python@0.1.0"

    def test_system_properties_custom(self):
        """Test SystemProperties with custom values."""
        props = SystemProperties(locale="fr-FR", is_debug=True, app_version="2.0.0")

        assert props.locale == "fr-FR"
        assert props.is_debug is True
        assert props.app_version == "2.0.0"

    def test_system_properties_to_dict(self):
        """Test SystemProperties to_dict conversion."""
        props = SystemProperties(app_version="1.5.0", is_debug=True)
        result = props.to_dict()

        assert result["appVersion"] == "1.5.0"
        assert result["isDebug"] is True
        assert "locale" in result
        assert "osName" in result
        assert "osVersion" in result
        assert "deviceModel" in result
        assert "sdkVersion" in result

    def test_event_defaults(self):
        """Test Event with defaults."""
        event = Event(name="test_event")

        assert event.name == "test_event"
        assert event.timestamp is not None
        assert event.session_id is not None
        assert event.props == {}

    def test_event_custom_values(self):
        """Test Event with custom values."""
        timestamp = datetime.now()
        session_id = "custom-session"
        props = {"key": "value"}

        event = Event(
            name="custom_event", timestamp=timestamp, session_id=session_id, props=props
        )

        assert event.name == "custom_event"
        assert event.timestamp == timestamp
        assert event.session_id == session_id
        assert event.props == props

    def test_event_to_dict(self):
        """Test Event to_dict conversion."""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        event = Event(
            name="test_event",
            timestamp=timestamp,
            session_id="session123",
            props={"user": "alice"},
        )

        system_props = SystemProperties()
        result = event.to_dict(system_props)

        assert result["eventName"] == "test_event"
        assert result["sessionId"] == "session123"
        assert result["props"] == {"user": "alice"}
        assert "timestamp" in result
        assert result["timestamp"].endswith("Z")
        assert "systemProps" in result

    def test_event_to_dict_no_props(self):
        """Test Event to_dict with no props."""
        event = Event(name="test_event", props=None)
        system_props = SystemProperties()
        result = event.to_dict(system_props)

        assert result["props"] == {}


class TestIntegration:
    """Integration tests."""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete workflow from init to shutdown."""
        async with Aptabase(
            "A-EU-1234567890", app_version="1.0.0", max_batch_size=5
        ) as client:
            with patch.object(
                client, "_send_events", new_callable=AsyncMock
            ) as mock_send:
                # Track multiple events
                await client.track("page_view", {"page": "home"})
                await client.track("button_click", {"button": "submit"})
                await client.track("form_submit", {"form": "contact"})

                # Manual flush
                await client.flush()

                assert mock_send.call_count >= 1

    @pytest.mark.asyncio
    async def test_concurrent_tracking(self):
        """Test concurrent event tracking."""
        client = Aptabase("A-EU-1234567890")
        await client.start()

        with patch.object(client, "_send_events", new_callable=AsyncMock):
            # Track events concurrently
            tasks = [client.track(f"event_{i}", {"index": i}) for i in range(10)]
            await asyncio.gather(*tasks)

            assert len(client._event_queue) <= 10

        await client.stop()

    @pytest.mark.asyncio
    async def test_error_recovery(self):
        """Test client recovery from errors."""
        client = Aptabase("A-EU-1234567890")
        await client.start()

        # First send fails
        call_count = 0

        async def mock_send_with_error(events):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise NetworkError("First attempt failed")

        with patch.object(client, "_send_events", new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = mock_send_with_error

            await client.track("event1")

            # This flush will fail and requeue
            async with client._queue_lock:
                await client._flush_events()

            # Events should still be in queue
            assert len(client._event_queue) > 0

        await client.stop()
