"""Safety framework models and utilities for AI Co-Scientist."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


class SafetyLevel(str, Enum):
    """Safety assessment levels for research goals and hypotheses."""
    
    SAFE = "safe"                        # Clearly safe, no concerns
    UNSAFE = "unsafe"                    # Clearly unsafe, should be rejected
    REVIEW_REQUIRED = "review_required"  # Needs human expert review


@dataclass
class SafetyFlag:
    """Individual safety concern flag."""
    
    flag_type: str      # "procedure_risk", "outcome_risk", "dual_use", etc.
    description: str    # Detailed description of the concern
    severity: str       # "high", "medium", "low"
    mitigation_suggested: Optional[str] = None  # Suggested mitigation if applicable


@dataclass
class SafetyCheck:
    """Safety evaluation result for a research goal or hypothesis."""
    
    # Core fields
    decision: SafetyLevel  # SAFE, UNSAFE, or REVIEW_REQUIRED
    safety_score: float    # 0.0 to 1.0 (1.0 = completely safe)
    reasoning: str         # Explanation of the safety decision
    
    # Identified concerns
    safety_flags: List[SafetyFlag] = field(default_factory=list)
    
    # Metadata
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    evaluator_version: str = "1.0"
    confidence: float = 0.0  # 0.0 to 1.0 confidence in assessment
    
    # Context (for audit without storing sensitive content)
    input_hash: Optional[str] = None  # SHA-256 hash of evaluated content
    filtering_applied: bool = False   # Whether content was filtered/modified
    
    def add_flag(self, flag_type: str, description: str, severity: str, 
                 mitigation: Optional[str] = None) -> None:
        """Add a safety flag to this check.
        
        Args:
            flag_type: Type of safety concern
            description: Description of the concern
            severity: Severity level (high/medium/low)
            mitigation: Optional suggested mitigation
        """
        self.safety_flags.append(SafetyFlag(
            flag_type=flag_type,
            description=description,
            severity=severity,
            mitigation_suggested=mitigation
        ))
    
    def has_high_severity_flags(self) -> bool:
        """Check if any high severity flags are present."""
        return any(flag.severity == "high" for flag in self.safety_flags)
    
    def get_flags_by_type(self, flag_type: str) -> List[SafetyFlag]:
        """Get all flags of a specific type."""
        return [flag for flag in self.safety_flags if flag.flag_type == flag_type]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "decision": self.decision.value,
            "safety_score": self.safety_score,
            "reasoning": self.reasoning,
            "safety_flags": [
                {
                    "flag_type": flag.flag_type,
                    "description": flag.description,
                    "severity": flag.severity,
                    "mitigation_suggested": flag.mitigation_suggested
                }
                for flag in self.safety_flags
            ],
            "timestamp": self.timestamp.isoformat(),
            "evaluator_version": self.evaluator_version,
            "confidence": self.confidence,
            "input_hash": self.input_hash,
            "filtering_applied": self.filtering_applied
        }


class PatternAlert(str, Enum):
    """Alert types for pattern monitoring."""
    
    CONTINUE = "continue"              # Safe to continue
    PAUSE_FOR_REVIEW = "pause_for_review"  # Pause and request review
    TERMINATE = "terminate"            # Terminate current research thread


@dataclass
class PatternMonitoringResult:
    """Result from continuous pattern monitoring."""
    
    alert_level: PatternAlert
    patterns_detected: List[str]
    risk_score: float  # 0.0 to 1.0
    reasoning: str
    recommended_action: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))