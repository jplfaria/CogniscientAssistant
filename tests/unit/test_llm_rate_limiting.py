"""Tests for LLM rate limiting functionality."""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List

from src.llm.base import LLMRequest, LLMResponse
from src.llm.rate_limiter import (
    RateLimiter,
    TokenBucketRateLimiter,
    SlidingWindowRateLimiter,
    RateLimitConfig,
    RateLimitExceeded
)


class TestRateLimiter:
    """Test the base RateLimiter functionality."""
    
    def test_rate_limit_config(self):
        """Test RateLimitConfig creation and validation."""
        # Valid config
        config = RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            tokens_per_minute=10000,
            concurrent_requests=10
        )
        
        assert config.requests_per_minute == 60
        assert config.requests_per_hour == 1000
        assert config.tokens_per_minute == 10000
        assert config.concurrent_requests == 10
        
        # Invalid config should raise ValueError
        with pytest.raises(ValueError):
            RateLimitConfig(requests_per_minute=-1)
        
        with pytest.raises(ValueError):
            RateLimitConfig(concurrent_requests=0)


class TestTokenBucketRateLimiter:
    """Test token bucket rate limiting algorithm."""
    
    @pytest.mark.asyncio
    async def test_token_bucket_basic(self):
        """Test basic token bucket functionality."""
        config = RateLimitConfig(
            requests_per_minute=60,  # 1 per second
            concurrent_requests=10
        )
        
        limiter = TokenBucketRateLimiter(config)
        
        # Should allow first request
        assert await limiter.acquire() is True
        
        # Should allow requests up to the limit
        for _ in range(59):
            assert await limiter.acquire() is True
        
        # Next request should fail (bucket empty)
        with pytest.raises(RateLimitExceeded):
            await limiter.acquire(raise_on_limit=True)
    
    @pytest.mark.asyncio
    async def test_token_bucket_refill(self):
        """Test that token bucket refills over time."""
        config = RateLimitConfig(
            requests_per_minute=60  # 1 per second
        )
        
        limiter = TokenBucketRateLimiter(config)
        
        # Consume all tokens
        for _ in range(60):
            await limiter.acquire()
        
        # Should be rate limited
        assert await limiter.acquire() is False
        
        # Wait for refill
        await asyncio.sleep(1.1)
        
        # Should allow new request
        assert await limiter.acquire() is True
    
    @pytest.mark.asyncio
    async def test_token_bucket_burst(self):
        """Test burst capacity in token bucket."""
        config = RateLimitConfig(
            requests_per_minute=60,
            burst_size=10  # Allow burst of 10
        )
        
        limiter = TokenBucketRateLimiter(config)
        
        # Should allow burst
        tasks = []
        for _ in range(10):
            tasks.append(limiter.acquire())
        
        results = await asyncio.gather(*tasks)
        assert all(results)
    
    @pytest.mark.asyncio
    async def test_concurrent_request_limit(self):
        """Test concurrent request limiting."""
        config = RateLimitConfig(
            requests_per_minute=1000,  # High limit
            concurrent_requests=3
        )
        
        limiter = TokenBucketRateLimiter(config)
        
        # Start 3 concurrent "requests"
        async def simulate_request(duration: float):
            async with limiter.concurrent_request():
                await asyncio.sleep(duration)
                return True
        
        # These should all start
        tasks = []
        for _ in range(3):
            tasks.append(asyncio.create_task(simulate_request(0.5)))
        
        # Give tasks time to acquire the semaphore
        await asyncio.sleep(0.1)
        
        # This should be blocked
        with pytest.raises(RateLimitExceeded):
            async with limiter.concurrent_request():
                pass
        
        # Wait for others to complete
        await asyncio.gather(*tasks)
        
        # Now should allow new request
        async with limiter.concurrent_request():
            pass  # Should not raise


