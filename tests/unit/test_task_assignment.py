"""Tests for TaskQueue task assignment logic."""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

import pytest
from uuid import UUID

from src.core.models import Task, TaskState, TaskType
from src.core.task_queue import TaskQueue, QueueConfig, TaskAssignment


class TestTaskAssignment:
    """Tests for TaskQueue task assignment functionality."""
    
    @pytest.fixture
    def queue(self):
        """Create a TaskQueue instance for tests."""
        return TaskQueue()
    
    @pytest.fixture
    def queue_with_small_timeout(self):
        """Create a TaskQueue with small timeout for testing."""
        config = QueueConfig(
            worker_timeout=5,  # 5 seconds
            heartbeat_interval=1,  # 1 second
            acknowledgment_timeout=0.05  # 50ms for quick testing
        )
        return TaskQueue(config=config)
    
    async def test_assign_task_to_capable_worker(self, queue):
        """Test task is assigned to worker with matching capabilities."""
        # Register workers with different capabilities
        await queue.register_worker("worker-1", {
            "agent_types": ["Generation", "Reflection"]
        })
        await queue.register_worker("worker-2", {
            "agent_types": ["Ranking", "Evolution"]
        })
        
        # Add a generation task
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=2,
            payload={"test": True}
        )
        await queue.enqueue(task)
        
        # Request task with worker-1 (has Generation capability)
        assignment = await queue.dequeue("worker-1")
        assert assignment is not None
        assert assignment.task.id == task.id
        
        # Worker-1 should be marked as active with task
        status = await queue.get_worker_status("worker-1")
        assert status["state"] == "active"
        assert status["assigned_task"] == str(task.id)
    
    async def test_task_not_assigned_to_incapable_worker(self, queue):
        """Test task is not assigned to worker without matching capabilities."""
        # Register worker without Generation capability
        await queue.register_worker("worker-1", {
            "agent_types": ["Ranking", "Evolution"]
        })
        
        # Add a generation task that worker-1 can't handle
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=2,
            payload={"test": True}
        )
        await queue.enqueue(task)
        
        # Enable capability checking
        await queue.enable_capability_matching()
        
        # Request should return None as worker can't handle this task
        assignment = await queue.dequeue("worker-1")
        assert assignment is None
        
        # Task should still be pending
        assert queue.get_task_state(task.id) == TaskState.PENDING
    
    async def test_task_acknowledgment_required(self, queue):
        """Test task requires acknowledgment within timeout."""
        # Register worker
        await queue.register_worker("worker-1", {
            "agent_types": ["Generation"]
        })
        
        # Add task
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=2,
            payload={"test": True}
        )
        await queue.enqueue(task)
        
        # Get assignment
        assignment = await queue.dequeue("worker-1")
        assert assignment is not None
        
        # Check acknowledgment deadline is set
        now = datetime.now(timezone.utc).timestamp()
        assert assignment.acknowledgment_required_by > now
        assert assignment.acknowledgment_required_by <= now + 5  # 5 second window
        
        # Acknowledge the task
        ack_result = await queue.acknowledge_task(
            "worker-1", 
            assignment.assignment_id
        )
        assert ack_result is True
        
        # Task should now be executing
        assert queue.get_task_state(task.id) == TaskState.EXECUTING
    
    async def test_task_reassigned_on_acknowledgment_timeout(self, queue_with_small_timeout):
        """Test task is reassigned if not acknowledged in time."""
        queue = queue_with_small_timeout
        
        # Register two workers
        await queue.register_worker("worker-1", {
            "agent_types": ["Generation"]
        })
        await queue.register_worker("worker-2", {
            "agent_types": ["Generation"]
        })
        
        # Add task
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=2,
            payload={"test": True}
        )
        await queue.enqueue(task)
        
        # Worker-1 gets the task
        assignment1 = await queue.dequeue("worker-1")
        assert assignment1 is not None
        
        # Don't acknowledge - wait for timeout
        await asyncio.sleep(0.1)  # Small delay
        
        # Process timeouts (this would normally be done by a background task)
        await queue.check_assignment_timeouts()
        
        # Task should be back in pending state
        assert queue.get_task_state(task.id) == TaskState.PENDING
        
        # Worker-2 should be able to get the task
        assignment2 = await queue.dequeue("worker-2")
        assert assignment2 is not None
        assert assignment2.task.id == task.id
        assert assignment2.assignment_id != assignment1.assignment_id
    
    async def test_multiple_task_assignment_by_priority(self, queue):
        """Test multiple tasks are assigned in priority order."""
        # Register workers
        await queue.register_worker("worker-1", {"agent_types": ["Generation"]})
        await queue.register_worker("worker-2", {"agent_types": ["Reflection"]})
        
        # Add tasks with different priorities
        low_task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=1,
            payload={"priority": "low"}
        )
        high_task = Task(
            task_type=TaskType.REFLECT_ON_HYPOTHESIS,
            priority=3,
            payload={"priority": "high"}
        )
        medium_task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=2,
            payload={"priority": "medium"}
        )
        
        # Add in mixed order
        await queue.enqueue(low_task)
        await queue.enqueue(high_task)
        await queue.enqueue(medium_task)
        
        # Worker-2 should get high priority reflection task
        assignment1 = await queue.dequeue("worker-2")
        assert assignment1.task.id == high_task.id
        
        # Worker-1 should get medium priority generation task
        assignment2 = await queue.dequeue("worker-1")
        assert assignment2.task.id == medium_task.id
    
    async def test_worker_load_balancing(self, queue):
        """Test tasks are distributed evenly among capable workers."""
        # Register three workers with same capabilities
        for i in range(3):
            await queue.register_worker(f"worker-{i+1}", {
                "agent_types": ["Generation"]
            })
        
        # Add multiple tasks
        task_ids = []
        for i in range(6):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=2,
                payload={"index": i}
            )
            task_id = await queue.enqueue(task)
            task_ids.append(task_id)
        
        # Each worker requests tasks
        assignments = {}
        for i in range(3):
            worker_id = f"worker-{i+1}"
            # Get 2 tasks per worker
            for j in range(2):
                assignment = await queue.dequeue(worker_id)
                if assignment:
                    if worker_id not in assignments:
                        assignments[worker_id] = []
                    assignments[worker_id].append(assignment.task.id)
                    # Acknowledge to allow getting next task
                    await queue.acknowledge_task(worker_id, assignment.assignment_id)
                    await queue.complete_task(worker_id, str(assignment.task.id), {})
        
        # Check distribution
        assert len(assignments) == 3  # All workers got tasks
        for worker_id, worker_tasks in assignments.items():
            assert len(worker_tasks) == 2  # Each worker got 2 tasks
    
    async def test_task_completion_workflow(self, queue):
        """Test complete task assignment and completion workflow."""
        # Register worker
        await queue.register_worker("worker-1", {
            "agent_types": ["Generation"]
        })
        
        # Add task
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=2,
            payload={"test": True}
        )
        await queue.enqueue(task)
        
        # Get assignment
        assignment = await queue.dequeue("worker-1")
        assert assignment is not None
        
        # Acknowledge
        await queue.acknowledge_task("worker-1", assignment.assignment_id)
        assert queue.get_task_state(task.id) == TaskState.EXECUTING
        
        # Complete task
        result = {"hypothesis": "Test hypothesis"}
        completion = await queue.complete_task(
            "worker-1", 
            str(task.id), 
            result
        )
        assert completion is True
        
        # Check final state
        assert queue.get_task_state(task.id) == TaskState.COMPLETED
        
        # Worker should be idle again
        status = await queue.get_worker_status("worker-1")
        assert status["state"] == "idle"
        assert status["assigned_task"] is None
    
    async def test_task_failure_and_retry(self, queue):
        """Test task failure and retry logic."""
        # Register worker
        await queue.register_worker("worker-1", {
            "agent_types": ["Generation"]
        })
        
        # Add task
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=2,
            payload={"test": True}
        )
        await queue.enqueue(task)
        
        # Get and acknowledge task
        assignment = await queue.dequeue("worker-1")
        await queue.acknowledge_task("worker-1", assignment.assignment_id)
        
        # Report failure
        error = {"error": "Test failure", "retryable": True}
        failure = await queue.fail_task(
            "worker-1",
            str(task.id),
            error
        )
        assert failure is True
        
        # Task should be back in pending for retry
        assert queue.get_task_state(task.id) == TaskState.PENDING
        
        # Should be able to get task again
        assignment2 = await queue.dequeue("worker-1")
        assert assignment2 is not None
        assert assignment2.task.id == task.id
        
        # Check retry count incremented
        task_info = await queue.get_task_info(str(task.id))
        assert task_info["retry_count"] == 1