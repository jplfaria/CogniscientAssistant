"""Tests for the Mock LLM Provider."""

import pytest
import asyncio
from typing import Dict, Any
from datetime import datetime

from src.llm.base import LLMRequest, LLMResponse, LLMError
from src.llm.mock_provider import MockLLMProvider, MockResponse, MockConfiguration


class TestMockLLMProvider:
    """Test the MockLLMProvider implementation."""
    
    @pytest.mark.asyncio
    async def test_mock_provider_initialization(self):
        """Test that MockLLMProvider can be initialized."""
        provider = MockLLMProvider()
        assert provider is not None
        assert isinstance(provider.get_capabilities(), dict)
        assert isinstance(provider.get_model_info(), dict)
    
    @pytest.mark.asyncio
    async def test_mock_provider_generate(self):
        """Test generate method with mock responses."""
        provider = MockLLMProvider()
        
        request = LLMRequest(
            request_id="test-001",
            agent_type="generation",
            request_type="generate",
            content={
                "prompt": "Generate a hypothesis about cancer",
                "context": {},
                "parameters": {"temperature": 0.7}
            }
        )
        
        response = await provider.generate(request)
        
        assert isinstance(response, LLMResponse)
        assert response.request_id == "test-001"
        assert response.status == "success"
        assert response.response is not None
        assert "content" in response.response
        assert response.error is None
    
    @pytest.mark.asyncio
    async def test_mock_provider_analyze(self):
        """Test analyze method with mock responses."""
        provider = MockLLMProvider()
        
        request = LLMRequest(
            request_id="test-002",
            agent_type="reflection",
            request_type="analyze",
            content={
                "prompt": "Analyze this hypothesis for feasibility",
                "context": {"hypothesis": "Test hypothesis"},
                "parameters": {}
            }
        )
        
        response = await provider.analyze(request)
        
        assert isinstance(response, LLMResponse)
        assert response.request_id == "test-002"
        assert response.status == "success"
    
    @pytest.mark.asyncio
    async def test_mock_provider_evaluate(self):
        """Test evaluate method with mock responses."""
        provider = MockLLMProvider()
        
        request = LLMRequest(
            request_id="test-003",
            agent_type="ranking",
            request_type="evaluate",
            content={
                "prompt": "Evaluate hypothesis quality",
                "context": {"criteria": ["novelty", "feasibility"]},
                "parameters": {}
            }
        )
        
        response = await provider.evaluate(request)
        
        assert isinstance(response, LLMResponse)
        assert response.status == "success"
    
    @pytest.mark.asyncio
    async def test_mock_provider_compare(self):
        """Test compare method with mock responses."""
        provider = MockLLMProvider()
        
        request = LLMRequest(
            request_id="test-004",
            agent_type="ranking",
            request_type="compare",
            content={
                "prompt": "Compare these two hypotheses",
                "context": {"items": ["hypothesis1", "hypothesis2"]},
                "parameters": {}
            }
        )
        
        response = await provider.compare(request)
        
        assert isinstance(response, LLMResponse)
        assert response.status == "success"
    
    @pytest.mark.asyncio
    async def test_mock_provider_configurable_responses(self):
        """Test that mock provider can be configured with specific responses."""
        # Configure custom responses
        mock_config = MockConfiguration()
        mock_config.add_response(
            request_pattern={"agent_type": "generation", "request_type": "generate"},
            response=MockResponse(
                content="Custom generated hypothesis",
                metadata={"custom": "metadata"},
                delay=0.1
            )
        )
        
        provider = MockLLMProvider(configuration=mock_config)
        
        request = LLMRequest(
            request_id="test-005",
            agent_type="generation",
            request_type="generate",
            content={
                "prompt": "Generate something",
                "context": {},
                "parameters": {}
            }
        )
        
        start_time = datetime.now()
        response = await provider.generate(request)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # Check custom response
        assert response.response["content"] == "Custom generated hypothesis"
        assert response.response["metadata"]["custom"] == "metadata"
        
        # Check delay was applied
        assert elapsed >= 0.1
    
    @pytest.mark.asyncio
    async def test_mock_provider_error_simulation(self):
        """Test that mock provider can simulate errors."""
        mock_config = MockConfiguration()
        mock_config.add_error(
            request_pattern={"request_type": "generate"},
            error=LLMError(
                code="rate_limit_exceeded",
                message="Simulated rate limit",
                recoverable=True
            )
        )
        
        provider = MockLLMProvider(configuration=mock_config)
        
        request = LLMRequest(
            request_id="test-006",
            agent_type="generation",
            request_type="generate",
            content={
                "prompt": "This should fail",
                "context": {},
                "parameters": {}
            }
        )
        
        response = await provider.generate(request)
        
        assert response.status == "error"
        assert response.error is not None
        assert response.error.code == "rate_limit_exceeded"
        assert response.error.recoverable is True
    
    @pytest.mark.asyncio
    async def test_mock_provider_sequence_responses(self):
        """Test that mock provider can return different responses in sequence."""
        mock_config = MockConfiguration()
        mock_config.add_sequence(
            request_pattern={"agent_type": "generation"},
            responses=[
                MockResponse(content="First response"),
                MockResponse(content="Second response"),
                MockResponse(content="Third response"),
            ]
        )
        
        provider = MockLLMProvider(configuration=mock_config)
        
        # Make three requests
        for i, expected_content in enumerate(["First response", "Second response", "Third response"]):
            request = LLMRequest(
                request_id=f"test-00{i}",
                agent_type="generation",
                request_type="generate",
                content={
                    "prompt": "Generate",
                    "context": {},
                    "parameters": {}
                }
            )
            
            response = await provider.generate(request)
            assert response.response["content"] == expected_content
    
    def test_mock_provider_capabilities(self):
        """Test that mock provider reports appropriate capabilities."""
        provider = MockLLMProvider()
        capabilities = provider.get_capabilities()
        
        assert "max_context" in capabilities
        assert "multimodal" in capabilities
        assert "streaming" in capabilities
        assert "function_calling" in capabilities
        
        # Mock should have reasonable defaults
        assert capabilities["max_context"] >= 10000
        assert isinstance(capabilities["multimodal"], bool)
    
    def test_mock_provider_model_info(self):
        """Test that mock provider reports model information."""
        provider = MockLLMProvider()
        model_info = provider.get_model_info()
        
        assert "name" in model_info
        assert "version" in model_info
        assert "provider" in model_info
        
        assert model_info["provider"] == "mock"
    
    @pytest.mark.asyncio
    async def test_mock_provider_async_behavior(self):
        """Test that mock provider properly handles async operations."""
        provider = MockLLMProvider()
        
        # Create multiple requests
        requests = []
        for i in range(5):
            request = LLMRequest(
                request_id=f"async-{i}",
                agent_type="generation",
                request_type="generate",
                content={
                    "prompt": f"Generate {i}",
                    "context": {},
                    "parameters": {}
                }
            )
            requests.append(request)
        
        # Execute concurrently
        responses = await asyncio.gather(*[provider.generate(req) for req in requests])
        
        # Verify all responses
        assert len(responses) == 5
        for i, response in enumerate(responses):
            assert response.request_id == f"async-{i}"
            assert response.status == "success"
    
    @pytest.mark.asyncio
    async def test_mock_provider_default_generation(self):
        """Test default content generation for different agent types."""
        provider = MockLLMProvider()
        
        # Test generation agent
        request = LLMRequest(
            request_id="test-gen",
            agent_type="generation",
            request_type="generate",
            content={
                "prompt": "Test prompt for generation",
                "context": {},
                "parameters": {}
            }
        )
        response = await provider.generate(request)
        assert "Mock hypothesis generated" in response.response["content"]
        
        # Test evolution agent
        request = LLMRequest(
            request_id="test-evo",
            agent_type="evolution",
            request_type="generate",
            content={
                "prompt": "Test prompt for evolution",
                "context": {},
                "parameters": {}
            }
        )
        response = await provider.generate(request)
        assert "Mock evolved hypothesis" in response.response["content"]
        
        # Test other agent type
        request = LLMRequest(
            request_id="test-other",
            agent_type="ranking",
            request_type="generate",
            content={
                "prompt": "Test prompt",
                "context": {},
                "parameters": {}
            }
        )
        response = await provider.generate(request)
        assert "Mock generated content for ranking agent" in response.response["content"]
    
    @pytest.mark.asyncio
    async def test_mock_provider_default_analysis(self):
        """Test default content analysis for different agent types."""
        provider = MockLLMProvider()
        
        # Test reflection agent
        request = LLMRequest(
            request_id="test-ref",
            agent_type="reflection",
            request_type="analyze",
            content={
                "prompt": "Analyze this",
                "context": {},
                "parameters": {}
            }
        )
        response = await provider.analyze(request)
        assert "hypothesis shows promise" in response.response["content"]
        
        # Test meta-review agent
        request = LLMRequest(
            request_id="test-meta",
            agent_type="meta-review",
            request_type="analyze",
            content={
                "prompt": "Analyze overall",
                "context": {},
                "parameters": {}
            }
        )
        response = await provider.analyze(request)
        assert "research direction is sound" in response.response["content"]