"""Test queue persistence functionality."""

import asyncio
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime
import pytest

from src.core.models import Task, TaskState, TaskType
from src.core.task_queue import TaskQueue, QueueConfig


@pytest.fixture
async def temp_dir():
    """Create a temporary directory for persistence tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
async def queue_with_persistence(temp_dir):
    """Create a queue with persistence enabled."""
    config = QueueConfig(
        persistence_interval=1,  # 1 second for testing
        persistence_path=str(temp_dir / "queue_state.json")
    )
    queue = TaskQueue(config)
    yield queue
    # Cleanup
    queue.stop_monitoring()
    await queue.stop_persistence()


class TestQueuePersistence:
    """Test queue persistence and recovery functionality."""
    
    async def test_save_queue_state(self, queue_with_persistence, temp_dir):
        """Test saving queue state to disk."""
        queue = queue_with_persistence
        
        # Add some tasks
        tasks = []
        for i in range(3):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=2,
                payload={"id": i}
            )
            task_id = await queue.enqueue(task)
            tasks.append((task_id, task))
        
        # Save state
        await queue.save_state()
        
        # Check file exists
        state_file = Path(queue.config.persistence_path)
        assert state_file.exists()
        
        # Load and verify state
        with open(state_file, 'r') as f:
            saved_state = json.load(f)
        
        assert "version" in saved_state
        assert "timestamp" in saved_state
        assert "queues" in saved_state
        assert "tasks" in saved_state
        assert "workers" in saved_state
        assert "assignments" in saved_state
        
        # Verify task data
        assert len(saved_state["tasks"]) == 3
        for task_id, task in tasks:
            assert task_id in saved_state["tasks"]
    
    async def test_load_queue_state(self, temp_dir):
        """Test loading queue state from disk."""
        # Create initial queue and add tasks
        config = QueueConfig(
            persistence_path=str(temp_dir / "queue_state.json")
        )
        queue1 = TaskQueue(config)
        
        # Add tasks
        task_ids = []
        for i in range(3):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=i + 1,  # Different priorities
                payload={"id": i}
            )
            task_id = await queue1.enqueue(task)
            task_ids.append(task_id)
        
        # Save state
        await queue1.save_state()
        
        # Create new queue and load state
        queue2 = TaskQueue(config)
        await queue2.load_state()
        
        # Verify state was loaded correctly
        assert queue2.size() == 3
        assert queue2.size_by_priority("high") == 1
        assert queue2.size_by_priority("medium") == 1
        assert queue2.size_by_priority("low") == 1
        
        # Verify tasks are in correct order
        for i in range(3):
            task_state = queue2.get_task_state(task_ids[i])
            assert task_state == TaskState.PENDING
    
    async def test_persist_worker_state(self, queue_with_persistence):
        """Test that worker registration state is persisted."""
        queue = queue_with_persistence
        
        # Register workers
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        await queue.register_worker("worker2", {"agent_types": ["Reflection", "Evolution"]})
        
        # Save state
        await queue.save_state()
        
        # Load state in new queue
        queue2 = TaskQueue(queue.config)
        await queue2.load_state()
        
        # Verify workers were restored
        assert queue2.is_worker_registered("worker1")
        assert queue2.is_worker_registered("worker2")
        
        # Verify capabilities were restored
        worker1_status = await queue2.get_worker_status("worker1")
        assert worker1_status["capabilities"]["agent_types"] == ["Generation"]
        
        worker2_status = await queue2.get_worker_status("worker2")
        assert worker2_status["capabilities"]["agent_types"] == ["Reflection", "Evolution"]
    
    async def test_persist_task_assignments(self, queue_with_persistence):
        """Test that task assignments are persisted."""
        queue = queue_with_persistence
        
        # Register worker and create task
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        task = Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=2, payload={})
        task_id = await queue.enqueue(task)
        
        # Assign task
        assignment = await queue.dequeue("worker1")
        await queue.acknowledge_task("worker1", assignment.assignment_id)
        
        # Save state
        await queue.save_state()
        
        # Load state in new queue
        queue2 = TaskQueue(queue.config)
        await queue2.load_state()
        
        # Verify task state
        assert queue2.get_task_state(task_id) == TaskState.EXECUTING
        
        # Verify worker state
        worker_status = await queue2.get_worker_status("worker1")
        assert worker_status["state"] == "active"
        assert worker_status["assigned_task"] == task_id
    
    async def test_persist_task_history(self, queue_with_persistence):
        """Test that task retry counts and failure history are persisted."""
        queue = queue_with_persistence
        
        # Register worker and create task
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        task = Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=2, payload={})
        task_id = await queue.enqueue(task)
        
        # Fail task once
        assignment = await queue.dequeue("worker1")
        await queue.acknowledge_task("worker1", assignment.assignment_id)
        await queue.fail_task("worker1", task_id, {"error": "Test failure", "retryable": True})
        
        # Save state
        await queue.save_state()
        
        # Load state in new queue
        queue2 = TaskQueue(queue.config)
        await queue2.load_state()
        
        # Verify retry count and failure history
        task_info = await queue2.get_task_info(task_id)
        assert task_info["retry_count"] == 1
        assert len(task_info["failure_history"]) == 1
        assert task_info["failure_history"][0]["error"]["error"] == "Test failure"
    
    async def test_automatic_persistence(self, temp_dir):
        """Test automatic periodic persistence."""
        config = QueueConfig(
            persistence_interval=0.5,  # 0.5 seconds for testing
            persistence_path=str(temp_dir / "auto_state.json")
        )
        queue = TaskQueue(config)
        
        # Start persistence
        await queue.start_persistence()
        
        # Add task
        task = Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=2, payload={})
        task_id = await queue.enqueue(task)
        
        # Wait for automatic save
        await asyncio.sleep(0.7)
        
        # Check file was created
        assert Path(config.persistence_path).exists()
        
        # Stop persistence
        await queue.stop_persistence()
        
        # Load state in new queue
        queue2 = TaskQueue(config)
        await queue2.load_state()
        
        # Verify task was persisted
        assert queue2.get_task_state(task_id) == TaskState.PENDING
    
    async def test_persistence_with_completed_tasks(self, queue_with_persistence):
        """Test persisting completed and failed tasks."""
        queue = queue_with_persistence
        
        # Register workers
        await queue.register_worker("worker1", {"agent_types": ["Generation"]})
        await queue.register_worker("worker2", {"agent_types": ["Generation"]})
        
        # Create tasks
        task1 = Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=2, payload={"id": 1})
        task2 = Task(task_type=TaskType.GENERATE_HYPOTHESIS, priority=2, payload={"id": 2})
        
        task1_id = await queue.enqueue(task1)
        task2_id = await queue.enqueue(task2)
        
        # Complete one task
        assignment1 = await queue.dequeue("worker1")
        await queue.acknowledge_task("worker1", assignment1.assignment_id)
        await queue.complete_task("worker1", task1_id, {"result": "success"})
        
        # Fail another task permanently
        assignment2 = await queue.dequeue("worker2")
        await queue.acknowledge_task("worker2", assignment2.assignment_id)
        await queue.fail_task("worker2", task2_id, {"error": "permanent", "retryable": False})
        
        # Save state
        await queue.save_state()
        
        # Load state in new queue
        queue2 = TaskQueue(queue.config)
        await queue2.load_state()
        
        # Verify states
        assert queue2.get_task_state(task1_id) == TaskState.COMPLETED
        assert queue2.get_task_state(task2_id) == TaskState.FAILED
        
        # Verify task results
        task1_info = await queue2.get_task_info(task1_id)
        assert task1_info is not None
        
        task2_info = await queue2.get_task_info(task2_id)
        assert len(task2_info["failure_history"]) == 1
    
    async def test_persistence_version_check(self, temp_dir):
        """Test that persistence format version is checked."""
        state_file = temp_dir / "version_test.json"
        
        # Create state with incompatible version
        incompatible_state = {
            "version": "0.0.1",  # Old version
            "timestamp": datetime.utcnow().isoformat(),
            "queues": {},
            "tasks": {},
            "workers": {},
            "assignments": {}
        }
        
        with open(state_file, 'w') as f:
            json.dump(incompatible_state, f)
        
        # Try to load with new queue
        config = QueueConfig(persistence_path=str(state_file))
        queue = TaskQueue(config)
        
        # Should handle version mismatch gracefully
        with pytest.raises(ValueError, match="version"):
            await queue.load_state()
    
    async def test_persistence_corruption_handling(self, temp_dir):
        """Test handling of corrupted persistence files."""
        state_file = temp_dir / "corrupt.json"
        
        # Write corrupted JSON
        with open(state_file, 'w') as f:
            f.write("{ corrupted json data")
        
        # Try to load
        config = QueueConfig(persistence_path=str(state_file))
        queue = TaskQueue(config)
        
        # Should handle corruption gracefully
        with pytest.raises(json.JSONDecodeError):
            await queue.load_state()
    
    async def test_persistence_missing_file(self, temp_dir):
        """Test loading when persistence file doesn't exist."""
        config = QueueConfig(
            persistence_path=str(temp_dir / "nonexistent.json")
        )
        queue = TaskQueue(config)
        
        # Should handle missing file gracefully (no error, empty queue)
        await queue.load_state()
        assert queue.size() == 0
    
    async def test_concurrent_persistence_safety(self, queue_with_persistence):
        """Test that concurrent operations don't corrupt persistence."""
        queue = queue_with_persistence
        
        # Start automatic persistence
        await queue.start_persistence()
        
        # Perform many concurrent operations
        async def add_tasks():
            for i in range(10):
                task = Task(
                    task_type=TaskType.GENERATE_HYPOTHESIS,
                    priority=2,
                    payload={"id": i}
                )
                await queue.enqueue(task)
                await asyncio.sleep(0.01)
        
        async def register_workers():
            for i in range(5):
                await queue.register_worker(f"worker{i}", {"agent_types": ["Generation"]})
                await asyncio.sleep(0.02)
        
        # Run concurrently
        await asyncio.gather(add_tasks(), register_workers())
        
        # Force save
        await queue.save_state()
        
        # Stop persistence
        await queue.stop_persistence()
        
        # Load in new queue
        queue2 = TaskQueue(queue.config)
        await queue2.load_state()
        
        # Verify state integrity
        assert queue2.size() == 10
        assert len(queue2.get_registered_workers()) == 5