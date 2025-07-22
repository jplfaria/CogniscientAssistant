"""Real LLM tests for BAML infrastructure behavior."""

import pytest
import os
from dotenv import load_dotenv
from baml_client.baml_client import b
from src.llm.baml_wrapper import BAMLWrapper

# Load environment variables
load_dotenv()


@pytest.mark.real_llm
class TestBAMLRealBehavior:
    """Test actual BAML behavior with real models."""
    
    @pytest.mark.asyncio
    async def test_baml_with_real_models(self):
        """Test BAML functions with different real models."""
        wrapper = BAMLWrapper()
        
        # Test research goal parsing with different models
        goal = "Develop a cure for aging using nanotechnology"
        
        result = await wrapper.parse_research_goal(
            natural_language_goal=goal,
            domain_context="biomedical engineering"
        )
        
        # Verify structured output
        assert result.primary_objective is not None
        assert len(result.sub_objectives) >= 2
        assert len(result.key_terms) >= 3
        
        # Check for expected concepts
        key_terms_text = " ".join(result.key_terms).lower()
        assert any(term in key_terms_text for term in ["nano", "aging", "longevity"])
        
    @pytest.mark.asyncio
    async def test_o3_reasoning_in_baml(self):
        """Test that o3 exhibits reasoning behavior through BAML."""
        wrapper = BAMLWrapper()
        
        # Test hypothesis generation with complex prompt
        goal = """
        Understand biological immortality based on recent observations that certain
        jellyfish can revert to their polyp stage, essentially becoming biologically
        younger through cellular transdifferentiation.
        """
        
        hypothesis = await wrapper.generate_hypothesis(
            goal=goal,
            constraints=["Must be testable", "Focus on cellular mechanisms"],
            existing_hypotheses=[],  # No existing hypotheses
            focus_area="cellular rejuvenation mechanisms",
            generation_method="literature_based"  # Required parameter
        )
        
        # o3 should provide detailed reasoning
        assert len(hypothesis.full_description) > 200
        assert hypothesis.reasoning is not None
        
        # Check for reasoning markers - o3 might use different styles
        reasoning_text = hypothesis.reasoning.lower()
        # More flexible check - look for any analytical/reasoning markers
        reasoning_markers = [
            "first", "then", "therefore", "because", "thus", "hence",
            "suggests", "shows", "combining", "literature", "facts", "implies"
        ]
        assert any(marker in reasoning_text for marker in reasoning_markers)