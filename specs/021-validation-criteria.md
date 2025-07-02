# Validation Criteria Specification

**Document ID**: 021-validation-criteria
**Type**: System Behavior
**Version**: 1.0
**Status**: Draft

## Overview

The Validation Criteria specification defines the comprehensive framework for evaluating hypotheses, research goals, experimental protocols, and system outputs throughout the AI Co-Scientist workflow. This system ensures scientific rigor, safety, novelty, and alignment with research objectives.

## Prerequisites

- Read: 002-core-principles.md - Understanding of safety and expert-in-the-loop principles
- Read: 008-reflection-agent.md - Review types and evaluation processes
- Read: 020-safety-mechanisms.md - Safety validation framework
- Understand: Scientific method and peer review processes

## Core Validation Dimensions

The system evaluates all hypotheses across five primary dimensions:

### 1. Alignment
Measures how well a hypothesis addresses the specified research goal.

**Scoring**: 0.0 (completely misaligned) to 1.0 (perfectly aligned)

**Evaluation Criteria**:
- Direct relevance to research objective
- Adherence to specified constraints
- Compatibility with domain requirements
- Focus on intended outcomes

### 2. Plausibility
Assesses scientific soundness and logical consistency.

**Scoring**: 0.0 (implausible) to 1.0 (highly plausible)

**Evaluation Criteria**:
- Freedom from logical contradictions
- Consistency with established science
- Justified departures from convention
- Mechanistic coherence

### 3. Novelty
Determines originality relative to existing literature.

**Scoring**: 0.0 (known/published) to 1.0 (completely novel)

**Evaluation Criteria**:
- Absence in published literature
- Conceptual innovation
- Methodological advancement
- Non-obvious combinations

### 4. Testability
Evaluates empirical validation feasibility.

**Scoring**: 0.0 (untestable) to 1.0 (readily testable)

**Evaluation Criteria**:
- Clear experimental protocols
- Measurable outcomes
- Resource feasibility
- Timeline practicality

### 5. Safety
Ensures ethical and risk considerations.

**Scoring**: 0.0 (unsafe) to 1.0 (completely safe)

**Evaluation Criteria**:
- Absence of harmful applications
- Ethical compliance
- Controlled risk factors
- Reversibility of effects

## Validation Levels

### Level 1: Structural Validation

**Purpose**: Verify format and completeness

**Inputs**:
```
hypothesis: {
  summary: string (required, 50-200 chars)
  description: string (required, 200-2000 chars)
  protocol: string (optional, 500-5000 chars)
  metadata: object (optional)
}
```

**Behavior**:
- MUST check all required fields present
- MUST verify character length constraints
- MUST validate data types
- MUST reject malformed inputs

**Output**:
```
{
  valid: boolean
  errors: string[] (if invalid)
}
```

### Level 2: Content Validation

**Purpose**: Assess scientific content quality

**Process**:
1. Parse hypothesis components
2. Identify key claims and assumptions
3. Check internal consistency
4. Evaluate scientific grounding

**Decision Tree**:
```
IF contains logical contradictions THEN reject
ELSE IF lacks scientific basis THEN flag for review
ELSE IF assumptions unjustified THEN request clarification
ELSE accept for full evaluation
```

### Level 3: Contextual Validation

**Purpose**: Evaluate against research context

**Inputs**:
- Hypothesis to validate
- Research goal configuration
- Domain constraints
- Historical context

**Behavior**:
- MUST compare against original research goal
- MUST check domain-specific requirements
- MUST consider cumulative progress
- SHOULD identify synergies with prior work

## Validation Processes

### Initial Screening

**Time Constraint**: 30-60 seconds

**Steps**:
1. Structural validation (5 seconds)
2. Quick plausibility check (20 seconds)
3. Preliminary safety scan (10 seconds)
4. Binary decision (5 seconds)

**Output Format**:
```
{
  decision: "accept" | "reject"
  confidence: 0.0-1.0
  primary_concern: string (if rejected)
}
```

### Comprehensive Evaluation

**Time Constraint**: 3-5 minutes

