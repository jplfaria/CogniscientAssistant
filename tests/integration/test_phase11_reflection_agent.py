"""Integration tests for Phase 11: Reflection Agent.

Tests the Reflection Agent's ability to evaluate hypotheses through
multiple review types and integrate with the overall system.
"""

import asyncio
import pytest
from uuid import uuid4
from datetime import datetime

from src.agents.reflection import ReflectionAgent
from src.agents.generation import GenerationAgent
from src.agents.supervisor import SupervisorAgent
from src.core.models import (
    Hypothesis,
    HypothesisCategory,
    ExperimentalProtocol,
    Review,
    ReviewType,
    ReviewDecision,
    ReviewScores,
    Task,
    TaskType,
    TaskState,
    Citation
)
from pathlib import Path
from src.core.task_queue import TaskQueue, QueueConfig
from src.core.context_memory import ContextMemory
from src.llm.mock_provider import MockLLMProvider, MockConfiguration


@pytest.fixture
async def setup_agents():
    """Set up the agent ecosystem for testing."""
    # Create shared infrastructure
    queue_config = QueueConfig()
    queue_config.max_queue_size = 100
    task_queue = TaskQueue(queue_config)
    context_memory = ContextMemory(storage_path=Path(".test_memory"))

    mock_config = MockConfiguration()
    mock_config.default_response = "Mock response"
    mock_config.default_delay = 0.01
    llm_provider = MockLLMProvider(configuration=mock_config)

    # Create agents
    supervisor = SupervisorAgent(
        task_queue=task_queue,
        context_memory=context_memory,
        llm_provider=llm_provider
    )

    generation = GenerationAgent(
        task_queue=task_queue,
        context_memory=context_memory,
        llm_provider=llm_provider,
        config={'enable_safety_logging': False}
    )

    reflection = ReflectionAgent(
        task_queue=task_queue,
        context_memory=context_memory,
        llm_provider=llm_provider,
        config={'enable_safety_logging': False}
    )

    # Clean up context memory before tests
    await context_memory.clear()

    yield {
        'supervisor': supervisor,
        'generation': generation,
        'reflection': reflection,
        'task_queue': task_queue,
        'context_memory': context_memory,
        'llm_provider': llm_provider
    }

    # Cleanup
    await context_memory.clear()


@pytest.fixture
def sample_hypothesis():
    """Create a sample hypothesis for testing."""
    return Hypothesis(
        id=uuid4(),
        summary="Inhibition of protein X reduces inflammation in disease Y",
        full_description="Detailed molecular mechanism involving protein X...",
        category=HypothesisCategory.THERAPEUTIC,
        novelty_claim="First demonstration of protein X role in disease Y",
        assumptions=[
            "Protein X is expressed in affected tissues",
            "Small molecule inhibitors can reach target site",
            "Disease Y has inflammatory component"
        ],
        reasoning="Based on literature showing protein X upregulation...",
        experimental_protocol=ExperimentalProtocol(
            objective="Validate protein X as therapeutic target",
            methodology="In vitro cell culture followed by mouse models",
            expected_outcomes=[
                "Reduced inflammation markers",
                "Improved disease symptoms"
            ],
            required_resources=[
                "Cell culture facilities",
                "Animal facility",
                "Protein X inhibitors"
            ],
            timeline="12 months",
            success_metrics=[
                "50% reduction in inflammatory markers",
                "Improved symptom scores"
            ],
            potential_challenges=[
                "Target accessibility",
                "Off-target effects"
            ],
            safety_considerations=[
                "Monitor for toxicity",
                "Check for immune responses"
            ]
        ),
        supporting_evidence=[
            Citation(
                authors=["Smith J", "Jones K"],
                title="Protein X role in inflammation",
                journal="Nature Medicine",
                year=2022
            ),
            Citation(
                authors=["Brown L"],
                title="Similar proteins in related diseases",
                journal="Science",
                year=2023
            )
        ],
        confidence_score=0.75,
        generation_method="literature_based"
    )


