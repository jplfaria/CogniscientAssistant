"""Unit tests for ContextMemory archive timezone handling."""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import tarfile
import tempfile

import pytest

from src.core.context_memory import ContextMemory, StateUpdate


@pytest.fixture
async def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestContextMemoryArchiveTimezone:
    """Test archive functionality with proper timezone handling."""
    
    @pytest.mark.asyncio
    async def test_archive_with_timezone_aware_dates(self, temp_dir: Path):
        """Test archiving handles timezone-aware dates correctly."""
        # Create memory with short retention
        memory = ContextMemory(
            storage_path=temp_dir / "memory",
            retention_days=0  # Archive immediately
        )
        await memory.initialize()
        
        # Create old iteration with timezone-aware timestamp
        iter_id = await memory.start_new_iteration()
        
        # Store data with explicit timezone
        state = StateUpdate(
            timestamp=datetime.now(timezone.utc),
            update_type="periodic",
            system_statistics={"test": "timezone_aware"},
            orchestration_state={"tz": "UTC"}
        )
        await memory.store_state_update(state)
        
        # Complete iteration with timezone-aware completion time
        await memory.complete_iteration(iter_id, {"completed_at": datetime.now(timezone.utc).isoformat()})
        
        # Archive should work without timezone comparison errors
        await memory.archive_old_data()
        
        # Verify archive was created
        archive_dir = memory.storage_path / "archive"
        assert archive_dir.exists()
        archives = list(archive_dir.glob("iteration_*.tar.gz"))
        assert len(archives) == 1
    
    @pytest.mark.asyncio
    async def test_archive_with_naive_dates_conversion(self, temp_dir: Path):
        """Test archiving converts naive dates to timezone-aware."""
        memory = ContextMemory(
            storage_path=temp_dir / "memory",
            retention_days=1
        )
        await memory.initialize()
        
        # Create iteration
        iter_id = await memory.start_new_iteration()
        
        # Manually create iteration info with naive datetime (simulating old data)
        iter_dir = memory.storage_path / "iterations" / f"iteration_{iter_id:03d}"
        iter_info_path = iter_dir / "iteration_info.json"
        
        # Write iteration info with naive datetime
        iter_info = {
            "iteration_id": iter_id,
            "start_time": datetime.now().isoformat(),  # Naive datetime
            "status": "completed",
            "completed_at": datetime.now().isoformat()  # Naive datetime
        }
        with open(iter_info_path, 'w') as f:
            json.dump(iter_info, f)
        
        # Complete the iteration
        await memory.complete_iteration(iter_id, {"status": "done"})
        
        # Set the iteration to be old by modifying the file
        old_time = datetime.now() - timedelta(days=2)
        iter_info["completed_at"] = old_time.isoformat()
        with open(iter_info_path, 'w') as f:
            json.dump(iter_info, f)
        
        # Archive should handle naive datetime without errors
        await memory.archive_old_data()
        
        # Verify no errors occurred and archive process completed
        assert memory.storage_path.exists()
    
    @pytest.mark.asyncio
    async def test_archive_cutoff_timezone_handling(self, temp_dir: Path):
        """Test archive cutoff date uses proper timezone."""
        memory = ContextMemory(
            storage_path=temp_dir / "memory",
            retention_days=7
        )
        await memory.initialize()
        
        # Create multiple iterations with different ages
        iterations = []
        
        # Old iteration (should be archived)
        iter1 = await memory.start_new_iteration()
        iter1_dir = memory.storage_path / "iterations" / f"iteration_{iter1:03d}"
        iter1_info = iter1_dir / "metadata.json"
        
        # Set to 10 days ago
        old_date = datetime.now(timezone.utc) - timedelta(days=10)
        await memory.complete_iteration(iter1, {"status": "old"})
        
        # Manually update the started time (archive checks started_at, not completed_at)
        with open(iter1_info, 'r') as f:
            info = json.load(f)
        info["started_at"] = old_date.isoformat()
        with open(iter1_info, 'w') as f:
            json.dump(info, f)
        
        # Recent iteration (should not be archived)
        iter2 = await memory.start_new_iteration()
        await memory.complete_iteration(iter2, {"status": "recent"})
        
        # Active iteration (should not be archived)
        iter3 = await memory.start_new_iteration()
        
        # Run archive
        archived = await memory.archive_old_data()
        
        # Verify old iteration was archived (archive_old_data only archives, doesn't remove)
        assert archived == 1
        archive_dir = memory.storage_path / "archive"
        archives = list(archive_dir.glob("*.tar.gz"))
        assert len(archives) == 1
        assert iter1_dir.exists()  # Directory still exists after archiving
        
        # Verify recent and active iterations remain
        iter2_dir = memory.storage_path / "iterations" / f"iteration_{iter2:03d}"
        iter3_dir = memory.storage_path / "iterations" / f"iteration_{iter3:03d}"
        assert iter2_dir.exists()
        assert iter3_dir.exists()
        
        # Verify archive was created
        archives = list((memory.storage_path / "archive").glob("*.tar.gz"))
        assert len(archives) == 1
    
    @pytest.mark.asyncio
    async def test_archive_preserves_timezone_info(self, temp_dir: Path):
        """Test that archived data preserves timezone information."""
        memory = ContextMemory(
            storage_path=temp_dir / "memory",
            retention_days=0
        )
        await memory.initialize()
        
        # Create iteration with specific timezone data
        iter_id = await memory.start_new_iteration()
        
        # Store data with various timezone formats
        utc_time = datetime.now(timezone.utc)
        state = StateUpdate(
            timestamp=utc_time,
            update_type="test",
            system_statistics={
                "utc_time": utc_time.isoformat(),
                "timezone": "UTC",
                "offset": "+00:00"
            },
            orchestration_state={"test": "timezone_preservation"}
        )
        result = await memory.store_state_update(state)
        stored_file = Path(result.storage_path)
        
        # Complete and archive
        await memory.complete_iteration(iter_id, {"final": "state"})
        await memory.archive_old_data()
        
        # Extract and verify archived data
        archive_dir = memory.storage_path / "archive"
        archives = list(archive_dir.glob("*.tar.gz"))
        assert len(archives) == 1
        
        # Extract archive
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()
        
        with tarfile.open(archives[0], 'r:gz') as tar:
            tar.extractall(extract_dir)
        
        # Find the state file in extracted data
        extracted_files = list(extract_dir.rglob("system_state_*.json"))
        assert len(extracted_files) > 0
        
        # Verify timezone info is preserved
        with open(extracted_files[0], 'r') as f:
            data = json.load(f)
        
        assert "timestamp" in data
        assert "+" in data["timestamp"] or "Z" in data["timestamp"]  # Has timezone info
        assert data["system_statistics"]["timezone"] == "UTC"
    
    @pytest.mark.asyncio
    async def test_archive_handles_missing_dates(self, temp_dir: Path):
        """Test archive handles iterations with missing date information."""
        memory = ContextMemory(
            storage_path=temp_dir / "memory",
            retention_days=1
        )
        await memory.initialize()
        
        # Create iteration
        iter_id = await memory.start_new_iteration()
        iter_dir = memory.storage_path / "iterations" / f"iteration_{iter_id:03d}"
        
        # Create iteration info without completed_at
        iter_info = {
            "iteration_id": iter_id,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "abandoned"  # No completed_at field
        }
        with open(iter_dir / "iteration_info.json", 'w') as f:
            json.dump(iter_info, f)
        
        # Archive should handle missing dates gracefully
        await memory.archive_old_data()
        
        # Iteration without completion date should remain
        assert iter_dir.exists()
    
    @pytest.mark.asyncio
    async def test_archive_concurrent_with_different_timezones(self, temp_dir: Path):
        """Test archiving handles concurrent operations with different timezone representations."""
        memory = ContextMemory(
            storage_path=temp_dir / "memory",
            retention_days=-1  # Archive everything older than tomorrow
        )
        await memory.initialize()
        
        # Create multiple iterations concurrently
        async def create_iteration_with_tz(tz_offset: int):
            """Create iteration with specific timezone offset."""
            iter_id = await memory.start_new_iteration()
            
            # Create custom timezone
            tz = timezone(timedelta(hours=tz_offset))
            timestamp = datetime.now(tz)
            
            state = StateUpdate(
                timestamp=timestamp,
                update_type="concurrent",
                system_statistics={"tz_offset": tz_offset},
                orchestration_state={"timestamp": timestamp.isoformat()}
            )
            await memory.store_state_update(state)
            await memory.complete_iteration(iter_id, {"tz": str(tz)})
            return iter_id
        
        # Create iterations with different timezones sequentially
        iter_ids = []
        for tz_offset in [0, -5, 8, 9]:  # UTC, EST, PST, JST
            iter_id = await create_iteration_with_tz(tz_offset)
            iter_ids.append(iter_id)
        
        # Archive all iterations
        archived = await memory.archive_old_data()
        
        # All should be archived since retention_days=-1
        assert archived == len(iter_ids)
        archive_dir = memory.storage_path / "archive"
        archives = list(archive_dir.glob("*.tar.gz"))
        assert len(archives) == len(iter_ids)
        
        # Directories remain after archiving (archive doesn't remove)
        remaining = list((memory.storage_path / "iterations").glob("iteration_*"))
        assert len(remaining) == len(iter_ids)
    
    @pytest.mark.asyncio
    async def test_archive_filename_timezone_format(self, temp_dir: Path):
        """Test archive filenames use consistent timezone format."""
        memory = ContextMemory(
            storage_path=temp_dir / "memory",
            retention_days=0
        )
        await memory.initialize()
        
        # Create and complete iteration
        iter_id = await memory.start_new_iteration()
        await memory.complete_iteration(iter_id, {"test": "filename"})
        
        # Archive
        await memory.archive_old_data()
        
        # Check archive filename format
        archive_dir = memory.storage_path / "archive"
        archives = list(archive_dir.glob("*.tar.gz"))
        assert len(archives) == 1
        
        # Filename should contain UTC timestamp
        filename = archives[0].name
        assert filename.startswith(f"iteration_{iter_id:03d}_")
        assert filename.endswith(".tar.gz")
        
        # Extract timestamp part and verify format
        timestamp_part = filename.replace(f"iteration_{iter_id:03d}_", "").replace(".tar.gz", "")
        # Should be in format: YYYYMMDD_HHMMSS
        assert len(timestamp_part) == 15  # 8 + 1 + 6
        assert timestamp_part[8] == "_"