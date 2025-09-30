"""Unit tests for BAML error handler."""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.llm.baml_error_handler import (
    BAMLErrorHandler,
    ErrorCategory,
    ErrorRecord,
    FallbackAttempt,
)
from src.llm.circuit_breaker import CircuitBreakerError


class TestBAMLErrorHandler:
    """Test suite for BAMLErrorHandler."""

    def test_initialization(self):
        """Test error handler initializes with correct defaults."""
        handler = BAMLErrorHandler()

        assert handler.max_retries == 3
        assert handler.base_delay == 1.0
        assert handler.max_delay == 60.0
        assert handler.exponential_base == 2.0
        assert len(handler._error_history) == 0
        assert len(handler._fallback_history) == 0

    def test_initialization_custom_params(self):
        """Test error handler with custom parameters."""
        handler = BAMLErrorHandler(
            max_retries=5,
            base_delay=2.0,
            max_delay=120.0,
            exponential_base=3.0,
        )

        assert handler.max_retries == 5
        assert handler.base_delay == 2.0
        assert handler.max_delay == 120.0
        assert handler.exponential_base == 3.0

    def test_error_categorization_timeout(self):
        """Test timeout error categorization."""
        handler = BAMLErrorHandler()

        error = Exception("Request timed out")
        category = handler._categorize_error(error)

        assert category == ErrorCategory.TIMEOUT

    def test_error_categorization_rate_limit(self):
        """Test rate limit error categorization."""
        handler = BAMLErrorHandler()

        error = Exception("Rate limit exceeded (429)")
        category = handler._categorize_error(error)

        assert category == ErrorCategory.RATE_LIMIT

    def test_error_categorization_invalid_request(self):
        """Test invalid request error categorization."""
        handler = BAMLErrorHandler()

        error = Exception("Invalid request (400)")
        category = handler._categorize_error(error)

        assert category == ErrorCategory.INVALID_REQUEST

    def test_error_categorization_authentication(self):
        """Test authentication error categorization."""
        handler = BAMLErrorHandler()

        error = Exception("Authentication failed (401)")
        category = handler._categorize_error(error)

        assert category == ErrorCategory.AUTHENTICATION

    def test_error_categorization_network(self):
        """Test network error categorization."""
        handler = BAMLErrorHandler()

        error = Exception("Network connection failed")
        category = handler._categorize_error(error)

        assert category == ErrorCategory.NETWORK_ERROR

    def test_error_categorization_unknown(self):
        """Test unknown error categorization."""
        handler = BAMLErrorHandler()

        error = Exception("Something went wrong")
        category = handler._categorize_error(error)

        assert category == ErrorCategory.UNKNOWN

    def test_recoverable_errors(self):
        """Test which error categories are recoverable."""
        handler = BAMLErrorHandler()

        # Recoverable errors
        assert handler._is_recoverable(ErrorCategory.TIMEOUT)
        assert handler._is_recoverable(ErrorCategory.RATE_LIMIT)
        assert handler._is_recoverable(ErrorCategory.NETWORK_ERROR)
        assert handler._is_recoverable(ErrorCategory.MODEL_ERROR)
        assert handler._is_recoverable(ErrorCategory.UNKNOWN)

        # Non-recoverable errors
        assert not handler._is_recoverable(ErrorCategory.INVALID_REQUEST)
        assert not handler._is_recoverable(ErrorCategory.AUTHENTICATION)

    def test_delay_calculation(self):
        """Test exponential backoff delay calculation."""
        handler = BAMLErrorHandler(base_delay=1.0, exponential_base=2.0, max_delay=60.0)

        # First retry: 1 * 2^0 = 1
        assert handler._calculate_delay(0) == 1.0

        # Second retry: 1 * 2^1 = 2
        assert handler._calculate_delay(1) == 2.0

        # Third retry: 1 * 2^2 = 4
        assert handler._calculate_delay(2) == 4.0

        # Fourth retry: 1 * 2^3 = 8
        assert handler._calculate_delay(3) == 8.0

        # Should cap at max_delay
        assert handler._calculate_delay(10) == 60.0

    def test_error_recording(self):
        """Test error recording functionality."""
        handler = BAMLErrorHandler()

        error = Exception("Test error")
        record = handler._record_error(
            error=error,
            client_name="TestClient",
            function_name="TestFunction",
            retry_attempt=0,
            metadata={"key": "value"},
        )

        assert isinstance(record, ErrorRecord)
        assert record.error_message == "Test error"
        assert record.client_name == "TestClient"
        assert record.function_name == "TestFunction"
        assert record.retry_attempt == 0
        assert record.metadata["key"] == "value"

        # Should be in history
        assert len(handler._error_history) == 1
        assert handler._error_history[0] == record

        # Should update error counts
        assert handler._error_counts["TestClient:TestFunction"] == 1

    def test_fallback_recording(self):
        """Test fallback recording functionality."""
        handler = BAMLErrorHandler()

        handler._record_fallback(
            from_client="PrimaryClient",
            to_client="FallbackClient",
            reason="Primary failed",
            success=True,
            duration=1.5,
        )

        assert len(handler._fallback_history) == 1
        fallback = handler._fallback_history[0]

        assert isinstance(fallback, FallbackAttempt)
        assert fallback.from_client == "PrimaryClient"
        assert fallback.to_client == "FallbackClient"
        assert fallback.reason == "Primary failed"
        assert fallback.success is True
        assert fallback.duration == 1.5

    @pytest.mark.asyncio
    async def test_call_with_retry_success_first_attempt(self):
        """Test successful call on first attempt."""
        handler = BAMLErrorHandler()

        async def mock_func():
            return "success"

        result = await handler.call_with_retry(
            mock_func, "TestClient", "TestFunction"
        )

        assert result == "success"
        assert len(handler._error_history) == 0

    @pytest.mark.asyncio
    async def test_call_with_retry_success_after_retry(self):
        """Test successful call after one retry."""
        handler = BAMLErrorHandler(base_delay=0.01)  # Fast retry for testing

        call_count = 0

        async def mock_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Timeout error")
            return "success"

        result = await handler.call_with_retry(
            mock_func, "TestClient", "TestFunction"
        )

        assert result == "success"
        assert call_count == 2
        assert len(handler._error_history) == 1

    @pytest.mark.asyncio
    async def test_call_with_retry_max_retries_exceeded(self):
        """Test failure after max retries."""
        handler = BAMLErrorHandler(max_retries=2, base_delay=0.01)

        async def mock_func():
            raise Exception("Persistent timeout")

        with pytest.raises(Exception) as exc_info:
            await handler.call_with_retry(
                mock_func, "TestClient", "TestFunction"
            )

        assert "Persistent timeout" in str(exc_info.value)
        assert len(handler._error_history) == 3  # Initial + 2 retries

    @pytest.mark.asyncio
    async def test_call_with_retry_non_recoverable_error(self):
        """Test immediate failure for non-recoverable errors."""
        handler = BAMLErrorHandler(max_retries=3, base_delay=0.01)

        async def mock_func():
            raise Exception("Invalid request (400)")

        with pytest.raises(Exception) as exc_info:
            await handler.call_with_retry(
                mock_func, "TestClient", "TestFunction"
            )

        assert "Invalid request" in str(exc_info.value)
        # Should not retry non-recoverable errors
        assert len(handler._error_history) == 1

    @pytest.mark.asyncio
    async def test_call_with_retry_circuit_breaker_open(self):
        """Test circuit breaker prevents calls when open."""
        handler = BAMLErrorHandler(
            enable_circuit_breaker=True,
            circuit_breaker_threshold=2,
        )

        async def mock_func():
            raise Exception("Service unavailable")

        # First two calls should fail and open circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await handler.call_with_retry(
                    mock_func, "TestClient", "TestFunction"
                )

        # Circuit should now be open
        breaker = handler._get_circuit_breaker("TestClient")
        assert breaker.is_open()

        # Next call should fail immediately with CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            await handler.call_with_retry(
                mock_func, "TestClient", "TestFunction"
            )

    @pytest.mark.asyncio
    async def test_call_with_fallback_primary_succeeds(self):
        """Test fallback when primary client succeeds."""
        handler = BAMLErrorHandler()

        async def primary_func():
            return "primary_success"

        def func_factory(client_name: str):
            return primary_func

        result, client_used = await handler.call_with_fallback(
            func_factory, "TestFunction", "PrimaryClient"
        )

        assert result == "primary_success"
        assert client_used == "PrimaryClient"
        assert len(handler._fallback_history) == 0  # No fallback needed

    @pytest.mark.asyncio
    async def test_call_with_fallback_falls_back_on_failure(self):
        """Test fallback to secondary client on primary failure."""
        handler = BAMLErrorHandler(max_retries=1, base_delay=0.01)

        async def primary_func():
            raise Exception("Primary failed")

        async def fallback_func():
            return "fallback_success"

        def func_factory(client_name: str):
            if client_name == "PrimaryClient":
                return primary_func
            else:
                return fallback_func

        result, client_used = await handler.call_with_fallback(
            func_factory, "TestFunction", "PrimaryClient"
        )

        assert result == "fallback_success"
        assert client_used != "PrimaryClient"
        assert len(handler._fallback_history) >= 1
        assert handler._fallback_history[-1].success is True

    @pytest.mark.asyncio
    async def test_call_with_fallback_all_clients_fail(self):
        """Test when all fallback clients fail."""
        handler = BAMLErrorHandler(max_retries=0, base_delay=0.01)

        async def failing_func():
            raise Exception("All clients failed")

        def func_factory(client_name: str):
            return failing_func

        with pytest.raises(Exception) as exc_info:
            await handler.call_with_fallback(
                func_factory, "TestFunction", "PrimaryClient"
            )

        assert "All clients failed" in str(exc_info.value)
        # Should have tried multiple clients
        assert len(handler._error_history) > 1

    def test_error_summary_empty(self):
        """Test error summary with no errors."""
        handler = BAMLErrorHandler()

        summary = handler.get_error_summary()

        assert summary["total_errors"] == 0
        assert summary["by_category"] == {}
        assert summary["by_client"] == {}
        assert summary["by_function"] == {}
        assert summary["recent_errors"] == []

    def test_error_summary_with_errors(self):
        """Test error summary with recorded errors."""
        handler = BAMLErrorHandler()

        # Record some errors
        handler._record_error(
            Exception("Error 1"), "Client1", "Function1", 0
        )
        handler._record_error(
            Exception("Timeout error"), "Client2", "Function2", 1
        )
        handler._record_error(
            Exception("Error 3"), "Client1", "Function1", 0
        )

        summary = handler.get_error_summary()

        assert summary["total_errors"] == 3
        assert summary["by_client"]["Client1"] == 2
        assert summary["by_client"]["Client2"] == 1
        assert summary["by_function"]["Function1"] == 2
        assert summary["by_function"]["Function2"] == 1
        assert len(summary["recent_errors"]) == 3

    def test_error_summary_with_time_filter(self):
        """Test error summary with time filtering."""
        handler = BAMLErrorHandler()

        # Record an old error
        old_time = datetime.now() - timedelta(hours=2)
        handler._record_error(
            Exception("Old error"), "Client1", "Function1", 0
        )
        handler._error_history[-1].timestamp = old_time

        # Record a recent error
        handler._record_error(
            Exception("Recent error"), "Client2", "Function2", 0
        )

        # Get summary for last hour only
        since = datetime.now() - timedelta(hours=1)
        summary = handler.get_error_summary(since=since)

        assert summary["total_errors"] == 1
        assert "Client2" in summary["by_client"]
        assert "Client1" not in summary["by_client"]

    def test_fallback_summary_empty(self):
        """Test fallback summary with no fallbacks."""
        handler = BAMLErrorHandler()

        summary = handler.get_fallback_summary()

        assert summary["total_fallbacks"] == 0
        assert summary["successful_fallbacks"] == 0
        assert summary["by_client"] == {}
        assert summary["recent_fallbacks"] == []

    def test_fallback_summary_with_fallbacks(self):
        """Test fallback summary with recorded fallbacks."""
        handler = BAMLErrorHandler()

        # Record some fallbacks
        handler._record_fallback(
            "Primary", "Fallback1", "Primary failed", True, 1.0
        )
        handler._record_fallback(
            "Primary", "Fallback2", "Fallback1 failed", False, 2.0
        )
        handler._record_fallback(
            "Primary", "Fallback1", "Primary failed", True, 1.5
        )

        summary = handler.get_fallback_summary()

        assert summary["total_fallbacks"] == 3
        assert summary["successful_fallbacks"] == 2
        assert summary["success_rate"] == pytest.approx(2/3)
        assert summary["by_client"]["Fallback1"] == 2
        assert summary["by_client"]["Fallback2"] == 1
        assert len(summary["recent_fallbacks"]) == 3

    def test_clear_history(self):
        """Test clearing error and fallback history."""
        handler = BAMLErrorHandler()

        # Record some data
        handler._record_error(
            Exception("Error"), "Client1", "Function1", 0
        )
        handler._record_fallback(
            "Primary", "Fallback", "Test", True, 1.0
        )

        assert len(handler._error_history) == 1
        assert len(handler._fallback_history) == 1

        # Clear all
        handler.clear_history()

        assert len(handler._error_history) == 0
        assert len(handler._fallback_history) == 0
        assert len(handler._error_counts) == 0

    def test_clear_history_with_time_filter(self):
        """Test clearing history with time filter."""
        handler = BAMLErrorHandler()

        # Record old data
        old_time = datetime.now() - timedelta(hours=2)
        handler._record_error(
            Exception("Old"), "Client1", "Function1", 0
        )
        handler._error_history[-1].timestamp = old_time

        # Record recent data
        handler._record_error(
            Exception("Recent"), "Client2", "Function2", 0
        )

        # Clear only old data
        cutoff = datetime.now() - timedelta(hours=1)
        handler.clear_history(before=cutoff)

        assert len(handler._error_history) == 1
        assert handler._error_history[0].client_name == "Client2"

    def test_reset_circuit_breakers(self):
        """Test resetting all circuit breakers."""
        handler = BAMLErrorHandler(enable_circuit_breaker=True, circuit_breaker_threshold=3)

        # Get circuit breakers for multiple clients (creates them)
        breaker1 = handler._get_circuit_breaker("Client1")
        breaker2 = handler._get_circuit_breaker("Client2")

        # Manually open them (need 3 failures based on threshold)
        breaker1.record_failure()
        breaker1.record_failure()
        breaker1.record_failure()
        breaker2.record_failure()
        breaker2.record_failure()
        breaker2.record_failure()

        assert breaker1.is_open()
        assert breaker2.is_open()

        # Reset all
        handler.reset_circuit_breakers()

        assert not breaker1.is_open()
        assert not breaker2.is_open()

    def test_circuit_breaker_disabled(self):
        """Test error handler with circuit breaker disabled."""
        handler = BAMLErrorHandler(enable_circuit_breaker=False)

        breaker = handler._get_circuit_breaker("TestClient")

        assert breaker is None