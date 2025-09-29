# Agent Interaction Protocols Specification

**Type**: System Behavior  
**Interactions**: All Agents, Supervisor Agent, Context Memory, Task Queue

## Prerequisites

- Read: 004-multi-agent-architecture.md
- Read: 005-supervisor-agent.md
- Read: 006-task-queue-behavior.md
- Understand: Asynchronous task execution patterns
- Understand: Shared state management concepts

## Purpose

This specification defines the protocols governing communication and coordination between agents in the AI Co-Scientist system. All agent interactions follow a supervisor-mediated pattern with no direct agent-to-agent communication, ensuring system coherence and enabling asynchronous operation.

## Core Communication Principles

### 1. No Direct Agent Communication
- Agents MUST NOT communicate directly with other agents
- All coordination MUST flow through the Supervisor Agent
- Agent outputs become inputs to other agents only via Supervisor orchestration

### 2. Asynchronous Operation
- Agents operate as independent worker processes
- Communication is inherently asynchronous
- No agent may block waiting for another agent's response

### 3. Shared State Management
- Context Memory serves as the persistent communication hub
- All inter-agent data exchange occurs through Context Memory
- Agents MUST read current state before processing
- Agents MUST write results atomically to avoid race conditions

## Communication Patterns

### Pattern 1: Task Assignment Protocol

**Flow**: Supervisor → Task Queue → Worker Process → Agent

**Protocol**:
1. Supervisor WRITES task to Task Queue with:
   - task_id: unique identifier
   - agent_type: target agent specification
   - input_data: required inputs for the agent
   - priority: execution priority
   - dependencies: list of prerequisite task_ids

2. Worker Process READS from Task Queue
3. Worker Process INSTANTIATES specified agent
4. Agent READS input_data and Context Memory
5. Agent EXECUTES assigned task
6. Agent WRITES results to Context Memory
7. Agent SIGNALS task completion to Supervisor

### Pattern 2: Feedback Propagation Protocol

**Flow**: Agent → Context Memory → Meta-review Agent → Context Memory → Other Agents

**Protocol**:
1. Source Agent WRITES outputs to Context Memory:
   - agent_id: identifier of writing agent
   - output_type: hypothesis/review/ranking/etc.
   - content: actual output data
   - timestamp: creation time
   - metadata: additional context

2. Meta-review Agent READS accumulated outputs when triggered
3. Meta-review Agent GENERATES synthesis feedback
4. Meta-review Agent WRITES feedback to Context Memory:
   - feedback_type: meta_review/research_overview
   - target_agents: list of agents to receive feedback
   - feedback_content: synthesized insights
   - incorporation_strategy: how to use feedback

5. Target Agents READ feedback on next execution
6. Target Agents INCORPORATE feedback via prompt augmentation

### Pattern 3: Tournament Coordination Protocol

**Flow**: Ranking Agent → Supervisor → Multiple Worker Processes → Context Memory

**Protocol**:
1. Ranking Agent REQUESTS tournament via Supervisor:
   - hypothesis_pairs: list of hypotheses to compare
   - debate_format: type of scientific debate
   - evaluation_criteria: scoring parameters

2. Supervisor CREATES parallel debate tasks
3. Multiple Worker Processes EXECUTE debates concurrently
4. Each debate WRITES results to Context Memory:
   - debate_id: unique identifier
   - winner_id: winning hypothesis
   - loser_id: losing hypothesis
   - debate_transcript: full debate content
   - confidence_score: result certainty

5. Ranking Agent READS all debate results
6. Ranking Agent UPDATES Elo ratings
7. Ranking Agent WRITES updated rankings to Context Memory

## Data Exchange Formats

### Standard Message Structure
```
Message:
  header:
    message_id: string (UUID)
    source_agent: string
    target_agent: string (or "broadcast")
    timestamp: datetime
    message_type: string
  payload:
    data: agent-specific content
    metadata: optional context
  routing:
    priority: integer (1-10)
    expires_at: datetime (optional)
```

### Context Memory Entry Structure
```
ContextEntry:
  entry_id: string (UUID)
  agent_id: string (creator)
  entry_type: string (hypothesis/review/ranking/feedback/etc.)
  content: structured data
  created_at: datetime
  updated_at: datetime
  version: integer
  dependencies: list[entry_id]
```

## Synchronization Protocols

