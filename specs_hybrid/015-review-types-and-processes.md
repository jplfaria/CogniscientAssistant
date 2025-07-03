# Review Types and Processes Specification

**Type**: Process Specification  
**Components**: Reflection Agent, Supervisor Agent, Context Memory, Web Search Tools

## Prerequisites
- Read: Reflection Agent Specification
- Read: Multi-Agent Framework Specification
- Read: Context Memory System Specification
- Understand: Tournament and Elo Rating System concepts

## Purpose

This specification defines the six distinct review types and their execution processes within the AI Co-Scientist system. These review types enable comprehensive evaluation of scientific hypotheses through varying depths of analysis, ensuring scientific rigor, novelty, and safety.

## Review Type Definitions

### Initial Review

**Purpose**: Rapid preliminary evaluation without external tool usage

**Behavior**:
- Evaluates logical consistency and hypothesis structure
- Assesses basic scientific validity
- Identifies obvious methodological flaws
- Provides quick accept/reject recommendation
- Performs preliminary safety screening

**Constraints**:
- Time limit: < 30 seconds per hypothesis
- No external tool usage permitted
- Relies solely on internal knowledge

### Full Review

**Purpose**: Comprehensive evaluation with literature grounding

**Behavior**:
- Conducts extensive literature searches via web tools
- Verifies novelty claims against existing research
- Validates methodological soundness with citations
- Assesses experimental feasibility
- Provides detailed improvement suggestions
- Performs thorough safety and ethics evaluation

**Tool Usage**:
- Web search for relevant papers
- Literature database queries
- Citation verification

### Deep Verification Review

**Purpose**: Rigorous assumption decomposition and validation

**Behavior**:
- Decomposes hypothesis into constituent assumptions
- Recursively breaks down assumptions into sub-assumptions
- Decontextualizes and independently evaluates each assumption
- Identifies invalidating elements
- Distinguishes fundamental from correctable errors
- Assesses impact of invalid assumptions on overall hypothesis

**Analysis Depth**:
- Minimum 2 levels of assumption decomposition
- Individual assumption validation
- Error criticality assessment

### Observation Review

**Purpose**: Evaluate explanatory power for existing phenomena

**Behavior**:
- Searches for relevant experimental observations in literature
- Determines if hypothesis explains existing findings
- Compares explanatory power to existing theories
- Tests alignment with known scientific phenomena
- Summarizes explained observations

**Completion Criteria**:
- May complete without findings if no relevant observations exist
- Positive observations appended to hypothesis documentation

### Simulation Review

**Purpose**: Test predictions through mental simulation

**Behavior**:
- Simulates hypothesis mechanisms step-by-step
- Models proposed experimental procedures
- Identifies potential failure scenarios
- Tests edge cases and boundary conditions
- Predicts experimental outcomes
- Highlights implementation challenges

**Simulation Scope**:
- Mechanism of action pathways
- Experimental protocol execution
- Expected vs. potential outcomes

### Tournament/Recurrent Review

**Purpose**: Adaptive review based on accumulated system knowledge

**Behavior**:
- Analyzes patterns from prior reviews
- Studies tournament debate outcomes
- Identifies recurring hypothesis weaknesses
- Refines evaluation criteria dynamically
- Provides meta-insights for system improvement

**Adaptation Sources**:
- Previous review outcomes
- Tournament ranking patterns
- Meta-review feedback
- Hypothesis evolution trajectories

## Review Process Execution

### Review Request Interface

```
ReviewRequest {
  hypothesis_id: string
  review_type: ReviewType
  priority: Priority
  deadline: timestamp (optional)
  context: {
    prior_reviews: list[ReviewId] (optional)
    related_hypotheses: list[HypothesisId] (optional)
    specific_concerns: list[string] (optional)
  }
}
```

### Review Output Format

```
ReviewResult {
  review_id: string
  hypothesis_id: string
  review_type: ReviewType
  timestamp: timestamp
  
  evaluation: {
    correctness_score: float (0.0-1.0)
    quality_score: float (0.0-1.0)
    novelty_score: float (0.0-1.0)
    safety_score: float (0.0-1.0)
    overall_recommendation: Recommendation
  }
  
  findings: {
    strengths: list[string]
    weaknesses: list[string]
    suggestions: list[string]
    critical_issues: list[string] (optional)
  }
  
  evidence: {
    citations: list[Citation] (for Full Review)
    assumptions: AssumptionTree (for Deep Verification)
    observations: list[Observation] (for Observation Review)
    simulations: list[SimulationResult] (for Simulation Review)
    patterns: list[Pattern] (for Tournament Review)
  }
  
  metadata: {
    execution_time: duration
    tools_used: list[string]
    confidence: float (0.0-1.0)
  }
}
```

