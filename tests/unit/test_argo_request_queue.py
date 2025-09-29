"""Unit tests for Argo provider request queuing during outages."""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.llm.argo_provider import ArgoLLMProvider, RequestQueue
from src.llm.base import LLMRequest, LLMResponse, LLMError
from src.llm.circuit_breaker import CircuitBreaker, CircuitBreakerError


class TestRequestQueue:
    """Test request queuing functionality."""
    
    def test_queue_initialization(self):
        """Test queue is properly initialized."""
        queue = RequestQueue(max_size=100, max_wait_time=300)
        
        assert queue.max_size == 100
        assert queue.max_wait_time == 300
        assert queue.size() == 0
        assert queue.is_empty()
    
    def test_enqueue_request(self):
        """Test adding requests to the queue."""
        queue = RequestQueue(max_size=10)
        
        request = LLMRequest(
            request_id="test-1",
            agent_type="generation",
            request_type="generate",
            content={
                "prompt": "Test prompt",
                "context": {},
                "parameters": {"model": "gpt4o", "temperature": 0.7}
            }
        )
        
        # Add request to queue
        assert queue.enqueue(request)
        assert queue.size() == 1
        assert not queue.is_empty()
    
    def test_queue_max_size(self):
        """Test queue respects maximum size."""
        queue = RequestQueue(max_size=2)
        
        request1 = LLMRequest(
            request_id="test-1",
            agent_type="generation",
            request_type="generate",
            content={"prompt": "Test 1", "context": {}, "parameters": {"model": "gpt4o"}}
        )
        request2 = LLMRequest(
            request_id="test-2",
            agent_type="generation",
            request_type="generate",
            content={"prompt": "Test 2", "context": {}, "parameters": {"model": "gpt4o"}}
        )
        request3 = LLMRequest(
            request_id="test-3",
            agent_type="generation",
            request_type="generate",
            content={"prompt": "Test 3", "context": {}, "parameters": {"model": "gpt4o"}}
        )
        
        # First two should succeed
        assert queue.enqueue(request1)
        assert queue.enqueue(request2)
        assert queue.size() == 2
        
        # Third should fail
        assert not queue.enqueue(request3)
        assert queue.size() == 2
    
    def test_dequeue_request(self):
        """Test removing requests from the queue."""
        queue = RequestQueue(max_size=10)
        
        request1 = LLMRequest(
            request_id="test-1",
            agent_type="generation",
            request_type="generate",
            content={"prompt": "Test 1", "context": {}, "parameters": {"model": "gpt4o"}}
        )
        request2 = LLMRequest(
            request_id="test-2",
            agent_type="generation",
            request_type="generate",
            content={"prompt": "Test 2", "context": {}, "parameters": {"model": "gpt4o"}}
        )
        
        queue.enqueue(request1)
        queue.enqueue(request2)
        
        # Dequeue in FIFO order
        dequeued = queue.dequeue()
        assert dequeued is not None
        assert dequeued.request.content["prompt"] == "Test 1"
        assert queue.size() == 1
        
        dequeued = queue.dequeue()
        assert dequeued is not None
        assert dequeued.request.content["prompt"] == "Test 2"
        assert queue.size() == 0
        assert queue.is_empty()
        
        # Queue empty
        assert queue.dequeue() is None
    
    def test_expired_requests(self):
        """Test that expired requests are not returned."""
        queue = RequestQueue(max_size=10, max_wait_time=1)  # 1 second wait time
        
        request = LLMRequest(
            request_id="test-1",
            agent_type="generation",
            request_type="generate",
            content={"prompt": "Test", "context": {}, "parameters": {"model": "gpt4o"}}
        )
        queue.enqueue(request)
        
        # Wait for request to expire
        import time
        time.sleep(1.1)
        
        # Should return None for expired request
        assert queue.dequeue() is None
        assert queue.size() == 0
    
    def test_clear_queue(self):
        """Test clearing the queue."""
        queue = RequestQueue(max_size=10)
        
        for i in range(5):
            queue.enqueue(LLMRequest(
                request_id=f"test-{i}",
                agent_type="generation",
                request_type="generate",
                content={"prompt": f"Test {i}", "context": {}, "parameters": {"model": "gpt4o"}}
            ))
        
        assert queue.size() == 5
        
        queue.clear()
        assert queue.size() == 0
        assert queue.is_empty()


