"""Memory Context Optimizer for context optimization.

This module implements intelligent memory context filtering to select the most
relevant memory entries for agent operations, reducing context size while
maintaining decision-making capability.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from src.core.models import MemoryEntry, utcnow

logger = logging.getLogger(__name__)


class MemoryContextOptimizer:
    """Optimizes memory context for agent operations."""

    def __init__(self, relevance_threshold: float = 0.4):
        """Initialize the memory context optimizer.

        Args:
            relevance_threshold: Minimum relevance score for including memory entries
        """
        self.relevance_threshold = relevance_threshold

        # Weight factors for different memory types
        self.type_weights = {
            'hypothesis': 1.5,      # Hypotheses are very relevant
            'task': 1.2,           # Task results are important
            'result': 1.3,         # Results are highly relevant
            'feedback': 1.4,       # Feedback is very valuable
            'error': 1.1,          # Errors provide learning context
            'decision': 1.3,       # Previous decisions are important
            'observation': 1.0,    # Observations are baseline relevant
            'meta_review': 1.6,    # Meta-reviews are extremely relevant
            'default': 1.0         # Default weight for unknown types
        }

        # Recency decay factors (how much to weight recent vs old entries)
        self.recency_decay = {
            'critical': 0.1,    # Critical entries decay slowly
            'high': 0.2,        # High priority entries
            'medium': 0.5,      # Medium priority entries
            'low': 0.8          # Low priority entries decay quickly
        }

    def select_relevant_memories(self, available_memories: List[MemoryEntry],
                                current_context: str,
                                agent_type: str,
                                max_memories: int = 10) -> List[MemoryEntry]:
        """Select most relevant memory entries for current operation.

        Args:
            available_memories: All available memory entries
            current_context: Current operation context/goal
            agent_type: Type of agent requesting memory
            max_memories: Maximum number of memory entries to return

        Returns:
            List of most relevant memory entries
        """
        if not available_memories:
            logger.debug("No memories available for optimization")
            return []

        if len(available_memories) <= max_memories:
            logger.debug(f"All {len(available_memories)} memories included (below max limit)")
            return available_memories

        # Score all memories for relevance
        scored_memories = []
        for memory in available_memories:
            score = self._score_memory_relevance(memory, current_context, agent_type)
            if score >= self.relevance_threshold:
                scored_memories.append((memory, score))
                logger.debug(f"Memory {memory.id} scored {score:.3f} for agent {agent_type}")

        # Sort by relevance and return top entries
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        selected_memories = [memory for memory, score in scored_memories[:max_memories]]

        logger.info(f"Selected {len(selected_memories)} memories from {len(available_memories)} "
                   f"available (threshold: {self.relevance_threshold})")

        return selected_memories

    def _score_memory_relevance(self, memory: MemoryEntry, current_context: str,
                               agent_type: str) -> float:
        """Score a single memory entry for relevance.

        Args:
            memory: Memory entry to score
            current_context: Current operation context
            agent_type: Type of agent requesting memory

        Returns:
            Relevance score between 0.0 and 1.0
        """
        # Start with base relevance from memory's built-in method
        base_score = memory.matches_context(current_context, agent_type)

        # Apply type-specific weights
        type_weight = self.type_weights.get(memory.entry_type.lower(),
                                           self.type_weights['default'])
        weighted_score = base_score * type_weight

        # Apply recency weighting
        recency_factor = self._calculate_recency_factor(memory)
        time_weighted_score = weighted_score * recency_factor

        # Apply agent-specific bonuses
        agent_bonus = self._calculate_agent_bonus(memory, agent_type)
        final_score = time_weighted_score * agent_bonus

        # Apply task continuity bonus
        if self._is_task_continuation(memory, current_context):
            final_score *= 1.3

        # Ensure score is within bounds
        return min(final_score, 1.0)

    def _calculate_recency_factor(self, memory: MemoryEntry) -> float:
        """Calculate recency factor for memory weighting.

        Args:
            memory: Memory entry to analyze

        Returns:
            Recency factor between 0.1 and 1.0
        """
        now = utcnow()
        age_hours = (now - memory.timestamp).total_seconds() / 3600

        # Determine memory priority from content or tags
        priority = self._determine_memory_priority(memory)

        # Get decay rate for this priority
        decay_rate = self.recency_decay.get(priority, self.recency_decay['medium'])

        # Calculate exponential decay
        recency_factor = max(0.1, 1.0 - (age_hours * decay_rate / 24))

        # Recent memories within 6 hours get full weight
        if age_hours <= 6:
            recency_factor = max(recency_factor, 0.9)

        return recency_factor

    def _determine_memory_priority(self, memory: MemoryEntry) -> str:
        """Determine the priority level of a memory entry.

        Args:
            memory: Memory entry to analyze

        Returns:
            Priority level: 'critical', 'high', 'medium', or 'low'
        """
        # Check tags for priority indicators
        if 'critical' in memory.tags or 'urgent' in memory.tags:
            return 'critical'

        # High priority for certain entry types
        if memory.entry_type.lower() in ['meta_review', 'feedback', 'hypothesis']:
            return 'high'

        # Check content for priority indicators
        content_str = str(memory.content).lower()
        if any(word in content_str for word in ['error', 'fail', 'critical', 'important']):
            return 'high'

        # Medium priority for most operational entries
        if memory.entry_type.lower() in ['task', 'result', 'decision']:
            return 'medium'

        # Default to low priority
        return 'low'

    def _calculate_agent_bonus(self, memory: MemoryEntry, agent_type: str) -> float:
        """Calculate bonus factor for agent-specific relevance.

        Args:
            memory: Memory entry to analyze
            agent_type: Type of agent requesting memory

        Returns:
            Bonus factor between 1.0 and 1.5
        """
        bonus = 1.0

        # Bonus for memories created by the same agent type
        if memory.agent_id and agent_type.lower() in memory.agent_id.lower():
            bonus += 0.3

        # Bonus for memories tagged with agent type
        if any(agent_type.lower() in tag.lower() for tag in memory.tags):
            bonus += 0.2

        # Cross-agent relevance bonuses
        agent_affinities = {
            'generation': ['hypothesis', 'literature', 'creativity'],
            'reflection': ['review', 'critique', 'analysis'],
            'ranking': ['comparison', 'evaluation', 'tournament'],
            'evolution': ['improvement', 'refinement', 'iteration'],
            'proximity': ['similarity', 'clustering', 'grouping'],
            'meta_review': ['synthesis', 'overview', 'summary']
        }

        agent_keywords = agent_affinities.get(agent_type.lower(), [])
        content_str = str(memory.content).lower()

        for keyword in agent_keywords:
            if keyword in content_str:
                bonus += 0.1
                break

        return min(bonus, 1.5)

    def _is_task_continuation(self, memory: MemoryEntry, current_context: str) -> bool:
        """Check if memory is part of current task continuation.

        Args:
            memory: Memory entry to check
            current_context: Current operation context

        Returns:
            True if memory appears to be part of current task flow
        """
        # Check if task IDs match (simple heuristic)
        if memory.task_id and any(memory.task_id in part
                                 for part in current_context.split()):
            return True

        # Check for iteration continuity
        if memory.iteration_number is not None:
            # Recent iteration (within 2 iterations) gets continuation bonus
            if hasattr(self, 'current_iteration'):
                iteration_gap = abs(self.current_iteration - memory.iteration_number)
                return iteration_gap <= 2

        # Check for research phase continuity
        if memory.research_phase and memory.research_phase in current_context:
            return True

        return False

    def optimize_for_agent_type(self, available_memories: List[MemoryEntry],
                               agent_type: str,
                               max_memories: int = 10) -> List[MemoryEntry]:
        """Optimize memory selection for specific agent type.

        This method provides agent-specific optimization strategies beyond
        the general relevance scoring.

        Args:
            available_memories: All available memory entries
            agent_type: Type of agent requesting memory
            max_memories: Maximum number of memories to return

        Returns:
            Optimized memory selection for the agent type
        """
        if agent_type.lower() == 'generation':
            # Generation agents benefit from hypothesis and literature memories
            return self._optimize_for_generation(available_memories, max_memories)

        elif agent_type.lower() == 'reflection':
            # Reflection agents benefit from reviews and critiques
            return self._optimize_for_reflection(available_memories, max_memories)

        elif agent_type.lower() == 'ranking':
            # Ranking agents benefit from comparison and evaluation memories
            return self._optimize_for_ranking(available_memories, max_memories)

        else:
            # Use general optimization for other agent types
            return self.select_relevant_memories(
                available_memories, f"{agent_type} operation", agent_type, max_memories
            )

    def _optimize_for_generation(self, memories: List[MemoryEntry],
                                max_memories: int) -> List[MemoryEntry]:
        """Optimize memory selection for generation agents."""
        # Prioritize hypothesis and literature-related memories
        preferred_types = ['hypothesis', 'literature', 'result', 'feedback']

        # Separate preferred and other memories
        preferred = [m for m in memories if m.entry_type.lower() in preferred_types]
        others = [m for m in memories if m.entry_type.lower() not in preferred_types]

        # Take most recent preferred memories plus some others
        preferred_count = min(len(preferred), int(max_memories * 0.7))
        other_count = max_memories - preferred_count

        selected = preferred[:preferred_count] + others[:other_count]
        return selected[:max_memories]

    def _optimize_for_reflection(self, memories: List[MemoryEntry],
                                max_memories: int) -> List[MemoryEntry]:
        """Optimize memory selection for reflection agents."""
        # Prioritize review and analysis-related memories
        preferred_types = ['hypothesis', 'review', 'feedback', 'critique']

        preferred = [m for m in memories if m.entry_type.lower() in preferred_types]
        others = [m for m in memories if m.entry_type.lower() not in preferred_types]

        preferred_count = min(len(preferred), int(max_memories * 0.8))
        other_count = max_memories - preferred_count

        selected = preferred[:preferred_count] + others[:other_count]
        return selected[:max_memories]

    def _optimize_for_ranking(self, memories: List[MemoryEntry],
                             max_memories: int) -> List[MemoryEntry]:
        """Optimize memory selection for ranking agents."""
        # Prioritize comparison and evaluation memories
        preferred_types = ['hypothesis', 'result', 'comparison', 'evaluation']

        preferred = [m for m in memories if m.entry_type.lower() in preferred_types]
        others = [m for m in memories if m.entry_type.lower() not in preferred_types]

        preferred_count = min(len(preferred), int(max_memories * 0.6))
        other_count = max_memories - preferred_count

        selected = preferred[:preferred_count] + others[:other_count]
        return selected[:max_memories]