# Multi-Agent Architecture Specification

**Type**: System Architecture Pattern  
**Interactions**: All Agents, Context Memory, Task Queue, External Tools

## Prerequisites
- Read: System Overview Specification
- Read: Core Principles Specification  
- Read: Research Workflow Specification

## Purpose

This specification defines the collaborative architecture pattern that enables seven specialized agents to work together asynchronously to achieve scientific hypothesis generation and refinement. The architecture emphasizes loose coupling, scalability, and continuous improvement without traditional machine learning techniques.

## Architecture Components

### Agent Types

The system includes seven distinct agent types, each with specialized responsibilities:

1. **Supervisor Agent**: Central orchestrator and resource manager
2. **Generation Agent**: Hypothesis creator
3. **Reflection Agent**: Scientific peer reviewer
4. **Ranking Agent**: Tournament organizer and evaluator
5. **Evolution Agent**: Hypothesis refiner
6. **Proximity Agent**: Similarity calculator
7. **Meta-Review Agent**: Pattern synthesizer and feedback provider

### Collaboration Model

The multi-agent system operates on these principles:

- **No Direct Communication**: Agents never communicate directly with each other
- **Supervisor-Mediated**: All agent interactions occur through the Supervisor
- **Shared State**: Agents access common state through Context Memory
- **Asynchronous Execution**: Agents operate independently on assigned tasks
- **Queue-Based**: Tasks distributed via centralized task queue

## Behavioral Patterns

### Task Distribution Pattern

The Supervisor Agent manages work distribution:

1. **Task Creation**: Research goals parsed into discrete tasks
2. **Queue Management**: Tasks placed in priority queue
3. **Worker Assignment**: Available workers receive tasks from queue
4. **Result Collection**: Completed work stored in Context Memory
5. **Progress Monitoring**: System statistics guide resource allocation

### Information Flow Pattern

Information flows through the system in defined pathways:

```
Research Goal → Supervisor → Task Queue → Worker Process → Agent
                    ↑                           ↓
                    └──── Context Memory ←──────┘
```

### Feedback Loop Pattern

The Meta-Review Agent enables system-wide learning:

1. **Pattern Recognition**: Analyzes outputs across all agents
2. **Feedback Generation**: Creates actionable insights
3. **Prompt Enhancement**: Feedback appended to agent prompts
4. **No Backpropagation**: Improvement without model retraining

## Agent Interaction Protocols

### Supervisor-to-Agent Protocol

The Supervisor communicates with agents through:
- **Task Assignment**: Specific work items with parameters
- **Resource Allocation**: Computational budget for tasks
- **Priority Indication**: Task urgency and importance
- **Termination Signals**: When to stop processing

### Agent-to-Context Memory Protocol

Agents interact with shared state by:
- **Reading**: Accessing prior results and system state
- **Writing**: Storing outputs and intermediate results
- **Querying**: Searching for relevant prior work
- **Updating**: Modifying progress indicators

### Tool Access Protocol

Agents access external resources through:
- **Web Search**: Literature and knowledge retrieval
- **Specialized Models**: Domain-specific AI tools
- **Databases**: Scientific data repositories
- **Computation Services**: Resource-intensive calculations

## Scalability Behaviors

The architecture scales through:

### Horizontal Scaling
- **Multiple Workers**: Parallel task execution
- **Dynamic Allocation**: Workers added based on load
- **Queue Depth Monitoring**: Automatic scaling triggers
- **Resource Balancing**: Fair distribution across workers

### Vertical Scaling
- **Compute Budget**: More resources for complex tasks
- **Tournament Depth**: Extended debates for top hypotheses
- **Review Iterations**: Additional passes for critical ideas
- **Evolution Rounds**: More refinement for promising concepts

## Resilience Behaviors

The system maintains operation through:

### Failure Handling
- **Task Retry**: Failed tasks return to queue
- **State Persistence**: Context Memory enables recovery
- **Graceful Degradation**: System continues with reduced capacity
- **Isolation**: Agent failures don't cascade

### Progress Preservation
- **Checkpoint Storage**: Regular state snapshots
- **Incremental Progress**: Partial results saved
- **Restart Capability**: Resume from last checkpoint
- **No Work Loss**: Completed tasks always preserved

## Coordination Examples

### Example 1: Initial Hypothesis Generation

1. **Supervisor** receives research goal: "Find novel AML drug targets"
2. **Supervisor** creates generation task with parameters
3. **Generation Agent** assigned to worker process
4. **Generation Agent** queries Context Memory for prior work
5. **Generation Agent** uses web search for literature
6. **Generation Agent** produces 20 hypothesis candidates
7. **Results** stored in Context Memory
8. **Supervisor** creates reflection tasks for each hypothesis

### Example 2: Tournament-Based Ranking

1. **Proximity Agent** computes similarity matrix for 50 hypotheses
2. **Supervisor** uses matrix to create tournament brackets
3. **Multiple Ranking Agents** assigned pairwise comparisons
4. **Parallel execution** of tournament matches
5. **Results** aggregated in Context Memory
6. **Elo ratings** updated after each match
7. **Supervisor** schedules detailed debates for top 10

### Example 3: Meta-Review Feedback Loop

1. **Meta-Review Agent** analyzes 100+ completed reviews
2. **Pattern identified**: "Hypotheses lack mechanistic detail"
3. **Feedback generated**: Specific improvement suggestions
4. **Supervisor** updates Generation Agent prompts
5. **Next generation** produces more detailed hypotheses
6. **System improvement** without retraining

## System Invariants

The architecture maintains these properties:

1. **Agent Independence**: No agent depends on another's internal state
2. **Eventual Consistency**: All agents see same Context Memory state
3. **Progress Guarantee**: System always moves toward completion
4. **Resource Fairness**: All agents receive necessary compute
5. **Transparency**: All decisions traceable through Context Memory

## Integration Points

The architecture provides interfaces for:

### External Systems
- **Tool APIs**: Standardized access to external resources
- **Data Sources**: Scientific database connections
- **Compute Resources**: Cloud or cluster integration
- **Monitoring**: Observability and metrics export

### Human Interaction
- **Goal Specification**: Natural language research objectives
- **Manual Review**: Expert hypothesis evaluation
- **Idea Injection**: Adding human-generated hypotheses
- **Progress Monitoring**: Real-time system observation

## Performance Characteristics

The architecture exhibits:

- **Linear Scalability**: Performance scales with workers
- **Bounded Latency**: Task completion within time limits
- **Efficient Queuing**: Minimal task waiting time
- **Adaptive Throughput**: Adjusts to workload variations

## Boundary Conditions

The architecture operates within:

- **Worker Limits**: Maximum concurrent processes
- **Memory Constraints**: Context Memory size bounds
- **API Rate Limits**: External tool access restrictions
- **Compute Budget**: Total resource allocation

These boundaries ensure predictable system behavior while maintaining flexibility for diverse research tasks.