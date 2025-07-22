"""Argo Gateway LLM Provider implementation."""

import asyncio
import os
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta
from dataclasses import dataclass

import httpx
from pydantic import BaseModel

from src.llm.base import LLMProvider, LLMRequest, LLMResponse, LLMError
from src.llm.circuit_breaker import CircuitBreaker, CircuitBreakerError


class ArgoConnectionError(Exception):
    """Raised when connection to Argo Gateway fails."""
    pass


@dataclass
class QueuedRequest:
    """Represents a queued LLM request."""
    request: LLMRequest
    enqueued_at: datetime
    future: asyncio.Future


class RequestQueue:
    """Queue for holding requests during outages."""
    
    def __init__(self, max_size: int = 1000, max_wait_time: int = 300):
        """Initialize request queue.
        
        Args:
            max_size: Maximum number of requests to queue
            max_wait_time: Maximum time in seconds to hold a request
        """
        self.max_size = max_size
        self.max_wait_time = max_wait_time
        self._queue: deque[QueuedRequest] = deque()
        self._lock = asyncio.Lock()
    
    def size(self) -> int:
        """Get current queue size."""
        return len(self._queue)
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._queue) == 0
    
    def enqueue(self, request: LLMRequest) -> bool:
        """Add request to queue.
        
        Args:
            request: LLM request to queue
            
        Returns:
            True if queued successfully, False if queue is full
        """
        if len(self._queue) >= self.max_size:
            return False
        
        future = asyncio.Future()
        queued_request = QueuedRequest(
            request=request,
            enqueued_at=datetime.now(),
            future=future
        )
        self._queue.append(queued_request)
        return True
    
    def dequeue(self) -> Optional[QueuedRequest]:
        """Remove and return the oldest non-expired request.
        
        Returns:
            Oldest queued request or None if queue is empty
        """
        now = datetime.now()
        
        while self._queue:
            queued_request = self._queue[0]
            
            # Check if request has expired
            age = (now - queued_request.enqueued_at).total_seconds()
            if age > self.max_wait_time:
                # Remove expired request
                self._queue.popleft()
                # Set exception on the future
                queued_request.future.set_exception(
                    TimeoutError("Request expired in queue")
                )
                continue
            
            # Return valid request
            return self._queue.popleft()
        
        return None
    
    def clear(self):
        """Clear all queued requests."""
        while self._queue:
            queued_request = self._queue.popleft()
            queued_request.future.cancel()


