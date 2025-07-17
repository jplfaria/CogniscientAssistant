"""Tests for ContextMemory key-value store operations."""
import pytest
import asyncio
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

from src.core.context_memory import ContextMemory


@pytest.fixture
def temp_storage_path():
    """Create a temporary directory for test storage."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
async def context_memory(temp_storage_path):
    """Create and initialize a ContextMemory instance for testing."""
    memory = ContextMemory(storage_path=temp_storage_path)
    await memory.initialize()
    return memory


@pytest.mark.asyncio
async def test_set_get_simple_value(context_memory):
    """Test basic set and get operations."""
    # Set a value
    success = await context_memory.set("test_key", "test_value")
    assert success is True
    
    # Get the value
    value = await context_memory.get("test_key")
    assert value == "test_value"


@pytest.mark.asyncio
async def test_get_nonexistent_key(context_memory):
    """Test getting a non-existent key returns None."""
    value = await context_memory.get("nonexistent_key")
    assert value is None


@pytest.mark.asyncio
async def test_set_get_complex_value(context_memory):
    """Test storing and retrieving complex data structures."""
    complex_data = {
        "hypothesis_id": "h123",
        "confidence": 0.85,
        "metadata": {"source": "generation_agent", "iteration": 5},
        "created_at": datetime.now().isoformat()
    }
    
    success = await context_memory.set("hypothesis_data", complex_data)
    assert success is True
    
    retrieved = await context_memory.get("hypothesis_data")
    assert retrieved == complex_data
    assert retrieved["confidence"] == 0.85
    assert retrieved["metadata"]["iteration"] == 5


@pytest.mark.asyncio
async def test_update_existing_key(context_memory):
    """Test updating an existing key."""
    # Set initial value
    await context_memory.set("counter", 1)
    
    # Update value
    success = await context_memory.set("counter", 2)
    assert success is True
    
    # Verify update
    value = await context_memory.get("counter")
    assert value == 2


@pytest.mark.asyncio
async def test_delete_key(context_memory):
    """Test deleting a key."""
    # Set a value
    await context_memory.set("temp_key", "temp_value")
    
    # Delete the key
    success = await context_memory.delete("temp_key")
    assert success is True
    
    # Verify deletion
    value = await context_memory.get("temp_key")
    assert value is None


@pytest.mark.asyncio
async def test_delete_nonexistent_key(context_memory):
    """Test deleting a non-existent key returns False."""
    success = await context_memory.delete("nonexistent_key")
    assert success is False


@pytest.mark.asyncio
async def test_exists_key(context_memory):
    """Test checking if a key exists."""
    # Key doesn't exist
    exists = await context_memory.exists("test_key")
    assert exists is False
    
    # Set a value
    await context_memory.set("test_key", "test_value")
    
    # Key exists
    exists = await context_memory.exists("test_key")
    assert exists is True


@pytest.mark.asyncio
async def test_list_keys(context_memory):
    """Test listing all keys."""
    # Initially empty
    keys = await context_memory.list_keys()
    assert keys == []
    
    # Add some keys
    await context_memory.set("key1", "value1")
    await context_memory.set("key2", "value2")
    await context_memory.set("key3", "value3")
    
    # List keys
    keys = await context_memory.list_keys()
    assert set(keys) == {"key1", "key2", "key3"}


@pytest.mark.asyncio
async def test_list_keys_with_prefix(context_memory):
    """Test listing keys with a specific prefix."""
    # Add keys with different prefixes
    await context_memory.set("hypothesis_001", {"id": "h001"})
    await context_memory.set("hypothesis_002", {"id": "h002"})
    await context_memory.set("ranking_001", {"elo": 1500})
    await context_memory.set("agent_state", {"active": True})
    
    # List keys with prefix
    hypothesis_keys = await context_memory.list_keys(prefix="hypothesis_")
    assert set(hypothesis_keys) == {"hypothesis_001", "hypothesis_002"}
    
    ranking_keys = await context_memory.list_keys(prefix="ranking_")
    assert ranking_keys == ["ranking_001"]


@pytest.mark.asyncio
async def test_batch_operations(context_memory):
    """Test batch set and get operations."""
    # Batch set
    data = {
        "key1": "value1",
        "key2": {"nested": "data"},
        "key3": [1, 2, 3]
    }
    
    success = await context_memory.batch_set(data)
    assert success is True
    
    # Batch get
    keys = ["key1", "key2", "key3", "nonexistent"]
    results = await context_memory.batch_get(keys)
    
    assert results["key1"] == "value1"
    assert results["key2"] == {"nested": "data"}
    assert results["key3"] == [1, 2, 3]
    assert results["nonexistent"] is None


@pytest.mark.asyncio
async def test_clear_all_keys(context_memory):
    """Test clearing all key-value pairs."""
    # Add some keys
    await context_memory.set("key1", "value1")
    await context_memory.set("key2", "value2")
    await context_memory.set("key3", "value3")
    
    # Clear all
    success = await context_memory.clear()
    assert success is True
    
    # Verify all cleared
    keys = await context_memory.list_keys()
    assert keys == []


@pytest.mark.asyncio
async def test_persistence_across_instances(temp_storage_path):
    """Test that key-value data persists across different instances."""
    # First instance
    memory1 = ContextMemory(storage_path=temp_storage_path)
    await memory1.initialize()
    await memory1.set("persistent_key", {"data": "should_persist"})
    
    # Second instance
    memory2 = ContextMemory(storage_path=temp_storage_path)
    await memory2.initialize()
    value = await memory2.get("persistent_key")
    assert value == {"data": "should_persist"}


@pytest.mark.asyncio
async def test_concurrent_operations(context_memory):
    """Test concurrent key-value operations."""
    async def set_value(key, value):
        return await context_memory.set(key, value)
    
    async def get_value(key):
        return await context_memory.get(key)
    
    # Concurrent sets
    tasks = [
        set_value(f"concurrent_{i}", i)
        for i in range(10)
    ]
    results = await asyncio.gather(*tasks)
    assert all(results)
    
    # Concurrent gets
    tasks = [
        get_value(f"concurrent_{i}")
        for i in range(10)
    ]
    values = await asyncio.gather(*tasks)
    assert values == list(range(10))


@pytest.mark.asyncio
async def test_large_value_storage(context_memory):
    """Test storing large values."""
    # Create a large data structure (1MB+)
    large_data = {
        "large_list": list(range(100000)),
        "metadata": {
            "size": "large",
            "test": "performance"
        }
    }
    
    success = await context_memory.set("large_key", large_data)
    assert success is True
    
    retrieved = await context_memory.get("large_key")
    assert retrieved == large_data
    assert len(retrieved["large_list"]) == 100000


@pytest.mark.asyncio
async def test_key_validation(context_memory):
    """Test key validation for invalid characters."""
    # Test various invalid keys
    invalid_keys = [
        "",  # Empty key
        " ",  # Whitespace
        "key with spaces",
        "key/with/slashes",
        "key\\with\\backslashes",
        "key:with:colons",
        "key*with*asterisks",
        "key?with?questions",
        "key|with|pipes",
        None  # None key
    ]
    
    for key in invalid_keys:
        with pytest.raises((ValueError, TypeError)):
            await context_memory.set(key, "value")


@pytest.mark.asyncio
async def test_value_serialization_errors(context_memory):
    """Test handling of non-serializable values."""
    # Non-serializable value (function)
    def non_serializable():
        pass
    
    with pytest.raises(TypeError):
        await context_memory.set("bad_value", non_serializable)


@pytest.mark.asyncio 
async def test_storage_size_tracking(context_memory):
    """Test tracking storage size for key-value pairs."""
    # Get initial size
    initial_size = await context_memory.get_kv_storage_size()
    assert initial_size == 0
    
    # Add some data
    await context_memory.set("key1", "a" * 1000)  # 1KB string
    await context_memory.set("key2", {"data": "b" * 1000})
    
    # Check size increased
    current_size = await context_memory.get_kv_storage_size()
    assert current_size > initial_size
    assert current_size >= 2000  # At least 2KB


@pytest.mark.asyncio
async def test_namespace_isolation(context_memory):
    """Test that key-value store is isolated from other storage."""
    # Set a key-value pair
    await context_memory.set("test_key", "test_value")
    
    # Verify it doesn't interfere with other storage operations
    from src.core.context_memory import StateUpdate
    state_update = StateUpdate(
        timestamp=datetime.now(),
        update_type="periodic",
        system_statistics={},
        orchestration_state={}
    )
    
    result = await context_memory.store_state_update(state_update)
    assert result.success
    
    # Key-value pair should still exist
    value = await context_memory.get("test_key")
    assert value == "test_value"