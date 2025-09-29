"""Tests for LLM model capability tracking."""

import pytest
from typing import Dict, Any

from src.llm.capabilities import (
    ModelCapabilities,
    CapabilityManager,
    ModelRegistry,
    CapabilityMismatchError
)


class TestModelCapabilities:
    """Test ModelCapabilities data structure."""
    
    def test_model_capabilities_creation(self):
        """Test creating model capabilities."""
        capabilities = ModelCapabilities(
            max_context=128000,
            multimodal=True,
            streaming=True,
            function_calling=True,
            supports_json_mode=True,
            supports_temperature=True,
            max_output_tokens=4096,
            cost_per_1k_input_tokens=0.01,
            cost_per_1k_output_tokens=0.03
        )
        
        assert capabilities.max_context == 128000
        assert capabilities.multimodal is True
        assert capabilities.streaming is True
        assert capabilities.function_calling is True
        assert capabilities.cost_per_1k_input_tokens == 0.01
    
    def test_model_capabilities_validation(self):
        """Test that capabilities are validated."""
        # Invalid max_context
        with pytest.raises(ValueError):
            ModelCapabilities(max_context=-1)
        
        # Invalid max_output_tokens
        with pytest.raises(ValueError):
            ModelCapabilities(max_context=1000, max_output_tokens=0)
        
        # Invalid cost
        with pytest.raises(ValueError):
            ModelCapabilities(
                max_context=1000,
                max_output_tokens=100,
                cost_per_1k_input_tokens=-0.01
            )
    
    def test_model_capabilities_supports_request(self):
        """Test checking if capabilities support a request."""
        capabilities = ModelCapabilities(
            max_context=10000,
            multimodal=False,
            streaming=True,
            function_calling=True,
            max_output_tokens=1000
        )
        
        # Request within capabilities
        assert capabilities.supports_request(
            context_size=5000,
            output_size=500,
            requires_multimodal=False,
            requires_streaming=False
        )
        
        # Request exceeds context
        assert not capabilities.supports_request(
            context_size=15000,
            output_size=500
        )
        
        # Request requires multimodal
        assert not capabilities.supports_request(
            context_size=1000,
            output_size=100,
            requires_multimodal=True
        )