class ModelSelector:
    """Handles model selection logic and usage tracking."""
    
    def __init__(self):
        """Initialize model selector with costs and capabilities."""
        # Model costs per 1M tokens (input, output)
        self.model_costs = {
            "gpto3": (15.0, 60.0),  # $15/$60 per 1M tokens (reasoning model)
            "gpt4o": (5.0, 15.0),  # $5/$15 per 1M tokens
            "gpt35": (0.5, 1.5),  # $0.50/$1.50 per 1M tokens
            "claudeopus4": (15.0, 75.0),  # $15/$75 per 1M tokens
            "claudesonnet4": (3.0, 15.0),  # $3/$15 per 1M tokens
            "gemini25pro": (3.5, 10.5),  # $3.50/$10.50 per 1M tokens
            "gemini25flash": (0.075, 0.3),  # $0.075/$0.30 per 1M tokens
        }
        
        # Model capabilities
        self.model_capabilities = {
            "gpto3": ["deep_reasoning", "complex_analysis", "step_by_step", "verification"],
            "gpt4o": ["reasoning", "generation", "analysis", "coding"],
            "gpt35": ["simple_query", "summarization", "basic_analysis"],
            "claudeopus4": ["reasoning", "generation", "creative", "long_context"],
            "claudesonnet4": ["analysis", "summarization", "moderate_reasoning"],
            "gemini25pro": ["reasoning", "analysis", "multimodal"],
            "gemini25flash": ["simple_query", "fast_response", "basic_analysis"],
        }
        
        # Task type to preferred models mapping
        self.task_preferences = {
            "generation": ["claudeopus4", "gpt4o"],
            "reasoning": ["gpto3", "gpt4o", "claudeopus4", "gemini25pro"],
            "simple_query": ["gpt35", "gemini25flash"],
            "analysis": ["gpt4o", "gemini25pro", "claudesonnet4"],
            "summarization": ["claudesonnet4", "gpt35"],
        }
        
        # Usage tracking
        self.usage_stats = defaultdict(lambda: {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "request_count": 0,
            "total_cost": 0.0
        })
        
        # Model availability
        self.available_models = set(self.model_costs.keys())
        
        # Custom routing rules (can be overridden)
        self.routing_rules = {}
    
    def select_model_for_task(self, task_type: str, budget_conscious: bool = False) -> str:
        """Select the best model for a given task type.
        
        Args:
            task_type: Type of task (generation, reasoning, etc.)
            budget_conscious: Whether to prioritize cost over capability
            
        Returns:
            Selected model name
        """
        # Get preferred models for task
        preferred = self.task_preferences.get(task_type, ["gpt4o"])
        
        # Filter by availability
        available_preferred = [m for m in preferred if m in self.available_models]
        
        if not available_preferred:
            # Fallback to any available model
            if self.available_models:
                available_preferred = list(self.available_models)
            else:
                raise ValueError("No models available")
        
        if budget_conscious:
            # Sort by cost (cheapest first)
            available_preferred.sort(key=lambda m: self.model_costs.get(m, (999, 999))[0])
        
        return available_preferred[0]
    
    def select_model_for_agent(self, agent_type: str) -> str:
        """Select model based on agent-specific routing rules.
        
        Args:
            agent_type: Type of agent (supervisor, generation, etc.)
            
        Returns:
            Selected model name
        """
        # Check custom routing rules first
        if agent_type in self.routing_rules:
            model = self.routing_rules[agent_type]
            if model in self.available_models:
                return model
        
        # Default agent to task mapping
        agent_task_map = {
            "supervisor": "reasoning",
            "generation": "generation",
            "reflection": "analysis",
            "ranking": "simple_query",
            "evolution": "generation",
            "proximity": "simple_query",
            "meta_review": "analysis"
        }
        
        task_type = agent_task_map.get(agent_type, "reasoning")
        return self.select_model_for_task(task_type)
    
    def get_estimated_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost for a request.
        
        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in dollars
        """
        if model not in self.model_costs:
            return 0.0
        
        input_cost, output_cost = self.model_costs[model]
        
        # Calculate cost (prices are per 1M tokens)
        total_cost = (input_tokens * input_cost / 1_000_000) + (output_tokens * output_cost / 1_000_000)
        
        return round(total_cost, 6)
    
    def track_usage(self, model: str, input_tokens: int, output_tokens: int):
        """Track usage statistics for a model.
        
        Args:
            model: Model name
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
        """
        stats = self.usage_stats[model]
        stats["total_input_tokens"] += input_tokens
        stats["total_output_tokens"] += output_tokens
        stats["request_count"] += 1
        stats["total_cost"] += self.get_estimated_cost(model, input_tokens, output_tokens)
    
    def get_usage_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get usage statistics for all models.
        
        Returns:
            Dictionary of usage stats by model
        """
        return dict(self.usage_stats)
    
    def set_routing_rules(self, rules: Dict[str, str]):
        """Set custom routing rules for agents.
        
        Args:
            rules: Dictionary mapping agent types to model names
        """
        self.routing_rules = rules
    
    def mark_model_unavailable(self, model: str):
        """Mark a model as unavailable.
        
        Args:
            model: Model name to mark unavailable
        """
        self.available_models.discard(model)
    
    def mark_model_available(self, model: str):
        """Mark a model as available.
        
        Args:
            model: Model name to mark available
        """
        if model in self.model_costs:
            self.available_models.add(model)
    
    def get_available_models(self) -> List[str]:
        """Get list of available models.
        
        Returns:
            List of available model names
        """
        return list(self.available_models)


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
        self.proxy_url = proxy_url or os.getenv("ARGO_PROXY_URL", "http://localhost:8000/v1")
        self.auth_user = auth_user or os.getenv("ARGO_AUTH_USER", "")
        self.timeout = timeout or int(os.getenv("ARGO_REQUEST_TIMEOUT", "30"))
        self.max_retries = max_retries or int(os.getenv("ARGO_MAX_RETRIES", "3"))
        
        # Initialize HTTP client
        self._client = httpx.AsyncClient(
            base_url=self.proxy_url,
            timeout=self.timeout,
            headers=self._get_default_headers()
        )
        
        # Available models - using Argo model IDs directly
        self.available_models = [
            "gpt4o", "gpt35", "gpt35large", "gpt4turbo",
            "claudeopus4", "claudesonnet4", "claudesonnet37",
            "gemini25pro", "gemini25flash"
        ]
        
        # Initialize model selector
        self.model_selector = ModelSelector()
        # Update model selector with Argo's available models
        self.model_selector.available_models = set(self.available_models)
        
        # Initialize circuit breakers per model
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        for model in self.available_models:
            self._circuit_breakers[model] = CircuitBreaker(
                failure_threshold=3,
                recovery_timeout=60.0,
                half_open_max_calls=2
            )
        
        # Initialize request queue
        self.request_queue = RequestQueue(
            max_size=int(os.getenv("ARGO_QUEUE_MAX_SIZE", "1000")),
            max_wait_time=int(os.getenv("ARGO_QUEUE_MAX_WAIT", "300"))
        )
        
        # Queue processor task
        self._queue_processor_task = None
        self._stop_queue_processor = False
    
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
            # Test with OpenAI-compatible models endpoint
            response = await self._client.get("/models", timeout=5.0)
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
                    # Remove the "argo:" prefix for comparison
                    argo_models.add(model_id[5:])
            
            # Check each requested model
            result = {}
            for model in models:
                # Models are already in Argo format
                result[model] = model in argo_models
                
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
        model = request.content.get("parameters", {}).get("model", "gpt4o")
        circuit_breaker = self._circuit_breakers.get(model)
        
        if circuit_breaker and circuit_breaker.is_open():
            # Circuit breaker is open, try to queue the request
            if self.request_queue.enqueue(request):
                # Start queue processor if not running
                if self._queue_processor_task is None or self._queue_processor_task.done():
                    self._queue_processor_task = asyncio.create_task(self._queue_processor())
                
                return LLMResponse(
                    request_id=request.request_id,
                    status="success",
                    response={
                        "content": "Request queued for processing when service recovers",
                        "metadata": {
                            "queued": True,
                            "queue_size": self.request_queue.size()
                        }
                    },
                    error=None
                )
            else:
                # Queue is full
                return LLMResponse(
                    request_id=request.request_id,
                    status="error",
                    response=None,
                    error=LLMError(
                        code="QUEUE_FULL",
                        message="Request queue is full. Please try again later.",
                        recoverable=True
                    )
                )
        
        # Normal processing (circuit breaker not open)
        try:
            # This is a placeholder for actual API call
            # Will be implemented when we add the actual Argo API calls
            raise NotImplementedError("Actual API call not yet implemented")
        except Exception as e:
            if circuit_breaker:
                circuit_breaker.record_failure()
            raise
    
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
            "models": self.available_models,
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
            "available_models": self.available_models,
            "auth_configured": bool(self.auth_user)
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Stop queue processor
        self._stop_queue_processor = True
        if self._queue_processor_task:
            await self._queue_processor_task
        
        await self._client.aclose()
    
    def select_model_for_task(self, task_type: str, budget_conscious: bool = False) -> str:
        """Select the best model for a given task type.
        
        Args:
            task_type: Type of task (generation, reasoning, etc.)
            budget_conscious: Whether to prioritize cost over capability
            
        Returns:
            Selected model name
        """
        return self.model_selector.select_model_for_task(task_type, budget_conscious)
    
    def select_model_for_agent(self, agent_type: str) -> str:
        """Select model based on agent-specific routing rules.
        
        Args:
            agent_type: Type of agent (supervisor, generation, etc.)
            
        Returns:
            Selected model name
        """
        return self.model_selector.select_model_for_agent(agent_type)
    
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost for a request.
        
        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in dollars
        """
        return self.model_selector.get_estimated_cost(model, input_tokens, output_tokens)
    
    def track_request(self, model: str, input_tokens: int, output_tokens: int):
        """Track usage for a completed request.
        
        Args:
            model: Model name used
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
        """
        self.model_selector.track_usage(model, input_tokens, output_tokens)
    
    def get_usage_report(self) -> Dict[str, Dict[str, Any]]:
        """Get usage report for all models.
        
        Returns:
            Dictionary of usage statistics by model
        """
        return self.model_selector.get_usage_stats()
    
    def set_routing_rules(self, rules: Dict[str, str]):
        """Set custom routing rules for agents.
        
        Args:
            rules: Dictionary mapping agent types to model names
        """
        self.model_selector.set_routing_rules(rules)
    
    def mark_model_status(self, model: str, available: bool):
        """Update model availability status.
        
        Args:
            model: Model name
            available: Whether model is available
        """
        if available:
            self.model_selector.mark_model_available(model)
        else:
            self.model_selector.mark_model_unavailable(model)
    
    def get_circuit_breaker_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers.
        
        Returns:
            Dictionary mapping model names to circuit breaker info
        """
        status = {}
        for model, breaker in self._circuit_breakers.items():
            status[model] = breaker.get_state_info()
        return status
    
    def reset_circuit_breaker(self, model: str):
        """Reset circuit breaker for a specific model.
        
        Args:
            model: Model name to reset
        """
        if model in self._circuit_breakers:
            self._circuit_breakers[model].reset()
    
    async def _call_with_circuit_breaker(
        self,
        model: str,
        func: Any,
        *args,
        **kwargs
    ) -> Any:
        """Execute function through circuit breaker for model.
        
        Args:
            model: Model name
            func: Async function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        if model not in self._circuit_breakers:
            # Fallback to direct call if no breaker
            return await func(*args, **kwargs)
        
        breaker = self._circuit_breakers[model]
        try:
            result = await breaker.call(func, *args, **kwargs)
            return result
        except CircuitBreakerError:
            # Mark model as unavailable when circuit opens
            self.model_selector.mark_model_unavailable(model)
            raise
        except Exception:
            # Check if circuit is now open after the failure
            if breaker.state == CircuitState.OPEN:
                self.model_selector.mark_model_unavailable(model)
            raise
    
    async def select_model_with_failover(
        self,
        task_type: str,
        preferred_model: Optional[str] = None
    ) -> str:
        """Select a model with failover support.
        
        Args:
            task_type: Type of task
            preferred_model: Preferred model if any
            
        Returns:
            Selected available model
            
        Raises:
            ValueError: If no models are available
        """
        if preferred_model and preferred_model in self.model_selector.available_models:
            # Check if preferred model's circuit is not open
            breaker = self._circuit_breakers.get(preferred_model)
            if breaker and breaker.state.value != "OPEN":
                return preferred_model
        
        # Get candidates based on task type
        candidates = self.model_selector.task_preferences.get(task_type, self.available_models)
        
        # Filter by availability and circuit state
        available_candidates = []
        for model in candidates:
            if model in self.model_selector.available_models:
                breaker = self._circuit_breakers.get(model)
                if not breaker or breaker.state.value != "OPEN":
                    available_candidates.append(model)
        
        if not available_candidates:
            raise ValueError(f"No models available for task type: {task_type}")
        
        return available_candidates[0]
    
    async def _queue_processor(self):
        """Background task to process queued requests."""
        while not self._stop_queue_processor:
            try:
                # Process any queued requests
                await self._process_queued_requests()
                
                # Wait before next check
                await asyncio.sleep(5.0)
            except Exception as e:
                # Log error but continue processing
                print(f"Error in queue processor: {e}")
                await asyncio.sleep(10.0)
    
    async def _process_queued_requests(self) -> int:
        """Process queued requests when circuit breakers recover.
        
        Returns:
            Number of requests processed
        """
        processed = 0
        
        while not self.request_queue.is_empty():
            queued_request = self.request_queue.dequeue()
            if not queued_request:
                break
            
            model = queued_request.request.content.get("parameters", {}).get("model", "gpt4o")
            circuit_breaker = self._circuit_breakers.get(model)
            
            # Check if circuit breaker has recovered
            if circuit_breaker and circuit_breaker.is_open():
                # Still open, re-queue (future will be cancelled)
                if not queued_request.future.cancelled():
                    queued_request.future.cancel()
                self.request_queue.enqueue(queued_request.request)
                break
            
            try:
                # Process the request
                # Note: This is a placeholder - actual implementation would call the API
                response = LLMResponse(
                    request_id=queued_request.request.request_id,
                    status="success",
                    response={
                        "content": "Processed from queue",
                        "metadata": {"processed_from_queue": True}
                    },
                    error=None
                )
                
                # Set result on the future if not cancelled
                if not queued_request.future.cancelled():
                    queued_request.future.set_result(response)
                
                processed += 1
                
                # Record success with circuit breaker
                if circuit_breaker:
                    circuit_breaker.record_success()
                    
            except Exception as e:
                # Set exception on the future
                if not queued_request.future.cancelled():
                    queued_request.future.set_exception(e)
                
                # Record failure with circuit breaker
                if circuit_breaker:
                    circuit_breaker.record_failure()
        
        return processed
