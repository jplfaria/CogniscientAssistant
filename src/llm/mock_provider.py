"""Mock LLM Provider for testing."""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field

from .base import LLMProvider, LLMRequest, LLMResponse, LLMError


@dataclass
class MockResponse:
    """Configuration for a mock response."""
    content: str
    metadata: Optional[Dict[str, Any]] = None
    delay: float = 0.0  # Simulated response delay in seconds
    
    def to_response(self, request_id: str) -> LLMResponse:
        """Convert to an LLMResponse."""
        return LLMResponse(
            request_id=request_id,
            status="success",
            response={
                "content": self.content,
                "metadata": self.metadata or {
                    "model_used": "mock-model-v1",
                    "tokens_used": len(self.content.split()),
                    "processing_time": self.delay
                }
            },
            error=None
        )


@dataclass
class MockConfiguration:
    """Configuration for mock provider behavior."""
    responses: Dict[str, Union[MockResponse, List[MockResponse]]] = field(default_factory=dict)
    errors: Dict[str, LLMError] = field(default_factory=dict)
    default_delay: float = 0.1
    
    def add_response(self, request_pattern: Dict[str, Any], response: MockResponse):
        """Add a response for requests matching the pattern."""
        pattern_key = self._pattern_to_key(request_pattern)
        self.responses[pattern_key] = response
    
    def add_sequence(self, request_pattern: Dict[str, Any], responses: List[MockResponse]):
        """Add a sequence of responses for matching requests."""
        pattern_key = self._pattern_to_key(request_pattern)
        self.responses[pattern_key] = responses
    
    def add_error(self, request_pattern: Dict[str, Any], error: LLMError):
        """Add an error response for matching requests."""
        pattern_key = self._pattern_to_key(request_pattern)
        self.errors[pattern_key] = error
    
    def get_response(self, request: LLMRequest) -> Union[MockResponse, LLMError, None]:
        """Get the configured response for a request."""
        # Check for errors first
        for pattern_key, error in self.errors.items():
            if self._matches_pattern(request, pattern_key):
                return error
        
        # Check for configured responses
        for pattern_key, response in self.responses.items():
            if self._matches_pattern(request, pattern_key):
                if isinstance(response, list):
                    # Return next in sequence
                    if not hasattr(self, '_sequence_counters'):
                        self._sequence_counters = {}
                    
                    counter = self._sequence_counters.get(pattern_key, 0)
                    self._sequence_counters[pattern_key] = (counter + 1) % len(response)
                    return response[counter]
                return response
        
        return None
    
    def _pattern_to_key(self, pattern: Dict[str, Any]) -> str:
        """Convert a pattern dict to a string key."""
        parts = []
        for key in sorted(pattern.keys()):
            parts.append(f"{key}={pattern[key]}")
        return "|".join(parts)
    
    def _matches_pattern(self, request: LLMRequest, pattern_key: str) -> bool:
        """Check if a request matches a pattern."""
        for part in pattern_key.split("|"):
            key, value = part.split("=", 1)
            if hasattr(request, key) and getattr(request, key) != value:
                return False
        return True


