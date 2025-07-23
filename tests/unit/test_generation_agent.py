"""Unit tests for Generation Agent."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4
from datetime import datetime

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
def mock_dependencies():
    """Create mock dependencies for GenerationAgent."""
    task_queue = AsyncMock(spec=TaskQueue)
    context_memory = AsyncMock(spec=ContextMemory)
    llm_provider = AsyncMock(spec=LLMProvider)
    
    # Set up default return values
    context_memory.get.return_value = None
    context_memory.set.return_value = None
    
    return task_queue, context_memory, llm_provider


@pytest.fixture
def generation_agent(mock_dependencies):
    """Create a GenerationAgent instance."""
    task_queue, context_memory, llm_provider = mock_dependencies
    return GenerationAgent(
        task_queue=task_queue,
        context_memory=context_memory,
        llm_provider=llm_provider
    )


class TestGenerationAgentInit:
    """Test GenerationAgent initialization."""
    
    def test_init_with_defaults(self, mock_dependencies):
        """Test initialization with default configuration."""
        task_queue, context_memory, llm_provider = mock_dependencies
        
        agent = GenerationAgent(
            task_queue=task_queue,
            context_memory=context_memory,
            llm_provider=llm_provider
        )
        
        # Verify dependencies
        assert agent.task_queue is task_queue
        assert agent.context_memory is context_memory
        assert agent.llm_provider is llm_provider
        
        # Verify default configuration
        assert agent.max_retries == 3
        assert agent.confidence_threshold == 0.7
        assert agent.generation_timeout == 300
        assert agent.enable_caching is False
        
        # Verify strategies
        assert agent.generation_strategies == [
            'literature_based',
            'debate',
            'assumptions',
            'expansion'
        ]
        
        # Verify state initialization
        assert agent._generation_count == 0
        assert all(rate == 0.5 for rate in agent._strategy_success_rates.values())
    
    def test_init_with_custom_config(self, mock_dependencies):
        """Test initialization with custom configuration."""
        task_queue, context_memory, llm_provider = mock_dependencies
        
        config = {
            'max_retries': 5,
            'confidence_threshold': 0.8,
            'generation_timeout': 600,
            'enable_caching': True,
            'generation_strategies': ['literature_based', 'debate']
        }
        
        agent = GenerationAgent(
            task_queue=task_queue,
            context_memory=context_memory,
            llm_provider=llm_provider,
            config=config
        )
        
        # Verify custom configuration
        assert agent.max_retries == 5
        assert agent.confidence_threshold == 0.8
        assert agent.generation_timeout == 600
        assert agent.enable_caching is True
        assert agent.generation_strategies == ['literature_based', 'debate']
        
        # Verify success rates initialized for custom strategies
        assert len(agent._strategy_success_rates) == 2
        assert 'literature_based' in agent._strategy_success_rates
        assert 'debate' in agent._strategy_success_rates


class TestGenerateHypothesis:
    """Test main hypothesis generation method."""
    
    async def test_invalid_generation_method(self, generation_agent):
        """Test that invalid generation method raises ValueError."""
        research_goal = ResearchGoal(description="Test research goal for unit testing")
        
        with pytest.raises(ValueError, match="Invalid generation method"):
            await generation_agent.generate_hypothesis(
                research_goal=research_goal,
                generation_method='invalid_method'
            )
    
    async def test_literature_based_routing(self, generation_agent):
        """Test routing to literature-based generation."""
        research_goal = ResearchGoal(description="Test research goal for unit testing")
        
        # Mock the internal methods
        generation_agent._search_literature = AsyncMock(return_value=[])
        generation_agent.generate_from_literature = AsyncMock(
            return_value=Mock(spec=Hypothesis)
        )
        
        result = await generation_agent.generate_hypothesis(
            research_goal=research_goal,
            generation_method='literature_based'
        )
        
        # Verify routing
        generation_agent._search_literature.assert_called_once_with(research_goal)
        generation_agent.generate_from_literature.assert_called_once()
        assert result is not None
    
    async def test_debate_routing(self, generation_agent):
        """Test routing to debate-based generation."""
        research_goal = ResearchGoal(description="Test research goal for unit testing")
        
        # Mock the internal methods
        generation_agent._simulate_debate = AsyncMock(return_value=[])
        generation_agent.generate_from_debate = AsyncMock(
            return_value=Mock(spec=Hypothesis)
        )
        
        result = await generation_agent.generate_hypothesis(
            research_goal=research_goal,
            generation_method='debate'
        )
        
        # Verify routing
        generation_agent._simulate_debate.assert_called_once_with(research_goal, num_turns=3)
        generation_agent.generate_from_debate.assert_called_once()
        assert result is not None
    
    async def test_assumptions_routing(self, generation_agent):
        """Test routing to assumption-based generation."""
        research_goal = ResearchGoal(description="Test research goal for unit testing")
        
        # Mock the internal methods
        generation_agent.identify_assumptions = AsyncMock(return_value=[])
        generation_agent.generate_from_assumptions = AsyncMock(
            return_value=Mock(spec=Hypothesis)
        )
        
        result = await generation_agent.generate_hypothesis(
            research_goal=research_goal,
            generation_method='assumptions'
        )
        
        # Verify routing
        generation_agent.identify_assumptions.assert_called_once_with(research_goal)
        generation_agent.generate_from_assumptions.assert_called_once()
        assert result is not None
    
    async def test_expansion_routing(self, generation_agent):
        """Test routing to expansion-based generation."""
        research_goal = ResearchGoal(description="Test research goal for unit testing")
        
        # Mock the internal methods
        generation_agent._get_expansion_feedback = AsyncMock(return_value={})
        generation_agent.generate_from_feedback = AsyncMock(
            return_value=Mock(spec=Hypothesis)
        )
        
        result = await generation_agent.generate_hypothesis(
            research_goal=research_goal,
            generation_method='expansion'
        )
        
        # Verify routing
        generation_agent._get_expansion_feedback.assert_called_once()
        generation_agent.generate_from_feedback.assert_called_once()
        assert result is not None


class TestGenerateFromLiterature:
    """Test literature-based generation."""
    
    async def test_successful_generation(self, generation_agent):
        """Test successful hypothesis generation from literature."""
        research_goal = ResearchGoal(
            description="Test research goal",
            constraints=["Constraint 1", "Constraint 2"]
        )
        
        literature = [
            {
                'title': 'Paper 1',
                'abstract': 'Abstract 1',
                'doi': '10.1234/test1'
            }
        ]
        
        # Mock BAML wrapper
        from src.llm.baml_wrapper import BAMLWrapper
        mock_baml_wrapper = AsyncMock(spec=BAMLWrapper)
        mock_baml_hypothesis = Mock()
        mock_baml_hypothesis.summary = "Test hypothesis"
        mock_baml_hypothesis.category = "mechanistic"
        mock_baml_hypothesis.full_description = "Detailed description"
        mock_baml_hypothesis.novelty_claim = "Novel because..."
        mock_baml_hypothesis.assumptions = ["Assumption 1"]
        mock_baml_hypothesis.confidence_score = 0.85
        mock_baml_hypothesis.generation_method = "literature_based"
        mock_baml_hypothesis.created_at = "2024-01-01T00:00:00Z"
        
        # Set up experimental protocol mock
        mock_protocol = Mock()
        mock_protocol.objective = "Test objective"
        mock_protocol.methodology = "Test methodology"
        mock_protocol.required_resources = ["Resource 1"]
        mock_protocol.timeline = "6 months"
        mock_protocol.success_metrics = ["Metric 1"]
        mock_protocol.potential_challenges = ["Challenge 1"]
        mock_protocol.safety_considerations = ["Safety 1"]
        mock_baml_hypothesis.experimental_protocol = mock_protocol
        
        mock_baml_wrapper.generate_hypothesis = AsyncMock(return_value=mock_baml_hypothesis)
        generation_agent.baml_wrapper = mock_baml_wrapper
        
        # Execute
        result = await generation_agent.generate_from_literature(research_goal, literature)
        
        # Verify
        assert isinstance(result, Hypothesis)
        assert result.summary == "Test hypothesis"
        assert result.generation_method == "literature_based"
        assert result.confidence_score == 0.85
        assert len(result.supporting_evidence) == 1
        assert result.supporting_evidence[0].doi == '10.1234/test1'
        
        # Verify storage
        generation_agent.context_memory.set.assert_called()
    
    async def test_generation_failure(self, generation_agent):
        """Test handling of generation failure."""
        research_goal = ResearchGoal(description="Test research goal for unit testing")
        literature = []
        
        # Mock BAML wrapper to raise exception
        from src.llm.baml_wrapper import BAMLWrapper
        mock_baml_wrapper = AsyncMock(spec=BAMLWrapper)
        mock_baml_wrapper.generate_hypothesis = AsyncMock(side_effect=Exception("BAML error"))
        generation_agent.baml_wrapper = mock_baml_wrapper
        
        # Execute and verify exception
        with pytest.raises(RuntimeError, match="Generation failed"):
            await generation_agent.generate_from_literature(research_goal, literature)


class TestGenerateFromDebate:
    """Test debate-based generation."""
    
    async def test_debate_generation(self, generation_agent):
        """Test hypothesis generation from debate."""
        research_goal = ResearchGoal(description="Test research question")
        debate_turns = [
            {'perspective': 'biologist', 'argument': 'Biological perspective...'},
            {'perspective': 'chemist', 'argument': 'Chemical perspective...'},
            {'perspective': 'physicist', 'argument': 'Physical perspective...'}
        ]
        
        result = await generation_agent.generate_from_debate(
            research_goal, debate_turns, num_perspectives=3
        )
        
        # Verify result
        assert isinstance(result, Hypothesis)
        assert result.generation_method == 'debate'
        assert len(result.assumptions) == 3  # One per debate turn
        assert 'debate' in result.summary.lower()
        assert result.confidence_score == 0.75
        
        # Verify storage
        generation_agent.context_memory.set.assert_called()


class TestIdentifyAssumptions:
    """Test assumption identification."""
    
    async def test_identify_assumptions(self, generation_agent):
        """Test identifying testable assumptions."""
        research_goal = ResearchGoal(description="Why does ice float?")
        
        assumptions = await generation_agent.identify_assumptions(research_goal)
        
        # Verify assumptions
        assert isinstance(assumptions, list)
        assert len(assumptions) == 3
        assert all('testable' in assumption.lower() for assumption in assumptions)


class TestGenerateFromAssumptions:
    """Test assumption-based generation."""
    
    async def test_assumption_generation(self, generation_agent):
        """Test hypothesis generation from assumptions."""
        research_goal = ResearchGoal(description="Test research goal for unit testing")
        assumptions = [
            "Testable assumption 1",
            "Testable assumption 2",
            "Testable assumption 3"
        ]
        
        result = await generation_agent.generate_from_assumptions(
            research_goal, assumptions
        )
        
        # Verify result
        assert isinstance(result, Hypothesis)
        assert result.generation_method == 'assumptions'
        assert result.assumptions == assumptions
        assert 'density' in result.full_description.lower()
        assert result.confidence_score == 0.8
        
        # Verify storage
        generation_agent.context_memory.set.assert_called()


class TestGenerateFromFeedback:
    """Test feedback-based generation."""
    
    async def test_feedback_generation(self, generation_agent):
        """Test hypothesis generation from feedback."""
        research_goal = ResearchGoal(description="Protein research")
        feedback = {
            'patterns': ['Too focused on single proteins'],
            'suggestions': ['Consider protein networks']
        }
        
        result = await generation_agent.generate_from_feedback(
            research_goal, feedback
        )
        
        # Verify result
        assert isinstance(result, Hypothesis)
        assert result.generation_method == 'expansion'
        assert 'network' in result.full_description.lower()
        assert 'network' in result.novelty_claim.lower() or 'system' in result.full_description.lower()
        assert result.confidence_score == 0.85
        
        # Verify storage
        generation_agent.context_memory.set.assert_called()


class TestCreativityMetrics:
    """Test creativity metrics calculation."""
    
    async def test_calculate_creativity_metrics(self, generation_agent):
        """Test calculating creativity metrics for hypotheses."""
        hypotheses = [
            Mock(spec=Hypothesis, generation_method='debate'),
            Mock(spec=Hypothesis, generation_method='literature_based'),
            Mock(spec=Hypothesis, generation_method='assumptions')
        ]
        
        metrics = await generation_agent.calculate_creativity_metrics(hypotheses)
        
        # Verify metrics
        assert isinstance(metrics, dict)
        assert 'novelty_score' in metrics
        assert 'diversity_score' in metrics
        assert 'paradigm_shift_potential' in metrics
        assert 0 <= metrics['novelty_score'] <= 1
        assert 0 <= metrics['diversity_score'] <= 1
        assert 0 <= metrics['paradigm_shift_potential'] <= 1


class TestWebSearchIntegration:
    """Test web search integration."""
    
    async def test_web_search_injection(self, generation_agent):
        """Test that web search can be injected into the agent."""
        mock_web_search = AsyncMock()
        generation_agent.web_search = mock_web_search
        
        assert generation_agent.web_search is mock_web_search
    
    async def test_search_literature_with_web_search(self, generation_agent):
        """Test that _search_literature uses injected web search."""
        # Create mock web search
        mock_web_search = AsyncMock()
        mock_web_search.search.return_value = {
            'articles': [
                {
                    'title': 'Web Search Result',
                    'abstract': 'Found via web search',
                    'doi': '10.1234/websearch.2024.001',
                    'relevance': 0.95
                }
            ]
        }
        
        # Inject web search
        generation_agent.web_search = mock_web_search
        
        # Call search literature
        research_goal = ResearchGoal(description="Test research goal for web search")
        results = await generation_agent._search_literature(research_goal)
        
        # Verify web search was called
        mock_web_search.search.assert_called_once()
        assert len(results) == 1
        assert results[0]['title'] == 'Web Search Result'
    
    async def test_generate_from_literature_with_real_search(self, generation_agent, mock_dependencies):
        """Test hypothesis generation with real web search results."""
        _, _, llm_provider = mock_dependencies
        
        # Set up mock web search
        mock_web_search = AsyncMock()
        mock_web_search.search.return_value = {
            'articles': [
                {
                    'title': 'CRISPR advances in cancer therapy',
                    'abstract': 'Novel CRISPR applications for targeted cancer treatment...',
                    'doi': '10.1038/nature.2024.001',
                    'journal': 'Nature',
                    'relevance': 0.98
                }
            ]
        }
        generation_agent.web_search = mock_web_search
        
        # Set up BAML wrapper mock
        mock_baml_hypothesis = Mock()
        mock_baml_hypothesis.summary = "CRISPR-based cancer therapy hypothesis"
        mock_baml_hypothesis.category = "therapeutic"
        mock_baml_hypothesis.full_description = "Detailed hypothesis about CRISPR"
        mock_baml_hypothesis.novelty_claim = "Novel CRISPR approach"
        mock_baml_hypothesis.assumptions = ["Assumption 1"]
        mock_baml_hypothesis.confidence_score = 0.85
        mock_baml_hypothesis.generation_method = "literature_based"
        mock_baml_hypothesis.experimental_protocol = None
        
        generation_agent.baml_wrapper.generate_hypothesis = AsyncMock(
            return_value=mock_baml_hypothesis
        )
        
        # Generate hypothesis
        research_goal = ResearchGoal(description="Develop CRISPR cancer therapies")
        hypothesis = await generation_agent.generate_hypothesis(
            research_goal=research_goal,
            generation_method='literature_based'
        )
        
        # Verify web search was used
        mock_web_search.search.assert_called_once()
        
        # Verify hypothesis has citations from web search
        assert len(hypothesis.supporting_evidence) == 1
        assert hypothesis.supporting_evidence[0].doi == '10.1038/nature.2024.001'


class TestSafetyIntegration:
    """Test safety integration in generation."""
    
    async def test_safety_logging_enabled(self, generation_agent, mock_dependencies):
        """Test that safety logging is enabled by default."""
        assert hasattr(generation_agent, 'safety_logger')
        assert generation_agent.safety_logger is not None
    
    async def test_hypothesis_safety_logging(self, generation_agent, mock_dependencies):
        """Test that hypotheses are logged for safety monitoring."""
        task_queue, context_memory, llm_provider = mock_dependencies
        
        # Mock safety logger
        mock_safety_logger = AsyncMock()
        generation_agent.safety_logger = mock_safety_logger
        
        # Generate a hypothesis
        research_goal = ResearchGoal(
            description="Research goal for safety testing"
        )
        
        await generation_agent.generate_hypothesis(
            research_goal=research_goal,
            generation_method='assumptions'
        )
        
        # Verify safety logger was called
        mock_safety_logger.log_hypothesis.assert_called_once()
    
    async def test_safety_logger_can_be_disabled(self, mock_dependencies):
        """Test that safety logger can be disabled via config."""
        task_queue, context_memory, llm_provider = mock_dependencies
        
        config = {'enable_safety_logging': False}
        agent = GenerationAgent(
            task_queue=task_queue,
            context_memory=context_memory,
            llm_provider=llm_provider,
            config=config
        )
        
        assert agent.safety_logger is None


class TestHelperMethods:
    """Test helper methods."""
    
    def test_prepare_literature_context(self, generation_agent):
        """Test preparing context from literature."""
        literature = [
            {'title': 'Paper 1', 'abstract': 'Abstract 1'},
            {'title': 'Paper 2', 'abstract': 'Abstract 2'},
            {'title': 'Paper 3', 'abstract': 'Abstract 3'}
        ]
        
        context = generation_agent._prepare_literature_context(literature)
        
        assert 'focus_area' in context
        assert 'key_findings' in context
        assert 'Paper 1' in context['focus_area']
        assert 'Abstract 1' in context['key_findings']
    
    def test_prepare_empty_literature_context(self, generation_agent):
        """Test preparing context from empty literature."""
        context = generation_agent._prepare_literature_context([])
        assert context == {}
    
    def test_extract_citations(self, generation_agent):
        """Test extracting citations from literature."""
        literature = [
            {
                'title': 'Test Paper',
                'doi': '10.1234/test',
                'journal': 'Test Journal'
            },
            {
                'title': 'Another Paper',
                # No DOI
            }
        ]
        
        citations = generation_agent._extract_citations(literature)
        
        assert len(citations) == 1
        assert citations[0].title == 'Test Paper'
        assert citations[0].doi == '10.1234/test'
        assert citations[0].journal == 'Test Journal'
    
    def test_create_mock_protocol(self, generation_agent):
        """Test creating mock experimental protocol."""
        protocol = generation_agent._create_mock_protocol()
        
        assert isinstance(protocol, ExperimentalProtocol)
        assert protocol.objective == "Test the hypothesis"
        assert len(protocol.required_resources) == 2
        assert len(protocol.success_metrics) == 3
        assert len(protocol.safety_considerations) == 2