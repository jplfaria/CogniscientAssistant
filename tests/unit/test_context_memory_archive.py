"""Unit tests for ContextMemory archive-specific functionality."""
import asyncio
import json
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

from src.core.context_memory import ContextMemory


class TestContextMemoryArchive:
    """Test ContextMemory archive-specific operations."""
    
    @pytest.fixture
    def temp_storage_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Cleanup after test
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    async def memory_instance(self, temp_storage_dir):
        """Create a ContextMemory instance."""
        memory = ContextMemory(storage_path=temp_storage_dir)
        await memory.initialize()
        return memory
    
    async def test_archive_metadata_update(self, memory_instance):
        """Test updating archive metadata."""
        memory = memory_instance
        
        # Update archive metadata
        await memory._update_archive_metadata(5)
        
        # Verify metadata file was created
        metadata_file = memory.storage_path / "archive" / "archive_metadata.json"
        assert metadata_file.exists()
        
        # Verify content
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        assert "archives" in metadata
        assert len(metadata["archives"]) == 1
        assert metadata["archives"][0]["archived_count"] == 5
    
    async def test_archive_metadata_append(self, memory_instance):
        """Test appending to existing archive metadata."""
        memory = memory_instance
        
        # Create initial metadata
        await memory._update_archive_metadata(3)
        
        # Append more
        await memory._update_archive_metadata(2)
        
        # Verify both entries exist
        metadata_file = memory.storage_path / "archive" / "archive_metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        assert len(metadata["archives"]) == 2
        assert metadata["archives"][0]["archived_count"] == 3
        assert metadata["archives"][1]["archived_count"] == 2
    
    async def test_check_archive_rotation_no_file(self, memory_instance):
        """Test archive rotation check when no last archive file exists."""
        memory = memory_instance
        
        # Should return True when no last archive file exists
        needs_rotation = await memory.check_archive_rotation_needed()
        assert needs_rotation
    
    async def test_check_archive_rotation_recent(self, memory_instance):
        """Test archive rotation check with recent archive."""
        memory = memory_instance
        
        # Create a recent last archive file
        last_archive_file = memory.storage_path / "configuration" / "last_archive.json"
        last_archive_file.parent.mkdir(parents=True, exist_ok=True)
        
        recent_time = datetime.now(timezone.utc) - timedelta(hours=1)
        last_archive_data = {
            "timestamp": recent_time.isoformat(),
            "archived_count": 0
        }
        
        with open(last_archive_file, 'w') as f:
            json.dump(last_archive_data, f)
        
        # Should return False for recent archive
        needs_rotation = await memory.check_archive_rotation_needed()
        assert not needs_rotation
    
    async def test_storage_breakdown_empty(self, memory_instance):
        """Test storage breakdown on empty storage."""
        memory = memory_instance
        
        breakdown = await memory.get_storage_breakdown()
        
        assert breakdown["iterations"] == 0
        assert breakdown["checkpoints"] == 0
        assert breakdown["aggregates"] == 0
        assert breakdown["kv_store"] == 0
    
    async def test_enable_performance_monitoring(self, memory_instance):
        """Test enabling performance monitoring."""
        memory = memory_instance
        
        # Enable monitoring
        await memory.enable_performance_monitoring()
        
        assert hasattr(memory, '_performance_monitoring')
        assert memory._performance_monitoring is True
        assert hasattr(memory, '_cleanup_metrics')
        
        # Get initial metrics
        metrics = await memory.get_cleanup_metrics()
        assert metrics["last_cleanup_duration"] == 0
        assert metrics["items_cleaned"] == 0
        assert metrics["storage_freed_bytes"] == 0
        assert metrics["cleanup_history"] == []
    
    async def test_set_cleanup_batch_size(self, memory_instance):
        """Test setting cleanup batch size."""
        memory = memory_instance
        
        # Set batch size
        memory.set_cleanup_batch_size(5)
        
        assert hasattr(memory, '_cleanup_batch_size')
        assert memory._cleanup_batch_size == 5
    
    async def test_cleanup_batch_empty(self, memory_instance):
        """Test cleanup batch with no iterations."""
        memory = memory_instance
        
        memory.set_cleanup_batch_size(10)
        cleaned = await memory.cleanup_batch()
        
        assert cleaned == 0
    
    async def test_garbage_collection_under_limit(self, memory_instance):
        """Test garbage collection check when under storage limit."""
        memory = memory_instance
        
        # With empty storage, should not need GC
        needs_gc = await memory.check_garbage_collection_needed()
        assert not needs_gc
    
    async def test_run_garbage_collection_empty(self, memory_instance):
        """Test running garbage collection on empty storage."""
        memory = memory_instance
        
        # Run GC on empty storage
        freed = await memory.run_garbage_collection()
        
        # Should free 0 bytes
        assert freed == 0
    
    async def test_get_total_storage_size_with_files(self, memory_instance):
        """Test getting total storage size with some files."""
        memory = memory_instance
        
        # Create some test files
        test_file = memory.storage_path / "test_file.json"
        test_data = {"test": "data" * 100}
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Get storage size
        size = await memory.get_total_storage_size()
        
        # Should be greater than 0
        assert size > 0
        
        # Create another file in a subdirectory
        subdir = memory.storage_path / "subdir"
        subdir.mkdir()
        test_file2 = subdir / "test_file2.json"
        with open(test_file2, 'w') as f:
            json.dump(test_data, f)
        
        # Size should increase
        new_size = await memory.get_total_storage_size()
        assert new_size > size
    
    async def test_rotate_archives_success(self, memory_instance):
        """Test successful archive rotation."""
        memory = memory_instance
        
        # Create an old iteration to archive
        old_date = datetime.now(timezone.utc) - timedelta(days=10)
        iter_dir = memory.storage_path / "iterations" / "iteration_001"
        iter_dir.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            "iteration_number": 1,
            "started_at": old_date.isoformat(),
            "status": "completed"
        }
        with open(iter_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f)
        
        # Rotate archives
        rotated = await memory.rotate_archives()
        
        # Should succeed
        assert rotated
        
        # Verify last archive file was created
        last_archive_file = memory.storage_path / "configuration" / "last_archive.json"
        assert last_archive_file.exists()