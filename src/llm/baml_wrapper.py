"""BAML wrapper that integrates with the LLM abstraction layer.

This module provides a bridge between the BAML-generated clients and our
LLM abstraction layer, allowing agents to use BAML functions while maintaining
provider-agnostic behavior.
"""

import asyncio
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
import logging
from datetime import datetime

from baml_client.baml_client import b
from baml_client.baml_client.types import (
    AgentRequest,
    AgentResponse,
    AgentType,
    ComparisonResult,
    Hypothesis,
    ParsedResearchGoal,
    RequestType,
    ResearchPatterns,
    ResponseStatus,
    Review,
    ReviewType,
    SafetyCheck,
    SimilarityScore,
)

from .base import LLMProvider, LLMRequest, LLMResponse
from .capabilities import ModelCapabilities
from .baml_error_handler import BAMLErrorHandler

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BAMLWrapper:
    """Wrapper that integrates BAML functions with the LLM abstraction layer."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        """Initialize the BAML wrapper.

        Args:
            provider: Optional LLM provider to use. If not provided,
                     uses the default BAML configuration.
        """
        self.provider = provider
        self._client = b
        self.error_handler = BAMLErrorHandler()
        
    async def generate_hypothesis(
        self,
        goal: str,
        constraints: List[str],
        existing_hypotheses: List[Hypothesis],
        focus_area: Optional[str] = None,
        generation_method: str = "literature_based",
    ) -> Hypothesis:
        """Generate a new hypothesis using BAML.
        
        Args:
            goal: Research goal or objective
            constraints: Constraints to consider
            existing_hypotheses: Already generated hypotheses
            focus_area: Optional specific area to focus on
            generation_method: Method to use for generation
            
        Returns:
            Generated hypothesis
        """
        async def _generate():
            """Inner function for BAML call."""
            return await self._client.GenerateHypothesis(
                goal=goal,
                constraints=constraints,
                existing_hypotheses=existing_hypotheses,
                focus_area=focus_area,
                generation_method=generation_method,
            )

        try:
            # Use error handler for retry logic and fallback
            result = await self.error_handler.call_with_retry(
                _generate,
                client_name="ProductionClient",  # Default BAML client
                function_name="GenerateHypothesis"
            )

            logger.info(f"Generated hypothesis: {result.id}")
            return result

        except Exception as e:
            logger.error(f"Error generating hypothesis after retries: {e}")
            raise
            
    async def evaluate_hypothesis(
        self,
        hypothesis: Hypothesis,
        review_type: ReviewType,
        evaluation_criteria: List[str],
        context: Optional[Dict[str, str]] = None,
    ) -> Review:
        """Evaluate a hypothesis from different perspectives.
        
        Args:
            hypothesis: The hypothesis to evaluate
            review_type: Type of review to perform
            evaluation_criteria: Specific criteria to evaluate against
            context: Additional context for evaluation
            
        Returns:
            Review of the hypothesis
        """
        try:
            result = await self._client.EvaluateHypothesis(
                hypothesis=hypothesis,
                review_type=review_type,
                evaluation_criteria=evaluation_criteria,
                context=context or {},
            )
            
            logger.info(f"Evaluated hypothesis {hypothesis.id} with {review_type}")
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating hypothesis: {e}")
            raise
            
    async def perform_safety_check(
        self,
        target_type: str,
        target_content: str,
        trust_level: str,
        safety_criteria: List[str],
    ) -> SafetyCheck:
        """Perform safety check on hypothesis or task.
        
        Args:
            target_type: Type of item (hypothesis, task, or goal)
            target_content: Content to check for safety
            trust_level: Trust level (high, medium, or low)
            safety_criteria: Specific safety criteria to check
            
        Returns:
            Safety check result
        """
        try:
            result = await self._client.PerformSafetyCheck(
                target_type=target_type,
                target_content=target_content,
                trust_level=trust_level,
                safety_criteria=safety_criteria,
            )
            
            logger.info(f"Safety check completed: {result.safety_level}")
            return result
            
        except Exception as e:
            logger.error(f"Error performing safety check: {e}")
            raise
            
    async def compare_hypotheses(
        self,
        hypothesis1: Hypothesis,
        hypothesis2: Hypothesis,
        comparison_criteria: List[str],
        debate_context: Optional[str] = None,
    ) -> ComparisonResult:
        """Compare two hypotheses for ranking.
        
        Args:
            hypothesis1: First hypothesis
            hypothesis2: Second hypothesis
            comparison_criteria: Criteria for comparison
            debate_context: Optional context from ongoing debate
            
        Returns:
            Comparison result with winner and reasoning
        """
        try:
            result = await self._client.CompareHypotheses(
                hypothesis1=hypothesis1,
                hypothesis2=hypothesis2,
                comparison_criteria=comparison_criteria,
                debate_context=debate_context,
            )
            
            logger.info(f"Compared {hypothesis1.id} vs {hypothesis2.id}: winner={result.winner_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error comparing hypotheses: {e}")
            raise
            
    async def enhance_hypothesis(
        self,
        original_hypothesis: Hypothesis,
        enhancement_strategy: str,
        feedback: Optional[List[str]] = None,
        complementary_hypothesis: Optional[Hypothesis] = None,
    ) -> Hypothesis:
        """Enhance or evolve a hypothesis.
        
        Args:
            original_hypothesis: Hypothesis to enhance
            enhancement_strategy: Strategy (refine, combine, simplify, paradigm_shift)
            feedback: Optional feedback to incorporate
            complementary_hypothesis: For combination strategy
            
        Returns:
            Enhanced hypothesis
        """
        try:
            result = await self._client.EnhanceHypothesis(
                original_hypothesis=original_hypothesis,
                enhancement_strategy=enhancement_strategy,
                feedback=feedback,
                complementary_hypothesis=complementary_hypothesis,
            )
            
            logger.info(f"Enhanced hypothesis {original_hypothesis.id} using {enhancement_strategy}")
            return result
            
        except Exception as e:
            logger.error(f"Error enhancing hypothesis: {e}")
            raise
            
    async def calculate_similarity(
        self,
        hypothesis1: Hypothesis,
        hypothesis2: Hypothesis,
        similarity_aspects: List[str],
    ) -> SimilarityScore:
        """Calculate semantic similarity between hypotheses.
        
        Args:
            hypothesis1: First hypothesis
            hypothesis2: Second hypothesis
            similarity_aspects: Aspects to compare
            
        Returns:
            Similarity scores and analysis
        """
        try:
            result = await self._client.CalculateSimilarity(
                hypothesis1=hypothesis1,
                hypothesis2=hypothesis2,
                similarity_aspects=similarity_aspects,
            )
            
            logger.info(f"Calculated similarity: {result.overall_similarity}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            raise
            
    async def extract_research_patterns(
        self,
        hypotheses: List[Hypothesis],
        reviews: List[Review],
        focus: str,
    ) -> ResearchPatterns:
        """Extract patterns across multiple hypotheses and reviews.
        
        Args:
            hypotheses: All hypotheses to analyze
            reviews: All reviews to analyze
            focus: Focus area (methodology, assumptions, or themes)
            
        Returns:
            Identified patterns and recommendations
        """
        try:
            result = await self._client.ExtractResearchPatterns(
                hypotheses=hypotheses,
                reviews=reviews,
                focus=focus,
            )
            
            logger.info(f"Extracted {len(result.identified_patterns)} patterns")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting patterns: {e}")
            raise
            
    async def parse_research_goal(
        self,
        natural_language_goal: str,
        domain_context: Optional[str] = None,
    ) -> ParsedResearchGoal:
        """Parse natural language research goal into structured format.
        
        Args:
            natural_language_goal: User's research goal in natural language
            domain_context: Scientific domain if specified
            
        Returns:
            Parsed research goal with structured components
        """
        try:
            result = await self._client.ParseResearchGoal(
                natural_language_goal=natural_language_goal,
                domain_context=domain_context,
            )
            
            logger.info(f"Parsed research goal: {result.primary_objective}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing research goal: {e}")
            raise
            
    def convert_to_agent_request(
        self,
        agent_type: AgentType,
        request_type: RequestType,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AgentRequest:
        """Convert parameters to a standard AgentRequest.
        
        This is useful for agents that need to format their requests
        in the standard way expected by the LLM abstraction layer.
        
        Args:
            agent_type: Type of agent making the request
            request_type: Type of request being made
            prompt: Natural language instruction
            context: Additional context
            parameters: Request parameters
            
        Returns:
            Formatted AgentRequest
        """
        from baml_client.baml_client.types import AgentRequest, RequestContent
        
        return AgentRequest(
            request_id=f"{agent_type}_{datetime.now().timestamp()}",
            agent_type=agent_type,
            request_type=request_type,
            content=RequestContent(
                prompt=prompt,
                context={k: str(v) for k, v in (context or {}).items()},
                parameters={k: str(v) for k, v in (parameters or {}).items()},
            ),
        )