class TestReflectionAgentInitialization:
    """Test Reflection Agent initialization."""

    @pytest.mark.asyncio
    async def test_reflection_agent_initialization(self, setup_agents):
        """Test that Reflection Agent initializes correctly."""
        agents = setup_agents
        reflection = agents['reflection']

        assert reflection is not None
        assert reflection.agent_id.startswith("reflection_agent_")
        assert reflection._review_count == 0
        assert len(reflection._review_type_counts) == len(ReviewType)

        # Verify review type configurations are loaded
        for review_type in ReviewType:
            assert review_type in ReflectionAgent.REVIEW_TYPE_CONFIGS

    @pytest.mark.asyncio
    async def test_reflection_agent_context_memory_integration(self, setup_agents):
        """Test that Reflection Agent properly integrates with Context Memory."""
        agents = setup_agents
        reflection = agents['reflection']
        memory = agents['context_memory']

        # Test that agent can store and retrieve aggregate data
        test_data = {"test": "data", "agent_id": reflection.agent_id}
        timestamp = datetime.now()

        # Store aggregate data
        success = await memory.store_aggregate(
            aggregate_type='test_reflection',
            data=test_data,
            timestamp=timestamp
        )

        assert success is True

        # Retrieve aggregate data
        retrieved = await memory.retrieve_aggregate(
            aggregate_type='test_reflection',
            query_type='latest'
        )

        assert retrieved is not None
        # The retrieve_aggregate returns the data directly for latest query
        assert 'test' in retrieved
        assert retrieved['test'] == 'data'
        assert retrieved['agent_id'] == reflection.agent_id


