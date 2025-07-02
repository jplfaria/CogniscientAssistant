# Task Queue Behavior Specification

**Type**: System Component  
**Interactions**: Supervisor Agent, Worker Processes, Context Memory

## Prerequisites
- Read: Multi-Agent Architecture Specification
- Read: Supervisor Agent Specification
- Understand: Asynchronous execution patterns and worker pool concepts

## Overview

The Task Queue is the central coordination mechanism that enables asynchronous, scalable execution of agent tasks in the AI Co-Scientist system. It manages the flow of work from the Supervisor Agent to Worker Processes, supporting continuous operation and flexible resource allocation.

## Core Behaviors

### 1. Task Lifecycle Management

The queue manages tasks through the following states:
- **Pending**: Task created and waiting for execution
- **Assigned**: Task assigned to a worker process
- **Executing**: Task being processed by an agent
- **Completed**: Task finished successfully
- **Failed**: Task execution failed
- **Retrying**: Task scheduled for retry after failure

State transitions:
```
Pending → Assigned → Executing → Completed
                   ↓           ↓
                   Failed → Retrying → Pending
```

### 2. Priority-Based Ordering

Tasks are ordered based on:
- **Priority Level**: High, Medium, Low (as assigned by Supervisor)
- **Creation Time**: FIFO within same priority level
- **Retry Count**: Failed tasks may have adjusted priority
- **Agent Type**: Certain agents may have inherent priority boosts

Priority rules:
- High priority tasks always execute before lower priorities
- Within same priority: older tasks execute first
- Starvation prevention: Low priority tasks eventually promote if waiting too long

### 3. Worker Assignment

The queue matches tasks to available workers:
- **Worker Registration**: Workers announce availability to queue
- **Task Matching**: Queue assigns next eligible task to available worker
- **Heartbeat Monitoring**: Workers send periodic heartbeats
- **Worker Timeout**: Tasks reassigned if worker stops responding

Assignment constraints:
- One task per worker at a time
- Tasks cannot be assigned to multiple workers
- Worker must acknowledge assignment within timeout period

### 4. Queue Capacity Management

The queue enforces capacity limits:
- **Maximum Queue Size**: Total task limit across all priorities
- **Priority Quotas**: Maximum tasks per priority level
- **Backpressure**: Supervisor notified when approaching limits
- **Overflow Handling**: Oldest low-priority tasks dropped if at capacity

Capacity behaviors:
- New high-priority tasks can displace low-priority tasks
- Queue depth metrics available for monitoring
- Configurable warning thresholds

## Inputs

### Task Submission
```
Task {
    id: unique_identifier
    agent_type: Generation|Reflection|Ranking|Evolution|Proximity|MetaReview
    priority: High|Medium|Low
    payload: agent-specific data
    dependencies: list of task_ids (optional)
    retry_policy: {max_attempts, backoff_strategy}
    timeout: maximum execution time
    created_at: timestamp
}
```

### Worker Commands
- **Register**: Worker announces availability with capabilities
- **Heartbeat**: Worker confirms active status
- **Complete**: Worker reports task completion with results
- **Fail**: Worker reports task failure with error details
- **Request**: Worker requests next available task

### Management Commands
- **Query**: Get queue status and metrics
- **Purge**: Remove tasks matching criteria
- **Pause**: Temporarily stop task assignment
- **Resume**: Restart task assignment
- **Rebalance**: Redistribute tasks among workers

## Outputs

### To Workers
```
Assignment {
    task: complete task object
    assignment_id: unique assignment identifier
    deadline: execution deadline timestamp
    acknowledgment_required_by: timestamp
}
```

### To Supervisor
```
QueueStatus {
    depth: {high: N, medium: N, low: N}
    workers: {active: N, idle: N, failed: N}
    throughput: tasks_per_minute
    average_wait_time: by_priority
    failed_tasks: recent_failures
    capacity_warnings: if approaching limits
}
```

### Task Results
```
TaskResult {
    task_id: original task identifier
    status: Completed|Failed
    result: agent-specific output (if completed)
    error: error details (if failed)
    execution_time: duration
    worker_id: executing worker
    completed_at: timestamp
}
```

## Queue Operations

### Core Operations

