# System States and Transitions Specification

**Type**: System-wide Behaviors  
**Status**: Core Specification

## Prerequisites
- Read: 003-research-workflow.md (session lifecycle)
- Read: 005-supervisor-agent.md (orchestration states)
- Read: 021-validation-criteria.md (quality states)

## Purpose

This specification defines all system states, valid transitions between states, and the complete lifecycle of key entities (research sessions, hypotheses, tasks). Clear state definitions ensure predictable behavior and proper error recovery.

## Research Session States

### State Definitions

```yaml
session_states:
  INITIALIZING:
    description: "Session created, parsing research goal"
    allowed_duration: "60 seconds maximum"
    next_states: ["ACTIVE", "FAILED", "REJECTED"]
    
  ACTIVE:
    description: "Normal operation, generating and evaluating hypotheses"
    allowed_duration: "24 hours maximum"
    next_states: ["PAUSED", "TERMINATING", "FAILED"]
    
  PAUSED:
    description: "Temporarily suspended by user or system"
    allowed_duration: "7 days maximum"
    next_states: ["ACTIVE", "TERMINATING", "EXPIRED"]
    
  TERMINATING:
    description: "Gracefully shutting down, completing final tasks"
    allowed_duration: "5 minutes maximum"
    next_states: ["COMPLETED", "FAILED"]
    
  COMPLETED:
    description: "Successfully finished, results available"
    allowed_duration: "Permanent (archived after 30 days)"
    next_states: ["ARCHIVED"]
    
  FAILED:
    description: "Unrecoverable error occurred"
    allowed_duration: "Permanent (archived after 7 days)"
    next_states: ["ARCHIVED"]
    
  REJECTED:
    description: "Failed safety check or invalid goal"
    allowed_duration: "Permanent (archived after 1 day)"
    next_states: ["ARCHIVED"]
    
  EXPIRED:
    description: "Paused session exceeded time limit"
    allowed_duration: "Permanent (archived after 7 days)"
    next_states: ["ARCHIVED"]
    
  ARCHIVED:
    description: "Moved to long-term storage"
    allowed_duration: "Permanent"
    next_states: []
```

### State Transition Rules

```yaml
session_transitions:
  INITIALIZING_to_ACTIVE:
    conditions:
      - "Research goal parsed successfully"
      - "Safety check passed"
      - "Resources allocated"
    actions:
      - "Queue initial hypothesis generation"
      - "Start iteration counter"
      - "Begin logging activities"
      
  INITIALIZING_to_REJECTED:
    conditions:
      - "Safety check failed"
      - "Invalid research goal format"
      - "Prohibited research area"
    actions:
      - "Log rejection reason"
      - "Notify user with explanation"
      - "Clean up allocated resources"
      
  ACTIVE_to_PAUSED:
    conditions:
      - "User pause request"
      - "System maintenance required"
      - "Resource constraints"
    actions:
      - "Complete current agent operations"
      - "Checkpoint all state"
      - "Release non-essential resources"
      
  PAUSED_to_ACTIVE:
    conditions:
      - "User resume request"
      - "Resources available"
      - "Within pause time limit"
    actions:
      - "Restore from checkpoint"
      - "Reallocate resources"
      - "Resume task queue processing"
      
  ACTIVE_to_TERMINATING:
    conditions:
      - "Terminal state reached"
      - "User stop request"
      - "Maximum duration exceeded"
    actions:
      - "Stop accepting new tasks"
      - "Complete in-flight operations"
      - "Generate final report"
```

## Hypothesis States

### Lifecycle States

```yaml
hypothesis_states:
  GENERATED:
    description: "Newly created, awaiting review"
    timeout: "5 minutes to enter review"
    next_states: ["UNDER_REVIEW", "DISCARDED"]
    
  UNDER_REVIEW:
    description: "Being evaluated by Reflection Agent"
    timeout: "10 minutes maximum"
    next_states: ["REVIEWED", "UNSAFE", "FAILED_REVIEW"]
    
  REVIEWED:
    description: "Passed initial review, awaiting ranking"
    timeout: "None"
    next_states: ["RANKED", "DISCARDED"]
    
  RANKED:
    description: "Has Elo rating, participating in tournaments"
    timeout: "None"
    next_states: ["EVOLVING", "SELECTED", "STALE", "DISCARDED"]
    
  EVOLVING:
    description: "Being enhanced by Evolution Agent"
    timeout: "5 minutes"
    next_states: ["RANKED", "FAILED_EVOLUTION"]
    
  SELECTED:
    description: "Chosen for final output"
    timeout: "None"
    next_states: ["FINALIZED"]
    
  STALE:
    description: "No improvement for multiple cycles"
    timeout: "Until pruning"
    next_states: ["DISCARDED", "ARCHIVED"]
    
  UNSAFE:
    description: "Failed safety review"
    timeout: "Immediate"
    next_states: ["QUARANTINED"]
    
  DISCARDED:
    description: "Removed from active consideration"
    timeout: "1 hour until permanent deletion"
    next_states: ["DELETED"]
    
  FINALIZED:
    description: "Included in final output"
    timeout: "None"
    next_states: ["ARCHIVED"]
```

### State Transition Triggers

```yaml
hypothesis_transitions:
  quality_based:
    to_STALE: "No Elo improvement for 3 evolution cycles"
    to_SELECTED: "Top 10% by Elo AND confidence > 0.7"
    to_DISCARDED: "Bottom 20% when at capacity"
    
  safety_based:
    to_UNSAFE: "Any safety flag raised"
    to_QUARANTINED: "Potential dual-use identified"
    
  timeout_based:
    to_FAILED_REVIEW: "Review timeout exceeded"
    to_FAILED_EVOLUTION: "Evolution timeout exceeded"
    to_DISCARDED: "Stuck in state > timeout"
```