class TestReviewProcesses:
    """Test different review processes."""

    @pytest.mark.asyncio
    async def test_initial_review_process(self, setup_agents, sample_hypothesis):
        """Test initial review without external tools."""
        agents = setup_agents
        reflection = agents['reflection']

        # Perform initial review
        review = await reflection.review_hypothesis(
            hypothesis=sample_hypothesis,
            review_type=ReviewType.INITIAL
        )

        assert review is not None
        assert review.hypothesis_id == sample_hypothesis.id
        assert review.review_type == ReviewType.INITIAL
        assert review.decision in [ReviewDecision.ACCEPT, ReviewDecision.REJECT, ReviewDecision.REVISE]
        assert review.scores is not None
        assert 0 <= review.scores.correctness <= 1
        assert 0 <= review.scores.quality <= 1
        assert 0 <= review.scores.novelty <= 1
        assert 0 <= review.scores.safety <= 1
        assert 0 <= review.scores.feasibility <= 1
        assert len(review.key_strengths) > 0
        assert len(review.key_weaknesses) > 0
        assert len(review.improvement_suggestions) > 0
        assert review.confidence_level in ["high", "medium", "low"]

    @pytest.mark.asyncio
    async def test_full_review_with_literature(self, setup_agents, sample_hypothesis):
        """Test full review that would use literature search."""
        agents = setup_agents
        reflection = agents['reflection']

        # Perform full review
        review = await reflection.review_hypothesis(
            hypothesis=sample_hypothesis,
            review_type=ReviewType.FULL
        )

        assert review is not None
        assert review.review_type == ReviewType.FULL
        assert review.narrative_feedback is not None and len(review.narrative_feedback) > 0

        # Full review should be more comprehensive
        assert review.time_spent_seconds is not None
        assert review.time_spent_seconds >= 0

    @pytest.mark.asyncio
    async def test_deep_verification_review(self, setup_agents, sample_hypothesis):
        """Test deep verification with assumption decomposition."""
        agents = setup_agents
        reflection = agents['reflection']

        # Perform deep verification
        review = await reflection.review_hypothesis(
            hypothesis=sample_hypothesis,
            review_type=ReviewType.DEEP_VERIFICATION
        )

        assert review is not None
        assert review.review_type == ReviewType.DEEP_VERIFICATION

        # Should analyze assumptions
        if review.assumption_decomposition:
            for assumption in review.assumption_decomposition:
                assert assumption.validity in ["valid", "questionable", "invalid"]
                assert assumption.criticality in ["fundamental", "peripheral"]
                assert len(assumption.evidence) > 0

    @pytest.mark.asyncio
    async def test_observation_review(self, setup_agents, sample_hypothesis):
        """Test observation review for explanatory power."""
        agents = setup_agents
        reflection = agents['reflection']

        # Perform observation review
        review = await reflection.review_hypothesis(
            hypothesis=sample_hypothesis,
            review_type=ReviewType.OBSERVATION
        )

        assert review is not None
        assert review.review_type == ReviewType.OBSERVATION

        # Should assess explanatory power
        assert review.scores.quality >= 0
        assert review.narrative_feedback is not None

    @pytest.mark.asyncio
    async def test_simulation_review(self, setup_agents, sample_hypothesis):
        """Test simulation review of hypothesis mechanism."""
        agents = setup_agents
        reflection = agents['reflection']

        # Perform simulation review
        review = await reflection.review_hypothesis(
            hypothesis=sample_hypothesis,
            review_type=ReviewType.SIMULATION
        )

        assert review is not None
        assert review.review_type == ReviewType.SIMULATION

        # Should simulate mechanism
        if review.simulation_results:
            assert len(review.simulation_results.mechanism_steps) > 0
            assert len(review.simulation_results.predicted_outcomes) > 0

            # Check failure points
            for failure in review.simulation_results.failure_points:
                assert 0 <= failure.probability <= 1
                assert len(failure.step) > 0
                assert len(failure.impact) > 0

    @pytest.mark.asyncio
    async def test_tournament_review(self, setup_agents, sample_hypothesis):
        """Test tournament review with adaptive criteria."""
        agents = setup_agents
        reflection = agents['reflection']

        # Add some context for tournament patterns
        context = {
            'tournament_history': [
                {'winner': 'hypothesis_1', 'loser': 'hypothesis_2', 'reason': 'better feasibility'},
                {'winner': 'hypothesis_3', 'loser': 'hypothesis_1', 'reason': 'higher novelty'}
            ],
            'elo_rating': 1350
        }

        # Perform tournament review
        review = await reflection.review_hypothesis(
            hypothesis=sample_hypothesis,
            review_type=ReviewType.TOURNAMENT,
            context=context
        )

        assert review is not None
        assert review.review_type == ReviewType.TOURNAMENT

        # Should adapt based on tournament patterns
        assert review.narrative_feedback is not None
        assert len(review.improvement_suggestions) > 0

    @pytest.mark.asyncio
    async def test_review_types(self, setup_agents, sample_hypothesis):
        """Test all six review types comprehensively."""
        agents = setup_agents
        reflection = agents['reflection']

        # Dictionary to store results from each review type
        review_results = {}

        # Test all review types
        review_types_to_test = [
            (ReviewType.INITIAL, {}),
            (ReviewType.FULL, {'use_tools': True}),
            (ReviewType.DEEP_VERIFICATION, {'focus_areas': ['assumptions']}),
            (ReviewType.OBSERVATION, {'known_observations': ['Observation 1', 'Observation 2']}),
            (ReviewType.SIMULATION, {'experimental_focus': True}),
            (ReviewType.TOURNAMENT, {'tournament_history': [], 'elo_rating': 1200})
        ]

        for review_type, context in review_types_to_test:
            review = await reflection.review_hypothesis(
                hypothesis=sample_hypothesis,
                review_type=review_type,
                context=context
            )

            # Store result
            review_results[review_type] = review

            # Common assertions for all review types
            assert review is not None
            assert review.hypothesis_id == sample_hypothesis.id
            assert review.review_type == review_type
            assert review.decision in [ReviewDecision.ACCEPT, ReviewDecision.REJECT, ReviewDecision.REVISE]
            assert review.scores is not None
            assert 0 <= review.scores.correctness <= 1
            assert 0 <= review.scores.quality <= 1
            assert 0 <= review.scores.novelty <= 1
            assert 0 <= review.scores.safety <= 1
            assert 0 <= review.scores.feasibility <= 1
            assert review.narrative_feedback is not None
            assert len(review.key_strengths) > 0
            assert len(review.key_weaknesses) > 0
            assert review.confidence_level in ["high", "medium", "low"]

        # Verify each review type has specific characteristics

        # Initial review should be quick
        initial_review = review_results[ReviewType.INITIAL]
        assert initial_review.time_spent_seconds is not None
        assert initial_review.time_spent_seconds < 60  # Should be under 60 seconds

        # Full review should be comprehensive
        full_review = review_results[ReviewType.FULL]
        assert len(full_review.narrative_feedback) >= len(initial_review.narrative_feedback)

        # Deep verification should analyze assumptions
        deep_review = review_results[ReviewType.DEEP_VERIFICATION]
        # Check for assumption-related feedback
        assert any('assumption' in weakness.lower() for weakness in deep_review.key_weaknesses) or \
               any('assumption' in strength.lower() for strength in deep_review.key_strengths) or \
               deep_review.assumption_decomposition is not None

        # Observation review should assess explanatory power
        obs_review = review_results[ReviewType.OBSERVATION]
        assert obs_review.scores.quality >= 0  # Should have quality score

        # Simulation review should evaluate mechanism
        sim_review = review_results[ReviewType.SIMULATION]
        assert sim_review.scores.feasibility >= 0  # Should assess feasibility

        # Tournament review should be adaptive
        tourn_review = review_results[ReviewType.TOURNAMENT]
        assert len(tourn_review.improvement_suggestions) > 0

        # Verify all review types were counted
        stats = reflection.get_statistics()
        assert stats['total_reviews'] >= 6
        for review_type in ReviewType:
            assert stats['reviews_by_type'][review_type] >= 1


