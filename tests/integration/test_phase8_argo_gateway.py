"""Integration tests for Phase 8: Argo Gateway Integration."""

import asyncio
import os
from unittest.mock import patch, Mock, AsyncMock

import pytest

from src.llm.argo_provider import ArgoLLMProvider, ArgoConnectionError


@pytest.mark.integration
class TestArgoGatewayIntegration:
    """Test Argo Gateway integration functionality."""
    
    @pytest.mark.asyncio
    async def test_argo_connectivity(self):
        """Test basic connectivity to Argo Gateway."""
        # Test with mock environment
        with patch.dict(os.environ, {
            "ARGO_PROXY_URL": "http://localhost:8000/v1",
            "ARGO_AUTH_USER": "test_scientist"
        }):
            provider = ArgoLLMProvider()
            
            # Mock the HTTP client for testing
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}
            mock_client.get.return_value = mock_response
            
            with patch.object(provider, '_client', mock_client):
                # Test connectivity
                is_connected = await provider.test_connectivity()
                assert is_connected is True
                
                # Verify models endpoint was called (Argo uses /models for connectivity check)
                mock_client.get.assert_called_with("/models", timeout=5.0)
    
    @pytest.mark.asyncio
    async def test_model_routing(self):
        """Test model routing and selection."""
        provider = ArgoLLMProvider()
        
        # Mock the HTTP client
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"id": "argo:gpt4o", "status": "available"},
                {"id": "argo:claudeopus4", "status": "available"},
                {"id": "argo:gemini25pro", "status": "available"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_client.get.return_value = mock_response
        
        with patch.object(provider, '_client', mock_client):
            # Test model access verification
            models_to_check = ["gpt4o", "claudeopus4", "gemini25pro", "gpt35"]
            access_results = await provider.verify_model_access(models_to_check)
            
            # Verify results
            # After fixing the implementation, models with "argo:" prefix are properly matched
            assert access_results["gpt4o"] is True
            assert access_results["claudeopus4"] is True
            assert access_results["gemini25pro"] is True
            assert access_results["gpt35"] is False  # Not in the mocked response
    
    @pytest.mark.asyncio
    async def test_failover_behavior(self):
        """Test failover behavior when Argo is unavailable."""
        provider = ArgoLLMProvider()
        
        # Mock connection failure
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Connection refused")
        
        with patch.object(provider, '_client', mock_client):
            # Test connectivity returns False on failure
            is_connected = await provider.test_connectivity()
            assert is_connected is False
            
            # Test model access raises error on failure
            with pytest.raises(ArgoConnectionError):
                await provider.verify_model_access(["gpt-4o"])
    
    @pytest.mark.asyncio
    async def test_cost_tracking(self):
        """Test cost tracking capabilities."""
        # This is a placeholder for future implementation
        # Will be implemented when actual cost tracking is added
        provider = ArgoLLMProvider()
        capabilities = provider.get_capabilities()
        
        # Verify provider identifies itself
        assert capabilities["provider"] == "argo"
        assert "models" in capabilities
        assert len(capabilities["models"]) > 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker(self):
        """Test circuit breaker pattern implementation."""
        # This is a placeholder for future implementation
        # Will be implemented when circuit breaker is added
        provider = ArgoLLMProvider()
        
        # For now, just verify the provider can be created
        assert provider is not None
        assert provider.max_retries == 3
    
    @pytest.mark.asyncio
    async def test_request_queuing(self):
        """Test request queuing during outages."""
        # This is a placeholder for future implementation
        # Will be implemented when request queuing is added
        provider = ArgoLLMProvider()
        
        # For now, verify timeout configuration
        assert provider.timeout == 30
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        provider = ArgoLLMProvider()
        
        # Mock successful responses
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_client.get.return_value = mock_response
        
        with patch.object(provider, '_client', mock_client):
            # Test multiple concurrent connectivity checks
            tasks = [provider.test_connectivity() for _ in range(5)]
            results = await asyncio.gather(*tasks)
            
            # All should succeed
            assert all(results)
            assert len(results) == 5
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="May fail - proxy failover not yet implemented")
    async def test_proxy_failover(self):
        """Test failover to alternate proxy endpoints."""
        # This will be implemented in later phases
        pass
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="May fail - rate limiting not yet implemented")
    async def test_rate_limiting(self):
        """Test rate limiting enforcement."""
        # This will be implemented in later phases
        pass
    
    @pytest.mark.asyncio
    async def test_health_monitoring(self):
        """Test health check monitoring functionality."""
        provider = ArgoLLMProvider()
        
        # Mock health responses
        health_responses = [
            {"status": "healthy", "models_available": 5},
            {"status": "degraded", "models_available": 3},
            {"status": "healthy", "models_available": 5}
        ]
        response_index = 0
        
        async def mock_get_health_status():
            nonlocal response_index
            response = health_responses[response_index % len(health_responses)]
            response_index += 1
            return response
        
        # Mock the health status method
        provider.get_health_status = mock_get_health_status
        
        # Track status changes
        status_changes = []
        
        def on_status_change(old_status, new_status):
            status_changes.append((old_status, new_status))
        
        # Start health monitoring
        await provider.start_health_monitoring(
            interval=0.1,
            on_status_change=on_status_change
        )
        
        # Wait for status changes
        await asyncio.sleep(0.35)
        
        # Stop monitoring
        await provider.stop_health_monitoring()
        
        # Verify health checks occurred
        assert response_index >= 3
        
        # Verify status changes were detected
        assert len(status_changes) >= 2
        assert ("healthy", "degraded") in status_changes
        assert ("degraded", "healthy") in status_changes
        
        # Verify health summary
        summary = provider.get_health_summary()
        assert "current_status" in summary
        assert "total_checks" in summary
        assert summary["total_checks"] >= 3