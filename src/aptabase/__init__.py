"""Aptabase Python SDK - Async analytics for privacy-conscious developers."""

__version__ = "0.1.0"

from .client import Aptabase
from .exceptions import AptabaseError, ConfigurationError, NetworkError
from .models import Event, SystemProperties

__all__ = [
    "Aptabase",
    "Event",
    "SystemProperties",
    "AptabaseError",
    "ConfigurationError",
    "NetworkError",
]