**Steps**:
1. Literature search for novelty (90 seconds)
2. Detailed plausibility analysis (60 seconds)
3. Testability assessment (30 seconds)
4. Safety evaluation (30 seconds)
5. Score compilation (30 seconds)

**Output Format**:
```
{
  scores: {
    alignment: 0.0-1.0
    plausibility: 0.0-1.0
    novelty: 0.0-1.0
    testability: 0.0-1.0
    safety: 0.0-1.0
  }
  overall: 0.0-1.0 (weighted average)
  recommendation: "accept" | "reject" | "revise"
  feedback: string[]
}
```

### Deep Verification

**Time Constraint**: 5-10 minutes

**Decomposition Process**:
1. Extract core assumptions
2. Validate each assumption independently
3. Assess assumption interactions
4. Identify critical dependencies

**Assumption Validation**:
```
For each assumption:
  - supporting_evidence: string[]
  - confidence_level: 0.0-1.0
  - criticality: "core" | "supporting" | "peripheral"
  - validation_method: string
```

## Scoring Rubrics

### Novelty Scoring

| Score | Description | Example |
|-------|-------------|---------|
| 0.0-0.2 | Published identical work | Exact replication of known research |
| 0.2-0.4 | Minor variations of known work | Changing dosage in established protocol |
| 0.4-0.6 | Significant modifications | New combination of known mechanisms |
| 0.6-0.8 | Substantially new approach | Novel mechanism with some precedent |
| 0.8-1.0 | Completely novel | Unprecedented mechanism or approach |

### Testability Scoring

| Score | Description | Requirements |
|-------|-------------|--------------|
| 0.0-0.2 | Practically untestable | Requires unavailable technology |
| 0.2-0.4 | Extremely difficult | Decade-long studies, extreme cost |
| 0.4-0.6 | Challenging but feasible | Multi-year study, significant resources |
| 0.6-0.8 | Readily testable | Standard lab, 6-12 months |
| 0.8-1.0 | Easily testable | Quick experiments, clear outcomes |

## Decision Thresholds

### Acceptance Criteria

**Minimum Requirements**:
- All scores ≥ 0.3
- Safety score ≥ 0.7
- At least one score ≥ 0.8
- Overall score ≥ 0.6

### Rejection Triggers

**Automatic Rejection**:
- Safety score < 0.3
- Alignment score < 0.2
- Multiple scores < 0.3
- Critical assumption failures

### Review Triggers

**Human Review Required**:
- Safety score 0.3-0.5
- Conflicting high/low scores
- Novel approach with risks
- Ambiguous test outcomes

## Validation Feedback

### Feedback Categories

1. **Alignment Issues**
   - "Hypothesis addresses [X] instead of specified goal [Y]"
   - "Missing constraint consideration: [constraint]"
   - "Scope too broad/narrow for research objective"

2. **Plausibility Concerns**
   - "Contradicts established principle: [principle]"
   - "Assumption [X] requires justification"
   - "Mechanism unclear between [A] and [B]"

3. **Novelty Observations**
   - "Similar to [reference] but differs in [aspect]"
   - "Builds upon [work] with innovation in [area]"
   - "No prior work found on [specific aspect]"

4. **Testability Improvements**
   - "Protocol needs specificity in [step]"
   - "Consider proxy measure for [outcome]"
   - "Timeline unrealistic for [experiment]"

5. **Safety Recommendations**
   - "Add safeguard for [risk]"
   - "Consider ethical review for [aspect]"
   - "Limit scope to prevent [concern]"

## Integration Points

### Input Sources
- Generation Agent: New hypotheses
- Evolution Agent: Modified hypotheses
- Meta-Review Agent: Refined criteria
- Expert Interface: Manual submissions

### Output Consumers
- Ranking Agent: Validated hypotheses only
- Evolution Agent: Feedback for improvements
- Supervisor Agent: Validation metrics
- Expert Interface: Detailed assessments

### Validation State Management

**Persistent Storage**:
```
validation_record: {
  hypothesis_id: string
  timestamp: datetime
  validation_type: string
  scores: object
  decision: string
  feedback: string[]
  validator_version: string
}
```

