"""Test queue statistics methods in TaskQueue."""

import asyncio
from datetime import datetime, timedelta
import pytest

from src.core.models import Task, TaskState, TaskType
from src.core.task_queue import TaskQueue, QueueConfig


@pytest.fixture
async def queue():
    """Create a test queue."""
    queue = TaskQueue()
    yield queue
    # Cleanup
    queue.stop_monitoring()


@pytest.fixture
def tasks():
    """Create a set of test tasks with different priorities."""
    return [
        Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=3, payload={"id": 1}),  # High
        Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=3, payload={"id": 2}),  # High
        Task(task_type=TaskType.REFLECT_ON_HYPOTHESIS, priority=2, payload={"id": 3}),  # Medium
        Task(task_type=TaskType.REFLECT_ON_HYPOTHESIS, priority=2, payload={"id": 4}),  # Medium
        Task(task_type=TaskType.REFLECT_ON_HYPOTHESIS, priority=2, payload={"id": 5}),  # Medium
        Task(task_type=TaskType.EVOLVE_HYPOTHESIS, priority=1, payload={"id": 6}),  # Low
    ]


class TestQueueStatistics:
    """Test queue statistics and metrics functionality."""
    
    async def test_get_queue_depth(self, queue, tasks):
        """Test getting overall and per-priority queue depth."""
        # Initially empty
        stats = await queue.get_queue_statistics()
        assert stats["total_tasks"] == 0
        assert stats["depth_by_priority"]["high"] == 0
        assert stats["depth_by_priority"]["medium"] == 0
        assert stats["depth_by_priority"]["low"] == 0
        
        # Add tasks
        for task in tasks:
            await queue.enqueue(task)
        
        # Check statistics
        stats = await queue.get_queue_statistics()
        assert stats["total_tasks"] == 6
        assert stats["depth_by_priority"]["high"] == 2
        assert stats["depth_by_priority"]["medium"] == 3
        assert stats["depth_by_priority"]["low"] == 1
    
    async def test_worker_statistics(self, queue):
        """Test worker-related statistics."""
        # Register workers
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        await queue.register_worker("worker2", {"agent_types": ["Reflection"]})
        await queue.register_worker("worker3", {"agent_types": ["Evolution"]})
        
        # Get initial stats
        stats = await queue.get_queue_statistics()
        assert stats["worker_stats"]["total"] == 3
        assert stats["worker_stats"]["idle"] == 3
        assert stats["worker_stats"]["active"] == 0
        assert stats["worker_stats"]["failed"] == 0
        
        # Assign task to worker1
        task = Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=2, payload={})
        await queue.enqueue(task)
        assignment = await queue.dequeue("worker1")
        
        # Check updated stats
        stats = await queue.get_queue_statistics()
        assert stats["worker_stats"]["idle"] == 2
        assert stats["worker_stats"]["active"] == 1
        
        # Mark worker2 as failed
        queue._worker_info["worker2"].state = "failed"
        
        # Check failed worker in stats
        stats = await queue.get_queue_statistics()
        assert stats["worker_stats"]["failed"] == 1
    
    async def test_task_state_statistics(self, queue, tasks):
        """Test statistics on task states."""
        # Register workers
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        await queue.register_worker("worker2", {"agent_types": ["Reflection"]})
        
        # Add tasks
        task_ids = []
        for task in tasks[:4]:
            task_id = await queue.enqueue(task)
            task_ids.append(task_id)
        
        # Get initial stats
        stats = await queue.get_queue_statistics()
        assert stats["task_states"]["pending"] == 4
        assert stats["task_states"]["assigned"] == 0
        assert stats["task_states"]["executing"] == 0
        assert stats["task_states"]["completed"] == 0
        assert stats["task_states"]["failed"] == 0
        
        # Assign and execute some tasks
        assignment1 = await queue.dequeue("worker1")
        await queue.acknowledge_task("worker1", assignment1.assignment_id)
        
        assignment2 = await queue.dequeue("worker2")
        
        # Update stats
        stats = await queue.get_queue_statistics()
        assert stats["task_states"]["pending"] == 2
        assert stats["task_states"]["assigned"] == 1
        assert stats["task_states"]["executing"] == 1
        
        # Complete one task
        await queue.complete_task("worker1", task_ids[0], {"result": "done"})
        
        # Fail another task
        await queue.fail_task("worker2", task_ids[1], {"error": "test", "retryable": False})
        
        # Final stats check
        stats = await queue.get_queue_statistics()
        assert stats["task_states"]["completed"] == 1
        assert stats["task_states"]["failed"] == 1
    
    async def test_throughput_calculation(self, queue):
        """Test task throughput calculation."""
        # Register worker
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        
        # Process several tasks quickly
        start_time = datetime.utcnow()
        completed_count = 5
        
        for i in range(completed_count):
            task = Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=2, payload={"id": i})
            task_id = await queue.enqueue(task)
            assignment = await queue.dequeue("worker1")
            await queue.acknowledge_task("worker1", assignment.assignment_id)
            await queue.complete_task("worker1", task_id, {"result": f"done{i}"})
        
        # Get throughput stats
        stats = await queue.get_throughput_metrics()
        
        # Should have completed tasks
        assert stats["completed_last_minute"] == completed_count
        assert stats["completed_last_hour"] == completed_count
        assert stats["throughput_per_minute"] > 0
    
    async def test_average_wait_time(self, queue):
        """Test calculation of average task wait times."""
        # Register worker
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        
        # Add tasks with known timing
        task_ids = []
        for i in range(3):
            task = Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=2, payload={"id": i})
            task_id = await queue.enqueue(task)
            task_ids.append((task_id, datetime.utcnow()))
            await asyncio.sleep(0.1)  # Small delay between tasks
        
        # Dequeue tasks after waiting
        await asyncio.sleep(0.2)
        
        wait_times = []
        for task_id, enqueue_time in task_ids:
            assignment = await queue.dequeue("worker1")
            dequeue_time = datetime.utcnow()
            wait_time = (dequeue_time - enqueue_time).total_seconds()
            wait_times.append(wait_time)
            await queue.complete_task("worker1", task_id, {})
        
        # Get wait time stats
        stats = await queue.get_wait_time_statistics()
        
        # Average wait time should be positive
        assert stats["average_wait_time"]["overall"] > 0
        assert stats["average_wait_time"]["by_priority"]["medium"] > 0
    
    async def test_retry_statistics(self, queue):
        """Test statistics on task retries."""
        # Register worker
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        
        # Create task and fail it multiple times
        task = Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=2, payload={})
        task_id = await queue.enqueue(task)
        
        # Fail twice (with retries)
        for i in range(2):
            assignment = await queue.dequeue("worker1")
            await queue.acknowledge_task("worker1", assignment.assignment_id)
            await queue.fail_task("worker1", task_id, {"error": f"attempt{i}", "retryable": True})
        
        # Get retry stats
        stats = await queue.get_retry_statistics()
        
        assert stats["total_retries"] == 2
        assert stats["tasks_with_retries"] == 1
        assert stats["max_retry_count"] == 2
        assert stats["retry_by_task_type"][TaskType.GENERATE_HYPOTHESIS.value] == 2
    
    async def test_queue_capacity_statistics(self, queue, tasks):
        """Test queue capacity and warning statistics."""
        # Create queue with small capacity
        small_queue = TaskQueue(QueueConfig(
            max_queue_size=10,
            priority_quotas={"high": 3, "medium": 4, "low": 3}
        ))
        
        # Add tasks to approach capacity
        for task in tasks:
            await small_queue.enqueue(task)
        
        # Get capacity stats
        stats = await small_queue.get_capacity_statistics()
        
        assert stats["max_capacity"] == 10
        assert stats["current_size"] == 6
        assert stats["utilization_percent"] == 60.0
        assert stats["capacity_by_priority"]["high"]["used"] == 2
        assert stats["capacity_by_priority"]["high"]["limit"] == 3
        assert stats["capacity_by_priority"]["medium"]["used"] == 3
        assert stats["capacity_by_priority"]["medium"]["limit"] == 4
        
        # Check warnings when approaching limits
        assert not stats["warnings"]["near_capacity"]
        
        # We have: 2 high (limit 3), 3 medium (limit 4), 1 low (limit 3)
        # Total: 6/10 = 60%
        # Add more to trigger warning at 80%
        
        # Add 1 more high priority task
        await small_queue.enqueue(Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=3, payload={"id": 10}))
        # Add 1 more low priority task  
        await small_queue.enqueue(Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=1, payload={"id": 11}))
        
        # Now we have 8/10 = 80%
        stats = await small_queue.get_capacity_statistics()
        assert stats["utilization_percent"] == 80.0
        assert stats["warnings"]["near_capacity"]  # Should warn at 80%+
    
    async def test_starvation_detection(self, queue):
        """Test detection of starved tasks."""
        # Configure queue with short starvation threshold
        config = QueueConfig(starvation_threshold=2)  # 2 seconds
        starve_queue = TaskQueue(config)
        
        # Add low priority task
        low_task = Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=1, payload={})
        low_task_id = await starve_queue.enqueue(low_task)
        
        # Wait for task to become starved
        await asyncio.sleep(2.5)
        
        # Get starvation stats
        stats = await starve_queue.get_starvation_statistics()
        
        assert stats["starved_tasks"] == 1
        assert stats["oldest_waiting_task"]["priority"] == "low"
        assert stats["oldest_waiting_task"]["wait_time"] > 2.0
        assert low_task_id in stats["starved_task_ids"]
    
    async def test_detailed_metrics(self, queue, tasks):
        """Test getting all detailed metrics at once."""
        # Register workers
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        await queue.register_worker("worker2", {"agent_types": ["Reflection"]})
        
        # Add and process some tasks
        for task in tasks[:3]:
            task_id = await queue.enqueue(task)
            if task.priority == 3:  # High priority
                assignment = await queue.dequeue("worker1")
                await queue.acknowledge_task("worker1", assignment.assignment_id)
                await queue.complete_task("worker1", task_id, {"result": "done"})
        
        # Get comprehensive metrics
        metrics = await queue.get_detailed_metrics()
        
        # Verify structure
        assert "queue_statistics" in metrics
        assert "throughput_metrics" in metrics
        assert "wait_time_statistics" in metrics
        assert "retry_statistics" in metrics
        assert "capacity_statistics" in metrics
        assert "heartbeat_metrics" in metrics
        assert "timestamp" in metrics
        
        # Verify some values
        assert metrics["queue_statistics"]["total_tasks"] > 0
        assert metrics["queue_statistics"]["worker_stats"]["total"] == 2
        assert metrics["throughput_metrics"]["completed_last_minute"] == 2
    
    async def test_metrics_by_agent_type(self, queue):
        """Test metrics grouped by agent type."""
        # Register workers for different agent types
        await queue.register_worker("gen1", {"agent_types": ["Generation"]})
        await queue.register_worker("ref1", {"agent_types": ["Reflection"]})
        await queue.enable_capability_matching()
        
        # Create tasks for different agent types
        gen_tasks = [
            Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=2, payload={"id": i})
            for i in range(3)
        ]
        ref_tasks = [
            Task(task_type=TaskType.REFLECT_ON_HYPOTHESIS, priority=2, payload={"id": i})
            for i in range(2)
        ]
        
        # Enqueue all tasks
        for task in gen_tasks + ref_tasks:
            await queue.enqueue(task)
        
        # Get metrics by agent type
        stats = await queue.get_metrics_by_agent_type()
        
        assert stats["Generation"]["pending_tasks"] == 3
        assert stats["Generation"]["capable_workers"] == 1
        assert stats["Reflection"]["pending_tasks"] == 2
        assert stats["Reflection"]["capable_workers"] == 1