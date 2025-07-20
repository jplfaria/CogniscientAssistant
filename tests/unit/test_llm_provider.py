"""Tests for the LLM Provider abstract class and interface."""

import pytest
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from src.llm.base import LLMProvider, LLMRequest, LLMResponse, LLMError


class TestLLMProvider:
    """Test the LLMProvider abstract base class."""
    
    def test_llm_provider_is_abstract(self):
        """Test that LLMProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            LLMProvider()
    
    def test_llm_provider_defines_required_methods(self):
        """Test that LLMProvider defines all required abstract methods."""
        # Check that the abstract methods exist
        assert hasattr(LLMProvider, 'generate')
        assert hasattr(LLMProvider, 'analyze')
        assert hasattr(LLMProvider, 'evaluate')
        assert hasattr(LLMProvider, 'compare')
        assert hasattr(LLMProvider, 'get_capabilities')
        assert hasattr(LLMProvider, 'get_model_info')
        
        # Verify they are abstract
        assert getattr(LLMProvider.generate, '__isabstractmethod__', False)
        assert getattr(LLMProvider.analyze, '__isabstractmethod__', False)
        assert getattr(LLMProvider.evaluate, '__isabstractmethod__', False)
        assert getattr(LLMProvider.compare, '__isabstractmethod__', False)
        assert getattr(LLMProvider.get_capabilities, '__isabstractmethod__', False)
        assert getattr(LLMProvider.get_model_info, '__isabstractmethod__', False)


class TestLLMRequest:
    """Test the LLMRequest data structure."""
    
    def test_llm_request_creation(self):
        """Test creating an LLM request with required fields."""
        request = LLMRequest(
            request_id="test-001",
            agent_type="generation",
            request_type="generate",
            content={
                "prompt": "Test prompt",
                "context": {},
                "parameters": {
                    "max_length": 1000,
                    "temperature": 0.7,
                    "response_format": "text"
                }
            }
        )
        
        assert request.request_id == "test-001"
        assert request.agent_type == "generation"
        assert request.request_type == "generate"
        assert request.content["prompt"] == "Test prompt"
    
    def test_llm_request_validation(self):
        """Test that LLMRequest validates agent and request types."""
        # Valid agent types
        valid_agents = ["generation", "reflection", "ranking", "evolution", "proximity", "meta-review"]
        for agent in valid_agents:
            request = LLMRequest(
                request_id="test",
                agent_type=agent,
                request_type="generate",
                content={"prompt": "test", "context": {}, "parameters": {}}
            )
            assert request.agent_type == agent
        
        # Invalid agent type should raise ValueError
        with pytest.raises(ValueError):
            LLMRequest(
                request_id="test",
                agent_type="invalid",
                request_type="generate",
                content={"prompt": "test", "context": {}, "parameters": {}}
            )
        
        # Valid request types
        valid_requests = ["generate", "analyze", "evaluate", "compare"]
        for req_type in valid_requests:
            request = LLMRequest(
                request_id="test",
                agent_type="generation",
                request_type=req_type,
                content={"prompt": "test", "context": {}, "parameters": {}}
            )
            assert request.request_type == req_type
        
        # Invalid request type should raise ValueError
        with pytest.raises(ValueError):
            LLMRequest(
                request_id="test",
                agent_type="generation",
                request_type="invalid",
                content={"prompt": "test", "context": {}, "parameters": {}}
            )
    
    def test_llm_request_content_validation(self):
        """Test that LLMRequest validates content structure."""
        # Missing prompt should raise ValueError
        with pytest.raises(ValueError):
            LLMRequest(
                request_id="test",
                agent_type="generation",
                request_type="generate",
                content={"context": {}, "parameters": {}}
            )
        
        # Missing context should raise ValueError
        with pytest.raises(ValueError):
            LLMRequest(
                request_id="test",
                agent_type="generation",
                request_type="generate",
                content={"prompt": "test", "parameters": {}}
            )
        
        # Missing parameters should raise ValueError
        with pytest.raises(ValueError):
            LLMRequest(
                request_id="test",
                agent_type="generation",
                request_type="generate",
                content={"prompt": "test", "context": {}}
            )


class TestLLMResponse:
    """Test the LLMResponse data structure."""
    
    def test_llm_response_success(self):
        """Test creating a successful LLM response."""
        response = LLMResponse(
            request_id="test-001",
            status="success",
            response={
                "content": "Generated content",
                "metadata": {
                    "model_used": "test-model",
                    "tokens_used": 100,
                    "processing_time": 1.5
                }
            },
            error=None
        )
        
        assert response.request_id == "test-001"
        assert response.status == "success"
        assert response.response["content"] == "Generated content"
        assert response.response["metadata"]["model_used"] == "test-model"
        assert response.error is None
    
    def test_llm_response_error(self):
        """Test creating an error LLM response."""
        error = LLMError(
            code="rate_limit_exceeded",
            message="Rate limit exceeded for model",
            recoverable=True
        )
        
        response = LLMResponse(
            request_id="test-002",
            status="error",
            response=None,
            error=error
        )
        
        assert response.request_id == "test-002"
        assert response.status == "error"
        assert response.response is None
        assert response.error.code == "rate_limit_exceeded"
        assert response.error.recoverable is True
    
    def test_llm_response_partial(self):
        """Test creating a partial LLM response."""
        response = LLMResponse(
            request_id="test-003",
            status="partial",
            response={
                "content": "Partial content...",
                "metadata": {
                    "model_used": "test-model",
                    "tokens_used": 50,
                    "processing_time": 0.8
                }
            },
            error=None
        )
        
        assert response.status == "partial"
        assert response.response["content"] == "Partial content..."
    
    def test_llm_response_status_validation(self):
        """Test that LLMResponse validates status values."""
        # Valid statuses
        for status in ["success", "error", "partial"]:
            response = LLMResponse(
                request_id="test",
                status=status,
                response={"content": "test", "metadata": {}},
                error=None
            )
            assert response.status == status
        
        # Invalid status should raise ValueError
        with pytest.raises(ValueError):
            LLMResponse(
                request_id="test",
                status="invalid",
                response={"content": "test", "metadata": {}},
                error=None
            )


class TestLLMError:
    """Test the LLMError data structure."""
    
    def test_llm_error_creation(self):
        """Test creating an LLM error."""
        error = LLMError(
            code="model_unavailable",
            message="The requested model is currently unavailable",
            recoverable=True
        )
        
        assert error.code == "model_unavailable"
        assert error.message == "The requested model is currently unavailable"
        assert error.recoverable is True
    
    def test_llm_error_types(self):
        """Test different types of LLM errors."""
        error_types = [
            ("rate_limit_exceeded", "Rate limit exceeded", True),
            ("model_unavailable", "Model not available", True),
            ("invalid_request", "Request format invalid", False),
            ("context_overflow", "Context window exceeded", False),
            ("safety_violation", "Content violates safety policy", False),
            ("network_timeout", "Network request timed out", True),
        ]
        
        for code, message, recoverable in error_types:
            error = LLMError(code=code, message=message, recoverable=recoverable)
            assert error.code == code
            assert error.message == message
            assert error.recoverable == recoverable