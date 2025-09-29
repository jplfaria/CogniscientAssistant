"""Core data models for AI Co-Scientist."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, field_serializer


def utcnow() -> datetime:
    """Get current UTC time with timezone info."""
    return datetime.now(timezone.utc)


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
    REFLECT_ON_HYPOTHESIS = "reflect_on_hypothesis"
    RANK_HYPOTHESES = "rank_hypotheses"
    EVOLVE_HYPOTHESIS = "evolve_hypothesis"
    FIND_SIMILAR_HYPOTHESES = "find_similar_hypotheses"
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
    created_at: datetime = Field(default_factory=utcnow)
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
        self.assigned_at = utcnow()
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
        self.completed_at = utcnow()
        self.state = TaskState.COMPLETED
    
    def fail(self, error: str) -> None:
        """Mark task as failed with error.
        
        Args:
            error: Error message
        """
        self.error = error
        self.completed_at = utcnow()
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
    created_at: datetime = Field(default_factory=utcnow)
    
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


class ReviewType(str, Enum):
    """Types of reviews that can be performed on hypotheses."""
    
    INITIAL = "initial"
    FULL = "full"
    DEEP_VERIFICATION = "deep_verification"
    OBSERVATION = "observation"
    SIMULATION = "simulation"
    TOURNAMENT = "tournament"


class ReviewDecision(str, Enum):
    """Possible review decisions."""
    
    ACCEPT = "accept"
    REJECT = "reject"
    REVISE = "revise"


class ReviewScores(BaseModel):
    """Scoring dimensions for hypothesis reviews."""
    
    correctness: float = Field(ge=0.0, le=1.0)
    quality: float = Field(ge=0.0, le=1.0)
    novelty: float = Field(ge=0.0, le=1.0)
    safety: float = Field(ge=0.0, le=1.0)
    feasibility: float = Field(ge=0.0, le=1.0)
    
    def average_score(self) -> float:
        """Calculate the average of all scores."""
        return (
            self.correctness + 
            self.quality + 
            self.novelty + 
            self.safety + 
            self.feasibility
        ) / 5


class AssumptionDecomposition(BaseModel):
    """Decomposition of assumptions for deep verification reviews."""
    
    assumption: str
    validity: str = Field(pattern="^(valid|questionable|invalid)$")
    evidence: str
    criticality: str = Field(pattern="^(fundamental|peripheral)$")


class FailurePoint(BaseModel):
    """Potential failure point in a simulated mechanism."""
    
    step: str
    probability: float = Field(ge=0.0, le=1.0)
    impact: str


class SimulationResults(BaseModel):
    """Results from simulating a hypothesis mechanism."""
    
    mechanism_steps: List[str] = Field(min_length=1)
    failure_points: List[FailurePoint]
    predicted_outcomes: List[str] = Field(min_length=1)


class Review(BaseModel):
    """Review of a hypothesis by an agent."""
    
    id: UUID = Field(default_factory=uuid4)
    hypothesis_id: UUID
    reviewer_agent_id: str
    review_type: ReviewType
    decision: ReviewDecision
    scores: ReviewScores
    
    # Narrative components
    narrative_feedback: str
    key_strengths: List[str] = Field(min_length=1)
    key_weaknesses: List[str] = Field(min_length=1)
    improvement_suggestions: List[str] = Field(min_length=1)
    confidence_level: str = Field(pattern="^(high|medium|low)$")
    
    # Optional review-type specific data
    assumption_decomposition: Optional[List[AssumptionDecomposition]] = None
    simulation_results: Optional[SimulationResults] = None
    literature_citations: Optional[List[Citation]] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=utcnow)
    time_spent_seconds: Optional[float] = Field(default=None, ge=0)
    
    model_config = ConfigDict()
    
    @field_serializer("id", "hypothesis_id")
    def serialize_uuid(self, value: UUID) -> str:
        """Serialize UUID to string."""
        return str(value)
    
    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        """Serialize datetime to ISO format string."""
        return value.isoformat()
    
    @field_validator("assumption_decomposition")
    @classmethod
    def validate_assumption_decomposition(
        cls, v: Optional[List[AssumptionDecomposition]], info
    ) -> Optional[List[AssumptionDecomposition]]:
        """Ensure assumption decomposition is provided for deep verification reviews."""
        review_type = info.data.get("review_type")
        if review_type == ReviewType.DEEP_VERIFICATION and not v:
            raise ValueError("Deep verification reviews must include assumption decomposition")
        return v
    
    @field_validator("simulation_results")
    @classmethod 
    def validate_simulation_results(
        cls, v: Optional[SimulationResults], info
    ) -> Optional[SimulationResults]:
        """Ensure simulation results are provided for simulation reviews."""
        review_type = info.data.get("review_type")
        if review_type == ReviewType.SIMULATION and not v:
            raise ValueError("Simulation reviews must include simulation results")
        return v


class ResearchGoal(BaseModel):
    """Research goal that guides hypothesis generation."""
    
    id: str = Field(default_factory=lambda: f"rg_{uuid4().hex[:8]}")
    description: str = Field(min_length=10)
    constraints: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: Optional[datetime] = None
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Ensure description is meaningful."""
        if len(v.strip()) < 10:
            raise ValueError("Description must be at least 10 characters")
        return v.strip()
    
    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        """Serialize datetime to ISO format string."""
        return value.isoformat() if value else None
    
    def update(self) -> None:
        """Update the timestamp when goal is modified."""
        self.updated_at = utcnow()


