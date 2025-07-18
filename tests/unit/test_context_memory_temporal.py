"""Unit tests for ContextMemory temporal guarantees."""
import asyncio
import json
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
import time
import pytest

from src.core.context_memory import (
    ContextMemory, StateUpdate, AgentOutput, 
    StorageResult, RetrievedState
)


class TestContextMemoryTemporalGuarantees:
    """Test ContextMemory temporal consistency and ordering guarantees."""
    
    @pytest.fixture
    def temp_storage_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Cleanup after test
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    async def initialized_memory(self, temp_storage_dir):
        """Create and initialize a ContextMemory instance."""
        memory = ContextMemory(storage_path=temp_storage_dir)
        await memory.initialize()
        return memory
    
    async def test_timestamp_ordering_guarantee(self, initialized_memory):
        """Test that writes are totally ordered by timestamp."""
        # Store multiple state updates with specific timestamps
        timestamps = []
        for i in range(5):
            timestamp = datetime.now(timezone.utc) + timedelta(microseconds=i * 1000)
            timestamps.append(timestamp)
            
            state_update = StateUpdate(
                timestamp=timestamp,
                update_type="periodic",
                system_statistics={"sequence": i},
                orchestration_state={"order": i}
            )
            
            await initialized_memory.store_state_update(state_update)
            # Small delay to ensure filesystem writes complete
            await asyncio.sleep(0.01)
        
        # Retrieve all states with temporal ordering
        all_states = await initialized_memory.retrieve_states_in_range(
            start_time=timestamps[0] - timedelta(seconds=1),
            end_time=timestamps[-1] + timedelta(seconds=1)
        )
        
        # Verify states are returned in timestamp order
        assert len(all_states) == 5
        for i in range(5):
            assert all_states[i]["system_statistics"]["sequence"] == i
    
    async def test_read_your_writes_guarantee(self, initialized_memory):
        """Test that agents always see their own writes immediately."""
        agent_id = "test_agent_123"
        
        # Agent writes data
        state_update = StateUpdate(
            timestamp=datetime.now(timezone.utc),
            update_type="periodic",
            system_statistics={"agent_id": agent_id, "value": 42},
            orchestration_state={},
            writer_id=agent_id
        )
        
        write_result = await initialized_memory.store_state_update(state_update)
        assert write_result.success
        
        # Agent reads immediately
        latest_state = await initialized_memory.retrieve_state_for_agent(
            agent_id=agent_id,
            request_type="latest"
        )
        
        assert latest_state is not None
        assert latest_state.content["system_state"]["value"] == 42
    
    async def test_monotonic_read_consistency(self, initialized_memory):
        """Test that successive reads never go backward in time."""
        # Store states with increasing values
        for i in range(3):
            state_update = StateUpdate(
                timestamp=datetime.now(timezone.utc),
                update_type="periodic",
                system_statistics={"counter": i},
                orchestration_state={"version": i}
            )
            await initialized_memory.store_state_update(state_update)
            await asyncio.sleep(0.1)  # Ensure temporal separation
        
        # Multiple reads should show monotonic progression
        last_version = -1
        for _ in range(5):
            state = await initialized_memory.retrieve_state("latest")
            if state:
                current_version = state.content["system_state"]["version"]
                assert current_version >= last_version
                last_version = current_version
            await asyncio.sleep(0.05)
    
    async def test_snapshot_isolation_for_queries(self, initialized_memory):
        """Test that queries see a consistent point-in-time view."""
        # Start a query transaction
        query_start = datetime.now(timezone.utc)
        
        # Begin reading state
        initial_state = await initialized_memory.retrieve_state("latest")
        initial_count = initial_state.content["statistics"].get("total_hypotheses", 0) if initial_state else 0
        
        # Concurrent write happens during query
        concurrent_update = StateUpdate(
            timestamp=datetime.now(timezone.utc),
            update_type="periodic",
            system_statistics={"total_hypotheses": initial_count + 100},
            orchestration_state={}
        )
        await initialized_memory.store_state_update(concurrent_update)
        
        # Continue reading with same query context
        query_state = await initialized_memory.retrieve_state_as_of(query_start)
        
        # Should see consistent view from query start time
        if query_state:
            assert query_state.content["statistics"].get("total_hypotheses", 0) == initial_count
    
    async def test_eventual_consistency_window(self, initialized_memory):
        """Test that updates become visible within 5 seconds."""
        write_time = datetime.now(timezone.utc)
        
        # Write an update
        state_update = StateUpdate(
            timestamp=write_time,
            update_type="periodic",
            system_statistics={"marker": "test_value"},
            orchestration_state={}
        )
        await initialized_memory.store_state_update(state_update)
        
        # Verify visibility within 5 seconds
        start_time = time.time()
        visible = False
        
        while time.time() - start_time < 5.0:
            state = await initialized_memory.retrieve_state("latest")
            if state and state.content["statistics"].get("marker") == "test_value":
                visible = True
                break
            await asyncio.sleep(0.1)
        
        assert visible, "Update not visible within 5-second consistency window"
        assert time.time() - start_time < 5.0
    
    async def test_concurrent_write_versioning(self, initialized_memory):
        """Test that concurrent writes maintain version numbers correctly."""
        # Simulate concurrent writes to same logical entity
        tasks = []
        
        async def write_with_delay(memory, agent_id, value):
            state_update = StateUpdate(
                timestamp=datetime.now(timezone.utc),
                update_type="periodic",
                system_statistics={"shared_counter": value},
                orchestration_state={"last_writer": agent_id},
                writer_id=agent_id
            )
            return await memory.store_state_update(state_update)
        
        # Launch concurrent writes
        for i in range(5):
            task = write_with_delay(initialized_memory, f"agent_{i}", i * 10)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # All writes should succeed
        assert all(r.success for r in results)
        
        # Verify version numbers are sequential
        versions = await initialized_memory.get_version_history(limit=5)
        assert len(versions) == 5
        
        # Check versions are incrementing
        for i in range(1, len(versions)):
            assert versions[i]["version"] > versions[i-1]["version"]
    
    async def test_checkpoint_exclusive_locking(self, initialized_memory):
        """Test that checkpoint creation uses exclusive locking."""
        # Track the order of checkpoint execution
        execution_order = []
        lock_acquired_times = []
        
        async def create_checkpoint_with_id(memory, checkpoint_num):
            state_update = StateUpdate(
                timestamp=datetime.now(timezone.utc),
                update_type="checkpoint",
                system_statistics={"checkpoint_num": checkpoint_num},
                orchestration_state={},
                checkpoint_data={"test_id": checkpoint_num}
            )
            
            # Add a small delay inside to make lock contention visible
            async def checkpoint_with_tracking():
                start_time = time.time()
                execution_order.append(f"start_{checkpoint_num}")
                checkpoint_id = await memory.create_checkpoint(state_update)
                execution_order.append(f"end_{checkpoint_num}")
                lock_acquired_times.append(start_time)
                return checkpoint_id
            
            return await checkpoint_with_tracking()
        
        # Launch concurrent checkpoint attempts
        tasks = []
        for i in range(3):
            task = create_checkpoint_with_id(initialized_memory, i)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # All checkpoints should succeed
        checkpoint_ids = [r for r in results if r is not None]
        assert len(checkpoint_ids) == 3
        
        # Verify that checkpoints don't overlap (exclusive locking)
        # Check execution order - starts and ends should not interleave
        # Valid patterns: start_0, end_0, start_1, end_1, start_2, end_2
        # Invalid patterns: start_0, start_1, end_0, end_1 (would indicate concurrent execution)
        
        # Count how many starts occur before their corresponding end
        in_progress = []
        max_concurrent = 0
        
        for event in execution_order:
            if event.startswith("start_"):
                in_progress.append(event)
                max_concurrent = max(max_concurrent, len(in_progress))
            elif event.startswith("end_"):
                checkpoint_num = event.split("_")[1]
                in_progress = [e for e in in_progress if not e.endswith(f"_{checkpoint_num}")]
        
        # With exclusive locking, max concurrent should be 1
        assert max_concurrent == 1, f"Expected exclusive access but found {max_concurrent} concurrent operations"
    
    async def test_causal_consistency_within_session(self, initialized_memory):
        """Test that operations within a session maintain causal relationships."""
        session_id = "test_session_123"
        
        # Create a causal chain of operations
        operations = []
        
        # Operation 1: Initial state
        op1 = StateUpdate(
            timestamp=datetime.now(timezone.utc),
            update_type="periodic",
            system_statistics={"step": 1, "value": 10},
            orchestration_state={"session_id": session_id}
        )
        result1 = await initialized_memory.store_state_update(op1)
        operations.append(("write", 1, result1))
        
        # Operation 2: Read state (establishes causal dependency)
        state = await initialized_memory.retrieve_state("latest")
        operations.append(("read", 2, state))
        
        # Operation 3: Update based on read
        if state:
            new_value = state.content["statistics"]["value"] + 5
            op3 = StateUpdate(
                timestamp=datetime.now(timezone.utc),
                update_type="periodic",
                system_statistics={"step": 3, "value": new_value},
                orchestration_state={"session_id": session_id}
            )
            result3 = await initialized_memory.store_state_update(op3)
            operations.append(("write", 3, result3))
        
        # Verify causal chain is preserved
        history = await initialized_memory.get_session_history(session_id)
        
        # Should see operations in causal order
        assert len(history) >= 2
        assert history[0]["step"] == 1
        assert history[-1]["step"] == 3
        assert history[-1]["value"] == 15  # Causally dependent on first write
    
    async def test_timestamp_precision_microseconds(self, initialized_memory):
        """Test that timestamps maintain microsecond precision."""
        # Write multiple updates in rapid succession
        timestamps = []
        
        for i in range(10):
            timestamp = datetime.now(timezone.utc)
            state_update = StateUpdate(
                timestamp=timestamp,
                update_type="periodic",
                system_statistics={"index": i},
                orchestration_state={}
            )
            
            result = await initialized_memory.store_state_update(state_update)
            assert result.success
            
            timestamps.append(timestamp)
            # Minimal delay to ensure microsecond differences
            await asyncio.sleep(0.0001)  # 100 microseconds
        
        # Retrieve and verify timestamp precision is preserved
        stored_timestamps = await initialized_memory.get_all_timestamps()
        
        # Check that microsecond precision is maintained
        for i, stored_ts in enumerate(stored_timestamps[:10]):
            # Timestamps should maintain microsecond precision
            assert stored_ts.microsecond is not None
            
            # Verify ordering is preserved at microsecond level
            if i > 0:
                time_diff = (stored_ts - stored_timestamps[i-1]).total_seconds()
                assert time_diff > 0  # Strictly increasing
    
    async def test_write_window_reservation(self, initialized_memory):
        """Test that agents can reserve write windows to minimize conflicts."""
        # Reserve write window for an agent
        agent_id = "high_priority_agent"
        reservation = await initialized_memory.reserve_write_window(
            agent_id=agent_id,
            duration_seconds=2
        )
        
        assert reservation is not None
        assert reservation["agent_id"] == agent_id
        
        # During reservation, other agents should wait or get deferred
        other_agent_id = "normal_agent"
        
        # Try concurrent write from another agent
        start_time = time.time()
        state_update = StateUpdate(
            timestamp=datetime.now(timezone.utc),
            update_type="periodic",
            system_statistics={"writer": other_agent_id},
            orchestration_state={},
            writer_id=other_agent_id
        )
        
        result = await initialized_memory.store_state_update(state_update)
        write_duration = time.time() - start_time
        
        # Write should succeed but may be deferred
        assert result.success
        
        # High priority agent writes should go through immediately
        priority_update = StateUpdate(
            timestamp=datetime.now(timezone.utc),
            update_type="periodic",
            system_statistics={"writer": agent_id},
            orchestration_state={},
            writer_id=agent_id
        )
        
        priority_start = time.time()
        priority_result = await initialized_memory.store_state_update(priority_update)
        priority_duration = time.time() - priority_start
        
        assert priority_result.success
        assert priority_duration < write_duration or priority_duration < 0.1  # Priority write is fast
    
    async def test_performance_sla_small_writes(self, initialized_memory):
        """Test that small write operations complete within 100ms."""
        # Measure small write performance
        durations = []
        
        for i in range(10):
            state_update = StateUpdate(
                timestamp=datetime.now(timezone.utc),
                update_type="periodic",
                system_statistics={"small_value": i},
                orchestration_state={"minimal": True}
            )
            
            start_time = time.time()
            result = await initialized_memory.store_state_update(state_update)
            duration = (time.time() - start_time) * 1000  # Convert to ms
            
            assert result.success
            durations.append(duration)
        
        # Check that 95% of writes are under 100ms
        sorted_durations = sorted(durations)
        p95_duration = sorted_durations[int(len(durations) * 0.95)]
        assert p95_duration < 100, f"P95 write latency {p95_duration}ms exceeds 100ms SLA"
    
    async def test_performance_sla_recent_reads(self, initialized_memory):
        """Test that recent data reads complete within 50ms."""
        # First, write some recent data
        state_update = StateUpdate(
            timestamp=datetime.now(timezone.utc),
            update_type="periodic",
            system_statistics={"test": "recent_data"},
            orchestration_state={}
        )
        await initialized_memory.store_state_update(state_update)
        
        # Measure read performance for recent data
        durations = []
        
        for _ in range(10):
            start_time = time.time()
            state = await initialized_memory.retrieve_state("latest")
            duration = (time.time() - start_time) * 1000  # Convert to ms
            
            assert state is not None
            durations.append(duration)
            
            await asyncio.sleep(0.01)  # Small delay between reads
        
        # Check that 95% of reads are under 50ms
        sorted_durations = sorted(durations)
        p95_duration = sorted_durations[int(len(durations) * 0.95)]
        assert p95_duration < 50, f"P95 read latency {p95_duration}ms exceeds 50ms SLA"
    
    async def test_retrieve_states_empty_range(self, initialized_memory):
        """Test retrieving states with no data in range."""
        # Query a future time range with no data
        future_start = datetime.now(timezone.utc) + timedelta(days=1)
        future_end = future_start + timedelta(days=1)
        
        states = await initialized_memory.retrieve_states_in_range(future_start, future_end)
        
        # Should return empty list
        assert states == []
    
    async def test_get_version_history_empty(self, initialized_memory):
        """Test getting version history with no data."""
        # Get version history on empty memory
        versions = await initialized_memory.get_version_history()
        
        # Should return empty list
        assert versions == []
    
    async def test_get_session_history_no_session(self, initialized_memory):
        """Test getting session history for non-existent session."""
        # Query non-existent session
        history = await initialized_memory.get_session_history("non_existent_session")
        
        # Should return empty list
        assert history == []
    
    async def test_retrieve_state_as_of_no_data(self, initialized_memory):
        """Test retrieving state as of timestamp with no prior data."""
        # Query state before any data exists
        past_time = datetime.now(timezone.utc) - timedelta(days=1)
        
        state = await initialized_memory.retrieve_state_as_of(past_time)
        
        # Should return None
        assert state is None
    
    async def test_retrieve_state_for_agent_no_writes(self, initialized_memory):
        """Test retrieving state for agent with no agent-specific writes."""
        # First write some general data
        state_update = StateUpdate(
            timestamp=datetime.now(timezone.utc),
            update_type="periodic",
            system_statistics={"general": "data"},
            orchestration_state={"test": True}
        )
        await initialized_memory.store_state_update(state_update)
        
        # Try to retrieve for a specific agent that hasn't written
        state = await initialized_memory.retrieve_state_for_agent(
            agent_id="new_agent",
            request_type="latest"
        )
        
        # Should return the general latest state
        assert state is not None
        assert state.content["statistics"]["general"] == "data"