class TestReviewQuality:
    """Test review quality and consistency."""

    @pytest.mark.asyncio
    async def test_review_consistency(self, setup_agents, sample_hypothesis):
        """Test that multiple reviews of same hypothesis are consistent."""
        agents = setup_agents
        reflection = agents['reflection']

        # Perform multiple initial reviews
        reviews = []
        for _ in range(3):
            review = await reflection.review_hypothesis(
                hypothesis=sample_hypothesis,
                review_type=ReviewType.INITIAL
            )
            reviews.append(review)

        # Check consistency in decisions and scores
        decisions = [r.decision for r in reviews]
        avg_scores = [r.scores.average_score() for r in reviews]

        # Decisions should be mostly consistent
        # (allowing some variation due to mock randomness)
        most_common_decision = max(set(decisions), key=decisions.count)
        decision_consistency = decisions.count(most_common_decision) / len(decisions)
        assert decision_consistency >= 0.5  # At least half should agree

        # Scores should be within reasonable range
        score_variance = max(avg_scores) - min(avg_scores)
        assert score_variance <= 0.5  # Scores shouldn't vary by more than 0.5

    @pytest.mark.asyncio
    async def test_review_quality_metrics(self, setup_agents, sample_hypothesis):
        """Test that review quality metrics are tracked properly."""
        agents = setup_agents
        reflection = agents['reflection']

        # Perform several reviews
        review_types = [
            ReviewType.INITIAL,
            ReviewType.FULL,
            ReviewType.DEEP_VERIFICATION
        ]

        for review_type in review_types:
            await reflection.review_hypothesis(
                hypothesis=sample_hypothesis,
                review_type=review_type
            )

        # Check statistics
        stats = reflection.get_statistics()

        assert stats['total_reviews'] == len(review_types)
        assert stats['agent_id'] == reflection.agent_id

        # Check review type counts
        for review_type in review_types:
            assert stats['reviews_by_type'][review_type] > 0


