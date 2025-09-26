"""Reflection Agent - Scientific peer review for hypotheses.

The Reflection Agent simulates scientific peer review within the AI Co-Scientist system.
It critically examines hypotheses for correctness, quality, novelty, and safety through
six distinct review types. The agent evaluates whether hypotheses provide improved
explanations for existing research observations and identifies potential failure scenarios.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from src.core.models import (
    Hypothesis,
    Review,
    ReviewType,
    ReviewDecision,
    ReviewScores,
    AssumptionDecomposition,
    SimulationResults,
    FailurePoint,
    Citation,
    utcnow
)
from src.core.task_queue import TaskQueue
from src.core.context_memory import ContextMemory
from src.llm.base import LLMProvider
from src.llm.baml_wrapper import BAMLWrapper
from src.core.safety import SafetyLevel, SafetyLogger, SafetyConfig


logger = logging.getLogger(__name__)


class ReflectionAgent:
    """Agent responsible for evaluating and reviewing scientific hypotheses.

    Implements six distinct review types to comprehensively assess hypotheses
    for scientific validity, safety, novelty, and feasibility.
    """

    # Review type configurations
    REVIEW_TYPE_CONFIGS = {
        ReviewType.INITIAL: {
            'use_tools': False,
            'timeout': 60,
            'focus': ['correctness', 'quality', 'novelty', 'preliminary_safety']
        },
        ReviewType.FULL: {
            'use_tools': True,
            'timeout': 300,
            'focus': ['correctness', 'quality', 'novelty', 'literature_grounding']
        },
        ReviewType.DEEP_VERIFICATION: {
            'use_tools': True,
            'timeout': 600,
            'focus': ['assumption_validity', 'logical_consistency']
        },
        ReviewType.OBSERVATION: {
            'use_tools': True,
            'timeout': 300,
            'focus': ['explanatory_power', 'existing_phenomena']
        },
        ReviewType.SIMULATION: {
            'use_tools': False,
            'timeout': 240,
            'focus': ['mechanism_validity', 'failure_points']
        },
        ReviewType.TOURNAMENT: {
            'use_tools': False,
            'timeout': 180,
            'focus': ['adaptive_criteria', 'weakness_patterns']
        }
    }

    def __init__(
        self,
        task_queue: TaskQueue,
        context_memory: ContextMemory,
        llm_provider: LLMProvider,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize ReflectionAgent with dependencies.

        Args:
            task_queue: Task queue for receiving review tasks
            context_memory: Context memory for storing/retrieving reviews
            llm_provider: LLM provider for evaluation operations
            config: Optional configuration parameters
        """
        self.task_queue = task_queue
        self.context_memory = context_memory
        self.llm_provider = llm_provider

        # Configuration
        config = config or {}
        self.confidence_threshold = config.get('confidence_threshold', 0.6)
        self.strict_mode = config.get('strict_mode', False)
        self.max_retries = config.get('max_retries', 2)
        self.enable_caching = config.get('enable_caching', True)

        # Initialize agent ID
        self.agent_id = f"reflection_agent_{uuid4().hex[:8]}"

        # State tracking
        self._review_count = 0
        self._review_type_counts = {rt: 0 for rt in ReviewType}
        self._average_scores = {}

        # Web search integration (to be injected or configured)
        self.web_search = None

        # Initialize BAML wrapper
        self.baml_wrapper = BAMLWrapper(provider=llm_provider)

        # Initialize safety logger (can be disabled via config)
        if config.get('enable_safety_logging', True):
            safety_config = SafetyConfig(
                enabled=True,
                trust_level=config.get('safety_trust_level', 'standard'),
                log_only_mode=True,
                log_directory=config.get('safety_log_directory', '.aicoscientist/safety_logs')
            )
            self.safety_logger = SafetyLogger(safety_config)
        else:
            self.safety_logger = None

    async def review_hypothesis(
        self,
        hypothesis: Hypothesis,
        review_type: ReviewType,
        context: Optional[Dict[str, Any]] = None
    ) -> Review:
        """Review a hypothesis using the specified review type.

        Args:
            hypothesis: The hypothesis to review
            review_type: Type of review to perform
            context: Optional additional context for review

        Returns:
            Review object containing evaluation results
        """
        start_time = time.time()

        # Get review configuration
        review_config = self.REVIEW_TYPE_CONFIGS.get(
            review_type,
            self.REVIEW_TYPE_CONFIGS[ReviewType.INITIAL]
        )

        # Log safety check if enabled
        if self.safety_logger:
            self.safety_logger.log_hypothesis(
                hypothesis_id=str(hypothesis.id),
                content=hypothesis.full_description,
                safety_level=SafetyLevel.SAFE  # Will be updated based on review
            )

        try:
            # Prepare evaluation context
            evaluation_context = self._prepare_evaluation_context(
                hypothesis, review_type, context
            )

            # Call appropriate review method based on type
            if review_type == ReviewType.INITIAL:
                review = await self._perform_initial_review(
                    hypothesis, evaluation_context
                )
            elif review_type == ReviewType.FULL:
                review = await self._perform_full_review(
                    hypothesis, evaluation_context
                )
            elif review_type == ReviewType.DEEP_VERIFICATION:
                review = await self._perform_deep_verification(
                    hypothesis, evaluation_context
                )
            elif review_type == ReviewType.OBSERVATION:
                review = await self._perform_observation_review(
                    hypothesis, evaluation_context
                )
            elif review_type == ReviewType.SIMULATION:
                review = await self._perform_simulation_review(
                    hypothesis, evaluation_context
                )
            elif review_type == ReviewType.TOURNAMENT:
                review = await self._perform_tournament_review(
                    hypothesis, evaluation_context
                )
            else:
                raise ValueError(f"Unknown review type: {review_type}")

            # Add metadata
            review.time_spent_seconds = time.time() - start_time

            # Update tracking
            self._review_count += 1
            self._review_type_counts[review_type] += 1
            self._update_average_scores(review)

            # Store review in context memory
            await self._store_review(review)

            return review

        except Exception as e:
            logger.error(f"Error reviewing hypothesis {hypothesis.id}: {e}")
            # Return a failed review
            return self._create_failed_review(
                hypothesis, review_type, str(e), time.time() - start_time
            )

    async def _perform_initial_review(
        self,
        hypothesis: Hypothesis,
        context: Dict[str, Any]
    ) -> Review:
        """Perform fast initial review without external tools.

        Args:
            hypothesis: The hypothesis to review
            context: Evaluation context

        Returns:
            Initial review results
        """
        # Use BAML to evaluate hypothesis
        baml_review = await self.baml_wrapper.evaluate_hypothesis(
            hypothesis=hypothesis,
            review_type=ReviewType.INITIAL,
            evaluation_criteria=context.get('criteria', [
                "Scientific correctness",
                "Internal consistency",
                "Basic novelty assessment",
                "Obvious safety concerns"
            ]),
            context=context
        )

        # Convert BAML review to our Review model
        review = Review(
            hypothesis_id=hypothesis.id,
            reviewer_agent_id=self.agent_id,
            review_type=ReviewType.INITIAL,
            decision=baml_review.decision,
            scores=baml_review.scores,
            narrative_feedback=baml_review.narrative_feedback,
            key_strengths=baml_review.key_strengths,
            key_weaknesses=baml_review.key_weaknesses,
            improvement_suggestions=baml_review.improvement_suggestions,
            confidence_level=baml_review.confidence_level
        )

        return review

    async def _perform_full_review(
        self,
        hypothesis: Hypothesis,
        context: Dict[str, Any]
    ) -> Review:
        """Perform comprehensive review with literature search.

        Args:
            hypothesis: The hypothesis to review
            context: Evaluation context

        Returns:
            Full review results with citations
        """
        # If web search is available, gather literature
        literature_context = {}
        if self.web_search and context.get('use_tools', True):
            literature_context = await self._search_literature(hypothesis)
            context['literature'] = literature_context

        # Use BAML to evaluate with full context
        baml_review = await self.baml_wrapper.evaluate_hypothesis(
            hypothesis=hypothesis,
            review_type=ReviewType.FULL,
            evaluation_criteria=context.get('criteria', [
                "Scientific rigor and accuracy",
                "Literature grounding",
                "True novelty vs existing work",
                "Methodological soundness",
                "Safety and ethical considerations"
            ]),
            context=context
        )

        # Convert to Review model with literature citations
        review = Review(
            hypothesis_id=hypothesis.id,
            reviewer_agent_id=self.agent_id,
            review_type=ReviewType.FULL,
            decision=baml_review.decision,
            scores=baml_review.scores,
            narrative_feedback=baml_review.narrative_feedback,
            key_strengths=baml_review.key_strengths,
            key_weaknesses=baml_review.key_weaknesses,
            improvement_suggestions=baml_review.improvement_suggestions,
            confidence_level=baml_review.confidence_level,
            literature_citations=baml_review.literature_citations if hasattr(baml_review, 'literature_citations') else None
        )

        return review

    async def _perform_deep_verification(
        self,
        hypothesis: Hypothesis,
        context: Dict[str, Any]
    ) -> Review:
        """Perform deep assumption decomposition and verification.

        Args:
            hypothesis: The hypothesis to review
            context: Evaluation context

        Returns:
            Deep verification review with assumption analysis
        """
        # Use BAML to decompose and evaluate assumptions
        baml_review = await self.baml_wrapper.evaluate_hypothesis(
            hypothesis=hypothesis,
            review_type=ReviewType.DEEP_VERIFICATION,
            evaluation_criteria=context.get('criteria', [
                "Decompose into fundamental assumptions",
                "Verify each assumption independently",
                "Identify critical vs peripheral assumptions",
                "Find logical inconsistencies",
                "Assess overall validity"
            ]),
            context=context
        )

        # Convert to Review model with assumption decomposition
        review = Review(
            hypothesis_id=hypothesis.id,
            reviewer_agent_id=self.agent_id,
            review_type=ReviewType.DEEP_VERIFICATION,
            decision=baml_review.decision,
            scores=baml_review.scores,
            narrative_feedback=baml_review.narrative_feedback,
            key_strengths=baml_review.key_strengths,
            key_weaknesses=baml_review.key_weaknesses,
            improvement_suggestions=baml_review.improvement_suggestions,
            confidence_level=baml_review.confidence_level,
            assumption_decomposition=baml_review.assumption_decomposition if hasattr(baml_review, 'assumption_decomposition') else None
        )

        return review

    async def _perform_observation_review(
        self,
        hypothesis: Hypothesis,
        context: Dict[str, Any]
    ) -> Review:
        """Review hypothesis for explanatory power of existing phenomena.

        Args:
            hypothesis: The hypothesis to review
            context: Evaluation context

        Returns:
            Observation review assessing explanatory power
        """
        # Use BAML to evaluate explanatory power
        baml_review = await self.baml_wrapper.evaluate_hypothesis(
            hypothesis=hypothesis,
            review_type=ReviewType.OBSERVATION,
            evaluation_criteria=context.get('criteria', [
                "Explains existing observations",
                "Addresses unexplained phenomena",
                "Consistency with known data",
                "Predictive power",
                "Comparison with current theories"
            ]),
            context=context
        )

        # Convert to Review model
        review = Review(
            hypothesis_id=hypothesis.id,
            reviewer_agent_id=self.agent_id,
            review_type=ReviewType.OBSERVATION,
            decision=baml_review.decision,
            scores=baml_review.scores,
            narrative_feedback=baml_review.narrative_feedback,
            key_strengths=baml_review.key_strengths,
            key_weaknesses=baml_review.key_weaknesses,
            improvement_suggestions=baml_review.improvement_suggestions,
            confidence_level=baml_review.confidence_level
        )

        return review

    async def _perform_simulation_review(
        self,
        hypothesis: Hypothesis,
        context: Dict[str, Any]
    ) -> Review:
        """Simulate the hypothesis mechanism step-by-step.

        Args:
            hypothesis: The hypothesis to review
            context: Evaluation context

        Returns:
            Simulation review with mechanism analysis
        """
        # Use BAML to simulate mechanism
        baml_review = await self.baml_wrapper.evaluate_hypothesis(
            hypothesis=hypothesis,
            review_type=ReviewType.SIMULATION,
            evaluation_criteria=context.get('criteria', [
                "Step-by-step mechanism simulation",
                "Identify causal chain",
                "Find potential failure points",
                "Predict experimental outcomes",
                "Assess practical feasibility"
            ]),
            context=context
        )

        # Convert to Review model with simulation results
        review = Review(
            hypothesis_id=hypothesis.id,
            reviewer_agent_id=self.agent_id,
            review_type=ReviewType.SIMULATION,
            decision=baml_review.decision,
            scores=baml_review.scores,
            narrative_feedback=baml_review.narrative_feedback,
            key_strengths=baml_review.key_strengths,
            key_weaknesses=baml_review.key_weaknesses,
            improvement_suggestions=baml_review.improvement_suggestions,
            confidence_level=baml_review.confidence_level,
            simulation_results=baml_review.simulation_results if hasattr(baml_review, 'simulation_results') else None
        )

        return review

    async def _perform_tournament_review(
        self,
        hypothesis: Hypothesis,
        context: Dict[str, Any]
    ) -> Review:
        """Perform adaptive review based on tournament patterns.

        Args:
            hypothesis: The hypothesis to review
            context: Evaluation context with tournament history

        Returns:
            Tournament-adapted review
        """
        # Get tournament patterns from context memory
        patterns = await self._get_tournament_patterns(hypothesis)
        context['tournament_patterns'] = patterns

        # Use BAML to perform adaptive review
        baml_review = await self.baml_wrapper.evaluate_hypothesis(
            hypothesis=hypothesis,
            review_type=ReviewType.TOURNAMENT,
            evaluation_criteria=context.get('criteria', [
                "Address known weakness patterns",
                "Leverage identified strengths",
                "Compare to high-performing hypotheses",
                "Strategic positioning",
                "Competitive advantages"
            ]),
            context=context
        )

        # Convert to Review model
        review = Review(
            hypothesis_id=hypothesis.id,
            reviewer_agent_id=self.agent_id,
            review_type=ReviewType.TOURNAMENT,
            decision=baml_review.decision,
            scores=baml_review.scores,
            narrative_feedback=baml_review.narrative_feedback,
            key_strengths=baml_review.key_strengths,
            key_weaknesses=baml_review.key_weaknesses,
            improvement_suggestions=baml_review.improvement_suggestions,
            confidence_level=baml_review.confidence_level
        )

        return review

    def _prepare_evaluation_context(
        self,
        hypothesis: Hypothesis,
        review_type: ReviewType,
        external_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Prepare context for hypothesis evaluation.

        Args:
            hypothesis: The hypothesis being reviewed
            review_type: Type of review being performed
            external_context: Additional context provided

        Returns:
            Prepared evaluation context
        """
        config = self.REVIEW_TYPE_CONFIGS[review_type]

        context = {
            'review_type': review_type.value,
            'hypothesis_id': str(hypothesis.id),
            'category': hypothesis.category.value,
            'use_tools': config['use_tools'],
            'timeout': config['timeout'],
            'focus_areas': config['focus'],
            'strict_mode': self.strict_mode,
            'agent_id': self.agent_id
        }

        # Merge external context
        if external_context:
            context.update(external_context)

        return context

    async def _search_literature(
        self,
        hypothesis: Hypothesis
    ) -> Dict[str, Any]:
        """Search literature for hypothesis validation.

        Args:
            hypothesis: The hypothesis to validate

        Returns:
            Literature search results
        """
        if not self.web_search:
            return {}

        # Extract key terms for search
        search_terms = self._extract_search_terms(hypothesis)

        # Perform searches (placeholder for actual implementation)
        results = {
            'papers_found': 0,
            'relevant_citations': [],
            'conflicting_evidence': [],
            'supporting_evidence': []
        }

        # This would integrate with actual web search tools
        # For now, return placeholder results
        return results

    def _extract_search_terms(self, hypothesis: Hypothesis) -> List[str]:
        """Extract search terms from hypothesis.

        Args:
            hypothesis: The hypothesis to extract terms from

        Returns:
            List of search terms
        """
        # Simple extraction - could be enhanced with NLP
        terms = []

        # Add category-specific terms
        if hypothesis.category:
            terms.append(hypothesis.category.value)

        # Extract from summary (simplified)
        summary_words = hypothesis.summary.split()
        # Filter for likely scientific terms (capitalized, long words)
        terms.extend([w for w in summary_words if len(w) > 5])

        return terms[:5]  # Limit to top 5 terms

    async def _get_tournament_patterns(
        self,
        hypothesis: Hypothesis
    ) -> Dict[str, Any]:
        """Get tournament patterns for adaptive review.

        Args:
            hypothesis: The hypothesis being reviewed

        Returns:
            Tournament patterns and insights
        """
        # Query context memory for tournament data
        patterns = {
            'common_strengths': [],
            'common_weaknesses': [],
            'winning_strategies': [],
            'elo_threshold': 1400
        }

        # This would query actual tournament history
        # For now, return placeholder patterns
        return patterns

    def _update_average_scores(self, review: Review) -> None:
        """Update running average of review scores.

        Args:
            review: The completed review
        """
        avg = review.scores.average_score()

        if review.review_type not in self._average_scores:
            self._average_scores[review.review_type] = []

        self._average_scores[review.review_type].append(avg)

        # Keep only last 100 scores
        if len(self._average_scores[review.review_type]) > 100:
            self._average_scores[review.review_type].pop(0)

    async def _store_review(self, review: Review) -> None:
        """Store review in context memory.

        Args:
            review: The review to store
        """
        # Store as agent output
        from src.core.context_memory import AgentOutput

        agent_output = AgentOutput(
            agent_type='reflection',
            task_id=f"review_{review.id}",
            timestamp=review.created_at,
            results={
                'review': review.model_dump(),
                'hypothesis_id': str(review.hypothesis_id),
                'review_type': review.review_type.value,
                'reviewer_agent_id': self.agent_id
            },
            state_data={'agent_id': self.agent_id}
        )

        await self.context_memory.store_agent_output(agent_output)

    def _create_failed_review(
        self,
        hypothesis: Hypothesis,
        review_type: ReviewType,
        error_message: str,
        time_spent: float
    ) -> Review:
        """Create a review object for failed evaluation.

        Args:
            hypothesis: The hypothesis that failed review
            review_type: Type of review attempted
            error_message: Error that occurred
            time_spent: Time spent before failure

        Returns:
            Review object marked as failed
        """
        return Review(
            hypothesis_id=hypothesis.id,
            reviewer_agent_id=self.agent_id,
            review_type=review_type,
            decision=ReviewDecision.REJECT,
            scores=ReviewScores(
                correctness=0.0,
                quality=0.0,
                novelty=0.0,
                safety=0.0,
                feasibility=0.0
            ),
            narrative_feedback=f"Review failed: {error_message}",
            key_strengths=["Unable to evaluate"],
            key_weaknesses=["Review process failed"],
            improvement_suggestions=["Retry review with different parameters"],
            confidence_level="low",
            time_spent_seconds=time_spent
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics.

        Returns:
            Dictionary of agent statistics
        """
        stats = {
            'agent_id': self.agent_id,
            'total_reviews': self._review_count,
            'reviews_by_type': dict(self._review_type_counts),
            'average_scores': {}
        }

        # Calculate averages
        for review_type, scores in self._average_scores.items():
            if scores:
                stats['average_scores'][review_type.value] = sum(scores) / len(scores)

        return stats

    async def generate_review(
        self,
        hypothesis: Hypothesis,
        review_type: ReviewType,
        criteria: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Review:
        """Generate a review using BAML function.

        This method is called by the review_hypothesis method and other agents
        that need to generate reviews. It uses BAML for content generation.

        Args:
            hypothesis: The hypothesis to review
            review_type: Type of review to perform
            criteria: Evaluation criteria
            context: Additional context for review

        Returns:
            Generated review
        """
        # Use BAML to generate the review
        baml_review = await self.baml_wrapper.evaluate_hypothesis(
            hypothesis=hypothesis,
            review_type=review_type,
            evaluation_criteria=criteria,
            context=context or {}
        )

        # Create Review model with generated content
        review = Review(
            hypothesis_id=hypothesis.id,
            reviewer_agent_id=self.agent_id,
            review_type=review_type,
            decision=baml_review.decision,
            scores=baml_review.scores,
            narrative_feedback=baml_review.narrative_feedback,
            key_strengths=baml_review.key_strengths,
            key_weaknesses=baml_review.key_weaknesses,
            improvement_suggestions=baml_review.improvement_suggestions,
            confidence_level=baml_review.confidence_level,
            assumption_decomposition=getattr(baml_review, 'assumption_decomposition', None),
            simulation_results=getattr(baml_review, 'simulation_results', None),
            literature_citations=getattr(baml_review, 'literature_citations', None)
        )

        return review

    async def generate_critique(
        self,
        hypothesis: Hypothesis,
        focus_areas: List[str]
    ) -> Dict[str, Any]:
        """Generate a detailed critique of a hypothesis.

        This method is used to generate focused critiques on specific aspects
        of a hypothesis. It uses BAML for content generation.

        Args:
            hypothesis: The hypothesis to critique
            focus_areas: Specific areas to focus the critique on

        Returns:
            Detailed critique with strengths, weaknesses, and suggestions
        """
        # Generate a focused review using BAML
        review = await self.generate_review(
            hypothesis=hypothesis,
            review_type=ReviewType.FULL,
            criteria=focus_areas,
            context={'critique_mode': True, 'detailed_feedback': True}
        )

        # Extract and return critique components
        return {
            'strengths': review.key_strengths,
            'weaknesses': review.key_weaknesses,
            'suggestions': review.improvement_suggestions,
            'overall_assessment': review.narrative_feedback,
            'scores': {
                'correctness': review.scores.correctness,
                'quality': review.scores.quality,
                'novelty': review.scores.novelty,
                'safety': review.scores.safety,
                'feasibility': review.scores.feasibility
            },
            'confidence': review.confidence_level,
            'review_type': review.review_type.value
        }

    async def shutdown(self) -> None:
        """Gracefully shutdown the agent."""
        logger.info(f"Shutting down {self.agent_id}")

        # Store final statistics as aggregate
        stats = self.get_statistics()
        await self.context_memory.store_aggregate(
            aggregate_type='agent_statistics',
            data={
                'agent_id': self.agent_id,
                'agent_type': 'reflection',
                'stats': stats,
                'final': True
            },
            timestamp=datetime.now()
        )