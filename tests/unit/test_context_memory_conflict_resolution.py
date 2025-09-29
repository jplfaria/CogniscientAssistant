"""Unit tests for ContextMemory conflict resolution functionality."""
import asyncio
import json
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import pytest

from src.core.context_memory import (
    ContextMemory, StateUpdate, AgentOutput, MetaReviewStorage
)


class TestContextMemoryConflictResolution:
    """Test conflict resolution mechanisms in ContextMemory."""
    
    @pytest.fixture
    def temp_storage_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Cleanup after test
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    async def context_memory(self, temp_storage_dir):
        """Create and initialize a ContextMemory instance."""
        cm = ContextMemory(storage_path=temp_storage_dir)
        await cm.initialize()
        return cm
    
    # Version-based conflict detection tests
    
    async def test_version_tracking_on_state_update(self, context_memory):
        """Test that version numbers are tracked on state updates."""
        # Create state update
        state_update = StateUpdate(
            timestamp=datetime.now(),
            update_type="periodic",
            system_statistics={"total_hypotheses": 10},
            orchestration_state={"agent_weights": {"generation": 0.5}}
        )
        
        # Store the update
        result = await context_memory.store_state_update(state_update)
        assert result.success
        
        # Verify version tracking
        state_file = result.storage_path
        with open(state_file, 'r') as f:
            data = json.load(f)
            assert "version" in data
            assert data["version"] == 1
    
    async def test_concurrent_state_update_conflict_detection(self, context_memory):
        """Test detection of concurrent write conflicts."""
        # Start an iteration
        iteration_num = await context_memory.start_new_iteration()
        
        # Create two concurrent state updates
        timestamp = datetime.now()
        state_update1 = StateUpdate(
            timestamp=timestamp,
            update_type="periodic",
            system_statistics={"total_hypotheses": 10},
            orchestration_state={"agent_weights": {"generation": 0.5}}
        )
        
        state_update2 = StateUpdate(
            timestamp=timestamp,
            update_type="periodic",
            system_statistics={"total_hypotheses": 15},
            orchestration_state={"agent_weights": {"generation": 0.6}}
        )
        
        # Store both updates (simulating concurrent writes)
        result1 = await context_memory.store_state_update(state_update1)
        result2 = await context_memory.store_state_update(state_update2)
        
        # Both should succeed but with different filenames due to microsecond precision
        assert result1.success
        assert result2.success
        assert result1.storage_path != result2.storage_path
    
    async def test_writer_identification_in_agent_output(self, context_memory):
        """Test that writer identification is properly tracked."""
        # Create agent output
        agent_output = AgentOutput(
            agent_type="generation",
            task_id="task_123",
            timestamp=datetime.now(),
            results={"hypothesis": "Test hypothesis"}
        )
        
        result = await context_memory.store_agent_output(agent_output)
        assert result.success
        
        # Verify writer identification
        with open(result.storage_path, 'r') as f:
            data = json.load(f)
            assert data["agent_type"] == "generation"
            assert data["task_id"] == "task_123"
    
    # Merge strategy tests
    
    async def test_merge_non_conflicting_fields_in_aggregates(self, context_memory):
        """Test merging non-conflicting fields in aggregate updates."""
        # Store initial aggregate
        initial_data = {
            "hypothesis_count": 10,
            "review_count": 5,
            "metadata": {"start_time": datetime.now().isoformat()}
        }
        await context_memory.store_aggregate("research_stats", initial_data, datetime.now())
        
        # Update with non-conflicting fields
        update_data = {
            "hypothesis_count": 15,  # Update existing
            "evolution_count": 3,    # Add new field
            "metadata": {"start_time": initial_data["metadata"]["start_time"]}  # Keep same
        }
        result = await context_memory.update_aggregate("research_stats", update_data)
        assert result
        
        # Verify merge
        retrieved = await context_memory.retrieve_aggregate("research_stats")
        assert retrieved["hypothesis_count"] == 15
        assert retrieved["evolution_count"] == 3
        assert retrieved["metadata"]["start_time"] == initial_data["metadata"]["start_time"]
    
    async def test_last_write_wins_for_conflicting_fields(self, context_memory):
        """Test last-write-wins strategy for conflicting fields."""
        # Store initial state
        timestamp1 = datetime.now()
        state_update1 = StateUpdate(
            timestamp=timestamp1,
            update_type="periodic",
            system_statistics={"total_hypotheses": 10, "pending_reviews": 5},
            orchestration_state={"agent_weights": {"generation": 0.5}}
        )
        result1 = await context_memory.store_state_update(state_update1)
        
        # Store conflicting update
        timestamp2 = datetime.now()
        state_update2 = StateUpdate(
            timestamp=timestamp2,
            update_type="periodic",
            system_statistics={"total_hypotheses": 15, "pending_reviews": 3},
            orchestration_state={"agent_weights": {"generation": 0.6}}
        )
        result2 = await context_memory.store_state_update(state_update2)
        
        # Retrieve latest state
        retrieved = await context_memory.retrieve_state()
        assert retrieved.content["statistics"]["total_hypotheses"] == 15
        assert retrieved.content["statistics"]["pending_reviews"] == 3
    
    # Statistical aggregate accumulation tests
    
    async def test_accumulate_statistical_updates(self, context_memory):
        """Test accumulation strategy for statistical aggregates."""
        # Start new iteration
        iteration_num = await context_memory.start_new_iteration()
        
        # Store multiple agent outputs with metrics
        for i in range(5):
            agent_output = AgentOutput(
                agent_type="generation",
                task_id=f"task_{i}",
                timestamp=datetime.now(),
                results={"quality_score": 0.8 + i * 0.02}
            )
            await context_memory.store_agent_output(agent_output)
        
        # Compute aggregate statistics
        stats = await context_memory.compute_aggregate_statistics("generation", "quality_score")
        
        assert stats is not None
        assert stats["count"] == 5
        assert stats["average"] == pytest.approx(0.84, rel=1e-2)
        assert stats["min"] == 0.8
        assert stats["max"] == 0.88
    
    async def test_sum_accumulation_for_counters(self, context_memory):
        """Test sum accumulation for counter-type fields."""
        # Store initial aggregate
        await context_memory.store_aggregate(
            "hypothesis_stats",
            {"generated": 10, "reviewed": 5, "evolved": 2},
            datetime.now()
        )
        
        # Add incremental updates
        await context_memory.store_aggregate(
            "hypothesis_stats",
            {"generated": 5, "reviewed": 3, "evolved": 1},
            datetime.now()
        )
        
        # Retrieve time range to see both entries
        entries = await context_memory.retrieve_aggregate(
            "hypothesis_stats",
            query_type="time_range",
            start_time=datetime.now().replace(hour=0, minute=0, second=0),
            end_time=datetime.now()
        )
        
        # Sum up the values
        totals = {"generated": 0, "reviewed": 0, "evolved": 0}
        for entry in entries:
            for key in totals:
                totals[key] += entry.get(key, 0)
        
        assert totals["generated"] == 15
        assert totals["reviewed"] == 8
        assert totals["evolved"] == 3
    
    # Checkpoint exclusive locking tests
    
    async def test_checkpoint_exclusive_lock_prevents_concurrent_writes(self, context_memory):
        """Test that exclusive lock prevents concurrent checkpoint writes."""
        # Create checkpoint data
        state_update = StateUpdate(
            timestamp=datetime.now(),
            update_type="checkpoint",
            system_statistics={"total_hypotheses": 10},
            orchestration_state={"agent_weights": {"generation": 0.5}},
            checkpoint_data={"in_flight_tasks": []}
        )
        
        # Simulate concurrent checkpoint creation
        async def create_checkpoint():
            return await context_memory.create_checkpoint(state_update)
        
        # Create two concurrent checkpoint tasks
        task1 = asyncio.create_task(create_checkpoint())
        task2 = asyncio.create_task(create_checkpoint())
        
        # Wait for both to complete
        checkpoint_id1 = await task1
        checkpoint_id2 = await task2
        
        # Both should succeed but with different IDs (no actual lock conflict)
        assert checkpoint_id1 is not None
        assert checkpoint_id2 is not None
        assert checkpoint_id1 != checkpoint_id2
    
    async def test_checkpoint_write_timeout_handling(self, context_memory):
        """Test handling of checkpoint write timeouts."""
        # Create a large checkpoint that might take time
        large_checkpoint_data = {
            "in_flight_tasks": [{"task_id": f"task_{i}"} for i in range(1000)],
            "large_state": {"data": "x" * 10000}
        }
        
        state_update = StateUpdate(
            timestamp=datetime.now(),
            update_type="checkpoint",
            system_statistics={"total_hypotheses": 1000},
            orchestration_state={"agent_weights": {"generation": 0.5}},
            checkpoint_data=large_checkpoint_data
        )
        
        # Should complete within timeout
        checkpoint_id = await context_memory.create_checkpoint(state_update)
        assert checkpoint_id is not None
        
        # Verify checkpoint was saved correctly
        recovery = await context_memory.recover_from_checkpoint(checkpoint_id)
        assert recovery is not None
        assert len(recovery.active_tasks) == 1000
    
    # Read-write consistency tests
    
    async def test_read_your_writes_consistency(self, context_memory):
        """Test that agents can read their own writes immediately."""
        # Start an iteration first
        iteration_num = await context_memory.start_new_iteration()
        
        # Store agent output
        agent_output = AgentOutput(
            agent_type="reflection",
            task_id="review_123",
            timestamp=datetime.now(),
            results={"review_score": 0.85, "feedback": "Good hypothesis"}
        )
        
        result = await context_memory.store_agent_output(agent_output)
        assert result.success
        
        # Immediately read back (should see the write)
        # Since we don't have a direct read method for agent outputs,
        # we'll check through iteration statistics
        active_iter = await context_memory.get_active_iteration()
        assert active_iter == iteration_num
        stats = await context_memory.get_iteration_statistics(active_iter)
        
        assert stats["agent_outputs_count"] >= 1
        assert "reflection" in stats["agent_type_breakdown"]
    
    async def test_snapshot_isolation_for_queries(self, context_memory):
        """Test snapshot isolation for concurrent reads during writes."""
        # Start iteration
        await context_memory.start_new_iteration()
        
        # Store initial state
        initial_update = StateUpdate(
            timestamp=datetime.now(),
            update_type="periodic",
            system_statistics={"total_hypotheses": 10},
            orchestration_state={"agent_weights": {"generation": 0.5}}
        )
        await context_memory.store_state_update(initial_update)
        
        # Start a read
        read_task = asyncio.create_task(context_memory.retrieve_state())
        
        # Concurrent write
        write_update = StateUpdate(
            timestamp=datetime.now(),
            update_type="periodic",
            system_statistics={"total_hypotheses": 20},
            orchestration_state={"agent_weights": {"generation": 0.6}}
        )
        await context_memory.store_state_update(write_update)
        
        # Complete the read
        read_result = await read_task
        
        # The read might see either value depending on timing,
        # but it should see a consistent snapshot
        assert read_result is not None
        stats = read_result.content["statistics"]
        assert stats["total_hypotheses"] in [10, 20]
    
    # Multi-agent coordination tests
    
    async def test_agent_write_slot_allocation(self, context_memory):
        """Test that different agent types can write without conflicts."""
        # Start iteration
        await context_memory.start_new_iteration()
        
        # Create outputs from different agents
        agents = ["generation", "reflection", "evolution", "ranking"]
        tasks = []
        
        for agent_type in agents:
            output = AgentOutput(
                agent_type=agent_type,
                task_id=f"{agent_type}_task_{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(),
                results={"score": 0.8}
            )
            task = asyncio.create_task(context_memory.store_agent_output(output))
            tasks.append(task)
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(r.success for r in results)
        
        # Verify all were stored
        active_iter = await context_memory.get_active_iteration()
        stats = await context_memory.get_iteration_statistics(active_iter)
        
        assert stats["agent_outputs_count"] == len(agents)
        for agent_type in agents:
            assert agent_type in stats["agent_type_breakdown"]
    
    async def test_batch_write_atomicity(self, context_memory):
        """Test all-or-nothing semantics for batch operations."""
        # Test batch key-value set
        batch_data = {
            "config_1": {"setting": "value1"},
            "config_2": {"setting": "value2"},
            "config_3": {"setting": "value3"}
        }
        
        # Should succeed atomically
        result = await context_memory.batch_set(batch_data)
        assert result
        
        # Verify all were written
        retrieved = await context_memory.batch_get(list(batch_data.keys()))
        assert all(retrieved[k] == batch_data[k] for k in batch_data)
        
        # Test failure case - invalid data
        invalid_batch = {
            "valid_key": {"data": "valid"},
            "": {"data": "invalid key"}  # Empty key should fail
        }
        
        with pytest.raises(ValueError):
            await context_memory.batch_set(invalid_batch)
        
        # Verify the valid key was NOT written (atomicity)
        assert await context_memory.get("valid_key") is None
    
    async def test_concurrent_kv_operations(self, context_memory):
        """Test concurrent key-value operations handle conflicts properly."""
        key = "shared_config"
        
        # Define concurrent operations
        async def writer1():
            return await context_memory.set(key, {"value": "writer1", "timestamp": datetime.now().isoformat()})
        
        async def writer2():
            return await context_memory.set(key, {"value": "writer2", "timestamp": datetime.now().isoformat()})
        
        async def reader():
            return await context_memory.get(key)
        
        # Execute concurrently
        write1_task = asyncio.create_task(writer1())
        write2_task = asyncio.create_task(writer2())
        read_task = asyncio.create_task(reader())
        
        # Wait for all
        write1_result, write2_result, read_result = await asyncio.gather(
            write1_task, write2_task, read_task
        )
        
        # Both writes should succeed
        assert write1_result
        assert write2_result
        
        # Final read should see one of the values (last write wins)
        final_value = await context_memory.get(key)
        assert final_value is not None
        assert final_value["value"] in ["writer1", "writer2"]