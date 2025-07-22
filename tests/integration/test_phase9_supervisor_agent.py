"""Integration tests for Phase 9: Supervisor Agent."""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import uuid

from src.agents.supervisor import SupervisorAgent
from src.core.models import Task, TaskState, TaskType, utcnow
from src.core.task_queue import TaskQueue, QueueConfig
from src.core.context_memory import ContextMemory
from src.llm.mock_provider import MockLLMProvider


@pytest.fixture
async def test_environment(tmp_path):
    """Create a test environment with real components."""
    # Initialize real components
    queue_config = QueueConfig(
        max_queue_size=10000,
        persistence_path=str(tmp_path / "queue_state.json"),
        auto_recovery=False,
        auto_start_persistence=False,
        auto_start_monitoring=False
    )
    task_queue = TaskQueue(config=queue_config)
    
    context_memory = ContextMemory(
        storage_path=tmp_path / "context_memory",
        retention_days=7
    )
    
    llm_provider = MockLLMProvider()
    
    # Initialize context memory with research goal
    await context_memory.set('research_goal', 'Develop new antimicrobial compounds')
    await context_memory.set('system_state', {
        'current_iteration': 1,
        'hypothesis_count': 0
    })
    
    yield {
        'task_queue': task_queue,
        'context_memory': context_memory,
        'llm_provider': llm_provider,
        'tmp_path': tmp_path
    }
    
    # Cleanup - TaskQueue doesn't have shutdown method
    pass


class TestSupervisorInitialization:
    """Test supervisor initialization in integrated environment."""
    
    @pytest.mark.asyncio
    async def test_supervisor_initialization(self, test_environment):
        """Test supervisor initializes correctly with real components."""
        supervisor = SupervisorAgent(
            task_queue=test_environment['task_queue'],
            context_memory=test_environment['context_memory'],
            llm_provider=test_environment['llm_provider']
        )
        
        assert supervisor is not None
        assert supervisor.task_queue == test_environment['task_queue']
        assert supervisor.context_memory == test_environment['context_memory']
        assert supervisor.llm_provider == test_environment['llm_provider']
        assert not supervisor.is_running
        assert supervisor.termination_probability == 0.0


class TestTaskCreation:
    """Test supervisor task creation and distribution."""
    
    @pytest.mark.asyncio
    async def test_supervisor_task_creation(self, test_environment):
        """Test supervisor can create and enqueue tasks."""
        supervisor = SupervisorAgent(
            task_queue=test_environment['task_queue'],
            context_memory=test_environment['context_memory'],
            llm_provider=test_environment['llm_provider']
        )
        
        # Create a generation task
        task = await supervisor.create_task(
            agent_type='generation',
            priority=3,  # High priority
            parameters={'goal': 'Test goal', 'method': 'literature_based'}
        )
        
        assert task is not None
        assert task.task_type == TaskType.GENERATE_HYPOTHESIS
        assert task.priority == 3
        assert task.payload['goal'] == 'Test goal'
        
        # Verify task is in queue
        queue_stats = await test_environment['task_queue'].get_queue_statistics()
        assert queue_stats['task_states']['pending'] == 1
    
    @pytest.mark.asyncio
    async def test_supervisor_orchestration(self, test_environment):
        """Test supervisor orchestrates multiple agents."""
        supervisor = SupervisorAgent(
            task_queue=test_environment['task_queue'],
            context_memory=test_environment['context_memory'],
            llm_provider=test_environment['llm_provider']
        )
        
        # Set weights to ensure variety
        supervisor.agent_weights = {
            'generation': 0.4,
            'reflection': 0.3,
            'ranking': 0.1,
            'evolution': 0.1,
            'proximity': 0.05,
            'meta_review': 0.05
        }
        
        # Create multiple tasks
        tasks = await supervisor.distribute_tasks(batch_size=10)
        
        assert len(tasks) == 10
        
        # Check task variety
        task_types = [task.task_type for task in tasks]
        unique_types = set(task_types)
        assert len(unique_types) >= 2  # Should have at least 2 different types
        
        # Verify all tasks are in queue
        queue_stats = await test_environment['task_queue'].get_queue_statistics()
        assert queue_stats['task_states']['pending'] == 10


