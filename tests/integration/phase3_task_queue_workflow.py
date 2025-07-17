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