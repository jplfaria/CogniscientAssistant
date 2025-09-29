"""Test checkpoint functionality for ContextMemory."""
import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import json
from unittest.mock import patch, MagicMock
import shutil

from src.core.context_memory import ContextMemory, StateUpdate, RecoveryState


@pytest.fixture
async def context_memory(tmp_path):
    """Create a ContextMemory instance for testing."""
    cm = ContextMemory(
        storage_path=tmp_path / "test_context",
        retention_days=30,
        checkpoint_interval_minutes=5,
        max_storage_gb=50
    )
    await cm.initialize()
    return cm


@pytest.fixture
def state_update():
    """Create a sample StateUpdate."""
    return StateUpdate(
        timestamp=datetime.now(),
        update_type="checkpoint",
        system_statistics={
            "total_hypotheses": 100,
            "hypotheses_by_state": {"generated": 50, "reviewed": 30, "ranked": 20},
            "pending_reviews": 10,
            "tournament_progress": 0.6,
            "agent_effectiveness": {"generation": 0.8, "reflection": 0.75}
        },
        orchestration_state={
            "agent_weights": {"generation": 0.3, "reflection": 0.3, "ranking": 0.4},
            "resource_allocation": {"generation": 100, "reflection": 150, "ranking": 200},
            "queue_statistics": {"pending": 25, "in_progress": 5, "completed": 70},
            "strategic_focus": "diversity"
        },
        checkpoint_data={
            "in_flight_tasks": [
                {"task_id": "task1", "type": "generate", "status": "executing"},
                {"task_id": "task2", "type": "review", "status": "pending"}
            ],
            "recovery_metadata": {"session_id": "session123", "version": "1.0"}
        }
    )


@pytest.mark.asyncio
async def test_create_checkpoint_basic(context_memory, state_update):
    """Test basic checkpoint creation."""
    # Create a checkpoint
    checkpoint_id = await context_memory.create_checkpoint(state_update)
    
    assert checkpoint_id is not None
    assert checkpoint_id.startswith("ckpt_")
    
    # Verify checkpoint file exists
    checkpoint_file = context_memory.storage_path / "checkpoints" / checkpoint_id / "checkpoint.json"
    assert checkpoint_file.exists()
    
    # Verify checkpoint content
    with open(checkpoint_file, 'r') as f:
        checkpoint_data = json.load(f)
    
    assert checkpoint_data["checkpoint_id"] == checkpoint_id
    assert checkpoint_data["timestamp"] == state_update.timestamp.isoformat()
    assert checkpoint_data["system_statistics"] == state_update.system_statistics
    assert checkpoint_data["orchestration_state"] == state_update.orchestration_state
    assert checkpoint_data["checkpoint_data"] == state_update.checkpoint_data
    assert "created_at" in checkpoint_data


@pytest.mark.asyncio
async def test_create_checkpoint_with_active_iteration(context_memory, state_update):
    """Test checkpoint creation linked to active iteration."""
    # Start a new iteration
    iteration_num = await context_memory.start_new_iteration()
    
    # Create a checkpoint
    checkpoint_id = await context_memory.create_checkpoint(state_update)
    
    # Verify checkpoint is linked to the iteration
    metadata_file = context_memory.storage_path / "iterations" / f"iteration_{iteration_num:03d}" / "metadata.json"
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    assert "checkpoints" in metadata
    assert checkpoint_id in metadata["checkpoints"]


@pytest.mark.asyncio
async def test_recover_from_checkpoint(context_memory, state_update):
    """Test recovery from checkpoint."""
    # Create a checkpoint
    checkpoint_id = await context_memory.create_checkpoint(state_update)
    
    # Recover from checkpoint
    recovery_state = await context_memory.recover_from_checkpoint(checkpoint_id)
    
    assert recovery_state is not None
    assert isinstance(recovery_state, RecoveryState)
    assert recovery_state.checkpoint_timestamp == state_update.timestamp
    assert recovery_state.system_configuration == state_update.orchestration_state
    assert recovery_state.active_tasks == state_update.checkpoint_data["in_flight_tasks"]
    assert recovery_state.completed_work["hypotheses"] == state_update.system_statistics["total_hypotheses"]
    assert recovery_state.data_integrity["valid"] is True


