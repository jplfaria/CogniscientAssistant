"""Rate limiting for LLM requests."""

import asyncio
import time
from abc import ABC, abstractmethod
from collections import deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Deque

from .base import LLMRequest


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    pass


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_minute: int = 60
    requests_per_hour: Optional[int] = None
    tokens_per_minute: Optional[int] = None
    tokens_per_hour: Optional[int] = None
    concurrent_requests: int = 10
    burst_size: Optional[int] = None
    window_size_seconds: int = 60
    
    def __post_init__(self):
        """Validate configuration."""
        if self.requests_per_minute < 0:
            raise ValueError("requests_per_minute must be non-negative")
        
        if self.concurrent_requests <= 0:
            raise ValueError("concurrent_requests must be positive")
        
        if self.requests_per_hour is not None and self.requests_per_hour < 0:
            raise ValueError("requests_per_hour must be non-negative")
        
        if self.tokens_per_minute is not None and self.tokens_per_minute < 0:
            raise ValueError("tokens_per_minute must be non-negative")


class RateLimiter(ABC):
    """Abstract base class for rate limiters."""
    
    @abstractmethod
    async def acquire(self, raise_on_limit: bool = False) -> bool:
        """Acquire permission to make a request.
        
        Args:
            raise_on_limit: If True, raise RateLimitExceeded instead of returning False
            
        Returns:
            True if request is allowed, False if rate limited
            
        Raises:
            RateLimitExceeded: If raise_on_limit is True and limit exceeded
        """
        pass
    
    @abstractmethod
    async def acquire_for_request(self, request: LLMRequest, estimated_tokens: Optional[int] = None) -> bool:
        """Acquire permission for a specific request.
        
        Args:
            request: The LLM request
            estimated_tokens: Estimated token count for the request
            
        Returns:
            True if request is allowed, False if rate limited
        """
        pass
    
    @abstractmethod
    @asynccontextmanager
    async def concurrent_request(self):
        """Context manager for tracking concurrent requests."""
        pass


class TokenBucketRateLimiter(RateLimiter):
    """Token bucket implementation of rate limiting."""
    
    def __init__(self, config: RateLimitConfig):
        """Initialize the token bucket rate limiter.
        
        Args:
            config: Rate limiting configuration
        """
        self.config = config
        
        # Request rate limiting
        self.request_bucket_size = config.burst_size or config.requests_per_minute
        self.request_tokens = float(self.request_bucket_size)
        self.request_refill_rate = config.requests_per_minute / 60.0  # per second
        self.last_request_refill = time.time()
        
        # Token rate limiting (if configured)
        if config.tokens_per_minute:
            self.token_bucket_size = config.tokens_per_minute
            self.token_tokens = float(self.token_bucket_size)
            self.token_refill_rate = config.tokens_per_minute / 60.0
            self.last_token_refill = time.time()
        
        # Concurrent request tracking
        self.concurrent_count = 0
        self.concurrent_lock = asyncio.Lock()
        
        # Thread safety
        self.request_lock = asyncio.Lock()
        self.token_lock = asyncio.Lock()
    
    async def acquire(self, raise_on_limit: bool = False) -> bool:
        """Acquire permission to make a request."""
        async with self.request_lock:
            # Refill bucket
            now = time.time()
            elapsed = now - self.last_request_refill
            self.request_tokens = min(
                self.request_bucket_size,
                self.request_tokens + (elapsed * self.request_refill_rate)
            )
            self.last_request_refill = now
            
            # Check if we can consume a token
            if self.request_tokens >= 1:
                self.request_tokens -= 1
                return True
            else:
                if raise_on_limit:
                    raise RateLimitExceeded("Request rate limit exceeded")
                return False
    
    async def acquire_for_request(self, request: LLMRequest, estimated_tokens: Optional[int] = None) -> bool:
        """Acquire permission for a specific request."""
        # Check request rate limit
        if not await self.acquire():
            return False
        
        # Check token rate limit if configured
        if self.config.tokens_per_minute and estimated_tokens:
            async with self.token_lock:
                # Refill token bucket
                now = time.time()
                elapsed = now - self.last_token_refill
                self.token_tokens = min(
                    self.token_bucket_size,
                    self.token_tokens + (elapsed * self.token_refill_rate)
                )
                self.last_token_refill = now
                
                # Check if we can consume tokens
                if self.token_tokens >= estimated_tokens:
                    self.token_tokens -= estimated_tokens
                    return True
                else:
                    # Rollback request token
                    async with self.request_lock:
                        self.request_tokens += 1
                    return False
        
        return True
    
    @asynccontextmanager
    async def concurrent_request(self):
        """Context manager for tracking concurrent requests."""
        async with self.concurrent_lock:
            if self.concurrent_count >= self.config.concurrent_requests:
                raise RateLimitExceeded("Concurrent request limit exceeded")
            self.concurrent_count += 1
        
        try:
            yield
        finally:
            async with self.concurrent_lock:
                self.concurrent_count -= 1


class SlidingWindowRateLimiter(RateLimiter):
    """Sliding window implementation of rate limiting."""
    
    def __init__(self, config: RateLimitConfig):
        """Initialize the sliding window rate limiter.
        
        Args:
            config: Rate limiting configuration
        """
        self.config = config
        
        # Request timestamps
        self.request_times: Deque[float] = deque()
        self.hour_request_times: Deque[float] = deque()
        
        # Token tracking
        if config.tokens_per_minute:
            self.token_usage: Deque[tuple[float, int]] = deque()
        
        # Concurrent request tracking
        self.concurrent_count = 0
        self.concurrent_lock = asyncio.Lock()
        
        # Thread safety
        self.request_lock = asyncio.Lock()
    
    def _clean_old_requests(self, window_seconds: int):
        """Remove requests older than the window."""
        cutoff = time.time() - window_seconds
        
        # Clean minute window
        while self.request_times and self.request_times[0] < cutoff:
            self.request_times.popleft()
        
        # Clean hour window if configured
        if self.config.requests_per_hour:
            hour_cutoff = time.time() - 3600
            while self.hour_request_times and self.hour_request_times[0] < hour_cutoff:
                self.hour_request_times.popleft()
    
    async def acquire(self, raise_on_limit: bool = False) -> bool:
        """Acquire permission to make a request."""
        async with self.request_lock:
            now = time.time()
            
            # Clean old requests
            self._clean_old_requests(self.config.window_size_seconds)
            
            # Check minute limit
            if len(self.request_times) >= self.config.requests_per_minute:
                if raise_on_limit:
                    raise RateLimitExceeded("Request rate limit exceeded")
                return False
            
            # Check hour limit if configured
            if self.config.requests_per_hour:
                if len(self.hour_request_times) >= self.config.requests_per_hour:
                    if raise_on_limit:
                        raise RateLimitExceeded("Hourly request limit exceeded")
                    return False
            
            # Record request
            self.request_times.append(now)
            if self.config.requests_per_hour:
                self.hour_request_times.append(now)
            
            return True
    
    async def acquire_for_request(self, request: LLMRequest, estimated_tokens: Optional[int] = None) -> bool:
        """Acquire permission for a specific request."""
        # For sliding window, we just use the basic acquire
        return await self.acquire()
    
    @asynccontextmanager
    async def concurrent_request(self):
        """Context manager for tracking concurrent requests."""
        async with self.concurrent_lock:
            if self.concurrent_count >= self.config.concurrent_requests:
                raise RateLimitExceeded("Concurrent request limit exceeded")
            self.concurrent_count += 1
        
        try:
            yield
        finally:
            async with self.concurrent_lock:
                self.concurrent_count -= 1