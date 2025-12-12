"""Tests for data models."""

import platform
import uuid
from datetime import datetime

import pytest

from aptabase.models import Event, SystemProperties


class TestSystemProperties:
    """Test SystemProperties model."""

    def test_default_initialization(self):
        """Test SystemProperties with default values."""
        props = SystemProperties()

        assert props.locale == "en-US"
        assert props.os_name == platform.system()
        assert props.os_version == platform.release()
        assert props.device_model == platform.machine()
        assert props.is_debug is False
        assert props.app_version == "1.0.0"
        assert props.sdk_version == "aptabase-python@0.1.0"

    def test_custom_initialization(self):
        """Test SystemProperties with custom values."""
        props = SystemProperties(
            locale="fr-FR",
            os_name="CustomOS",
            os_version="10.5",
            device_model="CustomDevice",
            is_debug=True,
            app_version="2.5.0",
            sdk_version="1.0.0",
        )

        assert props.locale == "fr-FR"
        assert props.os_name == "CustomOS"
        assert props.os_version == "10.5"
        assert props.device_model == "CustomDevice"
        assert props.is_debug is True
        assert props.app_version == "2.5.0"
        assert props.sdk_version == "1.0.0"

    def test_partial_initialization(self):
        """Test SystemProperties with some custom values."""
        props = SystemProperties(app_version="3.0.0", is_debug=True)

        assert props.app_version == "3.0.0"
        assert props.is_debug is True
        # Defaults should still apply
        assert props.locale == "en-US"
        assert props.sdk_version == "aptabase-python@0.1.0"

    def test_to_dict_structure(self):
        """Test to_dict returns correct structure."""
        props = SystemProperties()
        result = props.to_dict()

        assert isinstance(result, dict)
        assert "locale" in result
        assert "osName" in result
        assert "osVersion" in result
        assert "deviceModel" in result
        assert "isDebug" in result
        assert "appVersion" in result
        assert "sdkVersion" in result

    def test_to_dict_values(self):
        """Test to_dict returns correct values."""
        props = SystemProperties(
            locale="de-DE",
            os_name="Linux",
            os_version="5.15",
            device_model="x86_64",
            is_debug=True,
            app_version="4.2.0",
            sdk_version="2.0.0",
        )
        result = props.to_dict()

        assert result["locale"] == "de-DE"
        assert result["osName"] == "Linux"
        assert result["osVersion"] == "5.15"
        assert result["deviceModel"] == "x86_64"
        assert result["isDebug"] is True
        assert result["appVersion"] == "4.2.0"
        assert result["sdkVersion"] == "2.0.0"

    def test_to_dict_camel_case_keys(self):
        """Test that to_dict uses camelCase for keys."""
        props = SystemProperties()
        result = props.to_dict()

        # Check camelCase
        assert "osName" in result
        assert "osVersion" in result
        assert "deviceModel" in result
        assert "isDebug" in result
        assert "appVersion" in result
        assert "sdkVersion" in result

        # Check snake_case NOT in result
        assert "os_name" not in result
        assert "os_version" not in result
        assert "device_model" not in result
        assert "is_debug" not in result
        assert "app_version" not in result
        assert "sdk_version" not in result

    def test_debug_false_by_default(self):
        """Test that is_debug defaults to False."""
        props = SystemProperties()
        assert props.is_debug is False

    def test_debug_true_when_set(self):
        """Test that is_debug can be set to True."""
        props = SystemProperties(is_debug=True)
        assert props.is_debug is True


