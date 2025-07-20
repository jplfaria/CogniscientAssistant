"""Circuit breaker pattern implementation for fault tolerance."""

import asyncio
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar, Coroutine


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Failures exceeded threshold, rejecting calls
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass


T = TypeVar('T')


class CircuitBreaker:
    """Circuit breaker for fault tolerance.
    
    Prevents cascading failures by monitoring error rates and temporarily
    blocking calls to failing services.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3
    ):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying half-open
            half_open_max_calls: Max calls allowed in half-open state
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._half_open_calls = 0
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state, checking for automatic transitions."""
        if self._state == CircuitState.OPEN and self._last_failure_time:
            # Check if recovery timeout has passed
            if datetime.now() - self._last_failure_time > timedelta(seconds=self.recovery_timeout):
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
        return self._state
    
    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count
    
    @property
    def last_failure_time(self) -> Optional[datetime]:
        """Get time of last failure."""
        return self._last_failure_time
    
    async def call(
        self,
        func: Callable[..., Coroutine[Any, Any, T]],
        *args,
        **kwargs
    ) -> T:
        """Execute function through circuit breaker.
        
        Args:
            func: Async function to call
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result from func
            
        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Any exception from func
        """
        async with self._lock:
            # Check current state
            current_state = self.state
            
            if current_state == CircuitState.OPEN:
                raise CircuitBreakerError(
                    f"Circuit breaker is OPEN. Last failure: {self._last_failure_time}"
                )
            
            if current_state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.half_open_max_calls:
                    # Wait for other half-open calls to complete
                    raise CircuitBreakerError(
                        "Circuit breaker is HALF_OPEN but max calls reached"
                    )
                self._half_open_calls += 1
        
        # Execute the function
        try:
            result = await func(*args, **kwargs)
            
            # Success - update state
            async with self._lock:
                if self._state == CircuitState.HALF_OPEN:
                    # Successful call in half-open, check if we can close
                    if self._half_open_calls >= self.half_open_max_calls:
                        self._state = CircuitState.CLOSED
                        self._failure_count = 0
                        self._last_failure_time = None
                elif self._state == CircuitState.CLOSED:
                    # Reset failure count on success
                    self._failure_count = 0
            
            return result
            
        except Exception as e:
            # Failure - update state
            async with self._lock:
                self._failure_count += 1
                self._last_failure_time = datetime.now()
                
                if self._state == CircuitState.HALF_OPEN:
                    # Failure in half-open immediately opens circuit
                    self._state = CircuitState.OPEN
                elif self._state == CircuitState.CLOSED:
                    # Check if we've exceeded threshold
                    if self._failure_count >= self.failure_threshold:
                        self._state = CircuitState.OPEN
            
            # Re-raise the original exception
            raise
    
    def reset(self):
        """Manually reset the circuit breaker to closed state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._half_open_calls = 0
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get current state information.
        
        Returns:
            Dictionary with state details
        """
        return {
            "state": self._state.value,
            "failure_count": self._failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self._last_failure_time.isoformat() if self._last_failure_time else None,
            "recovery_timeout": self.recovery_timeout,
            "half_open_calls": self._half_open_calls if self._state == CircuitState.HALF_OPEN else 0
        }