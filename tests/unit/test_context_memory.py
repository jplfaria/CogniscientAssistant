"""Unit tests for ContextMemory class initialization and basic structure."""
import asyncio
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
import pytest

from src.core.context_memory import ContextMemory


class TestContextMemoryInitialization:
    """Test ContextMemory initialization and configuration."""
    
    @pytest.fixture
    def temp_storage_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Cleanup after test
        shutil.rmtree(temp_dir)
    
    def test_context_memory_creation_with_default_path(self):
        """Test creating ContextMemory with default storage path."""
        context_memory = ContextMemory()
        assert context_memory is not None
        assert context_memory.storage_path == Path(".aicoscientist/context")
        
    def test_context_memory_creation_with_custom_path(self, temp_storage_dir):
        """Test creating ContextMemory with custom storage path."""
        context_memory = ContextMemory(storage_path=temp_storage_dir)
        assert context_memory.storage_path == temp_storage_dir
        
    def test_context_memory_creates_directory_structure(self, temp_storage_dir):
        """Test that ContextMemory creates required directory structure."""
        context_memory = ContextMemory(storage_path=temp_storage_dir)
        
        # Check that required directories are created
        assert (temp_storage_dir / "iterations").exists()
        assert (temp_storage_dir / "checkpoints").exists()
        assert (temp_storage_dir / "aggregates").exists()
        assert (temp_storage_dir / "configuration").exists()
        
    def test_context_memory_initializes_indices(self, temp_storage_dir):
        """Test that ContextMemory initializes required indices."""
        context_memory = ContextMemory(storage_path=temp_storage_dir)
        
        # Check that indices are initialized
        assert hasattr(context_memory, '_temporal_index')
        assert hasattr(context_memory, '_component_index')
        assert hasattr(context_memory, '_hypothesis_index')
        assert hasattr(context_memory, '_pattern_index')
        assert hasattr(context_memory, '_performance_index')
        
    def test_context_memory_configuration_initialization(self, temp_storage_dir):
        """Test that ContextMemory initializes with proper configuration."""
        context_memory = ContextMemory(
            storage_path=temp_storage_dir,
            retention_days=60,
            checkpoint_interval_minutes=10,
            max_storage_gb=100
        )
        
        assert context_memory.retention_days == 60
        assert context_memory.checkpoint_interval_minutes == 10
        assert context_memory.max_storage_gb == 100
        
    def test_context_memory_loads_existing_configuration(self, temp_storage_dir):
        """Test that ContextMemory loads configuration from existing storage."""
        # Create initial context memory with custom config
        context_memory1 = ContextMemory(
            storage_path=temp_storage_dir,
            retention_days=45,
            checkpoint_interval_minutes=15
        )
        
        # Create new instance - should load existing config
        context_memory2 = ContextMemory(storage_path=temp_storage_dir)
        assert context_memory2.retention_days == 45
        assert context_memory2.checkpoint_interval_minutes == 15
        
    async def test_context_memory_async_initialization(self, temp_storage_dir):
        """Test async initialization operations."""
        context_memory = ContextMemory(storage_path=temp_storage_dir)
        
        # Test async init method if needed
        await context_memory.initialize()
        assert context_memory.is_initialized
        
    def test_context_memory_validates_storage_path(self):
        """Test that ContextMemory validates storage path permissions."""
        # Try to create in a path without write permissions
        # Use a system directory that exists but doesn't allow writes
        with pytest.raises((PermissionError, OSError)):
            ContextMemory(storage_path=Path("/System/forbidden"))
            
    def test_context_memory_handles_concurrent_initialization(self, temp_storage_dir):
        """Test that multiple ContextMemory instances can coexist safely."""
        context_memory1 = ContextMemory(storage_path=temp_storage_dir)
        context_memory2 = ContextMemory(storage_path=temp_storage_dir)
        
        # Both should be properly initialized without conflicts
        assert context_memory1.storage_path == context_memory2.storage_path
        assert (temp_storage_dir / "iterations").exists()