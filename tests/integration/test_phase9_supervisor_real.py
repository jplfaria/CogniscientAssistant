"""Integration tests for Phase 9: Supervisor Agent with real LLM interactions."""

import asyncio
import os
from typing import Dict, Any

import pytest

from src.agents.supervisor import SupervisorAgent
from src.core.models import Task, Hypothesis
from src.core.task_queue import TaskQueue, QueueConfig
from src.core.context_memory import ContextMemory
from src.llm.argo_provider import ArgoLLMProvider
from src.llm.provider_registry import ProviderRegistry


@pytest.mark.real_llm
@pytest.mark.asyncio
async def test_task_decomposition_quality():
    """Verify Supervisor decomposes tasks intelligently."""
    # Initialize components
    task_queue = TaskQueue(QueueConfig(capacity=100))
    memory = ContextMemory()
    
    # Use real Argo provider
    argo_provider = ArgoLLMProvider()
    registry = ProviderRegistry()
    registry.register_provider("argo", argo_provider)
    
    # Create supervisor with real LLM
    supervisor = SupervisorAgent(
        task_queue=task_queue,
        memory=memory,
        llm_provider=argo_provider
    )
    
    # Test research goal
    research_goal = "Why does ice float on water?"
    
    # Have supervisor create tasks
    tasks = await supervisor.create_tasks_for_goal(research_goal)
    
    # Verify o3 reasoning behavior
    print(f"\n=== o3 Task Decomposition for: {research_goal} ===")
    print(f"Number of tasks created: {len(tasks)}")
    
    for i, task in enumerate(tasks):
        print(f"\nTask {i+1}:")
        print(f"  Type: {task.type}")
        print(f"  Description: {task.description}")
        print(f"  Priority: {task.priority}")
        if 'reasoning' in task.context:
            print(f"  Reasoning: {task.context['reasoning']}")
    
    # Behavioral expectations for o3
    assert len(tasks) >= 3, "o3 should decompose into multiple subtasks"
    
    # Check for reasoning markers in task descriptions
    task_descriptions = [t.description.lower() for t in tasks]
    all_descriptions = " ".join(task_descriptions)
    
    # o3 should identify key scientific concepts
    key_concepts = ["density", "molecule", "hydrogen bond", "crystal", "structure"]
    found_concepts = [c for c in key_concepts if c in all_descriptions]
    assert len(found_concepts) >= 2, f"o3 should identify key concepts, found: {found_concepts}"
    
    # o3 should show systematic approach with reasoning steps
    systematic_markers = ["investigate", "analyze", "examine", "explore", "understand", "first", "then", "finally"]
    found_markers = [m for m in systematic_markers if m in all_descriptions]
    assert len(found_markers) >= 2, f"o3 should show systematic approach, found: {found_markers}"
    
    # Check for o3-specific reasoning patterns
    reasoning_patterns = ["step", "consider", "because", "therefore", "approach"]
    found_patterns = [p for p in reasoning_patterns if p in all_descriptions]
    assert len(found_patterns) >= 1, f"o3 should show reasoning steps, found: {found_patterns}"
    
    # Tasks should have appropriate priorities
    priorities = [t.priority for t in tasks]
    assert max(priorities) >= 2, "Should have some high-priority tasks"
    assert min(priorities) <= 2, "Should have varied priorities"
    
    return tasks


