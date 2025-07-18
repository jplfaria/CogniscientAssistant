"""Safety framework models and utilities for AI Co-Scientist."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union


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
    metadata: Optional[Dict] = None   # Additional metadata (e.g., log_id)
    
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


@dataclass
class SafetyConfig:
    """Configuration for lightweight safety system."""
    
    enabled: bool = True
    trust_level: str = "standard"
    log_only_mode: bool = True
    log_directory: Union[Path, str] = Path(".aicoscientist/safety_logs")
    blocking_threshold: float = 0.95
    retention_days: int = 30
    
    def __post_init__(self):
        """Validate and normalize configuration values."""
        # Ensure log_directory is a Path object
        if isinstance(self.log_directory, str):
            self.log_directory = Path(self.log_directory)
        
        # Validate trust level
        valid_trust_levels = ["trusted", "standard", "restricted"]
        if self.trust_level not in valid_trust_levels:
            raise ValueError(f"trust_level must be one of {valid_trust_levels}, got {self.trust_level}")
        
        # Validate blocking threshold
        if not 0.0 <= self.blocking_threshold <= 1.0:
            raise ValueError(f"blocking_threshold must be between 0.0 and 1.0, got {self.blocking_threshold}")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "enabled": self.enabled,
            "trust_level": self.trust_level,
            "log_only_mode": self.log_only_mode,
            "log_directory": str(self.log_directory),
            "blocking_threshold": self.blocking_threshold,
            "retention_days": self.retention_days
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SafetyConfig":
        """Create SafetyConfig from dictionary."""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> "SafetyConfig":
        """Create SafetyConfig from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    def get_trust_config(self) -> Dict:
        """Get trust level configuration."""
        trust_configs = {
            "trusted": {
                "description": "Minimal logging, no blocking",
                "safety_checks": False,
                "logging_level": "minimal"
            },
            "standard": {
                "description": "Full logging, advisory warnings",
                "safety_checks": True,
                "logging_level": "detailed"
            },
            "restricted": {
                "description": "Enhanced monitoring, possible delays",
                "safety_checks": True,
                "logging_level": "verbose",
                "review_threshold": 0.5
            }
        }
        return trust_configs[self.trust_level]


@dataclass
class LogEntry:
    """Individual log entry for safety monitoring."""
    
    id: str
    timestamp: datetime
    event_type: str  # "goal_submission", "hypothesis_generation", "pattern_alert"
    content_hash: str
    metadata: Dict
    trust_level: str
    user_id: Optional[str] = None