## Review Quality Assurance

### Evaluation Criteria

**Primary Dimensions**:
1. **Correctness**: Logical consistency, scientific accuracy, valid reasoning
2. **Quality**: Clarity, completeness, methodological rigor
3. **Novelty**: Advancement over prior work, unique insights
4. **Safety**: Ethical considerations, dual-use potential, harm assessment

**Secondary Dimensions**:
5. **Feasibility**: Resource requirements, technical prerequisites
6. **Impact**: Scientific contribution, practical applications

### Review Calibration

**Consistency Mechanisms**:
- Cross-review validation for critical hypotheses
- Meta-review pattern analysis
- Human expert benchmark comparisons
- Scoring distribution monitoring

**Adaptive Improvements**:
- Criteria weight adjustment based on feedback
- Review type selection optimization
- Evidence requirement refinement

## Process Orchestration

### Review Assignment Logic

**Priority Factors**:
1. Hypothesis ranking score
2. Review coverage gaps
3. Time since last review
4. Tournament participation status
5. Safety flag presence

**Assignment Rules**:
- Initial Review required before other types
- Full Review follows positive Initial Review
- Deep Verification for high-stakes hypotheses
- Observation/Simulation for mechanism-focused hypotheses
- Tournament Review after ranking competitions

### Review Pipeline States

```
ReviewState {
  PENDING: Awaiting assignment
  ASSIGNED: Worker processing
  IN_PROGRESS: Review execution
  COMPLETED: Results available
  FAILED: Error occurred
  CANCELLED: Review terminated
}
```

### Error Handling

**Retry Conditions**:
- Tool access failures: Retry with backoff
- Time limit exceeded: Downgrade to simpler review
- Invalid hypothesis format: Return error to supervisor

**Failure Reporting**:
- Error type classification
- Partial result preservation
- Alternative review suggestion

## Integration Points

### With Generation Agent
- Review feedback influences generation parameters
- Common failure patterns guide constraint setting
- Novelty assessments inform exploration strategies

### With Ranking Agent
- Review scores contribute to tournament seeding
- Detailed findings support debate arguments
- Quality metrics influence Elo calculations

### With Evolution Agent
- Weakness identification drives improvement focus
- Suggestions become evolution objectives
- Review history guides variation strategies

### With Meta-review Agent
- All reviews analyzed for systemic patterns
- Feedback loops identified and communicated
- Review effectiveness metrics calculated

### With Context Memory
- Review results persistently stored
- Cross-hypothesis patterns tracked
- Historical review data accessible

## Performance Requirements

### Timing Constraints
- Initial Review: < 30 seconds
- Full Review: < 5 minutes
- Deep Verification: < 10 minutes
- Observation Review: < 5 minutes
- Simulation Review: < 5 minutes
- Tournament Review: < 3 minutes

### Quality Metrics
- Inter-review consistency: > 85%
- Citation accuracy: > 95%
- Assumption identification completeness: > 90%
- Safety issue detection rate: > 99%

## Natural Language Examples

### Initial Review Request
"Perform a quick initial review of hypothesis H-2024-001 focusing on logical consistency and basic feasibility."

### Full Review with Specific Focus
"Conduct a full literature-grounded review of the cancer metabolism hypothesis, with special attention to existing GLUT1 inhibitor research."

### Deep Verification for Critical Hypothesis
"Execute deep verification review on the blood-brain barrier penetration hypothesis, decomposing all pharmacokinetic assumptions."

### Observation Review Query
"Check if this antibiotic resistance hypothesis explains the recent cf-PICI observations in clinical isolates."

### Simulation Review Scenario
"Simulate the proposed CRISPR screening protocol to identify potential technical challenges and failure modes."

### Tournament Review Analysis
"Analyze review patterns from the last tournament round to identify why metabolism-focused hypotheses consistently scored lower."