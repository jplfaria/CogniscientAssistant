# Supervisor Agent Specification

**Type**: Agent  
**Interactions**: All Specialized Agents, Context Memory, Task Queue, Natural Language Interface

## Prerequisites
- Read: System Overview Specification
- Read: Multi-Agent Architecture Specification
- Understand: Task queue and asynchronous execution concepts

## Purpose

The Supervisor Agent serves as the central orchestrator of the AI Co-Scientist system, managing resource allocation, task distribution, and strategic coordination of all specialized agents to achieve research goals efficiently and reliably.

## Core Behaviors

### Task Queue Management

The Supervisor Agent manages all task execution through:

- **Task Creation**: Converts research plans into discrete, executable tasks
- **Queue Prioritization**: Orders tasks based on urgency, dependencies, and strategic importance
- **Worker Assignment**: Matches available workers with queued tasks
- **Progress Tracking**: Monitors task completion and system throughput
- **Queue Optimization**: Adjusts priorities based on system state

### Resource Allocation

The Supervisor Agent distributes computational resources by:

- **Budget Assignment**: Allocates compute time to each task
- **Worker Pool Management**: Maintains optimal number of active workers
- **Dynamic Scaling**: Adjusts resources based on workload
- **Fair Distribution**: Ensures all agents receive necessary resources
- **Cost Monitoring**: Tracks resource consumption against limits

### Strategic Orchestration

The Supervisor Agent coordinates system operations through:

- **Agent Weighting**: Assigns execution probabilities to agents based on effectiveness
- **Statistical Analysis**: Calculates metrics to inform decisions
- **Adaptive Strategy**: Modifies orchestration based on progress
- **Termination Detection**: Recognizes when research goals are achieved
- **Recovery Planning**: Handles failures and system restarts

## Inputs

### Research Plan Configuration
```
ResearchPlan:
  goal: string (natural language research objective)
  constraints: 
    max_hypotheses: integer
    time_limit: duration
    resource_budget: float
  preferences:
    focus_areas: list[string]
    excluded_topics: list[string]
```

### System Feedback
```
SystemMetrics:
  hypothesis_count: integer
  pending_reviews: integer
  tournament_progress: float (0.0-1.0)
  agent_effectiveness: map[agent_name, float]
  resource_utilization: float (0.0-1.0)
```

### Agent Results
```
TaskResult:
  task_id: string
  agent_type: string
  status: enum (completed, failed, timeout)
  output: any (agent-specific)
  resource_consumed: float
  execution_time: duration
```

## Outputs

### Task Assignments
```
TaskAssignment:
  task_id: string
  agent_type: string
  priority: enum (critical, high, normal, low)
  parameters: map[string, any]
  resource_budget: float
  timeout: duration
```

### System State Updates
```
OrchestrationState:
  timestamp: datetime
  active_tasks: list[task_id]
  agent_weights: map[agent_name, float]
  strategic_focus: string
  termination_probability: float
```

### Resource Allocations
```
ResourceAllocation:
  worker_count: integer
  agent_budgets: map[agent_name, float]
  queue_depth_limits: map[priority, integer]
  scaling_directive: enum (scale_up, maintain, scale_down)
```

## Behavioral Contracts

### Task Execution Guarantees

The Supervisor Agent MUST:
- Ensure every created task is eventually assigned or explicitly cancelled
- Prevent task starvation through fair queuing algorithms
- Maintain task ordering constraints and dependencies
- Handle task failures with configurable retry policies
- Complete critical tasks before lower priority work

### Resource Management Rules

The Supervisor Agent MUST:
- Never exceed total resource budget constraints
- Allocate minimum viable resources to each active agent
- Reclaim resources from failed or timed-out tasks
- Balance resource allocation based on measured effectiveness
- Maintain resource reserves for critical operations

### State Persistence Requirements

The Supervisor Agent MUST:
- Write comprehensive state to Context Memory every N minutes
- Include sufficient information for complete system recovery
- Preserve in-flight task state across restarts
- Maintain audit trail of all orchestration decisions
- Enable rollback to previous stable states

## Interaction Protocols

### With Specialized Agents

Communication follows this pattern:

1. **Assignment Phase**
   - Supervisor creates task with specific parameters
   - Task placed in appropriate queue
   - Worker process receives task from queue
   - Agent instantiated with task context

2. **Execution Phase**
   - Agent operates autonomously within budget
   - Progress updates written to Context Memory
   - Resource consumption tracked continuously
   - Timeout enforcement by Supervisor

3. **Completion Phase**
   - Agent returns results to Context Memory
   - Supervisor notified of task completion
   - Resources reclaimed and reallocated
   - Follow-up tasks created if needed

### With Context Memory

The Supervisor Agent uses Context Memory for:

