"""Unit tests for structured logging module."""

import json
import logging
from typing import Any

import pytest

from app.core.logging import (
    add_request_id,
    get_logger,
    get_request_id,
    request_id_var,
    set_request_id,
    setup_logging,
)


class TestRequestIDContext:
    """Test request ID context variable functionality."""

    def test_set_and_get_request_id(self) -> None:
        """Test setting and retrieving request ID."""
        test_id = "test-request-123"
        set_request_id(test_id)
        assert get_request_id() == test_id

    def test_get_request_id_when_not_set(self) -> None:
        """Test getting request ID when not set returns empty string."""
        # Reset context to empty string
        _ = request_id_var.set("")
        assert get_request_id() == ""

    def test_request_id_isolation(self) -> None:
        """Test that request IDs are isolated to their context."""
        set_request_id("request-1")
        assert get_request_id() == "request-1"

        set_request_id("request-2")
        assert get_request_id() == "request-2"


class TestRequestIDProcessor:
    """Test the add_request_id processor."""

    def test_add_request_id_processor_with_id(self) -> None:
        """Test processor adds request_id when set."""
        set_request_id("test-123")
        event_dict: dict[str, Any] = {"event": "test.event"}

        # Create a mock logger
        result = add_request_id(None, "info", event_dict)

        assert result["request_id"] == "test-123"
        assert result["event"] == "test.event"

    def test_add_request_id_processor_without_id(self) -> None:
        """Test processor doesn't add request_id when empty."""
        _ = request_id_var.set("")
        event_dict: dict[str, Any] = {"event": "test.event"}

        result = add_request_id(None, "info", event_dict)

        assert "request_id" not in result
        assert result["event"] == "test.event"


