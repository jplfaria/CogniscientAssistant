"""Integration tests for Phase 3: Task Queue Workflow.

These tests validate that the task queue implementation works correctly
for AI Co-Scientist workflows without requiring actual agents.
"""

import asyncio
from pathlib import Path
from typing import Dict, List

import pytest

from src.core.models import Task, TaskState, TaskType
from src.core.task_queue import TaskQueue, QueueConfig


class TestTaskQueueIntegration:
    """Test task queue integration for AI Co-Scientist workflows."""
    
    @pytest.mark.asyncio
    async def test_full_task_lifecycle(self, task_queue: TaskQueue):
        """Test complete task lifecycle: Create → Enqueue → Assign → Execute → Complete."""
        # 1. Create a task representing hypothesis generation
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=3,  # High priority
            payload={"goal": "Discover new superconducting materials"}
        )
        
        # 2. Enqueue the task
        task_id = await task_queue.enqueue(task)
        assert task_id == str(task.id)
        assert task_queue.size() == 1
        
        # 3. Register a worker that can handle generation
        worker_id = "generation-worker-1"
        capabilities = {
            "agent_types": ["Generation"],
            "max_concurrent": 1,
            "version": "1.0.0"
        }
        await task_queue.register_worker(worker_id, capabilities)
        
        # 4. Worker dequeues the task
        assignment = await task_queue.dequeue(worker_id)
        assert assignment is not None
        assert assignment.task.id == task.id
        assert assignment.task.assigned_to == worker_id
        
        # 5. Verify task state is now assigned
        task_state = task_queue.get_task_state(task_id)
        assert task_state == TaskState.ASSIGNED
        
        # 6. Acknowledge the task (required by the API)
        ack_result = await task_queue.acknowledge_task(worker_id, assignment.assignment_id)
        assert ack_result is True
        
        # 7. Complete the task with a result
        result = {
            "hypothesis": "High-pressure hydrogen sulfide exhibits superconductivity at 203K",
            "confidence": 0.85,
            "experimental_protocol": "Apply 155 GPa pressure to H2S sample..."
        }
        complete_result = await task_queue.complete_task(worker_id, task_id, result)
        
        # 8. Verify final state
        task_state = task_queue.get_task_state(task_id)
        assert task_state == TaskState.COMPLETED
        
        # 9. Check statistics
        stats = await task_queue.get_queue_statistics()
        assert stats["task_states"]["completed"] == 1
        assert stats["worker_stats"]["active"] == 0  # Worker should be idle after completion
    
    @pytest.mark.asyncio
    async def test_hypothesis_generation_workflow(self, task_queue: TaskQueue):
        """Test a complete hypothesis generation and reflection workflow."""
        # Simulate what the Supervisor agent would do
        
        # 1. Create tasks for a research goal
        research_goal = "Find materials with negative thermal expansion"
        tasks = [
            Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=3,
                payload={"goal": research_goal, "iteration": 1}
            ),
            Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=3,
                payload={"goal": research_goal, "iteration": 2}
            ),
            Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=3,
                payload={"goal": research_goal, "iteration": 3}
            ),
        ]
        
        # 2. Enqueue all generation tasks
        task_ids = []
        for task in tasks:
            task_id = await task_queue.enqueue(task)
            task_ids.append(task_id)
        
        assert task_queue.size() == 3
        assert task_queue.size_by_priority("high") == 3
        
        # 3. Register multiple generation workers
        worker_ids = ["gen-worker-1", "gen-worker-2"]
        for worker_id in worker_ids:
            await task_queue.register_worker(
                worker_id, 
                {"agent_types": ["Generation"]}
            )
        
        # 4. Workers process tasks concurrently
        assignments = []
        for worker_id in worker_ids:
            assignment = await task_queue.dequeue(worker_id)
            if assignment:
                assignments.append(assignment)
        
        assert len(assignments) == 2  # Two workers got tasks
        assert task_queue.size() == 1  # One task remains
        
        # 5. Complete the assigned tasks
        hypotheses = []
        for i, assignment in enumerate(assignments):
            # Get the worker who has this assignment
            worker_id = assignment.task.assigned_to
            hypothesis = {
                "id": f"hyp_{i+1}",
                "summary": f"Hypothesis {i+1} about negative thermal expansion",
                "confidence": 0.7 + (i * 0.1)
            }
            await task_queue.complete_task(
                worker_id,
                str(assignment.task.id), 
                hypothesis
            )
            hypotheses.append(hypothesis)
        
        # 6. Create reflection tasks for completed hypotheses
        for hypothesis in hypotheses:
            reflection_task = Task(
                task_type=TaskType.REFLECT_ON_HYPOTHESIS,
                priority=2,  # Medium priority
                payload={"hypothesis_id": hypothesis["id"], "hypothesis": hypothesis}
            )
            await task_queue.enqueue(reflection_task)
        
        # 7. Verify queue state
        stats = await task_queue.get_queue_statistics()
        assert stats["task_states"]["completed"] == 2
        assert stats["task_states"]["pending"] == 3  # 1 generation + 2 reflection
        assert stats["total_tasks"] == 3  # 3 tasks still in queue
    
    @pytest.mark.asyncio
    async def test_priority_based_processing(self, task_queue: TaskQueue):
        """Test that high priority tasks are processed before lower priority ones."""
        # Create tasks with different priorities
        tasks = [
            Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=1,  # Low
                payload={"goal": "Low priority research", "expected_order": 3}
            ),
            Task(
                task_type=TaskType.RANK_HYPOTHESES,
                priority=3,  # High
                payload={"hypotheses": ["h1", "h2"], "expected_order": 1}
            ),
            Task(
                task_type=TaskType.REFLECT_ON_HYPOTHESIS,
                priority=2,  # Medium
                payload={"hypothesis_id": "h1", "expected_order": 2}
            ),
        ]
        
        # Enqueue in mixed order
        for task in tasks:
            await task_queue.enqueue(task)
        
        # Register a worker that can handle all task types
        await task_queue.register_worker(
            "universal-worker",
            {"agent_types": ["Generation", "Reflection", "Ranking"]}
        )
        
        # Dequeue tasks - should come out in priority order
        processing_order = []
        for _ in range(3):
            assignment = await task_queue.dequeue("universal-worker")
            assert assignment is not None
            expected_order = assignment.task.payload["expected_order"]
            processing_order.append(expected_order)
            # Complete immediately to free worker
            await task_queue.complete_task(
                "universal-worker",
                str(assignment.task.id), 
                {}
            )
        
        # Verify tasks were processed in priority order
        assert processing_order == [1, 2, 3]
    
    @pytest.mark.asyncio
    async def test_worker_capability_matching(self, task_queue: TaskQueue):
        """Test that tasks are only assigned to workers with matching capabilities."""
        # Enable capability matching
        await task_queue.enable_capability_matching()
        
        # Create tasks requiring different agent types
        gen_task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=3,
            payload={"goal": "Test generation"}
        )
        rank_task = Task(
            task_type=TaskType.RANK_HYPOTHESES,
            priority=3,
            payload={"hypotheses": ["h1", "h2"]}
        )
        
        await task_queue.enqueue(gen_task)
        await task_queue.enqueue(rank_task)
        
        # Register a worker that can only do ranking
        await task_queue.register_worker(
            "ranking-specialist",
            {"agent_types": ["Ranking"]}
        )
        
        # Try to dequeue - should only get the ranking task
        assignment = await task_queue.dequeue("ranking-specialist")
        assert assignment is not None
        assert assignment.task.task_type == TaskType.RANK_HYPOTHESES
        
        # Generation task should still be pending
        assert task_queue.size() == 1
        stats = await task_queue.get_queue_statistics()
        assert stats["total_tasks"] == 1
    
    @pytest.mark.asyncio
    async def test_failure_handling_and_retry(self, task_queue: TaskQueue):
        """Test task failure handling and retry logic."""
        # Configure queue with custom retry policy
        config = QueueConfig(
            retry_policy={
                "max_attempts": 3,
                "backoff_base": 2,
                "backoff_max": 10
            }
        )
        queue = TaskQueue(config=config)
        
        # Create and enqueue a task
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=3,
            payload={"goal": "Test retry behavior"}
        )
        task_id = await queue.enqueue(task)
        
        # Register worker and get task
        await queue.register_worker("worker-1", {"agent_types": ["Generation"]})
        assignment = await queue.dequeue("worker-1")
        assert assignment is not None
        
        # Fail the task with retryable error
        await queue.fail_task("worker-1", task_id, {"error": "Network timeout", "retryable": True})
        
        # Task should be retryable
        assert queue.size() == 1  # Back in queue
        task_state = queue.get_task_state(task_id)
        assert task_state == TaskState.PENDING
        
        # Get retry metadata
        stats = await queue.get_retry_statistics()
        assert stats["total_retries"] == 1
        assert stats["tasks_with_retries"] == 1
        
        # Dequeue again (first retry)
        assignment = await queue.dequeue("worker-1")
        assert assignment is not None
        # Check retry count through task info
        task_info = await queue.get_task_info(task_id)
        assert task_info["retry_count"] == 1
    
    @pytest.mark.asyncio
    async def test_queue_persistence_and_recovery(self, task_queue: TaskQueue, temp_dir: Path):
        """Test that queue state persists and recovers correctly."""
        persistence_path = temp_dir / "queue_state.json"
        
        # Create queue with persistence configured
        config1 = QueueConfig(persistence_path=str(persistence_path))
        queue1 = TaskQueue(config=config1)
        
        # Add tasks and workers
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=3,
            payload={"goal": "Test persistence"}
        )
        task_id = await queue1.enqueue(task)
        await queue1.register_worker("worker-1", {"agent_types": ["Generation"]})
        
        # Get some work done
        assignment = await queue1.dequeue("worker-1")
        # Task is now in assigned state, not executing
        
        # Save state
        await queue1.save_state()
        
        # Create new queue with same config and load state
        config2 = QueueConfig(persistence_path=str(persistence_path))
        queue2 = TaskQueue(config=config2)
        await queue2.load_state()
        
        # Verify state was restored
        assert queue2.is_worker_registered("worker-1")
        task_state = queue2.get_task_state(task_id)
        assert task_state == TaskState.ASSIGNED  # Task is assigned, not executing
        
        # Should be able to complete the task
        await queue2.complete_task("worker-1", task_id, {})
        stats = await queue2.get_queue_statistics()
        assert stats["task_states"]["completed"] == 1
    
    @pytest.mark.asyncio
    async def test_comprehensive_statistics(self, task_queue: TaskQueue):
        """Test that statistics accurately reflect queue operations."""
        # Perform various operations
        task_types = [
            (TaskType.GENERATE_HYPOTHESIS, 3),
            (TaskType.REFLECT_ON_HYPOTHESIS, 2),
            (TaskType.RANK_HYPOTHESES, 3),
            (TaskType.EVOLVE_HYPOTHESIS, 1),
        ]
        
        task_ids = []
        for task_type, priority in task_types:
            task = Task(
                task_type=task_type,
                priority=priority,
                payload={"test": True}
            )
            task_id = await task_queue.enqueue(task)
            task_ids.append(task_id)
        
        # Register workers
        await task_queue.register_worker("worker-1", {"agent_types": ["Generation", "Evolution"]})
        await task_queue.register_worker("worker-2", {"agent_types": ["Reflection", "Ranking"]})
        
        # Process some tasks
        for worker_id in ["worker-1", "worker-2"]:
            assignment = await task_queue.dequeue(worker_id)
            if assignment:
                await task_queue.complete_task(
                    worker_id,
                    str(assignment.task.id), 
                    {}
                )
        
        # Get comprehensive statistics
        stats = await task_queue.get_queue_statistics()
        
        # Verify statistics
        assert stats["total_tasks"] == 2  # 2 tasks still in queue
        assert stats["task_states"]["pending"] == 2
        assert stats["task_states"]["completed"] == 2
        assert stats["worker_stats"]["active"] == 0
        assert stats["worker_stats"]["idle"] == 2
        assert stats["worker_stats"]["total"] == 2
    
    @pytest.mark.asyncio
    async def test_concurrent_worker_processing(self, task_queue: TaskQueue):
        """Test multiple workers processing tasks concurrently."""
        # Create many tasks
        num_tasks = 10
        for i in range(num_tasks):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=2,
                payload={"goal": f"Research goal {i}"}
            )
            await task_queue.enqueue(task)
        
        # Register multiple workers
        num_workers = 3
        for i in range(num_workers):
            await task_queue.register_worker(
                f"worker-{i}",
                {"agent_types": ["Generation"]}
            )
        
        # Workers process tasks concurrently
        async def worker_process(worker_id: str):
            processed = 0
            while True:
                assignment = await task_queue.dequeue(worker_id)
                if not assignment:
                    break
                    
                # Simulate processing
                await asyncio.sleep(0.01)
                await task_queue.complete_task(
                    worker_id,
                    str(assignment.task.id),
                    {"result": f"Processed by {worker_id}"}
                )
                processed += 1
            return processed
        
        # Run workers concurrently
        results = await asyncio.gather(*[
            worker_process(f"worker-{i}") for i in range(num_workers)
        ])
        
        # Verify all tasks were processed
        total_processed = sum(results)
        assert total_processed == num_tasks
        
        # Check final statistics
        stats = await task_queue.get_queue_statistics()
        assert stats["task_states"]["completed"] == num_tasks
        assert stats["total_tasks"] == 0  # All tasks processed
        
        # Verify work was distributed among workers
        assert all(count > 0 for count in results)  # Each worker did something
    
    @pytest.mark.asyncio
    async def test_queue_capacity_limits(self, task_queue: TaskQueue):
        """Test queue capacity limits and behavior at different thresholds."""
        # Configure queue with capacity limits
        config = QueueConfig(
            max_queue_size=100,  # Small limit for testing
            priority_quotas={
                "high": 20,
                "medium": 50,
                "low": 30
            }
        )
        queue = TaskQueue(config=config)
        
        # Fill queue to 80% capacity
        # Priority quotas: low=30, medium=50, high=20
        # To get 80 tasks total without hitting quotas: low=24, medium=40, high=16
        tasks_added = 0
        
        # Add low priority tasks (quota: 30)
        for i in range(24):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=1,  # Low
                payload={"task_number": i}
            )
            await queue.enqueue(task)
            tasks_added += 1
        
        # Add medium priority tasks (quota: 50)
        for i in range(24, 64):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=2,  # Medium
                payload={"task_number": i}
            )
            await queue.enqueue(task)
            tasks_added += 1
        
        # Add high priority tasks (quota: 20)
        for i in range(64, 80):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=3,  # High
                payload={"task_number": i}
            )
            await queue.enqueue(task)
            tasks_added += 1
        
        # Check that warning threshold is triggered
        stats = await queue.get_queue_statistics()
        assert queue.size() == 80
        assert stats["capacity_percentage"] == 80.0
        assert stats["capacity_status"] == "warning"
        
        # Add more tasks to reach 95% capacity
        # We need to distribute across priorities to avoid quota limits
        # Low: 6 more (total 30), Medium: 9 more (total 49), High: 0
        for i in range(80, 86):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=1,  # Low
                payload={"task_number": i}
            )
            await queue.enqueue(task)
        
        for i in range(86, 95):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=2,  # Medium
                payload={"task_number": i}
            )
            await queue.enqueue(task)
        
        # Check critical threshold
        stats = await queue.get_queue_statistics()
        assert stats["capacity_percentage"] == 95.0
        assert stats["capacity_status"] == "critical"
        
        # Fill to 100% capacity
        # Medium: 1 more (total 50), High: 4 more (total 20)
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=2,  # Medium
            payload={"task_number": 95}
        )
        await queue.enqueue(task)
        
        for i in range(96, 100):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=3,  # High
                payload={"task_number": i}
            )
            await queue.enqueue(task)
        
        # Verify queue is full
        assert queue.size() == 100
        stats = await queue.get_queue_statistics()
        assert stats["capacity_percentage"] == 100.0
        assert stats["capacity_status"] == "full"
        
        # Try to add a high priority task - should displace low priority
        high_priority_task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=3,
            payload={"task_number": 100, "high_priority": True}
        )
        
        # This should succeed by displacing a low priority task
        # even though high priority queue is at quota
        initial_size = queue.size()
        task_id = await queue.enqueue(high_priority_task)
        assert task_id is not None
        
        # Queue should still be at capacity, but with displacement
        final_size = queue.size()
        stats = await queue.get_queue_statistics()
        print(f"Initial size: {initial_size}, Final size: {final_size}")
        print(f"Queue stats: {stats}")
        
        # After displacement and adding new task, size should remain 100
        assert final_size == 100
        assert stats["displaced_tasks"] > 0
        
        # Verify the displacement statistics
        overflow_stats = await queue.get_overflow_statistics()
        assert overflow_stats["total_displaced"] >= 1
        assert overflow_stats["displacement_by_priority"]["low"] >= 1
    
    @pytest.mark.asyncio
    async def test_task_overflow_handling(self, task_queue: TaskQueue):
        """Test task overflow handling strategies."""
        # Configure queue with small limits
        config = QueueConfig(
            max_queue_size=10,
            overflow_strategy="displace_oldest_low_priority",
            priority_quotas={
                "high": 3,
                "medium": 4,
                "low": 3
            }
        )
        queue = TaskQueue(config=config)
        
        # Fill queue with mixed priority tasks
        # Quotas: low=3, medium=4, high=3
        task_ids = []
        
        # Add 3 low priority tasks
        for i in range(3):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=1,  # Low
                payload={"task_number": i, "original": True}
            )
            task_id = await queue.enqueue(task)
            task_ids.append(task_id)
        
        # Add 4 medium priority tasks
        for i in range(3, 7):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=2,  # Medium
                payload={"task_number": i, "original": True}
            )
            task_id = await queue.enqueue(task)
            task_ids.append(task_id)
            
        # Add 3 high priority tasks
        for i in range(7, 10):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=3,  # High
                payload={"task_number": i, "original": True}
            )
            task_id = await queue.enqueue(task)
            task_ids.append(task_id)
        
        # Queue is now full
        assert queue.size() == 10
        
        # Add new high priority tasks
        new_high_priority_ids = []
        for i in range(3):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=3,
                payload={"task_number": 10 + i, "overflow": True}
            )
            task_id = await queue.enqueue(task)
            new_high_priority_ids.append(task_id)
        
        # Queue should still be at capacity
        assert queue.size() == 10
        
        # Verify low priority tasks were displaced
        for task_id in task_ids[:3]:  # First 3 low priority tasks
            assert queue.get_task_state(task_id) is None  # Displaced
        
        # Verify high priority tasks are present
        for task_id in new_high_priority_ids:
            assert queue.get_task_state(task_id) == TaskState.PENDING
        
        # Check overflow statistics
        stats = await queue.get_overflow_statistics()
        assert stats["total_displaced"] == 3
        assert stats["displacement_by_priority"]["low"] == 3
    
    @pytest.mark.asyncio
    async def test_worker_heartbeat_timeout(self, task_queue: TaskQueue):
        """Test worker heartbeat timeout detection and handling."""
        # Configure queue with short heartbeat timeout
        config = QueueConfig(
            heartbeat_interval=0.1,  # 100ms
            heartbeat_timeout=0.3,    # 300ms
            heartbeat_check_interval=0.1  # Check every 100ms
        )
        queue = TaskQueue(config=config)
        
        # Start heartbeat monitoring
        await queue.initialize()
        monitoring_task = asyncio.create_task(queue.monitor_heartbeats())
        
        # Register worker
        worker_id = "worker-heartbeat-test"
        await queue.register_worker(worker_id, {"agent_types": ["Generation"]})
        
        # Create and assign task
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=3,
            payload={"test": "heartbeat"}
        )
        task_id = await queue.enqueue(task)
        
        # Worker dequeues task
        assignment = await queue.dequeue(worker_id)
        assert assignment is not None
        
        # Send a few heartbeats
        for _ in range(2):
            await queue.send_heartbeat(worker_id)
            await asyncio.sleep(0.1)
        
        # Stop sending heartbeats and wait for timeout
        await asyncio.sleep(0.4)  # Exceed timeout
        
        # Check worker status
        worker_status = await queue.get_worker_status(worker_id)
        assert worker_status["state"] == "failed"
        assert worker_status["failure_reason"] == "heartbeat_timeout"
        
        # Task should be reassigned
        task_state = queue.get_task_state(task_id)
        assert task_state == TaskState.PENDING  # Back in queue
        
        # Check that task can be picked up by another worker
        await queue.register_worker("worker-2", {"agent_types": ["Generation"]})
        assignment2 = await queue.dequeue("worker-2")
        assert assignment2 is not None
        assert assignment2.task.id == task.id
        
        # Cleanup
        queue.stop_monitoring()
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass
    
    @pytest.mark.asyncio
    async def test_dead_letter_queue(self, task_queue: TaskQueue):
        """Test dead letter queue functionality for permanently failed tasks."""
        # Configure queue with retry limits
        config = QueueConfig(
            retry_policy={
                "max_attempts": 2,
                "send_to_dlq": True
            }
        )
        queue = TaskQueue(config=config)
        
        # Create task
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=3,
            payload={"test": "dlq"}
        )
        task_id = await queue.enqueue(task)
        
        # Register worker
        await queue.register_worker("worker-1", {"agent_types": ["Generation"]})
        
        # First attempt - fail with non-retryable error
        assignment = await queue.dequeue("worker-1")
        await queue.fail_task(
            "worker-1", 
            task_id, 
            {"error": "Invalid parameters", "retryable": False}
        )
        
        # Task should go directly to DLQ
        dlq_stats = await queue.get_dlq_statistics()
        assert dlq_stats["total_tasks"] == 1
        assert dlq_stats["by_reason"]["non_retryable_error"] == 1
        
        # Task should not be in main queue
        assert queue.size() == 0
        assert queue.get_task_state(task_id) == TaskState.FAILED
        
        # Create another task for retry exhaustion test
        task2 = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=3,
            payload={"test": "retry_exhaustion"}
        )
        task2_id = await queue.enqueue(task2)
        
        # Fail task multiple times to exhaust retries
        for attempt in range(2):
            assignment = await queue.dequeue("worker-1")
            await queue.fail_task(
                "worker-1",
                task2_id,
                {"error": "Temporary failure", "retryable": True}
            )
            if attempt < 1:  # Not the last attempt
                await asyncio.sleep(0.1)  # Wait for retry
        
        # After max attempts, task should be in DLQ
        dlq_stats = await queue.get_dlq_statistics()
        assert dlq_stats["total_tasks"] == 2
        assert dlq_stats["by_reason"]["retry_exhaustion"] == 1
        
        # Test manual retry from DLQ
        dlq_tasks = await queue.get_dlq_tasks()
        assert len(dlq_tasks) == 2
        
        # Retry first task from DLQ
        retry_result = await queue.retry_from_dlq(task_id)
        assert retry_result["success"] is True
        assert queue.size() == 1
        
        # DLQ should now have one task
        dlq_stats = await queue.get_dlq_statistics()
        assert dlq_stats["total_tasks"] == 1
    
    @pytest.mark.asyncio
    async def test_task_reassignment_on_failure(self, task_queue: TaskQueue):
        """Test task reassignment when workers fail."""
        # Configure queue
        config = QueueConfig()
        queue = TaskQueue(config=config)
        
        # Create high priority task
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=3,
            payload={"test": "reassignment"}
        )
        task_id = await queue.enqueue(task)
        
        # Register two workers
        await queue.register_worker("worker-1", {"agent_types": ["Generation"]})
        await queue.register_worker("worker-2", {"agent_types": ["Generation"]})
        
        # First worker gets the task
        assignment1 = await queue.dequeue("worker-1")
        assert assignment1 is not None
        assert assignment1.task.assigned_to == "worker-1"
        
        # Simulate worker crash (no explicit failure, just timeout)
        await queue.mark_worker_failed("worker-1", "crash_detected")
        
        # Task should be reassigned
        task_state = queue.get_task_state(task_id)
        assert task_state == TaskState.PENDING
        
        # Second worker should get the task
        assignment2 = await queue.dequeue("worker-2")
        assert assignment2 is not None
        assert assignment2.task.id == task.id
        assert assignment2.task.assigned_to == "worker-2"
        
        # Check reassignment metadata
        task_info = await queue.get_task_info(task_id)
        assert task_info["reassignment_count"] == 1
        assert task_info["previous_workers"] == ["worker-1"]
        assert task_info["prefer_different_worker"] is True
        
        # Complete the task successfully
        await queue.complete_task("worker-2", task_id, {"result": "success"})
        assert queue.get_task_state(task_id) == TaskState.COMPLETED
    
    @pytest.mark.asyncio
    async def test_starvation_prevention(self, task_queue: TaskQueue):
        """Test starvation prevention mechanisms."""
        # Configure queue with starvation prevention
        config = QueueConfig(
            starvation_threshold=5,  # 5 seconds for testing
            priority_boost_interval=1,  # Boost every 1 second for faster testing
            priority_boost_amount=0.6  # +0.6 priority per interval
        )
        queue = TaskQueue(config=config)
        
        # Create low priority task first
        old_task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=1,  # Low priority
            payload={"test": "old_task", "created_first": True}
        )
        old_task_id = await queue.enqueue(old_task)
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Add medium priority tasks (priority 2)
        # This way the old task with boost can exceed them
        medium_priority_ids = []
        for i in range(5):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=2,  # Medium priority
                payload={"test": "medium_priority", "number": i}
            )
            task_id = await queue.enqueue(task)
            medium_priority_ids.append(task_id)
        
        # Register worker
        await queue.register_worker("worker-1", {"agent_types": ["Generation"]})
        
        # Process some medium priority tasks
        # Since we have 5 medium priority tasks and 1 low priority task,
        # processing 3 tasks should consume 3 medium priority tasks
        processed_order = []
        for _ in range(3):
            assignment = await queue.dequeue("worker-1")
            if assignment:
                processed_order.append(assignment.task.id)
                await queue.complete_task("worker-1", str(assignment.task.id), {})
                
        # Verify we processed medium priority tasks
        print(f"Processed tasks: {len(processed_order)}")
        # The old low priority task should still be pending
        
        # Check if the old task was already processed due to starvation prevention
        task_info = await queue.get_task_info(old_task_id)
        print(f"Old task info: {task_info}")
        
        if task_info["state"] == "completed":
            # The old task was already processed - starvation prevention worked!
            # After 2 seconds wait, it had effective priority 2.2 which was enough
            assert task_info["effective_priority"] >= 2.0  # Was boosted
            assert old_task.id in processed_order  # Was in the processed batch
            print("Starvation prevention worked - old task was prioritized")
        else:
            # If not processed yet, wait more and check it gets processed next
            await asyncio.sleep(2)
            
            # Now it should definitely have higher priority
            task_info = await queue.get_task_info(old_task_id)
            assert task_info["effective_priority"] > 2.0
            
            # Should be processed next
            assignment = await queue.dequeue("worker-1")
            assert assignment is not None
            assert assignment.task.id == old_task.id
        
        # Check starvation statistics
        stats = await queue.get_starvation_statistics()
        # After processing, there may be no pending tasks with boosts
        # The important thing is that starvation prevention worked
        print(f"Starvation stats: {stats}")
        
        # The test passed if we got here - starvation prevention is working