## Task States

### Task Queue States

```yaml
task_states:
  QUEUED:
    description: "Waiting for available worker"
    timeout: "Based on priority"
    next_states: ["ASSIGNED", "EXPIRED", "CANCELLED"]
    
  ASSIGNED:
    description: "Allocated to specific worker"
    timeout: "30 seconds to start"
    next_states: ["RUNNING", "FAILED_TO_START"]
    
  RUNNING:
    description: "Actively being processed"
    timeout: "Agent-specific (see temporal behaviors)"
    next_states: ["COMPLETED", "FAILED", "TIMEOUT"]
    
  COMPLETED:
    description: "Successfully finished"
    timeout: "5 minutes until cleanup"
    next_states: ["ACKNOWLEDGED", "ARCHIVED"]
    
  FAILED:
    description: "Error during execution"
    timeout: "Immediate"
    next_states: ["RETRY_QUEUED", "PERMANENTLY_FAILED"]
    
  TIMEOUT:
    description: "Exceeded time limit"
    timeout: "Immediate"
    next_states: ["RETRY_QUEUED", "PERMANENTLY_FAILED"]
    
  RETRY_QUEUED:
    description: "Waiting for retry attempt"
    timeout: "Based on backoff"
    next_states: ["ASSIGNED", "PERMANENTLY_FAILED"]
    
  PERMANENTLY_FAILED:
    description: "All retries exhausted"
    timeout: "1 hour until cleanup"
    next_states: ["ARCHIVED"]
    
  CANCELLED:
    description: "Explicitly cancelled"
    timeout: "Immediate cleanup"
    next_states: ["ARCHIVED"]
```

### Task Retry State Machine

```yaml
retry_behavior:
  attempts_allowed: 3
  
  backoff_sequence:
    attempt_1: "5 seconds"
    attempt_2: "30 seconds"
    attempt_3: "120 seconds"
    
  retry_conditions:
    RETRY: ["timeout", "worker_failure", "temporary_error"]
    NO_RETRY: ["invalid_input", "safety_violation", "permanent_error"]
    
  state_preservation:
    on_retry: "Maintain task context and parameters"
    on_failure: "Archive for debugging"
```

## System Component States

### Agent States

```yaml
agent_states:
  IDLE:
    description: "Ready for work"
    next_states: ["PROCESSING", "DISABLED"]
    
  PROCESSING:
    description: "Actively working on task"
    next_states: ["IDLE", "ERROR", "OVERLOADED"]
    
  OVERLOADED:
    description: "Queue full, rejecting new work"
    next_states: ["PROCESSING", "ERROR"]
    
  ERROR:
    description: "Recoverable error state"
    next_states: ["IDLE", "DISABLED"]
    
  DISABLED:
    description: "Administratively disabled"
    next_states: ["IDLE"]
```

### Worker Process States

```yaml
worker_states:
  STARTING:
    timeout: "30 seconds"
    next_states: ["READY", "FAILED_START"]
    
  READY:
    description: "Available for task assignment"
    next_states: ["BUSY", "SHUTTING_DOWN"]
    
  BUSY:
    description: "Processing assigned task"
    next_states: ["READY", "CRASHED"]
    
  SHUTTING_DOWN:
    description: "Graceful termination"
    timeout: "60 seconds"
    next_states: ["TERMINATED"]
    
  CRASHED:
    description: "Unexpected termination"
    next_states: ["RESTARTING", "TERMINATED"]
    
  TERMINATED:
    description: "Process ended"
    next_states: []
```

## Conflict Resolution States

### Concurrent Access States

```yaml
resource_conflict_states:
  AVAILABLE:
    description: "Resource free for use"
    next_states: ["LOCKED", "RESERVED"]
    
  LOCKED:
    description: "Exclusive access granted"
    timeout: "Based on operation"
    next_states: ["AVAILABLE", "FORCE_RELEASED"]
    
  RESERVED:
    description: "Queued for future access"
    timeout: "30 seconds"
    next_states: ["LOCKED", "TIMEOUT_RELEASED"]
    
  FORCE_RELEASED:
    description: "Lock broken due to timeout"
    next_states: ["AVAILABLE"]
```

## State Monitoring and Enforcement

### State Invariants

```yaml
invariants:
  session_level:
    - "Only one session state active at a time"
    - "Completed sessions cannot return to active"
    - "Failed states are terminal except for retry"
    
  hypothesis_level:
    - "Safety violations immediately transition to UNSAFE"
    - "Cannot evolve hypotheses not yet ranked"
    - "Selected hypotheses are immutable"
    
  system_level:
    - "Worker count within min/max bounds"
    - "No orphaned tasks (all tasks have owner)"
    - "State transitions are atomic"
```

### State Change Notifications

```yaml
notifications:
  user_visible:
    - "Session state changes"
    - "Hypothesis selection"
    - "Error states"
    
  system_internal:
    - "All state transitions"
    - "Timeout warnings"
    - "Resource state changes"
    
  audit_log:
    - "State transition timestamp"
    - "Trigger condition"
    - "Actor (user/system/timeout)"
```

## Recovery from Invalid States

### Detection and Correction

```yaml
invalid_state_handling:
  detection:
    - "Periodic state validation sweep"
    - "Transition validation before execution"
    - "Timeout enforcement threads"
    
  correction_actions:
    zombie_tasks: "Force transition to FAILED"
    orphaned_hypotheses: "Move to DISCARDED"
    stuck_sessions: "Transition to TERMINATING"
    invalid_transitions: "Revert to previous valid state"
```

## Observable State Behaviors

Systems MUST provide:
- Real-time state visualization
- State transition history
- Time spent in each state
- State-based metrics and alerts
- Debugging information for invalid states