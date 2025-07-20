"""Tests for BAML SafetyCheck schema validation."""

import pytest
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum


# Mock the BAML types until client is generated
class SafetyLevel(Enum):
    SAFE = "safe"
    CONCERNING = "concerning"
    BLOCKED = "blocked"


class SafetyCategory(Enum):
    CONTENT_SAFETY = "content_safety"
    GOAL_VIOLATION = "goal_violation"
    ETHICAL_CONCERN = "ethical_concern"
    RESOURCE_MISUSE = "resource_misuse"


@dataclass
class SafetyCheck:
    id: str
    target_type: str
    target_id: str
    safety_level: SafetyLevel
    passed: bool
    checks_performed: list[str]
    timestamp: str
    violations: list[str] | None = None
    recommendations: list[str] | None = None
    category: SafetyCategory | None = None
    metadata: dict[str, Any] | None = None


class TestSafetyCheckSchema:
    """Test suite for SafetyCheck BAML schema."""
    
    def test_create_safety_check_minimal(self):
        """Test creating SafetyCheck with minimal required fields."""
        safety_check = SafetyCheck(
            id="sc_001",
            target_type="hypothesis",
            target_id="hyp_001",
            safety_level=SafetyLevel.SAFE,
            passed=True,
            checks_performed=["Research goal alignment", "Content safety"],
            timestamp="2025-01-18T10:00:00Z"
        )
        
        assert safety_check.id == "sc_001"
        assert safety_check.target_type == "hypothesis"
        assert safety_check.target_id == "hyp_001"
        assert safety_check.safety_level == SafetyLevel.SAFE
        assert safety_check.passed is True
        assert len(safety_check.checks_performed) == 2
        assert safety_check.timestamp == "2025-01-18T10:00:00Z"
    
    def test_create_safety_check_with_violations(self):
        """Test creating SafetyCheck with violations."""
        safety_check = SafetyCheck(
            id="sc_002",
            target_type="hypothesis",
            target_id="hyp_002",
            safety_level=SafetyLevel.CONCERNING,
            passed=False,
            checks_performed=["Research goal alignment", "Content safety", "Ethical considerations"],
            violations=["Hypothesis involves dangerous chemical synthesis"],
            recommendations=["Consider alternative synthesis pathways", "Add safety protocols"],
            timestamp="2025-01-18T10:05:00Z"
        )
        
        assert safety_check.safety_level == SafetyLevel.CONCERNING
        assert safety_check.passed is False
        assert len(safety_check.violations) == 1
        assert "dangerous chemical synthesis" in safety_check.violations[0]
        assert len(safety_check.recommendations) == 2
    
    def test_create_safety_check_blocked(self):
        """Test creating SafetyCheck for blocked content."""
        safety_check = SafetyCheck(
            id="sc_003",
            target_type="hypothesis",
            target_id="hyp_003",
            safety_level=SafetyLevel.BLOCKED,
            passed=False,
            checks_performed=["Research goal alignment"],
            violations=["Hypothesis directly violates research goal constraints"],
            category=SafetyCategory.GOAL_VIOLATION,
            timestamp="2025-01-18T10:10:00Z"
        )
        
        assert safety_check.safety_level == SafetyLevel.BLOCKED
        assert safety_check.passed is False
        assert safety_check.category == SafetyCategory.GOAL_VIOLATION
        assert len(safety_check.violations) == 1
    
    def test_safety_level_enum_values(self):
        """Test SafetyLevel enum values."""
        assert SafetyLevel.SAFE.value == "safe"
        assert SafetyLevel.CONCERNING.value == "concerning"
        assert SafetyLevel.BLOCKED.value == "blocked"
    
    def test_safety_category_enum_values(self):
        """Test SafetyCategory enum values."""
        assert SafetyCategory.CONTENT_SAFETY.value == "content_safety"
        assert SafetyCategory.GOAL_VIOLATION.value == "goal_violation"
        assert SafetyCategory.ETHICAL_CONCERN.value == "ethical_concern"
        assert SafetyCategory.RESOURCE_MISUSE.value == "resource_misuse"
    
    def test_safety_check_with_metadata(self):
        """Test creating SafetyCheck with metadata."""
        safety_check = SafetyCheck(
            id="sc_004",
            target_type="task",
            target_id="task_001",
            safety_level=SafetyLevel.SAFE,
            passed=True,
            checks_performed=["Task validation", "Resource check"],
            timestamp="2025-01-18T10:15:00Z",
            metadata={"trust_level": "high", "auto_approved": True}
        )
        
        assert safety_check.metadata is not None
        assert safety_check.metadata["trust_level"] == "high"
        assert safety_check.metadata["auto_approved"] is True


def test_safety_check_baml_schema_exists():
    """Test that the SafetyCheck schema is properly defined in BAML."""
    # Read the BAML file to verify schema exists
    import os
    baml_path = os.path.join(os.path.dirname(__file__), "../../baml_src/models.baml")
    
    with open(baml_path, 'r') as f:
        content = f.read()
    
    # Verify SafetyLevel enum exists
    assert "enum SafetyLevel {" in content
    assert "safe" in content
    assert "concerning" in content
    assert "blocked" in content
    
    # Verify SafetyCategory enum exists
    assert "enum SafetyCategory {" in content
    assert "content_safety" in content
    assert "goal_violation" in content
    assert "ethical_concern" in content
    assert "resource_misuse" in content
    
    # Verify SafetyCheck class exists
    assert "class SafetyCheck {" in content
    assert 'id string @description("Unique identifier for the safety check")' in content
    assert 'safety_level SafetyLevel @description("Overall safety assessment level")' in content
    assert 'passed bool @description("Whether the item passed safety checks")' in content