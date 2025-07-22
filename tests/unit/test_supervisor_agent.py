"""Unit tests for SupervisorAgent class."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import uuid

from src.core.models import Task, TaskState, TaskType, Hypothesis, utcnow
from src.core.task_queue import TaskQueue
from src.core.context_memory import ContextMemory
from src.llm.base import LLMProvider
from src.agents.supervisor import SupervisorAgent


class TestSupervisorAgentInitialization:
    """Test SupervisorAgent initialization and configuration."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for testing."""
        return {
            'task_queue': Mock(spec=TaskQueue),
            'context_memory': Mock(spec=ContextMemory),
            'llm_provider': Mock(spec=LLMProvider)
        }
    
    def test_supervisor_init_with_required_dependencies(self, mock_dependencies):
        """Test SupervisorAgent initializes with required dependencies."""
        supervisor = SupervisorAgent(
            task_queue=mock_dependencies['task_queue'],
            context_memory=mock_dependencies['context_memory'],
            llm_provider=mock_dependencies['llm_provider']
        )
        
        assert supervisor.task_queue == mock_dependencies['task_queue']
        assert supervisor.context_memory == mock_dependencies['context_memory']
        assert supervisor.llm_provider == mock_dependencies['llm_provider']
        assert supervisor.agent_weights == {
            'generation': 0.3,
            'reflection': 0.2,
            'ranking': 0.15,
            'evolution': 0.15,
            'proximity': 0.1,
            'meta_review': 0.1
        }
        assert supervisor.is_running is False
        assert supervisor.termination_probability == 0.0
    
    def test_supervisor_init_with_custom_agent_weights(self, mock_dependencies):
        """Test SupervisorAgent initializes with custom agent weights."""
        custom_weights = {
            'generation': 0.5,
            'reflection': 0.5,
            'ranking': 0.0,
            'evolution': 0.0,
            'proximity': 0.0,
            'meta_review': 0.0
        }
        
        supervisor = SupervisorAgent(
            task_queue=mock_dependencies['task_queue'],
            context_memory=mock_dependencies['context_memory'],
            llm_provider=mock_dependencies['llm_provider'],
            agent_weights=custom_weights
        )
        
        assert supervisor.agent_weights == custom_weights
    
    def test_supervisor_validates_agent_weights(self, mock_dependencies):
        """Test SupervisorAgent validates agent weights sum to 1.0."""
        invalid_weights = {
            'generation': 0.5,
            'reflection': 0.3,
            'ranking': 0.0,
            'evolution': 0.0,
            'proximity': 0.0,
            'meta_review': 0.0
        }  # Sum is 0.8, not 1.0
        
        with pytest.raises(ValueError, match="Agent weights must sum to 1.0"):
            SupervisorAgent(
                task_queue=mock_dependencies['task_queue'],
                context_memory=mock_dependencies['context_memory'],
                llm_provider=mock_dependencies['llm_provider'],
                agent_weights=invalid_weights
            )
    
    def test_supervisor_init_resource_config(self, mock_dependencies):
        """Test SupervisorAgent initializes with resource configuration."""
        resource_config = {
            'max_workers': 10,
            'memory_budget_mb': 4096,
            'compute_budget': 1000.0,
            'time_limit_hours': 24
        }
        
        supervisor = SupervisorAgent(
            task_queue=mock_dependencies['task_queue'],
            context_memory=mock_dependencies['context_memory'],
            llm_provider=mock_dependencies['llm_provider'],
            resource_config=resource_config
        )
        
        assert supervisor.resource_config == resource_config
        assert supervisor.resource_consumed == 0.0


