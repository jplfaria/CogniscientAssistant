# Expert Intervention Points Specification

**Type**: Interface Pattern  
**Interactions**: Scientist (User), All Agents, Natural Language Interface, Context Memory

## Prerequisites
- Read: 001-system-overview.md - System behaviors and expert-in-the-loop principle
- Read: 002-core-principles.md - Expert collaboration as foundational principle
- Read: 017-natural-language-interface.md - Primary interaction mechanism
- Understand: Asynchronous task execution and state persistence

## Purpose

Expert intervention points define where and how human scientists interact with the AI Co-Scientist system to guide research, provide feedback, and make critical decisions. These intervention points ensure the system remains a collaborative tool that augments rather than replaces human expertise, maintaining scientific rigor while leveraging AI capabilities.

## Core Intervention Categories

### Strategic Research Guidance

Scientists shape the overall research direction through:

- **Goal Specification**: Define initial research objectives in natural language
- **Goal Refinement**: Modify research goals based on emerging insights
- **Scope Adjustment**: Narrow or expand research boundaries during execution
- **Direction Steering**: Guide system focus toward promising areas
- **Constraint Definition**: Set experimental, ethical, and resource boundaries

### Hypothesis Management

Scientists directly influence hypothesis generation and evaluation:

- **Custom Hypothesis Injection**: Add scientist-formulated hypotheses to the system
- **Hypothesis Review**: Rate and comment on system-generated hypotheses
- **Priority Override**: Elevate or demote specific hypotheses regardless of Elo rating
- **Safety Assessment**: Override automated safety evaluations with expert judgment
- **Selection for Validation**: Choose which hypotheses proceed to experimental testing

### Continuous Collaboration

Scientists maintain ongoing dialogue with the system:

- **Conversational Refinement**: Use natural language chat for clarification
- **Feedback Integration**: Provide insights that influence future iterations
- **Progress Monitoring**: Track research advancement and intermediate results
- **Intervention Requests**: Respond to system-initiated requests for guidance
- **Knowledge Contribution**: Supply domain expertise and unpublished insights

## Intervention Point Behaviors

### Research Goal Definition Point

**When**: System initialization or research redirection

**Scientist Actions**:
```
- Provide natural language research goal
- Attach relevant documents (PDFs, prior publications)
- Specify preferences and constraints
- Define success criteria
```

**System Responses**:
```
- Parse goal into research plan configuration
- Request clarification for ambiguous elements
- Confirm understanding before proceeding
- Present resource and timeline estimates
```

**State Transitions**:
- From: Awaiting Input
- To: Active Research (upon scientist confirmation)

### Hypothesis Review Point

**When**: After hypothesis generation and initial system review

**Scientist Actions**:
```
- Rate hypotheses (1-5 scale)
- Provide detailed comments
- Mark safety concerns
- Suggest modifications
```

**System Responses**:
```
- Update hypothesis rankings based on feedback
- Propagate ratings to tournament system
- Adjust generation strategies
- Highlight changes from feedback
```

**Persistence**: All reviews stored in Context Memory for pattern analysis

### Custom Hypothesis Submission Point

**When**: Any time during active research

**Scientist Actions**:
```
- Submit complete hypothesis with:
  - Summary statement
  - Scientific rationale
  - Experimental approach
  - Priority level
- Optionally allow system refinement
```

**System Responses**:
```
- Validate hypothesis completeness
- Enter into tournament system
- Apply same review processes as generated hypotheses
- Track provenance as scientist-contributed
```

**Integration**: Custom hypotheses compete equally in tournaments

### Research Redirection Point

**When**: Based on intermediate results or new insights

**Scientist Actions**:
```
- Identify promising directions
- Exclude unproductive paths
- Adjust evaluation criteria
- Modify resource allocation
```

**System Responses**:
```
- Acknowledge direction change
- Adjust agent behaviors accordingly
- Summarize impact on current work
- Estimate timeline changes
```

**Propagation**: Changes flow to all active agents via Supervisor

### Safety Override Point

**When**: System flags safety concerns or scientist identifies risks

**Scientist Actions**:
```
- Review safety assessment rationale
- Override with documented justification
- Add additional safety constraints
- Halt specific research directions
```

**System Responses**:
```
- Log override with full audit trail
- Apply scientist's safety determination
- Adjust safety parameters for future assessments
- Alert if patterns of concern emerge
```

**Requirements**: All overrides require explicit justification

### Experimental Selection Point

**When**: Sufficient high-quality hypotheses generated

**Scientist Actions**:
```
- Review top-ranked hypotheses
- Select subset for wet-lab validation
- Prioritize based on resources
- Request additional experimental details
```

**System Responses**:
```
- Provide detailed protocols for selected hypotheses
- Suggest experimental priorities
- Estimate resource requirements
- Generate formal research proposals if requested
```

