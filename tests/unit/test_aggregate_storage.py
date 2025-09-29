"""Test aggregate storage functionality for ContextMemory."""
import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, Any, List

from src.core.context_memory import ContextMemory, AgentOutput


@pytest.fixture
async def context_memory(tmp_path):
    """Create a ContextMemory instance for testing."""
    cm = ContextMemory(
        storage_path=tmp_path / "test_context",
        retention_days=30,
        checkpoint_interval_minutes=5,
        max_storage_gb=50
    )
    await cm.initialize()
    return cm


@pytest.fixture
def sample_agent_outputs():
    """Create sample agent outputs for testing."""
    outputs = []
    for i in range(5):
        output = AgentOutput(
            agent_type="generation",
            task_id=f"task_{i}",
            timestamp=datetime.now() + timedelta(minutes=i),
            results={
                "hypotheses_generated": 3,
                "quality_score": 0.7 + (i * 0.05),
                "resource_consumed": 50 + (i * 10)
            },
            state_data={"iteration": i}
        )
        outputs.append(output)
    return outputs


@pytest.mark.asyncio
async def test_store_effectiveness_metrics(context_memory):
    """Test storing effectiveness metrics in aggregates."""
    # Store effectiveness metrics
    metrics = {
        "generation": {"success_rate": 0.85, "avg_quality": 0.72, "resource_efficiency": 0.9},
        "reflection": {"success_rate": 0.90, "avg_quality": 0.88, "resource_efficiency": 0.85},
        "ranking": {"success_rate": 0.95, "convergence_rate": 0.7, "resource_efficiency": 0.8}
    }
    
    result = await context_memory.store_aggregate(
        aggregate_type="effectiveness_metrics",
        data=metrics,
        timestamp=datetime.now()
    )
    
    assert result is True
    
    # Verify file was created
    aggregate_file = context_memory.storage_path / "aggregates" / "effectiveness_metrics.json"
    assert aggregate_file.exists()
    
    # Verify content
    with open(aggregate_file, 'r') as f:
        stored_data = json.load(f)
    
    assert "entries" in stored_data
    assert len(stored_data["entries"]) == 1
    assert stored_data["entries"][0]["data"] == metrics


@pytest.mark.asyncio
async def test_store_pattern_history(context_memory):
    """Test storing pattern history in aggregates."""
    # Store pattern data
    patterns = {
        "common_hypothesis_patterns": [
            {"pattern": "mechanism_based", "frequency": 0.4, "success_rate": 0.8},
            {"pattern": "correlation_based", "frequency": 0.3, "success_rate": 0.6}
        ],
        "successful_evolution_strategies": [
            {"strategy": "enhancement", "usage": 0.5, "improvement_rate": 0.7},
            {"strategy": "combination", "usage": 0.3, "improvement_rate": 0.65}
        ]
    }
    
    result = await context_memory.store_aggregate(
        aggregate_type="pattern_history",
        data=patterns,
        timestamp=datetime.now()
    )
    
    assert result is True
    
    # Verify storage
    aggregate_file = context_memory.storage_path / "aggregates" / "pattern_history.json"
    assert aggregate_file.exists()


@pytest.mark.asyncio
async def test_store_research_progress(context_memory):
    """Test storing research progress in aggregates."""
    # Store research progress
    progress = {
        "total_hypotheses": 150,
        "quality_distribution": {
            "high": 30,
            "medium": 80,
            "low": 40
        },
        "coverage_areas": ["neuroscience", "biochemistry", "genetics"],
        "milestone_reached": "initial_diversity",
        "estimated_completion": 0.3
    }
    
    result = await context_memory.store_aggregate(
        aggregate_type="research_progress",
        data=progress,
        timestamp=datetime.now()
    )
    
    assert result is True


@pytest.mark.asyncio
async def test_retrieve_aggregate_latest(context_memory):
    """Test retrieving latest aggregate data."""
    # Store multiple entries
    for i in range(3):
        metrics = {
            "generation": {"success_rate": 0.8 + (i * 0.05)},
            "timestamp_index": i
        }
        await context_memory.store_aggregate(
            aggregate_type="effectiveness_metrics",
            data=metrics,
            timestamp=datetime.now() + timedelta(minutes=i)
        )
        await asyncio.sleep(0.1)
    
    # Retrieve latest
    latest_data = await context_memory.retrieve_aggregate(
        aggregate_type="effectiveness_metrics",
        query_type="latest"
    )
    
    assert latest_data is not None
    assert latest_data["timestamp_index"] == 2
    assert latest_data["generation"]["success_rate"] == 0.9


