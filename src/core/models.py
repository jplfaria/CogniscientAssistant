"""Core data models for AI Co-Scientist."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
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