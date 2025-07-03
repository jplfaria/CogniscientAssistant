# Multi-Agent Framework Specification

**Type**: Framework  
**Interactions**: All Agents, Context Memory, Worker Processes, Task Queue

## Prerequisites
- Read: System Overview and Architecture Specification

## Purpose

The Multi-Agent Framework provides the coordination infrastructure that enables specialized agents to work together asynchronously on scientific hypothesis generation tasks. The framework ensures efficient resource utilization, maintains system state, and orchestrates complex multi-agent workflows without requiring direct agent-to-agent communication.

## Framework Behavior

The Multi-Agent Framework exhibits the following behaviors:

1. **Asynchronous Task Execution**: Manages concurrent agent operations through a worker process pool
2. **State Persistence**: Maintains system state across agent executions via Context Memory
3. **Dynamic Resource Allocation**: Assigns agents to tasks based on system needs and agent weights
4. **Progress Monitoring**: Tracks task completion and system convergence metrics
5. **Failure Recovery**: Enables system restart from checkpoints through persistent state
6. **Scalable Computation**: Adjusts test-time compute based on problem complexity

## Core Components

### Task Queue System
**Purpose**: Central work distribution mechanism

**Behaviors**:
- Accepts task submissions from the Supervisor Agent
- Maintains priority ordering of pending tasks
- Assigns tasks to available worker processes
- Tracks task execution status (pending, in-progress, completed, failed)
- Supports task dependencies and sequencing

### Worker Process Pool
**Purpose**: Execution environment for agent tasks

**Behaviors**:
- Executes agent code in isolated processes
- Manages computational resource allocation per task
- Reports task completion status to queue
- Handles task timeouts and failures gracefully
- Scales process count based on system load

### Context Memory
**Purpose**: Persistent state storage for inter-agent communication

**Behaviors**:
- Stores all generated hypotheses with metadata
- Maintains review results from all review types
- Tracks tournament state and Elo ratings
- Persists proximity graphs and similarity calculations
- Archives meta-review feedback for all agents
- Provides atomic read/write operations for consistency

### Agent Registry
**Purpose**: Manages available agents and their capabilities

**Behaviors**:
- Registers specialized agents with their interfaces
- Tracks agent availability and health status
- Maintains agent execution statistics
- Provides agent discovery for the Supervisor

## Communication Protocols

### Task Assignment Protocol
**From**: Supervisor Agent  
**To**: Task Queue  
**Message Format**:
```
TaskAssignment {
  task_id: string
  agent_type: AgentType
  parameters: dict
  priority: int
  dependencies: list[task_id]
  timeout: int (seconds)
}
```

### Task Result Protocol
**From**: Worker Process  
**To**: Context Memory  
**Message Format**:
```
TaskResult {
  task_id: string
  agent_type: AgentType
  status: Success | Failure | Timeout
  output_data: dict
  execution_time: float
  error_message: string (optional)
}
```

### State Query Protocol
**From**: Any Agent  
**To**: Context Memory  
**Operations**:
- `read_hypotheses(filter_criteria) -> List[Hypothesis]`
- `read_reviews(hypothesis_id) -> List[Review]`
- `read_rankings() -> List[RankedHypothesis]`
- `read_meta_feedback() -> MetaReview`
- `read_proximity_graph() -> ProximityGraph`

### State Update Protocol
**From**: Any Agent  
**To**: Context Memory  
**Operations**:
- `write_hypothesis(hypothesis_data) -> hypothesis_id`
- `write_review(hypothesis_id, review_data) -> review_id`
- `update_ranking(hypothesis_id, elo_rating) -> success`
- `write_proximity(hypothesis_pairs, similarities) -> success`
- `append_meta_feedback(feedback_data) -> success`

## Coordination Patterns

### Phase-Based Execution
The framework supports phased execution patterns:

1. **Generation Phase**
   - Multiple Generation Agent instances create hypotheses in parallel
   - Results accumulate in Context Memory
   - Supervisor monitors hypothesis count

2. **Review Phase**
   - Reflection Agents process hypothesis queue
   - Multiple review types execute concurrently
   - Reviews stored with hypothesis associations

