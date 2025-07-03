# Supervisor Agent Specification

**Type**: Agent  
**Interactions**: All Specialized Agents, Context Memory, Research Configuration

## Prerequisites
- Read: System Overview and Architecture Specification
- Read: Multi-Agent Framework Specification
- Read: Asynchronous Task Execution Framework Specification
- Read: Context Memory System Specification

## Purpose

The Supervisor Agent serves as the central orchestrator of the AI Co-Scientist multi-agent system. It coordinates all specialized agents, manages task queues, allocates computational resources, and makes strategic decisions to guide the system toward achieving the research goal through iterative hypothesis generation and refinement.

## Agent Behavior

The Supervisor Agent exhibits the following behaviors:

1. **Research Plan Evaluation**: Analyzes research configuration to understand requirements and constraints
2. **Task Queue Management**: Creates and maintains asynchronous task queues for system operations
3. **Resource Allocation**: Assigns computational resources and agent weights based on system needs
4. **Agent Orchestration**: Coordinates specialized agents without direct agent-to-agent communication
5. **System State Monitoring**: Computes comprehensive statistics to track progress
6. **Strategic Decision Making**: Determines next operations based on system state and performance
7. **Terminal State Detection**: Identifies when research goals have been sufficiently addressed

## Inputs

### From Research Configuration
```
ResearchPlan {
  goal: string (natural language research objective)
  preferences: dict (user preferences for research approach)
  constraints: list[string] (limitations and boundaries)
  attributes: dict (specific research attributes)
  max_iterations: int (optional)
  resource_limits: ResourceLimits (optional)
}
```

### From Context Memory
```
SystemState {
  hypothesis_statistics: HypothesisStats
  agent_performance: dict[AgentType, PerformanceMetrics]
  review_queue_status: QueueStatus
  tournament_progress: TournamentState
  generation_effectiveness: dict[Method, Effectiveness]
  system_health: HealthMetrics
}
```

### From Agent Operations
```
TaskCompletion {
  agent_type: AgentType
  task_id: string
  status: Success | Failure | Partial
  results_summary: dict
  resource_usage: ResourceMetrics
  duration: timedelta
}
```

## Outputs

### Task Assignment
```
TaskAssignment {
  task_id: string
  agent_type: AgentType
  priority: High | Medium | Low
  parameters: dict
  resource_allocation: ResourceAllocation
  timeout: timedelta
  dependencies: list[task_id]
}
```

### Agent Weight Configuration
```
AgentWeights {
  generation_weight: float
  reflection_weight: float
  ranking_weight: float
  evolution_weight: float
  proximity_weight: float
  meta_review_weight: float
  timestamp: datetime
  rationale: string
}
```

### System Decision
```
SystemDecision {
  decision_type: DecisionType
  action: string
  parameters: dict
  expected_outcome: string
  confidence: float
  timestamp: datetime
}
```

## Core Behaviors

### 1. Research Plan Processing

**Behavior**:
- Parses incoming research configuration
- Validates constraints and requirements
- Determines initial resource allocation strategy
- Sets system parameters based on research complexity

**Process**:
1. Extract key research objectives
2. Identify domain-specific requirements
3. Map constraints to system capabilities
4. Configure initial agent weights
5. Establish success criteria

### 2. Task Queue Management

**Behavior**:
- Maintains priority queues for different agent types
- Ensures proper task sequencing
- Handles task dependencies
- Manages concurrent execution limits

**Queue Structure**:
```
TaskQueue {
  high_priority: list[Task]
  medium_priority: list[Task]
  low_priority: list[Task]
  blocked_tasks: list[Task]
  active_tasks: dict[agent_id, Task]
}
```

**Sequencing Rules**:
- Generation tasks before initial Reflection
- Reflection completion before Ranking
- Ranking results before Evolution
- Meta-review after significant system changes

### 3. Dynamic Resource Allocation

**Behavior**:
- Monitors computational resource usage
- Adjusts agent weights based on effectiveness
- Scales worker processes based on demand
- Balances exploration vs exploitation

**Weight Adjustment Strategies**:
- Increase Generation weight when hypothesis diversity is low
- Boost Reflection weight when quality issues arise
- Enhance Evolution weight when improvements plateau
- Raise Ranking weight during tournament phases

### 4. System State Monitoring

**Behavior**:
- Periodically computes comprehensive statistics
- Identifies bottlenecks and inefficiencies
- Detects stagnation or loops
- Monitors overall progress metrics

**Key Metrics Tracked**:
```
SystemMetrics {
  total_hypotheses: int
  hypotheses_pending_review: int
  hypotheses_in_tournament: int
  average_hypothesis_quality: float
  generation_method_effectiveness: dict[Method, float]
  agent_utilization: dict[AgentType, float]
  system_throughput: float
  time_to_terminal_state: timedelta
}
```

### 5. Strategic Decision Making

**Behavior**:
- Analyzes current system state
- Determines optimal next actions
- Adapts strategy based on performance
- Balances multiple objectives

**Decision Types**:
1. **Generation Strategy**: Which generation methods to emphasize
2. **Review Depth**: Standard vs deep verification reviews
3. **Tournament Initiation**: When to start ranking competitions
4. **Evolution Focus**: Enhancement vs combination vs simplification
5. **Resource Reallocation**: Shifting compute between agents