@pytest.mark.asyncio
async def test_recover_from_nonexistent_checkpoint(context_memory):
    """Test recovery from non-existent checkpoint."""
    recovery_state = await context_memory.recover_from_checkpoint("ckpt_nonexistent")
    assert recovery_state is None


@pytest.mark.asyncio
async def test_checkpoint_with_versioning(context_memory):
    """Test checkpoint versioning and metadata."""
    # Create multiple checkpoints
    checkpoint_ids = []
    for i in range(3):
        state_update = StateUpdate(
            timestamp=datetime.now() + timedelta(minutes=i),
            update_type="checkpoint",
            system_statistics={"total_hypotheses": 100 + i * 10},
            orchestration_state={"version": f"1.{i}"},
            checkpoint_data={"iteration": i}
        )
        checkpoint_id = await context_memory.create_checkpoint(state_update)
        checkpoint_ids.append(checkpoint_id)
        await asyncio.sleep(0.1)  # Small delay to ensure different timestamps
    
    # Verify all checkpoints exist
    checkpoints_dir = context_memory.storage_path / "checkpoints"
    checkpoint_dirs = list(checkpoints_dir.iterdir())
    assert len(checkpoint_dirs) >= 3
    
    # Verify we can recover from each checkpoint
    for i, checkpoint_id in enumerate(checkpoint_ids):
        recovery_state = await context_memory.recover_from_checkpoint(checkpoint_id)
        assert recovery_state is not None
        assert recovery_state.system_configuration["version"] == f"1.{i}"


@pytest.mark.asyncio
async def test_checkpoint_automatic_interval(context_memory, state_update):
    """Test automatic checkpoint creation based on interval."""
    # This test verifies the checkpoint interval configuration
    assert context_memory.checkpoint_interval_minutes == 5
    
    # Create initial checkpoint
    checkpoint1_id = await context_memory.create_checkpoint(state_update)
    
    # Modify state update for second checkpoint
    state_update.timestamp = datetime.now() + timedelta(minutes=6)
    state_update.system_statistics["total_hypotheses"] = 150
    
    # Create second checkpoint after interval
    checkpoint2_id = await context_memory.create_checkpoint(state_update)
    
    assert checkpoint1_id != checkpoint2_id
    
    # Both checkpoints should exist
    assert (context_memory.storage_path / "checkpoints" / checkpoint1_id).exists()
    assert (context_memory.storage_path / "checkpoints" / checkpoint2_id).exists()


@pytest.mark.asyncio
async def test_checkpoint_size_validation(context_memory, state_update):
    """Test checkpoint size tracking and validation."""
    # Create a checkpoint with large data
    large_data = {"data": "x" * 10000}  # 10KB of data
    state_update.checkpoint_data["large_data"] = large_data
    
    checkpoint_id = await context_memory.create_checkpoint(state_update)
    
    # Verify checkpoint was created
    checkpoint_file = context_memory.storage_path / "checkpoints" / checkpoint_id / "checkpoint.json"
    assert checkpoint_file.exists()
    
    # Check file size
    file_size = checkpoint_file.stat().st_size
    assert file_size > 10000  # Should be larger than our data


@pytest.mark.asyncio
async def test_checkpoint_list_retrieval(context_memory):
    """Test listing all checkpoints."""
    # Create multiple checkpoints
    checkpoint_ids = []
    for i in range(3):
        state_update = StateUpdate(
            timestamp=datetime.now() + timedelta(minutes=i),
            update_type="checkpoint",
            system_statistics={"checkpoint_num": i},
            orchestration_state={},
            checkpoint_data={}
        )
        checkpoint_id = await context_memory.create_checkpoint(state_update)
        checkpoint_ids.append(checkpoint_id)
    
    # Get list of checkpoints
    checkpoints = await context_memory.list_checkpoints()
    
    assert len(checkpoints) >= 3
    for checkpoint in checkpoints:
        assert "checkpoint_id" in checkpoint
        assert "timestamp" in checkpoint
        assert "created_at" in checkpoint
        assert checkpoint["checkpoint_id"] in checkpoint_ids


