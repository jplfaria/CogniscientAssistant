"""Generation Agent - Creates novel hypotheses for scientific research.

The Generation Agent is responsible for creating innovative hypotheses using
multiple strategies including literature exploration, simulated debates,
assumption decomposition, and iterative refinement based on feedback.
"""

import asyncio
import logging
import random
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4

from src.core.models import (
    Hypothesis,
    HypothesisCategory,
    Citation,
    ExperimentalProtocol,
    ResearchGoal,
    Paper,
    MemoryEntry,
    utcnow
)
from src.core.task_queue import TaskQueue
from src.core.context_memory import ContextMemory
from src.llm.base import LLMProvider
from src.llm.baml_wrapper import BAMLWrapper
from src.core.safety import SafetyLevel, SafetyLogger, SafetyConfig

# Context Optimization imports
from src.config.context_optimization_config import ContextOptimizationConfig
from src.utils.research_context import LiteratureRelevanceScorer
from src.utils.memory_optimization import MemoryContextOptimizer
from src.utils.agent_validation import AgentOutputValidator
from src.utils.context_optimization_runtime import AgentContextMetrics

logger = logging.getLogger(__name__)


class GenerationAgent:
    """Agent responsible for generating novel scientific hypotheses.
    
    Uses multiple generation strategies to create diverse, scientifically
    grounded hypotheses that address research goals while respecting constraints.
    """
    
    # Default generation strategies
    GENERATION_STRATEGIES = [
        'literature_based',
        'debate',
        'assumptions',
        'expansion'
    ]
    
    def __init__(
        self,
        task_queue: TaskQueue,
        context_memory: ContextMemory,
        llm_provider: LLMProvider,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize GenerationAgent with dependencies.
        
        Args:
            task_queue: Task queue for receiving generation tasks
            context_memory: Context memory for storing/retrieving hypotheses
            llm_provider: LLM provider for generation operations
            config: Optional configuration parameters
        """
        self.task_queue = task_queue
        self.context_memory = context_memory
        self.llm_provider = llm_provider
        
        # Configuration
        config = config or {}
        self.max_retries = config.get('max_retries', 3)
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
        self.generation_timeout = config.get('generation_timeout', 300)
        self.enable_caching = config.get('enable_caching', False)
        
        # Available generation strategies
        self.generation_strategies = config.get(
            'generation_strategies',
            self.GENERATION_STRATEGIES.copy()
        )
        
        # State tracking
        self._generation_count = 0
        self._strategy_success_rates = {
            strategy: 0.5 for strategy in self.generation_strategies
        }
        
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

        # Initialize context optimization components
        self.context_optimization_config = ContextOptimizationConfig.from_environment()
        self.literature_scorer = LiteratureRelevanceScorer()
        self.memory_optimizer = MemoryContextOptimizer()
        self.output_validator = AgentOutputValidator()
        self.context_metrics = AgentContextMetrics()

        logger.info(f"GenerationAgent initialized with strategies: {self.generation_strategies}")

        if self.context_optimization_config.optimization_enabled:
            logger.info("Context optimization enabled")
        else:
            logger.debug("Context optimization disabled")
    
    async def generate_hypothesis(
        self,
        research_goal: ResearchGoal,
        generation_method: str,
        focus_area: Optional[str] = None,
        existing_hypotheses: Optional[List[Hypothesis]] = None
    ) -> Hypothesis:
        """Generate a new hypothesis using the specified method.
        
        Args:
            research_goal: The research goal to address
            generation_method: Strategy to use for generation
            focus_area: Optional specific area to focus on
            existing_hypotheses: Previous hypotheses to avoid duplication
            
        Returns:
            Generated hypothesis
            
        Raises:
            ValueError: If generation method is invalid
            RuntimeError: If generation fails after retries
        """
        if generation_method not in self.generation_strategies:
            raise ValueError(f"Invalid generation method: {generation_method}")
        
        existing_hypotheses = existing_hypotheses or []
        
        # Route to appropriate generation method
        if generation_method == 'literature_based':
            # Mock literature for now - would integrate with web search
            literature = await self._search_literature(research_goal)
            return await self.generate_from_literature(research_goal, literature)
        
        elif generation_method == 'debate':
            # For real LLM usage, we'll let the LLM simulate the debate internally
            # by providing instructions in the context rather than mock turns
            debate_turns = []  # Empty turns will trigger internal debate simulation
            return await self.generate_from_debate(research_goal, debate_turns)
        
        elif generation_method == 'assumptions':
            # For real LLM usage, we'll let the LLM identify assumptions internally
            assumptions = []  # Empty assumptions will trigger internal generation
            return await self.generate_from_assumptions(research_goal, assumptions)
        
        elif generation_method == 'expansion':
            # For real LLM usage, we'll provide general expansion guidance
            feedback = {}  # Empty feedback will trigger expansion guidance
            return await self.generate_from_feedback(research_goal, feedback)
        
        else:
            raise ValueError(f"Unimplemented generation method: {generation_method}")
    
    async def generate_from_literature(
        self,
        research_goal: ResearchGoal,
        literature: Union[List[Paper], List[Dict[str, Any]]]
    ) -> Hypothesis:
        """Generate hypothesis based on literature exploration.

        Args:
            research_goal: Research goal to address
            literature: Relevant literature papers (Paper objects or dictionaries)

        Returns:
            Generated hypothesis grounded in literature
        """
        # Convert literature to Paper objects if needed (backward compatibility)
        paper_objects = self._ensure_paper_objects(literature)

        original_paper_count = len(paper_objects)
        optimized_literature = paper_objects
        literature_confidence = 1.0

        # Apply literature context optimization if enabled
        if (self.context_optimization_config.literature_optimization and
            len(paper_objects) > self.context_optimization_config.literature_max_papers):

            logger.debug(f"Applying literature optimization: {len(paper_objects)} papers -> "
                        f"max {self.context_optimization_config.literature_max_papers}")

            literature_selection = self.literature_scorer.select_relevant_papers(
                papers=paper_objects,
                research_context=research_goal.description,
                max_papers=self.context_optimization_config.literature_max_papers
            )

            if not literature_selection.fallback_needed:
                optimized_literature = literature_selection.papers
                literature_confidence = literature_selection.confidence_score

                logger.info(f"Literature optimized: {original_paper_count} -> "
                           f"{len(optimized_literature)} papers "
                           f"(confidence: {literature_confidence:.2f})")

                # Log optimization metrics
                self.context_metrics.log_literature_optimization(
                    agent_type='generation',
                    original_papers=original_paper_count,
                    optimized_papers=len(optimized_literature),
                    quality_score=literature_confidence
                )
            else:
                logger.warning(f"Literature optimization confidence too low "
                              f"({literature_confidence:.2f}), using full context")

        # Prepare context from literature
        literature_context = self._prepare_literature_context_from_papers(optimized_literature)

        # Call BAML function to generate hypothesis
        try:
            baml_hypothesis = await self.baml_wrapper.generate_hypothesis(
                goal=research_goal.description,
                constraints=research_goal.constraints,
                existing_hypotheses=[],  # Convert existing if needed
                focus_area=literature_context.get('focus_area'),
                generation_method='literature_based'
            )

            # Convert BAML hypothesis to our model
            hypothesis = self._convert_baml_hypothesis(baml_hypothesis)

            # Add literature citations from optimized papers
            hypothesis.supporting_evidence = self._extract_citations_from_papers(optimized_literature)

            # Validate output if optimization was used
            if (self.context_optimization_config.output_validation and
                len(optimized_literature) < original_paper_count):

                validation_result = await self.output_validator.validate_output(
                    agent_output=hypothesis,
                    agent_type='generation',
                    context=research_goal.description,
                    original_context_size=original_paper_count,
                    optimized_context_size=len(optimized_literature)
                )

                if validation_result.requires_fallback:
                    logger.warning(f"Output validation failed (confidence: "
                                  f"{validation_result.confidence:.2f}), "
                                  f"regenerating with full context")

                    # Fallback to full literature context
                    literature_context = self._prepare_literature_context_from_papers(literature)
                    baml_hypothesis = await self.baml_wrapper.generate_hypothesis(
                        goal=research_goal.description,
                        constraints=research_goal.constraints,
                        existing_hypotheses=[],
                        focus_area=literature_context.get('focus_area'),
                        generation_method='literature_based'
                    )
                    hypothesis = self._convert_baml_hypothesis(baml_hypothesis)
                    hypothesis.supporting_evidence = self._extract_citations_from_papers(literature)

                    # Log fallback usage
                    self.context_metrics.log_literature_optimization(
                        agent_type='generation',
                        original_papers=original_paper_count,
                        optimized_papers=original_paper_count,  # Full context used
                        quality_score=validation_result.confidence
                    )

            # Update generation count
            self._generation_count += 1

            # Store in context memory
            await self._store_hypothesis(hypothesis)

            return hypothesis

        except Exception as e:
            logger.error(f"Failed to generate hypothesis from literature: {e}")
            raise RuntimeError(f"Generation failed: {e}")
    
    async def generate_from_debate(
        self,
        research_goal: ResearchGoal,
        debate_turns: List[Dict[str, str]],
        num_perspectives: int = 3
    ) -> Hypothesis:
        """Generate hypothesis through simulated scientific debate.
        
        Args:
            research_goal: Research goal to address
            debate_turns: Simulated debate perspectives
            num_perspectives: Number of perspectives to consider
            
        Returns:
            Hypothesis synthesized from debate
        """
        # Prepare debate context from turns
        debate_context = self._prepare_debate_context(debate_turns)
        
        # Call BAML function to generate hypothesis
        try:
            baml_hypothesis = await self.baml_wrapper.generate_hypothesis(
                goal=research_goal.description,
                constraints=research_goal.constraints,
                existing_hypotheses=[],  # TODO: Get from context memory
                focus_area=debate_context,
                generation_method='debate'
            )
            
            # Convert BAML hypothesis to our model
            hypothesis = self._convert_baml_hypothesis(baml_hypothesis)
            
            # Update generation count
            self._generation_count += 1
            
            # Store in context memory
            await self._store_hypothesis(hypothesis)
            
            return hypothesis
            
        except Exception as e:
            logger.error(f"Failed to generate hypothesis from debate: {e}")
            raise RuntimeError(f"Generation failed: {e}")
    
    async def identify_assumptions(self, research_goal: ResearchGoal) -> List[str]:
        """Identify testable assumptions for the research goal.
        
        Args:
            research_goal: Goal to decompose into assumptions
            
        Returns:
            List of testable assumptions
        """
        # Mock implementation - would use BAML
        assumptions = [
            f"Testable hypothesis: Component A affects outcome",
            f"Testable hypothesis: Mechanism B is necessary",
            f"Testable hypothesis: Factor C modulates the system"
        ]
        return assumptions
    
    async def generate_from_assumptions(
        self,
        research_goal: ResearchGoal,
        assumptions: List[str]
    ) -> Hypothesis:
        """Generate hypothesis by aggregating testable assumptions.
        
        Args:
            research_goal: Research goal
            assumptions: List of testable assumptions
            
        Returns:
            Hypothesis built from assumptions
        """
        # Prepare assumptions context
        if not assumptions:
            # When no assumptions provided, instruct LLM to identify them
            assumptions_context = ("First identify key testable assumptions about the research goal, "
                                 "then build a hypothesis based on those assumptions. "
                                 "Focus on assumptions that can be experimentally validated.")
        else:
            assumptions_context = "Based on the following testable assumptions: " + "; ".join(assumptions)
        
        # Call BAML function to generate hypothesis
        try:
            baml_hypothesis = await self.baml_wrapper.generate_hypothesis(
                goal=research_goal.description,
                constraints=research_goal.constraints,
                existing_hypotheses=[],  # TODO: Get from context memory
                focus_area=assumptions_context,
                generation_method='assumptions'
            )
            
            # Convert BAML hypothesis to our model
            hypothesis = self._convert_baml_hypothesis(baml_hypothesis)
            
            # If no assumptions were provided, extract them from the generated hypothesis
            if not assumptions and hypothesis.assumptions:
                assumptions = hypothesis.assumptions
            elif assumptions:
                # Ensure the provided assumptions are preserved
                hypothesis.assumptions = assumptions
            
            # Update generation count
            self._generation_count += 1
            
            # Store in context memory
            await self._store_hypothesis(hypothesis)
            
            return hypothesis
            
        except Exception as e:
            logger.error(f"Failed to generate hypothesis from assumptions: {e}")
            raise RuntimeError(f"Generation failed: {e}")
    
    async def generate_from_feedback(
        self,
        research_goal: ResearchGoal,
        feedback: Dict[str, Any]
    ) -> Hypothesis:
        """Generate hypothesis based on meta-review feedback.
        
        Args:
            research_goal: Research goal
            feedback: Feedback from meta-review agent
            
        Returns:
            Hypothesis addressing feedback
        """
        # Prepare feedback context
        if not feedback:
            # When no feedback provided, instruct LLM to expand creatively
            feedback_context = ("Expand the hypothesis to consider: "
                              "1) Systems-level implications and emergent properties, "
                              "2) Cross-disciplinary connections and applications, "
                              "3) Long-term impacts and transformative potential. "
                              "Generate a comprehensive, expanded hypothesis.")
        else:
            feedback_points = []
            if 'strengths' in feedback:
                feedback_points.append(f"Strengths: {feedback['strengths']}")
            if 'weaknesses' in feedback:
                feedback_points.append(f"Areas to improve: {feedback['weaknesses']}")
            if 'suggestions' in feedback:
                feedback_points.append(f"Suggestions: {feedback['suggestions']}")
            
            feedback_context = "Based on the following feedback: " + "; ".join(feedback_points)
        
        # Call BAML function to generate hypothesis
        try:
            baml_hypothesis = await self.baml_wrapper.generate_hypothesis(
                goal=research_goal.description,
                constraints=research_goal.constraints,
                existing_hypotheses=[],  # TODO: Get from context memory
                focus_area=feedback_context,
                generation_method='expansion'  # Feedback-based is a form of expansion
            )
            
            # Convert BAML hypothesis to our model
            hypothesis = self._convert_baml_hypothesis(baml_hypothesis)
            
            # Update generation count
            self._generation_count += 1
            
            # Store in context memory
            await self._store_hypothesis(hypothesis)
            
            return hypothesis
            
        except Exception as e:
            logger.error(f"Failed to generate hypothesis from feedback: {e}")
            raise RuntimeError(f"Generation failed: {e}")
    
    async def calculate_creativity_metrics(
        self,
        hypotheses: List[Hypothesis]
    ) -> Dict[str, float]:
        """Calculate creativity metrics for generated hypotheses.
        
        Args:
            hypotheses: List of hypotheses to analyze
            
        Returns:
            Dictionary of creativity metrics
        """
        # Mock implementation
        return {
            'novelty_score': 0.75,
            'diversity_score': 0.82,
            'paradigm_shift_potential': 0.6
        }
    
    # Private helper methods
    
    async def _search_literature(self, research_goal: ResearchGoal) -> List[Dict[str, Any]]:
        """Search for relevant literature using web search if available.

        Returns literature as dictionaries for backward compatibility.
        """
        if self.web_search:
            # Use injected web search
            search_result = await self.web_search.search(
                query=research_goal.description,
                search_type='EXPLORATION',
                max_results=10
            )

            # Return articles directly as dictionaries for backward compatibility
            return search_result.get('articles', [])

        # Fallback to mock implementation with dictionaries for backward compatibility
        mock_papers = []
        for i in range(15):  # Create more papers to test optimization
            paper = {
                'title': f'Related research paper {i+1}: {research_goal.description}',
                'abstract': f'Abstract content for paper {i+1} discussing {research_goal.description}...',
                'authors': [f'Author{i+1}A', f'Author{i+1}B'],
                'journal': 'Nature Medicine' if i % 2 == 0 else 'Science',
                'year': 2024 - (i % 5),  # Vary years
                'doi': f'10.1234/test.2024.{i+1:03d}',
                'relevance_score': 0.9 - (i * 0.05),  # Decreasing relevance
                'methodology_type': 'experimental' if i % 3 == 0 else 'computational',
                'research_domain': 'biology'
            }
            mock_papers.append(paper)

        return mock_papers
    
    async def _simulate_debate(self, research_goal: ResearchGoal, num_turns: int) -> List[Dict[str, str]]:
        """Simulate scientific debate (mock implementation)."""
        perspectives = ['molecular_biologist', 'systems_biologist', 'computational_biologist']
        return [
            {
                'perspective': perspectives[i % len(perspectives)],
                'argument': f"Perspective {i+1} on {research_goal.description}"
            }
            for i in range(num_turns)
        ]
    
    async def _get_expansion_feedback(self) -> Dict[str, Any]:
        """Get feedback for expansion (mock implementation)."""
        return {
            'patterns': ['Focus on systems', 'Consider emergence'],
            'suggestions': ['Explore networks', 'Study interactions']
        }
    
    def _prepare_literature_context(self, literature: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare context from literature for generation (legacy method)."""
        if not literature:
            return {}

        # Extract key themes
        titles = [article.get('title', '') for article in literature]
        abstracts = [article.get('abstract', '') for article in literature]

        return {
            'focus_area': ' '.join(titles[:3]),  # Simplified
            'key_findings': ' '.join(abstracts[:2])
        }

    def _ensure_paper_objects(self, literature: Union[List[Paper], List[Dict[str, Any]]]) -> List[Paper]:
        """Convert literature to Paper objects if needed (backward compatibility).

        Args:
            literature: Literature as Paper objects or dictionaries

        Returns:
            List of Paper objects
        """
        if not literature:
            return []

        # Check if already Paper objects
        if isinstance(literature[0], Paper):
            return literature

        # Convert dictionaries to Paper objects
        paper_objects = []
        for item in literature:
            if isinstance(item, dict):
                paper = Paper(
                    title=item.get('title', ''),
                    abstract=item.get('abstract', ''),
                    authors=item.get('authors', []),
                    year=item.get('year'),
                    journal=item.get('journal', ''),
                    doi=item.get('doi', ''),
                    keywords=item.get('keywords', []),
                    methodology_type=item.get('methodology_type', ''),
                    research_domain=item.get('research_domain', ''),
                    relevance_score=item.get('relevance_score', 0.5)
                )
                paper_objects.append(paper)
            else:
                # Already a Paper object
                paper_objects.append(item)

        return paper_objects

    def _prepare_literature_context_from_papers(self, papers: List[Paper]) -> Dict[str, Any]:
        """Prepare context from Paper objects for generation."""
        if not papers:
            return {}

        # Extract key themes from Paper objects
        titles = [paper.title for paper in papers]
        abstracts = [paper.abstract for paper in papers if paper.abstract]

        # Extract methodology and domain information
        methodologies = [paper.methodology_type for paper in papers
                        if paper.methodology_type]
        domains = [paper.research_domain for paper in papers
                  if paper.research_domain]

        # Build comprehensive context
        context = {
            'focus_area': ' '.join(titles[:3]),  # Top 3 most relevant titles
            'key_findings': ' '.join(abstracts[:2]) if abstracts else '',
            'methodologies': list(set(methodologies)) if methodologies else [],
            'research_domains': list(set(domains)) if domains else [],
            'paper_count': len(papers),
            'high_relevance_papers': len([p for p in papers if p.relevance_score > 0.7])
        }

        return context
    
    def _prepare_debate_context(self, debate_turns: List[Dict[str, str]]) -> str:
        """Prepare context from debate turns for generation."""
        if not debate_turns:
            # When no debate turns provided, instruct LLM to simulate debate
            return ("Consider this hypothesis from multiple scientific perspectives: "
                    "1) A molecular biologist focusing on mechanisms, "
                    "2) A systems biologist considering emergent properties, "
                    "3) A computational biologist analyzing patterns. "
                    "Synthesize these diverse viewpoints into a comprehensive hypothesis.")
        
        # Combine debate perspectives into a coherent context
        debate_summary = []
        for i, turn in enumerate(debate_turns):
            perspective = turn.get('perspective', f'Perspective {i+1}')
            argument = turn.get('argument', '')
            debate_summary.append(f"{perspective}: {argument}")
        
        return " | ".join(debate_summary)
    
    def _convert_baml_hypothesis(self, baml_hyp) -> Hypothesis:
        """Convert BAML hypothesis to our model."""
        # Map category string to enum
        category_map = {
            'mechanistic': HypothesisCategory.MECHANISTIC,
            'therapeutic': HypothesisCategory.THERAPEUTIC,
            'diagnostic': HypothesisCategory.DIAGNOSTIC,
            'biomarker': HypothesisCategory.BIOMARKER,
            'methodology': HypothesisCategory.METHODOLOGY,
            'other': HypothesisCategory.OTHER
        }
        category = category_map.get(baml_hyp.category.lower(), HypothesisCategory.MECHANISTIC)
        
        # Convert experimental protocol if present
        protocol = None
        if hasattr(baml_hyp, 'experimental_protocol') and baml_hyp.experimental_protocol:
            exp_proto = baml_hyp.experimental_protocol
            
            # Handle field name variations from LLM responses
            success_metrics = getattr(exp_proto, 'success_metrics', 
                                    getattr(exp_proto, 'expected_outcomes', []))
            potential_challenges = getattr(exp_proto, 'potential_challenges', [])
            safety_considerations = getattr(exp_proto, 'safety_considerations', [])
            
            # Ensure we have at least one item for required lists
            if not success_metrics:
                success_metrics = ["Successful completion of experiment"]
            if not potential_challenges:
                potential_challenges = ["Standard experimental variability"]
            if not safety_considerations:
                safety_considerations = ["Standard laboratory safety protocols"]
            
            protocol = ExperimentalProtocol(
                objective=exp_proto.objective,
                methodology=exp_proto.methodology,
                required_resources=exp_proto.required_resources,
                timeline=exp_proto.timeline,
                success_metrics=success_metrics,
                potential_challenges=potential_challenges,
                safety_considerations=safety_considerations
            )
        else:
            protocol = self._create_mock_protocol()
        
        return Hypothesis(
            id=uuid4(),  # Generate our own ID
            summary=baml_hyp.summary,
            category=category,
            full_description=baml_hyp.full_description,
            novelty_claim=baml_hyp.novelty_claim,
            assumptions=baml_hyp.assumptions,
            experimental_protocol=protocol,
            supporting_evidence=[],  # Will be added separately
            confidence_score=baml_hyp.confidence_score,
            generation_method=baml_hyp.generation_method,
            created_at=utcnow()
        )
    
    def _extract_citations(self, literature: List[Dict[str, Any]]) -> List[Citation]:
        """Extract citations from literature (legacy method)."""
        citations = []
        for article in literature:
            if 'doi' in article:
                citation = Citation(
                    authors=["Author1", "Author2"],  # Would parse properly
                    title=article.get('title', 'Unknown'),
                    journal=article.get('journal'),
                    year=2024,  # Would parse properly
                    doi=article.get('doi')
                )
                citations.append(citation)
        return citations

    def _extract_citations_from_papers(self, papers: List[Paper]) -> List[Citation]:
        """Extract citations from Paper objects."""
        citations = []
        for paper in papers:
            # Use the Paper's built-in citation conversion method
            citation = paper.get_citation()
            citations.append(citation)
        return citations
    
    def _create_mock_protocol(self) -> ExperimentalProtocol:
        """Create mock experimental protocol."""
        return ExperimentalProtocol(
            objective="Test the hypothesis",
            methodology="Detailed experimental steps",
            required_resources=["Lab equipment", "Reagents"],
            timeline="6 months",
            success_metrics=["Measurable outcome 1", "Measurable outcome 2", "Analysis of treatment effectiveness"],
            potential_challenges=["Challenge 1", "Challenge 2"],
            safety_considerations=["Safety protocol 1", "Safety protocol 2"]
        )
    
    async def _store_hypothesis(self, hypothesis: Hypothesis) -> None:
        """Store hypothesis in context memory and log for safety."""
        # Get existing hypotheses
        existing = await self.context_memory.get('hypotheses') or []
        
        # Convert hypothesis to serializable dict
        hypothesis_dict = {
            'id': str(hypothesis.id),
            'summary': hypothesis.summary,
            'full_description': hypothesis.full_description,
            'category': hypothesis.category.value,
            'assumptions': hypothesis.assumptions,
            'novelty_claim': hypothesis.novelty_claim,
            'supporting_evidence': hypothesis.supporting_evidence,
            'generation_method': hypothesis.generation_method,
            'confidence_score': hypothesis.confidence_score,
            'experimental_protocol': {
                'objective': hypothesis.experimental_protocol.objective,
                'methodology': hypothesis.experimental_protocol.methodology,
                'success_metrics': hypothesis.experimental_protocol.success_metrics,
                'required_resources': hypothesis.experimental_protocol.required_resources,
                'timeline': hypothesis.experimental_protocol.timeline,
                'potential_challenges': hypothesis.experimental_protocol.potential_challenges,
                'safety_considerations': hypothesis.experimental_protocol.safety_considerations
            },
            'created_at': hypothesis.created_at.isoformat(),
            'elo_rating': hypothesis.elo_rating,
            'review_count': hypothesis.review_count,
            'evolution_count': hypothesis.evolution_count
        }
        
        existing.append(hypothesis_dict)
        
        # Store updated list
        await self.context_memory.set('hypotheses', existing)
        
        # Update generation statistics
        stats = await self.context_memory.get('generation_statistics') or {}
        stats['total_generated'] = stats.get('total_generated', 0) + 1
        stats[f'{hypothesis.generation_method}_count'] = \
            stats.get(f'{hypothesis.generation_method}_count', 0) + 1
        await self.context_memory.set('generation_statistics', stats)
        
        # Log hypothesis for safety monitoring if enabled
        if self.safety_logger:
            await self.safety_logger.log_hypothesis({
                'hypothesis_id': str(hypothesis.id),
                'summary': hypothesis.summary,
                'category': hypothesis.category.value,
                'generation_method': hypothesis.generation_method,
                'confidence_score': hypothesis.confidence_score,
                'num_assumptions': len(hypothesis.assumptions),
                'has_citations': len(hypothesis.supporting_evidence) > 0
            })