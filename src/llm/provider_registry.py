"""Registry for managing LLM providers."""

from typing import Dict, List, Optional, Any

from src.llm.base import LLMProvider


class ProviderNotFoundError(Exception):
    """Raised when a provider is not found in registry."""
    pass


class ProviderRegistry:
    """Registry for managing LLM providers.
    
    Allows registration, discovery, and management of multiple LLM providers.
    """
    
    _instance: Optional['ProviderRegistry'] = None
    
    def __init__(self):
        """Initialize provider registry."""
        self._providers: Dict[str, LLMProvider] = {}
        self._default_provider: Optional[str] = None
    
    @classmethod
    def get_instance(cls) -> 'ProviderRegistry':
        """Get singleton instance of registry.
        
        Returns:
            Singleton registry instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register_provider(self, name: str, provider: LLMProvider):
        """Register a new provider.
        
        Args:
            name: Unique name for the provider
            provider: LLMProvider instance
            
        Raises:
            ValueError: If name is already registered
        """
        if name in self._providers:
            raise ValueError(f"Provider '{name}' is already registered")
        
        self._providers[name] = provider
    
    def unregister_provider(self, name: str):
        """Unregister a provider.
        
        Args:
            name: Name of provider to unregister
        """
        if name in self._providers:
            del self._providers[name]
            
            # Clear default if it was this provider
            if self._default_provider == name:
                self._default_provider = None
    
    def get_provider(self, name: str) -> LLMProvider:
        """Get a provider by name.
        
        Args:
            name: Name of the provider
            
        Returns:
            LLMProvider instance
            
        Raises:
            ProviderNotFoundError: If provider not found
        """
        if name not in self._providers:
            raise ProviderNotFoundError(f"Provider '{name}' not found")
        
        return self._providers[name]
    
    def list_providers(self) -> List[str]:
        """List all registered provider names.
        
        Returns:
            List of provider names
        """
        return list(self._providers.keys())
    
    def get_provider_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered providers.
        
        Returns:
            Dictionary mapping provider names to their info
        """
        info = {}
        for name, provider in self._providers.items():
            capabilities = provider.get_capabilities()
            info[name] = {
                "provider": capabilities.get("provider", name),
                "capabilities": capabilities,
                "model_info": provider.get_model_info() if hasattr(provider, 'get_model_info') else {}
            }
        return info
    
    def find_providers_by_capability(self, capability: str) -> List[str]:
        """Find providers that have a specific capability.
        
        Args:
            capability: Capability to search for (e.g., "supports_streaming")
            
        Returns:
            List of provider names with the capability
        """
        matching_providers = []
        
        for name, provider in self._providers.items():
            capabilities = provider.get_capabilities()
            if capabilities.get(capability, False):
                matching_providers.append(name)
        
        return matching_providers
    
    def set_default_provider(self, name: str):
        """Set the default provider.
        
        Args:
            name: Name of provider to set as default
            
        Raises:
            ProviderNotFoundError: If provider not found
        """
        if name not in self._providers:
            raise ProviderNotFoundError(f"Provider '{name}' not found")
        
        self._default_provider = name
    
    def get_default_provider(self) -> Optional[LLMProvider]:
        """Get the default provider.
        
        Returns:
            Default LLMProvider or None if not set
        """
        if self._default_provider:
            return self._providers.get(self._default_provider)
        return None
    
    def clear(self):
        """Clear all registered providers."""
        self._providers.clear()
        self._default_provider = None


# Global registry instance
_global_registry = ProviderRegistry()


def get_registry() -> ProviderRegistry:
    """Get the global provider registry.
    
    Returns:
        Global ProviderRegistry instance
    """
    return _global_registry


def register_provider(name: str, provider: LLMProvider):
    """Register a provider in the global registry.
    
    Args:
        name: Unique name for the provider
        provider: LLMProvider instance
    """
    _global_registry.register_provider(name, provider)


def get_provider(name: str) -> LLMProvider:
    """Get a provider from the global registry.
    
    Args:
        name: Name of the provider
        
    Returns:
        LLMProvider instance
    """
    return _global_registry.get_provider(name)