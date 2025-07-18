"""Task Queue implementation for AI Co-Scientist."""

import asyncio
import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Set, Tuple
from uuid import uuid4, UUID

from src.core.models import Task, TaskState, TaskType


@dataclass
class WorkerInfo:
    """Information about a registered worker."""
    
    id: str
    capabilities: Dict[str, Any]
    state: str = "idle"  # idle, active, failed
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    assigned_task: Optional[str] = None
    registration_time: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QueueConfig:
    """Configuration for TaskQueue."""
    
    max_queue_size: int = 10000
    priority_quotas: Dict[str, int] = None
    worker_timeout: int = 300
    heartbeat_interval: int = 30
    heartbeat_timeout: int = 60  # Worker considered dead after this many seconds
    heartbeat_check_interval: int = 15  # How often to check for dead workers
    retry_policy: Dict[str, Any] = None
    persistence_interval: int = 60
    persistence_path: Optional[str] = None  # Path to save queue state
    auto_recovery: bool = False  # Auto-load state on initialization
    auto_start_persistence: bool = False  # Auto-start persistence task
    auto_start_monitoring: bool = False  # Auto-start heartbeat monitoring
    starvation_threshold: int = 3600
    acknowledgment_timeout: int = 5
    overflow_strategy: str = "displace_oldest_low_priority"  # Strategy when queue full
    priority_boost_interval: int = 60  # Boost priority every N seconds
    priority_boost_amount: float = 0.1  # Amount to boost priority by
    
    def __post_init__(self):
        """Initialize and validate configuration."""
        if self.priority_quotas is None:
            self.priority_quotas = {"high": 1000, "medium": 5000, "low": 4000}
        
        if self.retry_policy is None:
            self.retry_policy = {
                "max_attempts": 3,
                "backoff_base": 2,
                "backoff_max": 300,
                "send_to_dlq": True
            }
        
        # Validation
        if self.max_queue_size <= 0:
            raise ValueError("max_queue_size must be positive")
        
        # Check priority quotas
        required_priorities = {"high", "medium", "low"}
        if set(self.priority_quotas.keys()) != required_priorities:
            raise ValueError("Priority quotas must include high, medium, low")
        
        quota_sum = sum(self.priority_quotas.values())
        if quota_sum > self.max_queue_size:
            raise ValueError("Priority quotas sum exceeds max_queue_size")


@dataclass
class TaskAssignment:
    """Task assignment to a worker."""
    
    task: Task
    assignment_id: str
    deadline: float
    acknowledgment_required_by: float