**Output**: Experimental protocols ready for laboratory execution

## Intervention Mechanisms

### Synchronous Interventions

Immediate scientist input required:

- **Blocking Requests**: System pauses for critical decisions
- **Clarification Dialogs**: Real-time ambiguity resolution
- **Safety Confirmations**: Immediate response for risk assessment
- **Resource Approvals**: Authorization for compute-intensive operations

### Asynchronous Interventions

Scientist input integrated when available:

- **Review Queues**: Hypotheses awaiting scientist evaluation
- **Feedback Windows**: Designated times for input collection
- **Progress Checkpoints**: Scheduled intervention opportunities
- **Passive Monitoring**: Optional engagement based on scientist availability

### Proactive System Requests

System initiates intervention needs:

- **Ambiguity Detection**: Request clarification on goals
- **Resource Limits**: Seek guidance when approaching constraints
- **Safety Concerns**: Escalate potential risks for review
- **Promising Directions**: Highlight opportunities for deeper exploration

## State Management

### Intervention State Tracking

The system maintains awareness of:

```
InterventionState:
  pending_requests: List[InterventionRequest]
  completed_interventions: List[CompletedIntervention]
  scientist_availability: AvailabilityStatus
  intervention_history: TimeSeriesLog
  preference_patterns: LearnedPreferences
```

### Pause and Resume Capability

Scientists can:

- **Pause**: Halt system operation at any point
- **Inspect**: Review current state and pending actions
- **Modify**: Adjust parameters before resuming
- **Resume**: Continue with same or modified configuration

### Context Preservation

All interventions maintain:

- **Full History**: Complete record of scientist inputs
- **Decision Rationale**: Reasoning behind each intervention
- **Impact Tracking**: How interventions affected outcomes
- **Learning Integration**: Patterns used to improve future interactions

## Quality Assurance

### Intervention Effectiveness

The system ensures:

- **Clear Requests**: Unambiguous intervention prompts
- **Minimal Disruption**: Efficient use of scientist time
- **Impact Visibility**: Clear indication of intervention effects
- **Feedback Loops**: Confirmation that input was understood

### Scientist Burden Management

The system optimizes:

- **Batch Operations**: Group similar interventions
- **Priority Filtering**: Only escalate critical decisions
- **Smart Defaults**: Reduce need for routine interventions
- **Learned Preferences**: Anticipate scientist choices

## Example Intervention Flows

### Example 1: Mid-Research Pivot
```
Scientist observes unexpected pattern in early results
→ Initiates research redirection intervention
→ System summarizes current state and implications
→ Scientist provides new focus area via chat
→ System adjusts all agent behaviors
→ Research continues in new direction with full context
```

### Example 2: Safety-Critical Override
```
System flags hypothesis as potentially unsafe
→ Escalates to scientist with detailed reasoning
→ Scientist reviews domain-specific context
→ Determines research is safe with specific precautions
→ Provides override with safety protocols
→ System proceeds with enhanced monitoring
```

### Example 3: Collaborative Hypothesis Refinement
```
Scientist has novel insight based on system output
→ Submits custom hypothesis building on AI suggestion
→ Requests system evolution of the concept
→ System generates variations and improvements
→ Scientist selects most promising for lab validation
→ Selected hypotheses fast-tracked for experimental protocols
```

## Integration Requirements

### With Natural Language Interface
- All interventions use natural language as primary modality
- Structured inputs translated from conversational interactions
- Multi-turn dialogues supported for complex interventions
- Context maintained across intervention sessions

### With Supervisor Agent
- Intervention requests routed through Supervisor
- Resource allocation adjusted based on scientist guidance
- Task priorities modified per scientist direction
- Intervention impacts propagated to all agents

### With Context Memory
- All interventions persistently stored
- Patterns extracted for system improvement
- Preference learning enables anticipation
- Full audit trail maintained

### With Safety Mechanisms
- Safety overrides logged with special prominence
- Patterns of overrides trigger system review
- Enhanced monitoring after safety interventions
- Regular safety status reports to scientist

## Behavioral Guarantees

The system MUST:
- Never proceed with critical decisions without scientist approval
- Always provide clear rationale for intervention requests
- Maintain full record of all scientist inputs and their impacts
- Respect scientist time by batching non-critical interventions
- Learn from intervention patterns to reduce future burden

The system MUST NOT:
- Make autonomous decisions on safety-critical matters
- Ignore or deprioritize scientist-provided guidance
- Proceed with resource-intensive operations without approval
- Generate hypotheses outside scientist-defined boundaries
- Claim credit for scientist-contributed insights

This specification ensures the AI Co-Scientist remains a truly collaborative system where human expertise guides and enhances AI capabilities throughout the scientific discovery process.