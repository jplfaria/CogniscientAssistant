"""Unit tests for ArgoLLMProvider."""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch, Mock

import pytest
from httpx import ConnectError, Response

from src.llm.argo_provider import ArgoLLMProvider, ArgoConnectionError


@pytest.fixture
def argo_provider():
    """Create an ArgoLLMProvider instance for testing."""
    with patch.dict(os.environ, {
        "ARGO_PROXY_URL": "http://localhost:8000/v1",
        "ARGO_AUTH_USER": "test_user",
        "ARGO_REQUEST_TIMEOUT": "30",
        "ARGO_MAX_RETRIES": "3"
    }):
        return ArgoLLMProvider()


@pytest.fixture
def mock_httpx_client():
    """Create a mock httpx client."""
    client = AsyncMock()
    return client


class TestArgoProviderInitialization:
    """Test ArgoLLMProvider initialization."""
    
    def test_init_with_env_vars(self):
        """Test initialization with environment variables."""
        with patch.dict(os.environ, {
            "ARGO_PROXY_URL": "http://test.argo:8000/v1",
            "ARGO_AUTH_USER": "scientist_123",
            "ARGO_REQUEST_TIMEOUT": "60",
            "ARGO_MAX_RETRIES": "5"
        }):
            provider = ArgoLLMProvider()
            assert provider.proxy_url == "http://test.argo:8000/v1"
            assert provider.auth_user == "scientist_123"
            assert provider.timeout == 60
            assert provider.max_retries == 5
    
    def test_init_with_defaults(self):
        """Test initialization with default values."""
        with patch.dict(os.environ, clear=True):
            provider = ArgoLLMProvider()
            assert provider.proxy_url == "http://localhost:8000/v1"
            assert provider.auth_user == ""
            assert provider.timeout == 30
            assert provider.max_retries == 3
    
    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        provider = ArgoLLMProvider(
            proxy_url="http://custom.argo:9000/v2",
            auth_user="custom_user",
            timeout=45,
            max_retries=2
        )
        assert provider.proxy_url == "http://custom.argo:9000/v2"
        assert provider.auth_user == "custom_user"
        assert provider.timeout == 45
        assert provider.max_retries == 2


class TestArgoConnectivity:
    """Test Argo connectivity methods."""
    
    @pytest.mark.asyncio
    async def test_test_connectivity_success(self, argo_provider, mock_httpx_client):
        """Test successful connectivity check."""
        # Mock successful response
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy", "models": ["gpt-4o", "claude-opus-4"]}
        mock_httpx_client.get.return_value = mock_response
        
        with patch.object(argo_provider, '_client', mock_httpx_client):
            result = await argo_provider.test_connectivity()
            
        assert result is True
        mock_httpx_client.get.assert_called_once_with(
            "/health",
            timeout=5.0
        )
    
    @pytest.mark.asyncio
    async def test_test_connectivity_connection_error(self, argo_provider, mock_httpx_client):
        """Test connectivity check with connection error."""
        # Mock connection error
        mock_httpx_client.get.side_effect = ConnectError("Connection refused")
        
        with patch.object(argo_provider, '_client', mock_httpx_client):
            result = await argo_provider.test_connectivity()
            
        assert result is False
    
    @pytest.mark.asyncio
    async def test_test_connectivity_http_error(self, argo_provider, mock_httpx_client):
        """Test connectivity check with HTTP error."""
        # Mock error response
        mock_response = Mock(spec=Response)
        mock_response.status_code = 503
        mock_response.json.return_value = {"error": "Service unavailable"}
        mock_httpx_client.get.return_value = mock_response
        
        with patch.object(argo_provider, '_client', mock_httpx_client):
            result = await argo_provider.test_connectivity()
            
        assert result is False
    
    @pytest.mark.asyncio
    async def test_verify_model_access_success(self, argo_provider, mock_httpx_client):
        """Test successful model access verification."""
        # Mock successful models response
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"id": "argo:gpt-4o", "status": "available"},
                {"id": "argo:claude-opus-4", "status": "available"},
                {"id": "argo:gemini-2.5-pro", "status": "available"},
                {"id": "argo:gpt-3.5-turbo", "status": "available"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_httpx_client.get.return_value = mock_response
        
        with patch.object(argo_provider, '_client', mock_httpx_client):
            models = ["gpt-4o", "claude-opus-4", "gemini-2.5-pro"]
            result = await argo_provider.verify_model_access(models)
            
        assert result == {
            "gpt-4o": True,
            "claude-opus-4": True,
            "gemini-2.5-pro": True
        }
        mock_httpx_client.get.assert_called_once_with("/models")
    
    @pytest.mark.asyncio
    async def test_verify_model_access_partial(self, argo_provider, mock_httpx_client):
        """Test model access verification with some models unavailable."""
        # Mock response with limited models
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"id": "argo:gpt-4o", "status": "available"},
                {"id": "argo:gpt-3.5-turbo", "status": "available"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_httpx_client.get.return_value = mock_response
        
        with patch.object(argo_provider, '_client', mock_httpx_client):
            models = ["gpt-4o", "claude-opus-4", "gemini-2.5-pro"]
            result = await argo_provider.verify_model_access(models)
            
        assert result == {
            "gpt-4o": True,
            "claude-opus-4": False,
            "gemini-2.5-pro": False
        }
    
    @pytest.mark.asyncio
    async def test_verify_model_access_error(self, argo_provider, mock_httpx_client):
        """Test model access verification with error."""
        # Mock error
        mock_httpx_client.get.side_effect = Exception("API Error")
        
        with patch.object(argo_provider, '_client', mock_httpx_client):
            models = ["gpt-4o"]
            with pytest.raises(ArgoConnectionError):
                await argo_provider.verify_model_access(models)


class TestArgoHealthCheck:
    """Test Argo health check functionality."""
    
    @pytest.mark.asyncio
    async def test_get_health_status_success(self, argo_provider, mock_httpx_client):
        """Test successful health status retrieval."""
        # Mock health response
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "uptime": 3600,
            "version": "1.2.3",
            "models_available": 5
        }
        mock_response.raise_for_status = Mock()
        mock_httpx_client.get.return_value = mock_response
        
        with patch.object(argo_provider, '_client', mock_httpx_client):
            health = await argo_provider.get_health_status()
            
        assert health["status"] == "healthy"
        assert health["uptime"] == 3600
        assert health["version"] == "1.2.3"
        assert health["models_available"] == 5
    
    @pytest.mark.asyncio
    async def test_get_health_status_unhealthy(self, argo_provider, mock_httpx_client):
        """Test health status when service is unhealthy."""
        # Mock unhealthy response
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "degraded",
            "issues": ["High latency", "Model unavailable"]
        }
        mock_response.raise_for_status = Mock()
        mock_httpx_client.get.return_value = mock_response
        
        with patch.object(argo_provider, '_client', mock_httpx_client):
            health = await argo_provider.get_health_status()
            
        assert health["status"] == "degraded"
        assert "issues" in health
    
    @pytest.mark.asyncio
    async def test_get_health_status_error(self, argo_provider, mock_httpx_client):
        """Test health status with connection error."""
        # Mock connection error
        mock_httpx_client.get.side_effect = ConnectError("Connection failed")
        
        with patch.object(argo_provider, '_client', mock_httpx_client):
            with pytest.raises(ArgoConnectionError):
                await argo_provider.get_health_status()