"""Integration tests for Argo provider with abstraction layer."""

import os
import pytest
from unittest.mock import patch, AsyncMock

from src.llm import get_registry, ArgoLLMProvider
from src.llm.setup import setup_providers, get_configured_provider
from src.llm.capabilities import CapabilityManager


class TestArgoIntegration:
    """Test Argo provider integration with abstraction layer."""
    
    def teardown_method(self):
        """Clear registry after each test."""
        get_registry().clear()
    
    def test_argo_provider_registration(self):
        """Test registering Argo provider."""
        # Set up providers with Argo configuration
        with patch.dict(os.environ, {"ARGO_PROXY_URL": "http://localhost:8000/v1"}):
            registry = setup_providers()
        
        # Check Argo is registered
        assert "argo" in registry.list_providers()
        assert "mock" in registry.list_providers()
        
        # Check Argo is default
        default = registry.get_default_provider()
        assert isinstance(default, ArgoLLMProvider)
    
    def test_get_configured_argo_provider(self):
        """Test getting configured Argo provider."""
        with patch.dict(os.environ, {"ARGO_PROXY_URL": "http://localhost:8000/v1"}):
            # Get Argo provider
            provider = get_configured_provider("argo")
            assert isinstance(provider, ArgoLLMProvider)
            
            # Get default (should be Argo)
            default = get_configured_provider()
            assert isinstance(default, ArgoLLMProvider)
    
    def test_argo_capabilities(self):
        """Test Argo provider capabilities."""
        with patch.dict(os.environ, {"ARGO_PROXY_URL": "http://localhost:8000/v1"}):
            provider = ArgoLLMProvider()
            capabilities = provider.get_capabilities()
            
            assert capabilities["provider"] == "argo"
            assert "models" in capabilities
            assert len(capabilities["models"]) > 0
            assert capabilities["supports_multimodal"] is True
            assert capabilities["supports_function_calling"] is True
    
    def test_argo_model_info(self):
        """Test Argo model information."""
        with patch.dict(os.environ, {
            "ARGO_PROXY_URL": "http://localhost:8000/v1",
            "ARGO_AUTH_USER": "test_user"
        }):
            provider = ArgoLLMProvider()
            info = provider.get_model_info()
            
            assert info["provider"] == "argo"
            assert info["proxy_url"] == "http://localhost:8000/v1"
            assert info["auth_configured"] is True
            assert "available_models" in info
    
    def test_argo_model_capabilities_mapping(self):
        """Test mapping Argo models to capability matrix."""
        with patch.dict(os.environ, {"ARGO_PROXY_URL": "http://localhost:8000/v1"}):
            provider = ArgoLLMProvider()
            
            # Check that Argo models have expected capabilities
            capabilities = provider.get_capabilities()
            
            # Verify provider supports expected features
            assert capabilities["supports_multimodal"] is True
            assert capabilities["supports_function_calling"] is True
            assert capabilities["supports_streaming"] is False
            
            # Verify models are listed
            models = capabilities["models"]
            assert "gpt4o" in models
            assert "claudeopus4" in models
            assert "gemini25pro" in models
    
    @pytest.mark.asyncio
    async def test_rate_limiting_with_argo(self):
        """Test rate limiting configuration for Argo provider."""
        from src.llm.rate_limiter import RateLimitConfig
        
        # Create rate limit config for Argo models
        configs = {
            "gpt4o": RateLimitConfig(
                requests_per_minute=60,
                tokens_per_minute=100000,
                concurrent_requests=10
            ),
            "claudeopus4": RateLimitConfig(
                requests_per_minute=30,
                tokens_per_minute=50000,
                concurrent_requests=5
            )
        }
        
        # Verify configurations
        assert configs["gpt4o"].requests_per_minute == 60
        assert configs["claudeopus4"].tokens_per_minute == 50000
    
    def test_model_routing_configuration(self):
        """Test model routing configuration for Argo."""
        with patch.dict(os.environ, {"ARGO_PROXY_URL": "http://localhost:8000/v1"}):
            provider = ArgoLLMProvider()
            
            # Configure routing rules
            routing_rules = {
                "supervisor": "gpt4o",
                "generation": "claudeopus4",
                "reflection": "gpt4o",
                "ranking": "gpt35turbo"
            }
            
            provider.set_routing_rules(routing_rules)
            
            # Test agent-specific selection
            assert provider.select_model_for_agent("supervisor") == "gpt4o"
            assert provider.select_model_for_agent("generation") == "claudeopus4"
    
    def test_cost_tracking_integration(self):
        """Test cost tracking across multiple requests."""
        with patch.dict(os.environ, {"ARGO_PROXY_URL": "http://localhost:8000/v1"}):
            provider = ArgoLLMProvider()
            
            # Track multiple requests
            provider.track_request("gpt4o", 1000, 500)
            provider.track_request("gpt4o", 2000, 1000)
            provider.track_request("claudeopus4", 500, 250)
            
            # Get usage report
            report = provider.get_usage_report()
            
            # Check GPT-4o usage
            gpt4_usage = report["gpt4o"]
            assert gpt4_usage["request_count"] == 2
            assert gpt4_usage["total_input_tokens"] == 3000
            assert gpt4_usage["total_output_tokens"] == 1500
            assert gpt4_usage["total_cost"] > 0
            
            # Check Claude usage
            claude_usage = report["claudeopus4"]
            assert claude_usage["request_count"] == 1
            assert claude_usage["total_cost"] > 0