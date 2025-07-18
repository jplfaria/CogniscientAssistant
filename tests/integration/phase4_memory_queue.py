"""Integration tests for Phase 4: Context Memory with Task Queue.

These tests validate that context memory works correctly with the task queue
for storing and retrieving state across AI Co-Scientist workflows.
"""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any
import uuid

import pytest

from src.core.context_memory import (
    ContextMemory, StateUpdate, AgentOutput, MetaReviewStorage,
    StorageResult, RetrievedState, FeedbackData, RecoveryState
)
from src.core.models import Task, TaskState, TaskType
from src.core.task_queue import TaskQueue, QueueConfig


class TestMemoryQueueIntegration:
    """Test context memory integration with task queue."""
    
    @pytest.mark.asyncio
    async def test_memory_storage_and_retrieval(self, temp_dir: Path):
        """Test basic memory storage and retrieval operations."""
        # Create memory with custom storage path
        memory = ContextMemory(storage_path=temp_dir / "memory")
        await memory.initialize()
        
        # Store a state update
        state_update = StateUpdate(
            timestamp=datetime.now(timezone.utc),
            update_type="periodic",
            system_statistics={
                "total_hypotheses": 10,
                "total_tasks": 25,
                "tournament_progress": 0.45
            },
            orchestration_state={
                "current_phase": "hypothesis_generation",
                "active_agents": ["Generation", "Reflection"],
                "resource_allocation": {"Generation": 0.6, "Reflection": 0.4}
            }
        )
        
        result = await memory.store_state_update(state_update)
        assert result.success is True
        assert result.storage_path is not None
        
        # Retrieve latest state
        retrieved = await memory.retrieve_state("latest")
        assert retrieved is not None
        assert retrieved.request_type == "latest"
        assert retrieved.content is not None
        
        # Verify content matches what was stored
        content = retrieved.content
        assert content["system_state"]["current_phase"] == "hypothesis_generation"
        assert content["statistics"]["total_hypotheses"] == 10
        assert content["system_state"]["tournament_progress"] == 0.45
    
    @pytest.mark.asyncio
    async def test_context_thread_isolation(self, temp_dir: Path):
        """Test that different execution threads maintain isolated context."""
        # Create shared memory instance
        memory = ContextMemory(storage_path=temp_dir / "shared_memory")
        await memory.initialize()
        
        # Start new iteration for thread 1
        iteration1 = await memory.start_new_iteration()
        
        # Store data in thread 1 context
        thread1_data = StateUpdate(
            timestamp=datetime.now(timezone.utc),
            update_type="periodic",
            system_statistics={"thread_id": "thread_1", "task_count": 5},
            orchestration_state={"phase": "generation"},
            writer_id="thread_1"
        )
        result1 = await memory.store_state_update(thread1_data)
        assert result1.success is True
        
        # Complete iteration 1
        await memory.complete_iteration(iteration1, {"total_tasks": 5})
        
        # Start new iteration for thread 2
        iteration2 = await memory.start_new_iteration()
        
        # Store data in thread 2 context
        thread2_data = StateUpdate(
            timestamp=datetime.now(timezone.utc),
            update_type="periodic",
            system_statistics={"thread_id": "thread_2", "task_count": 10},
            orchestration_state={"phase": "reflection"},
            writer_id="thread_2"
        )
        result2 = await memory.store_state_update(thread2_data)
        assert result2.success is True
        
        # Retrieve latest should get thread 2 data
        latest = await memory.retrieve_state("latest")
        assert latest.content["statistics"]["thread_id"] == "thread_2"
        assert latest.content["statistics"]["task_count"] == 10
        
        # Verify we can still access iteration-specific data
        iter1_info = await memory.get_iteration_info(iteration1)
        assert iter1_info["status"] == "completed"
        assert iter1_info["summary"]["total_tasks"] == 5
        
        iter2_info = await memory.get_iteration_info(iteration2)
        assert iter2_info["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_checkpoint_creation_and_recovery(self, temp_dir: Path):
        """Test checkpoint creation and recovery functionality."""
        # Create memory and task queue
        memory = ContextMemory(storage_path=temp_dir / "memory")
        await memory.initialize()
        
        queue_config = QueueConfig(persistence_path=str(temp_dir / "queue_state.json"))
        queue = TaskQueue(config=queue_config)
        
        # Start an iteration
        iteration = await memory.start_new_iteration()
        
        # Create some tasks and enqueue them
        tasks_created = []
        for i in range(5):
            task = Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=2,
                payload={"hypothesis_num": i, "research_goal": "Test checkpoint"}
            )
            task_id = await queue.enqueue(task)
            tasks_created.append(task_id)
        
        # Register worker and process some tasks
        await queue.register_worker("worker-1", {"agent_types": ["Generation"]})
        
        # Process 2 tasks
        completed_tasks = []
        for _ in range(2):
            assignment = await queue.dequeue("worker-1")
            if assignment:
                await queue.complete_task("worker-1", str(assignment.task.id), {"result": "completed"})
                completed_tasks.append(str(assignment.task.id))
        
        # Create checkpoint with current state
        checkpoint_data = StateUpdate(
            timestamp=datetime.now(timezone.utc),
            update_type="checkpoint",
            system_statistics={
                "total_tasks": len(tasks_created),
                "completed_tasks": len(completed_tasks),
                "pending_tasks": len(tasks_created) - len(completed_tasks)
            },
            orchestration_state={
                "active_iteration": iteration,
                "queue_size": queue.size(),
                "active_workers": 1
            },
            checkpoint_data={
                "in_flight_tasks": tasks_created,
                "completed_tasks": completed_tasks,
                "queue_state": await queue.export_state()
            }
        )
        
        checkpoint_id = await memory.create_checkpoint(checkpoint_data)
        assert checkpoint_id is not None
        
        # Simulate system restart - create new instances
        memory2 = ContextMemory(storage_path=temp_dir / "memory")
        await memory2.initialize()
        
        queue2 = TaskQueue(config=queue_config)
        
        # Recover from checkpoint
        recovery_state = await memory2.recover_from_checkpoint(checkpoint_id)
        assert recovery_state is not None
        assert recovery_state.data_integrity["valid"] is True
        assert len(recovery_state.active_tasks) == 5
        assert recovery_state.system_configuration["active_iteration"] == iteration
        
        # Restore queue state
        if "queue_state" in checkpoint_data.checkpoint_data:
            await queue2.import_state(checkpoint_data.checkpoint_data["queue_state"])
        
        # Verify queue has pending tasks
        assert queue2.size() == 3  # 5 total - 2 completed
        
        # Verify we can continue processing
        await queue2.register_worker("worker-2", {"agent_types": ["Generation"]})
        assignment = await queue2.dequeue("worker-2")
        assert assignment is not None
        assert assignment.task.payload["research_goal"] == "Test checkpoint"
    
    @pytest.mark.asyncio
    async def test_concurrent_write_conflict_resolution(self, temp_dir: Path):
        """Test handling of concurrent writes with conflict resolution."""
        # Create shared memory instance
        memory = ContextMemory(storage_path=temp_dir / "memory")
        await memory.initialize()
        
        # Start an iteration
        await memory.start_new_iteration()
        
        # Simulate concurrent writes from different components
        timestamp = datetime.now(timezone.utc)
        
        async def write_state(writer_id: str, value: int):
            """Simulate a component writing state."""
            state = StateUpdate(
                timestamp=timestamp,  # Same timestamp to force conflict
                update_type="periodic",
                system_statistics={"value": value, "writer": writer_id},
                orchestration_state={"last_writer": writer_id},
                writer_id=writer_id
            )
            return await memory.store_state_update(state)
        
        # Execute concurrent writes
        results = await asyncio.gather(
            write_state("supervisor_1", 100),
            write_state("supervisor_2", 200),
            write_state("supervisor_3", 300),
            return_exceptions=True
        )
        
        # All writes should succeed (conflict resolution creates unique filenames)
        successful_writes = [r for r in results if isinstance(r, StorageResult) and r.success]
        assert len(successful_writes) == 3
        
        # Verify all writes were stored (check the iteration directory)
        iteration_dir = memory.storage_path / "iterations" / "iteration_001"
        state_files = list(iteration_dir.glob("system_state_*.json"))
        assert len(state_files) >= 3  # At least our 3 concurrent writes
        
        # Read and verify each file has unique content
        writers_found = set()
        for state_file in state_files:
            with open(state_file, 'r') as f:
                data = json.load(f)
                if "writer_id" in data:
                    writers_found.add(data["writer_id"])
        
        # Should find all our writers
        assert "supervisor_1" in writers_found
        assert "supervisor_2" in writers_found
        assert "supervisor_3" in writers_found
    
    @pytest.mark.asyncio
    async def test_memory_version_history(self, temp_dir: Path):
        """Test version history tracking for memory updates."""
        memory = ContextMemory(storage_path=temp_dir / "memory")
        await memory.initialize()
        
        # Start iteration
        iteration = await memory.start_new_iteration()
        
        # Store multiple versions of state
        versions = []
        for i in range(5):
            state = StateUpdate(
                timestamp=datetime.now(timezone.utc),
                update_type="periodic",
                system_statistics={
                    "version": i + 1,
                    "total_hypotheses": 10 * (i + 1),
                    "iteration_progress": 0.2 * (i + 1)
                },
                orchestration_state={
                    "phase": f"phase_{i + 1}",
                    "active_agents": i + 1
                }
            )
            result = await memory.store_state_update(state)
            assert result.success is True
            versions.append(result.storage_path)
            
            # Small delay to ensure different timestamps
            await asyncio.sleep(0.01)
        
        # Verify we can access version history
        iteration_dir = memory.storage_path / "iterations" / f"iteration_{iteration:03d}"
        state_files = sorted(iteration_dir.glob("system_state_*.json"))
        assert len(state_files) >= 5
        
        # Verify chronological ordering
        timestamps = []
        for state_file in state_files:
            with open(state_file, 'r') as f:
                data = json.load(f)
                timestamps.append(datetime.fromisoformat(data["timestamp"]))
        
        # Timestamps should be in ascending order
        assert timestamps == sorted(timestamps)
        
        # Verify latest retrieval gets most recent version
        latest = await memory.retrieve_state("latest")
        assert latest.content["statistics"]["version"] == 5
        assert latest.content["statistics"]["iteration_progress"] == 1.0
    
    @pytest.mark.asyncio
    async def test_storage_overflow_handling(self, temp_dir: Path):
        """Test handling when storage approaches capacity limits."""
        # Create memory with very small storage limit
        memory = ContextMemory(
            storage_path=temp_dir / "memory",
            max_storage_gb=0.0001  # 100KB limit for testing
        )
        await memory.initialize()
        
        # Try to store large amounts of data
        large_data = {
            "data": "x" * 10000,  # 10KB string
            "nested": {
                "level1": {"level2": {"level3": ["item"] * 100}}
            }
        }
        
        stored_count = 0
        failed_count = 0
        
        for i in range(20):  # Try to store 200KB of data
            state = StateUpdate(
                timestamp=datetime.now(timezone.utc),
                update_type="periodic",
                system_statistics=large_data.copy(),
                orchestration_state=large_data.copy()
            )
            
            result = await memory.store_state_update(state)
            if result.success:
                stored_count += 1
            else:
                failed_count += 1
        
        # Should have stored some but not all due to size limit
        assert stored_count > 0
        assert stored_count < 20  # Shouldn't store all due to limit
        
        # Verify we can still retrieve data
        latest = await memory.retrieve_state("latest")
        assert latest is not None
    
    @pytest.mark.asyncio
    async def test_agent_memory_integration(self, temp_dir: Path):
        """Test memory integration with agent outputs (may fail)."""
        memory = ContextMemory(storage_path=temp_dir / "memory")
        await memory.initialize()
        
        # Start iteration
        await memory.start_new_iteration()
        
        # Store agent outputs
        agents = ["Generation", "Reflection", "Ranking", "Evolution"]
        for agent_type in agents:
            output = AgentOutput(
                agent_type=agent_type,
                task_id=f"task_{agent_type.lower()}_001",
                timestamp=datetime.now(timezone.utc),
                results={
                    "success": True,
                    "output": f"Result from {agent_type} agent",
                    "metrics": {"quality": 0.85, "time_ms": 1500}
                },
                state_data={
                    "internal_state": f"{agent_type}_state",
                    "memory_usage_mb": 256
                }
            )
            
            result = await memory.store_agent_output(output)
            assert result.success is True
        
        # Verify agent outputs are indexed
        assert len(memory._component_index) >= len(agents)
        for agent_type in agents:
            assert agent_type in memory._component_index
            assert len(memory._component_index[agent_type]) >= 1
    
    @pytest.mark.asyncio 
    async def test_memory_retrieval_performance(self, temp_dir: Path):
        """Test memory retrieval performance with large datasets (may fail)."""
        memory = ContextMemory(storage_path=temp_dir / "memory")
        await memory.initialize()
        
        # Create multiple iterations with lots of data
        for iter_num in range(5):
            await memory.start_new_iteration()
            
            # Store many state updates
            for i in range(20):
                state = StateUpdate(
                    timestamp=datetime.now(timezone.utc),
                    update_type="periodic",
                    system_statistics={
                        "iteration": iter_num + 1,
                        "update": i + 1,
                        "data": {"nested": {"values": list(range(100))}}
                    },
                    orchestration_state={
                        "phase": f"phase_{i}",
                        "metrics": {"m1": i * 1.5, "m2": i * 2.5}
                    }
                )
                await memory.store_state_update(state)
            
            # Complete iteration
            await memory.complete_iteration(
                iter_num + 1,
                {"total_updates": 20, "status": "completed"}
            )
        
        # Measure retrieval performance
        import time
        
        # Test latest retrieval
        start = time.time()
        latest = await memory.retrieve_state("latest")
        retrieval_time = time.time() - start
        
        assert latest is not None
        assert retrieval_time < 0.1  # Should retrieve in under 100ms
        
        # Test listing iterations
        start = time.time()
        iterations = await memory.list_iterations()
        list_time = time.time() - start
        
        assert len(iterations) == 5
        assert list_time < 0.5  # Should list in under 500ms
    
    @pytest.mark.asyncio
    async def test_periodic_archive_rotation(self, temp_dir: Path):
        """Test automatic archival of old data (may fail)."""
        # Create memory with short retention
        memory = ContextMemory(
            storage_path=temp_dir / "memory",
            retention_days=0  # Archive immediately for testing
        )
        await memory.initialize()
        
        # Create old iteration
        iter1 = await memory.start_new_iteration()
        
        # Store some data
        state = StateUpdate(
            timestamp=datetime.now(timezone.utc),
            update_type="periodic",
            system_statistics={"iteration": 1, "status": "old"},
            orchestration_state={"phase": "completed"}
        )
        await memory.store_state_update(state)
        
        # Complete the iteration
        await memory.complete_iteration(iter1, {"status": "done"})
        
        # Create new iteration
        iter2 = await memory.start_new_iteration()
        
        # Trigger archive process (normally would be scheduled)
        await memory.archive_old_data()
        
        # Verify old iteration was archived
        archive_dir = memory.storage_path / "archive"
        assert archive_dir.exists()
        
        archived_files = list(archive_dir.glob("iteration_001_*.tar.gz"))
        assert len(archived_files) == 1
        
        # Verify active iteration is not archived
        active_dir = memory.storage_path / "iterations" / f"iteration_{iter2:03d}"
        assert active_dir.exists()
    
    @pytest.mark.asyncio
    async def test_garbage_collection(self, temp_dir: Path):
        """Test garbage collection of orphaned data (may fail)."""
        memory = ContextMemory(storage_path=temp_dir / "memory")
        await memory.initialize()
        
        # Create some orphaned files manually
        orphan_dir = memory.storage_path / "iterations" / "orphaned_data"
        orphan_dir.mkdir(parents=True)
        
        orphan_file = orphan_dir / "orphan.json"
        with open(orphan_file, 'w') as f:
            json.dump({"orphaned": True}, f)
        
        # Create valid iteration
        await memory.start_new_iteration()
        
        # Run garbage collection
        collected = await memory.collect_garbage()
        
        # Should identify and clean orphaned data
        assert collected["orphaned_directories"] >= 1  # The orphaned_data directory
        assert not orphan_file.exists()
        assert not orphan_dir.exists()  # Directory should be removed too
        
        # Valid iteration should remain
        valid_dir = memory.storage_path / "iterations" / "iteration_001"
        assert valid_dir.exists()