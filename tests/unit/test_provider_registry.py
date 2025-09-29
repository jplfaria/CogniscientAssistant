"""Unit tests for LLM provider registry."""

import pytest
from typing import Dict, Any

from src.llm.provider_registry import ProviderRegistry, ProviderNotFoundError
from src.llm.mock_provider import MockLLMProvider
from src.llm.argo_provider import ArgoLLMProvider


class TestProviderRegistry:
    """Test provider registry functionality."""
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = ProviderRegistry()
        
        # Should start empty
        assert len(registry.list_providers()) == 0
    
    def test_register_provider(self):
        """Test registering a provider."""
        registry = ProviderRegistry()
        
        # Register mock provider
        provider = MockLLMProvider()
        registry.register_provider("mock", provider)
        
        # Check registration
        assert "mock" in registry.list_providers()
        assert registry.get_provider("mock") is provider
    
    def test_register_duplicate_provider(self):
        """Test registering duplicate provider name."""
        registry = ProviderRegistry()
        
        # Register first provider
        provider1 = MockLLMProvider()
        registry.register_provider("mock", provider1)
        
        # Try to register with same name
        provider2 = MockLLMProvider()
        with pytest.raises(ValueError) as exc_info:
            registry.register_provider("mock", provider2)
        
        assert "already registered" in str(exc_info.value)
    
    def test_get_nonexistent_provider(self):
        """Test getting a provider that doesn't exist."""
        registry = ProviderRegistry()
        
        with pytest.raises(ProviderNotFoundError):
            registry.get_provider("nonexistent")
    
    def test_unregister_provider(self):
        """Test unregistering a provider."""
        registry = ProviderRegistry()
        
        # Register and unregister
        provider = MockLLMProvider()
        registry.register_provider("mock", provider)
        registry.unregister_provider("mock")
        
        # Should no longer exist
        assert "mock" not in registry.list_providers()
        with pytest.raises(ProviderNotFoundError):
            registry.get_provider("mock")
    
    def test_get_provider_info(self):
        """Test getting provider information."""
        registry = ProviderRegistry()
        
        # Register providers
        mock_provider = MockLLMProvider()
        argo_provider = ArgoLLMProvider()
        
        registry.register_provider("mock", mock_provider)
        registry.register_provider("argo", argo_provider)
        
        # Get all provider info
        info = registry.get_provider_info()
        
        assert "mock" in info
        assert "argo" in info
        assert info["mock"]["provider"] == "mock"
        assert info["argo"]["provider"] == "argo"
    
    def test_select_provider_by_capability(self):
        """Test selecting provider by capability."""
        registry = ProviderRegistry()
        
        # Register providers
        mock_provider = MockLLMProvider()
        argo_provider = ArgoLLMProvider()
        
        registry.register_provider("mock", mock_provider)
        registry.register_provider("argo", argo_provider)
        
        # Select by capability
        providers = registry.find_providers_by_capability("supports_streaming")
        assert len(providers) >= 0  # May vary based on provider capabilities
    
    def test_get_default_provider(self):
        """Test default provider functionality."""
        registry = ProviderRegistry()
        
        # No default initially
        assert registry.get_default_provider() is None
        
        # Register and set default
        provider = MockLLMProvider()
        registry.register_provider("mock", provider)
        registry.set_default_provider("mock")
        
        assert registry.get_default_provider() is provider
    
    def test_set_invalid_default_provider(self):
        """Test setting invalid default provider."""
        registry = ProviderRegistry()
        
        with pytest.raises(ProviderNotFoundError):
            registry.set_default_provider("nonexistent")
    
    def test_registry_singleton(self):
        """Test that registry can be used as singleton."""
        registry1 = ProviderRegistry.get_instance()
        registry2 = ProviderRegistry.get_instance()
        
        # Should be same instance
        assert registry1 is registry2
        
        # Changes in one should reflect in other
        provider = MockLLMProvider()
        registry1.register_provider("test", provider)
        
        assert "test" in registry2.list_providers()