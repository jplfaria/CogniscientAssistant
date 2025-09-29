"""Agent Output Validator for context optimization.

This module implements validation and confidence assessment for agent outputs
when using optimized context, ensuring quality is maintained even with reduced
context size.
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from src.core.models import Hypothesis, Review, Paper

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of agent output validation."""
    output: Any
    confidence: float
    requires_fallback: bool
    validation_notes: str


class AgentOutputValidator:
    """Validates agent outputs and assesses confidence levels."""

    def __init__(self, confidence_threshold: float = 0.7):
        """Initialize the validator with confidence threshold.

        Args:
            confidence_threshold: Minimum confidence for accepting optimized results
        """
        self.confidence_threshold = confidence_threshold

        # Quality indicators for different output types
        self.quality_indicators = {
            'hypothesis': {
                'required_fields': ['summary', 'full_description', 'assumptions', 'experimental_protocol'],
                'quality_checks': ['has_novel_claim', 'has_testable_protocol', 'has_citations']
            },
            'review': {
                'required_fields': ['decision', 'scores', 'narrative_feedback'],
                'quality_checks': ['has_strengths', 'has_weaknesses', 'has_suggestions']
            },
            'ranking': {
                'required_fields': ['rankings', 'criteria'],
                'quality_checks': ['has_reasoning', 'consistent_scoring']
            }
        }

    async def validate_output(self, agent_output: Any,
                            agent_type: str,
                            context: str,
                            original_context_size: Optional[int] = None,
                            optimized_context_size: Optional[int] = None) -> ValidationResult:
        """Validate agent output with confidence assessment.

        Args:
            agent_output: Output from the agent to validate
            agent_type: Type of agent that produced the output
            context: Context description used for generation
            original_context_size: Size of original context (for comparison)
            optimized_context_size: Size of optimized context used

        Returns:
            ValidationResult with confidence assessment
        """
        # Calculate base confidence score
        confidence_score = await self._calculate_confidence_score(
            output=agent_output,
            agent_type=agent_type,
            context=context
        )

        # Apply context optimization penalty/bonus
        if original_context_size and optimized_context_size:
            context_factor = self._calculate_context_optimization_factor(
                original_context_size, optimized_context_size, confidence_score
            )
            confidence_score *= context_factor

        # Determine if fallback is needed
        should_fallback = confidence_score < self.confidence_threshold

        # Generate validation notes
        validation_notes = self._generate_validation_notes(
            confidence_score, agent_type, should_fallback
        )

        return ValidationResult(
            output=agent_output,
            confidence=min(confidence_score, 1.0),
            requires_fallback=should_fallback,
            validation_notes=validation_notes
        )

    async def _calculate_confidence_score(self, output: Any,
                                        agent_type: str,
                                        context: str) -> float:
        """Calculate confidence score for agent output.

        Args:
            output: Agent output to assess
            agent_type: Type of agent
            context: Context used for generation

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Route to agent-specific validation
        if agent_type.lower() == 'generation' and isinstance(output, Hypothesis):
            return await self._validate_hypothesis(output, context)
        elif agent_type.lower() == 'reflection' and isinstance(output, Review):
            return await self._validate_review(output, context)
        elif agent_type.lower() in ['ranking', 'tournament']:
            return await self._validate_ranking_output(output, context)
        else:
            # General validation for unknown types
            return await self._validate_general_output(output, agent_type, context)

    async def _validate_hypothesis(self, hypothesis: Hypothesis, context: str) -> float:
        """Validate a hypothesis output.

        Args:
            hypothesis: Generated hypothesis
            context: Generation context

        Returns:
            Confidence score for the hypothesis
        """
        confidence_factors = []

        # Factor 1: Completeness check
        completeness = self._check_hypothesis_completeness(hypothesis)
        confidence_factors.append(('completeness', completeness, 0.3))

        # Factor 2: Coherence check
        coherence = self._check_hypothesis_coherence(hypothesis)
        confidence_factors.append(('coherence', coherence, 0.25))

        # Factor 3: Novelty assessment
        novelty = self._assess_hypothesis_novelty(hypothesis)
        confidence_factors.append(('novelty', novelty, 0.2))

        # Factor 4: Context relevance
        relevance = self._check_context_relevance(hypothesis, context)
        confidence_factors.append(('relevance', relevance, 0.15))

        # Factor 5: Scientific validity
        validity = self._check_scientific_validity(hypothesis)
        confidence_factors.append(('validity', validity, 0.1))

        # Calculate weighted confidence
        total_confidence = sum(score * weight for _, score, weight in confidence_factors)

        logger.debug(f"Hypothesis validation: {dict((name, score) for name, score, _ in confidence_factors)}")

        return total_confidence

    async def _validate_review(self, review: Review, context: str) -> float:
        """Validate a review output.

        Args:
            review: Generated review
            context: Review context

        Returns:
            Confidence score for the review
        """
        confidence_factors = []

        # Factor 1: Review completeness
        completeness = self._check_review_completeness(review)
        confidence_factors.append(('completeness', completeness, 0.3))

        # Factor 2: Score consistency
        consistency = self._check_score_consistency(review)
        confidence_factors.append(('consistency', consistency, 0.25))

        # Factor 3: Feedback quality
        feedback_quality = self._assess_feedback_quality(review)
        confidence_factors.append(('feedback_quality', feedback_quality, 0.25))

        # Factor 4: Decision justification
        justification = self._check_decision_justification(review)
        confidence_factors.append(('justification', justification, 0.2))

        total_confidence = sum(score * weight for _, score, weight in confidence_factors)

        return total_confidence

    async def _validate_ranking_output(self, output: Any, context: str) -> float:
        """Validate ranking/tournament output.

        Args:
            output: Ranking output
            context: Ranking context

        Returns:
            Confidence score for the ranking
        """
        # Basic validation for ranking outputs
        if not output or not hasattr(output, '__len__'):
            return 0.1

        # Check if output has reasonable structure
        if hasattr(output, 'rankings') or isinstance(output, (list, dict)):
            return 0.8

        return 0.6

    async def _validate_general_output(self, output: Any, agent_type: str,
                                     context: str) -> float:
        """General validation for unknown output types.

        Args:
            output: Agent output
            agent_type: Type of agent
            context: Generation context

        Returns:
            Basic confidence score
        """
        # Basic checks for any output
        if output is None:
            return 0.0

        if not str(output).strip():
            return 0.1

        # Output has content - moderate confidence
        base_confidence = 0.6

        # Boost for structured outputs
        if hasattr(output, '__dict__') or isinstance(output, dict):
            base_confidence += 0.2

        return base_confidence

    def _check_hypothesis_completeness(self, hypothesis: Hypothesis) -> float:
        """Check if hypothesis has all required components.

        Args:
            hypothesis: Hypothesis to check

        Returns:
            Completeness score between 0.0 and 1.0
        """
        required_components = [
            (hypothesis.summary, "summary"),
            (hypothesis.full_description, "description"),
            (hypothesis.assumptions, "assumptions"),
            (hypothesis.experimental_protocol, "protocol"),
            (hypothesis.novelty_claim, "novelty_claim")
        ]

        present_components = 0
        for component, name in required_components:
            if component:
                if isinstance(component, list) and len(component) > 0:
                    present_components += 1
                elif isinstance(component, str) and len(component.strip()) > 10:
                    present_components += 1
                elif component is not None and not isinstance(component, (str, list)):
                    present_components += 1

        return present_components / len(required_components)

    def _check_hypothesis_coherence(self, hypothesis: Hypothesis) -> float:
        """Check internal coherence of hypothesis.

        Args:
            hypothesis: Hypothesis to check

        Returns:
            Coherence score between 0.0 and 1.0
        """
        coherence_score = 0.5  # Base coherence

        # Check if summary matches description
        if hypothesis.summary and hypothesis.full_description:
            summary_words = set(hypothesis.summary.lower().split())
            description_words = set(hypothesis.full_description.lower().split())
            overlap = len(summary_words & description_words)
            coherence_score += min(overlap / max(len(summary_words), 1) * 0.3, 0.3)

        # Check if assumptions align with description
        if hypothesis.assumptions and hypothesis.full_description:
            description_text = hypothesis.full_description.lower()
            assumption_alignment = 0
            for assumption in hypothesis.assumptions:
                if any(word in description_text for word in assumption.lower().split()[:3]):
                    assumption_alignment += 1

            if len(hypothesis.assumptions) > 0:
                coherence_score += (assumption_alignment / len(hypothesis.assumptions)) * 0.2

        return min(coherence_score, 1.0)

    def _assess_hypothesis_novelty(self, hypothesis: Hypothesis) -> float:
        """Assess novelty of hypothesis.

        Args:
            hypothesis: Hypothesis to assess

        Returns:
            Novelty score between 0.0 and 1.0
        """
        # Check for novelty indicators in the novelty claim
        if not hypothesis.novelty_claim:
            return 0.3

        novelty_indicators = [
            'novel', 'new', 'first', 'unprecedented', 'innovative',
            'breakthrough', 'pioneering', 'original', 'unique'
        ]

        novelty_claim_lower = hypothesis.novelty_claim.lower()
        indicator_count = sum(1 for indicator in novelty_indicators
                             if indicator in novelty_claim_lower)

        # Base novelty score
        novelty_score = min(0.5 + (indicator_count * 0.1), 0.9)

        # Check for specific novel mechanisms or approaches
        if any(phrase in novelty_claim_lower for phrase in
               ['new mechanism', 'novel approach', 'unprecedented method']):
            novelty_score += 0.1

        return min(novelty_score, 1.0)

    def _check_context_relevance(self, hypothesis: Hypothesis, context: str) -> float:
        """Check how well hypothesis addresses the context.

        Args:
            hypothesis: Generated hypothesis
            context: Original context/goal

        Returns:
            Relevance score between 0.0 and 1.0
        """
        if not context:
            return 0.8  # No context to check against

        context_words = set(context.lower().split())
        hypothesis_text = (hypothesis.summary + " " + hypothesis.full_description).lower()
        hypothesis_words = set(hypothesis_text.split())

        # Calculate word overlap
        overlap = len(context_words & hypothesis_words)
        relevance = overlap / max(len(context_words), 1)

        return min(relevance * 1.5, 1.0)  # Boost relevance score

    def _check_scientific_validity(self, hypothesis: Hypothesis) -> float:
        """Basic check for scientific validity indicators.

        Args:
            hypothesis: Hypothesis to check

        Returns:
            Validity score between 0.0 and 1.0
        """
        validity_score = 0.5  # Base validity

        # Check for testable claims
        testable_indicators = ['test', 'measure', 'observe', 'experiment', 'validate']
        protocol_text = str(hypothesis.experimental_protocol).lower()

        testable_count = sum(1 for indicator in testable_indicators
                            if indicator in protocol_text)
        validity_score += min(testable_count * 0.1, 0.3)

        # Check for measurable outcomes
        if hasattr(hypothesis.experimental_protocol, 'success_metrics'):
            if hypothesis.experimental_protocol.success_metrics:
                validity_score += 0.2

        return min(validity_score, 1.0)

    def _check_review_completeness(self, review: Review) -> float:
        """Check completeness of review output."""
        required_fields = ['decision', 'scores', 'narrative_feedback',
                          'key_strengths', 'key_weaknesses']

        present_count = 0
        for field in required_fields:
            if hasattr(review, field) and getattr(review, field):
                present_count += 1

        return present_count / len(required_fields)

    def _check_score_consistency(self, review: Review) -> float:
        """Check consistency of review scores."""
        if not hasattr(review, 'scores') or not review.scores:
            return 0.3

        scores = review.scores
        if hasattr(scores, 'average_score'):
            avg_score = scores.average_score()
            # Check if individual scores are reasonably consistent with average
            individual_scores = [
                getattr(scores, field, 0.5) for field in
                ['correctness', 'quality', 'novelty', 'safety', 'feasibility']
                if hasattr(scores, field)
            ]

            if individual_scores:
                variance = sum((score - avg_score) ** 2 for score in individual_scores) / len(individual_scores)
                consistency = max(0.3, 1.0 - variance)
                return consistency

        return 0.6

    def _assess_feedback_quality(self, review: Review) -> float:
        """Assess quality of narrative feedback."""
        if not hasattr(review, 'narrative_feedback') or not review.narrative_feedback:
            return 0.2

        feedback = review.narrative_feedback
        quality_score = 0.3  # Base quality

        # Check length (substantive feedback)
        if len(feedback) > 100:
            quality_score += 0.3

        # Check for specific feedback elements
        quality_indicators = ['because', 'however', 'therefore', 'specifically',
                             'evidence', 'suggests', 'indicates']
        indicator_count = sum(1 for indicator in quality_indicators
                             if indicator in feedback.lower())
        quality_score += min(indicator_count * 0.05, 0.4)

        return min(quality_score, 1.0)

    def _check_decision_justification(self, review: Review) -> float:
        """Check if review decision is well-justified."""
        if not hasattr(review, 'decision') or not review.decision:
            return 0.2

        # Check if narrative supports the decision
        if hasattr(review, 'narrative_feedback') and review.narrative_feedback:
            decision_str = str(review.decision).lower()
            feedback = review.narrative_feedback.lower()

            # Look for decision-supporting language
            if decision_str == 'accept' and any(word in feedback for word in
                                              ['accept', 'approve', 'good', 'strong']):
                return 0.9
            elif decision_str == 'reject' and any(word in feedback for word in
                                                 ['reject', 'weak', 'insufficient', 'poor']):
                return 0.9
            elif decision_str == 'revise' and any(word in feedback for word in
                                                 ['revise', 'improve', 'modify']):
                return 0.9

        return 0.6  # Moderate justification

    def _calculate_context_optimization_factor(self, original_size: int,
                                             optimized_size: int,
                                             base_confidence: float) -> float:
        """Calculate factor based on context optimization ratio.

        Args:
            original_size: Original context size
            optimized_size: Optimized context size
            base_confidence: Base confidence score

        Returns:
            Factor to apply to confidence score
        """
        if original_size <= 0 or optimized_size <= 0:
            return 1.0

        reduction_ratio = 1.0 - (optimized_size / original_size)

        # Less penalty for high base confidence
        if base_confidence >= 0.8:
            penalty_factor = 0.05  # Minimal penalty for high-confidence outputs
        elif base_confidence >= 0.6:
            penalty_factor = 0.1   # Moderate penalty
        else:
            penalty_factor = 0.2   # Higher penalty for low-confidence outputs

        # Calculate penalty based on reduction ratio
        penalty = reduction_ratio * penalty_factor

        # Factor should not go below 0.7 (max 30% penalty)
        factor = max(0.7, 1.0 - penalty)

        return factor

    def _generate_validation_notes(self, confidence_score: float,
                                 agent_type: str, should_fallback: bool) -> str:
        """Generate human-readable validation notes.

        Args:
            confidence_score: Calculated confidence score
            agent_type: Type of agent
            should_fallback: Whether fallback is recommended

        Returns:
            Validation notes string
        """
        notes = f"Confidence: {confidence_score:.2f} for {agent_type} agent output. "

        if should_fallback:
            notes += f"Below threshold ({self.confidence_threshold:.2f}), recommend fallback to full context."
        else:
            notes += "Confidence acceptable for optimized context."

        if confidence_score >= 0.9:
            notes += " High quality output detected."
        elif confidence_score <= 0.4:
            notes += " Low confidence - output may need review."

        return notes