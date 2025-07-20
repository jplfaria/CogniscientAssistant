"""Unit tests for circuit breaker pattern."""

import asyncio
import pytest
from datetime import datetime, timedelta

from src.llm.circuit_breaker import CircuitBreaker, CircuitBreakerError, CircuitState


class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initialization."""
        breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60,
            half_open_max_calls=2
        )
        
        assert breaker.failure_threshold == 3
        assert breaker.recovery_timeout == 60
        assert breaker.half_open_max_calls == 2
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_successful_calls_in_closed_state(self):
        """Test successful calls keep circuit closed."""
        breaker = CircuitBreaker(failure_threshold=3)
        
        async def success_call():
            return "success"
        
        # Multiple successful calls
        for _ in range(5):
            result = await breaker.call(success_call)
            assert result == "success"
        
        # Circuit should remain closed
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold(self):
        """Test circuit opens after failure threshold."""
        breaker = CircuitBreaker(failure_threshold=3)
        
        async def failing_call():
            raise Exception("Failed")
        
        # First two failures
        for _ in range(2):
            with pytest.raises(Exception):
                await breaker.call(failing_call)
        
        # Circuit should still be closed
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 2
        
        # Third failure opens circuit
        with pytest.raises(Exception):
            await breaker.call(failing_call)
        
        assert breaker.state == CircuitState.OPEN
        assert breaker.failure_count == 3
    
    @pytest.mark.asyncio
    async def test_open_circuit_rejects_calls(self):
        """Test open circuit rejects calls immediately."""
        breaker = CircuitBreaker(failure_threshold=1)
        
        async def failing_call():
            raise Exception("Failed")
        
        # Open the circuit
        with pytest.raises(Exception):
            await breaker.call(failing_call)
        
        assert breaker.state == CircuitState.OPEN
        
        # Subsequent calls should be rejected
        async def normal_call():
            return "success"
        
        with pytest.raises(CircuitBreakerError) as exc_info:
            await breaker.call(normal_call)
        
        assert "Circuit breaker is OPEN" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_circuit_transitions_to_half_open(self):
        """Test circuit transitions to half-open after timeout."""
        breaker = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=0.1  # 100ms for testing
        )
        
        async def failing_call():
            raise Exception("Failed")
        
        # Open the circuit
        with pytest.raises(Exception):
            await breaker.call(failing_call)
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        await asyncio.sleep(0.15)
        
        # Check state transition
        assert breaker.state == CircuitState.HALF_OPEN
    
    @pytest.mark.asyncio
    async def test_half_open_success_closes_circuit(self):
        """Test successful calls in half-open state close circuit."""
        breaker = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=0.1,
            half_open_max_calls=2
        )
        
        async def failing_call():
            raise Exception("Failed")
        
        async def success_call():
            return "success"
        
        # Open the circuit
        with pytest.raises(Exception):
            await breaker.call(failing_call)
        
        # Wait for half-open
        await asyncio.sleep(0.15)
        assert breaker.state == CircuitState.HALF_OPEN
        
        # Successful calls in half-open
        for _ in range(2):
            result = await breaker.call(success_call)
            assert result == "success"
        
        # Circuit should be closed
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_half_open_failure_reopens_circuit(self):
        """Test failure in half-open state reopens circuit."""
        breaker = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=0.1
        )
        
        async def failing_call():
            raise Exception("Failed")
        
        # Open the circuit
        with pytest.raises(Exception):
            await breaker.call(failing_call)
        
        # Wait for half-open
        await asyncio.sleep(0.15)
        assert breaker.state == CircuitState.HALF_OPEN
        
        # Failure in half-open reopens
        with pytest.raises(Exception):
            await breaker.call(failing_call)
        
        assert breaker.state == CircuitState.OPEN
    
    def test_get_state_info(self):
        """Test getting circuit breaker state information."""
        breaker = CircuitBreaker(failure_threshold=3)
        
        info = breaker.get_state_info()
        assert info["state"] == "CLOSED"
        assert info["failure_count"] == 0
        assert info["failure_threshold"] == 3
        assert info["last_failure_time"] is None
    
    @pytest.mark.asyncio
    async def test_reset_circuit(self):
        """Test manual circuit reset."""
        breaker = CircuitBreaker(failure_threshold=1)
        
        async def failing_call():
            raise Exception("Failed")
        
        # Open the circuit
        with pytest.raises(Exception):
            await breaker.call(failing_call)
        
        assert breaker.state == CircuitState.OPEN
        
        # Manual reset
        breaker.reset()
        
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.last_failure_time is None