class TestTaskDistribution:
    """Test SupervisorAgent task distribution logic."""
    
    @pytest.fixture
    def supervisor(self, mock_dependencies):
        """Create a SupervisorAgent instance for testing."""
        return SupervisorAgent(
            task_queue=mock_dependencies['task_queue'],
            context_memory=mock_dependencies['context_memory'],
            llm_provider=mock_dependencies['llm_provider']
        )
    
    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies."""
        return {
            'task_queue': AsyncMock(spec=TaskQueue),
            'context_memory': AsyncMock(spec=ContextMemory),
            'llm_provider': AsyncMock(spec=LLMProvider)
        }
    
    @pytest.mark.asyncio
    async def test_create_task_basic(self, supervisor):
        """Test creating a basic task."""
        task_params = {
            'agent_type': 'generation',
            'priority': 3,  # High priority
            'parameters': {'goal': 'Test research goal'}
        }
        
        # Mock the enqueue method to return the task
        supervisor.task_queue.enqueue.return_value = Task(
            id=uuid.uuid4(),
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=3,
            payload=task_params['parameters'],
            state=TaskState.PENDING,
            created_at=utcnow()
        )
        
        task = await supervisor.create_task(**task_params)
        
        assert task is not None
        assert task.task_type == TaskType.GENERATE_HYPOTHESIS
        assert task.priority == 3
        assert task.payload == task_params['parameters']
        supervisor.task_queue.enqueue.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_select_next_agent_weighted_random(self, supervisor):
        """Test agent selection uses weighted random sampling."""
        # Set deterministic weights for testing
        supervisor.agent_weights = {
            'generation': 1.0,
            'reflection': 0.0,
            'ranking': 0.0,
            'evolution': 0.0,
            'proximity': 0.0,
            'meta_review': 0.0
        }
        
        # Mock system state
        supervisor.context_memory.get.return_value = {
            'hypothesis_count': 10,
            'pending_reviews': 5,
            'tournament_progress': 0.0
        }
        
        selected_agent = await supervisor.select_next_agent()
        
        assert selected_agent == 'generation'
    
    @pytest.mark.asyncio
    async def test_distribute_tasks_creates_multiple_tasks(self, supervisor):
        """Test distribute_tasks creates appropriate number of tasks."""
        # Mock system state suggesting generation phase
        supervisor.context_memory.get.return_value = {
            'hypothesis_count': 0,
            'pending_reviews': 0,
            'tournament_progress': 0.0,
            'research_goal': 'Test goal'
        }
        
        # Mock task creation
        mock_task = Task(
            id=uuid.uuid4(),
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=2,
            payload={},
            state=TaskState.PENDING,
            created_at=utcnow()
        )
        supervisor.task_queue.enqueue.return_value = mock_task
        
        await supervisor.distribute_tasks(batch_size=5)
        
        # Should create 5 tasks
        assert supervisor.task_queue.enqueue.call_count == 5
    
    @pytest.mark.asyncio
    async def test_create_task_with_metadata(self, supervisor):
        """Test task creation with additional metadata in parameters."""
        task_params = {
            'agent_type': 'reflection',
            'priority': 2,  # Medium priority
            'parameters': {
                'hypothesis_id': 'test-hyp-1',
                'timeout': 300,
                'dependencies': ['dep-1', 'dep-2']
            }
        }
        
        # Mock the enqueue to return a task
        expected_task = Task(
            id=uuid.uuid4(),
            task_type=TaskType.REFLECT_ON_HYPOTHESIS,
            priority=2,
            payload=task_params['parameters'],
            state=TaskState.PENDING,
            created_at=utcnow()
        )
        supervisor.task_queue.enqueue.return_value = expected_task
        
        task = await supervisor.create_task(**task_params)
        
        # Should pass metadata in payload
        assert task.payload['timeout'] == 300
        assert task.payload['dependencies'] == ['dep-1', 'dep-2']
        assert task is not None


class TestResourceAllocation:
    """Test SupervisorAgent resource allocation methods."""
    
    @pytest.fixture
    def supervisor_with_resources(self, mock_dependencies):
        """Create supervisor with resource configuration."""
        resource_config = {
            'max_workers': 8,
            'memory_budget_mb': 2048,
            'compute_budget': 500.0,
            'time_limit_hours': 12
        }
        
        return SupervisorAgent(
            task_queue=mock_dependencies['task_queue'],
            context_memory=mock_dependencies['context_memory'],
            llm_provider=mock_dependencies['llm_provider'],
            resource_config=resource_config
        )
    
    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies."""
        return {
            'task_queue': AsyncMock(spec=TaskQueue),
            'context_memory': AsyncMock(spec=ContextMemory),
            'llm_provider': AsyncMock(spec=LLMProvider)
        }
    
    @pytest.mark.asyncio
    async def test_allocate_resources_within_budget(self, supervisor_with_resources):
        """Test resource allocation stays within budget."""
        agent_type = 'generation'
        
        # Mock context memory to return empty state
        supervisor_with_resources.context_memory.get.return_value = {}
        
        allocation = await supervisor_with_resources.allocate_resources(
            agent_type=agent_type,
            task_complexity='high'
        )
        
        assert 'compute_budget' in allocation
        assert 'memory_mb' in allocation
        assert 'timeout_seconds' in allocation
        assert allocation['compute_budget'] <= supervisor_with_resources.resource_config['compute_budget']
        assert allocation['memory_mb'] <= supervisor_with_resources.resource_config['memory_budget_mb']
    
    @pytest.mark.asyncio
    async def test_reclaim_resources_on_completion(self, supervisor_with_resources):
        """Test resources are reclaimed when task completes."""
        task_id = str(uuid.uuid4())
        allocated_resources = {
            'compute_budget': 50.0,
            'memory_mb': 256
        }
        
        # Track resource consumption
        supervisor_with_resources.resource_consumed = 50.0
        supervisor_with_resources.active_allocations = {task_id: allocated_resources}
        
        await supervisor_with_resources.reclaim_resources(task_id)
        
        assert supervisor_with_resources.resource_consumed == 0.0
        assert task_id not in supervisor_with_resources.active_allocations
    
    @pytest.mark.asyncio
    async def test_resource_allocation_scales_with_load(self, supervisor_with_resources):
        """Test resource allocation adjusts based on system load."""
        # Set high resource consumption to trigger load reduction
        supervisor_with_resources.resource_consumed = 450.0  # 90% of 500 budget
        supervisor_with_resources.context_memory.get.return_value = {}
        
        allocation = await supervisor_with_resources.allocate_resources(
            agent_type='generation',
            task_complexity='normal'
        )
        
        # Should allocate minimal resources under high load
        assert allocation['compute_budget'] < 20.0  # Lower than normal
    
    @pytest.mark.asyncio
    async def test_prevent_resource_overallocation(self, supervisor_with_resources):
        """Test prevents allocation beyond available resources."""
        # Consume most resources
        supervisor_with_resources.resource_consumed = 495.0  # Near 500 limit, leaves < 10
        supervisor_with_resources.context_memory.get.return_value = {}
        
        with pytest.raises(RuntimeError, match="Insufficient resources"):
            await supervisor_with_resources.allocate_resources(
                agent_type='generation',
                task_complexity='high'
            )


