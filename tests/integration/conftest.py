"""Shared fixtures for integration tests."""

import asyncio
import tempfile
from pathlib import Path
from typing import Generator

import pytest
import pytest_asyncio

from src.core.task_queue import TaskQueue, QueueConfig


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest_asyncio.fixture
async def task_queue() -> TaskQueue:
    """Create a TaskQueue instance for testing."""
    config = QueueConfig(
        max_queue_size=1000,
        priority_quotas={"high": 200, "medium": 500, "low": 300},
        worker_timeout=60,
        heartbeat_interval=5,
    )
    queue = TaskQueue(config=config)
    yield queue
    # Cleanup any remaining state
    if hasattr(queue, '_persistence_path') and queue._persistence_path:
        try:
            queue._persistence_path.unlink(missing_ok=True)
        except Exception:
            pass


@pytest.fixture
def integration_test_timeout() -> int:
    """Default timeout for integration tests."""
    return 30  # seconds


@pytest.mark.asyncio
class IntegrationTestBase:
    """Base class for integration tests with common utilities."""
    
    async def wait_for_condition(
        self, 
        condition_func, 
        timeout: float = 5.0, 
        interval: float = 0.1
    ) -> bool:
        """Wait for a condition to become true."""
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < timeout:
            if await condition_func():
                return True
            await asyncio.sleep(interval)
        return False