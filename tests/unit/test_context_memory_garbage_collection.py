"""Unit tests for ContextMemory garbage collection functionality."""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
import shutil
import tempfile

import pytest

from src.core.context_memory import ContextMemory, StateUpdate


@pytest.fixture
async def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestContextMemoryGarbageCollection:
    """Test garbage collection functionality."""
    
    @pytest.mark.asyncio
    async def test_collect_garbage_empty_storage(self, temp_dir: Path):
        """Test garbage collection on empty storage."""
        memory = ContextMemory(storage_path=temp_dir / "memory")
        await memory.initialize()
        
        result = await memory.collect_garbage()
        
        assert isinstance(result, dict)
        assert result["orphaned_directories"] == 0
        assert result["orphaned_files"] == 0
        assert result["bytes_freed"] == 0
        assert result["errors"] == []
    
    @pytest.mark.asyncio
    async def test_collect_garbage_with_orphaned_directories(self, temp_dir: Path):
        """Test garbage collection removes orphaned directories."""
        memory = ContextMemory(storage_path=temp_dir / "memory")
        await memory.initialize()
        
        # Create valid iteration
        iter_id = await memory.start_new_iteration()
        
        # Create orphaned directories
        orphan_dir1 = memory.storage_path / "iterations" / "orphan_dir_001"
        orphan_dir1.mkdir(parents=True)
        (orphan_dir1 / "data.json").write_text('{"orphaned": true}')
        
        orphan_dir2 = memory.storage_path / "iterations" / "temp_12345"
        orphan_dir2.mkdir(parents=True)
        (orphan_dir2 / "file1.txt").write_text("orphaned data")
        (orphan_dir2 / "file2.txt").write_text("more orphaned data")
        
        # Calculate expected bytes to be freed
        expected_bytes = sum(f.stat().st_size for f in orphan_dir1.rglob("*") if f.is_file())
        expected_bytes += sum(f.stat().st_size for f in orphan_dir2.rglob("*") if f.is_file())
        
        # Run garbage collection
        result = await memory.collect_garbage()
        
        # Verify orphaned directories were removed
        assert not orphan_dir1.exists()
        assert not orphan_dir2.exists()
        
        # Verify valid iteration remains
        valid_dir = memory.storage_path / "iterations" / f"iteration_{iter_id:03d}"
        assert valid_dir.exists()
        
        # Check results
        assert result["orphaned_directories"] == 2
        assert result["orphaned_files"] == 0
        assert result["bytes_freed"] >= expected_bytes
        assert result["errors"] == []
    
    @pytest.mark.asyncio
    async def test_collect_garbage_with_orphaned_files(self, temp_dir: Path):
        """Test garbage collection removes orphaned files."""
        memory = ContextMemory(storage_path=temp_dir / "memory")
        await memory.initialize()
        
        # Create valid iteration
        await memory.start_new_iteration()
        
        # Create orphaned files in iterations directory
        iterations_dir = memory.storage_path / "iterations"
        orphan_file1 = iterations_dir / "orphan_data.json"
        orphan_file1.write_text('{"orphaned": true}')
        
        orphan_file2 = iterations_dir / "temp_file.txt"
        orphan_file2.write_text("temporary data that should be cleaned")
        
        orphan_file3 = iterations_dir / ".DS_Store"  # System file
        orphan_file3.write_text("system junk")
        
        # Calculate expected bytes
        expected_bytes = orphan_file1.stat().st_size + orphan_file2.stat().st_size + orphan_file3.stat().st_size
        
        # Run garbage collection
        result = await memory.collect_garbage()
        
        # Verify orphaned files were removed
        assert not orphan_file1.exists()
        assert not orphan_file2.exists()
        assert not orphan_file3.exists()
        
        # Check results
        assert result["orphaned_directories"] == 0
        assert result["orphaned_files"] == 3
        assert result["bytes_freed"] >= expected_bytes
        assert result["errors"] == []
    
    @pytest.mark.asyncio
    async def test_collect_garbage_preserves_active_data(self, temp_dir: Path):
        """Test garbage collection preserves all active data."""
        memory = ContextMemory(storage_path=temp_dir / "memory")
        await memory.initialize()
        
        # Create multiple iterations with data
        iterations = []
        for i in range(3):
            iter_id = await memory.start_new_iteration()
            iterations.append(iter_id)
            
            # Store some data
            state = StateUpdate(
                timestamp=datetime.now(timezone.utc),
                update_type="periodic",
                system_statistics={"iteration": iter_id, "data": f"iter_{i}"},
                orchestration_state={"active": True}
            )
            await memory.store_state_update(state)
            
            # Don't complete the last iteration (keep it active)
            if i < 2:
                await memory.complete_iteration(iter_id, {"status": "done"})
        
        # Create some orphaned data
        orphan = memory.storage_path / "iterations" / "orphan_999"
        orphan.mkdir(parents=True)
        (orphan / "junk.txt").write_text("delete me")
        
        # Run garbage collection
        result = await memory.collect_garbage()
        
        # Verify all valid iterations remain
        for iter_id in iterations:
            iter_dir = memory.storage_path / "iterations" / f"iteration_{iter_id:03d}"
            assert iter_dir.exists()
            # Verify data files still exist
            assert any(iter_dir.glob("system_state_*.json"))
        
        # Verify orphan was removed
        assert not orphan.exists()
        
        # Check metadata remains
        assert (memory.storage_path / "metadata.json").exists()
        
        # Verify indexes remain
        assert (memory.storage_path / "component_index.json").exists()
        assert (memory.storage_path / "checkpoint_index.json").exists()
    
    @pytest.mark.asyncio
    async def test_collect_garbage_handles_permission_errors(self, temp_dir: Path):
        """Test garbage collection handles files it cannot delete."""
        memory = ContextMemory(storage_path=temp_dir / "memory")
        await memory.initialize()
        
        # Create orphaned directory
        orphan_dir = memory.storage_path / "iterations" / "protected_orphan"
        orphan_dir.mkdir(parents=True)
        protected_file = orphan_dir / "protected.txt"
        protected_file.write_text("protected content")
        
        # Make directory read-only (simulate permission issue)
        import os
        import stat
        try:
            # Remove write permissions
            os.chmod(orphan_dir, stat.S_IRUSR | stat.S_IXUSR)
            
            # Run garbage collection
            result = await memory.collect_garbage()
            
            # Should report the error
            assert len(result["errors"]) > 0
            assert any("protected_orphan" in err or "Permission" in err for err in result["errors"])
            
            # Directory should still exist due to permission error
            assert orphan_dir.exists()
        finally:
            # Restore permissions for cleanup
            os.chmod(orphan_dir, stat.S_IRWXU)
            shutil.rmtree(orphan_dir)
    
    @pytest.mark.asyncio
    async def test_collect_garbage_with_archive_directory(self, temp_dir: Path):
        """Test garbage collection handles archive directory correctly."""
        memory = ContextMemory(storage_path=temp_dir / "memory")
        await memory.initialize()
        
        # Create archive directory with files
        archive_dir = memory.storage_path / "archive"
        archive_dir.mkdir(exist_ok=True)
        
        # Add some archive files
        (archive_dir / "iteration_001_20240101.tar.gz").write_bytes(b"archived data")
        (archive_dir / "iteration_002_20240102.tar.gz").write_bytes(b"more archived data")
        
        # Add orphaned file in archive
        orphan_in_archive = archive_dir / "temp_file.txt"
        orphan_in_archive.write_text("should be removed")
        
        # Create orphaned directory outside archive
        orphan_dir = memory.storage_path / "iterations" / "orphan"
        orphan_dir.mkdir(parents=True)
        
        # Run garbage collection
        result = await memory.collect_garbage()
        
        # Verify archive files remain
        assert (archive_dir / "iteration_001_20240101.tar.gz").exists()
        assert (archive_dir / "iteration_002_20240102.tar.gz").exists()
        
        # Verify orphaned file in archive was removed
        assert not orphan_in_archive.exists()
        
        # Verify orphaned directory was removed
        assert not orphan_dir.exists()
    
    @pytest.mark.asyncio
    async def test_collect_garbage_empty_directories(self, temp_dir: Path):
        """Test garbage collection removes empty directories."""
        memory = ContextMemory(storage_path=temp_dir / "memory")
        await memory.initialize()
        
        # Create valid iteration
        await memory.start_new_iteration()
        
        # Create empty orphaned directories
        empty_dir1 = memory.storage_path / "iterations" / "empty_001"
        empty_dir1.mkdir(parents=True)
        
        empty_nested = memory.storage_path / "iterations" / "nested" / "empty" / "dirs"
        empty_nested.mkdir(parents=True)
        
        # Run garbage collection
        result = await memory.collect_garbage()
        
        # Verify empty directories were removed
        assert not empty_dir1.exists()
        assert not (memory.storage_path / "iterations" / "nested").exists()
        
        assert result["orphaned_directories"] >= 2  # At least the two we created
    
    @pytest.mark.asyncio
    async def test_collect_garbage_concurrent_operations(self, temp_dir: Path):
        """Test garbage collection during concurrent memory operations."""
        memory = ContextMemory(storage_path=temp_dir / "memory")
        await memory.initialize()
        
        # Start multiple iterations
        iter_ids = []
        for _ in range(3):
            iter_id = await memory.start_new_iteration()
            iter_ids.append(iter_id)
        
        # Create orphaned data
        orphan = memory.storage_path / "iterations" / "will_be_deleted"
        orphan.mkdir(parents=True)
        (orphan / "data.txt").write_text("orphaned")
        
        async def store_data():
            """Store data while garbage collection runs."""
            for i in range(5):
                state = StateUpdate(
                    timestamp=datetime.now(timezone.utc),
                    update_type="periodic",
                    system_statistics={"update": i},
                    orchestration_state={"concurrent": True}
                )
                await memory.store_state_update(state)
                await asyncio.sleep(0.01)
        
        # Run garbage collection concurrently with data storage
        store_task = asyncio.create_task(store_data())
        gc_result = await memory.collect_garbage()
        await store_task
        
        # Verify orphan was removed
        assert not orphan.exists()
        
        # Verify active iterations remain with their data
        for iter_id in iter_ids:
            iter_dir = memory.storage_path / "iterations" / f"iteration_{iter_id:03d}"
            if iter_dir.exists():  # Some might be completed
                # Should have state files from concurrent storage
                state_files = list(iter_dir.glob("system_state_*.json"))
                assert len(state_files) > 0
    
    @pytest.mark.asyncio
    async def test_collect_garbage_reports_size_correctly(self, temp_dir: Path):
        """Test garbage collection reports freed space accurately."""
        memory = ContextMemory(storage_path=temp_dir / "memory")
        await memory.initialize()
        
        # Create orphaned files with known sizes
        orphan1 = memory.storage_path / "iterations" / "big_file.dat"
        orphan1.write_bytes(b"x" * 10000)  # 10KB
        
        orphan_dir = memory.storage_path / "iterations" / "data_dir"
        orphan_dir.mkdir()
        (orphan_dir / "file1.txt").write_bytes(b"y" * 5000)  # 5KB
        (orphan_dir / "file2.txt").write_bytes(b"z" * 3000)  # 3KB
        
        # Calculate expected size
        expected_size = 10000 + 5000 + 3000
        
        # Run garbage collection
        result = await memory.collect_garbage()
        
        # Verify reported size is accurate
        assert result["bytes_freed"] == expected_size
        assert result["orphaned_files"] == 1
        assert result["orphaned_directories"] == 1