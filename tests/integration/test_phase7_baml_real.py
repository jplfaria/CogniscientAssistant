"""Real LLM tests for BAML infrastructure behavior."""

import pytest
import os
from baml_client import b
from src.llm.baml_wrapper import BAMLWrapper


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
        context = """
        Recent observations show that certain jellyfish can revert to their polyp stage,
        essentially becoming biologically younger. This process involves cellular
        transdifferentiation.
        """
        
        hypothesis = await wrapper.generate_hypothesis(
            context=context,
            research_goal="Understand biological immortality",
            constraints=["Must be testable", "Focus on cellular mechanisms"]
        )
        
        # o3 should provide detailed reasoning
        assert len(hypothesis.description) > 200
        assert hypothesis.reasoning is not None
        
        # Check for step-by-step thinking markers
        reasoning_text = hypothesis.reasoning.lower()
        assert any(marker in reasoning_text 
                  for marker in ["first", "then", "therefore", "because"])