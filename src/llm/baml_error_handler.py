"""Enhanced error handling for BAML operations with fallback history.

This module provides comprehensive error handling for BAML function calls,
including:
- Automatic retry with exponential backoff
- Fallback client selection
- Error history tracking
- Model-specific error handling
- Circuit breaker integration
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, TypeVar, Coroutine, Tuple
from enum import Enum
from dataclasses import dataclass, field

from .circuit_breaker import CircuitBreaker, CircuitBreakerError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ErrorCategory(Enum):
    """Categories of BAML errors."""
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    INVALID_REQUEST = "invalid_request"
    MODEL_ERROR = "model_error"
    NETWORK_ERROR = "network_error"
    AUTHENTICATION = "authentication"
    UNKNOWN = "unknown"


@dataclass
class ErrorRecord:
    """Record of a single error occurrence."""
    timestamp: datetime
    error_category: ErrorCategory
    error_message: str
    client_name: str
    function_name: str
    retry_attempt: int
    recoverable: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FallbackAttempt:
    """Record of a fallback attempt."""
    timestamp: datetime
    from_client: str
    to_client: str
    reason: str
    success: bool
    duration: float


class BAMLErrorHandler:
    """Enhanced error handler for BAML operations with fallback support."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        enable_circuit_breaker: bool = True,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 60.0,
    ):
        """Initialize the error handler.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff
            max_delay: Maximum delay between retries
            exponential_base: Base for exponential backoff calculation
            enable_circuit_breaker: Whether to use circuit breaker
            circuit_breaker_threshold: Failures before opening circuit
            circuit_breaker_timeout: Seconds before attempting recovery
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

        # Error tracking
        self._error_history: List[ErrorRecord] = []
        self._fallback_history: List[FallbackAttempt] = []
        self._error_counts: Dict[str, int] = {}

        # Circuit breakers per client
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._enable_circuit_breaker = enable_circuit_breaker
        self._circuit_breaker_threshold = circuit_breaker_threshold
        self._circuit_breaker_timeout = circuit_breaker_timeout

        # Fallback client ordering (from most to least preferred)
        self._fallback_clients: List[str] = [
            "ProductionClient",
            "ArgoClaudeOpus4",
            "ArgoGPT4o",
            "ArgoClaudeSonnet4",
            "ArgoGemini25Pro",
            "DefaultClient",
        ]

    def _get_circuit_breaker(self, client_name: str) -> Optional[CircuitBreaker]:
        """Get or create circuit breaker for a client.

        Args:
            client_name: Name of the BAML client

        Returns:
            Circuit breaker instance or None if disabled
        """
        if not self._enable_circuit_breaker:
            return None

        if client_name not in self._circuit_breakers:
            self._circuit_breakers[client_name] = CircuitBreaker(
                failure_threshold=self._circuit_breaker_threshold,
                recovery_timeout=self._circuit_breaker_timeout,
            )

        return self._circuit_breakers[client_name]

    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize an error for appropriate handling.

        Args:
            error: The exception that occurred

        Returns:
            Error category
        """
        error_str = str(error).lower()

        if "timeout" in error_str or "timed out" in error_str:
            return ErrorCategory.TIMEOUT
        elif "rate limit" in error_str or "429" in error_str:
            return ErrorCategory.RATE_LIMIT
        elif "invalid request" in error_str or "400" in error_str:
            return ErrorCategory.INVALID_REQUEST
        elif "authentication" in error_str or "401" in error_str or "403" in error_str:
            return ErrorCategory.AUTHENTICATION
        elif "network" in error_str or "connection" in error_str:
            return ErrorCategory.NETWORK_ERROR
        elif "model" in error_str:
            return ErrorCategory.MODEL_ERROR
        else:
            return ErrorCategory.UNKNOWN

    def _is_recoverable(self, category: ErrorCategory) -> bool:
        """Determine if an error category is recoverable.

        Args:
            category: Error category

        Returns:
            True if error is likely recoverable with retry
        """
        recoverable_categories = {
            ErrorCategory.TIMEOUT,
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.NETWORK_ERROR,
            ErrorCategory.MODEL_ERROR,
            ErrorCategory.UNKNOWN,
        }
        return category in recoverable_categories

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for exponential backoff.

        Args:
            attempt: Current retry attempt (0-indexed)

        Returns:
            Delay in seconds
        """
        delay = self.base_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)

    def _record_error(
        self,
        error: Exception,
        client_name: str,
        function_name: str,
        retry_attempt: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ErrorRecord:
        """Record an error occurrence.

        Args:
            error: The exception that occurred
            client_name: Name of the BAML client
            function_name: Name of the BAML function
            retry_attempt: Current retry attempt
            metadata: Additional error context

        Returns:
            Error record
        """
        category = self._categorize_error(error)
        recoverable = self._is_recoverable(category)

        record = ErrorRecord(
            timestamp=datetime.now(),
            error_category=category,
            error_message=str(error),
            client_name=client_name,
            function_name=function_name,
            retry_attempt=retry_attempt,
            recoverable=recoverable,
            metadata=metadata or {},
        )

        self._error_history.append(record)

        # Update error counts
        key = f"{client_name}:{function_name}"
        self._error_counts[key] = self._error_counts.get(key, 0) + 1

        logger.warning(
            f"BAML error recorded - Client: {client_name}, Function: {function_name}, "
            f"Category: {category.value}, Attempt: {retry_attempt}, Recoverable: {recoverable}, "
            f"Error: {str(error)[:200]}"
        )

        return record

    def _record_fallback(
        self,
        from_client: str,
        to_client: str,
        reason: str,
        success: bool,
        duration: float,
    ):
        """Record a fallback attempt.

        Args:
            from_client: Original client name
            to_client: Fallback client name
            reason: Reason for fallback
            success: Whether fallback succeeded
            duration: Time taken in seconds
        """
        attempt = FallbackAttempt(
            timestamp=datetime.now(),
            from_client=from_client,
            to_client=to_client,
            reason=reason,
            success=success,
            duration=duration,
        )

        self._fallback_history.append(attempt)

        logger.info(
            f"BAML fallback - From: {from_client} -> To: {to_client}, "
            f"Reason: {reason}, Success: {success}, Duration: {duration:.2f}s"
        )

    async def call_with_retry(
        self,
        func: Callable[..., Coroutine[Any, Any, T]],
        client_name: str,
        function_name: str,
        *args,
        **kwargs,
    ) -> T:
        """Call a BAML function with automatic retry and error handling.

        Args:
            func: Async BAML function to call
            client_name: Name of the BAML client being used
            function_name: Name of the BAML function being called
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from successful function call

        Raises:
            Exception: Last exception if all retries fail
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                # Check circuit breaker
                circuit_breaker = self._get_circuit_breaker(client_name)
                if circuit_breaker and circuit_breaker.is_open():
                    raise CircuitBreakerError(
                        f"Circuit breaker open for client {client_name}"
                    )

                # Execute the function
                logger.debug(
                    f"Calling BAML - Client: {client_name}, Function: {function_name}, "
                    f"Attempt: {attempt + 1}/{self.max_retries + 1}"
                )

                result = await func(*args, **kwargs)

                # Success - record in circuit breaker
                if circuit_breaker:
                    circuit_breaker.record_success()

                if attempt > 0:
                    logger.info(
                        f"BAML call succeeded after {attempt} retries - "
                        f"Client: {client_name}, Function: {function_name}"
                    )

                return result

            except Exception as e:
                last_error = e

                # Record error
                error_record = self._record_error(
                    e, client_name, function_name, attempt
                )

                # Record in circuit breaker
                if circuit_breaker:
                    circuit_breaker.record_failure()

                # Check if we should retry
                if attempt < self.max_retries and error_record.recoverable:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"BAML call failed, retrying in {delay:.2f}s - "
                        f"Client: {client_name}, Function: {function_name}, "
                        f"Error: {str(e)[:200]}"
                    )
                    await asyncio.sleep(delay)
                else:
                    # Final failure
                    logger.error(
                        f"BAML call failed after {attempt + 1} attempts - "
                        f"Client: {client_name}, Function: {function_name}, "
                        f"Error: {str(e)[:200]}"
                    )
                    raise

        # Should not reach here, but raise last error if we do
        if last_error:
            raise last_error

    async def call_with_fallback(
        self,
        func_factory: Callable[[str], Callable[..., Coroutine[Any, Any, T]]],
        function_name: str,
        preferred_client: str,
        *args,
        **kwargs,
    ) -> Tuple[T, str]:
        """Call a BAML function with automatic fallback to alternative clients.

        Args:
            func_factory: Function that creates BAML function for a given client
            function_name: Name of the BAML function
            preferred_client: Preferred client to try first
            *args: Positional arguments for BAML function
            **kwargs: Keyword arguments for BAML function

        Returns:
            Tuple of (result, client_name) indicating result and which client succeeded

        Raises:
            Exception: If all clients fail
        """
        # Build client list with preferred client first
        client_order = [preferred_client] + [
            c for c in self._fallback_clients if c != preferred_client
        ]

        last_error = None

        for client_name in client_order:
            start_time = datetime.now()

            try:
                # Get function for this client
                func = func_factory(client_name)

                # Try with retry
                result = await self.call_with_retry(
                    func, client_name, function_name, *args, **kwargs
                )

                duration = (datetime.now() - start_time).total_seconds()

                # Record successful fallback if not the preferred client
                if client_name != preferred_client:
                    self._record_fallback(
                        from_client=preferred_client,
                        to_client=client_name,
                        reason="Primary client failed",
                        success=True,
                        duration=duration,
                    )

                return result, client_name

            except Exception as e:
                last_error = e
                duration = (datetime.now() - start_time).total_seconds()

                logger.warning(
                    f"Client {client_name} failed for {function_name}, "
                    f"trying next fallback: {str(e)[:200]}"
                )

                # Record failed fallback if not the first client
                if client_name != preferred_client:
                    self._record_fallback(
                        from_client=preferred_client,
                        to_client=client_name,
                        reason="Primary client failed",
                        success=False,
                        duration=duration,
                    )

        # All clients failed
        logger.error(
            f"All fallback clients failed for {function_name}. "
            f"Last error: {str(last_error)[:200]}"
        )

        if last_error:
            raise last_error
        else:
            raise RuntimeError(f"All clients failed for {function_name}")

    def get_error_summary(
        self,
        since: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get summary of error history.

        Args:
            since: Only include errors after this time (default: all)

        Returns:
            Dictionary with error statistics
        """
        errors = self._error_history
        if since:
            errors = [e for e in errors if e.timestamp >= since]

        if not errors:
            return {
                "total_errors": 0,
                "by_category": {},
                "by_client": {},
                "by_function": {},
                "recent_errors": [],
            }

        # Count by category
        by_category = {}
        for error in errors:
            category = error.error_category.value
            by_category[category] = by_category.get(category, 0) + 1

        # Count by client
        by_client = {}
        for error in errors:
            by_client[error.client_name] = by_client.get(error.client_name, 0) + 1

        # Count by function
        by_function = {}
        for error in errors:
            by_function[error.function_name] = by_function.get(error.function_name, 0) + 1

        # Get recent errors (last 10)
        recent_errors = [
            {
                "timestamp": e.timestamp.isoformat(),
                "category": e.error_category.value,
                "client": e.client_name,
                "function": e.function_name,
                "message": e.error_message[:200],
                "recoverable": e.recoverable,
            }
            for e in sorted(errors, key=lambda x: x.timestamp, reverse=True)[:10]
        ]

        return {
            "total_errors": len(errors),
            "by_category": by_category,
            "by_client": by_client,
            "by_function": by_function,
            "recent_errors": recent_errors,
        }

    def get_fallback_summary(
        self,
        since: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get summary of fallback history.

        Args:
            since: Only include fallbacks after this time (default: all)

        Returns:
            Dictionary with fallback statistics
        """
        fallbacks = self._fallback_history
        if since:
            fallbacks = [f for f in fallbacks if f.timestamp >= since]

        if not fallbacks:
            return {
                "total_fallbacks": 0,
                "successful_fallbacks": 0,
                "by_client": {},
                "recent_fallbacks": [],
            }

        successful = sum(1 for f in fallbacks if f.success)

        # Count by target client
        by_client = {}
        for fallback in fallbacks:
            by_client[fallback.to_client] = by_client.get(fallback.to_client, 0) + 1

        # Get recent fallbacks (last 10)
        recent_fallbacks = [
            {
                "timestamp": f.timestamp.isoformat(),
                "from": f.from_client,
                "to": f.to_client,
                "reason": f.reason,
                "success": f.success,
                "duration": f.duration,
            }
            for f in sorted(fallbacks, key=lambda x: x.timestamp, reverse=True)[:10]
        ]

        return {
            "total_fallbacks": len(fallbacks),
            "successful_fallbacks": successful,
            "success_rate": successful / len(fallbacks) if fallbacks else 0.0,
            "by_client": by_client,
            "recent_fallbacks": recent_fallbacks,
        }

    def clear_history(self, before: Optional[datetime] = None):
        """Clear error and fallback history.

        Args:
            before: Only clear entries before this time (default: clear all)
        """
        if before:
            self._error_history = [
                e for e in self._error_history if e.timestamp >= before
            ]
            self._fallback_history = [
                f for f in self._fallback_history if f.timestamp >= before
            ]
        else:
            self._error_history.clear()
            self._fallback_history.clear()
            self._error_counts.clear()

        logger.info(f"Cleared error history before {before or 'all time'}")

    def reset_circuit_breakers(self):
        """Reset all circuit breakers to closed state."""
        for client_name, breaker in self._circuit_breakers.items():
            breaker.reset()
            logger.info(f"Reset circuit breaker for {client_name}")