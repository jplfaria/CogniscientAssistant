"""Unit tests for TaskQueue state export/import functionality."""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import uuid

import pytest

from src.core.models import Task, TaskState, TaskType
from src.core.task_queue import TaskQueue, QueueConfig, TaskAssignment


@pytest.fixture
async def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestTaskQueueStateManagement:
    """Test state export and import functionality."""
    
    @pytest.mark.asyncio
    async def test_export_state_empty_queue(self, temp_dir: Path):
        """Test exporting state from an empty queue."""
        config = QueueConfig()
        queue = TaskQueue(config=config)
        
        state = await queue.export_state()
        
        assert isinstance(state, dict)
        assert state["version"] == "1.0.0"
        assert state["pending_tasks"] == []
        assert state["in_progress_tasks"] == []
        assert state["completed_tasks"] == []
        assert state["failed_tasks"] == []
        assert state["workers"] == {}
        assert state["statistics"]["total_enqueued"] == 0
        assert state["statistics"]["total_completed"] == 0
        assert state["statistics"]["total_failed"] == 0
    
    @pytest.mark.asyncio
    async def test_export_state_with_tasks(self, temp_dir: Path):
        """Test exporting state with various task states."""
        config = QueueConfig()
        queue = TaskQueue(config=config)
        
        # Create a task that will remain pending
        pending_task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=1,
            payload={"content": "pending"}
        )
        pending_id = await queue.enqueue(pending_task)
        
        # Create a task that will be in progress
        in_progress_task = Task(
            task_type=TaskType.REFLECT_ON_HYPOTHESIS,
            priority=2,
            payload={"content": "in_progress"}
        )
        in_progress_id = await queue.enqueue(in_progress_task)
        
        # Register worker and get the second task (leaving first pending)
        await queue.register_worker("worker-1", {"agent_types": ["Reflection"]})
        assignment = await queue.dequeue("worker-1")
        assert str(assignment.task.id) == in_progress_id
        
        # Create and complete a task
        completed_task = Task(
            task_type=TaskType.RANK_HYPOTHESES,
            priority=2,
            payload={"content": "completed"}
        )
        completed_id = await queue.enqueue(completed_task)
        await queue.register_worker("worker-2", {"agent_types": ["Ranking"]})
        assignment2 = await queue.dequeue("worker-2")
        await queue.complete_task("worker-2", str(assignment2.task.id), {"result": "done"})
        
        # Export state
        state = await queue.export_state()
        
        # Verify structure
        assert len(state["pending_tasks"]) == 1
        assert state["pending_tasks"][0]["id"] == pending_id
        assert state["pending_tasks"][0]["state"] == TaskState.PENDING.value
        
        assert len(state["in_progress_tasks"]) == 1
        assert state["in_progress_tasks"][0]["id"] == in_progress_id
        assert state["in_progress_tasks"][0]["state"] == TaskState.ASSIGNED.value
        assert state["in_progress_tasks"][0]["assigned_worker"] == "worker-1"
        
        assert len(state["completed_tasks"]) == 1
        assert state["completed_tasks"][0]["id"] == completed_id
        assert state["completed_tasks"][0]["state"] == TaskState.COMPLETED.value
        
        assert len(state["workers"]) == 2
        assert "worker-1" in state["workers"]
        assert "worker-2" in state["workers"]
    
    @pytest.mark.asyncio
    async def test_import_state_basic(self, temp_dir: Path):
        """Test importing a basic state."""
        # Create state to import
        state = {
            "version": "1.0.0",
            "pending_tasks": [
                {
                    "id": str(uuid.uuid4()),
                    "task_type": TaskType.GENERATE_HYPOTHESIS.value,
                    "priority": 1,
                    "payload": {"content": "imported task"},
                    "state": TaskState.PENDING.value,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "metadata": {}
                }
            ],
            "in_progress_tasks": [],
            "completed_tasks": [],
            "failed_tasks": [],
            "workers": {},
            "statistics": {
                "total_enqueued": 1,
                "total_completed": 0,
                "total_failed": 0
            }
        }
        
        config = QueueConfig()
        queue = TaskQueue(config=config)
        
        # Import state
        await queue.import_state(state)
        
        # Verify task was imported
        assert queue.size() == 1
        
        # Register worker and dequeue to verify task details
        await queue.register_worker("worker-1", {"agent_types": ["Generation"]})
        assignment = await queue.dequeue("worker-1")
        
        assert assignment is not None
        assert assignment.task.payload["content"] == "imported task"
        assert assignment.task.task_type == TaskType.GENERATE_HYPOTHESIS
    
    @pytest.mark.asyncio
    async def test_import_state_preserves_task_states(self, temp_dir: Path):
        """Test that import preserves different task states correctly."""
        # Create IDs
        pending_id = str(uuid.uuid4())
        in_progress_id = str(uuid.uuid4())
        completed_id = str(uuid.uuid4())
        failed_id = str(uuid.uuid4())
        
        state = {
            "version": "1.0.0",
            "pending_tasks": [
                {
                    "id": pending_id,
                    "task_type": TaskType.GENERATE_HYPOTHESIS.value,
                    "priority": 1,
                    "payload": {"content": "pending"},
                    "state": TaskState.PENDING.value,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "metadata": {}
                }
            ],
            "in_progress_tasks": [
                {
                    "id": in_progress_id,
                    "task_type": TaskType.REFLECT_ON_HYPOTHESIS.value,
                    "priority": 2,
                    "payload": {"content": "in_progress"},
                    "state": TaskState.ASSIGNED.value,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "assigned_worker": "worker-1",
                    "metadata": {}
                }
            ],
            "completed_tasks": [
                {
                    "id": completed_id,
                    "task_type": TaskType.RANK_HYPOTHESES.value,
                    "priority": 3,
                    "payload": {"content": "completed"},
                    "state": TaskState.COMPLETED.value,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "result": {"score": 0.95},
                    "metadata": {}
                }
            ],
            "failed_tasks": [
                {
                    "id": failed_id,
                    "task_type": TaskType.EVOLVE_HYPOTHESIS.value,
                    "priority": 3,
                    "payload": {"content": "failed"},
                    "state": TaskState.FAILED.value,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "failed_at": datetime.now(timezone.utc).isoformat(),
                    "error": "Test error",
                    "metadata": {}
                }
            ],
            "workers": {
                "worker-1": {
                    "id": "worker-1",
                    "capabilities": {"agent_types": ["Review"]},
                    "state": "active",
                    "last_heartbeat": datetime.now(timezone.utc).isoformat(),
                    "assigned_task": in_progress_id,
                    "registration_time": datetime.now(timezone.utc).isoformat()
                }
            },
            "statistics": {
                "total_enqueued": 4,
                "total_completed": 1,
                "total_failed": 1
            }
        }
        
        config = QueueConfig()
        queue = TaskQueue(config=config)
        
        # Import state
        await queue.import_state(state)
        
        # Verify statistics
        stats = await queue.get_queue_statistics()
        assert stats["task_states"]["pending"] == 1
        assert stats["task_states"]["completed"] == 1
        assert stats["task_states"]["failed"] == 1
        assert stats["task_states"]["assigned"] == 1
        
        # Verify queue has pending task
        assert queue.size() == 1
        
        # Worker state verification is tested through statistics
    
    @pytest.mark.asyncio
    async def test_export_import_roundtrip(self, temp_dir: Path):
        """Test that export followed by import preserves state."""
        config = QueueConfig()
        queue1 = TaskQueue(config=config)
        
        # Create various tasks
        task_ids = []
        for i in range(5):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=min(i + 1, 3),  # Priority must be 1-3
                payload={"index": i, "data": f"task_{i}"}
            )
            task_id = await queue1.enqueue(task)
            task_ids.append(task_id)
        
        # Register workers
        await queue1.register_worker("worker-1", {"agent_types": ["Generation"]})
        await queue1.register_worker("worker-2", {"agent_types": ["Generation"]})
        
        # Process some tasks
        assignment1 = await queue1.dequeue("worker-1")
        assignment2 = await queue1.dequeue("worker-2")
        
        # Complete one task
        await queue1.complete_task("worker-1", str(assignment1.task.id), {"result": "done"})
        
        # Fail one task
        await queue1.fail_task("worker-2", str(assignment2.task.id), {"error": "Test failure", "retryable": False})
        
        # Export state
        exported_state = await queue1.export_state()
        
        # Create new queue and import
        queue2 = TaskQueue(config=config)
        await queue2.import_state(exported_state)
        
        # Compare statistics
        stats1 = await queue1.get_queue_statistics()
        stats2 = await queue2.get_queue_statistics()
        
        assert stats1["task_states"]["completed"] == stats2["task_states"]["completed"]
        assert stats1["task_states"]["failed"] == stats2["task_states"]["failed"]
        assert stats1["task_states"]["pending"] == stats2["task_states"]["pending"]
        
        # Verify queue sizes match
        assert queue1.size() == queue2.size()
    
    @pytest.mark.asyncio
    async def test_import_state_with_invalid_version(self, temp_dir: Path):
        """Test handling of incompatible state versions."""
        state = {
            "version": "2.0",  # Future version
            "pending_tasks": [],
            "in_progress_tasks": [],
            "completed_tasks": [],
            "failed_tasks": [],
            "workers": {},
            "statistics": {}
        }
        
        config = QueueConfig()
        queue = TaskQueue(config=config)
        
        # Should handle gracefully or raise clear error
        with pytest.raises(ValueError, match="version"):
            await queue.import_state(state)
    
    @pytest.mark.asyncio
    async def test_import_state_missing_fields(self, temp_dir: Path):
        """Test handling of incomplete state data."""
        # Missing required fields
        state = {
            "version": "1.0.0",
            "pending_tasks": []
            # Missing other required fields
        }
        
        config = QueueConfig()
        queue = TaskQueue(config=config)
        
        # Should handle gracefully without raising errors
        await queue.import_state(state)
        
        # Queue should be empty but functional
        assert queue.size() == 0
    
    @pytest.mark.asyncio
    async def test_export_state_concurrent_modifications(self, temp_dir: Path):
        """Test export state handles concurrent task modifications."""
        config = QueueConfig()
        queue = TaskQueue(config=config)
        
        # Add many tasks
        task_ids = []
        for i in range(10):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=1,
                payload={"index": i}
            )
            task_id = await queue.enqueue(task)
            task_ids.append(task_id)
        
        # Register worker
        await queue.register_worker("worker-1", {"agent_types": ["Generation"]})
        
        async def process_tasks():
            """Process tasks while export is happening."""
            for _ in range(5):
                assignment = await queue.dequeue("worker-1")
                if assignment:
                    await queue.complete_task("worker-1", str(assignment.task.id), {"done": True})
                await asyncio.sleep(0.01)
        
        # Start processing tasks concurrently with export
        process_task = asyncio.create_task(process_tasks())
        
        # Export state multiple times
        states = []
        for _ in range(3):
            state = await queue.export_state()
            states.append(state)
            await asyncio.sleep(0.02)
        
        await process_task
        
        # All exports should be valid
        for state in states:
            assert "version" in state
            assert isinstance(state["pending_tasks"], list)
            assert isinstance(state["completed_tasks"], list)
            # Total tasks should remain constant
            total = (len(state["pending_tasks"]) + 
                    len(state["in_progress_tasks"]) + 
                    len(state["completed_tasks"]) + 
                    len(state["failed_tasks"]))
            assert total == 10