class TestSlidingWindowRateLimiter:
    """Test sliding window rate limiting algorithm."""
    
    @pytest.mark.asyncio
    async def test_sliding_window_basic(self):
        """Test basic sliding window functionality."""
        config = RateLimitConfig(
            requests_per_minute=10
        )
        
        limiter = SlidingWindowRateLimiter(config)
        
        # Should allow 10 requests
        for _ in range(10):
            assert await limiter.acquire() is True
        
        # 11th request should be rate limited
        assert await limiter.acquire() is False
    
    @pytest.mark.asyncio
    async def test_sliding_window_expiry(self):
        """Test that old requests expire from window."""
        config = RateLimitConfig(
            requests_per_minute=5,
            window_size_seconds=2  # 2 second window
        )
        
        limiter = SlidingWindowRateLimiter(config)
        
        # Use up the limit
        for _ in range(5):
            await limiter.acquire()
        
        # Should be limited
        assert await limiter.acquire() is False
        
        # Wait for window to slide
        await asyncio.sleep(2.1)
        
        # Should allow new requests
        assert await limiter.acquire() is True
    
    @pytest.mark.asyncio
    async def test_sliding_window_hour_limit(self):
        """Test hour-based rate limiting."""
        config = RateLimitConfig(
            requests_per_minute=1000,  # High minute limit
            requests_per_hour=100     # Low hour limit
        )
        
        limiter = SlidingWindowRateLimiter(config)
        
        # Should enforce the stricter limit
        request_count = 0
        for _ in range(150):
            if await limiter.acquire():
                request_count += 1
        
        # Should have stopped at hour limit
        assert request_count == 100


class TestRateLimiterIntegration:
    """Test rate limiter integration with LLM requests."""
    
    @pytest.mark.asyncio
    async def test_rate_limited_requests(self):
        """Test rate limiting applied to LLM requests."""
        config = RateLimitConfig(
            requests_per_minute=5,
            tokens_per_minute=1000
        )
        
        limiter = TokenBucketRateLimiter(config)
        
        # Create requests
        requests = []
        for i in range(10):
            request = LLMRequest(
                request_id=f"test-{i}",
                agent_type="generation",
                request_type="generate",
                content={
                    "prompt": "Test prompt",
                    "context": {},
                    "parameters": {"max_length": 100}
                }
            )
            requests.append(request)
        
        # Process requests with rate limiting
        successful = 0
        rate_limited = 0
        
        for request in requests:
            try:
                if await limiter.acquire_for_request(request):
                    successful += 1
                else:
                    rate_limited += 1
            except RateLimitExceeded:
                rate_limited += 1
        
        assert successful == 5
        assert rate_limited == 5
    
    @pytest.mark.asyncio
    async def test_token_based_limiting(self):
        """Test token-based rate limiting."""
        config = RateLimitConfig(
            requests_per_minute=100,  # High request limit
            tokens_per_minute=500    # Low token limit
        )
        
        limiter = TokenBucketRateLimiter(config)
        
        # Create a request that uses many tokens
        big_request = LLMRequest(
            request_id="big-request",
            agent_type="generation",
            request_type="generate",
            content={
                "prompt": "x" * 1000,  # Long prompt
                "context": {},
                "parameters": {"max_length": 1000}
            }
        )
        
        # Should consume significant tokens
        assert await limiter.acquire_for_request(big_request, estimated_tokens=400)
        
        # Next big request should be limited
        assert not await limiter.acquire_for_request(big_request, estimated_tokens=400)
    
    @pytest.mark.asyncio
    async def test_multi_model_rate_limits(self):
        """Test different rate limits for different models."""
        # GPT-4 limits (stricter)
        gpt4_config = RateLimitConfig(
            requests_per_minute=20,
            tokens_per_minute=10000
        )
        
        # GPT-3.5 limits (more generous)
        gpt35_config = RateLimitConfig(
            requests_per_minute=60,
            tokens_per_minute=90000
        )
        
        rate_limiters = {
            "gpt-4": TokenBucketRateLimiter(gpt4_config),
            "gpt-3.5-turbo": TokenBucketRateLimiter(gpt35_config)
        }
        
        # Test that each model has independent limits
        gpt4_count = 0
        gpt35_count = 0
        
        # Make many requests
        for i in range(100):
            request = LLMRequest(
                request_id=f"test-{i}",
                agent_type="generation",
                request_type="generate",
                content={
                    "prompt": "Test",
                    "context": {},
                    "parameters": {}
                }
            )
            
            if i % 2 == 0:
                if await rate_limiters["gpt-4"].acquire():
                    gpt4_count += 1
            else:
                if await rate_limiters["gpt-3.5-turbo"].acquire():
                    gpt35_count += 1
        
        # GPT-4 should hit its lower limit
        assert gpt4_count <= 20
        # GPT-3.5 should allow more
        assert gpt35_count > 20