class TestEvent:
    """Test Event model."""

    def test_minimal_initialization(self):
        """Test Event with only required name parameter."""
        event = Event(name="test_event")

        assert event.name == "test_event"
        assert event.timestamp is not None
        assert isinstance(event.timestamp, datetime)
        assert event.session_id is not None
        assert isinstance(event.session_id, str)
        assert event.props == {}

    def test_full_initialization(self):
        """Test Event with all parameters."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        session_id = "custom-session-123"
        props = {"user_id": "123", "action": "click"}

        event = Event(
            name="button_click", timestamp=timestamp, session_id=session_id, props=props
        )

        assert event.name == "button_click"
        assert event.timestamp == timestamp
        assert event.session_id == session_id
        assert event.props == props

    def test_timestamp_auto_generation(self):
        """Test that timestamp is auto-generated when not provided."""
        before = datetime.now()
        event = Event(name="test")
        after = datetime.now()

        assert event.timestamp is not None
        assert before <= event.timestamp <= after

    def test_session_id_auto_generation(self):
        """Test that session_id is auto-generated when not provided."""
        event = Event(name="test")

        assert event.session_id is not None
        assert isinstance(event.session_id, str)
        assert len(event.session_id) > 0

    def test_session_id_is_uuid_format(self):
        """Test that auto-generated session_id is valid UUID."""
        event = Event(name="test")

        # Should be able to parse as UUID
        try:
            uuid.UUID(event.session_id)
        except ValueError:
            pytest.fail("session_id is not a valid UUID")

    def test_props_default_empty_dict(self):
        """Test that props defaults to empty dict."""
        event = Event(name="test")

        assert event.props == {}
        assert isinstance(event.props, dict)

    def test_props_none_becomes_empty_dict(self):
        """Test that props=None becomes empty dict."""
        event = Event(name="test", props=None)

        assert event.props == {}

    def test_props_custom_values(self):
        """Test Event with custom props."""
        props = {"user": "alice", "count": 42, "active": True, "tags": ["a", "b", "c"]}
        event = Event(name="test", props=props)

        assert event.props == props

    def test_to_dict_structure(self):
        """Test to_dict returns correct structure."""
        event = Event(name="test_event")
        system_props = SystemProperties()

        result = event.to_dict(system_props)

        assert isinstance(result, dict)
        assert "timestamp" in result
        assert "sessionId" in result
        assert "eventName" in result
        assert "systemProps" in result
        assert "props" in result

    def test_to_dict_values(self):
        """Test to_dict returns correct values."""
        timestamp = datetime(2024, 6, 15, 14, 30, 45)
        event = Event(
            name="custom_event",
            timestamp=timestamp,
            session_id="session-abc",
            props={"key": "value"},
        )
        system_props = SystemProperties(app_version="2.0.0")

        result = event.to_dict(system_props)

        assert result["eventName"] == "custom_event"
        assert result["sessionId"] == "session-abc"
        assert result["props"] == {"key": "value"}
        assert "2024-06-15" in result["timestamp"]
        assert result["timestamp"].endswith("Z")
        assert isinstance(result["systemProps"], dict)

    def test_to_dict_timestamp_format(self):
        """Test that timestamp is formatted as ISO with Z suffix."""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        event = Event(name="test", timestamp=timestamp)
        system_props = SystemProperties()

        result = event.to_dict(system_props)

        assert result["timestamp"].endswith("Z")
        assert "2024-01-01T12:00:00" in result["timestamp"]

    def test_to_dict_camel_case_keys(self):
        """Test that to_dict uses camelCase for keys."""
        event = Event(name="test")
        system_props = SystemProperties()

        result = event.to_dict(system_props)

        assert "sessionId" in result
        assert "eventName" in result
        assert "systemProps" in result

        # Check snake_case NOT in result
        assert "session_id" not in result
        assert "event_name" not in result
        assert "system_props" not in result

    def test_to_dict_empty_props(self):
        """Test to_dict with empty props."""
        event = Event(name="test", props=None)
        system_props = SystemProperties()

        result = event.to_dict(system_props)

        assert result["props"] == {}

    def test_to_dict_system_props_included(self):
        """Test that system properties are included in to_dict."""
        event = Event(name="test")
        system_props = SystemProperties(app_version="3.0.0", is_debug=True)

        result = event.to_dict(system_props)

        assert "systemProps" in result
        assert result["systemProps"]["appVersion"] == "3.0.0"
        assert result["systemProps"]["isDebug"] is True

    def test_multiple_events_different_session_ids(self):
        """Test that multiple events get different session IDs."""
        event1 = Event(name="event1")
        event2 = Event(name="event2")

        # Auto-generated session IDs should be different (UUIDs)
        assert event1.session_id != event2.session_id

    def test_multiple_events_different_timestamps(self):
        """Test that multiple events get different timestamps."""
        event1 = Event(name="event1")
        # Small delay to ensure different timestamp
        import time

        time.sleep(0.001)
        event2 = Event(name="event2")

        assert event1.timestamp != event2.timestamp

    def test_event_name_preserved(self):
        """Test that event name is preserved exactly."""
        names = [
            "simple",
            "with spaces",
            "with-dashes",
            "with_underscores",
            "CamelCase",
            "with.dots",
            "with123numbers",
        ]

        for name in names:
            event = Event(name=name)
            assert event.name == name

    def test_props_complex_types(self):
        """Test Event with complex prop types."""
        props = {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }

        event = Event(name="test", props=props)
        assert event.props == props

    def test_to_dict_preserves_prop_types(self):
        """Test that to_dict preserves prop types."""
        props = {
            "int": 42,
            "float": 3.14,
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
        }

        event = Event(name="test", props=props)
        system_props = SystemProperties()
        result = event.to_dict(system_props)

        assert result["props"]["int"] == 42
        assert result["props"]["float"] == 3.14
        assert result["props"]["bool"] is True
        assert result["props"]["none"] is None
        assert result["props"]["list"] == [1, 2, 3]


class TestModelsIntegration:
    """Integration tests for models working together."""

    def test_event_with_system_props_full_workflow(self):
        """Test complete workflow of creating event and converting to dict."""
        # Create system properties
        system_props = SystemProperties(app_version="1.5.0", is_debug=False)

        # Create event
        timestamp = datetime(2024, 3, 15, 9, 30, 0)
        event = Event(
            name="user_action",
            timestamp=timestamp,
            session_id="sess-123",
            props={"action": "submit", "value": 100},
        )

        # Convert to dict
        result = event.to_dict(system_props)

        # Verify complete structure
        assert result["eventName"] == "user_action"
        assert result["sessionId"] == "sess-123"
        assert result["props"]["action"] == "submit"
        assert result["props"]["value"] == 100
        assert result["systemProps"]["appVersion"] == "1.5.0"
        assert result["systemProps"]["isDebug"] is False
        assert "timestamp" in result

    def test_multiple_events_same_system_props(self):
        """Test multiple events can share same system properties."""
        system_props = SystemProperties(app_version="2.0.0")

        event1 = Event(name="event1", props={"num": 1})
        event2 = Event(name="event2", props={"num": 2})

        result1 = event1.to_dict(system_props)
        result2 = event2.to_dict(system_props)

        # Both should have same system props
        assert result1["systemProps"] == result2["systemProps"]
        # But different event data
        assert result1["eventName"] != result2["eventName"]
        assert result1["props"] != result2["props"]

    def test_dataclass_fields_accessible(self):
        """Test that dataclass fields are accessible."""
        system_props = SystemProperties()

        # Should be able to access all fields
        assert hasattr(system_props, "locale")
        assert hasattr(system_props, "os_name")
        assert hasattr(system_props, "os_version")
        assert hasattr(system_props, "device_model")
        assert hasattr(system_props, "is_debug")
        assert hasattr(system_props, "app_version")
        assert hasattr(system_props, "sdk_version")

        event = Event(name="test")

        assert hasattr(event, "name")
        assert hasattr(event, "timestamp")
        assert hasattr(event, "session_id")
        assert hasattr(event, "props")