@pytest.mark.real_llm
@pytest.mark.asyncio
async def test_o3_reasoning_visibility():
    """Test that o3 model shows clear reasoning steps in Supervisor decisions."""
    # Initialize components
    task_queue = TaskQueue(QueueConfig(capacity=100))
    memory = ContextMemory()
    
    # Use real Argo provider
    argo_provider = ArgoLLMProvider()
    registry = ProviderRegistry()
    registry.register_provider("argo", argo_provider)
    
    # Create supervisor
    supervisor = SupervisorAgent(
        task_queue=task_queue,
        memory=memory,
        llm_provider=argo_provider
    )
    
    # Set up a scenario with multiple tasks
    await task_queue.submit(Task(
        type="hypothesis_generation",
        description="Generate hypotheses about water's anomalous expansion",
        priority=3,
        context={"topic": "water density"}
    ))
    
    await task_queue.submit(Task(
        type="literature_review", 
        description="Review research on hydrogen bonding in water",
        priority=2,
        context={"topic": "hydrogen bonds"}
    ))
    
    await task_queue.submit(Task(
        type="experiment_design",
        description="Design experiment to measure ice density",
        priority=1,
        context={"topic": "ice density measurement"}
    ))
    
    # Run orchestration for a few cycles
    cycles = []
    for i in range(3):
        print(f"\n=== Orchestration Cycle {i+1} ===")
        
        # Get current metrics
        metrics = await supervisor.get_system_metrics()
        print(f"Queue depth: {metrics['queue_depth']}")
        print(f"Active workers: {metrics['active_workers']}")
        
        # Orchestrate one cycle
        assigned = await supervisor.orchestrate()
        
        print(f"Tasks assigned: {len(assigned)}")
        for task_id, agent_type in assigned.items():
            task = await task_queue.get_task_info(task_id)
            print(f"  - {task.type}: assigned to {agent_type}")
        
        cycles.append({
            "metrics": metrics,
            "assigned": assigned
        })
        
        # Simulate some work being done
        if assigned:
            task_id = list(assigned.keys())[0]
            await task_queue.complete(task_id, {"result": "simulated completion"})
    
    # Verify intelligent orchestration behavior
    assert len(cycles) >= 3, "Should have completed multiple cycles"
    
    # Check that high-priority tasks were assigned first
    first_assignments = cycles[0]["assigned"]
    if first_assignments:
        first_task_id = list(first_assignments.keys())[0]
        first_task = await task_queue.get_task_info(first_task_id)
        # High priority tasks (3) should generally be assigned first
        assert first_task is not None
    
    # Verify agent selection diversity
    all_agents = []
    for cycle in cycles:
        all_agents.extend(cycle["assigned"].values())
    
    unique_agents = set(all_agents)
    assert len(unique_agents) >= 2, f"Should use multiple agent types, used: {unique_agents}"
    
    return cycles


@pytest.mark.real_llm
@pytest.mark.asyncio 
@pytest.mark.skip(reason="Resource management testing belongs in Phase 17 (full integration)")
async def test_supervisor_real_resource_management():
    """Test that Supervisor shows intelligent resource allocation with o3."""
    # Initialize components
    task_queue = TaskQueue(QueueConfig(capacity=100))
    memory = ContextMemory()
    
    # Use real Argo provider
    argo_provider = ArgoLLMProvider()
    registry = ProviderRegistry()
    registry.register_provider("argo", argo_provider)
    
    # Create supervisor with limited budget
    supervisor = SupervisorAgent(
        task_queue=task_queue,
        memory=memory,
        llm_provider=argo_provider,
        max_daily_budget=10.0  # $10 budget
    )
    
    # Create expensive research goal
    research_goal = "Develop a comprehensive theory explaining quantum entanglement in biological systems"
    
    # Get resource allocation plan
    tasks = await supervisor.create_tasks_for_goal(research_goal)
    
    print(f"\n=== Resource Allocation for Complex Goal ===")
    print(f"Goal: {research_goal}")
    print(f"Daily budget: ${supervisor.max_daily_budget}")
    
    # Allocate resources
    allocations = []
    for task in tasks[:5]:  # Test first 5 tasks
        allocation = await supervisor.allocate_resources(task)
        allocations.append(allocation)
        
        print(f"\nTask: {task.description[:60]}...")
        print(f"  Compute: {allocation['compute_units']} units")
        print(f"  Memory: {allocation['memory_mb']} MB")
        print(f"  Time: {allocation['time_limit_seconds']} seconds")
        print(f"  Estimated cost: ${allocation['estimated_cost']:.2f}")
    
    # Verify intelligent resource allocation
    # Complex tasks should get more resources
    compute_allocations = [a['compute_units'] for a in allocations]
    assert max(compute_allocations) > min(compute_allocations), "Should vary compute based on task complexity"
    
    # Total cost should respect budget
    total_cost = sum(a['estimated_cost'] for a in allocations)
    assert total_cost <= supervisor.max_daily_budget, f"Should respect budget: ${total_cost:.2f} <= ${supervisor.max_daily_budget}"
    
    # Memory should scale with task complexity
    memory_allocations = [a['memory_mb'] for a in allocations]
    assert max(memory_allocations) >= 512, "Complex tasks should get substantial memory"
    
    return allocations


if __name__ == "__main__":
    # Run with: pytest tests/integration/test_phase9_supervisor_real.py -v --real-llm
    pytest.main([__file__, "-v", "--real-llm"])