class TestArgoRequestQueuing:
    """Test request queuing in ArgoLLMProvider."""
    
    @pytest.mark.asyncio
    async def test_queue_during_circuit_breaker_open(self):
        """Test requests are queued when circuit breaker is open."""
        provider = ArgoLLMProvider()
        
        # Mock circuit breaker as open
        with patch.object(provider._circuit_breakers["gpt4o"], "is_open", return_value=True):
            with patch.object(provider._circuit_breakers["gpt4o"], "is_half_open", return_value=False):
                request = LLMRequest(
                    request_id="test-1",
                    agent_type="generation",
                    request_type="generate",
                    content={
                        "prompt": "Test prompt",
                        "context": {},
                        "parameters": {"model": "gpt4o", "temperature": 0.7}
                    }
                )
                
                # Request should be queued, not failed immediately
                with patch.object(provider.request_queue, "enqueue") as mock_enqueue:
                    mock_enqueue.return_value = True
                    
                    response = await provider.generate(request)
                    
                    # Should return a response indicating request was queued
                    assert response.status == "success"
                    assert response.response["content"] == "Request queued for processing when service recovers"
                    assert response.error is None
                    mock_enqueue.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_queued_requests_on_recovery(self):
        """Test queued requests are processed when service recovers."""
        provider = ArgoLLMProvider()
        
        # Add some requests to queue
        request1 = LLMRequest(
            request_id="test-1",
            agent_type="generation",
            request_type="generate",
            content={"prompt": "Test 1", "context": {}, "parameters": {"model": "gpt4o"}}
        )
        request2 = LLMRequest(
            request_id="test-2",
            agent_type="generation",
            request_type="generate",
            content={"prompt": "Test 2", "context": {}, "parameters": {"model": "gpt4o"}}
        )
        
        provider.request_queue.enqueue(request1)
        provider.request_queue.enqueue(request2)
        
        # Mock successful API calls
        with patch.object(provider._client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{
                    "message": {"content": "Response"}
                }],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15
                }
            }
            mock_post.return_value = mock_response
            
            # Process queued requests
            processed = await provider._process_queued_requests()
            
            assert processed == 2
            assert provider.request_queue.is_empty()
    
    @pytest.mark.asyncio
    async def test_queue_overflow_handling(self):
        """Test behavior when queue is full."""
        provider = ArgoLLMProvider()
        provider.request_queue = RequestQueue(max_size=1)
        
        # Fill the queue
        request1 = LLMRequest(
            request_id="test-1",
            agent_type="generation",
            request_type="generate",
            content={"prompt": "Test 1", "context": {}, "parameters": {"model": "gpt4o"}}
        )
        provider.request_queue.enqueue(request1)
        
        # Mock circuit breaker as open
        with patch.object(provider._circuit_breakers["gpt4o"], "is_open", return_value=True):
            with patch.object(provider._circuit_breakers["gpt4o"], "is_half_open", return_value=False):
                request2 = LLMRequest(
                    request_id="test-2",
                    agent_type="generation",
                    request_type="generate",
                    content={"prompt": "Test 2", "context": {}, "parameters": {"model": "gpt4o"}}
                )
                
                # Should get error response when queue is full
                response = await provider.generate(request2)
                
                assert response.error is not None
                assert "queue is full" in response.error.message.lower()
    
    @pytest.mark.asyncio
    async def test_periodic_queue_processing(self):
        """Test that queued requests are periodically processed."""
        provider = ArgoLLMProvider()
        
        # Add request to queue
        request = LLMRequest(
            request_id="test-1",
            agent_type="generation",
            request_type="generate",
            content={"prompt": "Test", "context": {}, "parameters": {"model": "gpt4o"}}
        )
        provider.request_queue.enqueue(request)
        
        # Mock successful processing
        with patch.object(provider, "_process_queued_requests") as mock_process:
            mock_process.return_value = 1
            
            # Start queue processor
            task = asyncio.create_task(provider._queue_processor())
            
            # Wait a bit
            await asyncio.sleep(0.1)
            
            # Stop processor
            provider._stop_queue_processor = True
            await task
            
            # Should have attempted to process
            assert mock_process.called