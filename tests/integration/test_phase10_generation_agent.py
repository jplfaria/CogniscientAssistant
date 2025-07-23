"""Phase 10 Integration Tests - Generation Agent.

This module tests the Generation Agent's ability to create novel hypotheses
through various generation strategies including literature exploration,
simulated debates, and iterative refinement.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from src.agents.generation import GenerationAgent
from src.core.models import (
    Hypothesis,
    HypothesisCategory,
    Citation,
    ExperimentalProtocol,
    ResearchGoal
)
from src.core.task_queue import TaskQueue
from src.core.context_memory import ContextMemory
from src.llm.base import LLMProvider


@pytest.fixture
async def mock_dependencies():
    """Create mock dependencies for GenerationAgent."""
    task_queue = AsyncMock(spec=TaskQueue)
    context_memory = AsyncMock(spec=ContextMemory)
    llm_provider = AsyncMock(spec=LLMProvider)
    
    # Set up default return values
    context_memory.get.return_value = {}
    
    return task_queue, context_memory, llm_provider


@pytest.fixture
async def generation_agent(mock_dependencies):
    """Create a GenerationAgent instance with mocked dependencies."""
    task_queue, context_memory, llm_provider = mock_dependencies
    return GenerationAgent(
        task_queue=task_queue,
        context_memory=context_memory,
        llm_provider=llm_provider
    )


class TestGenerationAgentInitialization:
    """Test GenerationAgent initialization and configuration."""
    
    async def test_generation_agent_initialization(self, mock_dependencies):
        """Test that GenerationAgent initializes correctly with dependencies."""
        task_queue, context_memory, llm_provider = mock_dependencies
        
        # Create agent
        agent = GenerationAgent(
            task_queue=task_queue,
            context_memory=context_memory,
            llm_provider=llm_provider
        )
        
        # Verify initialization
        assert agent.task_queue is task_queue
        assert agent.context_memory is context_memory
        assert agent.llm_provider is llm_provider
        assert agent.generation_strategies == [
            'literature_based',
            'debate',
            'assumptions',
            'expansion'
        ]
        assert agent.max_retries == 3
        assert agent.confidence_threshold == 0.7
    
    async def test_custom_configuration(self, mock_dependencies):
        """Test GenerationAgent with custom configuration."""
        task_queue, context_memory, llm_provider = mock_dependencies
        
        config = {
            'max_retries': 5,
            'confidence_threshold': 0.8,
            'generation_timeout': 600,
            'enable_caching': True
        }
        
        agent = GenerationAgent(
            task_queue=task_queue,
            context_memory=context_memory,
            llm_provider=llm_provider,
            config=config
        )
        
        assert agent.max_retries == 5
        assert agent.confidence_threshold == 0.8
        assert agent.generation_timeout == 600
        assert agent.enable_caching is True


class TestLiteratureBasedGeneration:
    """Test literature-based hypothesis generation."""
    
    @pytest.mark.integration
    async def test_literature_based_generation(self, generation_agent):
        """Test generating hypothesis from literature exploration."""
        # Set up research goal
        research_goal = ResearchGoal(
            description="Identify novel treatments for acute myeloid leukemia",
            constraints=["Must use FDA-approved compounds", "Focus on repurposing"]
        )
        
        # Mock web search results
        mock_literature = [
            {
                'title': 'ER stress in AML cells',
                'abstract': 'Study showing increased endoplasmic reticulum stress...',
                'relevance': 0.9
            },
            {
                'title': 'KIRA6 as an IRE1α inhibitor',
                'abstract': 'KIRA6 selectively inhibits IRE1α kinase activity...',
                'relevance': 0.85
            }
        ]
        
        # Generate hypothesis
        hypothesis = await generation_agent.generate_from_literature(
            research_goal=research_goal,
            literature=mock_literature
        )
        
        # Verify hypothesis structure
        assert isinstance(hypothesis, Hypothesis)
        assert hypothesis.category in [HypothesisCategory.THERAPEUTIC, HypothesisCategory.MECHANISTIC]
        assert hypothesis.generation_method == 'literature_based'
        assert len(hypothesis.supporting_evidence) > 0
        assert hypothesis.confidence_score >= 0.7
        assert 'KIRA6' in hypothesis.full_description or 'IRE1' in hypothesis.full_description


class TestSimulatedDebateGeneration:
    """Test hypothesis generation through simulated debates."""
    
    @pytest.mark.integration
    async def test_simulated_debate_generation(self, generation_agent):
        """Test generating hypothesis through multi-perspective debate."""
        research_goal = ResearchGoal(
            description="Explain bacterial communication mechanisms across species"
        )
        
        # Mock debate turns
        mock_debate_turns = [
            {
                'perspective': 'molecular_biologist',
                'argument': 'Quorum sensing molecules are species-specific...'
            },
            {
                'perspective': 'evolutionary_biologist',
                'argument': 'Cross-species communication provides survival advantage...'
            },
            {
                'perspective': 'systems_biologist',
                'argument': 'Network effects amplify weak cross-species signals...'
            }
        ]
        
        hypothesis = await generation_agent.generate_from_debate(
            research_goal=research_goal,
            debate_turns=mock_debate_turns,
            num_perspectives=3
        )
        
        # Verify synthesis from multiple perspectives
        assert isinstance(hypothesis, Hypothesis)
        assert hypothesis.generation_method == 'debate'
        assert len(hypothesis.assumptions) >= 3
        assert 'communication' in hypothesis.summary.lower()


class TestAssumptionBasedGeneration:
    """Test hypothesis generation through assumption decomposition."""
    
    @pytest.mark.integration
    async def test_assumption_based_generation(self, generation_agent):
        """Test generating hypothesis by identifying testable assumptions."""
        research_goal = ResearchGoal(
            description="Understand why ice floats on water"
        )
        
        # Generate intermediate assumptions
        assumptions = await generation_agent.identify_assumptions(research_goal)
        assert len(assumptions) >= 3
        assert all('testable' in a.lower() or 'hypothesis' in a.lower() for a in assumptions)
        
        # Generate hypothesis from assumptions
        hypothesis = await generation_agent.generate_from_assumptions(
            research_goal=research_goal,
            assumptions=assumptions
        )
        
        assert isinstance(hypothesis, Hypothesis)
        assert hypothesis.generation_method == 'assumptions'
        assert len(hypothesis.assumptions) == len(assumptions)
        assert 'density' in hypothesis.full_description.lower()


class TestFeedbackBasedGeneration:
    """Test hypothesis generation based on feedback."""
    
    @pytest.mark.integration
    async def test_feedback_based_generation(self, generation_agent, mock_dependencies):
        """Test generating new hypotheses based on meta-review feedback."""
        _, context_memory, _ = mock_dependencies
        
        # Mock existing hypotheses and feedback
        existing_hypotheses = [
            Hypothesis(
                id=uuid4(),
                summary="Hypothesis about protein folding",
                category=HypothesisCategory.MECHANISTIC,
                full_description="Detailed description...",
                novelty_claim="Novel insight into chaperone function",
                assumptions=["Assumption 1"],
                experimental_protocol=Mock(spec=ExperimentalProtocol),
                supporting_evidence=[],
                confidence_score=0.8,
                generation_method="literature_based"
            )
        ]
        
        meta_feedback = {
            'patterns': ['Too focused on single proteins', 'Lacking systems perspective'],
            'suggestions': ['Consider protein networks', 'Explore emergent properties']
        }
        
        context_memory.get.side_effect = lambda key: {
            'hypotheses': existing_hypotheses,
            'meta_review_feedback': meta_feedback
        }.get(key, [])
        
        # Generate based on feedback
        hypothesis = await generation_agent.generate_from_feedback(
            research_goal=ResearchGoal(description="Understand protein misfolding diseases"),
            feedback=meta_feedback
        )
        
        # Verify feedback incorporation
        assert isinstance(hypothesis, Hypothesis)
        assert hypothesis.generation_method == 'expansion'
        assert 'network' in hypothesis.full_description.lower() or 'system' in hypothesis.full_description.lower()
        assert hypothesis.id != existing_hypotheses[0].id


class TestGenerationSafetyChecks:
    """Test safety checks during hypothesis generation."""
    
    @pytest.mark.integration
    async def test_generation_safety_checks(self, generation_agent):
        """Test that generated hypotheses pass safety checks."""
        research_goal = ResearchGoal(
            description="Develop safe methods for treating cancer",
            constraints=["No harmful compounds", "Ethical considerations"]
        )
        
        # Generate hypothesis
        hypothesis = await generation_agent.generate_hypothesis(
            research_goal=research_goal,
            generation_method='literature_based'
        )
        
        # Verify safety considerations
        assert isinstance(hypothesis, Hypothesis)
        assert len(hypothesis.experimental_protocol.safety_considerations) > 0
        assert hypothesis.confidence_score > 0
        assert any('safe' in consideration.lower() 
                  for consideration in hypothesis.experimental_protocol.safety_considerations)
    
    @pytest.mark.integration
    async def test_constraint_compliance(self, generation_agent):
        """Test that generated hypotheses comply with specified constraints."""
        research_goal = ResearchGoal(
            description="Find treatments using only natural compounds",
            constraints=[
                "Must use plant-derived compounds only",
                "No synthetic modifications",
                "Must be orally bioavailable"
            ]
        )
        
        hypothesis = await generation_agent.generate_hypothesis(
            research_goal=research_goal,
            generation_method='assumptions'
        )
        
        # Verify constraint compliance
        assert 'natural' in hypothesis.full_description.lower() or 'plant' in hypothesis.full_description.lower()
        assert 'synthetic' not in hypothesis.full_description.lower()
        assert any('oral' in metric.lower() 
                  for metric in hypothesis.experimental_protocol.success_metrics)


class TestWebSearchIntegration:
    """Test integration with web search for literature-based generation."""
    
    @pytest.mark.integration
    async def test_web_search_integration(self, generation_agent, mock_dependencies):
        """Test that generation agent properly integrates with web search."""
        _, _, llm_provider = mock_dependencies
        
        # Mock web search tool behavior
        mock_search_results = {
            'articles': [
                {
                    'title': 'Recent advances in immunotherapy',
                    'abstract': 'Novel checkpoint inhibitors show promise...',
                    'doi': '10.1234/example.2024.001',
                    'relevance': 0.95
                }
            ]
        }
        
        # Set up mock to return search results
        generation_agent.web_search = AsyncMock(return_value=mock_search_results)
        
        research_goal = ResearchGoal(
            description="Improve immunotherapy response rates"
        )
        
        hypothesis = await generation_agent.generate_from_literature(
            research_goal=research_goal,
            literature=mock_search_results['articles']
        )
        
        # Verify web search integration
        assert isinstance(hypothesis, Hypothesis)
        assert len(hypothesis.supporting_evidence) > 0
        assert any('10.1234' in citation.doi for citation in hypothesis.supporting_evidence
                  if citation.doi)


class TestHypothesisDiversity:
    """Test generation of diverse hypotheses."""
    
    @pytest.mark.integration
    @pytest.mark.parametrize("generation_method", [
        "literature_based",
        "debate", 
        "assumptions",
        "expansion"
    ])
    async def test_hypothesis_diversity(self, generation_agent, generation_method):
        """Test that different generation methods produce diverse hypotheses."""
        research_goal = ResearchGoal(
            description="Understand cellular aging mechanisms"
        )
        
        # Generate hypothesis with specified method
        hypothesis = await generation_agent.generate_hypothesis(
            research_goal=research_goal,
            generation_method=generation_method
        )
        
        # Verify method-specific characteristics
        assert hypothesis.generation_method == generation_method
        assert isinstance(hypothesis, Hypothesis)
        
        if generation_method == 'literature_based':
            assert len(hypothesis.supporting_evidence) > 0
        elif generation_method == 'debate':
            assert len(hypothesis.assumptions) >= 3
        elif generation_method == 'assumptions':
            assert all('test' in assumption.lower() for assumption in hypothesis.assumptions)
        elif generation_method == 'expansion':
            assert 'build' in hypothesis.novelty_claim.lower() or 'extend' in hypothesis.novelty_claim.lower()


class TestGenerationCreativityMetrics:
    """Test creativity metrics for generated hypotheses."""
    
    @pytest.mark.integration
    @pytest.mark.xfail(reason="May fail until creativity metrics are implemented")
    async def test_generation_creativity_metrics(self, generation_agent):
        """Test that creativity metrics are tracked for generated hypotheses."""
        research_goal = ResearchGoal(
            description="Propose novel biomaterials for tissue engineering"
        )
        
        # Generate multiple hypotheses
        hypotheses = []
        for _ in range(5):
            hypothesis = await generation_agent.generate_hypothesis(
                research_goal=research_goal,
                generation_method='debate'
            )
            hypotheses.append(hypothesis)
        
        # Calculate creativity metrics
        metrics = await generation_agent.calculate_creativity_metrics(hypotheses)
        
        # Verify metrics
        assert 'novelty_score' in metrics
        assert 'diversity_score' in metrics
        assert 'paradigm_shift_potential' in metrics
        assert 0 <= metrics['novelty_score'] <= 1
        assert 0 <= metrics['diversity_score'] <= 1


# Additional test marker for real LLM tests (to be implemented separately)
@pytest.mark.real_llm
class TestGenerationRealLLM:
    """Tests with real LLM for Generation Agent (in separate file)."""
    pass