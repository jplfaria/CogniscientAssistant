"""Tests for LLM request validation functionality."""

import pytest
from typing import Dict, Any

from src.llm.validation import (
    ParameterValidator,
    ContentValidator,
    RequestValidator,
    validate_request,
    validate_parameters
)


class TestParameterValidator:
    """Test parameter validation functionality."""
    
    def test_temperature_validation(self):
        """Test temperature parameter validation."""
        validator = ParameterValidator()
        
        # Valid temperatures
        assert validator.validate_temperature(0.0) is True
        assert validator.validate_temperature(0.5) is True
        assert validator.validate_temperature(1.0) is True
        
        # Invalid temperatures
        with pytest.raises(ValueError):
            validator.validate_temperature(-0.1)
        
        with pytest.raises(ValueError):
            validator.validate_temperature(1.1)
        
        with pytest.raises(ValueError):
            validator.validate_temperature("invalid")
    
    def test_max_length_validation(self):
        """Test max_length parameter validation."""
        validator = ParameterValidator()
        
        # Valid lengths
        assert validator.validate_max_length(100) is True
        assert validator.validate_max_length(1000) is True
        assert validator.validate_max_length(10000) is True
        
        # Invalid lengths
        with pytest.raises(ValueError):
            validator.validate_max_length(0)
        
        with pytest.raises(ValueError):
            validator.validate_max_length(-100)
        
        with pytest.raises(ValueError):
            validator.validate_max_length("invalid")
        
        # Exceeds maximum
        with pytest.raises(ValueError):
            validator.validate_max_length(1000001)
    
    def test_response_format_validation(self):
        """Test response_format parameter validation."""
        validator = ParameterValidator()
        
        # Valid formats
        assert validator.validate_response_format("text") is True
        assert validator.validate_response_format("structured") is True
        assert validator.validate_response_format("list") is True
        
        # Invalid format
        with pytest.raises(ValueError):
            validator.validate_response_format("invalid")
    
    def test_parameter_set_validation(self):
        """Test validation of complete parameter sets."""
        validator = ParameterValidator()
        
        # Valid parameter set
        params = {
            "temperature": 0.7,
            "max_length": 1000,
            "response_format": "text"
        }
        assert validator.validate_parameters(params) is True
        
        # Missing optional parameters is okay
        params = {"temperature": 0.5}
        assert validator.validate_parameters(params) is True
        
        # Invalid parameter values
        params = {"temperature": 2.0}
        with pytest.raises(ValueError):
            validator.validate_parameters(params)


class TestContentValidator:
    """Test content validation functionality."""
    
    def test_prompt_validation(self):
        """Test prompt validation."""
        validator = ContentValidator()
        
        # Valid prompts
        assert validator.validate_prompt("Generate a hypothesis") is True
        assert validator.validate_prompt("A" * 100) is True
        
        # Empty prompt
        with pytest.raises(ValueError):
            validator.validate_prompt("")
        
        # Prompt too long
        with pytest.raises(ValueError):
            validator.validate_prompt("A" * 100001)
    
    def test_context_validation(self):
        """Test context validation."""
        validator = ContentValidator()
        
        # Valid contexts
        context = {
            "previous_results": ["result1", "result2"],
            "domain_knowledge": ["fact1", "fact2"],
            "constraints": ["constraint1"]
        }
        assert validator.validate_context(context) is True
        
        # Empty context is valid
        assert validator.validate_context({}) is True
        
        # Invalid context structure
        with pytest.raises(ValueError):
            validator.validate_context("invalid")
        
        # Context too large
        large_context = {
            "data": ["x" * 1000] * 1100  # Create context larger than 1MB
        }
        with pytest.raises(ValueError):
            validator.validate_context(large_context)
    
    def test_content_structure_validation(self):
        """Test full content structure validation."""
        validator = ContentValidator()
        
        # Valid content
        content = {
            "prompt": "Test prompt",
            "context": {"key": "value"},
            "parameters": {"temperature": 0.5}
        }
        assert validator.validate_content(content) is True
        
        # Missing required fields
        content = {"prompt": "Test"}
        with pytest.raises(ValueError):
            validator.validate_content(content)


class TestRequestValidator:
    """Test complete request validation."""
    
    def test_full_request_validation(self):
        """Test validation of complete requests."""
        validator = RequestValidator()
        
        # Valid request
        request = {
            "request_id": "test-001",
            "agent_type": "generation",
            "request_type": "generate",
            "content": {
                "prompt": "Generate hypothesis",
                "context": {},
                "parameters": {"temperature": 0.7}
            }
        }
        assert validator.validate(request) is True
        
        # Invalid agent type
        request["agent_type"] = "invalid"
        with pytest.raises(ValueError):
            validator.validate(request)
        
        # Reset and test invalid request type
        request["agent_type"] = "generation"
        request["request_type"] = "invalid"
        with pytest.raises(ValueError):
            validator.validate(request)
    
    def test_request_size_limits(self):
        """Test that requests are limited in total size."""
        validator = RequestValidator()
        
        # Create a request that's too large
        large_request = {
            "request_id": "test-002",
            "agent_type": "generation",
            "request_type": "generate",
            "content": {
                "prompt": "Test",
                "context": {
                    "data": ["x" * 1000] * 1000  # Very large context
                },
                "parameters": {}
            }
        }
        
        with pytest.raises(ValueError) as exc_info:
            validator.validate(large_request)
        assert "exceeds maximum size" in str(exc_info.value)
    
    def test_request_sanitization(self):
        """Test that requests are sanitized for security."""
        validator = RequestValidator()
        
        # Request with potential injection
        request = {
            "request_id": "test<script>alert('xss')</script>",
            "agent_type": "generation",
            "request_type": "generate",
            "content": {
                "prompt": "Normal prompt",
                "context": {},
                "parameters": {}
            }
        }
        
        # Should sanitize the request_id
        sanitized = validator.sanitize(request)
        assert "<script>" not in sanitized["request_id"]
        assert sanitized["content"]["prompt"] == "Normal prompt"


def test_validate_request_function():
    """Test the standalone validate_request function."""
    # Valid request
    request = {
        "request_id": "test-001",
        "agent_type": "generation",
        "request_type": "generate",
        "content": {
            "prompt": "Test prompt",
            "context": {},
            "parameters": {"temperature": 0.5}
        }
    }
    
    # Should not raise any exceptions
    validated = validate_request(request)
    assert validated["request_id"] == "test-001"
    
    # Invalid request
    invalid_request = {
        "request_id": "test-002",
        "agent_type": "invalid",
        "request_type": "generate",
        "content": {}
    }
    
    with pytest.raises(ValueError):
        validate_request(invalid_request)


def test_validate_parameters_function():
    """Test the standalone validate_parameters function."""
    # Valid parameters
    params = {
        "temperature": 0.8,
        "max_length": 2000,
        "response_format": "structured"
    }
    
    validated = validate_parameters(params)
    assert validated["temperature"] == 0.8
    assert validated["max_length"] == 2000
    
    # Invalid parameters
    invalid_params = {
        "temperature": 1.5,
        "max_length": -100
    }
    
    with pytest.raises(ValueError):
        validate_parameters(invalid_params)