"""Unit tests for safety log rotation and cleanup."""

import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

from src.core.safety import SafetyConfig, SafetyLogger, LogRotationManager


class TestSafetyLogRotation:
    """Test suite for safety log rotation and cleanup."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def config_with_temp_dir(self, temp_dir):
        """Create SafetyConfig with temporary directory."""
        return SafetyConfig(
            log_directory=temp_dir / "safety_logs",
            retention_days=7
        )
    
    @pytest.mark.asyncio
    async def test_cleanup_old_logs(self, config_with_temp_dir):
        """Test cleanup of logs older than retention period."""
        logger = SafetyLogger(config_with_temp_dir)
        log_dir = config_with_temp_dir.log_directory
        
        # Create old log files
        now = datetime.now(timezone.utc)
        old_date = now - timedelta(days=10)
        recent_date = now - timedelta(days=3)
        
        # Create old log file (should be deleted)
        old_file = log_dir / f"{old_date.strftime('%Y%m%d')}_old-log.json"
        old_file.write_text(json.dumps({"test": "old"}))
        
        # Create recent log file (should be kept)
        recent_file = log_dir / f"{recent_date.strftime('%Y%m%d')}_recent-log.json"
        recent_file.write_text(json.dumps({"test": "recent"}))
        
        # Create current log file (should be kept)
        current_file = log_dir / f"{now.strftime('%Y%m%d')}_current-log.json"
        current_file.write_text(json.dumps({"test": "current"}))
        
        # Run cleanup
        await logger.cleanup_old_logs()
        
        # Check results
        assert not old_file.exists()  # Should be deleted
        assert recent_file.exists()   # Should be kept
        assert current_file.exists()  # Should be kept
    
    @pytest.mark.asyncio
    async def test_cleanup_with_custom_retention(self, temp_dir):
        """Test cleanup with custom retention period."""
        config = SafetyConfig(
            log_directory=temp_dir / "safety_logs",
            retention_days=1  # Only keep 1 day
        )
        logger = SafetyLogger(config)
        
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=2)
        
        # Create log from 2 days ago
        old_file = config.log_directory / f"{yesterday.strftime('%Y%m%d')}_test.json"
        old_file.write_text(json.dumps({"test": "data"}))
        
        await logger.cleanup_old_logs()
        
        assert not old_file.exists()
    
    @pytest.mark.asyncio
    async def test_cleanup_invalid_filenames(self, config_with_temp_dir):
        """Test that cleanup handles invalid filename formats gracefully."""
        logger = SafetyLogger(config_with_temp_dir)
        log_dir = config_with_temp_dir.log_directory
        
        # Create files with invalid names
        invalid_file1 = log_dir / "invalid_format.json"
        invalid_file1.write_text(json.dumps({"test": "data"}))
        
        invalid_file2 = log_dir / "no_extension"
        invalid_file2.write_text("test")
        
        # Should not raise exceptions
        await logger.cleanup_old_logs()
        
        # Invalid files should remain untouched
        assert invalid_file1.exists()
        assert invalid_file2.exists()
    
    def test_log_rotation_manager_initialization(self, config_with_temp_dir):
        """Test LogRotationManager initialization."""
        manager = LogRotationManager(config_with_temp_dir)
        
        assert manager.config == config_with_temp_dir
        assert manager.log_directory == config_with_temp_dir.log_directory
        assert manager.retention_days == config_with_temp_dir.retention_days
    
    @pytest.mark.asyncio
    async def test_log_rotation_by_size(self, config_with_temp_dir):
        """Test log rotation when file size exceeds limit."""
        manager = LogRotationManager(config_with_temp_dir)
        
        # Create a large log file
        large_file = config_with_temp_dir.log_directory / "20250118_large.json"
        large_content = json.dumps({"data": "x" * 10000})  # ~10KB
        large_file.write_text(large_content)
        
        # Set size limit to 5KB
        rotated_file = await manager.rotate_if_needed(large_file, size_limit_kb=5)
        
        # Original file should be rotated
        assert rotated_file is not None
        assert rotated_file.name.endswith(".rotated.json")
        assert rotated_file.exists()
        assert not large_file.exists()
    
    @pytest.mark.asyncio
    async def test_log_rotation_by_age(self, temp_dir):
        """Test log rotation for files older than specified age."""
        config = SafetyConfig(
            log_directory=temp_dir / "safety_logs",
            retention_days=7
        )
        manager = LogRotationManager(config)
        
        # Create an old log file
        old_date = datetime.now(timezone.utc) - timedelta(days=10)
        old_file = config.log_directory / f"{old_date.strftime('%Y%m%d')}_old.json"
        old_file.write_text(json.dumps({"test": "old"}))
        
        # Rotate old files
        rotated_files = await manager.rotate_old_files(age_days=7)
        
        assert len(rotated_files) == 1
        assert not old_file.exists()
        assert rotated_files[0].name.endswith(".rotated.json")
    
    @pytest.mark.asyncio
    async def test_archive_rotated_logs(self, config_with_temp_dir):
        """Test archiving of rotated logs."""
        manager = LogRotationManager(config_with_temp_dir)
        
        # Create some rotated files
        for i in range(3):
            rotated_file = config_with_temp_dir.log_directory / f"test_{i}.rotated.json"
            rotated_file.write_text(json.dumps({"index": i}))
        
        # Archive rotated files
        archive_path = await manager.archive_rotated_logs()
        
        assert archive_path is not None
        assert archive_path.exists()
        assert archive_path.name.endswith(".tar.gz")
        
        # Rotated files should be removed
        rotated_files = list(config_with_temp_dir.log_directory.glob("*.rotated.json"))
        assert len(rotated_files) == 0
    
    @pytest.mark.asyncio
    async def test_scheduled_rotation(self, config_with_temp_dir):
        """Test scheduled log rotation task."""
        manager = LogRotationManager(config_with_temp_dir)
        
        # Create test files
        now = datetime.now(timezone.utc)
        
        # Old file to be cleaned up
        old_file = config_with_temp_dir.log_directory / f"{(now - timedelta(days=10)).strftime('%Y%m%d')}_old.json"
        old_file.write_text(json.dumps({"test": "old"}))
        
        # Large file to be rotated
        large_file = config_with_temp_dir.log_directory / f"{now.strftime('%Y%m%d')}_large.json"
        large_file.write_text(json.dumps({"data": "x" * 50000}))  # ~50KB
        
        # Run scheduled rotation (with small size limit for testing)
        await manager.run_scheduled_rotation(size_limit_kb=10)
        
        # Old file should be deleted
        assert not old_file.exists()
        
        # Large file should be rotated
        assert not large_file.exists()
        
        # Check for archived files (rotated files are archived immediately)
        archive_files = list(config_with_temp_dir.log_directory.glob("*.tar.gz"))
        assert len(archive_files) > 0
    
    def test_get_file_age_days(self, config_with_temp_dir):
        """Test calculation of file age in days."""
        manager = LogRotationManager(config_with_temp_dir)
        
        # Create a file with known date
        test_date = datetime.now(timezone.utc) - timedelta(days=5)
        test_file = config_with_temp_dir.log_directory / f"{test_date.strftime('%Y%m%d')}_test.json"
        test_file.write_text(json.dumps({"test": "data"}))
        
        age_days = manager.get_file_age_days(test_file)
        
        # Should be approximately 5 days (allowing for small timing differences)
        assert 4 <= age_days <= 6
    
    def test_get_file_size_kb(self, config_with_temp_dir):
        """Test file size calculation."""
        manager = LogRotationManager(config_with_temp_dir)
        
        # Create a file with known size
        test_file = config_with_temp_dir.log_directory / "test_size.json"
        content = "x" * 1024  # 1KB of data
        test_file.write_text(content)
        
        size_kb = manager.get_file_size_kb(test_file)
        
        # Should be approximately 1KB
        assert 0.9 <= size_kb <= 1.1