class TestCapabilityManager:
    """Test CapabilityManager functionality."""
    
    def test_capability_manager_registration(self):
        """Test registering model capabilities."""
        manager = CapabilityManager()
        
        # Register GPT-4 capabilities
        gpt4_caps = ModelCapabilities(
            max_context=128000,
            multimodal=True,
            streaming=True,
            function_calling=True,
            cost_per_1k_input_tokens=0.01,
            cost_per_1k_output_tokens=0.03
        )
        
        manager.register_model("gpt-4", gpt4_caps)
        
        # Should be able to retrieve
        retrieved = manager.get_capabilities("gpt-4")
        assert retrieved.max_context == 128000
        assert retrieved.multimodal is True
    
    def test_capability_manager_update(self):
        """Test updating model capabilities."""
        manager = CapabilityManager()
        
        # Register initial capabilities
        initial_caps = ModelCapabilities(
            max_context=100000,
            multimodal=False
        )
        manager.register_model("test-model", initial_caps)
        
        # Update capabilities
        updated_caps = ModelCapabilities(
            max_context=200000,
            multimodal=True
        )
        manager.update_model("test-model", updated_caps)
        
        # Should have updated values
        retrieved = manager.get_capabilities("test-model")
        assert retrieved.max_context == 200000
        assert retrieved.multimodal is True
    
    def test_capability_manager_find_suitable_model(self):
        """Test finding suitable models for requirements."""
        manager = CapabilityManager()
        
        # Register multiple models
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
        
        manager.register_model("medium-model", ModelCapabilities(
            max_context=32000,
            multimodal=False,
            cost_per_1k_input_tokens=0.005
        ))
        
        # Find model for small request
        suitable = manager.find_suitable_models(
            context_size=3000,
            requires_multimodal=False
        )
        assert len(suitable) == 3  # All models can handle it
        
        # Find model for large context
        suitable = manager.find_suitable_models(
            context_size=50000,
            requires_multimodal=False
        )
        assert len(suitable) == 1
        assert suitable[0] == "large-model"
        
        # Find model requiring multimodal
        suitable = manager.find_suitable_models(
            context_size=1000,
            requires_multimodal=True
        )
        assert len(suitable) == 1
        assert suitable[0] == "large-model"
    
    def test_capability_manager_cheapest_model(self):
        """Test finding the cheapest suitable model."""
        manager = CapabilityManager()
        
        # Register models with different costs
        manager.register_model("expensive", ModelCapabilities(
            max_context=100000,
            cost_per_1k_input_tokens=0.02,
            cost_per_1k_output_tokens=0.06
        ))
        
        manager.register_model("cheap", ModelCapabilities(
            max_context=100000,
            cost_per_1k_input_tokens=0.001,
            cost_per_1k_output_tokens=0.002
        ))
        
        manager.register_model("medium", ModelCapabilities(
            max_context=100000,
            cost_per_1k_input_tokens=0.01,
            cost_per_1k_output_tokens=0.03
        ))
        
        # Find cheapest model
        cheapest = manager.find_cheapest_model(
            context_size=10000,
            estimated_output_tokens=1000
        )
        
        assert cheapest == "cheap"
    
    def test_capability_mismatch_error(self):
        """Test capability mismatch error handling."""
        manager = CapabilityManager()
        
        # Register a limited model
        manager.register_model("limited", ModelCapabilities(
            max_context=1000,
            multimodal=False
        ))
        
        # Try to use for request that exceeds capabilities
        with pytest.raises(CapabilityMismatchError) as exc_info:
            manager.validate_request(
                model="limited",
                context_size=2000,
                requires_multimodal=False
            )
        
        assert "exceeds max context" in str(exc_info.value)
        
        # Try to use for multimodal request
        with pytest.raises(CapabilityMismatchError) as exc_info:
            manager.validate_request(
                model="limited",
                context_size=500,
                requires_multimodal=True
            )
        
        assert "does not support multimodal" in str(exc_info.value)


class TestModelRegistry:
    """Test model registry functionality."""
    
    def test_model_registry_defaults(self):
        """Test that model registry has sensible defaults."""
        registry = ModelRegistry()
        
        # Should have common models registered
        assert registry.has_model("gpt-4")
        assert registry.has_model("gpt-3.5-turbo")
        assert registry.has_model("claude-3-opus")
        assert registry.has_model("claude-3-sonnet")
        assert registry.has_model("gemini-2.0")
        
        # Check capabilities make sense
        gpt4 = registry.get_capabilities("gpt-4")
        assert gpt4.max_context >= 128000
        assert gpt4.multimodal is True
        
        gpt35 = registry.get_capabilities("gpt-3.5-turbo")
        assert gpt35.max_context >= 16000
        assert gpt35.cost_per_1k_input_tokens < gpt4.cost_per_1k_input_tokens
    
    def test_model_registry_aliases(self):
        """Test model name aliases."""
        registry = ModelRegistry()
        
        # Should support common aliases
        assert registry.resolve_model_name("gpt4") == "gpt-4"
        assert registry.resolve_model_name("gpt-4-turbo") == "gpt-4"
        assert registry.resolve_model_name("claude-opus") == "claude-3-opus"
        assert registry.resolve_model_name("gemini-pro") == "gemini-2.0"
    
    def test_model_registry_custom_models(self):
        """Test adding custom models to registry."""
        registry = ModelRegistry()
        
        # Add custom model
        custom_caps = ModelCapabilities(
            max_context=50000,
            multimodal=False,
            cost_per_1k_input_tokens=0.005
        )
        
        registry.register_custom_model("my-custom-model", custom_caps)
        
        assert registry.has_model("my-custom-model")
        retrieved = registry.get_capabilities("my-custom-model")
        assert retrieved.max_context == 50000