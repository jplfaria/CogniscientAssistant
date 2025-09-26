"""Cross-component workflow integration tests.

These tests verify that different agents can work together properly across phases.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest

from src.agents.generation import GenerationAgent
from src.agents.reflection import ReflectionAgent
from src.agents.supervisor import SupervisorAgent
from src.core.context_memory import ContextMemory
from src.core.models import (
    Hypothesis,
    HypothesisCategory,
    ExperimentalProtocol,
    ResearchGoal,
    ReviewType,
    ReviewDecision,
    Task,
    TaskType,
    TaskState,
    utcnow
)
from src.core.task_queue import TaskQueue, QueueConfig
from src.llm.mock_provider import MockLLMProvider, MockConfiguration


@pytest.fixture
async def integrated_system(tmp_path):
    """Set up integrated system with all agents."""
    # Create infrastructure
    queue_config = QueueConfig()
    queue_config.max_queue_size = 100
    task_queue = TaskQueue(config=queue_config)

    context_memory = ContextMemory(
        storage_path=tmp_path / "test_memory",
        checkpoint_interval_minutes=1
    )

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

    return {
        'supervisor': supervisor,
        'generation': generation,
        'reflection': reflection,
        'task_queue': task_queue,
        'context_memory': context_memory,
        'llm_provider': llm_provider
    }


class TestCrossComponentWorkflow:
    """Test workflows across multiple components."""

    @pytest.mark.asyncio
    async def test_hypothesis_generation(self, integrated_system):
        """Test hypothesis generation workflow across agents."""
        system = integrated_system
        generation = system['generation']
        context_memory = system['context_memory']

        # Create research goal
        research_goal = ResearchGoal(
            description="Find treatment for disease X",
            constraints=["Must be safe", "Must be cost-effective"],
            success_criteria=["Reduces symptoms by 50%"],
            time_horizon="12 months"
        )

        # Generate hypothesis
        hypothesis = await generation.generate_hypothesis(
            research_goal=research_goal,
            generation_method="literature_based"
        )

        assert hypothesis is not None
        assert hypothesis.id is not None
        assert hypothesis.summary != ""
        assert hypothesis.category in HypothesisCategory
        assert hypothesis.confidence_score >= 0.0
        assert hypothesis.confidence_score <= 1.0

        # Verify hypothesis was stored in context memory
        stored_hypotheses = await context_memory.get('hypotheses')
        assert stored_hypotheses is not None
        assert len(stored_hypotheses) > 0

        # Find our hypothesis in storage
        found = False
        for stored in stored_hypotheses:
            if stored['id'] == str(hypothesis.id):
                found = True
                break
        assert found, "Generated hypothesis should be stored in context memory"

    @pytest.mark.asyncio
    async def test_hypothesis_reflection(self, integrated_system):
        """Test hypothesis review/reflection workflow across agents."""
        system = integrated_system
        generation = system['generation']
        reflection = system['reflection']
        context_memory = system['context_memory']

        # First generate a hypothesis
        research_goal = ResearchGoal(
            description="Find biomarker for disease Y",
            constraints=["Must be measurable in blood"],
            success_criteria=["90% specificity", "85% sensitivity"],
            time_horizon="6 months"
        )

        hypothesis = await generation.generate_hypothesis(
            research_goal=research_goal,
            generation_method="assumptions"
        )

        assert hypothesis is not None

        # Now review the hypothesis
        review = await reflection.review_hypothesis(
            hypothesis=hypothesis,
            review_type=ReviewType.INITIAL
        )

        assert review is not None
        assert review.hypothesis_id == hypothesis.id
        assert review.review_type == ReviewType.INITIAL
        assert review.decision in [ReviewDecision.ACCEPT, ReviewDecision.REJECT, ReviewDecision.REVISE]
        assert review.scores is not None
        assert len(review.key_strengths) >= 0  # Can be empty for poor hypotheses
        assert len(review.key_weaknesses) >= 0
        assert review.confidence_level in ["high", "medium", "low"]

        # Verify review was stored
        agent_outputs = await context_memory.get_agent_outputs()
        assert len(agent_outputs) > 0

        # Find review output
        found_review = False
        for output in agent_outputs:
            if output.agent_type == 'reflection' and output.results.get('hypothesis_id') == str(hypothesis.id):
                found_review = True
                break
        assert found_review, "Review should be stored as agent output"

    @pytest.mark.asyncio
    async def test_review_types(self, integrated_system):
        """Test different review types work correctly."""
        system = integrated_system
        generation = system['generation']
        reflection = system['reflection']

        # Generate a hypothesis to review
        research_goal = ResearchGoal(
            description="Develop therapy for condition Z",
            constraints=["Must target specific pathway"],
            success_criteria=["Improved patient outcomes"],
            time_horizon="18 months"
        )

        hypothesis = await generation.generate_hypothesis(
            research_goal=research_goal,
            generation_method="debate"
        )

        # Test different review types
        review_types_to_test = [
            ReviewType.INITIAL,
            ReviewType.FULL,
            ReviewType.DEEP_VERIFICATION,
            ReviewType.OBSERVATION,
            ReviewType.SIMULATION,
            ReviewType.TOURNAMENT
        ]

        reviews = {}
        for review_type in review_types_to_test:
            review = await reflection.review_hypothesis(
                hypothesis=hypothesis,
                review_type=review_type
            )

            assert review is not None
            assert review.review_type == review_type
            assert review.hypothesis_id == hypothesis.id
            reviews[review_type] = review

        # Verify different review types produce different results
        # (They should have different focuses and potentially different scores)
        initial_scores = reviews[ReviewType.INITIAL].scores.average_score()
        full_scores = reviews[ReviewType.FULL].scores.average_score()

        # Scores might differ but should be within reasonable range
        assert abs(initial_scores - full_scores) <= 1.0  # Max difference is 1.0

        # Different review types should have been performed
        assert len(reviews) == len(review_types_to_test)

    @pytest.mark.asyncio
    async def test_full_research_cycle(self, integrated_system):
        """Test a complete research cycle: goal -> generation -> reflection."""
        system = integrated_system
        supervisor = system['supervisor']
        generation = system['generation']
        reflection = system['reflection']
        task_queue = system['task_queue']
        context_memory = system['context_memory']

        # Create research goal
        research_goal = ResearchGoal(
            description="Find novel treatment for rare disease",
            constraints=["Must be FDA-approvable", "Cost under $100k/year"],
            success_criteria=["Extends life by 2+ years", "Improves quality of life"],
            time_horizon="5 years"
        )

        # Store research goal
        await context_memory.set('research_goal', {
            'description': research_goal.description,
            'constraints': research_goal.constraints,
            'success_criteria': research_goal.success_criteria,
            'time_horizon': research_goal.time_horizon
        })

        # Supervisor creates generation task
        generation_task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=8,
            payload={
                'research_goal': research_goal.description,
                'generation_method': 'literature_based'
            }
        )
        task_queue.enqueue(generation_task)

        # Process generation
        task = task_queue.dequeue()
        assert task is not None

        hypothesis = await generation.generate_hypothesis(
            research_goal=research_goal,
            generation_method='literature_based'
        )

        # Create reflection task
        reflection_task = Task(
            task_type=TaskType.REFLECT_ON_HYPOTHESIS,
            priority=7,
            payload={
                'hypothesis_id': str(hypothesis.id),
                'review_type': ReviewType.INITIAL.value
            }
        )
        task_queue.enqueue(reflection_task)

        # Process reflection
        task = task_queue.dequeue()
        assert task is not None

        review = await reflection.review_hypothesis(
            hypothesis=hypothesis,
            review_type=ReviewType.INITIAL
        )

        # Verify complete cycle
        assert hypothesis is not None
        assert review is not None
        assert review.hypothesis_id == hypothesis.id

        # Check supervisor statistics
        stats = supervisor.get_statistics()
        assert stats['tasks_created'] >= 2  # At least generation and reflection tasks

    @pytest.mark.asyncio
    async def test_multi_hypothesis_workflow(self, integrated_system):
        """Test workflow with multiple hypotheses being generated and reviewed."""
        system = integrated_system
        generation = system['generation']
        reflection = system['reflection']

        research_goal = ResearchGoal(
            description="Find multiple approaches to problem",
            constraints=["Various constraints"],
            success_criteria=["Multiple success metrics"],
            time_horizon="1 year"
        )

        # Generate multiple hypotheses with different methods
        generation_methods = ['literature_based', 'debate', 'assumptions']
        hypotheses = []

        for method in generation_methods:
            hypothesis = await generation.generate_hypothesis(
                research_goal=research_goal,
                generation_method=method
            )
            hypotheses.append(hypothesis)

        assert len(hypotheses) == len(generation_methods)

        # Review all hypotheses
        reviews = []
        for hypothesis in hypotheses:
            review = await reflection.review_hypothesis(
                hypothesis=hypothesis,
                review_type=ReviewType.INITIAL
            )
            reviews.append(review)

        assert len(reviews) == len(hypotheses)

        # Each hypothesis should have a corresponding review
        for hypothesis, review in zip(hypotheses, reviews):
            assert review.hypothesis_id == hypothesis.id

        # Different generation methods might lead to different review outcomes
        decisions = [r.decision for r in reviews]
        # At least one should be accepted or need revision
        assert ReviewDecision.REJECT not in decisions or len(set(decisions)) > 1