class TestResourceManagement:
    """Test supervisor resource allocation and tracking."""
    
    @pytest.mark.asyncio  
    async def test_resource_allocation(self, test_environment):
        """Test supervisor allocates resources appropriately."""
        resource_config = {
            'max_workers': 4,
            'memory_budget_mb': 1024,
            'compute_budget': 200.0,
            'time_limit_hours': 2
        }
        
        supervisor = SupervisorAgent(
            task_queue=test_environment['task_queue'],
            context_memory=test_environment['context_memory'],
            llm_provider=test_environment['llm_provider'],
            resource_config=resource_config
        )
        
        # Test allocation for different agents
        allocations = {}
        for agent_type in ['generation', 'reflection', 'ranking']:
            allocation = await supervisor.allocate_resources(
                agent_type=agent_type,
                task_complexity='normal'
            )
            allocations[agent_type] = allocation
            
            assert 'compute_budget' in allocation
            assert 'memory_mb' in allocation
            assert 'timeout_seconds' in allocation
            assert allocation['compute_budget'] <= resource_config['compute_budget']
        
        # Verify different agents get different allocations
        assert allocations['generation']['compute_budget'] > allocations['ranking']['compute_budget']
    
    @pytest.mark.asyncio
    async def test_resource_pressure_handling(self, test_environment):
        """Test supervisor handles resource pressure correctly."""
        resource_config = {
            'max_workers': 2,
            'memory_budget_mb': 512,
            'compute_budget': 100.0,
            'time_limit_hours': 1
        }
        
        supervisor = SupervisorAgent(
            task_queue=test_environment['task_queue'],
            context_memory=test_environment['context_memory'],
            llm_provider=test_environment['llm_provider'],
            resource_config=resource_config
        )
        
        # Consume most resources
        supervisor.resource_consumed = 85.0
        
        # Allocation should succeed but be reduced
        allocation = await supervisor.allocate_resources(
            agent_type='generation',
            task_complexity='normal'
        )
        
        assert allocation['compute_budget'] < 20.0  # Reduced due to load
        
        # Consume almost all resources
        supervisor.resource_consumed = 95.0
        
        # Should fail to allocate
        with pytest.raises(RuntimeError, match="Insufficient resources"):
            await supervisor.allocate_resources(
                agent_type='meta_review',
                task_complexity='high'
            )


class TestProgressMonitoring:
    """Test supervisor progress monitoring and termination detection."""
    
    @pytest.mark.asyncio
    async def test_system_metrics_calculation(self, test_environment):
        """Test supervisor calculates system metrics correctly."""
        supervisor = SupervisorAgent(
            task_queue=test_environment['task_queue'],
            context_memory=test_environment['context_memory'],
            llm_provider=test_environment['llm_provider']
        )
        
        # Set up some test data
        await test_environment['context_memory'].set('hypotheses', [
            {'id': f'hyp-{i}', 'state': 'reviewed'} for i in range(5)
        ])
        await test_environment['context_memory'].set('reviews', [
            {'id': f'rev-{i}'} for i in range(3)
        ])
        
        # Create some tasks
        for i in range(3):
            await supervisor.create_task(
                agent_type='generation',
                priority=2,  # Medium priority
                parameters={'test': i}
            )
        
        # Calculate metrics
        metrics = await supervisor.calculate_system_metrics()
        
        assert metrics['hypothesis_count'] == 5
        assert metrics['review_count'] == 3
        assert metrics['pending_tasks'] == 3
        assert metrics['resource_utilization'] == 0.0
        assert 'agent_effectiveness' in metrics
    
    @pytest.mark.asyncio
    async def test_termination_detection(self, test_environment):
        """Test supervisor detects termination conditions."""
        supervisor = SupervisorAgent(
            task_queue=test_environment['task_queue'],
            context_memory=test_environment['context_memory'],
            llm_provider=test_environment['llm_provider']
        )
        
        # Test goal achievement termination
        await test_environment['context_memory'].set('system_state', {
            'research_goal_achieved': True,
            'high_quality_hypotheses': 12
        })
        
        should_terminate = await supervisor.check_termination_conditions()
        assert should_terminate is True
        
        # Test resource exhaustion termination
        await test_environment['context_memory'].set('system_state', {})
        supervisor.resource_consumed = supervisor.resource_config['compute_budget'] * 0.96
        
        should_terminate = await supervisor.check_termination_conditions()
        assert should_terminate is True
    
    @pytest.mark.asyncio
    async def test_adaptive_weight_adjustment(self, test_environment):
        """Test supervisor adjusts agent weights based on performance."""
        supervisor = SupervisorAgent(
            task_queue=test_environment['task_queue'],
            context_memory=test_environment['context_memory'],
            llm_provider=test_environment['llm_provider']
        )
        
        # Set initial weights
        initial_weights = supervisor.agent_weights.copy()
        
        # Simulate effectiveness scores
        supervisor.agent_effectiveness = {
            'generation': 0.9,
            'reflection': 0.7,
            'ranking': 0.5,
            'evolution': 0.6,
            'proximity': 0.4,
            'meta_review': 0.8
        }
        
        # Adjust weights
        await supervisor.adjust_agent_weights()
        
        # Verify weights changed
        assert supervisor.agent_weights != initial_weights
        
        # More effective agents should have higher weights
        assert supervisor.agent_weights['generation'] > supervisor.agent_weights['proximity']
        
        # Weights should still sum to 1.0
        total = sum(supervisor.agent_weights.values())
        assert abs(total - 1.0) < 0.001


