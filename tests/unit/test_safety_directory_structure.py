"""Unit tests for safety logging directory structure."""

import os
import tempfile
from pathlib import Path
import pytest

from src.core.safety import SafetyConfig, SafetyLogger


class TestSafetyDirectoryStructure:
    """Test suite for safety logging directory structure."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_create_directory_structure(self, temp_dir):
        """Test that SafetyLogger creates the required directory structure."""
        log_dir = temp_dir / ".aicoscientist" / "safety_logs"
        config = SafetyConfig(log_directory=log_dir)
        
        # Directory should not exist initially
        assert not log_dir.exists()
        
        # Create SafetyLogger
        logger = SafetyLogger(config)
        
        # Directory should be created
        assert log_dir.exists()
        assert log_dir.is_dir()
    
    def test_nested_directory_creation(self, temp_dir):
        """Test creation of nested directory structure."""
        log_dir = temp_dir / "deep" / "nested" / "safety" / "logs"
        config = SafetyConfig(log_directory=log_dir)
        
        logger = SafetyLogger(config)
        
        assert log_dir.exists()
        assert log_dir.is_dir()
    
    def test_existing_directory_handling(self, temp_dir):
        """Test that existing directories are handled correctly."""
        log_dir = temp_dir / "safety_logs"
        log_dir.mkdir(parents=True)
        
        # Create a test file in the directory
        test_file = log_dir / "existing.txt"
        test_file.write_text("test content")
        
        config = SafetyConfig(log_directory=log_dir)
        logger = SafetyLogger(config)
        
        # Directory should still exist
        assert log_dir.exists()
        # Existing file should be preserved
        assert test_file.exists()
        assert test_file.read_text() == "test content"
    
    def test_directory_permissions(self, temp_dir):
        """Test that created directories have proper permissions."""
        log_dir = temp_dir / "safety_logs"
        config = SafetyConfig(log_directory=log_dir)
        
        logger = SafetyLogger(config)
        
        # Check that directory is readable and writable
        assert os.access(log_dir, os.R_OK)
        assert os.access(log_dir, os.W_OK)
    
    def test_disabled_logger_no_directory(self, temp_dir):
        """Test that disabled logger doesn't create directories."""
        log_dir = temp_dir / "safety_logs"
        config = SafetyConfig(enabled=False, log_directory=log_dir)
        
        logger = SafetyLogger(config)
        
        # Directory should not be created when logger is disabled
        assert not log_dir.exists()
    
    @pytest.mark.asyncio
    async def test_subdirectory_organization(self, temp_dir):
        """Test organization of logs into subdirectories by date."""
        log_dir = temp_dir / "safety_logs"
        config = SafetyConfig(log_directory=log_dir)
        logger = SafetyLogger(config)
        
        # Log a research goal
        await logger.log_research_goal("Test goal", {"domain": "test"})
        
        # Check that log files are created in the main directory
        log_files = list(log_dir.glob("*.json"))
        assert len(log_files) > 0
        
        # Verify file naming convention (YYYYMMDD_uuid.json)
        log_file = log_files[0]
        assert log_file.name.startswith("202")  # Year
        assert "_" in log_file.name
        assert log_file.suffix == ".json"
    
    def test_default_directory_path(self):
        """Test the default directory path configuration."""
        config = SafetyConfig()
        
        assert config.log_directory == Path(".aicoscientist/safety_logs")
        assert isinstance(config.log_directory, Path)
    
    def test_custom_directory_path(self, temp_dir):
        """Test custom directory path configuration."""
        custom_path = temp_dir / "custom" / "safety" / "path"
        config = SafetyConfig(log_directory=custom_path)
        
        logger = SafetyLogger(config)
        
        assert custom_path.exists()
        assert custom_path.is_dir()