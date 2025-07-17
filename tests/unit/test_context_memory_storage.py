"""Unit tests for ContextMemory file-based storage backend."""
import asyncio
import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
import pytest

from src.core.context_memory import ContextMemory, StateUpdate, AgentOutput, MetaReviewStorage


class TestContextMemoryStorage:
    """Test ContextMemory storage operations."""
    
    @pytest.fixture
    def temp_storage_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Cleanup after test
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    async def initialized_memory(self, temp_storage_dir):
        """Create and initialize a ContextMemory instance."""
        memory = ContextMemory(storage_path=temp_storage_dir)
        await memory.initialize()
        return memory
    
    async def test_store_state_update(self, initialized_memory):
        """Test storing a state update from Supervisor Agent."""
        state_update = StateUpdate(
            timestamp=datetime.now(),
            update_type="periodic",
            system_statistics={
                "total_hypotheses": 42,
                "hypotheses_by_state": {"pending": 10, "reviewed": 32},
                "pending_reviews": 5,
                "tournament_progress": 0.75,
                "agent_effectiveness": {"generation": 0.8, "reflection": 0.9}
            },
            orchestration_state={
                "agent_weights": {"generation": 1.0, "reflection": 1.2},
                "resource_allocation": {"generation": 0.4, "reflection": 0.3},
                "queue_statistics": {"pending": 15, "processing": 3},
                "strategic_focus": "exploration"
            },
            checkpoint_data=None
        )
        
        # Store the update
        result = await initialized_memory.store_state_update(state_update)
        assert result.success
        assert result.storage_path is not None
        
    async def test_store_agent_output(self, initialized_memory):
        """Test storing output from a specialized agent."""
        agent_output = AgentOutput(
            agent_type="generation",
            task_id="task-123",
            timestamp=datetime.now(),
            results={
                "primary_output": ["hypothesis1", "hypothesis2"],
                "metadata": {"strategy": "literature_based"},
                "confidence_score": 0.85,
                "resource_consumed": 0.25
            },
            state_data={
                "internal_state": {"last_search_query": "quantum computing"},
                "continuation_token": None
            }
        )
        
        # Store the output
        result = await initialized_memory.store_agent_output(agent_output)
        assert result.success
        assert result.storage_path is not None
        
    async def test_store_meta_review(self, initialized_memory):
        """Test storing meta-review data."""
        meta_review = MetaReviewStorage(
            iteration_number=5,
            timestamp=datetime.now(),
            critique={
                "common_patterns": ["overreliance on assumptions", "lack of experimental detail"],
                "agent_feedback": {
                    "generation": "Increase diversity of sources",
                    "reflection": "Be more critical of methodology"
                },
                "iteration_improvements": {"hypothesis_quality": 0.15}
            },
            research_overview={
                "synthesis": "Good progress on theoretical framework",
                "research_areas": ["quantum algorithms", "error correction"],
                "next_priorities": ["experimental validation", "scalability analysis"]
            }
        )
        
        # Store the meta-review
        result = await initialized_memory.store_meta_review(meta_review)
        assert result.success
        assert result.storage_path is not None
        
    async def test_retrieve_latest_state(self, initialized_memory):
        """Test retrieving the latest system state."""
        # First store some state
        state_update = StateUpdate(
            timestamp=datetime.now(),
            update_type="periodic",
            system_statistics={
                "total_hypotheses": 50,
                "hypotheses_by_state": {"pending": 5, "reviewed": 45},
                "pending_reviews": 2,
                "tournament_progress": 0.9,
                "agent_effectiveness": {}
            },
            orchestration_state={
                "agent_weights": {},
                "resource_allocation": {},
                "queue_statistics": {},
                "strategic_focus": "refinement"
            },
            checkpoint_data=None
        )
        await initialized_memory.store_state_update(state_update)
        
        # Retrieve latest state
        retrieved = await initialized_memory.retrieve_state(request_type="latest")
        assert retrieved is not None
        assert retrieved.content["system_state"]["strategic_focus"] == "refinement"
        assert retrieved.content["system_state"]["tournament_progress"] == 0.9
        
    async def test_retrieve_feedback_by_iteration(self, initialized_memory):
        """Test retrieving feedback for a specific iteration."""
        # Store meta-review
        meta_review = MetaReviewStorage(
            iteration_number=3,
            timestamp=datetime.now(),
            critique={
                "common_patterns": ["pattern1"],
                "agent_feedback": {"generation": "feedback1"},
                "iteration_improvements": {}
            },
            research_overview={
                "synthesis": "summary",
                "research_areas": ["area1"],
                "next_priorities": ["priority1"]
            }
        )
        await initialized_memory.store_meta_review(meta_review)
        
        # Retrieve feedback
        feedback = await initialized_memory.retrieve_feedback(
            iteration_requested=3,
            agent_type="generation"
        )
        assert feedback is not None
        assert "feedback1" in feedback.feedback_content["agent_specific"]["generation"]
        
    async def test_create_checkpoint(self, initialized_memory):
        """Test creating a recovery checkpoint."""
        # Add some state
        state_update = StateUpdate(
            timestamp=datetime.now(),
            update_type="checkpoint",
            system_statistics={
                "total_hypotheses": 100,
                "hypotheses_by_state": {},
                "pending_reviews": 0,
                "tournament_progress": 1.0,
                "agent_effectiveness": {}
            },
            orchestration_state={
                "agent_weights": {},
                "resource_allocation": {},
                "queue_statistics": {},
                "strategic_focus": "complete"
            },
            checkpoint_data={
                "in_flight_tasks": [],
                "recovery_metadata": {"session_id": "test-session"}
            }
        )
        
        # Create checkpoint
        checkpoint_id = await initialized_memory.create_checkpoint(state_update)
        assert checkpoint_id is not None
        assert checkpoint_id.startswith("ckpt_")
        
    async def test_recover_from_checkpoint(self, initialized_memory):
        """Test recovering system state from a checkpoint."""
        # Create a checkpoint
        state_update = StateUpdate(
            timestamp=datetime.now(),
            update_type="checkpoint",
            system_statistics={
                "total_hypotheses": 75,
                "hypotheses_by_state": {"reviewed": 75},
                "pending_reviews": 0,
                "tournament_progress": 1.0,
                "agent_effectiveness": {}
            },
            orchestration_state={
                "agent_weights": {"generation": 1.5},
                "resource_allocation": {},
                "queue_statistics": {},
                "strategic_focus": "evaluation"
            },
            checkpoint_data={
                "in_flight_tasks": [{"task_id": "task-999", "state": "processing"}],
                "recovery_metadata": {"important": "data"}
            }
        )
        checkpoint_id = await initialized_memory.create_checkpoint(state_update)
        
        # Recover from checkpoint
        recovery_state = await initialized_memory.recover_from_checkpoint(checkpoint_id)
        assert recovery_state is not None
        assert recovery_state.system_configuration["strategic_focus"] == "evaluation"
        assert len(recovery_state.active_tasks) == 1
        assert recovery_state.active_tasks[0]["task_id"] == "task-999"
        
    async def test_storage_persistence_across_instances(self, temp_storage_dir):
        """Test that stored data persists across ContextMemory instances."""
        # First instance stores data
        memory1 = ContextMemory(storage_path=temp_storage_dir)
        await memory1.initialize()
        
        state_update = StateUpdate(
            timestamp=datetime.now(),
            update_type="periodic",
            system_statistics={
                "total_hypotheses": 25,
                "hypotheses_by_state": {},
                "pending_reviews": 3,
                "tournament_progress": 0.5,
                "agent_effectiveness": {}
            },
            orchestration_state={
                "agent_weights": {},
                "resource_allocation": {},
                "queue_statistics": {},
                "strategic_focus": "testing"
            },
            checkpoint_data=None
        )
        await memory1.store_state_update(state_update)
        
        # Second instance reads data
        memory2 = ContextMemory(storage_path=temp_storage_dir)
        await memory2.initialize()
        
        retrieved = await memory2.retrieve_state(request_type="latest")
        assert retrieved is not None
        assert retrieved.content["system_state"]["strategic_focus"] == "testing"
        
    async def test_concurrent_write_handling(self, initialized_memory):
        """Test handling concurrent writes to storage."""
        # Create multiple state updates
        updates = []
        for i in range(5):
            update = StateUpdate(
                timestamp=datetime.now(),
                update_type="periodic",
                system_statistics={
                    "total_hypotheses": i * 10,
                    "hypotheses_by_state": {},
                    "pending_reviews": i,
                    "tournament_progress": i * 0.2,
                    "agent_effectiveness": {}
                },
                orchestration_state={
                    "agent_weights": {},
                    "resource_allocation": {},
                    "queue_statistics": {},
                    "strategic_focus": f"test-{i}"
                },
                checkpoint_data=None
            )
            updates.append(update)
        
        # Store concurrently
        tasks = [initialized_memory.store_state_update(u) for u in updates]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(r.success for r in results)
        assert len(set(r.storage_path for r in results)) == 5  # All unique paths