3. **Tournament Phase**
   - Ranking Agent orchestrates pairwise comparisons
   - Proximity Agent calculates similarities for matchmaking
   - Elo ratings updated atomically

4. **Evolution Phase**
   - Evolution Agents refine top-ranked hypotheses
   - New hypotheses feed back to generation queue
   - Meta-review Agent synthesizes patterns

### Resource Allocation Strategy
```
Agent Weight Distribution:
- Generation: 0.3 (initial), 0.1 (steady state)
- Reflection: 0.3 (constant)
- Ranking: 0.2 (after sufficient hypotheses)
- Evolution: 0.1 (after rankings stabilize)
- Proximity: 0.05 (on-demand)
- Meta-review: 0.05 (periodic)
```

### Failure Handling Patterns

**Task-Level Failures**:
- Retry with exponential backoff (max 3 attempts)
- Log failure details to Context Memory
- Continue with remaining tasks
- Alert Supervisor for critical failures

**System-Level Failures**:
- Checkpoint state to persistent storage every N tasks
- Enable restart from last checkpoint
- Maintain transaction log for recovery
- Graceful degradation for non-critical agents

## Scalability Mechanisms

### Horizontal Scaling
- Worker process pool expands based on queue depth
- Multiple instances of same agent type allowed
- Load balancing across available workers
- Dynamic resource provisioning

### Vertical Scaling
- Adjust compute resources per agent task
- Allocate more time for complex operations
- Scale memory for large hypothesis sets
- Prioritize critical path tasks

### Test-Time Compute Scaling
- Increase generation attempts for difficult problems
- Extend tournament rounds for close competitions
- Deepen review analysis for promising hypotheses
- Expand evolution iterations based on progress

## Monitoring and Observability

### System Metrics
The framework tracks:
- Task queue depth and latency
- Agent execution times by type
- Success/failure rates per agent
- Resource utilization (CPU, memory)
- Hypothesis generation rate
- Review throughput
- Tournament completion percentage

### Progress Indicators
- Total hypotheses generated
- Hypotheses reviewed by type
- Tournament matches completed
- Evolution cycles finished
- System convergence score

## Integration Interfaces

### Supervisor Integration
The Supervisor Agent interfaces with the framework to:
- Submit tasks to queue
- Query system metrics
- Adjust agent weights
- Monitor progress
- Determine terminal conditions

### Tool Integration
The framework provides agents access to:
- Web search capabilities
- Specialized AI models
- Document processing
- Citation databases

Access managed through:
```
ToolRequest {
  tool_type: ToolType
  parameters: dict
  timeout: int
  retry_policy: RetryPolicy
}
```

## Error Conditions

The framework must handle:
- Worker process crashes
- Context Memory unavailability
- Network failures for tool access
- Queue overflow conditions
- Deadlock in task dependencies
- Resource exhaustion
- Corrupted state data

## Quality Assurance

### Consistency Guarantees
- Atomic operations on Context Memory
- Ordered task execution when dependencies exist
- Exactly-once task completion semantics
- Consistent view of system state

### Performance Requirements
- Task assignment latency < 100ms
- State read operations < 50ms
- State write operations < 200ms
- Worker startup time < 5 seconds
- Checkpoint creation < 30 seconds

## Framework Boundaries

**What the Framework Provides**:
- Asynchronous task execution infrastructure
- Reliable state persistence
- Inter-agent communication mechanisms
- Resource management and scaling
- Failure recovery capabilities
- Progress monitoring

**What the Framework Does Not Provide**:
- Agent implementation logic
- Scientific reasoning capabilities
- Direct agent-to-agent messaging
- Real-time synchronization
- Distributed consensus
- External system integration (handled by tools)

## Success Criteria

A properly functioning Multi-Agent Framework will:
1. Execute thousands of agent tasks without degradation
2. Maintain consistent state across all operations
3. Recover gracefully from component failures
4. Scale resources based on workload
5. Provide visibility into system behavior
6. Enable complex multi-agent workflows without deadlocks