class TaskQueue:
    """Priority-based task queue for agent coordination."""
    
    def __init__(self, config: Optional[QueueConfig] = None):
        """Initialize the task queue.
        
        Args:
            config: Queue configuration, uses defaults if None
        """
        self.config = config or QueueConfig()
        self.is_running = False
        self.is_paused = False
        
        # Priority queues (3=high, 2=medium, 1=low)
        self._queues: Dict[int, deque] = {
            3: deque(),  # High priority
            2: deque(),  # Medium priority
            1: deque()   # Low priority
        }
        
        # Task tracking
        self._tasks: Dict[str, Task] = {}
        self._task_states: Dict[str, TaskState] = {}
        self._task_retry_counts: Dict[str, int] = {}
        self._task_failure_history: Dict[str, list] = {}
        self._task_enqueue_times: Dict[str, datetime] = {}  # Track when tasks were enqueued
        self._task_boost_levels: Dict[str, float] = {}  # Track priority boosts
        
        # Worker tracking
        self._workers: Set[str] = set()
        self._active_workers: Set[str] = set()
        self._worker_info: Dict[str, WorkerInfo] = {}
        
        # Assignment tracking
        self._active_assignments: Dict[str, TaskAssignment] = {}
        self._assignment_to_task: Dict[str, str] = {}
        self._assignment_to_worker: Dict[str, str] = {}
        
        # Capability matching
        self._capability_matching_enabled = False
        
        # Heartbeat monitoring
        self._monitoring_task: Optional[asyncio.Task] = None
        self._monitoring_stopped = False
        
        # Task progress tracking
        self._task_progress: Dict[str, Dict[str, Any]] = {}
        
        # Persistence
        self._persistence_task: Optional[asyncio.Task] = None
        self._persistence_stopped = False
        self._persistence_version = "1.0.0"
        
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
        
        # Track initialization status
        self._initialized = False
        
        # Dead letter queue
        self._dead_letter_queue: deque = deque()
        self._dlq_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Overflow tracking
        self._displaced_tasks: int = 0
        self._displacement_by_priority: Dict[str, int] = {"low": 0, "medium": 0, "high": 0}
        
        # Starvation prevention
        self._priority_boost_task: Optional[asyncio.Task] = None
        self._priority_boost_stopped = False
    
    async def initialize(self) -> None:
        """Initialize the queue, optionally recovering state and starting background tasks.
        
        This method should be called after creating the queue if you want to:
        - Recover state from a previous run (if auto_recovery is True)
        - Start automatic persistence (if auto_start_persistence is True)
        - Start heartbeat monitoring (if auto_start_monitoring is True)
        """
        if self._initialized:
            return
        
        # Recover state if configured
        if self.config.auto_recovery and self.config.persistence_path:
            try:
                await self.load_state()
            except json.JSONDecodeError:
                # Log error but continue with empty queue
                print(f"Error: Corrupted state file at {self.config.persistence_path}")
            except Exception as e:
                # Log other errors but continue
                print(f"Error loading state: {e}")
        
        # Start background tasks if configured
        if self.config.auto_start_persistence:
            await self.start_persistence()
        
        if self.config.auto_start_monitoring:
            if not self._monitoring_task or self._monitoring_task.done():
                self._monitoring_stopped = False
                self._monitoring_task = asyncio.create_task(self.monitor_heartbeats())
        
        self._initialized = True
    
    def size(self) -> int:
        """Get total number of tasks in queue."""
        return sum(len(q) for q in self._queues.values())
    
    def size_by_priority(self, priority: str) -> int:
        """Get number of tasks for a specific priority level."""
        priority_map = {"high": 3, "medium": 2, "low": 1}
        priority_num = priority_map.get(priority)
        if priority_num is None:
            return 0
        return len(self._queues.get(priority_num, []))
    
    def active_workers(self) -> int:
        """Get number of active workers."""
        return len(self._active_workers)
    
    def idle_workers(self) -> int:
        """Get number of idle workers."""
        return len(self._workers - self._active_workers)
    
    async def enqueue(self, task: Task) -> str:
        """Add task to the queue.
        
        Args:
            task: Task to enqueue
            
        Returns:
            Task ID
            
        Raises:
            ValueError: If task is invalid
            RuntimeError: If queue is at capacity
        """
        # Validate task
        if task.priority <= 0:
            raise ValueError("Priority must be positive")
        
        async with self._lock:
            # Map priority to queue (1=low, 2=medium, 3=high)
            priority_queue = self._queues.get(task.priority)
            if priority_queue is None:
                raise ValueError(f"Invalid priority: {task.priority}")
            
            priority_name = {1: "low", 2: "medium", 3: "high"}.get(task.priority)
            
            # Track if we've already displaced a task
            displaced_for_capacity = False
            
            # Check if queue is at capacity
            if self.size() >= self.config.max_queue_size:
                # Handle overflow based on strategy
                if self.config.overflow_strategy == "displace_oldest_low_priority" and task.priority > 1:
                    # Try to displace a lower priority task
                    displaced = await self._displace_low_priority_task(task.priority)
                    if not displaced:
                        raise RuntimeError("Queue at capacity and no tasks can be displaced")
                    displaced_for_capacity = True
                else:
                    raise RuntimeError("Queue at capacity")
            
            # Check priority quota only if we didn't displace due to total capacity
            # (because displacement already made room)
            if not displaced_for_capacity and len(priority_queue) >= self.config.priority_quotas.get(priority_name, 0):
                # For high priority tasks, try to displace lower priority
                if task.priority > 1 and self.config.overflow_strategy == "displace_oldest_low_priority":
                    displaced = await self._displace_low_priority_task(task.priority)
                    if not displaced:
                        raise RuntimeError(f"Queue at capacity for {priority_name} priority")
                else:
                    raise RuntimeError(f"Queue at capacity for {priority_name} priority")
            
            # Add to queue
            task_id = str(task.id)
            self._tasks[task_id] = task
            self._task_states[task_id] = TaskState.PENDING
            self._task_enqueue_times[task_id] = datetime.utcnow()
            self._task_boost_levels[task_id] = 0.0
            priority_queue.append(task_id)
            
            return task_id
    
    async def dequeue(self, worker_id: str) -> Optional[TaskAssignment]:
        """Get next task for a worker.
        
        Args:
            worker_id: ID of the requesting worker
            
        Returns:
            TaskAssignment if available, None otherwise
        """
        async with self._lock:
            # Register worker if new (backward compatibility)
            if worker_id not in self._workers:
                self._workers.add(worker_id)
                self._worker_info[worker_id] = WorkerInfo(
                    id=worker_id,
                    capabilities={},
                    state="idle"
                )
            
            # Apply priority boosts for starving tasks
            await self._apply_priority_boosts()
            
            # Collect all pending tasks with their effective priorities
            candidate_tasks = []
            for priority in [3, 2, 1]:
                queue = self._queues[priority]
                for task_id in queue:
                    task = self._tasks.get(task_id)
                    if task and self._can_worker_handle_task(worker_id, task):
                        boost = self._task_boost_levels.get(task_id, 0.0)
                        effective_priority = task.priority + boost
                        candidate_tasks.append((task_id, task, effective_priority))
            
            # Sort by effective priority (highest first)
            candidate_tasks.sort(key=lambda x: x[2], reverse=True)
            
            if candidate_tasks:
                # Take the highest priority task
                task_id, task, _ = candidate_tasks[0]
                
                # Remove from its queue
                priority_queue = self._queues[task.priority]
                priority_queue.remove(task_id)
                
                # Update task state
                task.assign(worker_id)
                self._task_states[task_id] = TaskState.ASSIGNED
                self._active_workers.add(worker_id)
                
                # Update worker state
                if worker_id in self._worker_info:
                    self._worker_info[worker_id].state = "active"
                    self._worker_info[worker_id].assigned_task = task_id
                    self._worker_info[worker_id].last_heartbeat = datetime.utcnow()
                
                # Create assignment
                now = datetime.utcnow().timestamp()
                assignment_id = str(uuid4())
                assignment = TaskAssignment(
                    task=task,
                    assignment_id=assignment_id,
                    deadline=now + self.config.worker_timeout,
                    acknowledgment_required_by=now + self.config.acknowledgment_timeout
                )
                
                # Track assignment
                self._active_assignments[assignment_id] = assignment
                self._assignment_to_task[assignment_id] = task_id
                self._assignment_to_worker[assignment_id] = worker_id
                
                return assignment
            
            return None
    
    async def peek(self) -> Optional[Task]:
        """Peek at next task without removing it.
        
        Returns:
            Next task if available, None otherwise
        """
        async with self._lock:
            # Find highest priority task
            for priority in [3, 2, 1]:  # High to low
                queue = self._queues[priority]
                if queue:
                    task_id = queue[0]  # Peek without removing
                    return self._tasks.get(task_id)
            
            return None
    
    def get_task_state(self, task_id: str) -> Optional[TaskState]:
        """Get current state of a task.
        
        Args:
            task_id: Task ID to check
            
        Returns:
            TaskState if task exists, None otherwise
        """
        return self._task_states.get(str(task_id))
    
    async def register_worker(self, worker_id: str, capabilities: Dict[str, Any]) -> bool:
        """Register a worker with the queue.
        
        Args:
            worker_id: Unique identifier for the worker
            capabilities: Worker capabilities (agent_types, etc.)
            
        Returns:
            True if registration successful
        """
        async with self._lock:
            # Create or update worker info
            self._worker_info[worker_id] = WorkerInfo(
                id=worker_id,
                capabilities=capabilities,
                state="idle",
                last_heartbeat=datetime.utcnow()
            )
            self._workers.add(worker_id)
            
            # If updating existing worker, maintain active state if applicable
            if worker_id in self._active_workers:
                self._worker_info[worker_id].state = "active"
            
            return True
    
    async def unregister_worker(self, worker_id: str) -> bool:
        """Unregister a worker from the queue.
        
        Args:
            worker_id: Worker to unregister
            
        Returns:
            True if worker was registered and removed, False otherwise
        """
        async with self._lock:
            if worker_id not in self._workers:
                return False
            
            # Remove from all tracking structures
            self._workers.discard(worker_id)
            self._active_workers.discard(worker_id)
            self._worker_info.pop(worker_id, None)
            
            # TODO: Handle any tasks assigned to this worker
            
            return True
    
    def is_worker_registered(self, worker_id: str) -> bool:
        """Check if a worker is registered.
        
        Args:
            worker_id: Worker to check
            
        Returns:
            True if worker is registered
        """
        return worker_id in self._workers
    
    def get_registered_workers(self) -> Set[str]:
        """Get set of all registered worker IDs.
        
        Returns:
            Set of worker IDs
        """
        return self._workers.copy()
    
    async def get_worker_status(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a worker.
        
        Args:
            worker_id: Worker to get status for
            
        Returns:
            Worker status dict or None if not found
        """
        async with self._lock:
            worker_info = self._worker_info.get(worker_id)
            if not worker_info:
                return None
            
            return {
                "id": worker_info.id,
                "state": worker_info.state,
                "capabilities": worker_info.capabilities,
                "last_heartbeat": worker_info.last_heartbeat,
                "assigned_task": worker_info.assigned_task,
                "registration_time": worker_info.registration_time
            }
    
    async def get_workers_by_state(self, state: str) -> Set[str]:
        """Get workers in a specific state.
        
        Args:
            state: State to filter by (idle, active, failed)
            
        Returns:
            Set of worker IDs in the specified state
        """
        async with self._lock:
            return {
                worker_id 
                for worker_id, info in self._worker_info.items()
                if info.state == state
            }
    
    async def get_workers_by_capability(self, capability: str) -> Set[str]:
        """Get workers with a specific capability.
        
        Args:
            capability: Capability to filter by (e.g., agent type)
            
        Returns:
            Set of worker IDs with the capability
        """
        async with self._lock:
            result = set()
            for worker_id, info in self._worker_info.items():
                agent_types = info.capabilities.get("agent_types", [])
                if capability in agent_types:
                    result.add(worker_id)
            return result
    
    async def enable_capability_matching(self) -> None:
        """Enable capability-based task matching."""
        async with self._lock:
            self._capability_matching_enabled = True
    
    async def disable_capability_matching(self) -> None:
        """Disable capability-based task matching."""
        async with self._lock:
            self._capability_matching_enabled = False
    
    def _can_worker_handle_task(self, worker_id: str, task: Task) -> bool:
        """Check if worker can handle the given task type.
        
        Args:
            worker_id: Worker to check
            task: Task to check compatibility
            
        Returns:
            True if worker can handle task type
        """
        if not self._capability_matching_enabled:
            return True
        
        worker_info = self._worker_info.get(worker_id)
        if not worker_info:
            return False
        
        # Map task type to required agent type
        task_to_agent_mapping = {
            TaskType.GENERATE_HYPOTHESIS: "Generation",
            TaskType.REFLECT_ON_HYPOTHESIS: "Reflection",
            TaskType.RANK_HYPOTHESES: "Ranking",
            TaskType.EVOLVE_HYPOTHESIS: "Evolution",
            TaskType.FIND_SIMILAR_HYPOTHESES: "Proximity",
            TaskType.META_REVIEW: "MetaReview"
        }
        
        required_agent_type = task_to_agent_mapping.get(task.task_type)
        if not required_agent_type:
            return True  # Unknown task type, allow any worker
        
        agent_types = worker_info.capabilities.get("agent_types", [])
        return required_agent_type in agent_types
    
    async def acknowledge_task(self, worker_id: str, assignment_id: str) -> bool:
        """Acknowledge task assignment.
        
        Args:
            worker_id: Worker acknowledging
            assignment_id: Assignment to acknowledge
            
        Returns:
            True if acknowledgment successful
        """
        async with self._lock:
            # Check assignment exists and belongs to worker
            if assignment_id not in self._active_assignments:
                return False
            
            if self._assignment_to_worker.get(assignment_id) != worker_id:
                return False
            
            # Update task state to executing
            task_id = self._assignment_to_task.get(assignment_id)
            if task_id and task_id in self._task_states:
                self._task_states[task_id] = TaskState.EXECUTING
                return True
            
            return False
    
    async def complete_task(self, worker_id: str, task_id: str, result: Dict[str, Any]) -> bool:
        """Mark task as completed.
        
        Args:
            worker_id: Worker completing the task
            task_id: Task to complete
            result: Task execution result
            
        Returns:
            True if completion successful
        """
        async with self._lock:
            # Verify worker has this task
            task = self._tasks.get(task_id)
            if not task or task.assigned_to != worker_id:
                return False
            
            # Update task state and result
            self._task_states[task_id] = TaskState.COMPLETED
            task.state = TaskState.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow()
            
            # Clear assignment
            for assignment_id, tid in self._assignment_to_task.items():
                if tid == task_id:
                    del self._active_assignments[assignment_id]
                    del self._assignment_to_task[assignment_id]
                    del self._assignment_to_worker[assignment_id]
                    break
            
            # Update worker state
            if worker_id in self._worker_info:
                self._worker_info[worker_id].state = "idle"
                self._worker_info[worker_id].assigned_task = None
                self._active_workers.discard(worker_id)
            
            return True
    
    async def fail_task(self, worker_id: str, task_id: str, error: Dict[str, Any]) -> bool:
        """Mark task as failed.
        
        Args:
            worker_id: Worker reporting failure
            task_id: Task that failed
            error: Error details including retryable flag
            
        Returns:
            True if failure recorded successfully
        """
        async with self._lock:
            # Verify worker has this task
            task = self._tasks.get(task_id)
            if not task or task.assigned_to != worker_id:
                return False
            
            # Record failure
            if task_id not in self._task_failure_history:
                self._task_failure_history[task_id] = []
            self._task_failure_history[task_id].append({
                "worker_id": worker_id,
                "error": error,
                "timestamp": datetime.utcnow()
            })
            
            # Clear assignment
            for assignment_id, tid in self._assignment_to_task.items():
                if tid == task_id:
                    del self._active_assignments[assignment_id]
                    del self._assignment_to_task[assignment_id]
                    del self._assignment_to_worker[assignment_id]
                    break
            
            # Update worker state
            if worker_id in self._worker_info:
                self._worker_info[worker_id].state = "idle"
                self._worker_info[worker_id].assigned_task = None
                self._active_workers.discard(worker_id)
            
            # Handle retry logic
            retry_count = self._task_retry_counts.get(task_id, 0)
            max_retries = self.config.retry_policy.get("max_attempts", 3)
            
            if error.get("retryable", False) and retry_count < max_retries - 1:
                # Reset task for retry
                task.state = TaskState.PENDING
                task.assigned_to = None
                task.assigned_at = None
                self._task_states[task_id] = TaskState.PENDING
                self._task_retry_counts[task_id] = retry_count + 1
                
                # Re-queue the task
                priority_queue = self._queues.get(task.priority)
                if priority_queue is not None:
                    priority_queue.append(task_id)
            else:
                # Permanent failure or max retries reached
                self._task_states[task_id] = TaskState.FAILED
                
                # Send to DLQ if configured
                if self.config.retry_policy.get("send_to_dlq", False):
                    self._dead_letter_queue.append(task_id)
                    
                    # Determine reason for DLQ
                    if not error.get("retryable", False):
                        dlq_reason = "non_retryable_error"
                    else:
                        dlq_reason = "retry_exhaustion"
                    
                    self._dlq_metadata[task_id] = {
                        "reason": dlq_reason,
                        "error": error,
                        "retry_count": retry_count + 1,
                        "timestamp": datetime.utcnow()
                    }
            
            return True
    
    async def heartbeat(self, worker_id: str, progress: Optional[Dict[str, Any]] = None) -> bool:
        """Update worker heartbeat timestamp.
        
        Args:
            worker_id: Worker sending heartbeat
            progress: Optional task progress update
            
        Returns:
            True if heartbeat recorded successfully
        """
        async with self._lock:
            if worker_id not in self._worker_info:
                return False
            
            # Update heartbeat timestamp
            self._worker_info[worker_id].last_heartbeat = datetime.utcnow()
            
            # If worker was failed, recover it
            if self._worker_info[worker_id].state == "failed":
                self._worker_info[worker_id].state = "idle"
            
            # Update task progress if provided
            if progress and self._worker_info[worker_id].assigned_task:
                task_id = self._worker_info[worker_id].assigned_task
                self._task_progress[task_id] = progress
            
            return True
    
    async def check_dead_workers(self) -> Set[str]:
        """Check for workers that haven't sent heartbeats.
        
        Returns:
            Set of worker IDs that are considered dead
        """
        async with self._lock:
            dead_workers = set()
            now = datetime.utcnow()
            timeout = timedelta(seconds=self.config.heartbeat_timeout)
            
            for worker_id, info in self._worker_info.items():
                if info.state != "failed":  # Don't recheck already failed workers
                    time_since_heartbeat = now - info.last_heartbeat
                    if time_since_heartbeat > timeout:
                        dead_workers.add(worker_id)
            
            return dead_workers
    
    async def process_dead_workers(self) -> None:
        """Process workers that are considered dead."""
        dead_workers = await self.check_dead_workers()
        
        async with self._lock:
            for worker_id in dead_workers:
                # Mark worker as failed
                self._worker_info[worker_id].state = "failed"
                
                # Handle any assigned task
                assigned_task_id = self._worker_info[worker_id].assigned_task
                if assigned_task_id:
                    task = self._tasks.get(assigned_task_id)
                    if task:
                        # Reset task state
                        task.state = TaskState.PENDING
                        task.assigned_to = None
                        task.assigned_at = None
                        self._task_states[assigned_task_id] = TaskState.PENDING
                        
                        # Re-queue the task
                        priority_queue = self._queues.get(task.priority)
                        if priority_queue is not None:
                            priority_queue.append(assigned_task_id)
                        
                        # Clear assignment tracking
                        for assignment_id, tid in list(self._assignment_to_task.items()):
                            if tid == assigned_task_id:
                                del self._active_assignments[assignment_id]
                                del self._assignment_to_task[assignment_id]
                                del self._assignment_to_worker[assignment_id]
                                break
                    
                    # Clear worker task assignment
                    self._worker_info[worker_id].assigned_task = None
                    self._active_workers.discard(worker_id)
    
    async def monitor_heartbeats(self) -> None:
        """Background task to monitor worker heartbeats."""
        while not self._monitoring_stopped:
            try:
                await self.process_dead_workers()
                await asyncio.sleep(self.config.heartbeat_check_interval)
            except Exception as e:
                # Log error but continue monitoring
                print(f"Error in heartbeat monitoring: {e}")
                await asyncio.sleep(self.config.heartbeat_check_interval)
    
    def stop_monitoring(self) -> None:
        """Stop the heartbeat monitoring task."""
        self._monitoring_stopped = True
    
    async def get_heartbeat_metrics(self) -> Dict[str, Any]:
        """Get metrics about worker heartbeats.
        
        Returns:
            Dictionary with heartbeat metrics
        """
        async with self._lock:
            total_workers = len(self._worker_info)
            healthy_workers = sum(1 for info in self._worker_info.values() if info.state != "failed")
            failed_workers = sum(1 for info in self._worker_info.values() if info.state == "failed")
            
            # Calculate average heartbeat age
            now = datetime.utcnow()
            heartbeat_ages = []
            for info in self._worker_info.values():
                if info.state != "failed":
                    age = (now - info.last_heartbeat).total_seconds()
                    heartbeat_ages.append(age)
            
            avg_heartbeat_age = sum(heartbeat_ages) / len(heartbeat_ages) if heartbeat_ages else 0
            
            return {
                "total_workers": total_workers,
                "healthy_workers": healthy_workers,
                "failed_workers": failed_workers,
                "average_heartbeat_age": avg_heartbeat_age
            }
    
    async def check_assignment_timeouts(self) -> None:
        """Check for timed out task assignments."""
        async with self._lock:
            now = datetime.utcnow().timestamp()
            timed_out_assignments = []
            
            # Find timed out assignments
            for assignment_id, assignment in self._active_assignments.items():
                if assignment.acknowledgment_required_by < now:
                    # Assignment not acknowledged in time
                    task_id = self._assignment_to_task.get(assignment_id)
                    if task_id and self._task_states.get(task_id) == TaskState.ASSIGNED:
                        timed_out_assignments.append((assignment_id, task_id))
            
            # Process timeouts
            for assignment_id, task_id in timed_out_assignments:
                task = self._tasks.get(task_id)
                if task:
                    # Reset task state
                    task.state = TaskState.PENDING
                    task.assigned_to = None
                    task.assigned_at = None
                    self._task_states[task_id] = TaskState.PENDING
                    
                    # Re-queue the task
                    priority_queue = self._queues.get(task.priority)
                    if priority_queue is not None:
                        priority_queue.append(task_id)
                    
                    # Clear assignment
                    worker_id = self._assignment_to_worker.get(assignment_id)
                    del self._active_assignments[assignment_id]
                    del self._assignment_to_task[assignment_id]
                    del self._assignment_to_worker[assignment_id]
                    
                    # Update worker state
                    if worker_id and worker_id in self._worker_info:
                        self._worker_info[worker_id].state = "idle"
                        self._worker_info[worker_id].assigned_task = None
                        self._active_workers.discard(worker_id)
    
    async def get_task_info(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a task.
        
        Args:
            task_id: Task to get info for
            
        Returns:
            Task information dict or None if not found
        """
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None
            
            return {
                "id": task_id,
                "type": task.task_type.value,
                "priority": task.priority,
                "state": self._task_states.get(task_id, task.state).value,
                "assigned_to": task.assigned_to,
                "assigned_at": task.assigned_at,
                "retry_count": self._task_retry_counts.get(task_id, 0),
                "failure_history": self._task_failure_history.get(task_id, []),
                "progress": self._task_progress.get(task_id, {})
            }
    
    async def get_queue_statistics(self) -> Dict[str, Any]:
        """Get overall queue statistics.
        
        Returns:
            Dictionary with queue statistics
        """
        async with self._lock:
            # Count tasks by priority
            depth_by_priority = {
                "high": len(self._queues[3]),
                "medium": len(self._queues[2]),
                "low": len(self._queues[1])
            }
            
            # Count tasks by state
            task_states = {
                "pending": 0,
                "assigned": 0,
                "executing": 0,
                "completed": 0,
                "failed": 0
            }
            
            for state in self._task_states.values():
                task_states[state.value] += 1
            
            # Count workers by state
            worker_stats = {
                "total": len(self._workers),
                "idle": len(self._workers - self._active_workers),
                "active": len(self._active_workers),
                "failed": sum(1 for info in self._worker_info.values() if info.state == "failed")
            }
            
            # Calculate capacity information
            current_size = self.size()
            max_size = self.config.max_queue_size
            capacity_percentage = (current_size / max_size * 100) if max_size > 0 else 0
            
            # Determine capacity status
            if capacity_percentage >= 100:
                capacity_status = "full"
            elif capacity_percentage >= 95:
                capacity_status = "critical"
            elif capacity_percentage >= 80:
                capacity_status = "warning"
            else:
                capacity_status = "normal"
            
            return {
                "total_tasks": current_size,
                "depth_by_priority": depth_by_priority,
                "task_states": task_states,
                "worker_stats": worker_stats,
                "active_assignments": len(self._active_assignments),
                "capacity_percentage": capacity_percentage,
                "capacity_status": capacity_status,
                "displaced_tasks": self._displaced_tasks
            }
    
    async def get_throughput_metrics(self) -> Dict[str, Any]:
        """Calculate task throughput metrics.
        
        Returns:
            Dictionary with throughput metrics
        """
        async with self._lock:
            now = datetime.utcnow()
            one_minute_ago = now - timedelta(minutes=1)
            one_hour_ago = now - timedelta(hours=1)
            
            # Count completed tasks
            completed_last_minute = 0
            completed_last_hour = 0
            
            for task_id, task in self._tasks.items():
                if task.completed_at:
                    if task.completed_at >= one_minute_ago:
                        completed_last_minute += 1
                    if task.completed_at >= one_hour_ago:
                        completed_last_hour += 1
            
            throughput_per_minute = completed_last_minute
            
            return {
                "completed_last_minute": completed_last_minute,
                "completed_last_hour": completed_last_hour,
                "throughput_per_minute": throughput_per_minute,
                "active_tasks": len(self._active_assignments)
            }
    
    async def get_wait_time_statistics(self) -> Dict[str, Any]:
        """Calculate average task wait times.
        
        Returns:
            Dictionary with wait time statistics
        """
        async with self._lock:
            wait_times = []
            wait_times_by_priority = {"high": [], "medium": [], "low": []}
            
            for task_id, task in self._tasks.items():
                if task.assigned_at and task.created_at:
                    wait_time = (task.assigned_at - task.created_at).total_seconds()
                    wait_times.append(wait_time)
                    
                    priority_name = {1: "low", 2: "medium", 3: "high"}.get(task.priority)
                    if priority_name:
                        wait_times_by_priority[priority_name].append(wait_time)
            
            # Calculate averages
            avg_overall = sum(wait_times) / len(wait_times) if wait_times else 0
            avg_by_priority = {}
            
            for priority, times in wait_times_by_priority.items():
                avg_by_priority[priority] = sum(times) / len(times) if times else 0
            
            return {
                "average_wait_time": {
                    "overall": avg_overall,
                    "by_priority": avg_by_priority
                },
                "sample_size": len(wait_times)
            }
    
    async def get_retry_statistics(self) -> Dict[str, Any]:
        """Get statistics on task retries.
        
        Returns:
            Dictionary with retry statistics
        """
        async with self._lock:
            total_retries = sum(self._task_retry_counts.values())
            tasks_with_retries = len(self._task_retry_counts)
            max_retry_count = max(self._task_retry_counts.values()) if self._task_retry_counts else 0
            
            # Count retries by task type
            retry_by_type = defaultdict(int)
            for task_id, retry_count in self._task_retry_counts.items():
                task = self._tasks.get(task_id)
                if task:
                    retry_by_type[task.task_type.value] += retry_count
            
            return {
                "total_retries": total_retries,
                "tasks_with_retries": tasks_with_retries,
                "max_retry_count": max_retry_count,
                "retry_by_task_type": dict(retry_by_type)
            }
    
    async def get_capacity_statistics(self) -> Dict[str, Any]:
        """Get queue capacity statistics.
        
        Returns:
            Dictionary with capacity information
        """
        async with self._lock:
            current_size = self.size()
            max_capacity = self.config.max_queue_size
            utilization = (current_size / max_capacity * 100) if max_capacity > 0 else 0
            
            # Capacity by priority
            capacity_by_priority = {}
            for priority, (name, limit) in [(3, ("high", self.config.priority_quotas["high"])),
                                           (2, ("medium", self.config.priority_quotas["medium"])),
                                           (1, ("low", self.config.priority_quotas["low"]))]:
                used = len(self._queues[priority])
                capacity_by_priority[name] = {
                    "used": used,
                    "limit": limit,
                    "utilization_percent": (used / limit * 100) if limit > 0 else 0
                }
            
            # Warnings
            warnings = {
                "near_capacity": utilization >= 80,
                "at_capacity": utilization >= 100,
                "priority_at_limit": any(
                    info["utilization_percent"] >= 100 
                    for info in capacity_by_priority.values()
                )
            }
            
            return {
                "max_capacity": max_capacity,
                "current_size": current_size,
                "utilization_percent": utilization,
                "capacity_by_priority": capacity_by_priority,
                "warnings": warnings
            }
    
    async def get_starvation_statistics(self) -> Dict[str, Any]:
        """Get statistics on starved tasks.
        
        Returns:
            Dictionary with starvation information
        """
        async with self._lock:
            now = datetime.utcnow()
            starvation_threshold = timedelta(seconds=self.config.starvation_threshold)
            
            starved_tasks = 0
            starved_task_ids = []
            oldest_task = None
            oldest_wait_time = 0
            
            # Check pending tasks for starvation
            for priority in [1, 2, 3]:  # Check all priorities
                for task_id in self._queues[priority]:
                    task = self._tasks.get(task_id)
                    if task and task.created_at:
                        wait_time = now - task.created_at
                        if wait_time > starvation_threshold:
                            starved_tasks += 1
                            starved_task_ids.append(task_id)
                        
                        wait_seconds = wait_time.total_seconds()
                        if wait_seconds > oldest_wait_time:
                            oldest_wait_time = wait_seconds
                            oldest_task = {
                                "task_id": task_id,
                                "priority": {1: "low", 2: "medium", 3: "high"}[priority],
                                "wait_time": wait_seconds
                            }
            
            return {
                "starved_tasks": starved_tasks,
                "starved_task_ids": starved_task_ids,
                "oldest_waiting_task": oldest_task,
                "starvation_threshold": self.config.starvation_threshold
            }
    
    async def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics about the queue.
        
        Returns:
            Dictionary with all available metrics
        """
        metrics = {
            "queue_statistics": await self.get_queue_statistics(),
            "throughput_metrics": await self.get_throughput_metrics(),
            "wait_time_statistics": await self.get_wait_time_statistics(),
            "retry_statistics": await self.get_retry_statistics(),
            "capacity_statistics": await self.get_capacity_statistics(),
            "starvation_statistics": await self.get_starvation_statistics(),
            "heartbeat_metrics": await self.get_heartbeat_metrics(),
            "timestamp": datetime.utcnow()
        }
        
        return metrics
    
    async def get_metrics_by_agent_type(self) -> Dict[str, Any]:
        """Get metrics grouped by agent type.
        
        Returns:
            Dictionary with metrics per agent type
        """
        async with self._lock:
            metrics = {}
            
            # Map task types to agent types
            task_to_agent = {
                TaskType.GENERATE_HYPOTHESIS: "Generation",
                TaskType.REFLECT_ON_HYPOTHESIS: "Reflection",
                TaskType.RANK_HYPOTHESES: "Ranking",
                TaskType.EVOLVE_HYPOTHESIS: "Evolution",
                TaskType.FIND_SIMILAR_HYPOTHESES: "Proximity",
                TaskType.META_REVIEW: "MetaReview"
            }
            
            # Initialize metrics for each agent type
            for agent_type in task_to_agent.values():
                metrics[agent_type] = {
                    "pending_tasks": 0,
                    "executing_tasks": 0,
                    "completed_tasks": 0,
                    "failed_tasks": 0,
                    "capable_workers": 0
                }
            
            # Count tasks by type and state
            for task_id, task in self._tasks.items():
                agent_type = task_to_agent.get(task.task_type)
                if agent_type:
                    state = self._task_states.get(task_id, TaskState.PENDING)
                    if state == TaskState.PENDING:
                        metrics[agent_type]["pending_tasks"] += 1
                    elif state == TaskState.EXECUTING:
                        metrics[agent_type]["executing_tasks"] += 1
                    elif state == TaskState.COMPLETED:
                        metrics[agent_type]["completed_tasks"] += 1
                    elif state == TaskState.FAILED:
                        metrics[agent_type]["failed_tasks"] += 1
            
            # Count capable workers
            for worker_id, info in self._worker_info.items():
                agent_types = info.capabilities.get("agent_types", [])
                for agent_type in agent_types:
                    if agent_type in metrics:
                        metrics[agent_type]["capable_workers"] += 1
            
            return metrics
    
    async def save_state(self) -> None:
        """Save current queue state to disk.
        
        Raises:
            IOError: If unable to write state file
        """
        if not self.config.persistence_path:
            return
        
        async with self._lock:
            # Prepare state for serialization
            state = {
                "version": self._persistence_version,
                "timestamp": datetime.utcnow().isoformat(),
                "queues": {
                    "high": list(self._queues[3]),
                    "medium": list(self._queues[2]),
                    "low": list(self._queues[1])
                },
                "tasks": {},
                "task_states": {},
                "task_retry_counts": dict(self._task_retry_counts),
                "task_failure_history": {},
                "task_progress": dict(self._task_progress),
                "workers": {},
                "assignments": {},
                "capability_matching_enabled": self._capability_matching_enabled
            }
            
            # Serialize tasks
            for task_id, task in self._tasks.items():
                state["tasks"][task_id] = {
                    "id": str(task.id),
                    "task_type": task.task_type.value,
                    "priority": task.priority,
                    "state": task.state.value,
                    "payload": task.payload,
                    "assigned_to": task.assigned_to,
                    "result": task.result,
                    "error": task.error,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "assigned_at": task.assigned_at.isoformat() if task.assigned_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
            
            # Serialize task states
            for task_id, task_state in self._task_states.items():
                state["task_states"][task_id] = task_state.value
            
            # Serialize failure history with datetime conversion
            for task_id, failures in self._task_failure_history.items():
                serialized_failures = []
                for failure in failures:
                    serialized_failure = failure.copy()
                    if 'timestamp' in serialized_failure and isinstance(serialized_failure['timestamp'], datetime):
                        serialized_failure['timestamp'] = serialized_failure['timestamp'].isoformat()
                    serialized_failures.append(serialized_failure)
                state["task_failure_history"][task_id] = serialized_failures
            
            # Serialize workers
            for worker_id, worker_info in self._worker_info.items():
                state["workers"][worker_id] = {
                    "id": worker_info.id,
                    "capabilities": worker_info.capabilities,
                    "state": worker_info.state,
                    "last_heartbeat": worker_info.last_heartbeat.isoformat(),
                    "assigned_task": worker_info.assigned_task,
                    "registration_time": worker_info.registration_time.isoformat()
                }
                
            # Serialize active assignments
            for assignment_id, assignment in self._active_assignments.items():
                state["assignments"][assignment_id] = {
                    "task_id": str(assignment.task.id),
                    "assignment_id": assignment.assignment_id,
                    "deadline": assignment.deadline,
                    "acknowledgment_required_by": assignment.acknowledgment_required_by,
                    "worker_id": self._assignment_to_worker.get(assignment_id)
                }
            
            # Write to file atomically
            import json
            import os
            temp_path = f"{self.config.persistence_path}.tmp"
            
            with open(temp_path, 'w') as f:
                json.dump(state, f, indent=2)
            
            # Atomic rename
            os.replace(temp_path, self.config.persistence_path)
    
    async def load_state(self) -> None:
        """Load queue state from disk.
        
        Raises:
            IOError: If unable to read state file
            ValueError: If state file version is incompatible
            json.JSONDecodeError: If state file is corrupted
        """
        if not self.config.persistence_path:
            return
        
        import os
        if not os.path.exists(self.config.persistence_path):
            # No state to load
            return
        
        import json
        with open(self.config.persistence_path, 'r') as f:
            state = json.load(f)
        
        # Check version compatibility
        if state.get("version") != self._persistence_version:
            raise ValueError(f"Incompatible persistence version: {state.get('version')}")
        
        async with self._lock:
            # Clear current state
            self._queues = {3: deque(), 2: deque(), 1: deque()}
            self._tasks.clear()
            self._task_states.clear()
            self._task_retry_counts.clear()
            self._task_failure_history.clear()
            self._task_progress.clear()
            self._workers.clear()
            self._active_workers.clear()
            self._worker_info.clear()
            self._active_assignments.clear()
            self._assignment_to_task.clear()
            self._assignment_to_worker.clear()
            
            # Restore tasks
            for task_id, task_data in state.get("tasks", {}).items():
                task = Task(
                    id=UUID(task_data["id"]),
                    task_type=TaskType(task_data["task_type"]),
                    priority=task_data["priority"],
                    state=TaskState(task_data["state"]),
                    payload=task_data["payload"],
                    assigned_to=task_data["assigned_to"],
                    result=task_data["result"],
                    error=task_data["error"],
                    created_at=datetime.fromisoformat(task_data["created_at"]) if task_data["created_at"] else None,
                    assigned_at=datetime.fromisoformat(task_data["assigned_at"]) if task_data["assigned_at"] else None,
                    completed_at=datetime.fromisoformat(task_data["completed_at"]) if task_data["completed_at"] else None
                )
                self._tasks[task_id] = task
            
            # Restore task states
            for task_id, task_state in state.get("task_states", {}).items():
                self._task_states[task_id] = TaskState(task_state)
            
            # Restore queues
            for priority_name, task_ids in state.get("queues", {}).items():
                priority = {"high": 3, "medium": 2, "low": 1}.get(priority_name)
                if priority:
                    self._queues[priority].extend(task_ids)
            
            # Restore retry counts and failure history
            self._task_retry_counts.update(state.get("task_retry_counts", {}))
            
            # Restore failure history with datetime conversion
            for task_id, failures in state.get("task_failure_history", {}).items():
                deserialized_failures = []
                for failure in failures:
                    deserialized_failure = failure.copy()
                    if 'timestamp' in deserialized_failure and isinstance(deserialized_failure['timestamp'], str):
                        deserialized_failure['timestamp'] = datetime.fromisoformat(deserialized_failure['timestamp'])
                    deserialized_failures.append(deserialized_failure)
                self._task_failure_history[task_id] = deserialized_failures
                
            self._task_progress.update(state.get("task_progress", {}))
            
            # Restore workers
            for worker_id, worker_data in state.get("workers", {}).items():
                worker_info = WorkerInfo(
                    id=worker_data["id"],
                    capabilities=worker_data["capabilities"],
                    state=worker_data["state"],
                    last_heartbeat=datetime.fromisoformat(worker_data["last_heartbeat"]),
                    assigned_task=worker_data["assigned_task"],
                    registration_time=datetime.fromisoformat(worker_data["registration_time"])
                )
                self._worker_info[worker_id] = worker_info
                self._workers.add(worker_id)
                
                if worker_info.state == "active" and worker_info.assigned_task:
                    self._active_workers.add(worker_id)
            
            # Restore assignments
            for assignment_id, assignment_data in state.get("assignments", {}).items():
                task_id = assignment_data["task_id"]
                task = self._tasks.get(task_id)
                if task:
                    assignment = TaskAssignment(
                        task=task,
                        assignment_id=assignment_data["assignment_id"],
                        deadline=assignment_data["deadline"],
                        acknowledgment_required_by=assignment_data["acknowledgment_required_by"]
                    )
                    self._active_assignments[assignment_id] = assignment
                    self._assignment_to_task[assignment_id] = task_id
                    self._assignment_to_worker[assignment_id] = assignment_data["worker_id"]
            
            # Restore other settings
            self._capability_matching_enabled = state.get("capability_matching_enabled", False)
    
    async def start_persistence(self) -> None:
        """Start automatic periodic persistence."""
        if not self.config.persistence_path:
            return
        
        if self._persistence_task and not self._persistence_task.done():
            return  # Already running
        
        self._persistence_stopped = False
        self._persistence_task = asyncio.create_task(self._run_persistence())
    
    async def stop_persistence(self) -> None:
        """Stop automatic periodic persistence."""
        self._persistence_stopped = True
        
        if self._persistence_task:
            self._persistence_task.cancel()
            try:
                await self._persistence_task
            except asyncio.CancelledError:
                pass
            self._persistence_task = None
    
    async def _run_persistence(self) -> None:
        """Background task for automatic persistence."""
        while not self._persistence_stopped:
            try:
                await asyncio.sleep(self.config.persistence_interval)
                await self.save_state()
            except Exception as e:
                # Log error but continue
                print(f"Error in persistence: {e}")
                import traceback
                traceback.print_exc()
    
    async def _displace_low_priority_task(self, incoming_priority: int) -> bool:
        """Displace a lower priority task to make room.
        
        Args:
            incoming_priority: Priority of incoming task
            
        Returns:
            True if a task was displaced, False otherwise
        """
        # Note: This method must be called within a lock
        # Try to displace from lowest priority first
        for priority in [1, 2]:  # Low to medium
            if priority >= incoming_priority:
                break  # Can't displace equal or higher priority
                
            queue = self._queues[priority]
            if queue:
                # Remove oldest task from this priority
                displaced_task_id = queue.popleft()
                displaced_task = self._tasks.pop(displaced_task_id, None)
                
                if displaced_task:
                    # Clean up task state
                    self._task_states.pop(displaced_task_id, None)
                    self._task_enqueue_times.pop(displaced_task_id, None)
                    self._task_boost_levels.pop(displaced_task_id, None)
                    
                    # Track displacement
                    self._displaced_tasks += 1
                    priority_name = {1: "low", 2: "medium", 3: "high"}.get(priority, "unknown")
                    self._displacement_by_priority[priority_name] += 1
                    
                    return True
        
        return False
    
    async def get_overflow_statistics(self) -> Dict[str, Any]:
        """Get statistics about task displacement due to overflow.
        
        Returns:
            Dictionary with overflow statistics
        """
        async with self._lock:
            return {
                "total_displaced": self._displaced_tasks,
                "displacement_by_priority": self._displacement_by_priority.copy()
            }
    
    async def send_heartbeat(self, worker_id: str) -> None:
        """Send heartbeat for a worker.
        
        Args:
            worker_id: ID of the worker
        """
        async with self._lock:
            if worker_id in self._worker_info:
                self._worker_info[worker_id].last_heartbeat = datetime.utcnow()
    
    async def get_worker_status(self, worker_id: str) -> Dict[str, Any]:
        """Get detailed status of a worker.
        
        Args:
            worker_id: ID of the worker
            
        Returns:
            Dictionary with worker status
        """
        async with self._lock:
            if worker_id not in self._worker_info:
                return {"error": "Worker not found"}
            
            worker = self._worker_info[worker_id]
            now = datetime.utcnow()
            time_since_heartbeat = (now - worker.last_heartbeat).total_seconds()
            
            return {
                "id": worker_id,
                "state": worker.state,
                "last_heartbeat": worker.last_heartbeat.isoformat(),
                "time_since_heartbeat": time_since_heartbeat,
                "assigned_task": worker.assigned_task,
                "capabilities": worker.capabilities,
                "failure_reason": "heartbeat_timeout" if worker.state == "failed" and time_since_heartbeat > self.config.heartbeat_timeout else None
            }
    
    async def mark_worker_failed(self, worker_id: str, reason: str) -> None:
        """Mark a worker as failed and reassign its tasks.
        
        Args:
            worker_id: ID of the worker
            reason: Reason for failure
        """
        async with self._lock:
            if worker_id not in self._worker_info:
                return
            
            worker = self._worker_info[worker_id]
            worker.state = "failed"
            
            # Remove from active workers
            self._active_workers.discard(worker_id)
            
            # Find and reassign any tasks assigned to this worker
            reassigned_tasks = []
            for assignment_id, assignment in list(self._active_assignments.items()):
                if assignment.task.assigned_to == worker_id:
                    task_id = str(assignment.task.id)
                    
                    # Reset task state
                    assignment.task.state = TaskState.PENDING
                    assignment.task.assigned_to = None
                    assignment.task.assigned_at = None
                    self._task_states[task_id] = TaskState.PENDING
                    
                    # Track failure for reassignment history
                    if task_id not in self._task_failure_history:
                        self._task_failure_history[task_id] = []
                    self._task_failure_history[task_id].append({
                        "worker_id": worker_id,
                        "reason": "worker_failure",
                        "timestamp": datetime.utcnow()
                    })
                    
                    # Add back to appropriate queue
                    priority_queue = self._queues[assignment.task.priority]
                    priority_queue.appendleft(task_id)  # Add to front for quick reassignment
                    
                    # Clean up assignment
                    self._active_assignments.pop(assignment_id, None)
                    self._assignment_to_task.pop(assignment_id, None)
                    self._assignment_to_worker.pop(assignment_id, None)
                    
                    reassigned_tasks.append(task_id)
            
            # Update worker's assigned task
            worker.assigned_task = None
    
    async def get_dlq_statistics(self) -> Dict[str, Any]:
        """Get dead letter queue statistics.
        
        Returns:
            Dictionary with DLQ statistics
        """
        async with self._lock:
            by_reason = defaultdict(int)
            for metadata in self._dlq_metadata.values():
                reason = metadata.get("reason", "unknown")
                by_reason[reason] += 1
            
            return {
                "total_tasks": len(self._dead_letter_queue),
                "by_reason": dict(by_reason)
            }
    
    async def get_dlq_tasks(self) -> list:
        """Get all tasks in the dead letter queue.
        
        Returns:
            List of task IDs in DLQ
        """
        async with self._lock:
            return list(self._dead_letter_queue)
    
    async def retry_from_dlq(self, task_id: str) -> Dict[str, Any]:
        """Retry a task from the dead letter queue.
        
        Args:
            task_id: ID of task to retry
            
        Returns:
            Dictionary with retry result
        """
        async with self._lock:
            if task_id not in self._dlq_metadata:
                return {"success": False, "error": "Task not in DLQ"}
            
            # Find and remove task from DLQ
            task = None
            for i, tid in enumerate(self._dead_letter_queue):
                if tid == task_id:
                    self._dead_letter_queue.remove(tid)
                    task = self._tasks.get(tid)
                    break
            
            if not task:
                return {"success": False, "error": "Task not found"}
            
            # Reset task state
            task.state = TaskState.PENDING
            task.assigned_to = None
            task.assigned_at = None
            self._task_states[task_id] = TaskState.PENDING
            self._task_retry_counts[task_id] = 0  # Reset retry count
            
            # Add back to appropriate queue
            priority_queue = self._queues[task.priority]
            priority_queue.append(task_id)
            
            # Clean up DLQ metadata
            self._dlq_metadata.pop(task_id, None)
            
            return {"success": True, "task_id": task_id}
    
    async def get_task_info(self, task_id: str) -> Dict[str, Any]:
        """Get detailed information about a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Dictionary with task information
        """
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return {"error": "Task not found"}
            
            enqueue_time = self._task_enqueue_times.get(task_id)
            wait_time = 0
            if enqueue_time:
                if task.assigned_at:
                    wait_time = (task.assigned_at - enqueue_time).total_seconds()
                else:
                    wait_time = (datetime.utcnow() - enqueue_time).total_seconds()
            
            # Calculate effective priority with boost
            boost_level = self._task_boost_levels.get(task_id, 0.0)
            effective_priority = task.priority + boost_level
            
            # Get reassignment info
            reassignment_count = 0
            previous_workers = []
            for failure in self._task_failure_history.get(task_id, []):
                if failure.get("reason") == "worker_failure":
                    reassignment_count += 1
                    if "worker_id" in failure:
                        previous_workers.append(failure["worker_id"])
            
            return {
                "task_id": task_id,
                "state": self._task_states.get(task_id, TaskState.PENDING).value,
                "priority": task.priority,
                "effective_priority": effective_priority,
                "wait_time": wait_time,
                "retry_count": self._task_retry_counts.get(task_id, 0),
                "reassignment_count": reassignment_count,
                "previous_workers": previous_workers,
                "prefer_different_worker": reassignment_count > 0,
                "failure_history": self._task_failure_history.get(task_id, []),
                "progress": self._task_progress.get(task_id, {})
            }
    
    async def get_starvation_statistics(self) -> Dict[str, Any]:
        """Get statistics about task starvation.
        
        Returns:
            Dictionary with starvation statistics
        """
        async with self._lock:
            now = datetime.utcnow()
            starvation_threshold = timedelta(seconds=self.config.starvation_threshold)
            
            starved_tasks = 0
            starved_task_ids = []
            oldest_task = None
            oldest_wait_time = 0
            tasks_boosted = 0
            max_wait_time = 0
            tasks_above_threshold = 0
            
            # Check pending tasks for starvation using created_at
            for priority in [1, 2, 3]:  # Check all priorities
                for task_id in self._queues[priority]:
                    task = self._tasks.get(task_id)
                    if task and task.created_at:
                        wait_time = now - task.created_at
                        if wait_time > starvation_threshold:
                            starved_tasks += 1
                            starved_task_ids.append(task_id)
                        
                        wait_seconds = wait_time.total_seconds()
                        if wait_seconds > oldest_wait_time:
                            oldest_wait_time = wait_seconds
                            oldest_task = {
                                "task_id": task_id,
                                "priority": {1: "low", 2: "medium", 3: "high"}[priority],
                                "wait_time": wait_seconds
                            }
            
            # Also check for priority boosts
            for task_id, enqueue_time in self._task_enqueue_times.items():
                if self._task_states.get(task_id) == TaskState.PENDING:
                    wait_time = (now - enqueue_time).total_seconds()
                    max_wait_time = max(max_wait_time, wait_time)
                    
                    if self._task_boost_levels.get(task_id, 0) > 0:
                        tasks_boosted += 1
                    
                    if wait_time > self.config.starvation_threshold:
                        tasks_above_threshold += 1
            
            return {
                "starved_tasks": starved_tasks,
                "starved_task_ids": starved_task_ids,
                "oldest_waiting_task": oldest_task,
                "starvation_threshold": self.config.starvation_threshold,
                "tasks_boosted": tasks_boosted,
                "max_wait_time": max_wait_time,
                "tasks_above_threshold": tasks_above_threshold
            }
    
    async def _apply_priority_boosts(self) -> None:
        """Apply priority boosts to tasks that have been waiting too long.
        
        Note: This method must be called within a lock.
        """
        now = datetime.utcnow()
        boost_interval = self.config.priority_boost_interval
        boost_amount = self.config.priority_boost_amount
        
        for task_id, enqueue_time in self._task_enqueue_times.items():
            if self._task_states.get(task_id) == TaskState.PENDING:
                wait_time = (now - enqueue_time).total_seconds()
                
                # Calculate how many boost intervals have passed
                boost_intervals_passed = int(wait_time / boost_interval)
                
                if boost_intervals_passed > 0:
                    # Apply boost
                    current_boost = self._task_boost_levels.get(task_id, 0.0)
                    new_boost = boost_intervals_passed * boost_amount
                    
                    # Only update if the new boost is higher
                    if new_boost > current_boost:
                        self._task_boost_levels[task_id] = new_boost
    
    async def export_state(self) -> Dict[str, Any]:
        """Export current queue state as a dictionary.
        
        Returns:
            Dictionary containing the complete queue state
        """
        async with self._lock:
            # Prepare state for export
            state = {
                "version": self._persistence_version,
                "timestamp": datetime.utcnow().isoformat(),
                "queues": {
                    "high": list(self._queues[3]),
                    "medium": list(self._queues[2]),
                    "low": list(self._queues[1])
                },
                "tasks": {},
                "task_states": {},
                "task_retry_counts": dict(self._task_retry_counts),
                "task_failure_history": {},
                "task_progress": dict(self._task_progress),
                "task_enqueue_times": {},
                "task_boost_levels": dict(self._task_boost_levels),
                "workers": {},
                "assignments": {},
                "capability_matching_enabled": self._capability_matching_enabled,
                "dead_letter_queue": list(self._dead_letter_queue),
                "dlq_metadata": dict(self._dlq_metadata),
                "displaced_tasks": self._displaced_tasks,
                "displacement_by_priority": dict(self._displacement_by_priority)
            }
            
            # Serialize tasks
            for task_id, task in self._tasks.items():
                state["tasks"][task_id] = {
                    "id": str(task.id),
                    "task_type": task.task_type.value,
                    "priority": task.priority,
                    "state": task.state.value,
                    "payload": task.payload,
                    "assigned_to": task.assigned_to,
                    "result": task.result,
                    "error": task.error,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "assigned_at": task.assigned_at.isoformat() if task.assigned_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
            
            # Serialize task states
            for task_id, task_state in self._task_states.items():
                state["task_states"][task_id] = task_state.value
            
            # Serialize task enqueue times
            for task_id, enqueue_time in self._task_enqueue_times.items():
                state["task_enqueue_times"][task_id] = enqueue_time.isoformat()
            
            # Serialize failure history with datetime conversion
            for task_id, failures in self._task_failure_history.items():
                serialized_failures = []
                for failure in failures:
                    serialized_failure = failure.copy()
                    if 'timestamp' in serialized_failure and isinstance(serialized_failure['timestamp'], datetime):
                        serialized_failure['timestamp'] = serialized_failure['timestamp'].isoformat()
                    serialized_failures.append(serialized_failure)
                state["task_failure_history"][task_id] = serialized_failures
            
            # Serialize workers
            for worker_id, worker_info in self._worker_info.items():
                state["workers"][worker_id] = {
                    "id": worker_info.id,
                    "capabilities": worker_info.capabilities,
                    "state": worker_info.state,
                    "last_heartbeat": worker_info.last_heartbeat.isoformat(),
                    "assigned_task": worker_info.assigned_task,
                    "registration_time": worker_info.registration_time.isoformat()
                }
                
            # Serialize active assignments
            for assignment_id, assignment in self._active_assignments.items():
                state["assignments"][assignment_id] = {
                    "task_id": str(assignment.task.id),
                    "assignment_id": assignment.assignment_id,
                    "deadline": assignment.deadline,
                    "acknowledgment_required_by": assignment.acknowledgment_required_by,
                    "worker_id": self._assignment_to_worker.get(assignment_id)
                }
            
            return state
    
    async def import_state(self, state: Dict[str, Any]) -> None:
        """Import queue state from a dictionary.
        
        Args:
            state: Dictionary containing queue state to import
            
        Raises:
            ValueError: If state version is incompatible
        """
        # Check version compatibility
        version = state.get("version", "0.0.0")
        if version.split('.')[0] != self._persistence_version.split('.')[0]:
            raise ValueError(f"Incompatible state version: {version}")
        
        async with self._lock:
            # Clear current state
            self._queues = {3: deque(), 2: deque(), 1: deque()}
            self._tasks.clear()
            self._task_states.clear()
            self._task_retry_counts.clear()
            self._task_failure_history.clear()
            self._task_progress.clear()
            self._task_enqueue_times.clear()
            self._task_boost_levels.clear()
            self._workers.clear()
            self._active_workers.clear()
            self._worker_info.clear()
            self._active_assignments.clear()
            self._assignment_to_task.clear()
            self._assignment_to_worker.clear()
            self._dead_letter_queue.clear()
            self._dlq_metadata.clear()
            
            # Restore queues
            queues = state.get("queues", {})
            if "high" in queues:
                self._queues[3].extend(queues["high"])
            if "medium" in queues:
                self._queues[2].extend(queues["medium"])
            if "low" in queues:
                self._queues[1].extend(queues["low"])
            
            # Restore tasks
            for task_id, task_data in state.get("tasks", {}).items():
                task = Task(
                    task_type=TaskType(task_data["task_type"]),
                    priority=task_data["priority"],
                    payload=task_data["payload"]
                )
                # Set ID from saved data
                task.id = UUID(task_data["id"])
                task.state = TaskState(task_data["state"])
                task.assigned_to = task_data["assigned_to"]
                task.result = task_data["result"]
                task.error = task_data["error"]
                
                # Restore timestamps
                if task_data["created_at"]:
                    task.created_at = datetime.fromisoformat(task_data["created_at"])
                if task_data["assigned_at"]:
                    task.assigned_at = datetime.fromisoformat(task_data["assigned_at"])
                if task_data["completed_at"]:
                    task.completed_at = datetime.fromisoformat(task_data["completed_at"])
                
                self._tasks[task_id] = task
            
            # Restore task states
            for task_id, state_value in state.get("task_states", {}).items():
                self._task_states[task_id] = TaskState(state_value)
            
            # Restore task enqueue times
            for task_id, enqueue_time_str in state.get("task_enqueue_times", {}).items():
                self._task_enqueue_times[task_id] = datetime.fromisoformat(enqueue_time_str)
            
            # Restore task boost levels
            self._task_boost_levels.update(state.get("task_boost_levels", {}))
            
            # Restore retry counts
            self._task_retry_counts.update(state.get("task_retry_counts", {}))
            
            # Restore failure history
            for task_id, failures in state.get("task_failure_history", {}).items():
                restored_failures = []
                for failure in failures:
                    restored_failure = failure.copy()
                    if 'timestamp' in restored_failure and isinstance(restored_failure['timestamp'], str):
                        restored_failure['timestamp'] = datetime.fromisoformat(restored_failure['timestamp'])
                    restored_failures.append(restored_failure)
                self._task_failure_history[task_id] = restored_failures
            
            # Restore progress
            self._task_progress.update(state.get("task_progress", {}))
            
            # Restore workers
            for worker_id, worker_data in state.get("workers", {}).items():
                worker_info = WorkerInfo(
                    id=worker_data["id"],
                    capabilities=worker_data["capabilities"],
                    state=worker_data["state"],
                    last_heartbeat=datetime.fromisoformat(worker_data["last_heartbeat"]),
                    assigned_task=worker_data["assigned_task"],
                    registration_time=datetime.fromisoformat(worker_data["registration_time"])
                )
                self._worker_info[worker_id] = worker_info
                self._workers.add(worker_id)
                
                if worker_info.state == "active" and worker_info.assigned_task:
                    self._active_workers.add(worker_id)
            
            # Restore assignments
            for assignment_id, assignment_data in state.get("assignments", {}).items():
                task_id = assignment_data["task_id"]
                task = self._tasks.get(task_id)
                if task:
                    assignment = TaskAssignment(
                        task=task,
                        assignment_id=assignment_data["assignment_id"],
                        deadline=assignment_data["deadline"],
                        acknowledgment_required_by=assignment_data["acknowledgment_required_by"]
                    )
                    self._active_assignments[assignment_id] = assignment
                    self._assignment_to_task[assignment_id] = task_id
                    self._assignment_to_worker[assignment_id] = assignment_data["worker_id"]
            
            # Restore other settings
            self._capability_matching_enabled = state.get("capability_matching_enabled", False)
            
            # Restore dead letter queue
            if "dead_letter_queue" in state:
                self._dead_letter_queue.extend(state["dead_letter_queue"])
            
            # Restore DLQ metadata
            if "dlq_metadata" in state:
                self._dlq_metadata.update(state["dlq_metadata"])
            
            # Restore displacement stats
            if "displaced_tasks" in state:
                self._displaced_tasks = state["displaced_tasks"]
            if "displacement_by_priority" in state:
                self._displacement_by_priority.update(state["displacement_by_priority"])