"""Supervisor Agent - Central orchestrator of the AI Co-Scientist system."""
import asyncio
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import logging

from src.core.models import Task, TaskState, TaskType, utcnow
from src.core.task_queue import TaskQueue
from src.core.context_memory import ContextMemory
from src.llm.base import LLMProvider

logger = logging.getLogger(__name__)


@dataclass
class ResourceAllocation:
    """Resource allocation for a task."""
    task_id: str
    compute_budget: float
    memory_mb: int
    timeout_seconds: int
    allocated_at: datetime = field(default_factory=utcnow)


class SupervisorAgent:
    """Central orchestrator managing task distribution, resource allocation, and strategic coordination."""
    
    # Default agent weights for weighted random selection
    DEFAULT_WEIGHTS = {
        'generation': 0.3,
        'reflection': 0.2,
        'ranking': 0.15,
        'evolution': 0.15,
        'proximity': 0.1,
        'meta_review': 0.1
    }
    
    # Agent type to TaskType mapping
    AGENT_TYPE_MAP = {
        'generation': TaskType.GENERATE_HYPOTHESIS,
        'reflection': TaskType.REFLECT_ON_HYPOTHESIS,
        'ranking': TaskType.RANK_HYPOTHESES,
        'evolution': TaskType.EVOLVE_HYPOTHESIS,
        'proximity': TaskType.FIND_SIMILAR_HYPOTHESES,
        'meta_review': TaskType.META_REVIEW
    }
    
    def __init__(
        self,
        task_queue: TaskQueue,
        context_memory: ContextMemory,
        llm_provider: LLMProvider,
        agent_weights: Optional[Dict[str, float]] = None,
        resource_config: Optional[Dict[str, Any]] = None
    ):
        """Initialize SupervisorAgent with dependencies.
        
        Args:
            task_queue: Task queue for managing work distribution
            context_memory: Context memory for state persistence
            llm_provider: LLM provider for AI operations
            agent_weights: Optional custom agent selection weights
            resource_config: Optional resource allocation configuration
        """
        self.task_queue = task_queue
        self.context_memory = context_memory
        self.llm_provider = llm_provider
        
        # Agent selection weights
        if agent_weights:
            self._validate_weights(agent_weights)
            self.agent_weights = agent_weights
        else:
            self.agent_weights = self.DEFAULT_WEIGHTS.copy()
        
        # Resource configuration
        self.resource_config = resource_config or {
            'max_workers': 8,
            'memory_budget_mb': 4096,
            'compute_budget': 1000.0,
            'time_limit_hours': 24
        }
        
        # State tracking
        self.is_running = False
        self.termination_probability = 0.0
        self.resource_consumed = 0.0
        self.active_allocations: Dict[str, ResourceAllocation] = {}
        self.agent_effectiveness: Dict[str, float] = {
            agent: 0.5 for agent in self.agent_weights
        }
        
        # Performance tracking
        self._start_time = None
        self._task_history: List[Dict[str, Any]] = []
        self._checkpoint_interval = timedelta(minutes=5)
        self._last_checkpoint = None
    
    def _validate_weights(self, weights: Dict[str, float]) -> None:
        """Validate agent weights sum to 1.0."""
        total = sum(weights.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Agent weights must sum to 1.0, got {total}")
    
    async def create_task(
        self,
        agent_type: str,
        priority: int,
        parameters: Dict[str, Any]
    ) -> Task:
        """Create and enqueue a new task.
        
        Args:
            agent_type: Type of agent to execute task
            priority: Task priority
            parameters: Task-specific parameters
            timeout: Optional timeout in seconds
            dependencies: Optional list of dependency task IDs
            
        Returns:
            Created task
        """
        # Validate agent type
        if agent_type not in self.AGENT_TYPE_MAP:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Store timeout and dependencies in payload if needed
        if 'timeout' in parameters or 'dependencies' in parameters:
            # These can be handled by the task executor
            pass
        
        # Create task
        task_type = self.AGENT_TYPE_MAP[agent_type]
        task = Task(
            id=uuid.uuid4(),
            task_type=task_type,
            priority=priority,
            payload=parameters,
            state=TaskState.PENDING,
            created_at=utcnow()
        )
        
        # Enqueue task
        await self.task_queue.enqueue(task)
        
        logger.info(f"Created task {task.id} for {agent_type} agent")
        return task
    
    async def select_next_agent(self) -> str:
        """Select next agent to activate using weighted random sampling.
        
        Returns:
            Selected agent type
        """
        # Get current system state
        system_state = await self._get_system_state()
        
        # Adjust weights based on system state (can be enhanced)
        adjusted_weights = self.agent_weights.copy()
        
        # Weighted random selection
        agents = list(adjusted_weights.keys())
        weights = list(adjusted_weights.values())
        
        selected = random.choices(agents, weights=weights, k=1)[0]
        
        logger.debug(f"Selected {selected} agent based on weights: {adjusted_weights}")
        return selected
    
    async def distribute_tasks(self, batch_size: int = 5) -> List[Task]:
        """Distribute tasks to agents based on system state.
        
        Args:
            batch_size: Number of tasks to create
            
        Returns:
            List of created tasks
        """
        tasks = []
        system_state = await self._get_system_state()
        
        for _ in range(batch_size):
            # Select agent type
            agent_type = await self.select_next_agent()
            
            # Determine task parameters based on agent type and system state
            parameters = await self._generate_task_parameters(agent_type, system_state)
            
            # Create task
            task = await self.create_task(
                agent_type=agent_type,
                priority=2,  # Medium priority
                parameters=parameters
            )
            tasks.append(task)
        
        return tasks
    
    async def allocate_resources(
        self,
        agent_type: str,
        task_complexity: str = 'normal'
    ) -> Dict[str, Any]:
        """Allocate resources for a task.
        
        Args:
            agent_type: Type of agent requesting resources
            task_complexity: Task complexity (low, normal, high)
            
        Returns:
            Resource allocation details
        """
        # Check available resources
        available_compute = self.resource_config['compute_budget'] - self.resource_consumed
        
        if available_compute < 10.0:  # Minimum allocation
            raise RuntimeError("Insufficient resources available")
        
        # Determine allocation based on agent type and complexity
        complexity_multiplier = {'low': 0.5, 'normal': 1.0, 'high': 2.0}[task_complexity]
        
        base_allocations = {
            'generation': {'compute': 30.0, 'memory_mb': 256, 'timeout': 300},
            'reflection': {'compute': 20.0, 'memory_mb': 128, 'timeout': 180},
            'ranking': {'compute': 15.0, 'memory_mb': 128, 'timeout': 120},
            'evolution': {'compute': 25.0, 'memory_mb': 256, 'timeout': 240},
            'proximity': {'compute': 10.0, 'memory_mb': 256, 'timeout': 120},
            'meta_review': {'compute': 40.0, 'memory_mb': 512, 'timeout': 600}
        }
        
        base = base_allocations.get(agent_type, base_allocations['generation'])
        
        # Adjust for system load
        system_state = await self._get_system_state()
        load_factor = 1.0
        utilization = system_state.get('resource_utilization', 0)
        if utilization > 0.8:
            load_factor = 0.5  # Reduce allocation under high load
        
        allocation = {
            'compute_budget': min(base['compute'] * complexity_multiplier * load_factor, available_compute),
            'memory_mb': int(base['memory_mb'] * complexity_multiplier),
            'timeout_seconds': int(base['timeout'] * complexity_multiplier)
        }
        
        return allocation
    
    async def reclaim_resources(self, task_id: str) -> None:
        """Reclaim resources from completed or failed task.
        
        Args:
            task_id: ID of task to reclaim resources from
        """
        if task_id in self.active_allocations:
            allocation = self.active_allocations[task_id]
            if isinstance(allocation, ResourceAllocation):
                self.resource_consumed -= allocation.compute_budget
                logger.info(f"Reclaimed {allocation.compute_budget} compute units from task {task_id}")
            elif isinstance(allocation, dict):
                self.resource_consumed -= allocation.get('compute_budget', 0)
                logger.info(f"Reclaimed {allocation.get('compute_budget', 0)} compute units from task {task_id}")
            del self.active_allocations[task_id]
    
    async def calculate_system_metrics(self) -> Dict[str, Any]:
        """Calculate current system metrics.
        
        Returns:
            Dictionary of system metrics
        """
        # Get task queue statistics
        queue_stats = await self.task_queue.get_queue_statistics()
        
        # Get hypothesis and review counts
        hypotheses = await self.context_memory.get('hypotheses') or []
        reviews = await self.context_memory.get('reviews') or []
        tournament_data = await self.context_memory.get('tournament_results') or {}
        
        # Calculate metrics
        # Extract task counts from queue stats
        task_states = queue_stats.get('task_states', {})
        total_completed = task_states.get('completed', 0)
        total_failed = task_states.get('failed', 0)
        total_tasks = total_completed + total_failed
        completion_rate = total_completed / total_tasks if total_tasks > 0 else 0
        
        metrics = {
            'hypothesis_count': len(hypotheses),
            'review_count': len(reviews),
            'tournament_progress': tournament_data.get('progress', 0.0),
            'task_completion_rate': completion_rate,
            'resource_utilization': self.resource_consumed / self.resource_config['compute_budget'],
            'active_tasks': task_states.get('executing', 0),
            'pending_tasks': task_states.get('pending', 0),
            'agent_effectiveness': self.agent_effectiveness.copy()
        }
        
        return metrics
    
    async def check_termination_conditions(self) -> bool:
        """Check if termination conditions are met.
        
        Returns:
            True if should terminate, False otherwise
        """
        system_state = await self._get_system_state()
        
        # Check various termination conditions
        conditions = {
            'goal_achieved': system_state.get('research_goal_achieved', False),
            'resource_exhausted': self.resource_consumed >= self.resource_config['compute_budget'] * 0.95,
            'time_limit': self._check_time_limit() if self._start_time else False,
            'quality_threshold': system_state.get('high_quality_hypotheses', 0) >= 10,
            'convergence': system_state.get('no_improvement_iterations', 0) >= 5
        }
        
        # Update termination probability
        met_conditions = sum(1 for v in conditions.values() if v)
        self.termination_probability = met_conditions / len(conditions)
        
        # Terminate if any critical condition is met
        should_terminate = any([
            conditions['goal_achieved'],
            conditions['resource_exhausted'],
            conditions['time_limit']
        ])
        
        if should_terminate:
            logger.info(f"Termination conditions met: {conditions}")
        
        return should_terminate
    
    async def update_agent_effectiveness(self) -> None:
        """Update agent effectiveness based on recent results."""
        # Get recent task results
        recent_results = await self.context_memory.get('recent_task_results') or []
        
        # Group by agent type
        agent_results: Dict[str, List[float]] = {
            agent: [] for agent in self.agent_weights
        }
        
        for result in recent_results:
            agent_type = result.get('agent_type')
            if agent_type and agent_type in agent_results:
                # Calculate effectiveness score
                score = 0.0
                if result.get('success', False):
                    score = result.get('quality_score', 0.5)
                agent_results[agent_type].append(score)
        
        # Update effectiveness with exponential moving average
        alpha = 0.3  # Learning rate
        for agent_type, scores in agent_results.items():
            if scores:
                new_effectiveness = sum(scores) / len(scores)
                old_effectiveness = self.agent_effectiveness[agent_type]
                self.agent_effectiveness[agent_type] = (
                    alpha * new_effectiveness + (1 - alpha) * old_effectiveness
                )
    
    async def adjust_agent_weights(self) -> None:
        """Adjust agent weights based on effectiveness."""
        # Calculate total effectiveness
        total_effectiveness = sum(self.agent_effectiveness.values())
        
        if total_effectiveness == 0:
            return  # Avoid division by zero
        
        # Adjust weights proportionally to effectiveness
        for agent_type in self.agent_weights:
            # Blend current weight with effectiveness-based weight
            effectiveness_weight = self.agent_effectiveness[agent_type] / total_effectiveness
            current_weight = self.agent_weights[agent_type]
            
            # Use momentum to avoid drastic changes
            momentum = 0.8
            self.agent_weights[agent_type] = (
                momentum * current_weight + (1 - momentum) * effectiveness_weight
            )
        
        # Normalize to ensure sum is 1.0
        total_weight = sum(self.agent_weights.values())
        for agent_type in self.agent_weights:
            self.agent_weights[agent_type] /= total_weight
        
        logger.info(f"Adjusted agent weights: {self.agent_weights}")
    
    async def _get_system_state(self) -> Dict[str, Any]:
        """Get current system state from context memory."""
        # Always await since context_memory.get is async
        state = await self.context_memory.get('system_state') or {}
        
        # Add runtime information
        state['resource_utilization'] = self.resource_consumed / self.resource_config['compute_budget']
        state['active_allocations'] = len(self.active_allocations)
        
        return state
    
    async def _generate_task_parameters(
        self,
        agent_type: str,
        system_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate task parameters based on agent type and system state."""
        # Basic parameters that all agents need
        base_params = {
            'research_goal': system_state.get('research_goal', 'Unknown goal'),
            'iteration': system_state.get('current_iteration', 0)
        }
        
        # Agent-specific parameters
        if agent_type == 'generation':
            return {
                **base_params,
                'generation_method': random.choice(['literature_based', 'debate', 'assumptions', 'expansion']),
                'focus_area': system_state.get('current_focus_area')
            }
        elif agent_type == 'reflection':
            hypotheses = system_state.get('pending_review_hypotheses', [])
            if hypotheses:
                return {
                    **base_params,
                    'hypothesis_id': hypotheses[0],
                    'review_type': random.choice(['initial', 'deep_verification', 'simulation'])
                }
        elif agent_type == 'ranking':
            return {
                **base_params,
                'hypothesis_ids': system_state.get('tournament_candidates', [])[:10]
            }
        elif agent_type == 'evolution':
            return {
                **base_params,
                'hypothesis_id': system_state.get('top_hypothesis_id'),
                'strategy': random.choice(['refine', 'combine', 'simplify', 'paradigm_shift'])
            }
        elif agent_type == 'proximity':
            return {
                **base_params,
                'hypothesis_ids': system_state.get('all_hypothesis_ids', [])[:50]
            }
        elif agent_type == 'meta_review':
            return {
                **base_params,
                'focus': random.choice(['methodology', 'assumptions', 'themes'])
            }
        
        return base_params
    
    def _check_time_limit(self) -> bool:
        """Check if time limit has been exceeded."""
        if not self._start_time:
            return False
        
        elapsed = utcnow() - self._start_time
        limit = timedelta(hours=self.resource_config['time_limit_hours'])
        
        return elapsed >= limit