"""Argo Gateway LLM Provider implementation."""

import asyncio
import os
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from src.llm.base import LLMProvider, LLMRequest, LLMResponse, LLMError


class ArgoConnectionError(Exception):
    """Raised when connection to Argo Gateway fails."""
    pass


class ArgoLLMProvider(LLMProvider):
    """LLM Provider implementation for Argo Gateway."""
    
    def __init__(
        self,
        proxy_url: Optional[str] = None,
        auth_user: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ):
        """Initialize Argo provider with configuration.
        
        Args:
            proxy_url: Argo proxy URL (default from ARGO_PROXY_URL env var)
            auth_user: Authentication user ID (default from ARGO_AUTH_USER env var)
            timeout: Request timeout in seconds (default from ARGO_REQUEST_TIMEOUT or 30)
            max_retries: Maximum retry attempts (default from ARGO_MAX_RETRIES or 3)
        """
        self.proxy_url = proxy_url or os.getenv("ARGO_PROXY_URL", "http://localhost:8050/v1")
        self.auth_user = auth_user or os.getenv("ARGO_AUTH_USER", "")
        self.timeout = timeout or int(os.getenv("ARGO_REQUEST_TIMEOUT", "30"))
        self.max_retries = max_retries or int(os.getenv("ARGO_MAX_RETRIES", "3"))
        
        # Initialize HTTP client
        self._client = httpx.AsyncClient(
            base_url=self.proxy_url,
            timeout=self.timeout,
            headers=self._get_default_headers()
        )
        
        # Model mapping from logical names to Argo names
        self.model_mapping = {
            "gpt-4o": "argo:gpt-4o",
            "gpt-3.5-turbo": "argo:gpt-3.5-turbo",
            "claude-opus-4": "argo:claude-opus-4",
            "claude-3-sonnet": "argo:claude-3-sonnet",
            "gemini-2.5-pro": "argo:gemini-2.5-pro",
            "gemini-2.5-flash": "argo:gemini-2.5-flash"
        }
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for Argo requests."""
        headers = {
            "Content-Type": "application/json"
        }
        if self.auth_user:
            headers["X-User-Id"] = self.auth_user
        return headers
    
    async def test_connectivity(self) -> bool:
        """Test connectivity to Argo Gateway.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = await self._client.get("/health", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False
    
    async def verify_model_access(self, models: List[str]) -> Dict[str, bool]:
        """Verify access to specific models.
        
        Args:
            models: List of model names to check
            
        Returns:
            Dictionary mapping model names to availability status
        """
        try:
            response = await self._client.get("/models")
            response.raise_for_status()
            
            available_models = response.json()
            argo_models = set()
            
            for model in available_models.get("models", []):
                model_id = model.get("id", "")
                if model_id.startswith("argo:"):
                    argo_models.add(model_id)
            
            # Check each requested model
            result = {}
            for model in models:
                argo_name = self.model_mapping.get(model, f"argo:{model}")
                result[model] = argo_name in argo_models
                
            return result
            
        except Exception as e:
            raise ArgoConnectionError(f"Failed to verify model access: {str(e)}")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status from Argo Gateway.
        
        Returns:
            Health status information
        """
        try:
            response = await self._client.get("/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise ArgoConnectionError(f"Failed to get health status: {str(e)}")
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Argo Gateway.
        
        Args:
            request: LLM request
            
        Returns:
            LLM response
        """
        # This will be implemented in the next iteration
        raise NotImplementedError("Generate method not yet implemented")
    
    async def analyze(self, request: LLMRequest) -> LLMResponse:
        """Analyze existing content based on the request.
        
        Args:
            request: The LLM request containing content to analyze
            
        Returns:
            LLMResponse with analysis results or error
        """
        # This will be implemented in the next iteration
        raise NotImplementedError("Analyze method not yet implemented")
    
    async def evaluate(self, request: LLMRequest) -> LLMResponse:
        """Evaluate content against specified criteria.
        
        Args:
            request: The LLM request containing content and evaluation criteria
            
        Returns:
            LLMResponse with evaluation results or error
        """
        # This will be implemented in the next iteration
        raise NotImplementedError("Evaluate method not yet implemented")
    
    async def compare(self, request: LLMRequest) -> LLMResponse:
        """Compare multiple items based on specified criteria.
        
        Args:
            request: The LLM request containing items to compare
            
        Returns:
            LLMResponse with comparison results or error
        """
        # This will be implemented in the next iteration
        raise NotImplementedError("Compare method not yet implemented")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this LLM provider.
        
        Returns:
            Dictionary describing model capabilities
        """
        return {
            "provider": "argo",
            "supports_streaming": False,
            "supports_multimodal": True,
            "supports_function_calling": True,
            "models": list(self.model_mapping.keys()),
            "max_retries": self.max_retries,
            "timeout": self.timeout
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the Argo provider.
        
        Returns:
            Dictionary with provider metadata
        """
        return {
            "provider": "argo",
            "proxy_url": self.proxy_url,
            "available_models": list(self.model_mapping.keys()),
            "auth_configured": bool(self.auth_user)
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._client.aclose()