### 1. Read-Before-Write Protocol
Agents MUST:
1. READ relevant Context Memory entries
2. VALIDATE no conflicting updates occurred
3. WRITE new results with version tracking
4. RETRY if version conflict detected

### 2. Dependency Resolution Protocol
When task has dependencies:
1. Agent CHECKS all dependency task_ids are complete
2. Agent READS outputs from dependent tasks
3. Agent PROCEEDS only when all dependencies satisfied
4. Agent REPORTS error if dependencies fail

### 3. Resource Coordination Protocol
For shared resources (web search, external tools):
1. Agent REQUESTS resource lock from Supervisor
2. Supervisor GRANTS or QUEUES request based on availability
3. Agent USES resource within time limit
4. Agent RELEASES resource on completion
5. Supervisor REALLOCATES to queued requests

## Error Handling Protocols

### 1. Task Failure Protocol
When agent encounters error:
1. Agent WRITES error details to Context Memory
2. Agent SIGNALS failure to Supervisor
3. Supervisor EVALUATES retry strategy
4. Supervisor MAY reassign task or escalate to scientist

### 2. Communication Timeout Protocol
For time-sensitive operations:
1. Supervisor SETS timeout for each task
2. Worker Process MONITORS execution time
3. If timeout exceeded:
   - Worker INTERRUPTS agent execution
   - Worker WRITES partial results if available
   - Supervisor DECIDES on retry or alternative approach

### 3. State Consistency Protocol
To maintain system coherence:
1. Agents MUST use atomic writes
2. Agents MUST handle partial state gracefully
3. Supervisor PERFORMS periodic consistency checks
4. System PROVIDES rollback capability for critical errors

## Agent Interaction Examples

### Example 1: Hypothesis Generation and Review
```
1. Supervisor assigns Generation Agent task
2. Generation Agent:
   - READS research goal from Context Memory
   - READS previous meta-review feedback
   - GENERATES new hypotheses
   - WRITES hypotheses to Context Memory
   
3. Supervisor detects new hypotheses
4. Supervisor assigns Reflection Agent task
5. Reflection Agent:
   - READS hypotheses from Context Memory
   - PERFORMS initial review
   - WRITES reviews to Context Memory
   
6. Process continues through ranking and evolution
```

### Example 2: Feedback-Driven Improvement
```
1. Multiple agents complete initial round
2. Supervisor triggers Meta-review Agent
3. Meta-review Agent:
   - READS all reviews and rankings
   - IDENTIFIES patterns and weaknesses
   - WRITES targeted feedback for each agent type
   
4. On next iteration:
   - Generation Agent READS its feedback
   - Generation Agent ADJUSTS strategy based on feedback
   - Process demonstrates improvement without retraining
```

### Example 3: Parallel Tournament Execution
```
1. Ranking Agent needs to compare 50 hypothesis pairs
2. Ranking Agent requests tournament from Supervisor
3. Supervisor:
   - CREATES 50 debate tasks
   - DISTRIBUTES across available workers
   - MONITORS completion progress
   
4. Workers execute debates in parallel
5. Each debate result written to Context Memory
6. Ranking Agent:
   - WAITS for all debates to complete
   - READS all results atomically
   - COMPUTES new Elo ratings
   - WRITES updated rankings
```

## Performance Characteristics

### Latency Expectations
- Intra-system communication: milliseconds
- Agent task execution: seconds to minutes
- Full iteration cycle: minutes to hours
- Dependent on task complexity and external tool usage

### Scalability Considerations
- Agents scale horizontally as worker processes
- Communication overhead grows with agent count
- Context Memory must handle concurrent access
- Supervisor becomes bottleneck at extreme scale

## Natural Language Interaction

Scientists interact with the system through natural language commands that the Supervisor translates into agent tasks:

**Scientist**: "Focus the next generation round on hypotheses that involve protein-protein interactions"

**System Response**:
1. Supervisor PARSES instruction
2. Supervisor WRITES guidance to Context Memory
3. Generation Agent READS guidance on next execution
4. Generation Agent EMPHASIZES protein interactions in output

## Success Metrics

1. **Communication Reliability**: 99.9% message delivery
2. **State Consistency**: No lost updates or race conditions
3. **Latency**: 95th percentile task assignment < 1 second
4. **Throughput**: Support 100+ concurrent agent executions
5. **Feedback Effectiveness**: Measurable improvement from feedback incorporation