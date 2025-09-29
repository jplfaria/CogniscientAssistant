"""Unit tests for the Task model."""

from datetime import datetime
from enum import Enum
from uuid import UUID

import pytest
from pydantic import ValidationError

from src.core.models import Task, TaskState, TaskType


class TestTaskState:
    """Test the TaskState enum."""
    
    def test_task_state_values(self):
        """Test that TaskState has all required values."""
        assert TaskState.PENDING.value == "pending"
        assert TaskState.ASSIGNED.value == "assigned"
        assert TaskState.EXECUTING.value == "executing"
        assert TaskState.COMPLETED.value == "completed"
        assert TaskState.FAILED.value == "failed"
    
    def test_task_state_members(self):
        """Test that TaskState has exactly the required members."""
        expected_members = {"PENDING", "ASSIGNED", "EXECUTING", "COMPLETED", "FAILED"}
        actual_members = {member.name for member in TaskState}
        assert actual_members == expected_members


class TestTaskType:
    """Test the TaskType enum."""
    
    def test_task_type_values(self):
        """Test that TaskType has expected values."""
        # These should be defined based on the specs
        assert hasattr(TaskType, "GENERATE_HYPOTHESIS")
        assert hasattr(TaskType, "REFLECT_ON_HYPOTHESIS")
        assert hasattr(TaskType, "RANK_HYPOTHESES")
        assert hasattr(TaskType, "EVOLVE_HYPOTHESIS")
        assert hasattr(TaskType, "FIND_SIMILAR_HYPOTHESES")
        assert hasattr(TaskType, "META_REVIEW")


class TestTaskModel:
    """Test the Task model."""
    
    def test_task_creation_minimal(self):
        """Test creating a task with minimal required fields."""
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=1,
            payload={"goal": "Test hypothesis generation"}
        )
        
        assert isinstance(task.id, UUID)
        assert task.task_type == TaskType.GENERATE_HYPOTHESIS
        assert task.priority == 1
        assert task.state == TaskState.PENDING
        assert task.payload == {"goal": "Test hypothesis generation"}
        assert task.assigned_to is None
        assert task.result is None
        assert task.error is None
        assert isinstance(task.created_at, datetime)
        assert task.assigned_at is None
        assert task.completed_at is None
    
    def test_task_creation_with_id(self):
        """Test creating a task with a specific ID."""
        task_id = UUID("12345678-1234-5678-1234-567812345678")
        task = Task(
            id=task_id,
            task_type=TaskType.REFLECT_ON_HYPOTHESIS,
            priority=2,
            payload={"hypothesis_id": "h123"}
        )
        
        assert task.id == task_id
    
    def test_task_priority_validation(self):
        """Test that task priority must be positive."""
        with pytest.raises(ValidationError) as exc_info:
            Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=0,
                payload={}
            )
        assert "priority" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            Task(
                task_type=TaskType.GENERATE_HYPOTHESIS,
                priority=-1,
                payload={}
            )
        assert "priority" in str(exc_info.value)
    
    def test_task_state_transitions(self):
        """Test task state transition methods."""
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=1,
            payload={}
        )
        
        # Test assign
        assert task.state == TaskState.PENDING
        task.assign("worker-1")
        assert task.state == TaskState.ASSIGNED
        assert task.assigned_to == "worker-1"
        assert isinstance(task.assigned_at, datetime)
        
        # Test start execution
        task.start_execution()
        assert task.state == TaskState.EXECUTING
        
        # Test complete
        result = {"hypothesis": "Test hypothesis"}
        task.complete(result)
        assert task.state == TaskState.COMPLETED
        assert task.result == result
        assert isinstance(task.completed_at, datetime)
        
    def test_task_fail(self):
        """Test failing a task."""
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=1,
            payload={}
        )
        
        task.assign("worker-1")
        task.start_execution()
        
        error_msg = "Generation failed"
        task.fail(error_msg)
        
        assert task.state == TaskState.FAILED
        assert task.error == error_msg
        assert isinstance(task.completed_at, datetime)
    
    def test_task_state_transition_validation(self):
        """Test that invalid state transitions raise errors."""
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=1,
            payload={}
        )
        
        # Can't start execution without assignment
        with pytest.raises(ValueError) as exc_info:
            task.start_execution()
        assert "Cannot start execution" in str(exc_info.value)
        
        # Can't complete without execution
        with pytest.raises(ValueError) as exc_info:
            task.complete({})
        assert "Cannot complete" in str(exc_info.value)
        
        # Can't reassign
        task.assign("worker-1")
        with pytest.raises(ValueError) as exc_info:
            task.assign("worker-2")
        assert "already assigned" in str(exc_info.value)
    
    def test_task_serialization(self):
        """Test task serialization to/from dict."""
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=1,
            payload={"goal": "Test"}
        )
        
        # Serialize with mode='json' to trigger serializers
        task_dict = task.model_dump(mode='json')
        assert task_dict["id"] == str(task.id)
        assert task_dict["task_type"] == TaskType.GENERATE_HYPOTHESIS.value
        assert task_dict["priority"] == 1
        assert task_dict["state"] == TaskState.PENDING.value
        
        # Deserialize
        task2 = Task.model_validate(task_dict)
        assert str(task2.id) == str(task.id)  # Compare as strings
        assert task2.task_type == task.task_type
        assert task2.priority == task.priority
        assert task2.state == task.state
    
    def test_task_json_serialization(self):
        """Test task JSON serialization."""
        task = Task(
            task_type=TaskType.GENERATE_HYPOTHESIS,
            priority=1,
            payload={"goal": "Test"}
        )
        
        # To JSON
        json_str = task.model_dump_json()
        assert isinstance(json_str, str)
        
        # From JSON
        task2 = Task.model_validate_json(json_str)
        assert task2.id == task.id
        assert task2.task_type == task.task_type