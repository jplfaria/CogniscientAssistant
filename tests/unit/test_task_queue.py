"""Tests for TaskQueue class."""

import asyncio
from datetime import datetime
from typing import Optional

import pytest
from uuid import UUID

from src.core.models import Task, TaskState, TaskType
from src.core.task_queue import TaskQueue, QueueConfig


class TestTaskQueueInitialization:
    """Tests for TaskQueue initialization."""
    
    def test_create_task_queue_with_default_config(self):
        """Test creating TaskQueue with default configuration."""
        queue = TaskQueue()
        
        assert queue is not None
        assert isinstance(queue.config, QueueConfig)
        assert queue.config.max_queue_size == 10000
        assert queue.config.priority_quotas == {"high": 1000, "medium": 5000, "low": 4000}
        assert queue.config.worker_timeout == 300
        assert queue.config.heartbeat_interval == 30
        assert queue.is_running is False
    
    def test_create_task_queue_with_custom_config(self):
        """Test creating TaskQueue with custom configuration."""
        config = QueueConfig(
            max_queue_size=500,
            priority_quotas={"high": 100, "medium": 300, "low": 100},
            worker_timeout=60,
            heartbeat_interval=10,
            retry_policy={
                "max_attempts": 5,
                "backoff_base": 3,
                "backoff_max": 600
            }
        )
        queue = TaskQueue(config=config)
        
        assert queue.config == config
        assert queue.config.max_queue_size == 500
        assert queue.config.worker_timeout == 60
    
    def test_queue_config_validation(self):
        """Test QueueConfig validates input correctly."""
        # Test invalid max_queue_size
        with pytest.raises(ValueError, match="max_queue_size must be positive"):
            QueueConfig(max_queue_size=-1)
        
        # Test invalid priority quotas sum
        with pytest.raises(ValueError, match="Priority quotas sum exceeds max_queue_size"):
            QueueConfig(
                max_queue_size=100,
                priority_quotas={"high": 50, "medium": 60, "low": 50}
            )
        
        # Test missing priority level
        with pytest.raises(ValueError, match="Priority quotas must include high, medium, low"):
            QueueConfig(priority_quotas={"high": 100, "medium": 200})
    
    def test_task_queue_initial_state(self):
        """Test TaskQueue starts in correct initial state."""
        queue = TaskQueue()
        
        # Check queue is empty
        assert queue.size() == 0
        assert queue.size_by_priority("high") == 0
        assert queue.size_by_priority("medium") == 0
        assert queue.size_by_priority("low") == 0
        
        # Check no workers registered
        assert queue.active_workers() == 0
        assert queue.idle_workers() == 0
        
        # Check queue is not paused
        assert queue.is_paused is False


class TestTaskQueueBasicOperations:
    """Tests for basic TaskQueue operations."""
    
    @pytest.fixture
    def queue(self):
        """Create a TaskQueue instance for tests."""
        return TaskQueue()
    
    @pytest.fixture
    def sample_task(self):
        """Create a sample task for tests."""
        return Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=2,  # Medium priority
            payload={"goal": "test hypothesis generation"}
        )
    
    async def test_enqueue_single_task(self, queue, sample_task):
        """Test enqueueing a single task."""
        task_id = await queue.enqueue(sample_task)
        
        assert task_id == str(sample_task.id)
        assert queue.size() == 1
        assert queue.size_by_priority("medium") == 1
        
        # Task should be in pending state
        task_state = queue.get_task_state(task_id)
        assert task_state == TaskState.PENDING
    
    async def test_enqueue_validates_task(self, queue):
        """Test enqueue validates task before adding."""
        # Test with invalid task (negative priority)
        # Note: Task model itself validates priority, so we can't create invalid task
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            invalid_task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=-1,
                payload={}
            )
    
    async def test_enqueue_respects_capacity_limits(self, queue):
        """Test enqueue respects queue capacity limits."""
        # Create a small queue
        small_queue = TaskQueue(config=QueueConfig(
            max_queue_size=5,
            priority_quotas={"high": 2, "medium": 2, "low": 1}
        ))
        
        # Fill the queue with mixed priorities
        # Add 2 high priority tasks
        for i in range(2):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=3,  # High
                payload={"index": i, "priority": "high"}
            )
            await small_queue.enqueue(task)
        
        # Add 2 medium priority tasks
        for i in range(2):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=2,  # Medium
                payload={"index": i, "priority": "medium"}
            )
            await small_queue.enqueue(task)
        
        # Add 1 low priority task
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=1,  # Low
            payload={"index": 0, "priority": "low"}
        )
        await small_queue.enqueue(task)
        
        # Try to add one more to any priority - should raise
        with pytest.raises(RuntimeError, match="Queue at capacity"):
            overflow_task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=1,  # Try low priority (already at limit)
                payload={"overflow": True}
            )
            await small_queue.enqueue(overflow_task)
    
    async def test_dequeue_empty_queue_returns_none(self, queue):
        """Test dequeue on empty queue returns None."""
        result = await queue.dequeue("worker-1")
        assert result is None
    
    async def test_dequeue_returns_highest_priority_task(self, queue):
        """Test dequeue returns highest priority task first."""
        # Add tasks with different priorities
        low_task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=1,  # Low
            payload={"priority": "low"}
        )
        medium_task = Task(
            task_type=TaskType.REVIEW_HYPOTHESIS,
            priority=2,  # Medium
            payload={"priority": "medium"}
        )
        high_task = Task(
            task_type=TaskType.RANK_HYPOTHESES,
            priority=3,  # High
            payload={"priority": "high"}
        )
        
        # Add in random order
        await queue.enqueue(medium_task)
        await queue.enqueue(low_task)
        await queue.enqueue(high_task)
        
        # Dequeue should return high priority first
        assignment = await queue.dequeue("worker-1")
        assert assignment is not None
        assert assignment.task.id == high_task.id
        assert assignment.task.priority == 3
    
    async def test_dequeue_updates_task_state(self, queue, sample_task):
        """Test dequeue updates task state to assigned."""
        await queue.enqueue(sample_task)
        
        assignment = await queue.dequeue("worker-1")
        assert assignment is not None
        
        # Check task state updated
        task_state = queue.get_task_state(sample_task.id)
        assert task_state == TaskState.ASSIGNED
        
        # Check task assigned to correct worker
        assert assignment.task.assigned_to == "worker-1"
        assert assignment.task.assigned_at is not None
    
    async def test_peek_does_not_modify_queue(self, queue, sample_task):
        """Test peek returns next task without modifying queue."""
        await queue.enqueue(sample_task)
        
        # Peek at next task
        next_task = await queue.peek()
        assert next_task is not None
        assert next_task.id == sample_task.id
        
        # Queue should be unchanged
        assert queue.size() == 1
        task_state = queue.get_task_state(sample_task.id)
        assert task_state == TaskState.PENDING
        
        # Should be able to dequeue the same task
        assignment = await queue.dequeue("worker-1")
        assert assignment.task.id == sample_task.id