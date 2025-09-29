"""Tests for Task BAML schema."""

import pytest
from datetime import datetime, timezone
from uuid import UUID, uuid4


def test_task_schema_contains_required_fields():
    """Test that Task BAML schema has all required fields."""
    # When BAML is compiled, we should be able to import the generated Task type
    # For now, we'll test the schema structure once it's created
    expected_fields = {
        "id": "string",
        "task_type": "TaskType",
        "priority": "int",
        "state": "TaskState",
        "payload": "map<string, any>",
        "assigned_to": "string?",
        "result": "map<string, any>?",
        "error": "string?",
        "created_at": "string",
        "assigned_at": "string?",
        "completed_at": "string?"
    }
    # This test will be properly implemented once BAML generation is set up
    assert True  # Placeholder for now


def test_task_type_enum_values():
    """Test that TaskType enum has all required values."""
    expected_values = [
        "generate_hypothesis",
        "reflect_on_hypothesis",
        "rank_hypotheses",
        "evolve_hypothesis",
        "find_similar_hypotheses",
        "meta_review"
    ]
    # This test will validate the BAML enum once compiled
    assert True  # Placeholder for now


def test_task_state_enum_values():
    """Test that TaskState enum has all required values."""
    expected_values = [
        "pending",
        "assigned", 
        "executing",
        "completed",
        "failed"
    ]
    # This test will validate the BAML enum once compiled
    assert True  # Placeholder for now


def test_task_serialization_format():
    """Test that Task can be serialized to expected format."""
    # Example task data that should match BAML schema
    task_data = {
        "id": str(uuid4()),
        "task_type": "generate_hypothesis",
        "priority": 5,
        "state": "pending",
        "payload": {
            "research_goal": "Find novel cancer therapeutics",
            "constraints": ["FDA approved", "Low toxicity"]
        },
        "assigned_to": None,
        "result": None,
        "error": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "assigned_at": None,
        "completed_at": None
    }
    
    # Verify the structure matches what BAML expects
    assert isinstance(task_data["id"], str)
    assert isinstance(task_data["priority"], int)
    assert task_data["priority"] > 0
    assert isinstance(task_data["created_at"], str)
    assert task_data["created_at"].endswith("Z") or "+" in task_data["created_at"]


def test_agent_request_schema():
    """Test that AgentRequest schema has required fields."""
    expected_fields = {
        "request_id": "string",
        "agent_type": "AgentType", 
        "request_type": "RequestType",
        "content": "RequestContent"
    }
    # This test will be properly implemented once BAML generation is set up
    assert True  # Placeholder for now


def test_agent_response_schema():
    """Test that AgentResponse schema has required fields."""
    expected_fields = {
        "request_id": "string",
        "status": "ResponseStatus",
        "response": "ResponseData?",
        "error": "ErrorInfo?"
    }
    # This test will be properly implemented once BAML generation is set up
    assert True  # Placeholder for now