class TestRecoveryMechanisms:
    """Test supervisor recovery and error handling."""
    
    @pytest.mark.asyncio
    async def test_supervisor_recovery(self, test_environment):
        """Test supervisor can recover from failures."""
        supervisor = SupervisorAgent(
            task_queue=test_environment['task_queue'],
            context_memory=test_environment['context_memory'],
            llm_provider=test_environment['llm_provider']
        )
        
        # Create some tasks
        tasks = []
        for i in range(3):
            task = await supervisor.create_task(
                agent_type='generation',
                priority=2,  # Medium priority
                parameters={'index': i}
            )
            tasks.append(task)
        
        # Simulate task failure
        failed_task = tasks[0]
        failed_task.state = TaskState.FAILED
        failed_task.error = "Simulated failure"
        
        # Reclaim resources
        supervisor.active_allocations[str(failed_task.id)] = {
            'compute_budget': 30.0,
            'memory_mb': 256
        }
        supervisor.resource_consumed = 30.0
        
        await supervisor.reclaim_resources(str(failed_task.id))
        
        # Verify resources reclaimed
        assert supervisor.resource_consumed == 0.0
        assert str(failed_task.id) not in supervisor.active_allocations


# Tests that may fail (waiting for other components)
class TestMultiAgentCoordination:
    """Test coordination with actual agents (may fail without agent implementations)."""
    
    @pytest.mark.asyncio
    async def test_multi_agent_coordination(self, test_environment):
        """Test supervisor coordinates multiple agents effectively."""
        supervisor = SupervisorAgent(
            task_queue=test_environment['task_queue'],
            context_memory=test_environment['context_memory'],
            llm_provider=test_environment['llm_provider']
        )
        
        # This test would require actual agent implementations
        # For now, just verify basic task creation works
        tasks = await supervisor.distribute_tasks(batch_size=5)
        assert len(tasks) == 5


class TestSupervisorPerformance:
    """Test supervisor performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_supervisor_performance(self, test_environment):
        """Test supervisor can handle high task throughput."""
        supervisor = SupervisorAgent(
            task_queue=test_environment['task_queue'],
            context_memory=test_environment['context_memory'],
            llm_provider=test_environment['llm_provider']
        )
        
        # Create many tasks quickly
        start_time = utcnow()
        tasks = await supervisor.distribute_tasks(batch_size=50)
        end_time = utcnow()
        
        # Should complete quickly
        duration = (end_time - start_time).total_seconds()
        assert duration < 1.0  # Should take less than 1 second
        
        # Verify all tasks created
        queue_stats = await test_environment['task_queue'].get_queue_statistics()
        assert queue_stats['task_states']['pending'] == 50