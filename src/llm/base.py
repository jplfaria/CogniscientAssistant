"""Base classes for the LLM abstraction layer."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime

from .validation import validate_request as _validate_request, validate_parameters as _validate_parameters


@dataclass
class LLMError:
    """Represents an error from the LLM system."""
    code: str
    message: str
    recoverable: bool


@dataclass
class LLMRequest:
    """Standard request format for LLM interactions."""
    request_id: str
    agent_type: str
    request_type: str
    content: Dict[str, Any]
    
    # Valid agent and request types
    VALID_AGENTS = {"generation", "reflection", "ranking", "evolution", "proximity", "meta-review"}
    VALID_REQUEST_TYPES = {"generate", "analyze", "evaluate", "compare"}
    
    def __post_init__(self):
        """Validate the request after initialization."""
        # Validate agent type
        if self.agent_type not in self.VALID_AGENTS:
            raise ValueError(f"Invalid agent_type: {self.agent_type}. Must be one of {self.VALID_AGENTS}")
        
        # Validate request type
        if self.request_type not in self.VALID_REQUEST_TYPES:
            raise ValueError(f"Invalid request_type: {self.request_type}. Must be one of {self.VALID_REQUEST_TYPES}")
        
        # Validate content structure
        required_fields = {"prompt", "context", "parameters"}
        if not all(field in self.content for field in required_fields):
            missing = required_fields - set(self.content.keys())
            raise ValueError(f"Missing required content fields: {missing}")


@dataclass
class LLMResponse:
    """Standard response format from LLM interactions."""
    request_id: str
    status: str
    response: Optional[Dict[str, Any]]
    error: Optional[LLMError]
    
    # Valid status values
    VALID_STATUSES = {"success", "error", "partial"}
    
    def __post_init__(self):
        """Validate the response after initialization."""
        if self.status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {self.VALID_STATUSES}")


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate new content based on the request.
        
        Args:
            request: The LLM request containing prompt and parameters
            
        Returns:
            LLMResponse with generated content or error
        """
        pass
    
    @abstractmethod
    async def analyze(self, request: LLMRequest) -> LLMResponse:
        """Analyze existing content based on the request.
        
        Args:
            request: The LLM request containing content to analyze
            
        Returns:
            LLMResponse with analysis results or error
        """
        pass
    
    @abstractmethod
    async def evaluate(self, request: LLMRequest) -> LLMResponse:
        """Evaluate content against specified criteria.
        
        Args:
            request: The LLM request containing content and evaluation criteria
            
        Returns:
            LLMResponse with evaluation results or error
        """
        pass
    
    @abstractmethod
    async def compare(self, request: LLMRequest) -> LLMResponse:
        """Compare multiple items based on specified criteria.
        
        Args:
            request: The LLM request containing items to compare
            
        Returns:
            LLMResponse with comparison results or error
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this LLM provider.
        
        Returns:
            Dictionary describing model capabilities like max_context,
            multimodal support, streaming, etc.
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model.
        
        Returns:
            Dictionary with model name, version, and other metadata
        """
        pass


# Export validation functions
validate_request = _validate_request
validate_parameters = _validate_parameters