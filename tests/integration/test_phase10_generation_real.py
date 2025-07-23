"""Phase 10 Real LLM Tests - Generation Agent.

This module tests the Generation Agent's actual behavior with real LLMs
to verify that it exhibits expected AI capabilities like creativity,
scientific validity, and coherent hypothesis generation.
"""

import pytest
from uuid import uuid4

from src.agents.generation import GenerationAgent
from src.core.models import ResearchGoal, HypothesisCategory
from src.core.task_queue import TaskQueue
from src.core.context_memory import ContextMemory
from src.llm.argo_provider import ArgoLLMProvider


@pytest.mark.real_llm
class TestGenerationAgentRealLLM:
    """Tests for Generation Agent with real LLM models."""
    
    async def test_hypothesis_creativity(self, real_llm_provider):
        """Test that o3 exhibits creative hypothesis generation.
        
        Verifies:
        - Novel connections between concepts
        - Non-obvious approaches to problems
        - Paradigm-shifting potential
        - Creative use of analogies
        """
        # Create real agent with o3
        task_queue = TaskQueue()
        context_memory = ContextMemory()
        
        generation_agent = GenerationAgent(
            task_queue=task_queue,
            context_memory=context_memory,
            llm_provider=real_llm_provider,
            config={'enable_safety_logging': False}  # Disable for testing
        )
        
        # Complex research goal requiring creativity
        research_goal = ResearchGoal(
            description="Develop innovative approaches to reverse cellular aging using quantum biology principles",
            constraints=["Must be theoretically grounded", "Should suggest testable predictions"]
        )
        
        # Generate hypothesis using debate method (encourages creativity)
        hypothesis = await generation_agent.generate_hypothesis(
            research_goal=research_goal,
            generation_method='debate'
        )
        
        # Verify creative elements
        assert hypothesis is not None
        assert len(hypothesis.summary) > 50  # Substantial summary
        assert len(hypothesis.full_description) > 200  # Detailed description
        
        # Check for creative markers
        description_lower = hypothesis.full_description.lower()
        creative_markers = [
            'quantum', 'entanglement', 'coherence', 'novel', 'innovative',
            'paradigm', 'unexpected', 'counterintuitive', 'breakthrough'
        ]
        
        # Should contain at least 2 creative markers
        markers_found = sum(1 for marker in creative_markers if marker in description_lower)
        assert markers_found >= 2, f"Expected creative language, found {markers_found} markers"
        
        # Verify it's not just regurgitating known facts
        assert hypothesis.novelty_claim
        assert len(hypothesis.novelty_claim) > 30
        assert any(word in hypothesis.novelty_claim.lower() 
                  for word in ['novel', 'new', 'first', 'unique', 'innovative'])
        
        # Check assumptions show creative thinking
        assert len(hypothesis.assumptions) >= 3
        # At least one assumption should be non-trivial
        non_trivial_assumption = any(
            len(assumption) > 50 and 
            any(term in assumption.lower() for term in ['quantum', 'mechanism', 'process'])
            for assumption in hypothesis.assumptions
        )
        assert non_trivial_assumption, "Expected at least one complex assumption"
    
    async def test_hypothesis_scientific_validity(self, real_llm_provider):
        """Test that Claude generates scientifically valid hypotheses.
        
        Verifies:
        - Logical consistency
        - Grounding in established science
        - Proper experimental design
        - Falsifiable predictions
        """
        # Create real agent with Claude
        task_queue = TaskQueue()
        context_memory = ContextMemory()
        
        # Configure to use Claude
        claude_provider = ArgoLLMProvider(
            default_model='claude-3-opus-20240229',
            api_key=real_llm_provider.api_key,
            argo_proxy_url=real_llm_provider.argo_proxy_url
        )
        
        generation_agent = GenerationAgent(
            task_queue=task_queue,
            context_memory=context_memory,
            llm_provider=claude_provider,
            config={'enable_safety_logging': False}
        )
        
        # Scientific research goal
        research_goal = ResearchGoal(
            description="Investigate the role of epigenetic modifications in transgenerational trauma inheritance",
            constraints=[
                "Must propose specific molecular mechanisms",
                "Should identify measurable biomarkers",
                "Include ethical considerations"
            ]
        )
        
        # Generate using literature-based method for scientific grounding
        hypothesis = await generation_agent.generate_hypothesis(
            research_goal=research_goal,
            generation_method='literature_based'
        )
        
        # Verify scientific validity
        assert hypothesis.category in [
            HypothesisCategory.MECHANISTIC,
            HypothesisCategory.BIOMARKER,
            HypothesisCategory.DIAGNOSTIC
        ]
        
        # Check experimental protocol
        protocol = hypothesis.experimental_protocol
        assert protocol is not None
        assert len(protocol.methodology) > 100  # Detailed methodology
        assert len(protocol.success_metrics) >= 2  # Multiple metrics
        assert len(protocol.required_resources) >= 3  # Realistic resources
        
        # Verify specific molecular mechanisms mentioned
        full_text = hypothesis.full_description + ' '.join(hypothesis.assumptions)
        molecular_terms = [
            'methylation', 'acetylation', 'histone', 'chromatin', 
            'transcription', 'expression', 'pathway', 'receptor'
        ]
        
        molecular_count = sum(1 for term in molecular_terms if term in full_text.lower())
        assert molecular_count >= 2, "Expected molecular mechanisms in hypothesis"
        
        # Check for measurable predictions
        metrics_text = ' '.join(protocol.success_metrics).lower()
        measurement_terms = ['measure', 'quantify', 'assess', 'level', 'concentration', 'activity']
        has_measurements = any(term in metrics_text for term in measurement_terms)
        assert has_measurements, "Expected measurable outcomes"
        
        # Verify ethical considerations (per constraint)
        safety_text = ' '.join(protocol.safety_considerations).lower()
        assert any(term in safety_text for term in ['ethic', 'consent', 'privacy', 'welfare'])
        
        # Check confidence is reasonable (not overconfident)
        assert 0.6 <= hypothesis.confidence_score <= 0.9

    async def test_generation_adaptation_to_constraints(self, real_llm_provider):
        """Test that the agent adapts generation to specific constraints.
        
        Verifies that different constraints lead to appropriately different hypotheses.
        """
        task_queue = TaskQueue()
        context_memory = ContextMemory()
        
        generation_agent = GenerationAgent(
            task_queue=task_queue,
            context_memory=context_memory,
            llm_provider=real_llm_provider,
            config={'enable_safety_logging': False}
        )
        
        # Test 1: Resource-constrained hypothesis
        constrained_goal = ResearchGoal(
            description="Develop low-cost diagnostic methods for infectious diseases",
            constraints=[
                "Must use only readily available materials",
                "Total cost under $1 per test",
                "No specialized equipment required"
            ]
        )
        
        constrained_hypothesis = await generation_agent.generate_hypothesis(
            research_goal=constrained_goal,
            generation_method='assumptions'
        )
        
        # Verify resource consciousness
        protocol_text = (constrained_hypothesis.experimental_protocol.methodology + 
                        ' '.join(constrained_hypothesis.experimental_protocol.required_resources))
        cost_aware_terms = ['low-cost', 'inexpensive', 'affordable', 'readily available', 'simple']
        assert any(term in protocol_text.lower() for term in cost_aware_terms)
        
        # Test 2: High-tech hypothesis
        hightech_goal = ResearchGoal(
            description="Develop advanced diagnostic methods using cutting-edge technology",
            constraints=[
                "Utilize state-of-the-art equipment",
                "Maximize sensitivity and specificity",
                "Cost is not a primary concern"
            ]
        )
        
        hightech_hypothesis = await generation_agent.generate_hypothesis(
            research_goal=hightech_goal,
            generation_method='assumptions'
        )
        
        # Verify high-tech approach
        hightech_text = (hightech_hypothesis.full_description + 
                        hightech_hypothesis.experimental_protocol.methodology)
        tech_terms = ['advanced', 'sophisticated', 'precision', 'high-resolution', 
                     'automated', 'AI', 'machine learning', 'quantum']
        tech_count = sum(1 for term in tech_terms if term in hightech_text.lower())
        assert tech_count >= 2, "Expected advanced technology references"
        
        # Verify the two hypotheses are substantially different
        # They should have different approaches despite similar goals
        assert constrained_hypothesis.summary != hightech_hypothesis.summary
        assert len(set(constrained_hypothesis.assumptions) & 
                  set(hightech_hypothesis.assumptions)) < 2  # Minimal overlap