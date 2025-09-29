"""Unit tests for Argo provider reliability features."""

import asyncio
import pytest
from unittest.mock import AsyncMock, Mock

from src.llm.argo_provider import ArgoLLMProvider
from src.llm.circuit_breaker import CircuitBreakerError, CircuitState


class TestArgoReliability:
    """Test reliability features of Argo provider."""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_initialization(self):
        """Test circuit breakers are initialized for each model."""
        provider = ArgoLLMProvider()
        
        # Check circuit breakers exist for each model
        status = provider.get_circuit_breaker_status()
        
        assert "gpt4o" in status
        assert "gpt35" in status
        assert "claudeopus4" in status
        
        # All should be closed initially
        for model, info in status.items():
            assert info["state"] == "CLOSED"
            assert info["failure_count"] == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after threshold failures."""
        provider = ArgoLLMProvider()
        
        # Mock failing HTTP calls
        async def failing_call(*args, **kwargs):
            raise Exception("Connection failed")
        
        # Simulate failures for a specific model
        model = "gpt4o"
        
        # First two failures (threshold is 3)
        for _ in range(2):
            with pytest.raises(Exception):
                await provider._call_with_circuit_breaker(model, failing_call)
        
        # Check still closed
        status = provider.get_circuit_breaker_status()[model]
        assert status["state"] == "CLOSED"
        assert status["failure_count"] == 2
        
        # Third failure opens circuit
        with pytest.raises(Exception):
            await provider._call_with_circuit_breaker(model, failing_call)
        
        # Small delay to ensure state updates
        await asyncio.sleep(0.01)
        
        # Check circuit is open
        status = provider.get_circuit_breaker_status()[model]
        assert status["state"] == "OPEN"
        assert status["failure_count"] == 3
        
        # Model should be marked unavailable after circuit opens
        # Actually, with current implementation, model is only marked unavailable 
        # when we try to call through open circuit (CircuitBreakerError)
        # Let's try another call to trigger the unavailability
        with pytest.raises(CircuitBreakerError):
            await provider._call_with_circuit_breaker(model, failing_call)
        
        # Now model should be unavailable
        assert model not in provider.model_selector.available_models
    
    @pytest.mark.asyncio
    async def test_failover_to_alternate_model(self):
        """Test failover to alternate model when primary fails."""
        provider = ArgoLLMProvider()
        
        # Open circuit for primary model
        provider._circuit_breakers["claudeopus4"]._state = CircuitState.OPEN
        provider.model_selector.mark_model_unavailable("claudeopus4")
        
        # Request generation task (prefers claude-opus-4)
        selected = await provider.select_model_with_failover("generation")
        
        # Should failover to gpt4o
        assert selected == "gpt4o"
    
    @pytest.mark.asyncio
    async def test_no_models_available_error(self):
        """Test error when no models are available."""
        provider = ArgoLLMProvider()
        
        # Mark all models as unavailable
        # Create a copy to avoid RuntimeError during iteration
        models_to_disable = list(provider.model_selector.available_models)
        for model in models_to_disable:
            provider._circuit_breakers[model]._state = CircuitState.OPEN
            provider.model_selector.mark_model_unavailable(model)
        
        # Should raise error
        with pytest.raises(ValueError) as exc_info:
            await provider.select_model_with_failover("generation")
        
        assert "No models available" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_reset(self):
        """Test manual circuit breaker reset."""
        provider = ArgoLLMProvider()
        
        # Open a circuit
        model = "gpt4o"
        provider._circuit_breakers[model]._state = CircuitState.OPEN
        provider._circuit_breakers[model]._failure_count = 3
        
        # Reset circuit
        provider.reset_circuit_breaker(model)
        
        # Check reset
        status = provider.get_circuit_breaker_status()[model]
        assert status["state"] == "CLOSED"
        assert status["failure_count"] == 0
    
    @pytest.mark.asyncio
    async def test_successful_calls_keep_circuit_closed(self):
        """Test successful calls keep circuit closed."""
        provider = ArgoLLMProvider()
        
        # Mock successful call
        async def success_call(*args, **kwargs):
            return {"result": "success"}
        
        model = "gpt4o"
        
        # Multiple successful calls
        for _ in range(5):
            result = await provider._call_with_circuit_breaker(model, success_call)
            assert result["result"] == "success"
        
        # Circuit should remain closed
        status = provider.get_circuit_breaker_status()[model]
        assert status["state"] == "CLOSED"
        assert status["failure_count"] == 0
    
    @pytest.mark.asyncio
    async def test_preferred_model_selection(self):
        """Test preferred model is selected when available."""
        provider = ArgoLLMProvider()
        
        # Prefer a specific model
        selected = await provider.select_model_with_failover(
            "generation",
            preferred_model="gpt4o"
        )
        
        assert selected == "gpt4o"
        
        # Open circuit for preferred model
        provider._circuit_breakers["gpt4o"]._state = CircuitState.OPEN
        
        # Should select alternate
        selected = await provider.select_model_with_failover(
            "generation",
            preferred_model="gpt4o"
        )
        
        assert selected != "gpt4o"
        assert selected == "claudeopus4"  # Next preference for generation