class Paper(BaseModel):
    """Scientific paper model for literature context."""

    id: str = Field(default_factory=lambda: f"paper_{uuid4().hex[:8]}")
    title: str = Field(min_length=5)
    abstract: str = Field(default="")
    authors: List[str] = Field(default_factory=list)
    journal: Optional[str] = None
    year: Optional[int] = Field(default=None, ge=1900, le=2100)
    doi: Optional[str] = None
    url: Optional[str] = None
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)

    # Content analysis fields
    keywords: List[str] = Field(default_factory=list)
    methodology_type: Optional[str] = None
    research_domain: Optional[str] = None

    # Metadata
    retrieved_at: datetime = Field(default_factory=utcnow)
    source: Optional[str] = Field(default="web_search")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Ensure title is meaningful."""
        if len(v.strip()) < 5:
            raise ValueError("Title must be at least 5 characters")
        return v.strip()

    @field_serializer("retrieved_at")
    def serialize_retrieved_at(self, value: datetime) -> str:
        """Serialize datetime to ISO format string."""
        return value.isoformat()

    def get_citation(self) -> Citation:
        """Convert paper to citation format.

        Returns:
            Citation object for this paper
        """
        return Citation(
            authors=self.authors or ["Unknown Author"],
            title=self.title,
            journal=self.journal,
            year=self.year or 2024,
            doi=self.doi,
            url=self.url
        )


class MemoryEntry(BaseModel):
    """Memory entry model for context memory system."""

    id: str = Field(default_factory=lambda: f"mem_{uuid4().hex[:8]}")
    entry_type: str = Field(description="Type of memory entry (hypothesis, task, result, etc.)")
    content: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utcnow)
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0)

    # Context tags for filtering
    tags: List[str] = Field(default_factory=list)
    iteration_number: Optional[int] = None
    research_phase: Optional[str] = None

    @field_serializer("timestamp")
    def serialize_timestamp(self, value: datetime) -> str:
        """Serialize datetime to ISO format string."""
        return value.isoformat()

    def is_recent(self, hours: int = 24) -> bool:
        """Check if memory entry is recent.

        Args:
            hours: Number of hours to consider recent

        Returns:
            True if entry is within the specified hours
        """
        from datetime import timedelta
        cutoff = utcnow() - timedelta(hours=hours)
        return self.timestamp > cutoff

    def matches_context(self, context: str, agent_type: str = None) -> float:
        """Calculate relevance to given context.

        Args:
            context: Context string to match against
            agent_type: Optional agent type for context-specific matching

        Returns:
            Relevance score between 0.0 and 1.0
        """
        # Simple keyword matching implementation
        context_lower = context.lower()
        content_str = str(self.content).lower()

        # Base relevance score
        relevance = 0.0

        # Check content similarity
        context_words = set(context_lower.split())
        content_words = set(content_str.split())
        if context_words and content_words:
            overlap = len(context_words & content_words)
            relevance += overlap / len(context_words | content_words)

        # Boost for agent type match
        if agent_type and self.agent_id and agent_type.lower() in self.agent_id.lower():
            relevance *= 1.2

        # Boost for recent entries
        if self.is_recent(6):  # Recent within 6 hours
            relevance *= 1.1

        return min(relevance, 1.0)