"""Unit tests for safety framework models."""

from datetime import datetime, timezone
import hashlib

import pytest

from src.core.safety import (
    SafetyLevel,
    SafetyFlag,
    SafetyCheck,
    PatternAlert,
    PatternMonitoringResult
)


class TestSafetyLevel:
    """Test SafetyLevel enum."""
    
    def test_safety_level_values(self):
        """Test that SafetyLevel has correct values."""
        assert SafetyLevel.SAFE.value == "safe"
        assert SafetyLevel.UNSAFE.value == "unsafe"
        assert SafetyLevel.REVIEW_REQUIRED.value == "review_required"
    
    def test_safety_level_comparison(self):
        """Test that SafetyLevel values can be compared."""
        assert SafetyLevel.SAFE == SafetyLevel.SAFE
        assert SafetyLevel.SAFE != SafetyLevel.UNSAFE
        assert SafetyLevel.UNSAFE != SafetyLevel.REVIEW_REQUIRED


class TestSafetyFlag:
    """Test SafetyFlag dataclass."""
    
    def test_safety_flag_creation(self):
        """Test creating a SafetyFlag."""
        flag = SafetyFlag(
            flag_type="procedure_risk",
            description="Risk of harmful procedure",
            severity="high",
            mitigation_suggested="Add safety protocols"
        )
        
        assert flag.flag_type == "procedure_risk"
        assert flag.description == "Risk of harmful procedure"
        assert flag.severity == "high"
        assert flag.mitigation_suggested == "Add safety protocols"
    
    def test_safety_flag_without_mitigation(self):
        """Test creating a SafetyFlag without mitigation."""
        flag = SafetyFlag(
            flag_type="outcome_risk",
            description="Potential harmful outcome",
            severity="medium"
        )
        
        assert flag.mitigation_suggested is None
    
    def test_safety_flag_equality(self):
        """Test SafetyFlag equality."""
        flag1 = SafetyFlag("dual_use", "Dual use concern", "low")
        flag2 = SafetyFlag("dual_use", "Dual use concern", "low")
        flag3 = SafetyFlag("dual_use", "Different concern", "low")
        
        assert flag1 == flag2
        assert flag1 != flag3


class TestSafetyCheck:
    """Test SafetyCheck dataclass."""
    
    def test_safety_check_creation(self):
        """Test creating a SafetyCheck."""
        check = SafetyCheck(
            decision=SafetyLevel.SAFE,
            safety_score=0.95,
            reasoning="No safety concerns identified"
        )
        
        assert check.decision == SafetyLevel.SAFE
        assert check.safety_score == 0.95
        assert check.reasoning == "No safety concerns identified"
        assert check.safety_flags == []
        assert check.evaluator_version == "1.0"
        assert check.confidence == 0.0
        assert check.input_hash is None
        assert check.filtering_applied is False
        assert isinstance(check.timestamp, datetime)
        assert check.timestamp.tzinfo is not None
    
    def test_safety_check_with_all_fields(self):
        """Test creating a SafetyCheck with all fields."""
        test_hash = hashlib.sha256(b"test input").hexdigest()
        check = SafetyCheck(
            decision=SafetyLevel.REVIEW_REQUIRED,
            safety_score=0.6,
            reasoning="Some concerns require expert review",
            confidence=0.85,
            input_hash=test_hash,
            filtering_applied=True
        )
        
        assert check.confidence == 0.85
        assert check.input_hash == test_hash
        assert check.filtering_applied is True
    
    def test_add_flag(self):
        """Test adding flags to a SafetyCheck."""
        check = SafetyCheck(
            decision=SafetyLevel.UNSAFE,
            safety_score=0.2,
            reasoning="Multiple safety concerns"
        )
        
        check.add_flag(
            flag_type="procedure_risk",
            description="Involves dangerous chemicals",
            severity="high",
            mitigation="Use proper PPE and ventilation"
        )
        
        check.add_flag(
            flag_type="outcome_risk",
            description="Could produce toxic byproducts",
            severity="high"
        )
        
        assert len(check.safety_flags) == 2
        assert check.safety_flags[0].flag_type == "procedure_risk"
        assert check.safety_flags[0].mitigation_suggested == "Use proper PPE and ventilation"
        assert check.safety_flags[1].flag_type == "outcome_risk"
        assert check.safety_flags[1].mitigation_suggested is None
    
    def test_has_high_severity_flags(self):
        """Test checking for high severity flags."""
        check = SafetyCheck(
            decision=SafetyLevel.REVIEW_REQUIRED,
            safety_score=0.5,
            reasoning="Mixed severity concerns"
        )
        
        # No flags initially
        assert not check.has_high_severity_flags()
        
        # Add low severity flag
        check.add_flag("dual_use", "Minor dual use concern", "low")
        assert not check.has_high_severity_flags()
        
        # Add medium severity flag
        check.add_flag("outcome_risk", "Moderate risk", "medium")
        assert not check.has_high_severity_flags()
        
        # Add high severity flag
        check.add_flag("procedure_risk", "Serious risk", "high")
        assert check.has_high_severity_flags()
    
    def test_get_flags_by_type(self):
        """Test filtering flags by type."""
        check = SafetyCheck(
            decision=SafetyLevel.UNSAFE,
            safety_score=0.1,
            reasoning="Multiple risks"
        )
        
        # Add various flags
        check.add_flag("procedure_risk", "Risk 1", "high")
        check.add_flag("outcome_risk", "Risk 2", "medium")
        check.add_flag("procedure_risk", "Risk 3", "low")
        check.add_flag("dual_use", "Risk 4", "high")
        
        # Get procedure_risk flags
        procedure_flags = check.get_flags_by_type("procedure_risk")
        assert len(procedure_flags) == 2
        assert procedure_flags[0].description == "Risk 1"
        assert procedure_flags[1].description == "Risk 3"
        
        # Get outcome_risk flags
        outcome_flags = check.get_flags_by_type("outcome_risk")
        assert len(outcome_flags) == 1
        assert outcome_flags[0].description == "Risk 2"
        
        # Get non-existent type
        other_flags = check.get_flags_by_type("other_risk")
        assert len(other_flags) == 0
    
    def test_to_dict(self):
        """Test converting SafetyCheck to dictionary."""
        check = SafetyCheck(
            decision=SafetyLevel.REVIEW_REQUIRED,
            safety_score=0.7,
            reasoning="Needs review",
            confidence=0.9,
            input_hash="abc123",
            filtering_applied=True
        )
        
        check.add_flag("dual_use", "Dual use concern", "medium", "Monitor usage")
        
        result = check.to_dict()
        
        assert result["decision"] == "review_required"
        assert result["safety_score"] == 0.7
        assert result["reasoning"] == "Needs review"
        assert result["confidence"] == 0.9
        assert result["input_hash"] == "abc123"
        assert result["filtering_applied"] is True
        assert result["evaluator_version"] == "1.0"
        assert len(result["safety_flags"]) == 1
        assert result["safety_flags"][0]["flag_type"] == "dual_use"
        assert result["safety_flags"][0]["mitigation_suggested"] == "Monitor usage"
        assert "timestamp" in result
    
    def test_safety_check_immutability_of_flags(self):
        """Test that modifying returned flag lists doesn't affect original."""
        check = SafetyCheck(
            decision=SafetyLevel.SAFE,
            safety_score=0.9,
            reasoning="Safe"
        )
        
        check.add_flag("minor_concern", "Small issue", "low")
        
        # Get flags and modify the returned list
        flags = check.get_flags_by_type("minor_concern")
        original_length = len(flags)
        flags.append(SafetyFlag("fake", "fake", "high"))
        
        # Original should be unchanged
        assert len(check.safety_flags) == original_length
        assert len(check.get_flags_by_type("minor_concern")) == original_length


