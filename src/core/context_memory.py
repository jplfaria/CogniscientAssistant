"""Context Memory implementation for persistent state management."""
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Literal
from dataclasses import dataclass, asdict
import logging
import os
import uuid

logger = logging.getLogger(__name__)


@dataclass
class StateUpdate:
    """State update from Supervisor Agent."""
    timestamp: datetime
    update_type: Literal["periodic", "checkpoint", "critical"]
    system_statistics: Dict[str, Any]
    orchestration_state: Dict[str, Any]
    checkpoint_data: Optional[Dict[str, Any]] = None


@dataclass
class AgentOutput:
    """Output from a specialized agent."""
    agent_type: str
    task_id: str
    timestamp: datetime
    results: Dict[str, Any]
    state_data: Optional[Dict[str, Any]] = None


@dataclass
class MetaReviewStorage:
    """Meta-review data for storage."""
    iteration_number: int
    timestamp: datetime
    critique: Dict[str, Any]
    research_overview: Dict[str, Any]


@dataclass
class StorageResult:
    """Result of a storage operation."""
    success: bool
    storage_path: Optional[Path] = None
    error: Optional[str] = None


@dataclass
class RetrievedState:
    """Retrieved state data."""
    request_type: str
    timestamp_range: Optional[tuple] = None
    content: Dict[str, Any] = None


@dataclass
class FeedbackData:
    """Retrieved feedback data."""
    iteration_requested: int
    agent_type: Optional[str] = None
    feedback_content: Dict[str, Any] = None


@dataclass
class RecoveryState:
    """Recovery state from checkpoint."""
    checkpoint_timestamp: datetime
    system_configuration: Dict[str, Any]
    active_tasks: List[Dict[str, Any]]
    completed_work: Dict[str, Any]
    resume_points: Dict[str, Any]
    data_integrity: Dict[str, Any]


