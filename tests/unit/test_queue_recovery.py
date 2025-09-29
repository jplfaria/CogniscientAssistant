"""Test queue recovery on startup functionality."""

import asyncio
import json
import os
from pathlib import Path
import tempfile
import pytest

from src.core.models import Task, TaskState, TaskType
from src.core.task_queue import TaskQueue, QueueConfig


@pytest.fixture
async def temp_dir():
    """Create a temporary directory for recovery tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestQueueRecovery:
    """Test queue recovery on startup functionality."""
    
    async def test_auto_recovery_on_init(self, temp_dir):
        """Test that queue automatically recovers state on initialization."""
        state_file = temp_dir / "recovery_test.json"
        
        # Create first queue and add tasks
        config1 = QueueConfig(
            persistence_path=str(state_file),
            auto_recovery=True
        )
        queue1 = TaskQueue(config1)
        
        # Add tasks
        task_ids = []
        for i in range(3):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=2,
                payload={"id": i}
            )
            task_id = await queue1.enqueue(task)
            task_ids.append(task_id)
        
        # Save state
        await queue1.save_state()
        
        # Create new queue with same config - should auto-recover
        config2 = QueueConfig(
            persistence_path=str(state_file),
            auto_recovery=True
        )
        queue2 = TaskQueue(config2)
        await queue2.initialize()  # Initialize and recover
        
        # Verify state was recovered
        assert queue2.size() == 3
        for task_id in task_ids:
            assert queue2.get_task_state(task_id) == TaskState.PENDING
    
    async def test_recovery_with_active_tasks(self, temp_dir):
        """Test recovery when there are active/assigned tasks."""
        state_file = temp_dir / "active_recovery.json"
        
        # Create first queue
        config = QueueConfig(
            persistence_path=str(state_file),
            auto_recovery=True
        )
        queue1 = TaskQueue(config)
        
        # Register worker and assign task
        await queue1.register_worker("worker1", {"agent_types": ["Generation"]})
        task = Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=2, payload={})
        task_id = await queue1.enqueue(task)
        
        assignment = await queue1.dequeue("worker1")
        await queue1.acknowledge_task("worker1", assignment.assignment_id)
        
        # Save state with active task
        await queue1.save_state()
        
        # Create new queue - should recover with task still assigned
        queue2 = TaskQueue(config)
        await queue2.initialize()
        
        # Verify task is still executing
        assert queue2.get_task_state(task_id) == TaskState.EXECUTING
        
        # Verify worker is registered and active
        assert queue2.is_worker_registered("worker1")
        worker_status = await queue2.get_worker_status("worker1")
        assert worker_status["state"] == "active"
        assert worker_status["assigned_task"] == task_id
    
    async def test_recovery_without_auto_recovery_flag(self, temp_dir):
        """Test that recovery doesn't happen if auto_recovery is False."""
        state_file = temp_dir / "no_auto_recovery.json"
        
        # Create first queue and add tasks
        config1 = QueueConfig(
            persistence_path=str(state_file),
            auto_recovery=False
        )
        queue1 = TaskQueue(config1)
        
        task = Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=2, payload={})
        await queue1.enqueue(task)
        await queue1.save_state()
        
        # Create new queue with auto_recovery=False
        config2 = QueueConfig(
            persistence_path=str(state_file),
            auto_recovery=False
        )
        queue2 = TaskQueue(config2)
        await queue2.initialize()
        
        # Should NOT have recovered
        assert queue2.size() == 0
    
    async def test_recovery_with_corrupted_file(self, temp_dir):
        """Test graceful handling of corrupted state file during recovery."""
        state_file = temp_dir / "corrupted.json"
        
        # Write corrupted state
        with open(state_file, 'w') as f:
            f.write("{ corrupted json")
        
        # Create queue with auto-recovery
        config = QueueConfig(
            persistence_path=str(state_file),
            auto_recovery=True
        )
        queue = TaskQueue(config)
        
        # Should handle corruption gracefully (log error, start empty)
        await queue.initialize()
        assert queue.size() == 0
    
    async def test_recovery_with_missing_file(self, temp_dir):
        """Test that missing state file is handled gracefully."""
        state_file = temp_dir / "nonexistent.json"
        
        config = QueueConfig(
            persistence_path=str(state_file),
            auto_recovery=True
        )
        queue = TaskQueue(config)
        
        # Should initialize empty queue without error
        await queue.initialize()
        assert queue.size() == 0
    
    async def test_recovery_preserves_all_state(self, temp_dir):
        """Test that recovery preserves complete queue state."""
        state_file = temp_dir / "complete_recovery.json"
        
        config = QueueConfig(
            persistence_path=str(state_file),
            auto_recovery=True
        )
        queue1 = TaskQueue(config)
        
        # Set up complex state
        await queue1.register_worker("worker1", {"agent_types": ["Generation"]})
        await queue1.register_worker("worker2", {"agent_types": ["Reflection"]})
        await queue1.enable_capability_matching()
        
        # Add various tasks
        tasks = []
        for i in range(5):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS if i < 3 else TaskType.REFLECT_ON_HYPOTHESIS,
                priority=(i % 3) + 1,
                payload={"id": i}
            )
            task_id = await queue1.enqueue(task)
            tasks.append((task_id, task))
        
        # Process some tasks - track which ones we actually process
        assignment1 = await queue1.dequeue("worker1")
        completed_task_id = str(assignment1.task.id)
        await queue1.acknowledge_task("worker1", assignment1.assignment_id)
        result = await queue1.complete_task("worker1", completed_task_id, {"result": "done"})
        assert result is True
        
        assignment2 = await queue1.dequeue("worker1")
        failed_task_id = str(assignment2.task.id)
        await queue1.acknowledge_task("worker1", assignment2.assignment_id)
        await queue1.fail_task("worker1", failed_task_id, {"error": "test", "retryable": True})
        
        # Save state
        await queue1.save_state()
        
        
        # Recover in new queue
        queue2 = TaskQueue(config)
        await queue2.initialize()
        
        # Verify all state preserved
        # Note: size() only counts tasks in queues, not completed/failed tasks
        assert queue2.size() == 4  # 5 - 1 completed (the failed one goes back to queue)
        assert queue2.is_worker_registered("worker1")
        assert queue2.is_worker_registered("worker2")
        assert queue2._capability_matching_enabled
        
        # Check task states
        # The completed task should maintain its completed state
        assert queue2.get_task_state(completed_task_id) == TaskState.COMPLETED
        
        # The failed task should be back in pending (retried)
        assert queue2.get_task_state(failed_task_id) == TaskState.PENDING
        assert queue2._task_retry_counts.get(failed_task_id, 0) == 1
    
    async def test_recovery_starts_background_tasks(self, temp_dir):
        """Test that recovery starts persistence and monitoring tasks."""
        state_file = temp_dir / "background_recovery.json"
        
        config = QueueConfig(
            persistence_path=str(state_file),
            auto_recovery=True,
            auto_start_persistence=True,
            auto_start_monitoring=True,
            persistence_interval=1,
            heartbeat_check_interval=1
        )
        
        # Create queue with background tasks
        queue = TaskQueue(config)
        await queue.initialize()
        
        # Verify background tasks are running
        assert queue._persistence_task is not None
        assert not queue._persistence_task.done()
        assert queue._monitoring_task is not None
        assert not queue._monitoring_task.done()
        
        # Cleanup
        await queue.stop_persistence()
        queue.stop_monitoring()
        
        # Wait a bit for tasks to properly cancel
        await asyncio.sleep(0.1)
    
    async def test_recovery_ordering_preserved(self, temp_dir):
        """Test that task ordering is preserved after recovery."""
        state_file = temp_dir / "ordering_recovery.json"
        
        config = QueueConfig(
            persistence_path=str(state_file),
            auto_recovery=True
        )
        queue1 = TaskQueue(config)
        
        # Add tasks in specific order
        task_ids = []
        priorities = [3, 3, 2, 2, 1]  # High, high, medium, medium, low
        for i, priority in enumerate(priorities):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=priority,
                payload={"order": i}
            )
            task_id = await queue1.enqueue(task)
            task_ids.append(task_id)
        
        await queue1.save_state()
        
        # Recover
        queue2 = TaskQueue(config)
        await queue2.initialize()
        
        # Register worker and dequeue in order
        await queue2.register_worker("worker1", {})
        
        # Should get high priority tasks first (in FIFO order)
        for i in range(2):
            assignment = await queue2.dequeue("worker1")
            assert assignment.task.payload["order"] == i
            await queue2.complete_task("worker1", str(assignment.task.id), {})
        
        # Then medium priority
        for i in range(2, 4):
            assignment = await queue2.dequeue("worker1")
            assert assignment.task.payload["order"] == i
            await queue2.complete_task("worker1", str(assignment.task.id), {})
        
        # Finally low priority
        assignment = await queue2.dequeue("worker1")
        assert assignment.task.payload["order"] == 4
    
    async def test_concurrent_recovery_safety(self, temp_dir):
        """Test that concurrent recovery attempts are handled safely."""
        state_file = temp_dir / "concurrent_recovery.json"
        
        # Create initial state
        config = QueueConfig(
            persistence_path=str(state_file),
            auto_recovery=True
        )
        queue1 = TaskQueue(config)
        
        task = Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=2, payload={})
        await queue1.enqueue(task)
        await queue1.save_state()
        
        # Try to initialize multiple queues concurrently
        async def create_queue():
            q = TaskQueue(config)
            await q.initialize()
            return q
        
        # This should not cause corruption or errors
        queues = await asyncio.gather(
            create_queue(),
            create_queue(),
            create_queue()
        )
        
        # All should have recovered the same state
        for q in queues:
            assert q.size() == 1