class TestProgressMonitoring:
    """Test SupervisorAgent progress monitoring capabilities."""
    
    @pytest.fixture
    def supervisor(self, mock_dependencies):
        """Create supervisor for testing."""
        return SupervisorAgent(
            task_queue=mock_dependencies['task_queue'],
            context_memory=mock_dependencies['context_memory'],
            llm_provider=mock_dependencies['llm_provider']
        )
    
    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies."""
        return {
            'task_queue': AsyncMock(spec=TaskQueue),
            'context_memory': AsyncMock(spec=ContextMemory),
            'llm_provider': AsyncMock(spec=LLMProvider)
        }
    
    @pytest.mark.asyncio
    async def test_calculate_system_metrics(self, supervisor):
        """Test system metrics calculation."""
        # Mock task queue statistics
        supervisor.task_queue.get_queue_statistics.return_value = {
            'pending_tasks': 10,
            'executing_tasks': 5,
            'task_states': {
                'pending': 10,
                'executing': 5,
                'completed': 100,
                'failed': 2
            }
        }
        
        # Mock context memory data
        supervisor.context_memory.get.side_effect = lambda key: {
            'hypotheses': [{'id': f'hyp-{i}', 'state': 'reviewed'} for i in range(50)],
            'reviews': [{'id': f'rev-{i}'} for i in range(40)],
            'tournament_results': {'progress': 0.6}
        }.get(key, {})
        
        metrics = await supervisor.calculate_system_metrics()
        
        assert metrics['hypothesis_count'] == 50
        assert metrics['review_count'] == 40
        assert metrics['tournament_progress'] == 0.6
        assert metrics['task_completion_rate'] > 0.9
    
    @pytest.mark.asyncio
    async def test_detect_termination_conditions(self, supervisor):
        """Test termination detection logic."""
        # Test goal achievement termination
        supervisor.context_memory.get.return_value = {
            'research_goal_achieved': True,
            'high_quality_hypotheses': 15
        }
        
        should_terminate = await supervisor.check_termination_conditions()
        
        assert should_terminate is True
        assert supervisor.termination_probability >= 0.2  # At least one condition met
    
    @pytest.mark.asyncio
    async def test_update_agent_effectiveness(self, supervisor):
        """Test agent effectiveness tracking and updates."""
        # Mock completed tasks with results
        task_results = [
            {'agent_type': 'generation', 'success': True, 'quality_score': 0.8},
            {'agent_type': 'generation', 'success': True, 'quality_score': 0.9},
            {'agent_type': 'reflection', 'success': True, 'quality_score': 0.7},
            {'agent_type': 'reflection', 'success': False, 'quality_score': 0.0}
        ]
        
        supervisor.context_memory.get.return_value = task_results
        
        await supervisor.update_agent_effectiveness()
        
        # Generation should have higher effectiveness
        assert supervisor.agent_effectiveness['generation'] > supervisor.agent_effectiveness['reflection']
    
    @pytest.mark.asyncio
    async def test_adaptive_weight_adjustment(self, supervisor):
        """Test adaptive adjustment of agent weights based on effectiveness."""
        # Set initial effectiveness scores
        supervisor.agent_effectiveness = {
            'generation': 0.9,  # Very effective
            'reflection': 0.5,  # Moderately effective
            'ranking': 0.3,     # Less effective
            'evolution': 0.6,
            'proximity': 0.4,
            'meta_review': 0.7
        }
        
        await supervisor.adjust_agent_weights()
        
        # More effective agents should get higher weights
        assert supervisor.agent_weights['generation'] > supervisor.agent_weights['ranking']
        # Weights should still sum to 1.0
        assert abs(sum(supervisor.agent_weights.values()) - 1.0) < 0.001