**Decision Factors**:
- Current hypothesis quality distribution
- Time remaining vs progress made
- Resource utilization efficiency
- Meta-review feedback patterns
- Domain-specific requirements

### 6. Agent Coordination Patterns

**Behavior**:
- Enforces no direct agent-to-agent communication
- Routes all coordination through task assignments
- Manages agent lifecycle (start, pause, resume, stop)
- Handles agent failures gracefully

**Coordination Mechanisms**:
- Task-based communication only
- Shared state via Context Memory
- Event-driven notifications
- Asynchronous result collection

### 7. Terminal State Detection

**Behavior**:
- Evaluates research goal satisfaction
- Checks iteration limits
- Assesses hypothesis quality threshold
- Monitors diminishing returns

**Terminal Conditions**:
```
TerminalCriteria {
  max_iterations_reached: boolean
  quality_threshold_met: boolean
  diversity_saturation: boolean
  resource_limit_reached: boolean
  user_intervention: boolean
  stagnation_detected: boolean
}
```

## State Management

### Read Operations
- Query current hypothesis statistics
- Check agent performance metrics
- Monitor queue depths
- Review resource utilization
- Access meta-review summaries

### Write Operations
- Update agent weight configurations
- Record task assignments
- Log decision rationale
- Store performance snapshots
- Checkpoint system state

## Error Handling

### Agent Failure Recovery
1. **Detection**: Monitor task timeouts and error reports
2. **Isolation**: Quarantine failed tasks
3. **Analysis**: Determine failure cause
4. **Recovery**: Reassign task or adjust strategy
5. **Learning**: Update agent weights based on failures

### Resource Exhaustion
- Pause low-priority tasks
- Reduce concurrent execution
- Clear intermediate results
- Request additional resources
- Gracefully degrade functionality

### Stagnation Detection
- Monitor hypothesis novelty trends
- Track improvement rates
- Detect repetitive patterns
- Inject diversity through weight adjustments
- Consider alternative strategies

## Performance Optimization

### Adaptive Scheduling
- Priority-based task assignment
- Dynamic batch sizing
- Load balancing across workers
- Preemptive resource allocation
- Predictive queue management

### Decision Caching
- Cache effective weight configurations
- Store successful strategy patterns
- Reuse decision trees for similar states
- Maintain performance history
- Enable rapid strategy switching

## Integration Patterns

### With Specialized Agents
- Issues task assignments with clear parameters
- Collects completion notifications
- Aggregates performance metrics
- Adjusts weights based on effectiveness
- Manages agent lifecycle

### With Context Memory
- Periodic state checkpointing
- Atomic updates for consistency
- Bulk reads for analysis
- Event stream for real-time monitoring
- Recovery state restoration

## Success Metrics

The Supervisor Agent's effectiveness is measured by:
1. **System Throughput**: Tasks completed per hour
2. **Goal Achievement**: Progress toward research objectives
3. **Resource Efficiency**: Compute utilization percentage
4. **Adaptation Speed**: Time to adjust to performance changes
5. **Failure Recovery**: Mean time to recover from errors

## Configuration Parameters

```
SupervisorConfig {
  monitoring_interval: timedelta (default: 5 minutes)
  decision_threshold: float (default: 0.7)
  max_concurrent_tasks: int (default: 10)
  weight_adjustment_rate: float (default: 0.1)
  stagnation_window: int (default: 3 iterations)
  checkpoint_frequency: timedelta (default: 30 minutes)
  resource_limits: ResourceLimits
}
```

## Examples

### Initial System Configuration
```
Input: Research goal "Find novel AML drug targets"
Actions:
1. Set generation_weight = 0.4 (high initial exploration)
2. Set reflection_weight = 0.3 (quality control)
3. Set evolution_weight = 0.1 (limited initially)
4. Queue 10 generation tasks
5. Monitor for 30 minutes before adjustment
```

### Dynamic Weight Adjustment
```
Observation: Low hypothesis quality scores
Actions:
1. Increase reflection_weight to 0.4
2. Enable deep_verification reviews
3. Reduce generation_weight to 0.3
4. Queue additional reflection tasks
5. Re-evaluate after 5 iterations
```

### Terminal State Detection
```
Conditions Met:
- 500 hypotheses generated
- Top 10 consistently high quality
- No new insights in 3 iterations
- 95% of research space explored
Decision: Signal terminal state reached
```

## Boundaries

**What the Supervisor Agent Does**:
- Orchestrates the entire multi-agent system
- Makes strategic resource allocation decisions
- Monitors system health and progress
- Adapts to changing performance patterns
- Ensures efficient progress toward research goals

**What the Supervisor Agent Does Not Do**:
- Generate hypotheses directly (Generation Agent's role)
- Evaluate hypothesis quality (Reflection Agent's role)
- Perform hypothesis ranking (Ranking Agent's role)
- Modify hypotheses (Evolution Agent's role)
- Conduct scientific analysis (Specialized agents' roles)
- Communicate directly between agents (uses task queue pattern)