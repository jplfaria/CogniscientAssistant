"""Tests for ContextMemory iteration tracking functionality."""
import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import json

from src.core.context_memory import (
    ContextMemory, StateUpdate, AgentOutput, MetaReviewStorage
)


class TestIterationTracking:
    """Test iteration tracking functionality."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create a temporary directory for storage."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    async def context_memory(self, temp_storage):
        """Create and initialize ContextMemory instance."""
        memory = ContextMemory(storage_path=temp_storage)
        await memory.initialize()
        return memory
    
    @pytest.mark.asyncio
    async def test_get_current_iteration_number(self, context_memory):
        """Test getting current iteration number."""
        # Initially should return 1
        current = await context_memory.get_current_iteration_number()
        assert current == 1
        
        # Create some iterations
        iterations_dir = context_memory.storage_path / "iterations"
        (iterations_dir / "iteration_001").mkdir(exist_ok=True)
        (iterations_dir / "iteration_002").mkdir(exist_ok=True)
        (iterations_dir / "iteration_005").mkdir(exist_ok=True)  # Gap in sequence
        
        # Should return the highest + 1
        current = await context_memory.get_current_iteration_number()
        assert current == 6
    
    @pytest.mark.asyncio
    async def test_start_new_iteration(self, context_memory):
        """Test starting a new iteration."""
        # Start first iteration
        result = await context_memory.start_new_iteration()
        assert result == 1
        
        # Verify iteration directory was created
        iter_dir = context_memory.storage_path / "iterations" / "iteration_001"
        assert iter_dir.exists()
        
        # Verify iteration metadata was created
        metadata_file = iter_dir / "metadata.json"
        assert metadata_file.exists()
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            assert metadata["iteration_number"] == 1
            assert "started_at" in metadata
            assert metadata["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_complete_iteration(self, context_memory):
        """Test completing an iteration."""
        # Start an iteration first
        iteration_num = await context_memory.start_new_iteration()
        
        # Complete the iteration with summary data
        summary = {
            "hypotheses_generated": 10,
            "hypotheses_ranked": 8,
            "top_hypothesis_score": 0.85,
            "total_reviews": 25
        }
        
        result = await context_memory.complete_iteration(iteration_num, summary)
        assert result is True
        
        # Verify metadata was updated
        metadata_file = context_memory.storage_path / "iterations" / f"iteration_{iteration_num:03d}" / "metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            assert metadata["status"] == "completed"
            assert "completed_at" in metadata
            assert metadata["summary"] == summary
    
    @pytest.mark.asyncio
    async def test_get_iteration_info(self, context_memory):
        """Test retrieving iteration information."""
        # Start and complete an iteration
        iteration_num = await context_memory.start_new_iteration()
        
        # Store some data in the iteration
        state_update = StateUpdate(
            timestamp=datetime.now(),
            update_type="periodic",
            system_statistics={"total_hypotheses": 5},
            orchestration_state={"agent_weights": {"generation": 0.3}}
        )
        await context_memory.store_state_update(state_update)
        
        summary = {"hypotheses_generated": 5}
        await context_memory.complete_iteration(iteration_num, summary)
        
        # Get iteration info
        info = await context_memory.get_iteration_info(iteration_num)
        assert info is not None
        assert info["iteration_number"] == iteration_num
        assert info["status"] == "completed"
        assert info["summary"] == summary
        assert "duration_seconds" in info
    
    @pytest.mark.asyncio
    async def test_list_iterations(self, context_memory):
        """Test listing all iterations."""
        # Create multiple iterations
        iter1 = await context_memory.start_new_iteration()
        await context_memory.complete_iteration(iter1, {"test": 1})
        
        iter2 = await context_memory.start_new_iteration()
        await context_memory.complete_iteration(iter2, {"test": 2})
        
        iter3 = await context_memory.start_new_iteration()
        # Leave iter3 active
        
        # List all iterations
        iterations = await context_memory.list_iterations()
        assert len(iterations) == 3
        
        # Check ordering (should be sorted by iteration number)
        assert iterations[0]["iteration_number"] == 1
        assert iterations[0]["status"] == "completed"
        assert iterations[1]["iteration_number"] == 2
        assert iterations[1]["status"] == "completed"
        assert iterations[2]["iteration_number"] == 3
        assert iterations[2]["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_get_active_iteration(self, context_memory):
        """Test getting the currently active iteration."""
        # Initially no active iteration
        active = await context_memory.get_active_iteration()
        assert active is None
        
        # Start an iteration
        iter_num = await context_memory.start_new_iteration()
        
        # Should now have active iteration
        active = await context_memory.get_active_iteration()
        assert active == iter_num
        
        # Complete it
        await context_memory.complete_iteration(iter_num, {})
        
        # No active iteration again
        active = await context_memory.get_active_iteration()
        assert active is None
    
    @pytest.mark.asyncio
    async def test_iteration_statistics(self, context_memory):
        """Test getting statistics for an iteration."""
        # Start iteration
        iter_num = await context_memory.start_new_iteration()
        
        # Store various data types
        # State updates
        for i in range(3):
            state_update = StateUpdate(
                timestamp=datetime.now() + timedelta(seconds=i),
                update_type="periodic",
                system_statistics={"total_hypotheses": i * 5},
                orchestration_state={}
            )
            await context_memory.store_state_update(state_update)
        
        # Agent outputs
        for i in range(5):
            agent_output = AgentOutput(
                agent_type="generation",
                task_id=f"task_{i}",
                timestamp=datetime.now(),
                results={"hypothesis_count": 2}
            )
            await context_memory.store_agent_output(agent_output)
        
        # Meta review
        meta_review = MetaReviewStorage(
            iteration_number=iter_num,
            timestamp=datetime.now(),
            critique={"patterns": ["good diversity"]},
            research_overview={"synthesis": "promising directions"}
        )
        await context_memory.store_meta_review(meta_review)
        
        # Get statistics
        stats = await context_memory.get_iteration_statistics(iter_num)
        assert stats is not None
        assert stats["state_updates_count"] == 3
        assert stats["agent_outputs_count"] == 5
        assert stats["has_meta_review"] is True
        assert "storage_size_bytes" in stats
        assert "agent_type_breakdown" in stats
        assert stats["agent_type_breakdown"]["generation"] == 5
    
    @pytest.mark.asyncio
    async def test_iteration_directory_structure(self, context_memory):
        """Test that iteration directories maintain proper structure."""
        iter_num = await context_memory.start_new_iteration()
        
        iter_dir = context_memory.storage_path / "iterations" / f"iteration_{iter_num:03d}"
        
        # Check expected subdirectories are created
        expected_dirs = ["agent_outputs", "tournament_data"]
        for dir_name in expected_dirs:
            subdir = iter_dir / dir_name
            assert subdir.exists()
            assert subdir.is_dir()
    
    @pytest.mark.asyncio
    async def test_multiple_active_iterations_prevented(self, context_memory):
        """Test that only one iteration can be active at a time."""
        # Start first iteration
        iter1 = await context_memory.start_new_iteration()
        assert iter1 == 1
        
        # Try to start another without completing the first
        with pytest.raises(RuntimeError, match="already an active iteration"):
            await context_memory.start_new_iteration()
        
        # Complete the first iteration
        await context_memory.complete_iteration(iter1, {})
        
        # Now should be able to start a new one
        iter2 = await context_memory.start_new_iteration()
        assert iter2 == 2
    
    @pytest.mark.asyncio
    async def test_complete_nonexistent_iteration(self, context_memory):
        """Test completing an iteration that doesn't exist."""
        result = await context_memory.complete_iteration(99, {})
        assert result is False
    
    @pytest.mark.asyncio
    async def test_iteration_with_checkpoint(self, context_memory):
        """Test that checkpoints are associated with iterations."""
        # Start iteration
        iter_num = await context_memory.start_new_iteration()
        
        # Create a checkpoint
        state_update = StateUpdate(
            timestamp=datetime.now(),
            update_type="checkpoint",
            system_statistics={"total_hypotheses": 10},
            orchestration_state={"agent_weights": {}},
            checkpoint_data={"in_flight_tasks": []}
        )
        checkpoint_id = await context_memory.create_checkpoint(state_update)
        
        # Get iteration info - should include checkpoint reference
        info = await context_memory.get_iteration_info(iter_num)
        assert "checkpoints" in info
        assert checkpoint_id in info["checkpoints"]