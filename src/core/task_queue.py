"""Task Queue implementation for AI Co-Scientist."""

import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Set, Tuple
from uuid import uuid4

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
    retry_policy: Dict[str, Any] = None
    persistence_interval: int = 60
    starvation_threshold: int = 3600
    acknowledgment_timeout: int = 5
    
    def __post_init__(self):
        """Initialize and validate configuration."""
        if self.priority_quotas is None:
            self.priority_quotas = {"high": 1000, "medium": 5000, "low": 4000}
        
        if self.retry_policy is None:
            self.retry_policy = {
                "max_attempts": 3,
                "backoff_base": 2,
                "backoff_max": 300
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
        
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
    
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
            # Check capacity
            if self.size() >= self.config.max_queue_size:
                raise RuntimeError("Queue at capacity")
            
            # Map priority to queue (1=low, 2=medium, 3=high)
            priority_queue = self._queues.get(task.priority)
            if priority_queue is None:
                raise ValueError(f"Invalid priority: {task.priority}")
            
            # Check priority quota
            priority_name = {1: "low", 2: "medium", 3: "high"}.get(task.priority)
            if len(priority_queue) >= self.config.priority_quotas.get(priority_name, 0):
                raise RuntimeError(f"Queue at capacity for {priority_name} priority")
            
            # Add to queue
            task_id = str(task.id)
            self._tasks[task_id] = task
            self._task_states[task_id] = TaskState.PENDING
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
            
            # Find highest priority task that worker can handle
            for priority in [3, 2, 1]:  # High to low
                queue = self._queues[priority]
                
                # Look through tasks in this priority level
                tasks_to_requeue = []
                found_task = None
                
                while queue and not found_task:
                    task_id = queue.popleft()
                    task = self._tasks.get(task_id)
                    
                    if task and self._can_worker_handle_task(worker_id, task):
                        found_task = (task_id, task)
                    else:
                        # Worker can't handle this task, save for requeue
                        tasks_to_requeue.append(task_id)
                
                # Requeue tasks that weren't suitable
                for tid in tasks_to_requeue:
                    queue.append(tid)
                
                if found_task:
                    task_id, task = found_task
                    
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
            
            # Update task state
            self._task_states[task_id] = TaskState.COMPLETED
            
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
            
            if error.get("retryable", False) and retry_count < max_retries:
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
                # Permanent failure
                self._task_states[task_id] = TaskState.FAILED
            
            return True
    
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
                "state": self._task_states.get(task_id, TaskState.PENDING).value,
                "assigned_to": task.assigned_to,
                "assigned_at": task.assigned_at,
                "retry_count": self._task_retry_counts.get(task_id, 0),
                "failure_history": self._task_failure_history.get(task_id, [])
            }