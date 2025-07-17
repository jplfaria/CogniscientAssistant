"""Core data models for AI Co-Scientist."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, field_serializer


class TaskState(str, Enum):
    """Task execution states."""
    
    PENDING = "pending"
    ASSIGNED = "assigned"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(str, Enum):
    """Types of tasks in the system."""
    
    GENERATE_HYPOTHESIS = "generate_hypothesis"
    REVIEW_HYPOTHESIS = "review_hypothesis"
    RANK_HYPOTHESES = "rank_hypotheses"
    EVOLVE_HYPOTHESIS = "evolve_hypothesis"
    CALCULATE_PROXIMITY = "calculate_proximity"
    META_REVIEW = "meta_review"


class Task(BaseModel):
    """Task model for the queue system."""
    
    id: UUID = Field(default_factory=uuid4)
    task_type: TaskType
    priority: int = Field(gt=0, description="Priority must be positive, higher = more important")
    state: TaskState = Field(default=TaskState.PENDING)
    payload: Dict[str, Any] = Field(default_factory=dict)
    
    # Worker assignment
    assigned_to: Optional[str] = None
    
    # Results
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: int) -> int:
        """Ensure priority is positive."""
        if v <= 0:
            raise ValueError("Priority must be positive")
        return v
    
    def assign(self, worker_id: str) -> None:
        """Assign task to a worker.
        
        Args:
            worker_id: ID of the worker to assign to
            
        Raises:
            ValueError: If task is already assigned
        """
        if self.state != TaskState.PENDING:
            if self.assigned_to is not None:
                raise ValueError(f"Task already assigned to {self.assigned_to}")
            raise ValueError(f"Cannot assign task in state {self.state}")
        
        self.assigned_to = worker_id
        self.assigned_at = datetime.utcnow()
        self.state = TaskState.ASSIGNED
    
    def start_execution(self) -> None:
        """Mark task as executing.
        
        Raises:
            ValueError: If task is not assigned
        """
        if self.state != TaskState.ASSIGNED:
            raise ValueError(f"Cannot start execution for task in state {self.state}")
        
        self.state = TaskState.EXECUTING
    
    def complete(self, result: Dict[str, Any]) -> None:
        """Mark task as completed with result.
        
        Args:
            result: Task execution result
            
        Raises:
            ValueError: If task is not executing
        """
        if self.state != TaskState.EXECUTING:
            raise ValueError(f"Cannot complete task in state {self.state}")
        
        self.result = result
        self.completed_at = datetime.utcnow()
        self.state = TaskState.COMPLETED
    
    def fail(self, error: str) -> None:
        """Mark task as failed with error.
        
        Args:
            error: Error message
        """
        self.error = error
        self.completed_at = datetime.utcnow()
        self.state = TaskState.FAILED
    
    model_config = ConfigDict()
    
    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        """Serialize UUID to string."""
        return str(value)
    
    @field_serializer("created_at", "assigned_at", "completed_at")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        """Serialize datetime to ISO format string."""
        return value.isoformat() if value else None


class HypothesisCategory(str, Enum):
    """Categories of scientific hypotheses."""
    
    MECHANISTIC = "mechanistic"
    THERAPEUTIC = "therapeutic"
    DIAGNOSTIC = "diagnostic"
    BIOMARKER = "biomarker"
    METHODOLOGY = "methodology"
    OTHER = "other"


class Citation(BaseModel):
    """Scientific citation model."""
    
    authors: List[str] = Field(min_length=1)
    title: str
    journal: Optional[str] = None
    year: int = Field(ge=1900, le=2100)
    doi: Optional[str] = None
    url: Optional[str] = None
    
    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        """Ensure year is reasonable."""
        current_year = datetime.now().year
        if v < 1900 or v > current_year + 10:
            raise ValueError(f"Year {v} is outside reasonable range")
        return v


class ExperimentalProtocol(BaseModel):
    """Experimental protocol for testing a hypothesis."""
    
    objective: str
    methodology: str
    required_resources: List[str] = Field(min_length=1)
    timeline: str
    success_metrics: List[str] = Field(min_length=1)
    potential_challenges: List[str] = Field(min_length=1)
    safety_considerations: List[str] = Field(min_length=1)


class HypothesisSummary(BaseModel):
    """Human-readable summary of a hypothesis."""
    
    core_idea: str
    scientific_impact: str
    feasibility_assessment: str
    next_steps: List[str] = Field(min_length=1)


class Hypothesis(BaseModel):
    """Scientific hypothesis model."""
    
    id: UUID = Field(default_factory=uuid4)
    summary: str = Field(description="Concise one-sentence description")
    category: HypothesisCategory
    full_description: str
    novelty_claim: str
    assumptions: List[str] = Field(min_length=1)
    experimental_protocol: ExperimentalProtocol
    supporting_evidence: List[Citation]
    confidence_score: float = Field(ge=0.0, le=1.0)
    generation_method: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Optional fields for tracking
    elo_rating: Optional[float] = Field(default=1200.0, ge=0)
    review_count: int = Field(default=0, ge=0)
    evolution_count: int = Field(default=0, ge=0)
    
    model_config = ConfigDict()
    
    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        """Serialize UUID to string."""
        return str(value)
    
    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        """Serialize datetime to ISO format string."""
        return value.isoformat()
    
    @field_validator("assumptions")
    @classmethod
    def validate_assumptions(cls, v: List[str]) -> List[str]:
        """Ensure assumptions list is not empty."""
        if not v:
            raise ValueError("Assumptions list cannot be empty")
        return v
    
    def create_summary(self) -> HypothesisSummary:
        """Create a human-readable summary of this hypothesis."""
        return HypothesisSummary(
            core_idea=self.summary,
            scientific_impact=f"Category: {self.category.value}. {self.novelty_claim}",
            feasibility_assessment=f"Confidence: {self.confidence_score:.0%}. Timeline: {self.experimental_protocol.timeline}",
            next_steps=[
                f"Objective: {self.experimental_protocol.objective}",
                f"Resources needed: {', '.join(self.experimental_protocol.required_resources[:3])}",
                "Begin experimental validation"
            ]
        )