1. **Enqueue**: Add new task with validation
   - Validate task structure
   - Check capacity limits
   - Assign to appropriate priority queue
   - Trigger worker notification if idle workers exist

2. **Dequeue**: Retrieve next task for worker
   - Select highest priority available task
   - Check task dependencies satisfied
   - Mark task as assigned
   - Start assignment timeout timer

3. **Requeue**: Return task to queue
   - Used for retry after failure
   - Adjust priority based on retry policy
   - Reset task state to pending
   - Increment retry counter

### Advanced Operations

1. **Dependency Resolution**
   - Track task completion status
   - Only assign tasks with satisfied dependencies
   - Notify dependent tasks when prerequisites complete

2. **Dead Letter Queue**
   - Move permanently failed tasks to DLQ
   - Preserve failure history for analysis
   - Allow manual retry from DLQ

3. **Queue Persistence**
   - Periodic snapshots to Context Memory
   - Restore queue state after system restart
   - Maintain task ordering and state

## Error Handling

### Worker Failures
- **Timeout**: Reassign task if worker doesn't respond
- **Crash**: Detect missing heartbeats and reassign tasks
- **Partial Failure**: Allow worker to report partial progress

### Task Failures
- **Retry Logic**: Exponential backoff with jitter
- **Max Retries**: Move to dead letter queue after limit
- **Failure Patterns**: Track and report systematic failures

### System Failures
- **Queue Overflow**: Gracefully reject new tasks
- **Persistence Failure**: Continue operating, alert Supervisor
- **Recovery**: Restore from last checkpoint in Context Memory

## Performance Characteristics

### Latency Guarantees
- Task assignment: < 100ms for available worker
- State transitions: < 50ms
- Query operations: < 10ms

### Throughput
- Support 100+ concurrent workers
- Handle 1000+ tasks per minute
- Scale with worker pool size

### Reliability
- No task loss during normal operation
- At-most-once execution guarantee
- Eventual consistency for distributed state

## Monitoring and Observability

The queue exposes metrics for:
- Queue depth by priority
- Task wait times
- Worker utilization
- Failure rates by agent type
- Throughput and latency percentiles

Alerting triggers:
- Queue depth exceeds threshold
- Worker pool shrinks below minimum
- Failure rate exceeds acceptable level
- Tasks stuck in executing state

## Configuration

Queue behavior is configurable via:
```
QueueConfig {
    max_queue_size: 10000
    priority_quotas: {high: 1000, medium: 5000, low: 4000}
    worker_timeout: 300 seconds
    heartbeat_interval: 30 seconds
    retry_policy: {
        max_attempts: 3
        backoff_base: 2
        backoff_max: 300 seconds
    }
    persistence_interval: 60 seconds
    starvation_threshold: 3600 seconds
}
```

## Integration Points

### With Supervisor Agent
- Receives task creation requests
- Reports queue status and metrics
- Accepts queue management commands
- Provides backpressure signals

### With Worker Processes
- Manages worker lifecycle
- Assigns tasks to workers
- Collects task results
- Monitors worker health

### With Context Memory
- Persists queue state periodically
- Restores state after restart
- Stores dead letter queue
- Archives completed task history

## Example Scenarios

### Hypothesis Generation Burst
1. Supervisor creates 50 Generation tasks (medium priority)
2. Queue distributes across available workers
3. As workers complete, queue assigns remaining tasks
4. Queue reports completion metrics to Supervisor

### Tournament Scheduling
1. Supervisor creates Ranking tasks (high priority)
2. Queue ensures tournament tasks execute before others
3. Failed matches retry with same priority
4. Queue maintains tournament progress state

### System Recovery
1. System restarts after failure
2. Queue restores state from Context Memory
3. Workers re-register with queue
4. Incomplete tasks reassigned to workers
5. Processing continues from last checkpoint

## Quality Requirements

### Correctness
- Never lose or duplicate tasks
- Maintain strict priority ordering
- Honor all task dependencies
- Accurately track task states

### Performance
- Sub-second task assignment latency
- Linear scaling with worker count
- Minimal memory overhead per task
- Efficient priority queue operations

### Reliability
- Graceful degradation under load
- Automatic recovery from transient failures
- Clear failure reporting
- Comprehensive audit trail