@pytest.mark.asyncio
async def test_checkpoint_cleanup(context_memory):
    """Test checkpoint cleanup based on retention policy."""
    # Create old checkpoint
    old_timestamp = datetime.now() - timedelta(days=35)
    old_state_update = StateUpdate(
        timestamp=old_timestamp,
        update_type="checkpoint",
        system_statistics={},
        orchestration_state={},
        checkpoint_data={}
    )
    
    with patch('src.core.context_memory.datetime') as mock_datetime:
        mock_datetime.now.return_value = old_timestamp
        mock_datetime.fromisoformat = datetime.fromisoformat
        old_checkpoint_id = await context_memory.create_checkpoint(old_state_update)
    
    # Create recent checkpoint
    recent_state_update = StateUpdate(
        timestamp=datetime.now(),
        update_type="checkpoint",
        system_statistics={},
        orchestration_state={},
        checkpoint_data={}
    )
    recent_checkpoint_id = await context_memory.create_checkpoint(recent_state_update)
    
    # Run cleanup
    cleaned_count = await context_memory.cleanup_old_checkpoints()
    
    # Old checkpoint should be cleaned up
    assert cleaned_count >= 1
    assert not (context_memory.storage_path / "checkpoints" / old_checkpoint_id).exists()
    assert (context_memory.storage_path / "checkpoints" / recent_checkpoint_id).exists()


@pytest.mark.asyncio
async def test_checkpoint_validation(context_memory, state_update):
    """Test checkpoint data validation."""
    # Create valid checkpoint
    checkpoint_id = await context_memory.create_checkpoint(state_update)
    
    # Validate checkpoint
    is_valid = await context_memory.validate_checkpoint(checkpoint_id)
    assert is_valid is True
    
    # Corrupt checkpoint file
    checkpoint_file = context_memory.storage_path / "checkpoints" / checkpoint_id / "checkpoint.json"
    with open(checkpoint_file, 'w') as f:
        f.write("corrupted data")
    
    # Validation should fail
    is_valid = await context_memory.validate_checkpoint(checkpoint_id)
    assert is_valid is False


@pytest.mark.asyncio
async def test_get_latest_checkpoint(context_memory):
    """Test retrieving the latest checkpoint."""
    # Create multiple checkpoints
    checkpoint_ids = []
    for i in range(3):
        state_update = StateUpdate(
            timestamp=datetime.now() + timedelta(minutes=i),
            update_type="checkpoint",
            system_statistics={"index": i},
            orchestration_state={},
            checkpoint_data={}
        )
        checkpoint_id = await context_memory.create_checkpoint(state_update)
        checkpoint_ids.append(checkpoint_id)
        await asyncio.sleep(0.1)
    
    # Get latest checkpoint
    latest_checkpoint = await context_memory.get_latest_checkpoint()
    
    assert latest_checkpoint is not None
    assert latest_checkpoint["checkpoint_id"] == checkpoint_ids[-1]
    assert latest_checkpoint["system_statistics"]["index"] == 2


@pytest.mark.asyncio
async def test_checkpoint_recovery_with_corrupted_data(context_memory, state_update):
    """Test recovery behavior with corrupted checkpoint data."""
    # Create checkpoint
    checkpoint_id = await context_memory.create_checkpoint(state_update)
    
    # Corrupt the checkpoint file
    checkpoint_file = context_memory.storage_path / "checkpoints" / checkpoint_id / "checkpoint.json"
    with open(checkpoint_file, 'w') as f:
        json.dump({"partial": "data"}, f)  # Missing required fields
    
    # Recovery should handle gracefully
    recovery_state = await context_memory.recover_from_checkpoint(checkpoint_id)
    assert recovery_state is None


@pytest.mark.asyncio
async def test_checkpoint_creation_failure_handling(context_memory, state_update):
    """Test checkpoint creation with storage failure."""
    # Make checkpoints directory read-only
    checkpoints_dir = context_memory.storage_path / "checkpoints"
    checkpoints_dir.chmod(0o444)
    
    try:
        # Attempt to create checkpoint should handle failure gracefully
        checkpoint_id = await context_memory.create_checkpoint(state_update)
        assert checkpoint_id is None
    finally:
        # Restore permissions
        checkpoints_dir.chmod(0o755)