class TestPatternAlert:
    """Test PatternAlert enum."""
    
    def test_pattern_alert_values(self):
        """Test that PatternAlert has correct values."""
        assert PatternAlert.CONTINUE.value == "continue"
        assert PatternAlert.PAUSE_FOR_REVIEW.value == "pause_for_review"
        assert PatternAlert.TERMINATE.value == "terminate"


class TestPatternMonitoringResult:
    """Test PatternMonitoringResult dataclass."""
    
    def test_pattern_monitoring_result_creation(self):
        """Test creating a PatternMonitoringResult."""
        result = PatternMonitoringResult(
            alert_level=PatternAlert.PAUSE_FOR_REVIEW,
            patterns_detected=["boundary_testing", "sensitive_aggregation"],
            risk_score=0.75,
            reasoning="Multiple concerning patterns detected",
            recommended_action="Pause and review current research direction"
        )
        
        assert result.alert_level == PatternAlert.PAUSE_FOR_REVIEW
        assert len(result.patterns_detected) == 2
        assert "boundary_testing" in result.patterns_detected
        assert result.risk_score == 0.75
        assert result.reasoning == "Multiple concerning patterns detected"
        assert result.recommended_action == "Pause and review current research direction"
        assert isinstance(result.timestamp, datetime)
        assert result.timestamp.tzinfo is not None
    
    def test_pattern_monitoring_result_safe(self):
        """Test creating a safe PatternMonitoringResult."""
        result = PatternMonitoringResult(
            alert_level=PatternAlert.CONTINUE,
            patterns_detected=[],
            risk_score=0.05,
            reasoning="No concerning patterns detected",
            recommended_action="Continue with current research"
        )
        
        assert result.alert_level == PatternAlert.CONTINUE
        assert len(result.patterns_detected) == 0
        assert result.risk_score == 0.05
    
    def test_pattern_monitoring_result_critical(self):
        """Test creating a critical PatternMonitoringResult."""
        result = PatternMonitoringResult(
            alert_level=PatternAlert.TERMINATE,
            patterns_detected=["dangerous_convergence", "safety_bypass_attempt"],
            risk_score=0.95,
            reasoning="Critical safety violations detected",
            recommended_action="Immediately terminate this research thread"
        )
        
        assert result.alert_level == PatternAlert.TERMINATE
        assert len(result.patterns_detected) == 2
        assert result.risk_score == 0.95