"""Exception classes for the Aptabase SDK."""


class AptabaseError(Exception):
    """Base exception class for all Aptabase SDK errors."""

    pass


class ConfigurationError(AptabaseError):
    """Raised when the SDK is misconfigured."""

    pass


class NetworkError(AptabaseError):
    """Raised when network requests fail."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize the NetworkError exception."""
        super().__init__(message)
        self.status_code = status_code


class ValidationError(AptabaseError):
    """Raised when event data validation fails."""

    pass