@dataclass
class PatternReport:
    """Report of observed patterns in safety logs."""
    
    report_id: str
    period: str  # "daily", "weekly", "monthly"
    patterns_observed: List[Dict[str, Union[str, int]]]
    total_events: int
    event_counts: Dict[str, int]
    recommendations: str = "No specific recommendations"
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SafetyLogger:
    """Lightweight safety monitoring system."""
    
    def __init__(self, config: SafetyConfig):
        """Initialize the safety logger with configuration.
        
        Args:
            config: SafetyConfig instance with settings
        """
        self.config = config
        self.enabled = config.enabled
        self.trust_level = config.trust_level
        self.log_only = config.log_only_mode
        self.log_directory = config.log_directory
        
        # Create log directory if enabled
        if self.enabled and not self.log_directory.exists():
            self.log_directory.mkdir(parents=True, exist_ok=True)
    
    async def log_research_goal(self, goal: str, context: Dict) -> SafetyCheck:
        """Log research goal without evaluation.
        
        Args:
            goal: Research goal text
            context: Additional context (domain, user_role, etc.)
            
        Returns:
            SafetyCheck with SAFE decision and log metadata
        """
        if not self.enabled:
            return SafetyCheck(
                decision=SafetyLevel.SAFE,
                safety_score=1.0,
                reasoning="Safety logging disabled"
            )
        
        # Create log entry
        log_entry = await self._create_log_entry(goal, context, "goal_submission")
        
        # Write to disk
        await self._write_log_entry(log_entry)
        
        # Different reasoning based on trust level
        reasoning = self._get_reasoning_for_trust_level()
        
        return SafetyCheck(
            decision=SafetyLevel.SAFE,
            safety_score=1.0,
            reasoning=reasoning,
            metadata={"log_id": log_entry.id},
            input_hash=log_entry.content_hash
        )
    
    async def log_hypothesis(self, hypothesis_data: Dict) -> SafetyCheck:
        """Log generated hypothesis for pattern tracking.
        
        Args:
            hypothesis_data: Dictionary with hypothesis details
            
        Returns:
            SafetyCheck with logging confirmation
        """
        if not self.enabled:
            return SafetyCheck(
                decision=SafetyLevel.SAFE,
                safety_score=1.0,
                reasoning="Safety logging disabled"
            )
        
        # Extract content for hashing
        content = hypothesis_data.get("content", str(hypothesis_data))
        
        # Create log entry
        log_entry = await self._create_log_entry(
            content,
            hypothesis_data,
            "hypothesis_generation"
        )
        
        # Write to disk
        await self._write_log_entry(log_entry)
        
        return SafetyCheck(
            decision=SafetyLevel.SAFE,
            safety_score=1.0,
            reasoning="Hypothesis logged for pattern tracking",
            metadata={"log_id": log_entry.id}
        )
    
    async def _create_log_entry(self, content: str, context: Dict, 
                                event_type: str) -> LogEntry:
        """Create a log entry with hashed content.
        
        Args:
            content: Content to log (will be hashed)
            context: Additional metadata
            event_type: Type of event being logged
            
        Returns:
            LogEntry instance
        """
        import uuid
        
        log_id = str(uuid.uuid4())
        content_hash = await self._hash_content(content)
        
        return LogEntry(
            id=log_id,
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            content_hash=content_hash,
            metadata=context,
            trust_level=self.trust_level,
            user_id=context.get("user_id")
        )
    
    async def _hash_content(self, content: str) -> str:
        """Create SHA-256 hash of content for privacy.
        
        Args:
            content: Content to hash
            
        Returns:
            Hex string of SHA-256 hash
        """
        import hashlib
        
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    async def _write_log_entry(self, log_entry: LogEntry) -> None:
        """Write log entry to disk.
        
        Args:
            log_entry: LogEntry to write
        """
        # Create filename with date prefix for easy sorting
        filename = f"{log_entry.timestamp.strftime('%Y%m%d')}_{log_entry.id}.json"
        filepath = self.log_directory / filename
        
        # Convert to dict for JSON serialization
        entry_dict = {
            "id": log_entry.id,
            "timestamp": log_entry.timestamp.isoformat(),
            "event_type": log_entry.event_type,
            "content_hash": log_entry.content_hash,
            "metadata": log_entry.metadata,
            "trust_level": log_entry.trust_level,
            "user_id": log_entry.user_id
        }
        
        # Write to file
        with open(filepath, 'w') as f:
            json.dump(entry_dict, f, indent=2)
    
    async def generate_pattern_report(self, period: str) -> PatternReport:
        """Generate a pattern report for the specified period.
        
        Args:
            period: Report period ("daily", "weekly", "monthly")
            
        Returns:
            PatternReport with analysis
        """
        import uuid
        
        # Read all log files
        log_entries = await self._read_recent_logs(period)
        
        # Count events by type
        event_counts: Dict[str, int] = {}
        for entry in log_entries:
            event_type = entry.get("event_type", "unknown")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Identify patterns (simplified for now)
        patterns = []
        if event_counts:
            for event_type, count in event_counts.items():
                patterns.append({
                    "pattern_type": f"High frequency {event_type}",
                    "frequency": count,
                    "examples": []  # Would include log IDs in production
                })
        
        return PatternReport(
            report_id=str(uuid.uuid4()),
            period=period,
            patterns_observed=patterns,
            total_events=len(log_entries),
            event_counts=event_counts
        )
    
    async def _read_recent_logs(self, period: str) -> List[Dict]:
        """Read log entries for the specified period.
        
        Args:
            period: Time period to read
            
        Returns:
            List of log entry dictionaries
        """
        from datetime import timedelta
        
        # Determine time range
        now = datetime.now(timezone.utc)
        if period == "daily":
            start_time = now - timedelta(days=1)
        elif period == "weekly":
            start_time = now - timedelta(weeks=1)
        elif period == "monthly":
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(days=1)
        
        # Read log files
        entries = []
        for log_file in self.log_directory.glob("*.json"):
            try:
                with open(log_file, 'r') as f:
                    entry = json.load(f)
                    # Parse timestamp
                    entry_time = datetime.fromisoformat(entry["timestamp"])
                    if entry_time >= start_time:
                        entries.append(entry)
            except Exception:
                # Skip corrupted files
                continue
        
        return entries
    
    async def cleanup_old_logs(self) -> None:
        """Remove log files older than retention period."""
        from datetime import timedelta
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=self.config.retention_days)
        
        for log_file in self.log_directory.glob("*.json"):
            try:
                # Extract date from filename (YYYYMMDD_...)
                date_str = log_file.name.split('_')[0]
                file_date = datetime.strptime(date_str, '%Y%m%d')
                file_date = file_date.replace(tzinfo=timezone.utc)
                
                if file_date < cutoff_time:
                    log_file.unlink()
            except Exception:
                # Skip files that don't match expected format
                continue
    
    async def get_audit_trail(self, start_time: datetime, 
                              end_time: datetime) -> List[LogEntry]:
        """Get audit trail for a specific time period.
        
        Args:
            start_time: Start of period
            end_time: End of period
            
        Returns:
            List of LogEntry instances
        """
        entries = []
        
        for log_file in self.log_directory.glob("*.json"):
            try:
                with open(log_file, 'r') as f:
                    entry_dict = json.load(f)
                    
                # Parse timestamp
                entry_time = datetime.fromisoformat(entry_dict["timestamp"])
                
                if start_time <= entry_time <= end_time:
                    # Reconstruct LogEntry
                    entry = LogEntry(
                        id=entry_dict["id"],
                        timestamp=entry_time,
                        event_type=entry_dict["event_type"],
                        content_hash=entry_dict["content_hash"],
                        metadata=entry_dict["metadata"],
                        trust_level=entry_dict["trust_level"],
                        user_id=entry_dict.get("user_id")
                    )
                    entries.append(entry)
            except Exception:
                # Skip corrupted files
                continue
        
        # Sort by timestamp
        entries.sort(key=lambda x: x.timestamp)
        return entries
    
    def is_safety_check_needed(self) -> bool:
        """Determine if safety checks are needed based on configuration.
        
        Returns:
            True if safety checks should be performed
        """
        if not self.enabled:
            return False
        
        trust_config = self.config.get_trust_config()
        return trust_config.get("safety_checks", True)
    
    def _get_reasoning_for_trust_level(self) -> str:
        """Get appropriate reasoning message based on trust level.
        
        Returns:
            Reasoning string
        """
        if self.trust_level == "trusted":
            return "Minimal logging for trusted level"
        elif self.trust_level == "restricted":
            return "Enhanced monitoring for restricted level"
        else:
            return "Logged for monitoring"