class MockLLMProvider(LLMProvider):
    """Mock implementation of LLMProvider for testing."""
    
    def __init__(self, configuration: Optional[MockConfiguration] = None):
        """Initialize the mock provider.
        
        Args:
            configuration: Optional configuration for custom responses
        """
        self.configuration = configuration or MockConfiguration()
        self._call_count = 0
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate mock content."""
        self._call_count += 1
        
        # Check for configured response
        configured = self.configuration.get_response(request)
        if isinstance(configured, LLMError):
            return LLMResponse(
                request_id=request.request_id,
                status="error",
                response=None,
                error=configured
            )
        elif isinstance(configured, MockResponse):
            await asyncio.sleep(configured.delay)
            return configured.to_response(request.request_id)
        
        # Default response
        await asyncio.sleep(self.configuration.default_delay)
        
        content = self._generate_default_content(request)
        return LLMResponse(
            request_id=request.request_id,
            status="success",
            response={
                "content": content,
                "metadata": {
                    "model_used": "mock-model-v1",
                    "tokens_used": len(content.split()),
                    "processing_time": self.configuration.default_delay
                }
            },
            error=None
        )
    
    async def analyze(self, request: LLMRequest) -> LLMResponse:
        """Analyze mock content."""
        self._call_count += 1
        
        # Check for configured response
        configured = self.configuration.get_response(request)
        if isinstance(configured, LLMError):
            return LLMResponse(
                request_id=request.request_id,
                status="error",
                response=None,
                error=configured
            )
        elif isinstance(configured, MockResponse):
            await asyncio.sleep(configured.delay)
            return configured.to_response(request.request_id)
        
        # Default response
        await asyncio.sleep(self.configuration.default_delay)
        
        content = self._analyze_default_content(request)
        return LLMResponse(
            request_id=request.request_id,
            status="success",
            response={
                "content": content,
                "metadata": {
                    "model_used": "mock-model-v1",
                    "tokens_used": len(content.split()),
                    "processing_time": self.configuration.default_delay
                }
            },
            error=None
        )
    
    async def evaluate(self, request: LLMRequest) -> LLMResponse:
        """Evaluate mock content."""
        self._call_count += 1
        
        # Check for configured response
        configured = self.configuration.get_response(request)
        if isinstance(configured, LLMError):
            return LLMResponse(
                request_id=request.request_id,
                status="error",
                response=None,
                error=configured
            )
        elif isinstance(configured, MockResponse):
            await asyncio.sleep(configured.delay)
            return configured.to_response(request.request_id)
        
        # Default response
        await asyncio.sleep(self.configuration.default_delay)
        
        content = {
            "score": 0.85,
            "reasoning": "Mock evaluation completed successfully",
            "strengths": ["Clear hypothesis", "Testable"],
            "weaknesses": ["Limited scope"]
        }
        
        return LLMResponse(
            request_id=request.request_id,
            status="success",
            response={
                "content": content,
                "metadata": {
                    "model_used": "mock-model-v1",
                    "tokens_used": 20,
                    "processing_time": self.configuration.default_delay
                }
            },
            error=None
        )
    
    async def compare(self, request: LLMRequest) -> LLMResponse:
        """Compare mock items."""
        self._call_count += 1
        
        # Check for configured response
        configured = self.configuration.get_response(request)
        if isinstance(configured, LLMError):
            return LLMResponse(
                request_id=request.request_id,
                status="error",
                response=None,
                error=configured
            )
        elif isinstance(configured, MockResponse):
            await asyncio.sleep(configured.delay)
            return configured.to_response(request.request_id)
        
        # Default response
        await asyncio.sleep(self.configuration.default_delay)
        
        content = {
            "ranking": ["item1", "item2"],
            "comparison": "Item 1 is superior due to better evidence support",
            "scores": {"item1": 0.9, "item2": 0.7}
        }
        
        return LLMResponse(
            request_id=request.request_id,
            status="success",
            response={
                "content": content,
                "metadata": {
                    "model_used": "mock-model-v1",
                    "tokens_used": 15,
                    "processing_time": self.configuration.default_delay
                }
            },
            error=None
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get mock provider capabilities."""
        return {
            "max_context": 100000,
            "multimodal": False,
            "streaming": False,
            "function_calling": True,
            "supports_json_mode": True,
            "supports_temperature": True,
            "max_output_tokens": 4096
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get mock model information."""
        return {
            "name": "mock-model",
            "version": "v1",
            "provider": "mock",
            "call_count": self._call_count,
            "created_at": datetime.now().isoformat()
        }
    
    def _generate_default_content(self, request: LLMRequest) -> str:
        """Generate default content based on agent type."""
        agent_type = request.agent_type
        prompt = request.content.get("prompt", "")
        
        if agent_type == "generation":
            return f"Mock hypothesis generated based on prompt: {prompt[:50]}..."
        elif agent_type == "evolution":
            return f"Mock evolved hypothesis based on: {prompt[:50]}..."
        else:
            return f"Mock generated content for {agent_type} agent"
    
    def _analyze_default_content(self, request: LLMRequest) -> str:
        """Generate default analysis based on agent type."""
        agent_type = request.agent_type
        
        if agent_type == "reflection":
            return "Mock analysis: The hypothesis shows promise with clear methodology"
        elif agent_type == "meta-review":
            return "Mock meta-analysis: Overall research direction is sound"
        else:
            return f"Mock analysis completed for {agent_type} agent"