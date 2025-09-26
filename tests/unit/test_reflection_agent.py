"""Unit tests for ReflectionAgent."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from uuid import UUID, uuid4

from src.agents.reflection import ReflectionAgent
from src.core.models import (
    Hypothesis,
    HypothesisCategory,
    ExperimentalProtocol,
    Review,
    ReviewType,
    ReviewDecision,
    ReviewScores,
    AssumptionDecomposition,
    SimulationResults,
    FailurePoint,
    Citation
)
from src.core.task_queue import TaskQueue
from src.core.context_memory import ContextMemory
from src.llm.base import LLMProvider


@pytest.fixture
def mock_task_queue():
    """Create a mock task queue."""
    return Mock(spec=TaskQueue)


@pytest.fixture
def mock_context_memory():
    """Create a mock context memory."""
    memory = Mock(spec=ContextMemory)
    memory.store = AsyncMock()
    memory.retrieve = AsyncMock()
    return memory


@pytest.fixture
def mock_llm_provider():
    """Create a mock LLM provider."""
    provider = Mock(spec=LLMProvider)
    provider.generate = AsyncMock()
    return provider


@pytest.fixture
def sample_hypothesis():
    """Create a sample hypothesis for testing."""
    return Hypothesis(
        id=uuid4(),
        summary="Test hypothesis about protein interactions",
        full_description="Detailed description of the hypothesis",
        category=HypothesisCategory.MECHANISTIC,
        novelty_claim="This is a novel approach",
        assumptions=["Assumption 1", "Assumption 2"],
        reasoning="Scientific reasoning",
        experimental_protocol=ExperimentalProtocol(
            objective="Test the hypothesis",
            methodology="Use these methods",
            expected_outcomes=["Outcome 1", "Outcome 2"],
            required_resources=["Resource 1", "Resource 2"],
            timeline="6 months",
            success_metrics=["Metric 1", "Metric 2"],
            potential_challenges=["Challenge 1", "Challenge 2"],
            safety_considerations=["Safety point 1", "Safety point 2"]
        ),
        supporting_evidence=[
            Citation(
                authors=["Author A", "Author B"],
                title="Evidence Paper 1",
                journal="Journal 1",
                year=2023
            ),
            Citation(
                authors=["Author C"],
                title="Evidence Paper 2",
                journal="Journal 2",
                year=2024
            )
        ],
        confidence_score=0.8,
        generation_method="literature_based"
    )


@pytest.fixture
def sample_review(sample_hypothesis):
    """Create a sample review for testing."""
    return Review(
        hypothesis_id=sample_hypothesis.id,
        reviewer_agent_id="test_agent",
        review_type=ReviewType.INITIAL,
        decision=ReviewDecision.ACCEPT,
        scores=ReviewScores(
            correctness=0.8,
            quality=0.7,
            novelty=0.9,
            safety=0.95,
            feasibility=0.7
        ),
        narrative_feedback="This is a well-constructed hypothesis",
        key_strengths=["Strong theoretical foundation", "Clear methodology"],
        key_weaknesses=["Limited preliminary data"],
        improvement_suggestions=["Gather more supporting evidence"],
        confidence_level="high"
    )


class TestReflectionAgentInitialization:
    """Test ReflectionAgent initialization."""

    def test_basic_initialization(self, mock_task_queue, mock_context_memory, mock_llm_provider):
        """Test basic agent initialization with required dependencies."""
        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider
        )

        assert agent.task_queue is mock_task_queue
        assert agent.context_memory is mock_context_memory
        assert agent.llm_provider is mock_llm_provider
        assert agent.agent_id.startswith("reflection_agent_")
        assert agent._review_count == 0
        assert agent.confidence_threshold == 0.6
        assert agent.strict_mode is False

    def test_initialization_with_config(
        self, mock_task_queue, mock_context_memory, mock_llm_provider
    ):
        """Test agent initialization with custom configuration."""
        config = {
            'confidence_threshold': 0.8,
            'strict_mode': True,
            'max_retries': 5,
            'enable_caching': False,
            'enable_safety_logging': False
        }

        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider,
            config=config
        )

        assert agent.confidence_threshold == 0.8
        assert agent.strict_mode is True
        assert agent.max_retries == 5
        assert agent.enable_caching is False
        assert agent.safety_logger is None

    def test_review_type_configs(self, mock_task_queue, mock_context_memory, mock_llm_provider):
        """Test that review type configurations are properly set."""
        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider
        )

        assert ReviewType.INITIAL in ReflectionAgent.REVIEW_TYPE_CONFIGS
        assert ReviewType.FULL in ReflectionAgent.REVIEW_TYPE_CONFIGS
        assert ReviewType.DEEP_VERIFICATION in ReflectionAgent.REVIEW_TYPE_CONFIGS
        assert ReviewType.OBSERVATION in ReflectionAgent.REVIEW_TYPE_CONFIGS
        assert ReviewType.SIMULATION in ReflectionAgent.REVIEW_TYPE_CONFIGS
        assert ReviewType.TOURNAMENT in ReflectionAgent.REVIEW_TYPE_CONFIGS

        # Check initial review config
        initial_config = ReflectionAgent.REVIEW_TYPE_CONFIGS[ReviewType.INITIAL]
        assert initial_config['use_tools'] is False
        assert initial_config['timeout'] == 60

        # Check full review config
        full_config = ReflectionAgent.REVIEW_TYPE_CONFIGS[ReviewType.FULL]
        assert full_config['use_tools'] is True
        assert full_config['timeout'] == 300

    @patch('src.agents.reflection.BAMLWrapper')
    def test_baml_wrapper_initialization(
        self, mock_baml_wrapper_class, mock_task_queue,
        mock_context_memory, mock_llm_provider
    ):
        """Test that BAML wrapper is properly initialized."""
        mock_baml_instance = Mock()
        mock_baml_wrapper_class.return_value = mock_baml_instance

        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider
        )

        mock_baml_wrapper_class.assert_called_once_with(provider=mock_llm_provider)
        assert agent.baml_wrapper == mock_baml_instance

    @patch('src.agents.reflection.SafetyLogger')
    def test_safety_logger_initialization(
        self, mock_safety_logger_class, mock_task_queue,
        mock_context_memory, mock_llm_provider
    ):
        """Test safety logger initialization."""
        mock_safety_instance = Mock()
        mock_safety_logger_class.return_value = mock_safety_instance

        # Test with safety enabled
        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider,
            config={'enable_safety_logging': True}
        )

        assert agent.safety_logger is not None

        # Test with safety disabled
        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider,
            config={'enable_safety_logging': False}
        )

        assert agent.safety_logger is None


class TestReflectionAgentReviewMethods:
    """Test ReflectionAgent review methods."""

    @pytest.mark.asyncio
    async def test_review_hypothesis_initial(
        self, mock_task_queue, mock_context_memory, mock_llm_provider,
        sample_hypothesis, sample_review
    ):
        """Test initial review of a hypothesis."""
        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider,
            config={'enable_safety_logging': False}
        )

        # Mock BAML wrapper
        with patch.object(agent.baml_wrapper, 'evaluate_hypothesis', new_callable=AsyncMock) as mock_evaluate:
            mock_evaluate.return_value = sample_review

            review = await agent.review_hypothesis(
                hypothesis=sample_hypothesis,
                review_type=ReviewType.INITIAL
            )

            assert review.hypothesis_id == sample_hypothesis.id
            assert review.review_type == ReviewType.INITIAL
            assert review.reviewer_agent_id == agent.agent_id
            mock_evaluate.assert_called_once()
            mock_context_memory.store.assert_called_once()

    @pytest.mark.asyncio
    async def test_review_hypothesis_with_context(
        self, mock_task_queue, mock_context_memory, mock_llm_provider,
        sample_hypothesis, sample_review
    ):
        """Test review with additional context."""
        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider,
            config={'enable_safety_logging': False}
        )

        # Mock BAML wrapper
        with patch.object(agent.baml_wrapper, 'evaluate_hypothesis', new_callable=AsyncMock) as mock_evaluate:
            mock_evaluate.return_value = sample_review

            context = {
                'research_goal': 'Test research goal',
                'priority': 'high'
            }

            review = await agent.review_hypothesis(
                hypothesis=sample_hypothesis,
                review_type=ReviewType.INITIAL,
                context=context
            )

            assert review is not None
            # Verify context was passed through
            call_args = mock_evaluate.call_args
            assert 'context' in call_args.kwargs

    @pytest.mark.asyncio
    async def test_review_hypothesis_error_handling(
        self, mock_task_queue, mock_context_memory, mock_llm_provider,
        sample_hypothesis
    ):
        """Test error handling during review."""
        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider,
            config={'enable_safety_logging': False}
        )

        # Mock BAML wrapper to raise an exception
        with patch.object(agent.baml_wrapper, 'evaluate_hypothesis', new_callable=AsyncMock) as mock_evaluate:
            mock_evaluate.side_effect = Exception("Test error")

            review = await agent.review_hypothesis(
                hypothesis=sample_hypothesis,
                review_type=ReviewType.INITIAL
            )

            assert review.decision == ReviewDecision.REJECT
            assert "Review failed" in review.narrative_feedback
            assert review.scores.average_score() == 0.0

    def test_prepare_evaluation_context(
        self, mock_task_queue, mock_context_memory, mock_llm_provider,
        sample_hypothesis
    ):
        """Test preparation of evaluation context."""
        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider
        )

        context = agent._prepare_evaluation_context(
            hypothesis=sample_hypothesis,
            review_type=ReviewType.FULL,
            external_context={'custom_key': 'custom_value'}
        )

        assert context['review_type'] == ReviewType.FULL.value
        assert context['hypothesis_id'] == str(sample_hypothesis.id)
        assert context['category'] == sample_hypothesis.category.value
        assert context['use_tools'] is True
        assert context['timeout'] == 300
        assert context['custom_key'] == 'custom_value'

    def test_extract_search_terms(
        self, mock_task_queue, mock_context_memory, mock_llm_provider,
        sample_hypothesis
    ):
        """Test extraction of search terms from hypothesis."""
        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider
        )

        terms = agent._extract_search_terms(sample_hypothesis)

        assert isinstance(terms, list)
        assert len(terms) <= 5
        assert sample_hypothesis.category.value in terms

    def test_update_average_scores(
        self, mock_task_queue, mock_context_memory, mock_llm_provider,
        sample_review
    ):
        """Test updating of average scores."""
        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider
        )

        # Initially no average scores
        assert len(agent._average_scores) == 0

        # Update with a review
        agent._update_average_scores(sample_review)

        assert ReviewType.INITIAL in agent._average_scores
        assert len(agent._average_scores[ReviewType.INITIAL]) == 1
        assert agent._average_scores[ReviewType.INITIAL][0] == sample_review.scores.average_score()

    def test_get_statistics(
        self, mock_task_queue, mock_context_memory, mock_llm_provider
    ):
        """Test getting agent statistics."""
        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider
        )

        # Update some internal state
        agent._review_count = 10
        agent._review_type_counts[ReviewType.INITIAL] = 5
        agent._review_type_counts[ReviewType.FULL] = 3
        agent._review_type_counts[ReviewType.DEEP_VERIFICATION] = 2

        stats = agent.get_statistics()

        assert stats['agent_id'] == agent.agent_id
        assert stats['total_reviews'] == 10
        assert stats['reviews_by_type'][ReviewType.INITIAL] == 5
        assert stats['reviews_by_type'][ReviewType.FULL] == 3
        assert stats['reviews_by_type'][ReviewType.DEEP_VERIFICATION] == 2

    @pytest.mark.asyncio
    async def test_shutdown(
        self, mock_task_queue, mock_context_memory, mock_llm_provider
    ):
        """Test agent shutdown."""
        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider
        )

        await agent.shutdown()

        # Verify statistics were stored
        mock_context_memory.store.assert_called_once()
        call_args = mock_context_memory.store.call_args
        assert call_args[1]['key'].startswith('agent_stats_')
        assert call_args[1]['metadata']['type'] == 'agent_statistics'
        assert call_args[1]['metadata']['final'] is True


class TestReflectionAgentReviewTypes:
    """Test different review types."""

    @pytest.mark.asyncio
    async def test_perform_full_review(
        self, mock_task_queue, mock_context_memory, mock_llm_provider,
        sample_hypothesis, sample_review
    ):
        """Test full review with literature search."""
        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider,
            config={'enable_safety_logging': False}
        )

        # Mock BAML wrapper
        with patch.object(agent.baml_wrapper, 'evaluate_hypothesis', new_callable=AsyncMock) as mock_evaluate:
            mock_evaluate.return_value = sample_review

            review = await agent.review_hypothesis(
                hypothesis=sample_hypothesis,
                review_type=ReviewType.FULL
            )

            assert review.review_type == ReviewType.FULL
            mock_evaluate.assert_called_once()

    @pytest.mark.asyncio
    async def test_perform_deep_verification(
        self, mock_task_queue, mock_context_memory, mock_llm_provider,
        sample_hypothesis, sample_review
    ):
        """Test deep verification review."""
        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider,
            config={'enable_safety_logging': False}
        )

        # Add assumption decomposition to the review
        sample_review.review_type = ReviewType.DEEP_VERIFICATION
        sample_review.assumption_decomposition = [
            AssumptionDecomposition(
                assumption="Test assumption",
                validity="valid",
                evidence="Strong evidence",
                criticality="fundamental"
            )
        ]

        # Mock BAML wrapper
        with patch.object(agent.baml_wrapper, 'evaluate_hypothesis', new_callable=AsyncMock) as mock_evaluate:
            mock_evaluate.return_value = sample_review

            review = await agent.review_hypothesis(
                hypothesis=sample_hypothesis,
                review_type=ReviewType.DEEP_VERIFICATION
            )

            assert review.review_type == ReviewType.DEEP_VERIFICATION

    @pytest.mark.asyncio
    async def test_perform_simulation_review(
        self, mock_task_queue, mock_context_memory, mock_llm_provider,
        sample_hypothesis, sample_review
    ):
        """Test simulation review."""
        agent = ReflectionAgent(
            task_queue=mock_task_queue,
            context_memory=mock_context_memory,
            llm_provider=mock_llm_provider,
            config={'enable_safety_logging': False}
        )

        # Add simulation results to the review
        sample_review.review_type = ReviewType.SIMULATION
        sample_review.simulation_results = SimulationResults(
            mechanism_steps=["Step 1", "Step 2", "Step 3"],
            failure_points=[
                FailurePoint(
                    step="Step 2",
                    probability=0.3,
                    impact="Moderate impact"
                )
            ],
            predicted_outcomes=["Outcome 1", "Outcome 2"]
        )

        # Mock BAML wrapper
        with patch.object(agent.baml_wrapper, 'evaluate_hypothesis', new_callable=AsyncMock) as mock_evaluate:
            mock_evaluate.return_value = sample_review

            review = await agent.review_hypothesis(
                hypothesis=sample_hypothesis,
                review_type=ReviewType.SIMULATION
            )

            assert review.review_type == ReviewType.SIMULATION