**State Transitions**:
- `pending` → `validating` → `validated`
- `validated` → `re-evaluating` (on criteria change)
- Any state → `invalidated` (on new evidence)

## Performance Requirements

### Throughput
- Initial screening: 60-120 hypotheses/minute
- Comprehensive evaluation: 12-20 hypotheses/minute
- Deep verification: 6-10 hypotheses/minute

### Accuracy Targets
- False positive rate < 5% (accepting bad hypotheses)
- False negative rate < 10% (rejecting good hypotheses)
- Inter-validator agreement > 85%

### Scalability
- Parallel validation for independent hypotheses
- Batched literature searches
- Cached validation results
- Progressive evaluation depth

## Error Handling

### Validation Failures

**Incomplete Information**:
```
{
  error: "insufficient_data"
  missing_fields: string[]
  partial_scores: object
  recommendation: "gather_more_data"
}
```

**External Service Errors**:
```
{
  error: "service_unavailable"
  service: string
  fallback_decision: string
  confidence: 0.0-0.5
}
```

### Conservative Defaults

When uncertain:
- Safety: Assume unsafe (score 0.0)
- Novelty: Assume known (score 0.3)
- Testability: Assume difficult (score 0.3)
- Overall: Reject or escalate to human

## Continuous Improvement

### Validation Metrics Tracking
- Hypothesis acceptance rate by category
- Score distributions over time
- Feedback effectiveness
- Expert override patterns

### Criteria Refinement Triggers
- Expert feedback patterns
- Validation accuracy assessments
- Domain-specific requirements
- Emerging safety concerns

### Adaptive Thresholds
- Adjust based on hypothesis quality trends
- Tighten for mature research areas
- Relax for exploratory domains
- Balance discovery vs. safety

## Examples

### Example 1: Drug Repurposing Hypothesis

**Input**:
```
{
  summary: "Metformin reduces neuroinflammation in Alzheimer's",
  description: "Metformin's AMPK activation suppresses microglial inflammation...",
  protocol: "Double-blind RCT with 200 mild AD patients..."
}
```

**Validation Output**:
```
{
  scores: {
    alignment: 0.9,      // Directly addresses AD research goal
    plausibility: 0.8,   // Strong mechanistic basis
    novelty: 0.6,        // Builds on emerging research
    testability: 0.9,    // Clear protocol, feasible
    safety: 0.9          // Well-studied drug
  },
  overall: 0.82,
  recommendation: "accept",
  feedback: [
    "Consider biomarker endpoints for faster results",
    "Similar to Zhang 2023 but novel patient population"
  ]
}
```

### Example 2: Novel Diagnostic Method

**Input**:
```
{
  summary: "Quantum sensors detect single cancer cells",
  description: "Novel quantum dot arrays with AI analysis...",
  protocol: "Prototype development followed by cell line validation..."
}
```

**Validation Output**:
```
{
  scores: {
    alignment: 0.7,      // Partially addresses early detection goal
    plausibility: 0.5,   // Theoretical basis needs development
    novelty: 0.9,        // Highly innovative approach
    testability: 0.4,    // Requires significant development
    safety: 0.8          // Low risk for diagnostic tool
  },
  overall: 0.66,
  recommendation: "revise",
  feedback: [
    "Strengthen theoretical foundation",
    "Add intermediate validation milestones",
    "Consider partnering with quantum tech lab"
  ]
}
```

## Behavioral Contracts

The validation system MUST:
- Complete initial screening within 60 seconds
- Provide specific, actionable feedback
- Maintain consistent scoring across sessions
- Escalate ambiguous cases to experts
- Track all validation decisions

The validation system MUST NOT:
- Accept hypotheses with safety scores below 0.7
- Skip required validation steps
- Override expert safety vetoes
- Lower standards without authorization
- Leak proprietary research information

The validation system SHOULD:
- Progressively refine criteria based on outcomes
- Batch similar validations for efficiency
- Cache literature search results
- Provide confidence intervals for scores
- Learn from expert override patterns