- **Statistical Monitoring**: Regular calculation and storage of system metrics
- **Decision History**: Recording rationale for orchestration choices
- **Recovery State**: Snapshots enabling restart from any point
- **Feedback Integration**: Accessing Meta-Review Agent insights

### With Task Queue

Queue operations include:

- **Enqueue**: Adding tasks with priority and metadata
- **Dequeue**: Retrieving highest priority available task
- **Requeue**: Returning failed tasks with updated priority
- **Query**: Examining queue state for planning
- **Purge**: Removing obsolete or cancelled tasks

## Decision-Making Behaviors

### Agent Selection Strategy

The Supervisor determines which agents to activate based on:

1. **Current System State**
   - Number of hypotheses at each stage
   - Distribution of hypothesis quality scores
   - Pending work in each category
   - Recent agent performance metrics

2. **Strategic Weights**
   - Historical effectiveness of each agent type
   - Meta-review feedback on agent contributions
   - Research goal alignment scores
   - Resource efficiency ratios

3. **Sampling Algorithm**
   - Weighted random selection from agent pool
   - Minimum activation thresholds
   - Burst prevention mechanisms
   - Load balancing constraints

### Termination Detection

The Supervisor recognizes completion through:

- **Goal Achievement**: Research objectives satisfied
- **Convergence Detection**: No further improvements possible
- **Resource Exhaustion**: Budget or time limits reached
- **Quality Threshold**: Sufficient high-quality hypotheses generated
- **User Intervention**: Explicit termination request

### Failure Handling

When failures occur, the Supervisor:

1. **Isolates Impact**: Prevents cascade failures
2. **Logs Context**: Records detailed failure information
3. **Attempts Recovery**: Retries with adjusted parameters
4. **Escalates Gracefully**: Notifies user of persistent issues
5. **Maintains Progress**: Preserves all successful work

## Performance Monitoring

### System Metrics

The Supervisor tracks:

- **Throughput Metrics**
  - Tasks completed per minute
  - Average task execution time
  - Queue depth over time
  - Worker utilization rates

- **Quality Metrics**
  - Hypothesis improvement rates
  - Review coverage percentages
  - Tournament completion speed
  - Meta-review satisfaction scores

- **Efficiency Metrics**
  - Resource consumption per hypothesis
  - Agent effectiveness ratios
  - Overhead percentage
  - Scaling efficiency

### Adaptive Behaviors

Based on metrics, the Supervisor:

- **Adjusts Priorities**: Reorders tasks for optimal flow
- **Reallocates Resources**: Shifts budget to effective agents
- **Modifies Strategy**: Changes agent weights dynamically
- **Scales Operations**: Adds/removes workers as needed
- **Optimizes Queues**: Adjusts depth limits and timeouts

## Boundary Conditions

### Operational Limits

The Supervisor operates within:

- **Worker Count**: Maximum concurrent processes (configurable)
- **Memory Budget**: Total Context Memory allocation
- **API Rate Limits**: External service constraints
- **Compute Budget**: Total resource allocation
- **Time Constraints**: Maximum operation duration

### Error Boundaries

The Supervisor handles:

- **Agent Failures**: Individual agent crashes or timeouts
- **Resource Exhaustion**: Out of memory or compute
- **Queue Overflow**: Too many pending tasks
- **External Failures**: Tool or service unavailability
- **State Corruption**: Invalid Context Memory data

## Example Scenarios

### Scenario 1: Initial Research Phase

```
Input: Research goal "Find novel antimicrobial resistance mechanisms"
Behavior:
1. Parse goal into initial generation tasks
2. Weight Generation Agent highly (0.7)
3. Create 10 parallel generation tasks
4. Monitor hypothesis quality distribution
5. Transition to reflection phase when 50 hypotheses generated
```

### Scenario 2: Tournament Coordination

```
State: 100 hypotheses awaiting ranking
Behavior:
1. Activate Proximity Agent for clustering
2. Create tournament brackets based on clusters
3. Assign Ranking Agents to parallel matches
4. Monitor Elo rating convergence
5. Schedule detailed debates for top 20%
```

### Scenario 3: Resource Pressure

```
Condition: 80% resource utilization, growing queue
Behavior:
1. Analyze agent effectiveness metrics
2. Reduce weight of least effective agents
3. Increase priority of high-impact tasks
4. Defer non-critical operations
5. Request additional resources if available
```

## Quality Requirements

The Supervisor Agent ensures:

- **Reliability**: 99.9% task completion rate
- **Fairness**: No agent starved of resources
- **Efficiency**: <5% overhead on task execution
- **Responsiveness**: <1 second queue operations
- **Recoverability**: Full restart in <30 seconds

These requirements ensure the AI Co-Scientist system operates smoothly, scales effectively, and achieves research goals reliably through intelligent orchestration.