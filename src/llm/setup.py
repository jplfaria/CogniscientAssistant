"""Setup and registration of LLM providers."""

import os
from typing import Optional

from src.llm.provider_registry import get_registry
from src.llm.mock_provider import MockLLMProvider
from src.llm.argo_provider import ArgoLLMProvider


def setup_providers(default_provider: Optional[str] = None):
    """Set up and register all available LLM providers.
    
    Args:
        default_provider: Name of provider to set as default (e.g., "argo", "mock")
                         If None, uses ARGO_PROXY_URL env var to determine
    """
    registry = get_registry()
    
    # Always register mock provider for testing
    mock_provider = MockLLMProvider()
    registry.register_provider("mock", mock_provider)
    
    # Register Argo provider if configuration exists
    argo_proxy_url = os.getenv("ARGO_PROXY_URL")
    if argo_proxy_url:
        try:
            argo_provider = ArgoLLMProvider()
            registry.register_provider("argo", argo_provider)
        except Exception as e:
            print(f"Warning: Failed to initialize Argo provider: {e}")
    
    # Set default provider
    if default_provider and default_provider in registry.list_providers():
        registry.set_default_provider(default_provider)
    elif "argo" in registry.list_providers():
        # Prefer Argo if available
        registry.set_default_provider("argo")
    else:
        # Fallback to mock
        registry.set_default_provider("mock")
    
    return registry


def get_configured_provider(name: Optional[str] = None):
    """Get a configured LLM provider.
    
    Args:
        name: Provider name. If None, returns default provider
        
    Returns:
        LLMProvider instance
    """
    registry = get_registry()
    
    # Setup providers if registry is empty
    if not registry.list_providers():
        setup_providers()
    
    if name:
        return registry.get_provider(name)
    else:
        provider = registry.get_default_provider()
        if not provider:
            raise ValueError("No default provider configured")
        return provider