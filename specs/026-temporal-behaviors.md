# Temporal Behaviors Specification

**Type**: System-wide Behaviors  
**Status**: Core Specification

## Prerequisites
- Read: 005-supervisor-agent.md (orchestration timing)
- Read: 012-meta-review-agent.md (periodic synthesis)
- Read: 015-context-memory.md (checkpoint intervals)

## Purpose

This specification defines all temporal behaviors in the AI Co-Scientist system, clarifying when operations occur, how often they repeat, and what triggers various system activities. These behaviors ensure predictable, consistent system operation across all deployments.

## System-Wide Temporal Definitions

### Periodic Operations

The system defines "periodic" operations based on configurable intervals with the following defaults:

```yaml
periodic_intervals:
  meta_review_synthesis:
    trigger: "BOTH"
    iteration_count: 10
    time_interval: "60 minutes"
    description: "Synthesize feedback after 10 iterations OR 60 minutes, whichever comes first"
    
  context_checkpoint:
    trigger: "BOTH"
    task_count: 50
    time_interval: "5 minutes"
    description: "Create checkpoint after 50 tasks OR 5 minutes, whichever comes first"
    
  supervisor_statistics:
    trigger: "EVENT"
    event: "iteration_complete"
    description: "Update statistics after each iteration completes"
    
  health_monitoring:
    trigger: "TIME"
    interval: "30 seconds"
    description: "Check system health every 30 seconds"
```

### Staleness Definitions

Data becomes "stale" based on age or lack of activity:

```yaml
staleness_thresholds:
  hypothesis:
    becomes_stale_after: "3 evolution cycles without Elo improvement"
    handling: "Deprioritize in tournaments, mark for potential removal"
    
  feedback:
    expires_after: "10 iterations"
    handling: "Remove from agent prompts, archive for historical analysis"
    
  web_search_results:
    cache_duration: "24 hours"
    handling: "Invalidate cache, fetch fresh results on next access"
    
  tournament_matches:
    timeout: "5 minutes"
    handling: "Declare timeout, no Elo change, reschedule match"
```

## Agent-Specific Temporal Behaviors

### Generation Agent
```yaml
timing:
  activation: "On new research goal OR evolution request"
  execution_timeout: "300 seconds per batch"
  batch_size: "10-20 hypotheses"
  retry_delay: "Exponential backoff: 5s, 15s, 45s"
```

### Reflection Agent
```yaml
timing:
  activation: "Immediately after hypothesis generation/evolution"
  review_timeout:
    initial: "30 seconds"
    full: "60 seconds"
    deep_verification: "180 seconds"
  queue_priority: "High for new hypotheses, medium for re-reviews"
```

### Ranking Agent
```yaml
timing:
  activation: "After reflection completes OR on-demand for tournaments"
  match_timeout: "60 seconds per comparison"
  tournament_round_limit: "5 minutes for 100 hypotheses"
  elo_update_frequency: "After each match completes"
```

### Evolution Agent
```yaml
timing:
  activation: "After tournament establishes top 20% OR every 5 iterations"
  evolution_timeout: "120 seconds per hypothesis"
  cooldown_period: "Must wait 2 iterations between evolving same hypothesis"
```

### Proximity Agent
```yaml
timing:
  activation: "After new hypotheses added OR every 3 iterations"
  computation_timeout: "180 seconds for full graph update"
  incremental_update: "30 seconds for new hypotheses only"
```

### Meta-review Agent
```yaml
timing:
  activation: "Every meta_review_interval (see periodic_intervals)"
  synthesis_timeout: "300 seconds"
  feedback_incorporation: "Next iteration after synthesis completes"
```

## Iteration and Session Timing

### Research Session Lifecycle
```yaml
session_timing:
  initialization: "Up to 60 seconds for goal parsing and safety check"
  
  iteration_cycle:
    minimum_duration: "5 minutes"
    maximum_duration: "30 minutes"
    components:
      - generation: "20% of iteration time"
      - reflection: "30% of iteration time"
      - ranking: "30% of iteration time"  
      - evolution: "15% of iteration time"
      - overhead: "5% of iteration time"
      
  termination_timeout: "24 hours maximum session duration"
  graceful_shutdown: "Complete current iteration, then stop"
```

### Concurrency Timing
```yaml
concurrent_operations:
  max_parallel_reflections: 10
  max_parallel_tournaments: 5
  max_parallel_evolutions: 3
  
  resource_contention:
    wait_timeout: "30 seconds"
    fallback: "Queue for next available slot"
```

## Timeout Escalation

When operations exceed their allocated time:

```yaml
timeout_handling:
  warning_threshold: "80% of timeout"
  action_at_warning: "Log performance warning"
  
  timeout_exceeded:
    first_attempt: "Gracefully terminate, save partial results"
    second_attempt: "Force terminate, mark as failed"
    third_attempt: "Skip task, alert supervisor"
    
  cascading_timeouts:
    threshold: "3 timeouts in 5 minutes"
    action: "Pause agent, diagnostic mode"
```

## Time-Based Triggers

### Automatic Actions
```yaml
scheduled_actions:
  hypothesis_pruning:
    when: "Every 20 iterations"
    action: "Remove bottom 10% by Elo if > 500 hypotheses"
    
  memory_optimization:
    when: "Every hour"
    action: "Archive old iterations, compress context"
    
  performance_review:
    when: "Every 100 iterations"
    action: "Analyze agent performance, adjust timeouts"
```

## Temporal Coordination

### Event Sequencing
```yaml
event_chains:
  hypothesis_lifecycle:
    sequence:
      - "Generation completes"
      - "Wait 0-5 seconds for batch accumulation"
      - "Reflection begins"
      - "Ranking queued after reflection"
      - "Evolution eligible after ranking stabilizes"
    
  feedback_loop:
    sequence:
      - "Meta-review completes synthesis"
      - "Wait for current iteration to complete"
      - "Incorporate feedback at iteration boundary"
      - "New iteration begins with updated prompts"
```

## Performance Expectations

### Latency Requirements
```yaml
response_times:
  user_query_acknowledgment: "< 1 second"
  first_hypothesis_generation: "< 30 seconds"
  status_update_frequency: "Every 10 seconds during processing"
  result_compilation: "< 5 seconds after termination"
```

### Throughput Targets
```yaml
processing_rates:
  hypotheses_per_hour: "100-500 depending on complexity"
  reviews_per_minute: "20-30 initial reviews"
  tournaments_per_iteration: "Sufficient for O(n log n) comparisons"
  evolution_cycles_per_session: "5-20 depending on duration"
```

## Clock Synchronization

All system components MUST use consistent time sources:
- Use UTC for all timestamps
- Synchronize clocks within 1 second accuracy
- Handle clock drift gracefully
- Log all times with timezone information

## Configuration Override

All temporal values MUST be configurable at deployment time:
- Default values specified in this document
- Override via configuration file
- Runtime adjustment through supervisor
- Validation to prevent invalid timeout configurations

## Observable Behaviors

Implementers MUST ensure these temporal behaviors are observable:
- Log when periodic operations trigger
- Record actual vs expected timing
- Alert on consistent timeout violations
- Provide timing metrics for monitoring