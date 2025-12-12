"""Data models for Aptabase SDK."""

from __future__ import annotations

import platform
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SystemProperties:
    """System properties automatically collected by the SDK."""

    locale: str = field(default_factory=lambda: "en-US")
    os_name: str = field(default_factory=platform.system)
    os_version: str = field(default_factory=platform.release)
    device_model: str = field(default_factory=platform.machine)
    is_debug: bool = False
    app_version: str = "1.0.0"
    sdk_version: str = "0.0.1"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format for API requests."""
        return {
            "locale": self.locale,
            "osName": self.os_name,
            "osVersion": self.os_version,
            "deviceModel": self.device_model,
            "isDebug": self.is_debug,
            "appVersion": self.app_version,
            "sdkVersion": self.sdk_version,
        }


@dataclass
class Event:
    """Represents an analytics event to be sent to Aptabase."""

    name: str
    timestamp: datetime | None = None
    session_id: str | None = None
    props: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Set default values after initialization."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.session_id is None:
            self.session_id = str(uuid.uuid4())
        if self.props is None:
            self.props = {}

    def to_dict(self, system_props: SystemProperties) -> dict[str, Any]:
        """Convert to dictionary format for API requests."""
        return {
            "timestamp": self.timestamp.isoformat() + "Z" if self.timestamp else None,
            "sessionId": self.session_id,
            "eventName": self.name,
            "systemProps": system_props.to_dict(),
            "props": self.props or {},
        }