class TestLoggingSetup:
    """Test logging setup and configuration."""

    def test_setup_logging_configures_structlog(self) -> None:
        """Test that setup_logging configures structlog."""
        setup_logging(log_level="INFO")

        # Verify we can get a logger and it has logging methods
        logger = get_logger()
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")

    def test_setup_logging_with_different_levels(self) -> None:
        """Test setup_logging with different log levels."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            setup_logging(log_level=level)
            root_logger = logging.getLogger()
            expected_level = getattr(logging, level)
            assert root_logger.level == expected_level

    def test_setup_logging_default_level(self) -> None:
        """Test setup_logging uses INFO as default level."""
        setup_logging()
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO


class TestLogger:
    """Test logger functionality."""

    def test_get_logger_returns_bound_logger(self) -> None:
        """Test get_logger returns a logger with proper methods."""
        setup_logging()
        logger = get_logger()
        # Verify logger has expected methods
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "warning")
        assert callable(logger.info)

    def test_get_logger_with_name(self) -> None:
        """Test get_logger accepts a custom name."""
        setup_logging()
        logger = get_logger("custom.logger")
        assert logger is not None

    def test_logger_outputs_json(self, capfd: pytest.CaptureFixture[str]) -> None:
        """Test that logger outputs valid JSON."""
        setup_logging(log_level="INFO")
        logger = get_logger()

        logger.info("test.event", key="value", count=42)

        captured = capfd.readouterr()
        output = captured.out.strip()

        # Parse as JSON to verify format
        log_entry = json.loads(output)
        assert log_entry["event"] == "test.event"
        assert log_entry["key"] == "value"
        assert log_entry["count"] == 42
        assert "timestamp" in log_entry
        assert log_entry["level"] == "info"

    def test_logger_includes_request_id(
        self, capfd: pytest.CaptureFixture[str]
    ) -> None:
        """Test that logger includes request_id when set."""
        setup_logging(log_level="INFO")
        logger = get_logger()

        set_request_id("req-xyz-789")
        logger.info("test.request_event", action="process")

        captured = capfd.readouterr()
        output = captured.out.strip()

        log_entry = json.loads(output)
        assert log_entry["request_id"] == "req-xyz-789"
        assert log_entry["event"] == "test.request_event"

    def test_logger_handles_exceptions(self, capfd: pytest.CaptureFixture[str]) -> None:
        """Test that logger properly formats exceptions."""
        setup_logging(log_level="ERROR")
        logger = get_logger()

        try:
            raise ValueError("Test error message")
        except ValueError as exc:
            logger.error("test.error_event", error=str(exc), exc_info=True)

        captured = capfd.readouterr()
        output = captured.out.strip()

        log_entry = json.loads(output)
        assert log_entry["event"] == "test.error_event"
        assert log_entry["error"] == "Test error message"
        # Exception should be formatted with traceback
        assert "exception" in log_entry
        assert "ValueError" in log_entry["exception"]
        assert "Traceback" in log_entry["exception"]


class TestLoggingPattern:
    """Test the hybrid dotted namespace logging pattern."""

    def test_dotted_namespace_pattern(self, capfd: pytest.CaptureFixture[str]) -> None:
        """Test logging follows domain.component.action_state pattern."""
        setup_logging(log_level="INFO")
        logger = get_logger()

        # Test various patterns
        patterns = [
            "user.registration_started",
            "user.registration_completed",
            "database.connection_initialized",
            "api.request_failed",
            "payment.processing_validated",
        ]

        for pattern in patterns:
            logger.info(pattern, test=True)

        captured = capfd.readouterr()
        output_lines = captured.out.strip().split("\n")

        assert len(output_lines) == len(patterns)

        for i, line in enumerate(output_lines):
            log_entry = json.loads(line)
            assert log_entry["event"] == patterns[i]

    def test_logging_with_context_data(self, capfd: pytest.CaptureFixture[str]) -> None:
        """Test logging with additional context data."""
        setup_logging(log_level="INFO")
        logger = get_logger()

        logger.info(
            "user.registration_completed",
            user_id="user-123",
            email="test@example.com",
            source="api",
            method="email_password",
        )

        captured = capfd.readouterr()
        output = captured.out.strip()

        log_entry = json.loads(output)
        assert log_entry["event"] == "user.registration_completed"
        assert log_entry["user_id"] == "user-123"
        assert log_entry["email"] == "test@example.com"
        assert log_entry["source"] == "api"
        assert log_entry["method"] == "email_password"


class TestLoggingLevels:
    """Test different logging levels."""

    def test_debug_level_logging(self, capfd: pytest.CaptureFixture[str]) -> None:
        """Test DEBUG level logging."""
        setup_logging(log_level="DEBUG")
        logger = get_logger()

        logger.debug("test.debug_event", detail="debug info")

        captured = capfd.readouterr()
        output = captured.out.strip()

        log_entry = json.loads(output)
        assert log_entry["level"] == "debug"
        assert log_entry["event"] == "test.debug_event"

    def test_info_level_logging(self, capfd: pytest.CaptureFixture[str]) -> None:
        """Test INFO level logging."""
        setup_logging(log_level="INFO")
        logger = get_logger()

        logger.info("test.info_event", status="ok")

        captured = capfd.readouterr()
        output = captured.out.strip()

        log_entry = json.loads(output)
        assert log_entry["level"] == "info"

    def test_warning_level_logging(self, capfd: pytest.CaptureFixture[str]) -> None:
        """Test WARNING level logging."""
        setup_logging(log_level="WARNING")
        logger = get_logger()

        logger.warning("test.warning_event", message="something unusual")

        captured = capfd.readouterr()
        output = captured.out.strip()

        log_entry = json.loads(output)
        assert log_entry["level"] == "warning"

    def test_error_level_logging(self, capfd: pytest.CaptureFixture[str]) -> None:
        """Test ERROR level logging."""
        setup_logging(log_level="ERROR")
        logger = get_logger()

        logger.error("test.error_event", error="something failed")

        captured = capfd.readouterr()
        output = captured.out.strip()

        log_entry = json.loads(output)
        assert log_entry["level"] == "error"

    def test_log_level_filtering(self, capfd: pytest.CaptureFixture[str]) -> None:
        """Test that log levels are properly filtered."""
        setup_logging(log_level="WARNING")
        logger = get_logger()

        # These should not appear
        logger.debug("test.debug_event")
        logger.info("test.info_event")

        # These should appear
        logger.warning("test.warning_event")
        logger.error("test.error_event")

        captured = capfd.readouterr()
        output_lines = [line for line in captured.out.strip().split("\n") if line]

        # Should only have 2 lines (warning and error)
        assert len(output_lines) == 2

        log_entries = [json.loads(line) for line in output_lines]
        assert log_entries[0]["level"] == "warning"
        assert log_entries[1]["level"] == "error"
