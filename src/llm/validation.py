"""Request validation for the LLM abstraction layer."""

import re
import json
from typing import Dict, Any, List, Union
from dataclasses import dataclass


class ParameterValidator:
    """Validates LLM request parameters."""
    
    MAX_LENGTH_LIMIT = 1000000  # Maximum allowed token/character limit
    
    def validate_temperature(self, temperature: Any) -> bool:
        """Validate temperature parameter.
        
        Args:
            temperature: The temperature value to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If temperature is invalid
        """
        if not isinstance(temperature, (int, float)):
            raise ValueError(f"Temperature must be numeric, got {type(temperature)}")
        
        if not 0.0 <= temperature <= 1.0:
            raise ValueError(f"Temperature must be between 0.0 and 1.0, got {temperature}")
        
        return True
    
    def validate_max_length(self, max_length: Any) -> bool:
        """Validate max_length parameter.
        
        Args:
            max_length: The max length value to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If max_length is invalid
        """
        if not isinstance(max_length, int):
            raise ValueError(f"max_length must be integer, got {type(max_length)}")
        
        if max_length <= 0:
            raise ValueError(f"max_length must be positive, got {max_length}")
        
        if max_length > self.MAX_LENGTH_LIMIT:
            raise ValueError(f"max_length exceeds limit of {self.MAX_LENGTH_LIMIT}, got {max_length}")
        
        return True
    
    def validate_response_format(self, response_format: Any) -> bool:
        """Validate response_format parameter.
        
        Args:
            response_format: The format to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If response_format is invalid
        """
        valid_formats = {"text", "structured", "list"}
        
        if response_format not in valid_formats:
            raise ValueError(f"response_format must be one of {valid_formats}, got {response_format}")
        
        return True
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate a complete parameter set.
        
        Args:
            parameters: Dictionary of parameters to validate
            
        Returns:
            True if all parameters are valid
            
        Raises:
            ValueError: If any parameter is invalid
        """
        if not isinstance(parameters, dict):
            raise ValueError("Parameters must be a dictionary")
        
        # Validate each known parameter if present
        if "temperature" in parameters:
            self.validate_temperature(parameters["temperature"])
        
        if "max_length" in parameters:
            self.validate_max_length(parameters["max_length"])
        
        if "response_format" in parameters:
            self.validate_response_format(parameters["response_format"])
        
        return True


class ContentValidator:
    """Validates LLM request content."""
    
    MAX_PROMPT_LENGTH = 100000  # Maximum prompt length in characters
    MAX_CONTEXT_SIZE = 1000000  # Maximum context size in bytes
    
    def validate_prompt(self, prompt: Any) -> bool:
        """Validate prompt string.
        
        Args:
            prompt: The prompt to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If prompt is invalid
        """
        if not isinstance(prompt, str):
            raise ValueError(f"Prompt must be string, got {type(prompt)}")
        
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        if len(prompt) > self.MAX_PROMPT_LENGTH:
            raise ValueError(f"Prompt exceeds maximum length of {self.MAX_PROMPT_LENGTH}")
        
        return True
    
    def validate_context(self, context: Any) -> bool:
        """Validate context dictionary.
        
        Args:
            context: The context to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If context is invalid
        """
        if not isinstance(context, dict):
            raise ValueError(f"Context must be dictionary, got {type(context)}")
        
        # Check context size
        context_str = json.dumps(context)
        if len(context_str.encode('utf-8')) > self.MAX_CONTEXT_SIZE:
            raise ValueError(f"Context exceeds maximum size of {self.MAX_CONTEXT_SIZE} bytes")
        
        return True
    
    def validate_content(self, content: Dict[str, Any]) -> bool:
        """Validate complete content structure.
        
        Args:
            content: The content dictionary to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If content is invalid
        """
        if not isinstance(content, dict):
            raise ValueError("Content must be a dictionary")
        
        # Check required fields
        required_fields = {"prompt", "context", "parameters"}
        missing_fields = required_fields - set(content.keys())
        if missing_fields:
            raise ValueError(f"Missing required content fields: {missing_fields}")
        
        # Validate each field
        self.validate_prompt(content["prompt"])
        self.validate_context(content["context"])
        
        # Parameters are validated separately
        param_validator = ParameterValidator()
        param_validator.validate_parameters(content["parameters"])
        
        return True


class RequestValidator:
    """Validates complete LLM requests."""
    
    MAX_REQUEST_SIZE = 5000000  # 5MB max request size
    
    def __init__(self):
        self.param_validator = ParameterValidator()
        self.content_validator = ContentValidator()
    
    def validate(self, request: Dict[str, Any]) -> bool:
        """Validate a complete request.
        
        Args:
            request: The request dictionary to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If request is invalid
        """
        # Check total request size
        request_str = json.dumps(request)
        if len(request_str.encode('utf-8')) > self.MAX_REQUEST_SIZE:
            raise ValueError(f"Request exceeds maximum size of {self.MAX_REQUEST_SIZE} bytes")
        
        # Validate required fields
        required_fields = {"request_id", "agent_type", "request_type", "content"}
        missing_fields = required_fields - set(request.keys())
        if missing_fields:
            raise ValueError(f"Missing required request fields: {missing_fields}")
        
        # Validate agent type
        valid_agents = {"generation", "reflection", "ranking", "evolution", "proximity", "meta-review"}
        if request["agent_type"] not in valid_agents:
            raise ValueError(f"Invalid agent_type: {request['agent_type']}")
        
        # Validate request type
        valid_request_types = {"generate", "analyze", "evaluate", "compare"}
        if request["request_type"] not in valid_request_types:
            raise ValueError(f"Invalid request_type: {request['request_type']}")
        
        # Validate content
        self.content_validator.validate_content(request["content"])
        
        return True
    
    def sanitize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize a request for security.
        
        Args:
            request: The request to sanitize
            
        Returns:
            Sanitized request dictionary
        """
        # Create a copy to avoid modifying the original
        sanitized = request.copy()
        
        # Remove any HTML/script tags from string fields
        html_pattern = re.compile(r'<[^>]+>')
        
        def clean_string(s: str) -> str:
            """Remove HTML tags from a string."""
            return html_pattern.sub('', s)
        
        # Sanitize request_id
        if "request_id" in sanitized and isinstance(sanitized["request_id"], str):
            sanitized["request_id"] = clean_string(sanitized["request_id"])
        
        # Sanitize prompt
        if "content" in sanitized and "prompt" in sanitized["content"]:
            if isinstance(sanitized["content"]["prompt"], str):
                # Keep the prompt content but remove any HTML
                sanitized["content"]["prompt"] = clean_string(sanitized["content"]["prompt"])
        
        return sanitized


def validate_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize an LLM request.
    
    Args:
        request: The request to validate
        
    Returns:
        Sanitized and validated request
        
    Raises:
        ValueError: If request is invalid
    """
    validator = RequestValidator()
    validator.validate(request)
    return validator.sanitize(request)


def validate_parameters(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Validate LLM parameters.
    
    Args:
        parameters: The parameters to validate
        
    Returns:
        Validated parameters
        
    Raises:
        ValueError: If parameters are invalid
    """
    validator = ParameterValidator()
    validator.validate_parameters(parameters)
    return parameters