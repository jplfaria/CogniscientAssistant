"""Model capability tracking and management."""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple


class CapabilityMismatchError(Exception):
    """Raised when a request exceeds model capabilities."""
    pass


@dataclass
class ModelCapabilities:
    """Represents the capabilities of an LLM model."""
    max_context: int
    multimodal: bool = False
    streaming: bool = False
    function_calling: bool = False
    supports_json_mode: bool = False
    supports_temperature: bool = True
    max_output_tokens: int = 4096
    cost_per_1k_input_tokens: float = 0.0
    cost_per_1k_output_tokens: float = 0.0
    
    def __post_init__(self):
        """Validate capabilities."""
        if self.max_context <= 0:
            raise ValueError("max_context must be positive")
        
        if self.max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be positive")
        
        if self.cost_per_1k_input_tokens < 0:
            raise ValueError("cost_per_1k_input_tokens cannot be negative")
        
        if self.cost_per_1k_output_tokens < 0:
            raise ValueError("cost_per_1k_output_tokens cannot be negative")
    
    def supports_request(
        self,
        context_size: int,
        output_size: Optional[int] = None,
        requires_multimodal: bool = False,
        requires_streaming: bool = False,
        requires_function_calling: bool = False
    ) -> bool:
        """Check if this model can handle the given request.
        
        Args:
            context_size: Size of the context in tokens
            output_size: Expected output size in tokens
            requires_multimodal: Whether request needs multimodal support
            requires_streaming: Whether request needs streaming
            requires_function_calling: Whether request needs function calling
            
        Returns:
            True if model can handle the request
        """
        if context_size > self.max_context:
            return False
        
        if output_size and output_size > self.max_output_tokens:
            return False
        
        if requires_multimodal and not self.multimodal:
            return False
        
        if requires_streaming and not self.streaming:
            return False
        
        if requires_function_calling and not self.function_calling:
            return False
        
        return True
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate the cost for a request.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in dollars
        """
        input_cost = (input_tokens / 1000) * self.cost_per_1k_input_tokens
        output_cost = (output_tokens / 1000) * self.cost_per_1k_output_tokens
        return input_cost + output_cost


class CapabilityManager:
    """Manages model capabilities and routing."""
    
    def __init__(self):
        """Initialize the capability manager."""
        self.models: Dict[str, ModelCapabilities] = {}
    
    def register_model(self, model_name: str, capabilities: ModelCapabilities):
        """Register a model with its capabilities.
        
        Args:
            model_name: Name of the model
            capabilities: The model's capabilities
        """
        self.models[model_name] = capabilities
    
    def update_model(self, model_name: str, capabilities: ModelCapabilities):
        """Update a model's capabilities.
        
        Args:
            model_name: Name of the model
            capabilities: The updated capabilities
        """
        self.models[model_name] = capabilities
    
    def get_capabilities(self, model_name: str) -> ModelCapabilities:
        """Get capabilities for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            The model's capabilities
            
        Raises:
            KeyError: If model not found
        """
        return self.models[model_name]
    
    def find_suitable_models(
        self,
        context_size: int,
        output_size: Optional[int] = None,
        requires_multimodal: bool = False,
        requires_streaming: bool = False,
        requires_function_calling: bool = False
    ) -> List[str]:
        """Find models that can handle the given requirements.
        
        Args:
            context_size: Required context size
            output_size: Required output size
            requires_multimodal: Whether multimodal is required
            requires_streaming: Whether streaming is required
            requires_function_calling: Whether function calling is required
            
        Returns:
            List of suitable model names
        """
        suitable = []
        
        for model_name, capabilities in self.models.items():
            if capabilities.supports_request(
                context_size=context_size,
                output_size=output_size,
                requires_multimodal=requires_multimodal,
                requires_streaming=requires_streaming,
                requires_function_calling=requires_function_calling
            ):
                suitable.append(model_name)
        
        return suitable
    
    def find_cheapest_model(
        self,
        context_size: int,
        estimated_output_tokens: int,
        requires_multimodal: bool = False,
        requires_streaming: bool = False,
        requires_function_calling: bool = False
    ) -> Optional[str]:
        """Find the cheapest model that meets requirements.
        
        Args:
            context_size: Required context size
            estimated_output_tokens: Estimated output tokens
            requires_multimodal: Whether multimodal is required
            requires_streaming: Whether streaming is required
            requires_function_calling: Whether function calling is required
            
        Returns:
            Name of the cheapest suitable model, or None if none found
        """
        suitable_models = self.find_suitable_models(
            context_size=context_size,
            output_size=estimated_output_tokens,
            requires_multimodal=requires_multimodal,
            requires_streaming=requires_streaming,
            requires_function_calling=requires_function_calling
        )
        
        if not suitable_models:
            return None
        
        # Calculate costs for each suitable model
        costs: List[Tuple[str, float]] = []
        for model_name in suitable_models:
            capabilities = self.models[model_name]
            cost = capabilities.estimate_cost(context_size, estimated_output_tokens)
            costs.append((model_name, cost))
        
        # Sort by cost and return cheapest
        costs.sort(key=lambda x: x[1])
        return costs[0][0]
    
    def validate_request(
        self,
        model: str,
        context_size: int,
        output_size: Optional[int] = None,
        requires_multimodal: bool = False,
        requires_streaming: bool = False,
        requires_function_calling: bool = False
    ):
        """Validate that a model can handle a request.
        
        Args:
            model: Model name
            context_size: Context size
            output_size: Expected output size
            requires_multimodal: Whether multimodal is required
            requires_streaming: Whether streaming is required
            requires_function_calling: Whether function calling is required
            
        Raises:
            CapabilityMismatchError: If model cannot handle request
            KeyError: If model not found
        """
        capabilities = self.models[model]
        
        if context_size > capabilities.max_context:
            raise CapabilityMismatchError(
                f"Context size {context_size} exceeds max context {capabilities.max_context} for {model}"
            )
        
        if output_size and output_size > capabilities.max_output_tokens:
            raise CapabilityMismatchError(
                f"Output size {output_size} exceeds max output {capabilities.max_output_tokens} for {model}"
            )
        
        if requires_multimodal and not capabilities.multimodal:
            raise CapabilityMismatchError(
                f"Model {model} does not support multimodal"
            )
        
        if requires_streaming and not capabilities.streaming:
            raise CapabilityMismatchError(
                f"Model {model} does not support streaming"
            )
        
        if requires_function_calling and not capabilities.function_calling:
            raise CapabilityMismatchError(
                f"Model {model} does not support function calling"
            )


class ModelRegistry:
    """Pre-configured registry of common models."""
    
    def __init__(self):
        """Initialize with common model configurations."""
        self.manager = CapabilityManager()
        self._setup_default_models()
        self._setup_aliases()
    
    def _setup_default_models(self):
        """Set up default model configurations."""
        # GPT-4
        self.manager.register_model("gpt-4", ModelCapabilities(
            max_context=128000,
            multimodal=True,
            streaming=True,
            function_calling=True,
            supports_json_mode=True,
            max_output_tokens=4096,
            cost_per_1k_input_tokens=0.01,
            cost_per_1k_output_tokens=0.03
        ))
        
        # GPT-3.5 Turbo
        self.manager.register_model("gpt-3.5-turbo", ModelCapabilities(
            max_context=16385,
            multimodal=False,
            streaming=True,
            function_calling=True,
            supports_json_mode=True,
            max_output_tokens=4096,
            cost_per_1k_input_tokens=0.0005,
            cost_per_1k_output_tokens=0.0015
        ))
        
        # Claude 3 Opus
        self.manager.register_model("claude-3-opus", ModelCapabilities(
            max_context=200000,
            multimodal=True,
            streaming=True,
            function_calling=False,
            supports_json_mode=False,
            max_output_tokens=4096,
            cost_per_1k_input_tokens=0.015,
            cost_per_1k_output_tokens=0.075
        ))
        
        # Claude 3 Sonnet
        self.manager.register_model("claude-3-sonnet", ModelCapabilities(
            max_context=200000,
            multimodal=True,
            streaming=True,
            function_calling=False,
            supports_json_mode=False,
            max_output_tokens=4096,
            cost_per_1k_input_tokens=0.003,
            cost_per_1k_output_tokens=0.015
        ))
        
        # Gemini 2.0
        self.manager.register_model("gemini-2.0", ModelCapabilities(
            max_context=1000000,
            multimodal=True,
            streaming=True,
            function_calling=True,
            supports_json_mode=True,
            max_output_tokens=8192,
            cost_per_1k_input_tokens=0.0025,
            cost_per_1k_output_tokens=0.01
        ))
    
    def _setup_aliases(self):
        """Set up common model name aliases."""
        self.aliases = {
            "gpt4": "gpt-4",
            "gpt-4-turbo": "gpt-4",
            "claude-opus": "claude-3-opus",
            "claude-sonnet": "claude-3-sonnet",
            "gemini-pro": "gemini-2.0",
            "gemini": "gemini-2.0"
        }
    
    def has_model(self, model_name: str) -> bool:
        """Check if a model is registered.
        
        Args:
            model_name: Model name or alias
            
        Returns:
            True if model exists
        """
        resolved = self.resolve_model_name(model_name)
        return resolved in self.manager.models
    
    def resolve_model_name(self, model_name: str) -> str:
        """Resolve model name aliases.
        
        Args:
            model_name: Model name or alias
            
        Returns:
            Canonical model name
        """
        return self.aliases.get(model_name, model_name)
    
    def get_capabilities(self, model_name: str) -> ModelCapabilities:
        """Get capabilities for a model.
        
        Args:
            model_name: Model name or alias
            
        Returns:
            Model capabilities
        """
        resolved = self.resolve_model_name(model_name)
        return self.manager.get_capabilities(resolved)
    
    def register_custom_model(self, model_name: str, capabilities: ModelCapabilities):
        """Register a custom model.
        
        Args:
            model_name: Name of the custom model
            capabilities: Model capabilities
        """
        self.manager.register_model(model_name, capabilities)