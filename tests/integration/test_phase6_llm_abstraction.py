"""Phase 6 Integration Tests: LLM Abstraction Layer."""

import pytest
import asyncio
from typing import Dict, Any, List

from src.llm import (
    LLMProvider, LLMRequest, LLMResponse, LLMError,
    MockLLMProvider, MockConfiguration, MockResponse,
    RateLimitConfig, TokenBucketRateLimiter,
    ModelCapabilities, CapabilityManager, ModelRegistry,
    validate_request
)
from src.core.models import Task, TaskType, TaskState
from src.core.task_queue import TaskQueue
from src.core.context_memory import ContextMemory


class TestLLMAbstractionInterface:
    """Test the LLM abstraction interface."""
    
    @pytest.mark.asyncio
    async def test_llm_abstraction_interface(self):
        """Test that the LLM abstraction provides uniform interface."""
        # Create mock provider
        provider = MockLLMProvider()
        
        # Test all request types
        request_types = ["generate", "analyze", "evaluate", "compare"]
        
        for req_type in request_types:
            request = LLMRequest(
                request_id=f"test-{req_type}",
                agent_type="generation",
                request_type=req_type,
                content={
                    "prompt": f"Test {req_type} request",
                    "context": {},
                    "parameters": {"temperature": 0.7}
                }
            )
            
            # All request types should work through the provider
            if req_type == "generate":
                response = await provider.generate(request)
            elif req_type == "analyze":
                response = await provider.analyze(request)
            elif req_type == "evaluate":
                response = await provider.evaluate(request)
            elif req_type == "compare":
                response = await provider.compare(request)
            
            # Response should have consistent structure
            assert isinstance(response, LLMResponse)
            assert response.request_id == f"test-{req_type}"
            assert response.status in ["success", "error", "partial"]
            if response.status == "success":
                assert response.response is not None
                assert "content" in response.response
                assert "metadata" in response.response
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting functionality."""
        config = RateLimitConfig(
            requests_per_minute=10,
            concurrent_requests=3
        )
        
        limiter = TokenBucketRateLimiter(config)
        
        # Test request rate limiting
        successful = 0
        limited = 0
        
        for i in range(15):
            if await limiter.acquire():
                successful += 1
            else:
                limited += 1
        
        assert successful == 10  # Should respect rate limit
        assert limited == 5
        
        # Test concurrent request limiting
        async def simulate_concurrent():
            async with limiter.concurrent_request():
                await asyncio.sleep(0.1)
                return True
        
        # Start max concurrent requests
        tasks = []
        for _ in range(3):
            tasks.append(asyncio.create_task(simulate_concurrent()))
        
        # Give tasks time to start
        await asyncio.sleep(0.05)
        
        # Additional request should be blocked
        from src.llm.rate_limiter import RateLimitExceeded
        with pytest.raises(RateLimitExceeded):
            async with limiter.concurrent_request():
                pass
        
        # Wait for tasks to complete
        await asyncio.gather(*tasks)
    
    def test_model_capability_tracking(self):
        """Test model capability tracking and routing."""
        manager = CapabilityManager()
        
        # Register models with different capabilities
        manager.register_model("small-model", ModelCapabilities(
            max_context=4000,
            multimodal=False,
            cost_per_1k_input_tokens=0.001
        ))
        
        manager.register_model("large-model", ModelCapabilities(
            max_context=100000,
            multimodal=True,
            cost_per_1k_input_tokens=0.01
        ))
        
        # Find suitable models for different requirements
        # Small request - both models should work
        suitable = manager.find_suitable_models(context_size=2000)
        assert len(suitable) == 2
        
        # Large context - only large model
        suitable = manager.find_suitable_models(context_size=50000)
        assert len(suitable) == 1
        assert suitable[0] == "large-model"
        
        # Multimodal request - only large model
        suitable = manager.find_suitable_models(
            context_size=1000,
            requires_multimodal=True
        )
        assert len(suitable) == 1
        assert suitable[0] == "large-model"
        
        # Find cheapest model
        cheapest = manager.find_cheapest_model(
            context_size=2000,
            estimated_output_tokens=1000
        )
        assert cheapest == "small-model"
    
    @pytest.mark.asyncio
    async def test_context_management(self):
        """Test context window management."""
        provider = MockLLMProvider()
        capabilities = provider.get_capabilities()
        
        # Test that provider reports context limits
        assert "max_context" in capabilities
        assert capabilities["max_context"] > 0
        
        # Test request validation considers context size
        large_context = {
            "data": ["x" * 1000] * 100  # Large context
        }
        
        request = LLMRequest(
            request_id="test-context",
            agent_type="generation",
            request_type="generate",
            content={
                "prompt": "Test with large context",
                "context": large_context,
                "parameters": {"max_length": 1000}
            }
        )
        
        # Should handle large context appropriately
        response = await provider.generate(request)
        assert response.status == "success"
    
    @pytest.mark.asyncio
    async def test_provider_failover(self):
        """Test failover between providers."""
        # Configure primary provider to fail
        primary_config = MockConfiguration()
        primary_config.add_error(
            request_pattern={"request_type": "generate"},
            error=LLMError(
                code="model_unavailable",
                message="Primary model unavailable",
                recoverable=True
            )
        )
        
        primary = MockLLMProvider(configuration=primary_config)
        fallback = MockLLMProvider()
        
        # Simple failover logic
        async def generate_with_failover(request: LLMRequest) -> LLMResponse:
            response = await primary.generate(request)
            if response.status == "error" and response.error.recoverable:
                # Try fallback
                return await fallback.generate(request)
            return response
        
        request = LLMRequest(
            request_id="test-failover",
            agent_type="generation",
            request_type="generate",
            content={
                "prompt": "Test failover",
                "context": {},
                "parameters": {}
            }
        )
        
        response = await generate_with_failover(request)
        
        # Should succeed with fallback
        assert response.status == "success"
        assert response.response is not None
    
    def test_request_transformation(self):
        """Test request validation and transformation."""
        # Test valid request
        request_data = {
            "request_id": "test-001",
            "agent_type": "generation",
            "request_type": "generate",
            "content": {
                "prompt": "Generate hypothesis",
                "context": {"domain": "cancer research"},
                "parameters": {"temperature": 0.8}
            }
        }
        
        validated = validate_request(request_data)
        assert validated["request_id"] == "test-001"
        
        # Test request with injection attempt
        malicious_request = {
            "request_id": "test<script>alert('xss')</script>",
            "agent_type": "generation",
            "request_type": "generate",
            "content": {
                "prompt": "Normal prompt",
                "context": {},
                "parameters": {}
            }
        }
        
        sanitized = validate_request(malicious_request)
        assert "<script>" not in sanitized["request_id"]
        
        # Test invalid request
        invalid_request = {
            "request_id": "test",
            "agent_type": "invalid",
            "request_type": "generate",
            "content": {}
        }
        
        with pytest.raises(ValueError):
            validate_request(invalid_request)


class TestCachingAndOptimization:
    """Test response caching and optimization (may_fail tests)."""
    
    @pytest.mark.asyncio
    async def test_smart_context_truncation(self):
        """Test intelligent context truncation when exceeding limits."""
        # This is a may_fail test - implement when context truncation is added
        pytest.skip("Context truncation not yet implemented")
        
        provider = MockLLMProvider()
        
        # Create request with context exceeding limits
        huge_context = {
            "history": ["item"] * 10000,
            "important": "This should be preserved",
            "metadata": {"priority": "high"}
        }
        
        request = LLMRequest(
            request_id="test-truncate",
            agent_type="generation",
            request_type="generate",
            content={
                "prompt": "Generate with huge context",
                "context": huge_context,
                "parameters": {"preserve": ["important"]}
            }
        )
        
        response = await provider.generate(request)
        
        # Should succeed with truncated context
        assert response.status == "success"
        # Important data should be preserved
        # Implementation would verify this
    
    @pytest.mark.asyncio
    async def test_llm_response_caching(self):
        """Test caching of LLM responses for efficiency."""
        # This is a may_fail test - implement when caching is added
        pytest.skip("Response caching not yet implemented")
        
        # Would test:
        # 1. Identical requests return cached responses
        # 2. Cache expiration
        # 3. Cache size limits
        # 4. Cache key generation