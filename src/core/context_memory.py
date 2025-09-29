"""Context Memory implementation for persistent state management."""
import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Literal
from dataclasses import dataclass, asdict
import logging
import os
import uuid
import fcntl
import time

logger = logging.getLogger(__name__)


@dataclass
class StateUpdate:
    """State update from Supervisor Agent."""
    timestamp: datetime
    update_type: Literal["periodic", "checkpoint", "critical"]
    system_statistics: Dict[str, Any]
    orchestration_state: Dict[str, Any]
    checkpoint_data: Optional[Dict[str, Any]] = None
    writer_id: Optional[str] = None  # ID of the writing agent/component


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
    
    Includes a key-value store for flexible data storage needs.
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
        
        # Key-value store in-memory cache
        self._kv_cache: Dict[str, Any] = {}
        self._kv_dirty: Set[str] = set()  # Track modified keys for persistence
        
        # Checkpoint locking
        self._checkpoint_lock = asyncio.Lock()
        self._checkpoint_lock_file = None
        
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
                self.storage_path / "configuration",
                self.storage_path / "kv_store"  # Key-value store directory
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
            
            # Load key-value cache
            await self._load_kv_cache()
            
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
            # Check storage limit
            if not await self._check_storage_limit():
                logger.warning("Storage limit exceeded, cannot store state update")
                return StorageResult(success=False, error="Storage limit exceeded")
            # Use active iteration if available, otherwise current
            active_iter = await self.get_active_iteration()
            if active_iter is not None:
                current_iteration = f"iteration_{active_iter:03d}"
            else:
                current_iteration = self._get_current_iteration()
            
            iteration_dir = self.storage_path / "iterations" / current_iteration
            iteration_dir.mkdir(exist_ok=True)
            
            # Create unique filename for concurrent writes
            timestamp_str = state_update.timestamp.strftime('%Y%m%d_%H%M%S_%f')
            base_filename = f"system_state_{timestamp_str}"
            
            # Handle concurrent writes by adding a counter if file exists
            counter = 0
            state_file = iteration_dir / f"{base_filename}.json"
            while state_file.exists():
                counter += 1
                state_file = iteration_dir / f"{base_filename}_{counter}.json"
            
            state_data = {
                "timestamp": state_update.timestamp.isoformat(),
                "update_type": state_update.update_type,
                "system_statistics": state_update.system_statistics,
                "orchestration_state": state_update.orchestration_state,
                "checkpoint_data": state_update.checkpoint_data,
                "version": 1,  # Add version tracking
                "writer_id": state_update.writer_id or f"supervisor_{timestamp_str}"  # Use provided writer_id or generate one
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
            # Use active iteration if available, otherwise current
            active_iter = await self.get_active_iteration()
            if active_iter is not None:
                current_iteration = f"iteration_{active_iter:03d}"
            else:
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
                "state_data": agent_output.state_data,
                "version": 1,  # Add version tracking
                "writer_id": f"{agent_output.agent_type}_{agent_output.task_id}"  # Add writer identification
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
        """Create a recovery checkpoint with exclusive locking."""
        # Use asyncio lock for high-level coordination
        async with self._checkpoint_lock:
            try:
                # Create a lock file for process-level locking
                lock_file_path = self.storage_path / "checkpoints" / ".checkpoint.lock"
                lock_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Try to acquire file lock with timeout
                lock_acquired = False
                start_time = time.time()
                timeout_seconds = 30  # 30 second timeout as per spec
                
                while not lock_acquired and (time.time() - start_time) < timeout_seconds:
                    try:
                        lock_file = open(lock_file_path, 'w')
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        lock_acquired = True
                    except (IOError, OSError):
                        # Lock is held by another process, wait and retry
                        await asyncio.sleep(0.1)
                        if 'lock_file' in locals():
                            lock_file.close()
                
                if not lock_acquired:
                    logger.error("Failed to acquire checkpoint lock within timeout")
                    return None
                
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
                        "created_at": datetime.now().isoformat(),
                        "version": 1,  # Add version tracking
                        "writer_id": f"checkpoint_{checkpoint_id}"  # Add writer identification
                    }
                    
                    with open(checkpoint_file, 'w') as f:
                        json.dump(checkpoint_data, f, indent=2)
                    
                    # Update active iteration's checkpoint list
                    active_iter = await self.get_active_iteration()
                    if active_iter is not None:
                        iter_name = f"iteration_{active_iter:03d}"
                        metadata_file = self.storage_path / "iterations" / iter_name / "metadata.json"
                        if metadata_file.exists():
                            try:
                                # Load metadata
                                with open(metadata_file, 'r') as f:
                                    metadata = json.load(f)
                                
                                # Add checkpoint to list
                                if "checkpoints" not in metadata:
                                    metadata["checkpoints"] = []
                                metadata["checkpoints"].append(checkpoint_id)
                                
                                # Save updated metadata
                                with open(metadata_file, 'w') as f:
                                    json.dump(metadata, f, indent=2)
                            except Exception as e:
                                logger.warning(f"Failed to update iteration metadata with checkpoint: {e}")
                    
                    logger.info(f"Created checkpoint {checkpoint_id}")
                    return checkpoint_id
                    
                finally:
                    # Release the file lock
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                    lock_file.close()
                    
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
                
                # Validate required fields exist
                required_fields = ["timestamp", "orchestration_state", "checkpoint_data", "system_statistics"]
                if not all(field in checkpoint_data for field in required_fields):
                    logger.error(f"Checkpoint {checkpoint_id} missing required fields")
                    return None
                
                return RecoveryState(
                    checkpoint_timestamp=datetime.fromisoformat(checkpoint_data["timestamp"]),
                    system_configuration=checkpoint_data["orchestration_state"],
                    active_tasks=checkpoint_data["checkpoint_data"].get("in_flight_tasks", []),
                    completed_work={"hypotheses": checkpoint_data["system_statistics"].get("total_hypotheses", 0)},
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
    
    async def get_current_iteration_number(self) -> int:
        """Get the current iteration number."""
        iterations_dir = self.storage_path / "iterations"
        if not iterations_dir.exists():
            return 1
        
        existing_iterations = [d for d in iterations_dir.iterdir() if d.is_dir() and d.name.startswith("iteration_")]
        
        if not existing_iterations:
            return 1
        
        # Find the highest iteration number and return next
        latest_num = max(int(d.name.split("_")[1]) for d in existing_iterations)
        return latest_num + 1
    
    async def get_active_iteration(self) -> Optional[int]:
        """Get the currently active iteration number, if any."""
        iterations_dir = self.storage_path / "iterations"
        if not iterations_dir.exists():
            return None
        
        # Check each iteration's metadata for active status
        for iter_dir in iterations_dir.iterdir():
            if iter_dir.is_dir() and iter_dir.name.startswith("iteration_"):
                metadata_file = iter_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            if metadata.get("status") == "active":
                                return metadata["iteration_number"]
                    except Exception:
                        continue
        
        return None
    
    async def start_new_iteration(self) -> int:
        """Start a new iteration and return its number."""
        # Check if there's already an active iteration
        active = await self.get_active_iteration()
        if active is not None:
            raise RuntimeError(f"Cannot start new iteration: there is already an active iteration ({active})")
        
        # Get the next iteration number
        iteration_num = await self.get_current_iteration_number()
        iter_name = f"iteration_{iteration_num:03d}"
        iter_dir = self.storage_path / "iterations" / iter_name
        
        # Create iteration directory structure
        iter_dir.mkdir(parents=True, exist_ok=True)
        (iter_dir / "agent_outputs").mkdir(exist_ok=True)
        (iter_dir / "tournament_data").mkdir(exist_ok=True)
        
        # Create iteration metadata
        metadata = {
            "iteration_number": iteration_num,
            "started_at": datetime.now().isoformat(),
            "status": "active",
            "checkpoints": []
        }
        
        metadata_file = iter_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Started new iteration {iteration_num}")
        return iteration_num
    
    async def complete_iteration(self, iteration_number: int, summary: Dict[str, Any]) -> bool:
        """Complete an iteration with summary data."""
        iter_name = f"iteration_{iteration_number:03d}"
        iter_dir = self.storage_path / "iterations" / iter_name
        metadata_file = iter_dir / "metadata.json"
        
        if not metadata_file.exists():
            logger.error(f"Cannot complete iteration {iteration_number}: metadata file not found")
            return False
        
        try:
            # Load existing metadata
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Calculate duration
            started_at = datetime.fromisoformat(metadata["started_at"])
            completed_at = datetime.now()
            duration_seconds = (completed_at - started_at).total_seconds()
            
            # Update metadata
            metadata["status"] = "completed"
            metadata["completed_at"] = completed_at.isoformat()
            metadata["duration_seconds"] = duration_seconds
            metadata["summary"] = summary
            
            # Save updated metadata
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Completed iteration {iteration_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete iteration {iteration_number}: {e}")
            return False
    
    async def get_iteration_info(self, iteration_number: int) -> Optional[Dict[str, Any]]:
        """Get information about a specific iteration."""
        iter_name = f"iteration_{iteration_number:03d}"
        iter_dir = self.storage_path / "iterations" / iter_name
        metadata_file = iter_dir / "metadata.json"
        
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Add duration if completed
            if metadata["status"] == "completed" and "started_at" in metadata and "completed_at" in metadata:
                started = datetime.fromisoformat(metadata["started_at"])
                completed = datetime.fromisoformat(metadata["completed_at"])
                metadata["duration_seconds"] = (completed - started).total_seconds()
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get iteration info for {iteration_number}: {e}")
            return None
    
    async def list_iterations(self) -> List[Dict[str, Any]]:
        """List all iterations with their basic info."""
        iterations = []
        iterations_dir = self.storage_path / "iterations"
        
        if not iterations_dir.exists():
            return iterations
        
        for iter_dir in sorted(iterations_dir.iterdir()):
            if iter_dir.is_dir() and iter_dir.name.startswith("iteration_"):
                try:
                    iter_num = int(iter_dir.name.split("_")[1])
                    info = await self.get_iteration_info(iter_num)
                    if info:
                        iterations.append(info)
                except Exception:
                    continue
        
        # Sort by iteration number
        iterations.sort(key=lambda x: x["iteration_number"])
        return iterations
    
    async def get_iteration_statistics(self, iteration_number: int) -> Optional[Dict[str, Any]]:
        """Get detailed statistics for an iteration."""
        iter_name = f"iteration_{iteration_number:03d}"
        iter_dir = self.storage_path / "iterations" / iter_name
        
        if not iter_dir.exists():
            return None
        
        stats = {
            "state_updates_count": 0,
            "agent_outputs_count": 0,
            "has_meta_review": False,
            "storage_size_bytes": 0,
            "agent_type_breakdown": {}
        }
        
        # Count state updates
        for file in iter_dir.glob("system_state_*.json"):
            stats["state_updates_count"] += 1
            stats["storage_size_bytes"] += file.stat().st_size
        
        # Old format state file
        old_state_file = iter_dir / "system_state.json"
        if old_state_file.exists():
            stats["state_updates_count"] += 1
            stats["storage_size_bytes"] += old_state_file.stat().st_size
        
        # Count agent outputs and breakdown by type
        agent_outputs_dir = iter_dir / "agent_outputs"
        if agent_outputs_dir.exists():
            for output_file in agent_outputs_dir.glob("*.json"):
                stats["agent_outputs_count"] += 1
                stats["storage_size_bytes"] += output_file.stat().st_size
                
                # Get agent type from file content
                try:
                    with open(output_file, 'r') as f:
                        data = json.load(f)
                        agent_type = data.get("agent_type", "unknown")
                        stats["agent_type_breakdown"][agent_type] = stats["agent_type_breakdown"].get(agent_type, 0) + 1
                except Exception:
                    pass
        
        # Check for meta review
        meta_review_file = iter_dir / "meta_review.json"
        if meta_review_file.exists():
            stats["has_meta_review"] = True
            stats["storage_size_bytes"] += meta_review_file.stat().st_size
        
        # Add metadata file size
        metadata_file = iter_dir / "metadata.json"
        if metadata_file.exists():
            stats["storage_size_bytes"] += metadata_file.stat().st_size
        
        return stats
    
    # Key-Value Store Methods
    
    def _validate_key(self, key: Any) -> str:
        """Validate and return a key for the key-value store."""
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key)}")
        
        if not key or key.isspace():
            raise ValueError("Key cannot be empty or whitespace")
        
        # Check for invalid characters
        invalid_chars = [' ', '/', '\\', ':', '*', '?', '|']
        for char in invalid_chars:
            if char in key:
                raise ValueError(f"Key cannot contain '{char}'")
        
        return key
    
    def _get_kv_file_path(self, key: str) -> Path:
        """Get the file path for a key in the key-value store."""
        # Use a simple file-per-key approach for persistence
        return self.storage_path / "kv_store" / f"{key}.json"
    
    async def _load_kv_cache(self):
        """Load key-value pairs from storage into cache."""
        kv_dir = self.storage_path / "kv_store"
        if kv_dir.exists():
            for kv_file in kv_dir.glob("*.json"):
                key = kv_file.stem
                try:
                    with open(kv_file, 'r') as f:
                        self._kv_cache[key] = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load key-value pair {key}: {e}")
    
    async def _persist_kv_changes(self):
        """Persist modified key-value pairs to storage."""
        for key in self._kv_dirty:
            if key in self._kv_cache:
                # Key exists, save it
                file_path = self._get_kv_file_path(key)
                try:
                    with open(file_path, 'w') as f:
                        json.dump(self._kv_cache[key], f, indent=2)
                except Exception as e:
                    logger.error(f"Failed to persist key {key}: {e}")
            else:
                # Key was deleted, remove file
                file_path = self._get_kv_file_path(key)
                if file_path.exists():
                    file_path.unlink()
        
        self._kv_dirty.clear()
    
    async def set(self, key: str, value: Any) -> bool:
        """Set a key-value pair in the store."""
        try:
            key = self._validate_key(key)
            
            # Ensure value is JSON serializable
            json.dumps(value)
            
            self._kv_cache[key] = value
            self._kv_dirty.add(key)
            
            # Persist immediately for consistency
            await self._persist_kv_changes()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set key {key}: {e}")
            if isinstance(e, (TypeError, ValueError)):
                raise
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the key-value store."""
        try:
            key = self._validate_key(key)
            
            # Check cache first
            if key in self._kv_cache:
                return self._kv_cache[key]
            
            # Try loading from disk if not in cache
            file_path = self._get_kv_file_path(key)
            if file_path.exists():
                with open(file_path, 'r') as f:
                    value = json.load(f)
                    self._kv_cache[key] = value
                    return value
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key-value pair from the store."""
        try:
            key = self._validate_key(key)
            
            if key not in self._kv_cache:
                # Check if it exists on disk
                file_path = self._get_kv_file_path(key)
                if not file_path.exists():
                    return False
            
            # Remove from cache
            if key in self._kv_cache:
                del self._kv_cache[key]
            
            # Mark for deletion
            self._kv_dirty.add(key)
            
            # Persist deletion
            await self._persist_kv_changes()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in the store."""
        try:
            key = self._validate_key(key)
            
            # Check cache first
            if key in self._kv_cache:
                return True
            
            # Check disk
            file_path = self._get_kv_file_path(key)
            return file_path.exists()
            
        except Exception as e:
            logger.error(f"Failed to check existence of key {key}: {e}")
            return False
    
    async def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """List all keys in the store, optionally filtered by prefix."""
        try:
            # Get keys from cache
            cache_keys = set(self._kv_cache.keys())
            
            # Get keys from disk
            disk_keys = set()
            kv_dir = self.storage_path / "kv_store"
            if kv_dir.exists():
                for kv_file in kv_dir.glob("*.json"):
                    disk_keys.add(kv_file.stem)
            
            # Combine all keys
            all_keys = cache_keys | disk_keys
            
            # Filter by prefix if provided
            if prefix:
                filtered_keys = [k for k in all_keys if k.startswith(prefix)]
            else:
                filtered_keys = list(all_keys)
            
            return sorted(filtered_keys)
            
        except Exception as e:
            logger.error(f"Failed to list keys: {e}")
            return []
    
    async def batch_set(self, data: Dict[str, Any]) -> bool:
        """Set multiple key-value pairs at once."""
        try:
            # Validate all keys first
            for key in data.keys():
                self._validate_key(key)
            
            # Ensure all values are JSON serializable
            json.dumps(data)
            
            # Update cache
            self._kv_cache.update(data)
            self._kv_dirty.update(data.keys())
            
            # Persist changes
            await self._persist_kv_changes()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to batch set: {e}")
            if isinstance(e, (TypeError, ValueError)):
                raise
            return False
    
    async def batch_get(self, keys: List[str]) -> Dict[str, Optional[Any]]:
        """Get multiple values at once."""
        results = {}
        
        for key in keys:
            try:
                value = await self.get(key)
                results[key] = value
            except Exception:
                results[key] = None
        
        return results
    
    async def clear(self) -> bool:
        """Clear all key-value pairs from the store."""
        try:
            # Clear cache
            self._kv_cache.clear()
            
            # Remove all files from disk
            kv_dir = self.storage_path / "kv_store"
            if kv_dir.exists():
                for kv_file in kv_dir.glob("*.json"):
                    kv_file.unlink()
            
            self._kv_dirty.clear()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear key-value store: {e}")
            return False
    
    async def get_kv_storage_size(self) -> int:
        """Get the total storage size of the key-value store in bytes."""
        try:
            total_size = 0
            kv_dir = self.storage_path / "kv_store"
            
            if kv_dir.exists():
                for kv_file in kv_dir.glob("*.json"):
                    total_size += kv_file.stat().st_size
            
            return total_size
            
        except Exception as e:
            logger.error(f"Failed to get storage size: {e}")
            return 0
    
    async def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List all checkpoints with their metadata."""
        try:
            checkpoints = []
            checkpoints_dir = self.storage_path / "checkpoints"
            
            if checkpoints_dir.exists():
                for checkpoint_dir in checkpoints_dir.iterdir():
                    if checkpoint_dir.is_dir():
                        checkpoint_file = checkpoint_dir / "checkpoint.json"
                        if checkpoint_file.exists():
                            try:
                                with open(checkpoint_file, 'r') as f:
                                    data = json.load(f)
                                    checkpoints.append({
                                        "checkpoint_id": data.get("checkpoint_id"),
                                        "timestamp": data.get("timestamp"),
                                        "created_at": data.get("created_at")
                                    })
                            except Exception as e:
                                logger.warning(f"Failed to read checkpoint {checkpoint_dir.name}: {e}")
            
            # Sort by created_at timestamp
            checkpoints.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return checkpoints
            
        except Exception as e:
            logger.error(f"Failed to list checkpoints: {e}")
            return []
    
    async def cleanup_old_checkpoints(self) -> int:
        """Clean up checkpoints older than retention period."""
        try:
            cleaned_count = 0
            checkpoints_dir = self.storage_path / "checkpoints"
            
            if not checkpoints_dir.exists():
                return 0
            
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            for checkpoint_dir in checkpoints_dir.iterdir():
                if checkpoint_dir.is_dir():
                    checkpoint_file = checkpoint_dir / "checkpoint.json"
                    if checkpoint_file.exists():
                        try:
                            with open(checkpoint_file, 'r') as f:
                                data = json.load(f)
                                created_at = datetime.fromisoformat(data.get("created_at", ""))
                                
                                if created_at < cutoff_date:
                                    # Remove old checkpoint
                                    import shutil
                                    shutil.rmtree(checkpoint_dir)
                                    cleaned_count += 1
                                    logger.info(f"Cleaned up old checkpoint: {checkpoint_dir.name}")
                        except Exception as e:
                            logger.warning(f"Failed to process checkpoint {checkpoint_dir.name}: {e}")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old checkpoints: {e}")
            return 0
    
    async def validate_checkpoint(self, checkpoint_id: str) -> bool:
        """Validate checkpoint data integrity."""
        try:
            checkpoint_file = self.storage_path / "checkpoints" / checkpoint_id / "checkpoint.json"
            
            if not checkpoint_file.exists():
                return False
            
            try:
                with open(checkpoint_file, 'r') as f:
                    data = json.load(f)
                
                # Check required fields
                required_fields = [
                    "checkpoint_id", "timestamp", "system_statistics",
                    "orchestration_state", "checkpoint_data", "created_at"
                ]
                
                if not all(field in data for field in required_fields):
                    return False
                
                # Validate checkpoint_id matches
                if data.get("checkpoint_id") != checkpoint_id:
                    return False
                
                # Try to parse timestamps
                datetime.fromisoformat(data["timestamp"])
                datetime.fromisoformat(data["created_at"])
                
                return True
                
            except (json.JSONDecodeError, ValueError, KeyError):
                return False
                
        except Exception as e:
            logger.error(f"Failed to validate checkpoint {checkpoint_id}: {e}")
            return False
    
    async def get_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Get the most recent checkpoint."""
        try:
            checkpoints = await self.list_checkpoints()
            if checkpoints:
                # Already sorted by created_at in descending order
                checkpoint_id = checkpoints[0]["checkpoint_id"]
                
                # Load full checkpoint data
                checkpoint_file = self.storage_path / "checkpoints" / checkpoint_id / "checkpoint.json"
                if checkpoint_file.exists():
                    with open(checkpoint_file, 'r') as f:
                        return json.load(f)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest checkpoint: {e}")
            return None
    
    # Aggregate Storage Methods
    
    async def store_aggregate(self, aggregate_type: str, data: Dict[str, Any], timestamp: datetime) -> bool:
        """Store aggregate data."""
        try:
            aggregate_file = self.storage_path / "aggregates" / f"{aggregate_type}.json"
            
            # Load existing data or create new structure
            if aggregate_file.exists():
                with open(aggregate_file, 'r') as f:
                    aggregate_data = json.load(f)
            else:
                aggregate_data = {"entries": []}
            
            # Add new entry
            entry = {
                "timestamp": timestamp.isoformat(),
                "data": data
            }
            aggregate_data["entries"].append(entry)
            
            # Sort entries by timestamp
            aggregate_data["entries"].sort(key=lambda x: x["timestamp"])
            
            # Write back to file
            with open(aggregate_file, 'w') as f:
                json.dump(aggregate_data, f, indent=2)
            
            logger.info(f"Stored aggregate data for {aggregate_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store aggregate: {e}")
            return False
    
    async def retrieve_aggregate(
        self,
        aggregate_type: str,
        query_type: str = "latest",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Optional[Any]:
        """Retrieve aggregate data based on query type."""
        try:
            aggregate_file = self.storage_path / "aggregates" / f"{aggregate_type}.json"
            
            if not aggregate_file.exists():
                return None
            
            with open(aggregate_file, 'r') as f:
                aggregate_data = json.load(f)
            
            entries = aggregate_data.get("entries", [])
            
            if not entries:
                return None
            
            if query_type == "latest":
                # Return data from the latest entry
                return entries[-1]["data"]
            
            elif query_type == "time_range":
                # Filter entries by time range
                if start_time is None or end_time is None:
                    raise ValueError("start_time and end_time required for time_range query")
                
                filtered_entries = []
                for entry in entries:
                    entry_time = datetime.fromisoformat(entry["timestamp"])
                    if start_time <= entry_time <= end_time:
                        filtered_entries.append(entry["data"])
                
                return filtered_entries
            
            else:
                raise ValueError(f"Unknown query_type: {query_type}")
            
        except Exception as e:
            logger.error(f"Failed to retrieve aggregate: {e}")
            return None
    
    async def update_aggregate(
        self,
        aggregate_type: str,
        data: Dict[str, Any],
        merge_strategy: str = "replace"
    ) -> bool:
        """Update aggregate data with merge strategy."""
        try:
            if merge_strategy == "replace":
                # Replace strategy: store as new entry
                return await self.store_aggregate(aggregate_type, data, datetime.now())
            
            elif merge_strategy == "merge":
                # Merge strategy: combine with latest entry
                aggregate_file = self.storage_path / "aggregates" / f"{aggregate_type}.json"
                
                if aggregate_file.exists():
                    with open(aggregate_file, 'r') as f:
                        aggregate_data = json.load(f)
                    
                    if aggregate_data.get("entries"):
                        # Get latest entry
                        latest_entry = aggregate_data["entries"][-1]
                        merged_data = latest_entry["data"].copy()
                        
                        # Merge non-conflicting fields
                        for key, value in data.items():
                            if key not in merged_data:
                                # Add new field
                                merged_data[key] = value
                            elif isinstance(value, dict) and isinstance(merged_data[key], dict):
                                # Recursively merge nested dicts
                                merged_data[key] = {**merged_data[key], **value}
                            else:
                                # Replace conflicting field (last-write-wins)
                                merged_data[key] = value
                        
                        # Store merged result
                        return await self.store_aggregate(aggregate_type, merged_data, datetime.now())
                
                # No existing data, just store
                return await self.store_aggregate(aggregate_type, data, datetime.now())
            
            elif merge_strategy == "accumulate":
                # Accumulate strategy: add numeric values
                aggregate_file = self.storage_path / "aggregates" / f"{aggregate_type}.json"
                
                if aggregate_file.exists():
                    with open(aggregate_file, 'r') as f:
                        aggregate_data = json.load(f)
                    
                    if aggregate_data.get("entries"):
                        # Get latest entry
                        latest_entry = aggregate_data["entries"][-1]
                        accumulated_data = latest_entry["data"].copy()
                        
                        # Accumulate numeric fields
                        for key, value in data.items():
                            if key in accumulated_data and isinstance(value, (int, float)):
                                accumulated_data[key] += value
                            else:
                                accumulated_data[key] = value
                        
                        # Store accumulated result
                        return await self.store_aggregate(aggregate_type, accumulated_data, datetime.now())
                
                # No existing data, just store
                return await self.store_aggregate(aggregate_type, data, datetime.now())
            
            else:
                raise ValueError(f"Unknown merge strategy: {merge_strategy}")
            
        except Exception as e:
            logger.error(f"Failed to update aggregate: {e}")
            return False
    
    async def compute_aggregate_statistics(
        self,
        agent_type: str,
        metric: str
    ) -> Optional[Dict[str, float]]:
        """Compute aggregate statistics from agent outputs."""
        try:
            # Get active iteration
            active_iter = await self.get_active_iteration()
            if active_iter is None:
                # No active iteration, check recent iterations
                iterations = await self.list_iterations()
                if not iterations:
                    return None
                # Use the most recent iteration
                active_iter = iterations[-1]["iteration_number"]
            
            iter_name = f"iteration_{active_iter:03d}"
            agent_outputs_dir = self.storage_path / "iterations" / iter_name / "agent_outputs"
            
            if not agent_outputs_dir.exists():
                return None
            
            values = []
            
            # Collect metric values from agent outputs
            for output_file in agent_outputs_dir.glob(f"{agent_type}_*.json"):
                with open(output_file, 'r') as f:
                    data = json.load(f)
                    if data["agent_type"] == agent_type:
                        results = data.get("results", {})
                        if metric in results:
                            values.append(results[metric])
            
            if not values:
                return None
            
            # Compute statistics
            stats = {
                "count": len(values),
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to compute aggregate statistics: {e}")
            return None
    
    async def cleanup_aggregate_entries(self) -> int:
        """Clean up old entries from aggregates."""
        try:
            cleaned_count = 0
            aggregates_dir = self.storage_path / "aggregates"
            
            if not aggregates_dir.exists():
                return 0
            
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            for aggregate_file in aggregates_dir.glob("*.json"):
                try:
                    with open(aggregate_file, 'r') as f:
                        aggregate_data = json.load(f)
                    
                    original_count = len(aggregate_data.get("entries", []))
                    
                    # Filter out old entries
                    aggregate_data["entries"] = [
                        entry for entry in aggregate_data.get("entries", [])
                        if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
                    ]
                    
                    cleaned_count += original_count - len(aggregate_data["entries"])
                    
                    # Write back cleaned data
                    with open(aggregate_file, 'w') as f:
                        json.dump(aggregate_data, f, indent=2)
                    
                except Exception as e:
                    logger.warning(f"Failed to clean aggregate {aggregate_file.name}: {e}")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup aggregate entries: {e}")
            return 0
    
    async def list_aggregate_types(self) -> List[str]:
        """List all available aggregate types."""
        try:
            aggregates_dir = self.storage_path / "aggregates"
            
            if not aggregates_dir.exists():
                return []
            
            aggregate_types = []
            for aggregate_file in aggregates_dir.glob("*.json"):
                aggregate_types.append(aggregate_file.stem)
            
            return sorted(aggregate_types)
            
        except Exception as e:
            logger.error(f"Failed to list aggregate types: {e}")
            return []
    
    async def get_aggregate_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary information for all aggregates."""
        try:
            summary = {}
            aggregates_dir = self.storage_path / "aggregates"
            
            if not aggregates_dir.exists():
                return summary
            
            for aggregate_file in aggregates_dir.glob("*.json"):
                try:
                    aggregate_type = aggregate_file.stem
                    file_size = aggregate_file.stat().st_size
                    
                    with open(aggregate_file, 'r') as f:
                        aggregate_data = json.load(f)
                    
                    entries = aggregate_data.get("entries", [])
                    
                    if entries:
                        latest_timestamp = entries[-1]["timestamp"]
                    else:
                        latest_timestamp = None
                    
                    summary[aggregate_type] = {
                        "entry_count": len(entries),
                        "file_size": file_size,
                        "latest_timestamp": latest_timestamp
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to get summary for {aggregate_file.name}: {e}")
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get aggregate summary: {e}")
            return {}
    
    # Temporal Guarantee Methods
    
    async def retrieve_states_in_range(
        self, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Retrieve all states within a time range, ordered by timestamp."""
        try:
            states = []
            
            # Search through all iterations
            iterations_dir = self.storage_path / "iterations"
            if not iterations_dir.exists():
                return states
            
            for iteration_dir in iterations_dir.iterdir():
                if not iteration_dir.is_dir():
                    continue
                
                # Check all state files in this iteration
                for state_file in iteration_dir.glob("system_state*.json"):
                    try:
                        with open(state_file, 'r') as f:
                            data = json.load(f)
                            timestamp = datetime.fromisoformat(data["timestamp"])
                            
                            # Check if in range
                            if start_time <= timestamp <= end_time:
                                states.append(data)
                    except Exception as e:
                        logger.warning(f"Failed to read state file {state_file}: {e}")
            
            # Sort by timestamp
            states.sort(key=lambda x: x["timestamp"])
            return states
            
        except Exception as e:
            logger.error(f"Failed to retrieve states in range: {e}")
            return []
    
    async def retrieve_state_for_agent(
        self, 
        agent_id: str, 
        request_type: str = "latest"
    ) -> Optional[RetrievedState]:
        """Retrieve state ensuring read-your-writes consistency for an agent."""
        try:
            # For now, retrieve latest state that was written by this agent
            # or the absolute latest if no agent-specific state exists
            latest_state = None
            latest_time = None
            agent_state = None
            agent_time = None
            
            for timestamp, path in sorted(self._temporal_index.items(), reverse=True):
                if path.name.startswith("system_state"):
                    with open(path, 'r') as f:
                        state_data = json.load(f)
                        
                        # Track absolute latest
                        if latest_state is None:
                            latest_state = state_data
                            latest_time = timestamp
                        
                        # Check if written by this agent
                        writer = state_data.get("writer_id")
                        if writer == agent_id and agent_state is None:
                            agent_state = state_data
                            agent_time = timestamp
                            break
            
            # Return agent's own write if available, otherwise latest
            if agent_state:
                system_state = agent_state["orchestration_state"].copy()
                system_state["tournament_progress"] = agent_state["system_statistics"].get("tournament_progress")
                # Include statistics values in system_state for compatibility
                system_state["value"] = agent_state["system_statistics"].get("value")
                return RetrievedState(
                    request_type=request_type,
                    content={
                        "system_state": system_state,
                        "statistics": agent_state["system_statistics"],
                        "timestamp": agent_state["timestamp"],
                        "writer_id": agent_id
                    }
                )
            elif latest_state:
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
            logger.error(f"Failed to retrieve state for agent {agent_id}: {e}")
            return None
    
    async def retrieve_state_as_of(self, timestamp: datetime) -> Optional[RetrievedState]:
        """Retrieve state as of a specific timestamp (snapshot isolation)."""
        try:
            # Find the most recent state before or at the given timestamp
            best_state = None
            best_time = None
            
            for ts, path in sorted(self._temporal_index.items()):
                if ts <= timestamp and path.name.startswith("system_state"):
                    with open(path, 'r') as f:
                        best_state = json.load(f)
                        best_time = ts
                elif ts > timestamp:
                    break  # No need to look further
            
            if best_state:
                system_state = best_state["orchestration_state"].copy()
                system_state["tournament_progress"] = best_state["system_statistics"].get("tournament_progress")
                return RetrievedState(
                    request_type="as_of",
                    timestamp_range=(best_time, timestamp),
                    content={
                        "system_state": system_state,
                        "statistics": best_state["system_statistics"],
                        "timestamp": best_state["timestamp"]
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve state as of {timestamp}: {e}")
            return None
    
    async def get_version_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get version history with version numbers."""
        try:
            versions = []
            version_counter = 0
            
            # Get recent states in reverse chronological order
            for timestamp, path in sorted(self._temporal_index.items(), reverse=True):
                if path.name.startswith("system_state"):
                    with open(path, 'r') as f:
                        data = json.load(f)
                        
                        # Add computed version number
                        version_info = {
                            "version": data.get("version", version_counter),
                            "timestamp": data["timestamp"],
                            "writer_id": data.get("writer_id", "unknown"),
                            "update_type": data.get("update_type", "unknown")
                        }
                        versions.append(version_info)
                        version_counter += 1
                        
                        if len(versions) >= limit:
                            break
            
            # Reverse to get chronological order with increasing versions
            versions.reverse()
            
            # Ensure version numbers are sequential
            for i, v in enumerate(versions):
                v["version"] = i + 1
            
            return versions
            
        except Exception as e:
            logger.error(f"Failed to get version history: {e}")
            return []
    
    async def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get causal history for a session."""
        try:
            history = []
            
            # Search all states for this session
            for timestamp, path in sorted(self._temporal_index.items()):
                if path.name.startswith("system_state"):
                    with open(path, 'r') as f:
                        data = json.load(f)
                        
                        # Check if part of this session
                        if data.get("orchestration_state", {}).get("session_id") == session_id:
                            # Extract relevant info
                            history_entry = {
                                "timestamp": data["timestamp"],
                                "step": data["system_statistics"].get("step"),
                                "value": data["system_statistics"].get("value"),
                                "update_type": data.get("update_type")
                            }
                            history.append(history_entry)
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get session history: {e}")
            return []
    
    async def get_all_timestamps(self) -> List[datetime]:
        """Get all stored timestamps in order."""
        try:
            timestamps = []
            
            # Collect from temporal index
            for timestamp, path in sorted(self._temporal_index.items()):
                timestamps.append(timestamp)
            
            return timestamps
            
        except Exception as e:
            logger.error(f"Failed to get all timestamps: {e}")
            return []
    
    async def reserve_write_window(
        self, 
        agent_id: str, 
        duration_seconds: float
    ) -> Optional[Dict[str, Any]]:
        """Reserve a write window for an agent to minimize conflicts."""
        try:
            # Store reservation in a special file
            reservations_file = self.storage_path / "configuration" / "write_reservations.json"
            
            # Load existing reservations
            if reservations_file.exists():
                with open(reservations_file, 'r') as f:
                    reservations = json.load(f)
            else:
                reservations = {}
            
            current_time = datetime.now(timezone.utc)
            
            # Clean up expired reservations
            active_reservations = {}
            for aid, res in reservations.items():
                expiry = datetime.fromisoformat(res["expiry"])
                if expiry > current_time:
                    active_reservations[aid] = res
            
            # Check if agent already has a reservation
            if agent_id in active_reservations:
                return active_reservations[agent_id]
            
            # Create new reservation
            reservation = {
                "agent_id": agent_id,
                "start_time": current_time.isoformat(),
                "expiry": (current_time + timedelta(seconds=duration_seconds)).isoformat(),
                "duration_seconds": duration_seconds
            }
            
            active_reservations[agent_id] = reservation
            
            # Save updated reservations
            with open(reservations_file, 'w') as f:
                json.dump(active_reservations, f, indent=2)
            
            return reservation
            
        except Exception as e:
            logger.error(f"Failed to reserve write window: {e}")
            return None
    
    # Cleanup and Archival Methods
    
    async def cleanup_old_iterations(self) -> int:
        """Clean up iterations older than retention period."""
        try:
            start_time = datetime.now(timezone.utc)
            initial_size = await self.get_total_storage_size() if hasattr(self, '_performance_monitoring') else 0
            
            cleaned_count = 0
            iterations_dir = self.storage_path / "iterations"
            
            if not iterations_dir.exists():
                return 0
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
            
            for iteration_dir in iterations_dir.iterdir():
                if not iteration_dir.is_dir() or not iteration_dir.name.startswith("iteration_"):
                    continue
                
                # Check if this is the active iteration
                metadata_file = iteration_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            
                        # Never clean up active iterations
                        if metadata.get("status") == "active":
                            continue
                        
                        # Check age
                        if "started_at" in metadata:
                            started_at = datetime.fromisoformat(metadata["started_at"])
                            if started_at < cutoff_date:
                                # Archive before deletion
                                await self._archive_iteration(iteration_dir)
                                
                                # Remove directory
                                import shutil
                                shutil.rmtree(iteration_dir)
                                cleaned_count += 1
                                logger.info(f"Cleaned up old iteration: {iteration_dir.name}")
                    except Exception as e:
                        logger.warning(f"Failed to process iteration {iteration_dir.name}: {e}")
            
            # Also run checkpoint cleanup
            checkpoint_cleaned = await self.cleanup_old_checkpoints()
            
            total_cleaned = cleaned_count + checkpoint_cleaned
            
            # Update metrics if performance monitoring is enabled
            if hasattr(self, '_performance_monitoring') and self._performance_monitoring:
                duration = (datetime.now(timezone.utc) - start_time).total_seconds()
                final_size = await self.get_total_storage_size()
                freed_bytes = initial_size - final_size
                
                self._cleanup_metrics["last_cleanup_duration"] = duration
                self._cleanup_metrics["items_cleaned"] = total_cleaned
                self._cleanup_metrics["storage_freed_bytes"] = freed_bytes
                self._cleanup_metrics["cleanup_history"].append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "duration": duration,
                    "items_cleaned": total_cleaned,
                    "bytes_freed": freed_bytes
                })
            
            return total_cleaned
            
        except Exception as e:
            logger.error(f"Failed to cleanup old iterations: {e}")
            return 0
    
    async def archive_old_data(self) -> int:
        """Archive old data before cleanup."""
        try:
            archive_dir = self.storage_path / "archive"
            archive_dir.mkdir(exist_ok=True)
            
            archived_count = 0
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
            
            # Archive old iterations
            iterations_dir = self.storage_path / "iterations"
            if iterations_dir.exists():
                for iteration_dir in iterations_dir.iterdir():
                    if not iteration_dir.is_dir():
                        continue
                    
                    try:
                        # Check if old enough to archive
                        metadata_file = iteration_dir / "metadata.json"
                        if metadata_file.exists():
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                            
                            if metadata.get("status") != "active":
                                started_at_str = metadata.get("started_at", datetime.now(timezone.utc).isoformat())
                                started_at = datetime.fromisoformat(started_at_str)
                                # Ensure timezone awareness
                                if started_at.tzinfo is None:
                                    started_at = started_at.replace(tzinfo=timezone.utc)
                                if started_at < cutoff_date:
                                    archived = await self._archive_iteration(iteration_dir)
                                    if archived:
                                        archived_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to archive {iteration_dir.name}: {e}")
            
            # Update archive metadata
            await self._update_archive_metadata(archived_count)
            
            return archived_count
            
        except Exception as e:
            logger.error(f"Failed to archive old data: {e}")
            return 0
    
    async def _archive_iteration(self, iteration_dir: Path) -> bool:
        """Archive a single iteration directory."""
        try:
            import tarfile
            import gzip
            
            archive_dir = self.storage_path / "archive"
            archive_dir.mkdir(exist_ok=True)
            
            # Create archive filename
            iteration_name = iteration_dir.name
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            archive_name = f"{iteration_name}_{timestamp}.tar.gz"
            archive_path = archive_dir / archive_name
            
            # Create compressed archive
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(iteration_dir, arcname=iteration_name)
            
            logger.info(f"Archived iteration to {archive_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to archive iteration {iteration_dir}: {e}")
            return False
    
    async def _update_archive_metadata(self, archived_count: int):
        """Update archive metadata file."""
        try:
            # Ensure archive directory exists
            archive_dir = self.storage_path / "archive"
            archive_dir.mkdir(exist_ok=True)
            
            metadata_file = archive_dir / "archive_metadata.json"
            
            # Load existing metadata or create new
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {"archives": []}
            
            # Add new archive entry
            archive_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "archived_count": archived_count
            }
            metadata["archives"].append(archive_entry)
            
            # Save updated metadata
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to update archive metadata: {e}")
    
    async def get_total_storage_size(self) -> int:
        """Get total storage size in bytes."""
        try:
            total_size = 0
            
            # Walk through all files in storage path
            for root, dirs, files in os.walk(self.storage_path):
                for file in files:
                    file_path = Path(root) / file
                    try:
                        total_size += file_path.stat().st_size
                    except Exception:
                        pass
            
            return total_size
            
        except Exception as e:
            logger.error(f"Failed to get total storage size: {e}")
            return 0
    
    async def get_storage_breakdown(self) -> Dict[str, int]:
        """Get storage size breakdown by component."""
        try:
            breakdown = {
                "iterations": 0,
                "checkpoints": 0,
                "aggregates": 0,
                "kv_store": 0
            }
            
            for component in breakdown.keys():
                component_dir = self.storage_path / component
                if component_dir.exists():
                    for root, dirs, files in os.walk(component_dir):
                        for file in files:
                            file_path = Path(root) / file
                            try:
                                breakdown[component] += file_path.stat().st_size
                            except Exception:
                                pass
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Failed to get storage breakdown: {e}")
            return {}
    
    async def check_garbage_collection_needed(self) -> bool:
        """Check if garbage collection is needed based on storage limits."""
        try:
            total_size = await self.get_total_storage_size()
            max_size_bytes = self.max_storage_gb * 1024 * 1024 * 1024
            
            # Trigger GC at 80% of max storage
            return total_size > (max_size_bytes * 0.8)
            
        except Exception as e:
            logger.error(f"Failed to check garbage collection: {e}")
            return False
    
    async def run_garbage_collection(self) -> int:
        """Run garbage collection to free up storage space."""
        try:
            initial_size = await self.get_total_storage_size()
            
            # First, clean up old data
            cleaned_iterations = await self.cleanup_old_iterations()
            
            # Clean up old aggregates
            cleaned_aggregates = await self.cleanup_aggregate_entries()
            
            # Get final size
            final_size = await self.get_total_storage_size()
            freed_bytes = initial_size - final_size
            
            logger.info(f"Garbage collection freed {freed_bytes} bytes")
            return freed_bytes
            
        except Exception as e:
            logger.error(f"Failed to run garbage collection: {e}")
            return 0
    
    async def check_archive_rotation_needed(self) -> bool:
        """Check if archive rotation is needed (every 24 hours)."""
        try:
            last_archive_file = self.storage_path / "configuration" / "last_archive.json"
            
            if not last_archive_file.exists():
                return True
            
            with open(last_archive_file, 'r') as f:
                data = json.load(f)
                last_archive = datetime.fromisoformat(data["timestamp"])
            
            # Check if 24 hours have passed
            hours_since = (datetime.now(timezone.utc) - last_archive).total_seconds() / 3600
            return hours_since >= 24
            
        except Exception as e:
            logger.error(f"Failed to check archive rotation: {e}")
            return False
    
    async def rotate_archives(self) -> bool:
        """Rotate archives - archive old data and update tracking."""
        try:
            # Archive old data
            archived_count = await self.archive_old_data()
            
            # Update last archive time
            last_archive_file = self.storage_path / "configuration" / "last_archive.json"
            last_archive_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "archived_count": archived_count
            }
            
            with open(last_archive_file, 'w') as f:
                json.dump(last_archive_data, f, indent=2)
            
            logger.info(f"Archive rotation completed, archived {archived_count} items")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate archives: {e}")
            return False
    
    async def enable_performance_monitoring(self):
        """Enable performance monitoring for cleanup operations."""
        self._performance_monitoring = True
        self._cleanup_metrics = {
            "last_cleanup_duration": 0,
            "items_cleaned": 0,
            "storage_freed_bytes": 0,
            "cleanup_history": []
        }
    
    async def get_cleanup_metrics(self) -> Dict[str, Any]:
        """Get cleanup performance metrics."""
        return getattr(self, '_cleanup_metrics', {})
    
    def set_cleanup_batch_size(self, batch_size: int):
        """Set the batch size for incremental cleanup."""
        self._cleanup_batch_size = batch_size
    
    async def cleanup_batch(self) -> int:
        """Clean up a batch of old items."""
        try:
            batch_size = getattr(self, '_cleanup_batch_size', 10)
            cleaned_count = 0
            
            iterations_dir = self.storage_path / "iterations"
            if not iterations_dir.exists():
                return 0
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
            
            for iteration_dir in iterations_dir.iterdir():
                if cleaned_count >= batch_size:
                    break
                
                if not iteration_dir.is_dir() or not iteration_dir.name.startswith("iteration_"):
                    continue
                
                # Check if eligible for cleanup
                metadata_file = iteration_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        
                        if metadata.get("status") != "active":
                            if "started_at" in metadata:
                                started_at = datetime.fromisoformat(metadata["started_at"])
                                if started_at < cutoff_date:
                                    # Archive and remove
                                    await self._archive_iteration(iteration_dir)
                                    import shutil
                                    shutil.rmtree(iteration_dir)
                                    cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to process {iteration_dir.name}: {e}")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup batch: {e}")
            return 0
    
    async def collect_garbage(self) -> Dict[str, Any]:
        """Collect garbage - identify and clean orphaned data.
        
        Returns:
            Dictionary with garbage collection statistics
        """
        try:
            collected_stats = {
                "orphaned_files": 0,
                "orphaned_directories": 0,
                "storage_freed_bytes": 0,
                "errors": []
            }
            
            # Check for orphaned iteration directories
            iterations_dir = self.storage_path / "iterations"
            if iterations_dir.exists():
                for item in iterations_dir.iterdir():
                    try:
                        if item.is_dir():
                            # Check if it's a valid iteration directory
                            if not item.name.startswith("iteration_"):
                                # Orphaned directory
                                collected_stats["orphaned_directories"] += 1
                                collected_stats["storage_freed_bytes"] += self._get_directory_size(item)
                                import shutil
                                shutil.rmtree(item)
                            else:
                                # Check if it has metadata
                                metadata_file = item / "metadata.json"
                                if not metadata_file.exists():
                                    # Orphaned iteration without metadata
                                    collected_stats["orphaned_directories"] += 1
                                    collected_stats["storage_freed_bytes"] += self._get_directory_size(item)
                                    import shutil
                                    shutil.rmtree(item)
                        elif item.is_file():
                            # Orphaned file in iterations directory
                            collected_stats["orphaned_files"] += 1
                            collected_stats["storage_freed_bytes"] += item.stat().st_size
                            item.unlink()
                    except Exception as e:
                        collected_stats["errors"].append(str(e))
                        logger.warning(f"Failed to collect garbage for {item}: {e}")
            
            # Check for orphaned files in other directories
            for subdir in ["checkpoints", "aggregates", "kv_store"]:
                dir_path = self.storage_path / subdir
                if dir_path.exists():
                    for item in dir_path.iterdir():
                        try:
                            if item.is_file() and item.name.startswith(".") and item.name.endswith(".tmp"):
                                # Temporary file
                                collected_stats["orphaned_files"] += 1
                                collected_stats["storage_freed_bytes"] += item.stat().st_size
                                item.unlink()
                        except Exception as e:
                            collected_stats["errors"].append(str(e))
            
            logger.info(f"Garbage collection completed: {collected_stats}")
            return collected_stats
            
        except Exception as e:
            logger.error(f"Failed to collect garbage: {e}")
            return {
                "orphaned_files": 0,
                "orphaned_directories": 0,
                "storage_freed_bytes": 0,
                "errors": [str(e)]
            }
    
    def _get_directory_size(self, directory: Path) -> int:
        """Get total size of a directory in bytes."""
        total_size = 0
        try:
            for item in directory.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
        except Exception:
            pass
        return total_size
    
    async def _check_storage_limit(self) -> bool:
        """Check if storage is within limits.
        
        Returns:
            True if within limits, False if exceeded
        """
        try:
            total_size = self._get_directory_size(self.storage_path)
            max_size_bytes = self.max_storage_gb * 1024 * 1024 * 1024
            return total_size < max_size_bytes
        except Exception as e:
            logger.error(f"Failed to check storage limit: {e}")
            return True  # Assume within limits on error