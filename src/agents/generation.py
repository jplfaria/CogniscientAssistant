"""Generation Agent - Creates novel hypotheses for scientific research.

The Generation Agent is responsible for creating innovative hypotheses using
multiple strategies including literature exploration, simulated debates,
assumption decomposition, and iterative refinement based on feedback.
"""

import asyncio
import logging
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from baml_client import b
from baml_client.types import Hypothesis as BamlHypothesis

from src.core.models import (
    Hypothesis,
    HypothesisCategory,
    Citation,
    ExperimentalProtocol,
    ResearchGoal,
    utcnow
)
from src.core.task_queue import TaskQueue
from src.core.context_memory import ContextMemory
from src.llm.base import LLMProvider
from src.core.safety import SafetyLevel

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
        
        logger.info(f"GenerationAgent initialized with strategies: {self.generation_strategies}")
    
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
            debate_turns = await self._simulate_debate(research_goal, num_turns=3)
            return await self.generate_from_debate(research_goal, debate_turns)
        
        elif generation_method == 'assumptions':
            assumptions = await self.identify_assumptions(research_goal)
            return await self.generate_from_assumptions(research_goal, assumptions)
        
        elif generation_method == 'expansion':
            feedback = await self._get_expansion_feedback()
            return await self.generate_from_feedback(research_goal, feedback)
        
        else:
            raise ValueError(f"Unimplemented generation method: {generation_method}")
    
    async def generate_from_literature(
        self,
        research_goal: ResearchGoal,
        literature: List[Dict[str, Any]]
    ) -> Hypothesis:
        """Generate hypothesis based on literature exploration.
        
        Args:
            research_goal: Research goal to address
            literature: Relevant literature articles
            
        Returns:
            Generated hypothesis grounded in literature
        """
        # Prepare context from literature
        literature_context = self._prepare_literature_context(literature)
        
        # Call BAML function to generate hypothesis
        try:
            baml_hypothesis = await b.GenerateHypothesis(
                goal=research_goal.description,
                constraints=research_goal.constraints,
                existing_hypotheses=[],  # Convert existing if needed
                focus_area=literature_context.get('focus_area'),
                generation_method='literature_based'
            )
            
            # Convert BAML hypothesis to our model
            hypothesis = self._convert_baml_hypothesis(baml_hypothesis)
            
            # Add literature citations
            hypothesis.supporting_evidence = self._extract_citations(literature)
            
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
        # For now, create a mock hypothesis
        # In full implementation, would use BAML to synthesize debate
        hypothesis = Hypothesis(
            id=uuid4(),
            summary=f"Hypothesis synthesized from {len(debate_turns)} debate perspectives",
            category=HypothesisCategory.MECHANISTIC,
            full_description=f"Based on debate about: {research_goal.description}",
            novelty_claim="Synthesized novel perspective from multiple viewpoints",
            assumptions=[turn['argument'][:50] + "..." for turn in debate_turns],
            experimental_protocol=self._create_mock_protocol(),
            supporting_evidence=[],
            confidence_score=0.75,
            generation_method='debate',
            created_at=utcnow()
        )
        
        await self._store_hypothesis(hypothesis)
        return hypothesis
    
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
        # Mock implementation
        hypothesis = Hypothesis(
            id=uuid4(),
            summary=f"Hypothesis addressing: {research_goal.description}",
            category=HypothesisCategory.MECHANISTIC,
            full_description="Hypothesis built from testable assumptions about density and molecular structure",
            novelty_claim="Novel integration of multiple testable components",
            assumptions=assumptions,
            experimental_protocol=self._create_mock_protocol(),
            supporting_evidence=[],
            confidence_score=0.8,
            generation_method='assumptions',
            created_at=utcnow()
        )
        
        await self._store_hypothesis(hypothesis)
        return hypothesis
    
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
        # Mock implementation incorporating feedback
        hypothesis = Hypothesis(
            id=uuid4(),
            summary=f"Expanded hypothesis with systems perspective",
            category=HypothesisCategory.MECHANISTIC,
            full_description="Hypothesis addressing protein networks and emergent system properties based on feedback",
            novelty_claim="Extends beyond single proteins to network-level understanding",
            assumptions=["Networks exhibit emergent properties", "System-level analysis reveals new targets"],
            experimental_protocol=self._create_mock_protocol(),
            supporting_evidence=[],
            confidence_score=0.85,
            generation_method='expansion',
            created_at=utcnow()
        )
        
        await self._store_hypothesis(hypothesis)
        return hypothesis
    
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
        """Search for relevant literature (mock implementation)."""
        return [
            {
                'title': 'Related research paper',
                'abstract': 'Abstract content...',
                'relevance': 0.9
            }
        ]
    
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
        """Prepare context from literature for generation."""
        if not literature:
            return {}
        
        # Extract key themes
        titles = [article.get('title', '') for article in literature]
        abstracts = [article.get('abstract', '') for article in literature]
        
        return {
            'focus_area': ' '.join(titles[:3]),  # Simplified
            'key_findings': ' '.join(abstracts[:2])
        }
    
    def _convert_baml_hypothesis(self, baml_hyp: BamlHypothesis) -> Hypothesis:
        """Convert BAML hypothesis to our model."""
        # This would do proper conversion - simplified for now
        return Hypothesis(
            id=uuid4(),
            summary=baml_hyp.summary,
            category=HypothesisCategory.MECHANISTIC,  # Would map properly
            full_description=baml_hyp.full_description,
            novelty_claim=baml_hyp.novelty_claim,
            assumptions=baml_hyp.assumptions,
            experimental_protocol=self._create_mock_protocol(),  # Would convert properly
            supporting_evidence=[],
            confidence_score=baml_hyp.confidence_score,
            generation_method=baml_hyp.generation_method,
            created_at=utcnow()
        )
    
    def _extract_citations(self, literature: List[Dict[str, Any]]) -> List[Citation]:
        """Extract citations from literature."""
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
    
    def _create_mock_protocol(self) -> ExperimentalProtocol:
        """Create mock experimental protocol."""
        return ExperimentalProtocol(
            objective="Test the hypothesis",
            methodology="Detailed experimental steps",
            required_resources=["Lab equipment", "Reagents"],
            timeline="6 months",
            success_metrics=["Measurable outcome 1", "Measurable outcome 2"],
            potential_challenges=["Challenge 1", "Challenge 2"],
            safety_considerations=["Safety protocol 1", "Safety protocol 2"]
        )
    
    async def _store_hypothesis(self, hypothesis: Hypothesis) -> None:
        """Store hypothesis in context memory."""
        # Get existing hypotheses
        existing = await self.context_memory.get('hypotheses') or []
        existing.append(hypothesis)
        
        # Store updated list
        await self.context_memory.set('hypotheses', existing)
        
        # Update generation statistics
        stats = await self.context_memory.get('generation_statistics') or {}
        stats['total_generated'] = stats.get('total_generated', 0) + 1
        stats[f'{hypothesis.generation_method}_count'] = \
            stats.get(f'{hypothesis.generation_method}_count', 0) + 1
        await self.context_memory.set('generation_statistics', stats)