@pytest.mark.asyncio
async def test_retrieve_aggregate_time_range(context_memory):
    """Test retrieving aggregate data within time range."""
    base_time = datetime.now()
    
    # Store entries at different times
    for i in range(5):
        timestamp = base_time + timedelta(hours=i)
        await context_memory.store_aggregate(
            aggregate_type="research_progress",
            data={"hour": i, "hypotheses": 10 * i},
            timestamp=timestamp
        )
    
    # Query for middle range
    start_time = base_time + timedelta(hours=1)
    end_time = base_time + timedelta(hours=3)
    
    results = await context_memory.retrieve_aggregate(
        aggregate_type="research_progress",
        query_type="time_range",
        start_time=start_time,
        end_time=end_time
    )
    
    assert isinstance(results, list)
    assert len(results) == 3  # Hours 1, 2, 3
    assert all(1 <= r["hour"] <= 3 for r in results)


@pytest.mark.asyncio
async def test_compute_aggregate_statistics(context_memory, sample_agent_outputs):
    """Test computing aggregate statistics from agent outputs."""
    # Start a new iteration
    await context_memory.start_new_iteration()
    
    # Store agent outputs
    for output in sample_agent_outputs:
        await context_memory.store_agent_output(output)
    
    # Compute aggregates
    stats = await context_memory.compute_aggregate_statistics(
        agent_type="generation",
        metric="quality_score"
    )
    
    assert stats is not None
    assert "average" in stats
    assert "min" in stats
    assert "max" in stats
    assert "count" in stats
    
    # Verify calculations
    assert stats["count"] == 5
    assert abs(stats["min"] - 0.7) < 0.01
    assert abs(stats["max"] - 0.9) < 0.01
    assert abs(stats["average"] - 0.8) < 0.01


@pytest.mark.asyncio
async def test_aggregate_storage_persistence(context_memory):
    """Test that aggregates persist across memory instances."""
    # Store aggregate
    data = {"test_key": "test_value", "number": 42}
    await context_memory.store_aggregate(
        aggregate_type="test_aggregate",
        data=data,
        timestamp=datetime.now()
    )
    
    # Create new instance with same storage path
    new_cm = ContextMemory(storage_path=context_memory.storage_path)
    await new_cm.initialize()
    
    # Retrieve from new instance
    retrieved = await new_cm.retrieve_aggregate(
        aggregate_type="test_aggregate",
        query_type="latest"
    )
    
    assert retrieved == data


@pytest.mark.asyncio
async def test_aggregate_update_merge(context_memory):
    """Test updating and merging aggregate data."""
    # Initial aggregate
    initial_data = {
        "counters": {"total": 100, "success": 80},
        "rates": {"success_rate": 0.8}
    }
    
    await context_memory.store_aggregate(
        aggregate_type="cumulative_stats",
        data=initial_data,
        timestamp=datetime.now()
    )
    
    # Update with merge
    update_data = {
        "counters": {"total": 150, "success": 120},
        "rates": {"success_rate": 0.8, "improvement_rate": 0.1}
    }
    
    await context_memory.update_aggregate(
        aggregate_type="cumulative_stats",
        data=update_data,
        merge_strategy="replace"
    )
    
    # Verify merged data
    result = await context_memory.retrieve_aggregate(
        aggregate_type="cumulative_stats",
        query_type="latest"
    )
    
    assert result["counters"]["total"] == 150
    assert result["rates"]["improvement_rate"] == 0.1


@pytest.mark.asyncio
async def test_aggregate_type_validation(context_memory):
    """Test validation of aggregate types."""
    # Valid aggregate types
    valid_types = ["effectiveness_metrics", "pattern_history", "research_progress"]
    
    for agg_type in valid_types:
        result = await context_memory.store_aggregate(
            aggregate_type=agg_type,
            data={"test": "data"},
            timestamp=datetime.now()
        )
        assert result is True
    
    # Custom aggregate type should also work
    result = await context_memory.store_aggregate(
        aggregate_type="custom_aggregate",
        data={"custom": "data"},
        timestamp=datetime.now()
    )
    assert result is True


