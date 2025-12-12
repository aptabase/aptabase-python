"""Tests for exception classes."""

import pytest


def test_imports():
    """Test that all exceptions can be imported."""
    from aptabase.exceptions import (
        AptabaseError,
        ConfigurationError,
        NetworkError,
        ValidationError,
    )

    assert AptabaseError is not None
    assert ConfigurationError is not None
    assert NetworkError is not None
    assert ValidationError is not None


class TestAptabaseError:
    """Test AptabaseError base class."""

    def test_create_with_message(self):
        """Test creating error with message."""
        from aptabase.exceptions import AptabaseError

        error = AptabaseError("Test error message")
        assert str(error) == "Test error message"

    def test_is_exception(self):
        """Test that AptabaseError is an Exception."""
        from aptabase.exceptions import AptabaseError

        error = AptabaseError("Test")
        assert isinstance(error, Exception)

    def test_can_be_raised(self):
        """Test that error can be raised and caught."""
        from aptabase.exceptions import AptabaseError

        with pytest.raises(AptabaseError, match="Test error"):
            raise AptabaseError("Test error")


class TestConfigurationError:
    """Test ConfigurationError class."""

    def test_create_with_message(self):
        """Test creating error with message."""
        from aptabase.exceptions import ConfigurationError

        error = ConfigurationError("Invalid configuration")
        assert str(error) == "Invalid configuration"

    def test_inherits_from_aptabase_error(self):
        """Test that ConfigurationError inherits from AptabaseError."""
        from aptabase.exceptions import AptabaseError, ConfigurationError

        error = ConfigurationError("Test")
        assert isinstance(error, AptabaseError)
        assert isinstance(error, Exception)

    def test_can_be_raised(self):
        """Test that error can be raised and caught."""
        from aptabase.exceptions import ConfigurationError

        with pytest.raises(ConfigurationError, match="Config error"):
            raise ConfigurationError("Config error")

    def test_can_be_caught_as_base_error(self):
        """Test that ConfigurationError can be caught as AptabaseError."""
        from aptabase.exceptions import AptabaseError, ConfigurationError

        with pytest.raises(AptabaseError):
            raise ConfigurationError("Test")


class TestNetworkError:
    """Test NetworkError class."""

    def test_create_with_message_only(self):
        """Test creating error with message only."""
        from aptabase.exceptions import NetworkError

        error = NetworkError("Connection failed")
        assert str(error) == "Connection failed"
        assert error.status_code is None

    def test_create_with_status_code(self):
        """Test creating error with status code."""
        from aptabase.exceptions import NetworkError

        error = NetworkError("Request failed", status_code=404)
        assert str(error) == "Request failed"
        assert error.status_code == 404

    def test_create_with_various_status_codes(self):
        """Test creating error with various HTTP status codes."""
        from aptabase.exceptions import NetworkError

        test_cases = [
            (400, "Bad Request"),
            (401, "Unauthorized"),
            (403, "Forbidden"),
            (404, "Not Found"),
            (500, "Internal Server Error"),
            (502, "Bad Gateway"),
            (503, "Service Unavailable"),
        ]

        for status_code, message in test_cases:
            error = NetworkError(message, status_code=status_code)
            assert error.status_code == status_code
            assert str(error) == message

    def test_inherits_from_aptabase_error(self):
        """Test that NetworkError inherits from AptabaseError."""
        from aptabase.exceptions import AptabaseError, NetworkError

        error = NetworkError("Test")
        assert isinstance(error, AptabaseError)
        assert isinstance(error, Exception)

    def test_can_be_raised(self):
        """Test that error can be raised and caught."""
        from aptabase.exceptions import NetworkError

        with pytest.raises(NetworkError, match="Network error"):
            raise NetworkError("Network error", status_code=500)

    def test_status_code_attribute_accessible(self):
        """Test that status_code attribute is accessible."""
        from aptabase.exceptions import NetworkError

        error = NetworkError("Test", status_code=200)
        assert hasattr(error, "status_code")
        assert error.status_code == 200

    def test_can_be_caught_as_base_error(self):
        """Test that NetworkError can be caught as AptabaseError."""
        from aptabase.exceptions import AptabaseError, NetworkError

        with pytest.raises(AptabaseError):
            raise NetworkError("Test", status_code=500)


class TestValidationError:
    """Test ValidationError class."""

    def test_create_with_message(self):
        """Test creating error with message."""
        from aptabase.exceptions import ValidationError

        error = ValidationError("Invalid data")
        assert str(error) == "Invalid data"

    def test_inherits_from_aptabase_error(self):
        """Test that ValidationError inherits from AptabaseError."""
        from aptabase.exceptions import AptabaseError, ValidationError

        error = ValidationError("Test")
        assert isinstance(error, AptabaseError)
        assert isinstance(error, Exception)

    def test_can_be_raised(self):
        """Test that error can be raised and caught."""
        from aptabase.exceptions import ValidationError

        with pytest.raises(ValidationError, match="Validation failed"):
            raise ValidationError("Validation failed")

    def test_can_be_caught_as_base_error(self):
        """Test that ValidationError can be caught as AptabaseError."""
        from aptabase.exceptions import AptabaseError, ValidationError

        with pytest.raises(AptabaseError):
            raise ValidationError("Test")


class TestExceptionHierarchy:
    """Test exception hierarchy and inheritance."""

    def test_all_inherit_from_aptabase_error(self):
        """Test that all custom exceptions inherit from AptabaseError."""
        from aptabase.exceptions import (
            AptabaseError,
            ConfigurationError,
            NetworkError,
            ValidationError,
        )

        errors = [
            ConfigurationError("test"),
            NetworkError("test"),
            ValidationError("test"),
        ]

        for error in errors:
            assert isinstance(error, AptabaseError)

    def test_all_inherit_from_exception(self):
        """Test that all custom exceptions inherit from Exception."""
        from aptabase.exceptions import (
            ConfigurationError,
            NetworkError,
            ValidationError,
        )

        errors = [
            ConfigurationError("test"),
            NetworkError("test"),
            ValidationError("test"),
        ]

        for error in errors:
            assert isinstance(error, Exception)

    def test_catch_any_with_base_error(self):
        """Test catching any custom exception with AptabaseError."""
        from aptabase.exceptions import (
            AptabaseError,
            ConfigurationError,
            NetworkError,
            ValidationError,
        )

        exceptions_to_test = [
            ConfigurationError("config"),
            NetworkError("network"),
            ValidationError("validation"),
        ]

        for exc in exceptions_to_test:
            with pytest.raises(AptabaseError):
                raise exc
