"""Tests for worker heartbeat tracking in TaskQueue."""

import asyncio
from datetime import datetime, timedelta
import pytest
from unittest.mock import AsyncMock, patch

from src.core.task_queue import TaskQueue, QueueConfig, WorkerInfo


@pytest.fixture
def queue_config():
    """Create a test queue configuration."""
    return QueueConfig(
        max_queue_size=10000,
        worker_timeout=300,
        heartbeat_interval=30,
        heartbeat_timeout=60,  # Worker considered dead after 60s without heartbeat
        heartbeat_check_interval=15
    )


@pytest.fixture
async def task_queue(queue_config):
    """Create a task queue instance."""
    return TaskQueue(config=queue_config)


class TestWorkerHeartbeat:
    """Test suite for worker heartbeat functionality."""
    
    async def test_heartbeat_updates_last_heartbeat(self, task_queue):
        """Test that heartbeat updates the worker's last heartbeat timestamp."""
        # Register a worker
        worker_id = "worker1"
        await task_queue.register_worker(worker_id, {"agent_types": ["Generation"]})
        
        # Get initial heartbeat time
        initial_status = await task_queue.get_worker_status(worker_id)
        initial_heartbeat = initial_status["last_heartbeat"]
        
        # Wait a moment
        await asyncio.sleep(0.1)
        
        # Send heartbeat
        success = await task_queue.heartbeat(worker_id)
        assert success is True
        
        # Check heartbeat was updated
        updated_status = await task_queue.get_worker_status(worker_id)
        assert updated_status["last_heartbeat"] > initial_heartbeat
    
    async def test_heartbeat_fails_for_unregistered_worker(self, task_queue):
        """Test that heartbeat fails for unregistered workers."""
        success = await task_queue.heartbeat("unknown_worker")
        assert success is False
    
    async def test_heartbeat_with_task_progress(self, task_queue):
        """Test heartbeat can include task progress updates."""
        # Register worker and give it a task
        worker_id = "worker1"
        await task_queue.register_worker(worker_id, {"agent_types": ["Generation"]})
        
        # Create and enqueue a task
        from src.core.models import Task, TaskType
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=2,
            payload={"goal": "test"}
        )
        task_id = await task_queue.enqueue(task)
        
        # Worker gets the task
        assignment = await task_queue.dequeue(worker_id)
        assert assignment is not None
        
        # Send heartbeat with progress
        progress_data = {
            "percentage": 50,
            "status": "Processing literature review"
        }
        success = await task_queue.heartbeat(worker_id, progress=progress_data)
        assert success is True
        
        # Verify progress is tracked
        task_info = await task_queue.get_task_info(str(task.id))
        assert task_info["progress"] == progress_data
    
    async def test_detect_dead_workers(self, task_queue):
        """Test detection of workers that haven't sent heartbeats."""
        # Register two workers
        worker1_id = "worker1"
        worker2_id = "worker2"
        await task_queue.register_worker(worker1_id, {"agent_types": ["Generation"]})
        await task_queue.register_worker(worker2_id, {"agent_types": ["Reflection"]})
        
        # Manually set worker1's last heartbeat to be old
        async with task_queue._lock:
            old_time = datetime.utcnow() - timedelta(seconds=90)
            task_queue._worker_info[worker1_id].last_heartbeat = old_time
        
        # Check for dead workers
        dead_workers = await task_queue.check_dead_workers()
        
        assert len(dead_workers) == 1
        assert worker1_id in dead_workers
        assert worker2_id not in dead_workers
    
    async def test_dead_worker_task_reassignment(self, task_queue):
        """Test that tasks from dead workers are reassigned."""
        # Register worker
        worker_id = "worker1"
        await task_queue.register_worker(worker_id, {"agent_types": ["Generation"]})
        
        # Create and assign task
        from src.core.models import Task, TaskType
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=2,
            payload={"goal": "test"}
        )
        await task_queue.enqueue(task)
        
        # Worker gets the task
        assignment = await task_queue.dequeue(worker_id)
        assert assignment is not None
        await task_queue.acknowledge_task(worker_id, assignment.assignment_id)
        
        # Manually mark worker as dead
        async with task_queue._lock:
            old_time = datetime.utcnow() - timedelta(seconds=90)
            task_queue._worker_info[worker_id].last_heartbeat = old_time
        
        # Process dead workers
        await task_queue.process_dead_workers()
        
        # Verify worker is marked as failed
        status = await task_queue.get_worker_status(worker_id)
        assert status["state"] == "failed"
        
        # Verify task is back in queue
        assert task_queue.size() == 1
        task_state = task_queue.get_task_state(str(task.id))
        assert task_state.value == "pending"
    
    async def test_heartbeat_monitoring_task(self, task_queue):
        """Test the heartbeat monitoring background task."""
        # Register a worker
        worker_id = "worker1"
        await task_queue.register_worker(worker_id, {"agent_types": ["Generation"]})
        
        # Start heartbeat monitoring
        monitor_task = asyncio.create_task(task_queue.monitor_heartbeats())
        
        # Let it run for a bit
        await asyncio.sleep(0.1)
        
        # Manually set worker's heartbeat to be old
        async with task_queue._lock:
            old_time = datetime.utcnow() - timedelta(seconds=90)
            task_queue._worker_info[worker_id].last_heartbeat = old_time
        
        # Wait for next monitoring cycle
        await asyncio.sleep(task_queue.config.heartbeat_check_interval + 0.1)
        
        # Check worker was marked as failed
        status = await task_queue.get_worker_status(worker_id)
        assert status["state"] == "failed"
        
        # Stop monitoring
        task_queue.stop_monitoring()
        await monitor_task
    
    async def test_worker_recovery_after_heartbeat(self, task_queue):
        """Test that a failed worker can recover by sending heartbeats."""
        # Register and mark worker as failed
        worker_id = "worker1"
        await task_queue.register_worker(worker_id, {"agent_types": ["Generation"]})
        
        async with task_queue._lock:
            task_queue._worker_info[worker_id].state = "failed"
        
        # Send heartbeat to recover
        success = await task_queue.heartbeat(worker_id)
        assert success is True
        
        # Check worker is back to idle
        status = await task_queue.get_worker_status(worker_id)
        assert status["state"] == "idle"
    
    async def test_heartbeat_metrics(self, task_queue):
        """Test heartbeat-related metrics collection."""
        # Register workers
        worker1_id = "worker1"
        worker2_id = "worker2"
        await task_queue.register_worker(worker1_id, {"agent_types": ["Generation"]})
        await task_queue.register_worker(worker2_id, {"agent_types": ["Reflection"]})
        
        # Set one worker as dead
        async with task_queue._lock:
            old_time = datetime.utcnow() - timedelta(seconds=90)
            task_queue._worker_info[worker1_id].last_heartbeat = old_time
            task_queue._worker_info[worker1_id].state = "failed"
        
        # Get heartbeat metrics
        metrics = await task_queue.get_heartbeat_metrics()
        
        assert metrics["total_workers"] == 2
        assert metrics["healthy_workers"] == 1
        assert metrics["failed_workers"] == 1
        assert metrics["average_heartbeat_age"] > 0
    
    async def test_configurable_heartbeat_timeout(self):
        """Test that heartbeat timeout is configurable."""
        # Create queue with custom timeout
        config = QueueConfig(heartbeat_timeout=10)  # 10 second timeout
        queue = TaskQueue(config=config)
        
        # Register worker
        worker_id = "worker1"
        await queue.register_worker(worker_id, {"agent_types": ["Generation"]})
        
        # Set heartbeat to 15 seconds ago
        async with queue._lock:
            old_time = datetime.utcnow() - timedelta(seconds=15)
            queue._worker_info[worker_id].last_heartbeat = old_time
        
        # Check for dead workers
        dead_workers = await queue.check_dead_workers()
        assert worker_id in dead_workers
    
    async def test_concurrent_heartbeats(self, task_queue):
        """Test that multiple workers can send heartbeats concurrently."""
        # Register multiple workers
        worker_ids = [f"worker{i}" for i in range(10)]
        for worker_id in worker_ids:
            await task_queue.register_worker(worker_id, {"agent_types": ["Generation"]})
        
        # Send heartbeats concurrently
        tasks = [task_queue.heartbeat(worker_id) for worker_id in worker_ids]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(results)
        
        # All should have recent heartbeats
        for worker_id in worker_ids:
            status = await task_queue.get_worker_status(worker_id)
            age = (datetime.utcnow() - status["last_heartbeat"]).total_seconds()
            assert age < 1.0  # Less than 1 second old