class ContextMemory:
    """
    Persistent state management for the AI Co-Scientist system.
    
    Provides storage, retrieval, and management of system state across
    iterations, supporting recovery, feedback loops, and performance tracking.
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        retention_days: int = 30,
        checkpoint_interval_minutes: int = 5,
        max_storage_gb: int = 50
    ):
        """
        Initialize ContextMemory with configuration.
        
        Args:
            storage_path: Base path for storage (default: .aicoscientist/context)
            retention_days: Days to retain active data before archival
            checkpoint_interval_minutes: Minutes between automatic checkpoints
            max_storage_gb: Maximum storage size in gigabytes
        """
        self.storage_path = storage_path or Path(".aicoscientist/context")
        self.retention_days = retention_days
        self.checkpoint_interval_minutes = checkpoint_interval_minutes
        self.max_storage_gb = max_storage_gb
        self.is_initialized = False
        
        # Initialize indices for efficient access
        self._temporal_index: Dict[datetime, Path] = {}
        self._component_index: Dict[str, List[Path]] = {}
        self._hypothesis_index: Dict[str, List[Path]] = {}
        self._pattern_index: Dict[str, List[Path]] = {}
        self._performance_index: Dict[str, List[Path]] = {}
        
        # Create directory structure
        self._initialize_storage()
        
        # Load existing configuration if present
        self._load_configuration()
        
    def _initialize_storage(self):
        """Create required directory structure."""
        try:
            # Validate write permissions
            if self.storage_path.exists() and not os.access(self.storage_path, os.W_OK):
                raise PermissionError(f"No write permission for {self.storage_path}")
            elif not self.storage_path.exists():
                # Check parent directory permissions
                parent = self.storage_path.parent
                if parent.exists() and not os.access(parent, os.W_OK):
                    raise PermissionError(f"No write permission for {parent}")
            
            # Create directory structure
            directories = [
                self.storage_path / "iterations",
                self.storage_path / "checkpoints", 
                self.storage_path / "aggregates",
                self.storage_path / "configuration"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                
            logger.info(f"Initialized storage structure at {self.storage_path}")
            
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"Failed to initialize storage: {e}")
            raise
    
    def _load_configuration(self):
        """Load existing configuration from storage."""
        config_file = self.storage_path / "configuration" / "system_config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    
                # Update configuration from stored values
                self.retention_days = config.get('retention_days', self.retention_days)
                self.checkpoint_interval_minutes = config.get(
                    'checkpoint_interval_minutes', 
                    self.checkpoint_interval_minutes
                )
                self.max_storage_gb = config.get('max_storage_gb', self.max_storage_gb)
                
                logger.info("Loaded existing configuration from storage")
                
            except Exception as e:
                logger.warning(f"Failed to load configuration: {e}")
        else:
            # Save current configuration
            self._save_configuration()
    
    def _save_configuration(self):
        """Save current configuration to storage."""
        config_file = self.storage_path / "configuration" / "system_config.json"
        
        config = {
            'retention_days': self.retention_days,
            'checkpoint_interval_minutes': self.checkpoint_interval_minutes,
            'max_storage_gb': self.max_storage_gb,
            'created_at': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info("Saved configuration to storage")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    async def initialize(self):
        """
        Perform async initialization operations.
        
        This includes loading indices, validating storage integrity,
        and preparing for operations.
        """
        try:
            # Load existing indices
            await self._load_indices()
            
            # Validate storage integrity
            await self._validate_storage_integrity()
            
            # Initialize background tasks if needed
            self.is_initialized = True
            
            logger.info("ContextMemory initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize ContextMemory: {e}")
            raise
    
    async def _load_indices(self):
        """Load indices from storage for fast access."""
        try:
            # Scan iterations directory for existing state files
            iterations_dir = self.storage_path / "iterations"
            if iterations_dir.exists():
                for iteration_dir in iterations_dir.iterdir():
                    if iteration_dir.is_dir():
                        # Load system state files (both old and new format)
                        # Old format: system_state.json
                        old_state_file = iteration_dir / "system_state.json"
                        if old_state_file.exists():
                            with open(old_state_file, 'r') as f:
                                data = json.load(f)
                                timestamp = datetime.fromisoformat(data["timestamp"])
                                self._temporal_index[timestamp] = old_state_file
                        
                        # New format: system_state_*.json
                        for state_file in iteration_dir.glob("system_state_*.json"):
                            with open(state_file, 'r') as f:
                                data = json.load(f)
                                timestamp = datetime.fromisoformat(data["timestamp"])
                                self._temporal_index[timestamp] = state_file
                        
                        # Load agent outputs
                        agent_outputs_dir = iteration_dir / "agent_outputs"
                        if agent_outputs_dir.exists():
                            for output_file in agent_outputs_dir.glob("*.json"):
                                with open(output_file, 'r') as f:
                                    data = json.load(f)
                                    agent_type = data["agent_type"]
                                    if agent_type not in self._component_index:
                                        self._component_index[agent_type] = []
                                    self._component_index[agent_type].append(output_file)
            
            logger.info(f"Loaded {len(self._temporal_index)} temporal entries from storage")
            
        except Exception as e:
            logger.error(f"Failed to load indices: {e}")
    
    async def _validate_storage_integrity(self):
        """Validate storage structure and data integrity."""
        # Implementation will be added when we implement storage operations  
        pass
    
    async def store_state_update(self, state_update: StateUpdate) -> StorageResult:
        """Store a state update from the Supervisor Agent."""
        try:
            # Determine iteration directory
            current_iteration = self._get_current_iteration()
            iteration_dir = self.storage_path / "iterations" / current_iteration
            iteration_dir.mkdir(exist_ok=True)
            
            # Create unique filename for concurrent writes
            timestamp_str = state_update.timestamp.strftime('%Y%m%d_%H%M%S_%f')
            state_file = iteration_dir / f"system_state_{timestamp_str}.json"
            
            state_data = {
                "timestamp": state_update.timestamp.isoformat(),
                "update_type": state_update.update_type,
                "system_statistics": state_update.system_statistics,
                "orchestration_state": state_update.orchestration_state,
                "checkpoint_data": state_update.checkpoint_data
            }
            
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            # Update indices
            self._temporal_index[state_update.timestamp] = state_file
            
            logger.info(f"Stored state update in {state_file}")
            return StorageResult(success=True, storage_path=state_file)
            
        except Exception as e:
            logger.error(f"Failed to store state update: {e}")
            return StorageResult(success=False, error=str(e))
    
    async def store_agent_output(self, agent_output: AgentOutput) -> StorageResult:
        """Store output from a specialized agent."""
        try:
            # Determine iteration and agent directory
            current_iteration = self._get_current_iteration()
            agent_dir = self.storage_path / "iterations" / current_iteration / "agent_outputs"
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            # Create unique filename
            filename = f"{agent_output.agent_type}_{agent_output.task_id}_{agent_output.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            output_file = agent_dir / filename
            
            # Store agent output
            output_data = {
                "agent_type": agent_output.agent_type,
                "task_id": agent_output.task_id,
                "timestamp": agent_output.timestamp.isoformat(),
                "results": agent_output.results,
                "state_data": agent_output.state_data
            }
            
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            # Update indices
            if agent_output.agent_type not in self._component_index:
                self._component_index[agent_output.agent_type] = []
            self._component_index[agent_output.agent_type].append(output_file)
            
            logger.info(f"Stored agent output in {output_file}")
            return StorageResult(success=True, storage_path=output_file)
            
        except Exception as e:
            logger.error(f"Failed to store agent output: {e}")
            return StorageResult(success=False, error=str(e))
    
    async def store_meta_review(self, meta_review: MetaReviewStorage) -> StorageResult:
        """Store meta-review data."""
        try:
            # Store in the specific iteration directory
            iteration_name = f"iteration_{meta_review.iteration_number:03d}"
            iteration_dir = self.storage_path / "iterations" / iteration_name
            iteration_dir.mkdir(exist_ok=True)
            
            # Store meta review
            review_file = iteration_dir / "meta_review.json"
            review_data = {
                "iteration_number": meta_review.iteration_number,
                "timestamp": meta_review.timestamp.isoformat(),
                "critique": meta_review.critique,
                "research_overview": meta_review.research_overview
            }
            
            with open(review_file, 'w') as f:
                json.dump(review_data, f, indent=2)
            
            logger.info(f"Stored meta-review in {review_file}")
            return StorageResult(success=True, storage_path=review_file)
            
        except Exception as e:
            logger.error(f"Failed to store meta-review: {e}")
            return StorageResult(success=False, error=str(e))
    
    async def retrieve_state(self, request_type: str = "latest") -> Optional[RetrievedState]:
        """Retrieve system state based on request type."""
        try:
            if request_type == "latest":
                # Find the most recent system state
                latest_state = None
                latest_time = None
                
                for timestamp, path in sorted(self._temporal_index.items(), reverse=True):
                    if path.name.startswith("system_state"):
                        with open(path, 'r') as f:
                            state_data = json.load(f)
                            latest_state = state_data
                            latest_time = timestamp
                            break
                
                if latest_state:
                    # Merge statistics into system_state for backward compatibility
                    system_state = latest_state["orchestration_state"].copy()
                    system_state["tournament_progress"] = latest_state["system_statistics"].get("tournament_progress")
                    
                    return RetrievedState(
                        request_type=request_type,
                        content={
                            "system_state": system_state,
                            "statistics": latest_state["system_statistics"],
                            "timestamp": latest_state["timestamp"]
                        }
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve state: {e}")
            return None
    
    async def retrieve_feedback(self, iteration_requested: int, agent_type: Optional[str] = None) -> Optional[FeedbackData]:
        """Retrieve feedback for a specific iteration."""
        try:
            iteration_name = f"iteration_{iteration_requested:03d}"
            review_file = self.storage_path / "iterations" / iteration_name / "meta_review.json"
            
            if review_file.exists():
                with open(review_file, 'r') as f:
                    review_data = json.load(f)
                
                feedback_content = {
                    "general_recommendations": review_data["critique"]["common_patterns"],
                    "agent_specific": review_data["critique"]["agent_feedback"],
                    "priority_improvements": review_data["research_overview"]["next_priorities"],
                    "success_patterns": []
                }
                
                return FeedbackData(
                    iteration_requested=iteration_requested,
                    agent_type=agent_type,
                    feedback_content=feedback_content
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve feedback: {e}")
            return None
    
    async def create_checkpoint(self, state_update: StateUpdate) -> Optional[str]:
        """Create a recovery checkpoint."""
        try:
            # Generate checkpoint ID
            checkpoint_id = f"ckpt_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            checkpoint_dir = self.storage_path / "checkpoints" / checkpoint_id
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            
            # Store checkpoint data
            checkpoint_file = checkpoint_dir / "checkpoint.json"
            checkpoint_data = {
                "checkpoint_id": checkpoint_id,
                "timestamp": state_update.timestamp.isoformat(),
                "system_statistics": state_update.system_statistics,
                "orchestration_state": state_update.orchestration_state,
                "checkpoint_data": state_update.checkpoint_data,
                "created_at": datetime.now().isoformat()
            }
            
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            logger.info(f"Created checkpoint {checkpoint_id}")
            return checkpoint_id
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            return None
    
    async def recover_from_checkpoint(self, checkpoint_id: str) -> Optional[RecoveryState]:
        """Recover system state from a checkpoint."""
        try:
            checkpoint_file = self.storage_path / "checkpoints" / checkpoint_id / "checkpoint.json"
            
            if checkpoint_file.exists():
                with open(checkpoint_file, 'r') as f:
                    checkpoint_data = json.load(f)
                
                return RecoveryState(
                    checkpoint_timestamp=datetime.fromisoformat(checkpoint_data["timestamp"]),
                    system_configuration=checkpoint_data["orchestration_state"],
                    active_tasks=checkpoint_data["checkpoint_data"]["in_flight_tasks"],
                    completed_work={"hypotheses": checkpoint_data["system_statistics"]["total_hypotheses"]},
                    resume_points={},
                    data_integrity={"valid": True}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to recover from checkpoint: {e}")
            return None
    
    def _get_current_iteration(self) -> str:
        """Get the current iteration name."""
        # For now, use a simple incremental approach
        iterations_dir = self.storage_path / "iterations"
        existing_iterations = [d for d in iterations_dir.iterdir() if d.is_dir() and d.name.startswith("iteration_")]
        
        if not existing_iterations:
            return "iteration_001"
        
        # Find the highest iteration number
        latest_num = max(int(d.name.split("_")[1]) for d in existing_iterations)
        return f"iteration_{latest_num:03d}"