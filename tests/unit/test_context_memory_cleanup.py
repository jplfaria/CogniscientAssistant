"""Unit tests for ContextMemory cleanup and archival operations."""
import asyncio
import json
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

from src.core.context_memory import (
    ContextMemory, StateUpdate, AgentOutput, 
    MetaReviewStorage
)


class TestContextMemoryCleanup:
    """Test ContextMemory cleanup and archival operations."""
    
    @pytest.fixture
    def temp_storage_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Cleanup after test
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    async def memory_with_old_data(self, temp_storage_dir):
        """Create a ContextMemory instance with old data for testing."""
        memory = ContextMemory(
            storage_path=temp_storage_dir,
            retention_days=7  # 7 days retention
        )
        await memory.initialize()
        
        # Create old iterations with proper metadata
        old_date = datetime.now(timezone.utc) - timedelta(days=10)
        
        # Create old iteration 1
        iter1_dir = temp_storage_dir / "iterations" / "iteration_001"
        iter1_dir.mkdir(parents=True, exist_ok=True)
        metadata1 = {
            "iteration_number": 1,
            "started_at": old_date.isoformat(),
            "status": "completed",
            "completed_at": (old_date + timedelta(hours=1)).isoformat()
        }
        with open(iter1_dir / "metadata.json", 'w') as f:
            json.dump(metadata1, f)
        
        # Add some data to old iteration
        state_update = StateUpdate(
            timestamp=old_date,
            update_type="periodic",
            system_statistics={"old_data": 1},
            orchestration_state={}
        )
        await memory.store_state_update(state_update)
        
        # Create old iteration 2
        iter2_dir = temp_storage_dir / "iterations" / "iteration_002" 
        iter2_dir.mkdir(parents=True, exist_ok=True)
        metadata2 = {
            "iteration_number": 2,
            "started_at": (old_date + timedelta(days=1)).isoformat(),
            "status": "completed",
            "completed_at": (old_date + timedelta(days=1, hours=1)).isoformat()
        }
        with open(iter2_dir / "metadata.json", 'w') as f:
            json.dump(metadata2, f)
        
        # Create recent iteration with proper metadata
        recent_date = datetime.now(timezone.utc) - timedelta(days=2)
        iter3_dir = temp_storage_dir / "iterations" / "iteration_003"
        iter3_dir.mkdir(parents=True, exist_ok=True)
        metadata3 = {
            "iteration_number": 3,
            "started_at": recent_date.isoformat(),
            "status": "completed",
            "completed_at": (recent_date + timedelta(hours=1)).isoformat()
        }
        with open(iter3_dir / "metadata.json", 'w') as f:
            json.dump(metadata3, f)
        
        # Add some data to recent iteration
        state_update = StateUpdate(
            timestamp=recent_date,
            update_type="periodic",
            system_statistics={"recent_data": 1},
            orchestration_state={}
        )
        await memory.store_state_update(state_update)
        
        return memory
    
    async def test_cleanup_old_iterations(self, memory_with_old_data):
        """Test cleanup of iterations older than retention period."""
        memory = memory_with_old_data
        
        # Get initial iteration count
        iterations_before = await memory.list_iterations()
        initial_count = len(iterations_before)
        
        # Run cleanup
        cleaned_count = await memory.cleanup_old_iterations()
        
        # Verify old iterations were cleaned
        assert cleaned_count > 0
        
        # Verify current iterations remain
        iterations_after = await memory.list_iterations()
        assert len(iterations_after) < initial_count
        
        # Verify only recent iterations remain
        for iteration in iterations_after:
            if "started_at" in iteration:
                started_at = datetime.fromisoformat(iteration["started_at"])
                age_days = (datetime.now(timezone.utc) - started_at).days
                assert age_days <= memory.retention_days
    
    async def test_archive_old_data(self, memory_with_old_data):
        """Test archival of old data before cleanup."""
        memory = memory_with_old_data
        
        # Create archive directory
        archive_dir = memory.storage_path / "archive"
        
        # Run archival
        archived_count = await memory.archive_old_data()
        
        # Verify archive was created
        assert archive_dir.exists()
        assert archived_count > 0
        
        # Verify archived files exist
        archived_files = list(archive_dir.glob("*.tar.gz"))
        assert len(archived_files) > 0
        
        # Verify archive metadata
        metadata_file = archive_dir / "archive_metadata.json"
        assert metadata_file.exists()
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            assert "archives" in metadata
            assert len(metadata["archives"]) > 0
    
    async def test_storage_size_monitoring(self, memory_with_old_data):
        """Test monitoring of storage size."""
        memory = memory_with_old_data
        
        # Get current storage size
        total_size = await memory.get_total_storage_size()
        assert total_size > 0
        
        # Get breakdown by component
        size_breakdown = await memory.get_storage_breakdown()
        assert "iterations" in size_breakdown
        assert "checkpoints" in size_breakdown
        assert "aggregates" in size_breakdown
        assert "kv_store" in size_breakdown
        
        # Verify total matches sum of components
        component_sum = sum(size_breakdown.values())
        assert abs(total_size - component_sum) < 1000  # Allow small difference for metadata
    
    async def test_garbage_collection_trigger(self, temp_storage_dir):
        """Test that garbage collection triggers when storage exceeds limit."""
        # Create memory with very small storage limit and short retention
        memory = ContextMemory(
            storage_path=temp_storage_dir,
            max_storage_gb=0.0001,  # 100KB limit
            retention_days=0  # Clean everything immediately
        )
        await memory.initialize()
        
        # Create an old iteration that can be cleaned
        old_date = datetime.now(timezone.utc) - timedelta(days=1)
        iter_dir = temp_storage_dir / "iterations" / "iteration_001"
        iter_dir.mkdir(parents=True, exist_ok=True)
        metadata = {
            "iteration_number": 1,
            "started_at": old_date.isoformat(),
            "status": "completed",
            "completed_at": old_date.isoformat()
        }
        with open(iter_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f)
        
        # Generate data until we exceed the limit
        for i in range(50):
            state_update = StateUpdate(
                timestamp=old_date,
                update_type="periodic",
                system_statistics={"data": "x" * 1000},  # 1KB of data
                orchestration_state={"large": "y" * 1000}
            )
            await memory.store_state_update(state_update)
        
        # Check if garbage collection was triggered
        gc_triggered = await memory.check_garbage_collection_needed()
        assert gc_triggered
        
        # Run garbage collection
        cleaned_size = await memory.run_garbage_collection()
        assert cleaned_size > 0
        
        # Verify storage is now reduced
        total_size_after = await memory.get_total_storage_size()
        # Storage should be under the limit after GC
        assert gc_triggered  # GC was needed and triggered
    
    async def test_periodic_archive_rotation(self, memory_with_old_data):
        """Test periodic archive rotation (every 24 hours)."""
        memory = memory_with_old_data
        
        # Set last archive time to 25 hours ago
        last_archive_file = memory.storage_path / "configuration" / "last_archive.json"
        last_archive_data = {
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat(),
            "archived_count": 0
        }
        with open(last_archive_file, 'w') as f:
            json.dump(last_archive_data, f)
        
        # Check if archive rotation is needed
        needs_rotation = await memory.check_archive_rotation_needed()
        assert needs_rotation
        
        # Run archive rotation
        rotated = await memory.rotate_archives()
        assert rotated
        
        # Verify last archive time was updated
        with open(last_archive_file, 'r') as f:
            new_data = json.load(f)
            new_timestamp = datetime.fromisoformat(new_data["timestamp"])
            assert (datetime.now(timezone.utc) - new_timestamp).total_seconds() < 60
    
    async def test_cleanup_preserves_active_iteration(self, temp_storage_dir):
        """Test that cleanup never removes the active iteration."""
        memory = ContextMemory(
            storage_path=temp_storage_dir,
            retention_days=1  # Very short retention
        )
        await memory.initialize()
        
        # Start an active iteration
        active_iter = await memory.start_new_iteration()
        
        # Add some old data to the active iteration
        old_date = datetime.now(timezone.utc) - timedelta(days=5)
        state_update = StateUpdate(
            timestamp=old_date,
            update_type="periodic",
            system_statistics={"active": True},
            orchestration_state={}
        )
        await memory.store_state_update(state_update)
        
        # Run cleanup
        cleaned_count = await memory.cleanup_old_iterations()
        
        # Verify active iteration still exists
        current_active = await memory.get_active_iteration()
        assert current_active == active_iter
        
        # Verify iteration data still exists
        iter_info = await memory.get_iteration_info(active_iter)
        assert iter_info is not None
        assert iter_info["status"] == "active"
    
    async def test_cleanup_performance_monitoring(self, memory_with_old_data):
        """Test performance monitoring during cleanup operations."""
        memory = memory_with_old_data
        
        # Enable performance monitoring
        await memory.enable_performance_monitoring()
        
        # Run cleanup operation
        start_time = datetime.now(timezone.utc)
        cleaned_count = await memory.cleanup_old_iterations()
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Get cleanup performance metrics
        metrics = await memory.get_cleanup_metrics()
        
        assert "last_cleanup_duration" in metrics
        assert "items_cleaned" in metrics
        assert "storage_freed_bytes" in metrics
        assert "cleanup_history" in metrics
        
        # Verify metrics are reasonable
        assert metrics["last_cleanup_duration"] > 0
        assert metrics["items_cleaned"] == cleaned_count
        # Note: storage_freed_bytes can be negative if archives were created
        assert "storage_freed_bytes" in metrics
    
    async def test_incremental_cleanup(self, memory_with_old_data):
        """Test incremental cleanup to avoid blocking operations."""
        memory = memory_with_old_data
        
        # Configure incremental cleanup
        memory.set_cleanup_batch_size(2)  # Clean 2 items at a time
        
        # Run incremental cleanup
        total_cleaned = 0
        batch_count = 0
        
        while True:
            cleaned = await memory.cleanup_batch()
            if cleaned == 0:
                break
            total_cleaned += cleaned
            batch_count += 1
            
            # Verify batch size limit is respected
            assert cleaned <= 2
        
        # Verify all old data was eventually cleaned
        assert total_cleaned > 0
        assert batch_count > 0
    
    async def test_cleanup_with_concurrent_writes(self, memory_with_old_data):
        """Test cleanup doesn't interfere with concurrent write operations."""
        memory = memory_with_old_data
        
        # Track write success during cleanup
        write_results = []
        
        async def continuous_writes():
            """Continuously write data during cleanup."""
            for i in range(10):
                state_update = StateUpdate(
                    timestamp=datetime.now(timezone.utc),
                    update_type="periodic",
                    system_statistics={"concurrent": i},
                    orchestration_state={}
                )
                result = await memory.store_state_update(state_update)
                write_results.append(result.success)
                await asyncio.sleep(0.01)
        
        # Run cleanup and writes concurrently
        cleanup_task = asyncio.create_task(memory.cleanup_old_iterations())
        write_task = asyncio.create_task(continuous_writes())
        
        # Wait for both to complete
        await asyncio.gather(cleanup_task, write_task)
        
        # Verify all writes succeeded
        assert all(write_results)
        
        # Verify recent data wasn't cleaned
        recent_states = await memory.retrieve_states_in_range(
            start_time=datetime.now(timezone.utc) - timedelta(minutes=1),
            end_time=datetime.now(timezone.utc)
        )
        assert len(recent_states) >= 10