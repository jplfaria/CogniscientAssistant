"""Task Queue implementation for AI Co-Scientist."""

import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, Any, Set
from uuid import uuid4

from src.core.models import Task, TaskState


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
        
        # Worker tracking
        self._workers: Set[str] = set()
        self._active_workers: Set[str] = set()
        
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
            # Register worker if new
            self._workers.add(worker_id)
            
            # Find highest priority task
            for priority in [3, 2, 1]:  # High to low
                queue = self._queues[priority]
                if queue:
                    task_id = queue.popleft()
                    task = self._tasks[task_id]
                    
                    # Update task state
                    task.assign(worker_id)
                    self._task_states[task_id] = TaskState.ASSIGNED
                    self._active_workers.add(worker_id)
                    
                    # Create assignment
                    now = datetime.utcnow().timestamp()
                    assignment = TaskAssignment(
                        task=task,
                        assignment_id=str(uuid4()),
                        deadline=now + self.config.worker_timeout,
                        acknowledgment_required_by=now + 5  # 5 seconds to acknowledge
                    )
                    
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