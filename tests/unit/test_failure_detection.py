"""Test failure detection and recovery in TaskQueue."""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import MagicMock
import pytest

from src.core.models import Task, TaskState, TaskType
from src.core.task_queue import TaskQueue, QueueConfig


@pytest.fixture
async def queue():
    """Create a queue with fast heartbeat timeout for testing."""
    config = QueueConfig(
        heartbeat_timeout=2,  # 2 seconds for faster testing
        heartbeat_check_interval=1,  # Check every second
        acknowledgment_timeout=1  # 1 second acknowledgment timeout
    )
    queue = TaskQueue(config)
    yield queue
    # Cleanup
    queue.stop_monitoring()


@pytest.fixture
async def task():
    """Create a test task."""
    return Task(
        task_type=TaskType.GENERATE_HYPOTHESIS,
        priority=2,
        data={"prompt": "Test hypothesis"}
    )


class TestFailureDetection:
    """Test failure detection mechanisms."""
    
    async def test_worker_timeout_detection(self, queue, task):
        """Test detection of timed out workers."""
        # Register worker
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        
        # Enqueue task
        await queue.enqueue(task)
        
        # Worker gets task
        assignment = await queue.dequeue("worker1")
        assert assignment is not None
        
        # Simulate worker timeout by setting old heartbeat directly
        old_time = datetime.utcnow() - timedelta(seconds=3)
        queue._worker_info["worker1"].last_heartbeat = old_time
        
        # Check for dead workers
        dead_workers = await queue.check_dead_workers()
        
        assert "worker1" in dead_workers
    
    async def test_acknowledgment_timeout(self, queue, task):
        """Test task reassignment when acknowledgment times out."""
        # Register workers
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        await queue.register_worker("worker2", {"agent_types": ["Generation"]})
        
        # Enqueue task
        task_id = await queue.enqueue(task)
        
        # Worker1 gets task but doesn't acknowledge
        assignment1 = await queue.dequeue("worker1")
        assert assignment1 is not None
        
        # Wait for acknowledgment timeout
        await asyncio.sleep(1.5)
        
        # Check assignment timeouts
        await queue.check_assignment_timeouts()
        
        # Task should be back in pending state
        assert queue.get_task_state(task_id) == TaskState.PENDING
        
        # Worker2 should be able to get the task
        assignment2 = await queue.dequeue("worker2")
        assert assignment2 is not None
        assert assignment2.task.id == task.id
    
    async def test_worker_failure_task_reassignment(self, queue, task):
        """Test task reassignment when worker fails."""
        # Register workers
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        await queue.register_worker("worker2", {"agent_types": ["Generation"]})
        
        # Enqueue task
        task_id = await queue.enqueue(task)
        
        # Worker1 gets and acknowledges task
        assignment1 = await queue.dequeue("worker1")
        await queue.acknowledge_task("worker1", assignment1.assignment_id)
        
        # Simulate worker failure
        queue._worker_info["worker1"].last_heartbeat = datetime.utcnow() - timedelta(seconds=3)
        
        # Process dead workers
        await queue.process_dead_workers()
        
        # Check worker marked as failed
        assert queue._worker_info["worker1"].state == "failed"
        
        # Task should be back in queue
        assert queue.get_task_state(task_id) == TaskState.PENDING
        
        # Worker2 should be able to get the task
        assignment2 = await queue.dequeue("worker2")
        assert assignment2 is not None
        assert assignment2.task.id == task.id
    
    async def test_multiple_worker_failures(self, queue):
        """Test handling multiple worker failures simultaneously."""
        # Register multiple workers
        for i in range(5):
            await queue.register_worker(f"worker{i}", {"agent_types": ["Generation"]})
        
        # Create and assign tasks
        tasks = []
        for i in range(5):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=2,
                data={"prompt": f"Test {i}"}
            )
            tasks.append(task)
            await queue.enqueue(task)
            
            assignment = await queue.dequeue(f"worker{i}")
            await queue.acknowledge_task(f"worker{i}", assignment.assignment_id)
        
        # Simulate failure of workers 1, 2, and 3
        failed_workers = ["worker1", "worker2", "worker3"]
        for worker_id in failed_workers:
            queue._worker_info[worker_id].last_heartbeat = datetime.utcnow() - timedelta(seconds=3)
        
        # Process dead workers
        await queue.process_dead_workers()
        
        # Check failed workers marked correctly
        for worker_id in failed_workers:
            assert queue._worker_info[worker_id].state == "failed"
        
        # Check healthy workers still active
        for i in [0, 4]:
            assert queue._worker_info[f"worker{i}"].state == "active"
        
        # Check tasks reassigned to pending
        pending_count = sum(1 for task in tasks[1:4] 
                          if queue.get_task_state(str(task.id)) == TaskState.PENDING)
        assert pending_count == 3
    
    async def test_worker_recovery_after_failure(self, queue, task):
        """Test worker recovery after being marked as failed."""
        # Register worker
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        
        # Mark worker as failed
        queue._worker_info["worker1"].state = "failed"
        
        # Worker sends heartbeat
        success = await queue.heartbeat("worker1")
        assert success
        
        # Worker should be recovered
        assert queue._worker_info["worker1"].state == "idle"
        
        # Worker should be able to get tasks again
        await queue.enqueue(task)
        assignment = await queue.dequeue("worker1")
        assert assignment is not None
    
    async def test_task_retry_after_failure(self, queue, task):
        """Test task retry logic after failure."""
        # Register worker
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        
        # Enqueue task
        task_id = await queue.enqueue(task)
        
        # Worker gets task
        assignment = await queue.dequeue("worker1")
        await queue.acknowledge_task("worker1", assignment.assignment_id)
        
        # Worker reports failure (retryable)
        error = {
            "message": "Temporary network error",
            "retryable": True
        }
        success = await queue.fail_task("worker1", task_id, error)
        assert success
        
        # Task should be back in pending
        assert queue.get_task_state(task_id) == TaskState.PENDING
        
        # Retry count should be incremented
        assert queue._task_retry_counts[task_id] == 1
        
        # Worker should be able to get task again
        assignment2 = await queue.dequeue("worker1")
        assert assignment2 is not None
        assert str(assignment2.task.id) == task_id
    
    async def test_max_retries_enforcement(self, queue, task):
        """Test that tasks fail permanently after max retries."""
        # Register worker
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        
        # Enqueue task
        task_id = await queue.enqueue(task)
        
        # Fail task max_attempts times
        max_attempts = queue.config.retry_policy["max_attempts"]
        
        for attempt in range(max_attempts + 1):
            assignment = await queue.dequeue("worker1")
            if assignment:
                await queue.acknowledge_task("worker1", assignment.assignment_id)
                
                error = {"message": f"Attempt {attempt}", "retryable": True}
                await queue.fail_task("worker1", task_id, error)
        
        # Task should be permanently failed
        assert queue.get_task_state(task_id) == TaskState.FAILED
        
        # Task should not be available for dequeue
        assignment = await queue.dequeue("worker1")
        assert assignment is None
    
    async def test_non_retryable_failure(self, queue, task):
        """Test that non-retryable failures don't retry."""
        # Register worker
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        
        # Enqueue task
        task_id = await queue.enqueue(task)
        
        # Worker gets task
        assignment = await queue.dequeue("worker1")
        await queue.acknowledge_task("worker1", assignment.assignment_id)
        
        # Worker reports non-retryable failure
        error = {
            "message": "Invalid task parameters",
            "retryable": False
        }
        success = await queue.fail_task("worker1", task_id, error)
        assert success
        
        # Task should be permanently failed
        assert queue.get_task_state(task_id) == TaskState.FAILED
        
        # Task should not be available for dequeue
        assignment2 = await queue.dequeue("worker1")
        assert assignment2 is None
    
    async def test_failure_history_tracking(self, queue, task):
        """Test that failure history is properly tracked."""
        # Register workers
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        await queue.register_worker("worker2", {"agent_types": ["Generation"]})
        
        # Enqueue task
        task_id = await queue.enqueue(task)
        
        # First failure
        assignment1 = await queue.dequeue("worker1")
        await queue.acknowledge_task("worker1", assignment1.assignment_id)
        error1 = {"message": "Network timeout", "retryable": True}
        await queue.fail_task("worker1", task_id, error1)
        
        # Second failure
        assignment2 = await queue.dequeue("worker2")
        await queue.acknowledge_task("worker2", assignment2.assignment_id)
        error2 = {"message": "API rate limit", "retryable": True}
        await queue.fail_task("worker2", task_id, error2)
        
        # Check failure history
        task_info = await queue.get_task_info(task_id)
        assert len(task_info["failure_history"]) == 2
        assert task_info["failure_history"][0]["worker_id"] == "worker1"
        assert task_info["failure_history"][0]["error"]["message"] == "Network timeout"
        assert task_info["failure_history"][1]["worker_id"] == "worker2"
        assert task_info["failure_history"][1]["error"]["message"] == "API rate limit"
    
    async def test_concurrent_failure_handling(self, queue):
        """Test handling failures from multiple workers concurrently."""
        # Register workers
        workers = []
        for i in range(10):
            worker_id = f"worker{i}"
            await queue.register_worker(worker_id, {"agent_types": ["Generation"]})
            workers.append(worker_id)
        
        # Create and assign tasks
        tasks = []
        for i in range(10):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=2,
                data={"prompt": f"Test {i}"}
            )
            task_id = await queue.enqueue(task)
            tasks.append(task_id)
            
            assignment = await queue.dequeue(workers[i])
            await queue.acknowledge_task(workers[i], assignment.assignment_id)
        
        # Concurrently fail all tasks
        async def fail_task(worker_id, task_id):
            error = {"message": f"Error from {worker_id}", "retryable": True}
            await queue.fail_task(worker_id, task_id, error)
        
        # Run failures concurrently
        await asyncio.gather(
            *[fail_task(workers[i], tasks[i]) for i in range(10)]
        )
        
        # All tasks should be back in pending
        for task_id in tasks:
            assert queue.get_task_state(task_id) == TaskState.PENDING
        
        # All workers should be idle
        for worker_id in workers:
            assert queue._worker_info[worker_id].state == "idle"
    
    async def test_heartbeat_monitoring_task(self, queue):
        """Test the background heartbeat monitoring task."""
        # Register worker
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        
        # Create and assign task
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=2,
            data={"prompt": "Test"}
        )
        task_id = await queue.enqueue(task)
        assignment = await queue.dequeue("worker1")
        await queue.acknowledge_task("worker1", assignment.assignment_id)
        
        # Start monitoring
        monitor_task = asyncio.create_task(queue.monitor_heartbeats())
        
        # Set worker heartbeat to expired
        queue._worker_info["worker1"].last_heartbeat = datetime.utcnow() - timedelta(seconds=3)
        
        # Wait for monitoring to process
        await asyncio.sleep(1.5)
        
        # Stop monitoring
        queue.stop_monitoring()
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        
        # Worker should be marked as failed
        assert queue._worker_info["worker1"].state == "failed"
        
        # Task should be back in pending
        assert queue.get_task_state(task_id) == TaskState.PENDING