@pytest.mark.asyncio
async def test_aggregate_size_limits(context_memory):
    """Test aggregate storage size limits."""
    # Create large aggregate data
    large_data = {
        "items": [{"id": i, "data": "x" * 1000} for i in range(100)]  # ~100KB
    }
    
    # Should handle large data
    result = await context_memory.store_aggregate(
        aggregate_type="large_aggregate",
        data=large_data,
        timestamp=datetime.now()
    )
    assert result is True
    
    # Verify retrieval works
    retrieved = await context_memory.retrieve_aggregate(
        aggregate_type="large_aggregate",
        query_type="latest"
    )
    assert len(retrieved["items"]) == 100


@pytest.mark.asyncio
async def test_aggregate_concurrent_writes(context_memory):
    """Test concurrent writes to aggregates."""
    # Define concurrent write tasks
    async def write_aggregate(index: int):
        data = {"writer": index, "timestamp": datetime.now().isoformat()}
        return await context_memory.store_aggregate(
            aggregate_type="concurrent_test",
            data=data,
            timestamp=datetime.now() + timedelta(seconds=index)
        )
    
    # Execute concurrent writes
    tasks = [write_aggregate(i) for i in range(5)]
    results = await asyncio.gather(*tasks)
    
    # All writes should succeed
    assert all(results)
    
    # Verify all entries are stored
    aggregate_file = context_memory.storage_path / "aggregates" / "concurrent_test.json"
    with open(aggregate_file, 'r') as f:
        stored_data = json.load(f)
    
    assert len(stored_data["entries"]) == 5


@pytest.mark.asyncio
async def test_aggregate_cleanup(context_memory):
    """Test cleanup of old aggregate entries."""
    # Store old and new entries
    old_timestamp = datetime.now() - timedelta(days=35)
    new_timestamp = datetime.now()
    
    # Manually create aggregate file with old and new entries
    aggregate_data = {
        "entries": [
            {
                "timestamp": old_timestamp.isoformat(),
                "data": {"old": True}
            },
            {
                "timestamp": new_timestamp.isoformat(),
                "data": {"old": False}
            }
        ]
    }
    
    aggregate_file = context_memory.storage_path / "aggregates" / "test_cleanup.json"
    aggregate_file.parent.mkdir(parents=True, exist_ok=True)
    with open(aggregate_file, 'w') as f:
        json.dump(aggregate_data, f)
    
    # Run cleanup
    cleaned_count = await context_memory.cleanup_aggregate_entries()
    
    assert cleaned_count >= 1
    
    # Verify old entry is removed
    with open(aggregate_file, 'r') as f:
        cleaned_data = json.load(f)
    
    assert len(cleaned_data["entries"]) == 1
    assert cleaned_data["entries"][0]["data"]["old"] is False


@pytest.mark.asyncio
async def test_list_aggregate_types(context_memory):
    """Test listing all aggregate types."""
    # Store different aggregate types
    types = ["metrics", "patterns", "progress", "custom"]
    for agg_type in types:
        await context_memory.store_aggregate(
            aggregate_type=agg_type,
            data={"type": agg_type},
            timestamp=datetime.now()
        )
    
    # List all types
    available_types = await context_memory.list_aggregate_types()
    
    assert set(available_types) == set(types)


@pytest.mark.asyncio
async def test_get_aggregate_summary(context_memory):
    """Test getting summary of all aggregates."""
    # Store various aggregates
    await context_memory.store_aggregate(
        aggregate_type="metrics",
        data={"value": 1},
        timestamp=datetime.now()
    )
    
    await context_memory.store_aggregate(
        aggregate_type="metrics",
        data={"value": 2},
        timestamp=datetime.now() + timedelta(minutes=1)
    )
    
    await context_memory.store_aggregate(
        aggregate_type="patterns",
        data={"pattern": "test"},
        timestamp=datetime.now()
    )
    
    # Get summary
    summary = await context_memory.get_aggregate_summary()
    
    assert "metrics" in summary
    assert "patterns" in summary
    assert summary["metrics"]["entry_count"] == 2
    assert summary["patterns"]["entry_count"] == 1
    assert "latest_timestamp" in summary["metrics"]
    assert "file_size" in summary["metrics"]