class TestIntegrationWithOtherAgents:
    """Test integration with other agents."""

    @pytest.mark.asyncio
    async def test_hypothesis_generation_and_reflection(self, setup_agents):
        """Test that generated hypotheses can be reviewed."""
        agents = setup_agents
        generation = agents['generation']
        reflection = agents['reflection']

        # Generate a hypothesis
        from src.core.models import ResearchGoal

        research_goal = ResearchGoal(
            description="Find treatment for disease X",
            constraints=["Must be safe", "Must be feasible"],
            timeframe="6 months",
            success_criteria="Identify viable treatment options"
        )

        hypothesis = await generation.generate_hypothesis(
            research_goal=research_goal,
            generation_method="literature_based",
            existing_hypotheses=[]
        )

        assert hypothesis is not None

        # Review the generated hypothesis
        review = await reflection.review_hypothesis(
            hypothesis=hypothesis,
            review_type=ReviewType.INITIAL
        )

        assert review is not None
        assert review.hypothesis_id == hypothesis.id

    @pytest.mark.asyncio
    async def test_hypothesis_reflection(self, setup_agents, sample_hypothesis):
        """Test comprehensive hypothesis reflection through multiple review types."""
        agents = setup_agents
        reflection = agents['reflection']
        context_memory = agents['context_memory']

        # Store hypothesis for reflection
        await context_memory.set(
            key=f"hypothesis_{sample_hypothesis.id}",
            value=sample_hypothesis.model_dump()
        )

        # Perform multiple review types to reflect on the hypothesis
        review_types_for_reflection = [
            ReviewType.INITIAL,
            ReviewType.FULL,
            ReviewType.DEEP_VERIFICATION
        ]

        reviews = []
        for review_type in review_types_for_reflection:
            review = await reflection.review_hypothesis(
                hypothesis=sample_hypothesis,
                review_type=review_type
            )
            reviews.append(review)

            # Each review should provide reflection
            assert review is not None
            assert review.hypothesis_id == sample_hypothesis.id
            assert review.review_type == review_type
            assert len(review.key_strengths) > 0
            assert len(review.key_weaknesses) > 0
            assert len(review.improvement_suggestions) > 0

        # Check that reviews build on each other (deeper analysis)
        initial_review = reviews[0]
        full_review = reviews[1]
        deep_review = reviews[2]

        # Full review should have more comprehensive feedback
        assert len(full_review.narrative_feedback) >= len(initial_review.narrative_feedback)

        # Deep review should provide assumption analysis
        assert any('assumption' in sugg.lower() for sugg in deep_review.improvement_suggestions) or \
               deep_review.assumption_decomposition is not None

        # Verify all reviews were stored
        stats = reflection.get_statistics()
        assert stats['total_reviews'] >= 3

    @pytest.mark.asyncio
    async def test_supervisor_coordinated_review(self, setup_agents):
        """Test supervisor-coordinated review workflow."""
        agents = setup_agents
        supervisor = agents['supervisor']
        reflection = agents['reflection']
        task_queue = agents['task_queue']
        context_memory = agents['context_memory']

        # Create a hypothesis to review
        hypothesis = Hypothesis(
            id=uuid4(),
            summary="Test hypothesis for supervisor coordination",
            full_description="Detailed description",
            category=HypothesisCategory.MECHANISTIC,
            novelty_claim="Novel approach",
            assumptions=["Assumption 1"],
            reasoning="Reasoning",
            experimental_protocol=ExperimentalProtocol(
                objective="Test",
                methodology="Method",
                expected_outcomes=["Outcome"],
                required_resources=["Resource"],
                timeline="6 months",
                success_metrics=["Metric"],
                potential_challenges=["Challenge"],
                safety_considerations=["Safety"]
            ),
            supporting_evidence=[
                Citation(
                    authors=["Test Author"],
                    title="Test Paper",
                    journal="Test Journal",
                    year=2024
                )
            ],
            confidence_score=0.7,
            generation_method="debate"
        )

        # Store hypothesis in context memory using the correct method
        await context_memory.set(
            key=f"hypothesis_{hypothesis.id}",
            value=hypothesis.model_dump()
        )

        # Create review task (priority must be 1, 2, or 3)
        review_task = Task(
            task_type=TaskType.REFLECT_ON_HYPOTHESIS,
            priority=2,  # Medium priority
            payload={
                'hypothesis_id': str(hypothesis.id),
                'review_type': ReviewType.INITIAL.value
            }
        )

        # Add task to queue
        await task_queue.enqueue(review_task)

        # Register a worker first
        worker_id = await task_queue.register_worker(
            worker_id="reflection_worker_1",
            capabilities=["reflection", TaskType.REFLECT_ON_HYPOTHESIS]
        )

        # Process task (simulating supervisor coordination)
        task_assignment = await task_queue.dequeue(worker_id)
        assert task_assignment is not None
        assert task_assignment.task.task_type == TaskType.REFLECT_ON_HYPOTHESIS

        # Perform the review
        review = await reflection.review_hypothesis(
            hypothesis=hypothesis,
            review_type=ReviewType.INITIAL
        )

        # Store review result
        await context_memory.set(
            key=f"review_{review.id}",
            value=review.model_dump()
        )

        # Verify review was completed and stored
        stored_review = await context_memory.get(f"review_{review.id}")
        assert stored_review is not None
        assert stored_review['hypothesis_id'] == str(hypothesis.id)


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery mechanisms."""

    @pytest.mark.asyncio
    async def test_review_error_recovery(self, setup_agents):
        """Test that agent recovers from review errors."""
        agents = setup_agents
        reflection = agents['reflection']

        # Create a malformed hypothesis
        bad_hypothesis = Hypothesis(
            id=uuid4(),
            summary="",  # Empty summary might cause issues
            full_description="Test",
            category=HypothesisCategory.OTHER,
            novelty_claim="Test",
            assumptions=["Test"],
            reasoning="Test",
            experimental_protocol=ExperimentalProtocol(
                objective="Test",
                methodology="Test",
                expected_outcomes=["Test"],
                required_resources=["Test"],
                timeline="Test",
                success_metrics=["Test metric"],
                potential_challenges=["Test challenge"],
                safety_considerations=["Test safety"]
            ),
            supporting_evidence=[
                Citation(
                    authors=["Test"],
                    title="Test",
                    journal="Test",
                    year=2024
                )
            ],
            confidence_score=0.5,
            generation_method="test"
        )

        # Should handle error gracefully
        review = await reflection.review_hypothesis(
            hypothesis=bad_hypothesis,
            review_type=ReviewType.INITIAL
        )

        assert review is not None
        # Even with error, should return a review (possibly failed)
        assert review.hypothesis_id == bad_hypothesis.id

    @pytest.mark.asyncio
    async def test_concurrent_reviews(self, setup_agents, sample_hypothesis):
        """Test that agent can handle concurrent review requests."""
        agents = setup_agents
        reflection = agents['reflection']

        # Create multiple hypotheses
        hypotheses = []
        for i in range(5):
            hyp = Hypothesis(
                id=uuid4(),
                summary=f"Hypothesis {i}",
                full_description=f"Description {i}",
                category=HypothesisCategory.THERAPEUTIC,
                novelty_claim=f"Novel claim {i}",
                assumptions=[f"Assumption {i}"],
                reasoning=f"Reasoning {i}",
                experimental_protocol=ExperimentalProtocol(
                    objective=f"Objective {i}",
                    methodology="Method",
                    expected_outcomes=["Outcome"],
                    required_resources=["Resource"],
                    timeline="6 months",
                    success_metrics=["Metric"],
                    potential_challenges=["Challenge"],
                    safety_considerations=["Safety"]
                ),
                supporting_evidence=[
                    Citation(
                        authors=[f"Author {i}"],
                        title=f"Evidence Paper {i}",
                        journal="Test Journal",
                        year=2024
                    )
                ],
                confidence_score=0.6 + i * 0.05,
                generation_method="test"
            )
            hypotheses.append(hyp)

        # Review all hypotheses concurrently
        review_tasks = [
            reflection.review_hypothesis(hyp, ReviewType.INITIAL)
            for hyp in hypotheses
        ]

        reviews = await asyncio.gather(*review_tasks)

        # All reviews should complete
        assert len(reviews) == len(hypotheses)
        for review, hypothesis in zip(reviews, hypotheses):
            assert review.hypothesis_id == hypothesis.id


class TestStatePersistence:
    """Test state persistence and recovery."""

    @pytest.mark.asyncio
    async def test_agent_state_persistence(self, setup_agents):
        """Test that agent state is properly persisted."""
        agents = setup_agents
        reflection = agents['reflection']
        context_memory = agents['context_memory']

        # Perform some reviews to build state
        hypothesis = Hypothesis(
            id=uuid4(),
            summary="Test hypothesis",
            full_description="Test description",
            category=HypothesisCategory.DIAGNOSTIC,
            novelty_claim="Novel",
            assumptions=["Assumption"],
            reasoning="Reasoning",
            experimental_protocol=ExperimentalProtocol(
                objective="Test",
                methodology="Method",
                expected_outcomes=["Outcome"],
                required_resources=["Resource"],
                timeline="3 months",
                success_metrics=["Metric"],
                potential_challenges=["Challenge"],
                safety_considerations=["Safety"]
            ),
            supporting_evidence=[
                Citation(
                    authors=["Test Author"],
                    title="Test Paper",
                    journal="Test Journal",
                    year=2024
                )
            ],
            confidence_score=0.8,
            generation_method="test"
        )

        # Perform reviews
        for review_type in [ReviewType.INITIAL, ReviewType.FULL]:
            await reflection.review_hypothesis(hypothesis, review_type)

        # Shutdown agent (should persist state)
        await reflection.shutdown()

        # Check that statistics were persisted as aggregate
        persisted_stats = await context_memory.retrieve_aggregate(
            aggregate_type='agent_statistics',
            query_type='latest'
        )

        assert persisted_stats is not None
        assert persisted_stats['stats']['total_reviews'] >= 2  # At least 2 reviews
        assert persisted_stats['agent_id'] == reflection.agent_id
        assert persisted_stats['final'] is True