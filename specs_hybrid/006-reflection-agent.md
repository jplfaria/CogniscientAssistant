# Reflection Agent Specification

**Type**: Agent  
**Interactions**: Supervisor Agent, Context Memory, Web Search Tools, Meta-review Agent

## Prerequisites
- Read: System Overview and Architecture Specification
- Read: Multi-Agent Framework Specification
- Read: Context Memory System Specification
- Read: Generation Agent Specification

## Purpose

The Reflection Agent serves as the primary quality control mechanism in the AI Co-Scientist system, evaluating generated hypotheses through multiple review strategies. It functions as an AI-powered scientific peer reviewer, providing detailed critiques, identifying flaws, and suggesting improvements across various evaluation dimensions.

## Agent Behavior

The Reflection Agent exhibits the following behaviors:

1. **Multi-Strategy Review Execution**: Performs six distinct types of reviews with different depths and focuses
2. **Literature-Grounded Evaluation**: Searches and analyzes scientific literature to verify claims
3. **Safety and Ethics Assessment**: Evaluates hypotheses for potential harmful applications
4. **Constructive Critique Generation**: Provides actionable feedback for hypothesis improvement
5. **Adaptive Review Criteria**: Adjusts evaluation stringency based on meta-review feedback
6. **Review History Tracking**: Maintains review patterns for learning and optimization

## Inputs

### From Task Assignment
```
ReviewTask {
  hypothesis_id: string
  review_type: ReviewType
  review_parameters: dict
  priority: int
  context: dict (optional)
}
```

### From Context Memory
```
HypothesisData {
  hypothesis: Hypothesis
  prior_reviews: list[Review] (if any)
  related_hypotheses: list[Hypothesis] (optional)
  tournament_history: list[TournamentResult] (optional)
}
```

### From Meta-review Agent
```
ReviewerFeedback {
  common_oversights: list[string]
  criteria_adjustments: dict[Criterion, float]
  false_positive_patterns: list[string]
  false_negative_patterns: list[string]
}
```

## Outputs

### Review Structure
```
Review {
  id: string
  hypothesis_id: string
  review_type: ReviewType
  overall_score: float (0.0 - 1.0)
  criteria_scores: dict[Criterion, Score]
  critiques: list[Critique]
  suggestions: list[Suggestion]
  grounding_evidence: list[Evidence]
  recommendation: Accept | Revise | Reject
  confidence: float (0.0 - 1.0)
  timestamp: datetime
}
```

### Critique Structure
```
Critique {
  criterion: Criterion
  severity: High | Medium | Low
  description: string
  specific_issues: list[string]
  evidence: list[Citation] (optional)
}
```

### Suggestion Structure
```
Suggestion {
  type: Improvement | Alternative | Extension
  description: string
  implementation_notes: string
  expected_impact: string
}
```

## Review Types

### 1. Initial Review

**Purpose**: Fast, preliminary evaluation without external tools

**Behavior**:
- Evaluates logical consistency
- Checks hypothesis completeness
- Assesses basic feasibility
- Identifies obvious flaws
- Provides quick accept/reject decision

**Criteria Focus**:
- Internal coherence
- Completeness of protocol
- Basic scientific validity
- Clear testable predictions

**Time Constraint**: < 30 seconds per hypothesis

### 2. Full Review

**Purpose**: Comprehensive evaluation with literature grounding

**Behavior**:
- Performs extensive literature search
- Verifies novelty claims
- Validates methodological soundness
- Checks experimental feasibility
- Provides detailed improvement suggestions

**Process**:
1. Extract key claims from hypothesis
2. Search for related work
3. Compare with existing literature
4. Evaluate novelty and contribution
5. Assess methodology rigor
6. Generate comprehensive feedback

**Tool Usage**:
- Multiple targeted literature searches
- Cross-reference with citation databases
- Verify experimental precedents

### 3. Deep Verification Review

**Purpose**: Rigorous assumption decomposition and validation

**Behavior**:
- Decomposes hypothesis into atomic assumptions
- Categorizes assumptions as fundamental vs. correctable
- Tests logical consistency of assumption chains
- Identifies critical vulnerabilities
- Suggests targeted experiments for validation

**Assumption Analysis**:
```
AssumptionReview {
  assumption: Assumption
  classification: Fundamental | Correctable | Auxiliary
  evidence_status: Supported | Contested | Unknown
  validation_approach: string
  risk_assessment: High | Medium | Low
}
```

### 4. Observation Review

**Purpose**: Evaluate alignment with existing experimental data

**Behavior**:
- Searches for relevant experimental observations
- Tests if hypothesis explains known phenomena
- Identifies contradictions with established data
- Evaluates predictive consistency
- Suggests observational tests

**Evaluation Criteria**:
- Explanatory power
- Consistency with data
- Predictive accuracy
- Scope of applicability

### 5. Simulation Review

**Purpose**: Mental model testing of hypothesis predictions

**Behavior**:
- Simulates experimental outcomes using LLM reasoning
- Tests edge cases and boundary conditions
- Evaluates robustness of predictions
- Identifies potential experimental challenges
- Estimates success probability

**Simulation Aspects**:
- Expected vs. unexpected outcomes
- Failure mode analysis
- Resource requirement estimation
- Timeline feasibility

### 6. Tournament/Recurrent Review

**Purpose**: Comparative evaluation against competing hypotheses

**Behavior**:
- Reviews hypothesis in context of alternatives
- Identifies unique advantages
- Evaluates relative strengths/weaknesses
- Considers portfolio diversity
- Provides ranking rationale

**Comparison Dimensions**:
- Scientific merit
- Experimental tractability
- Potential impact
- Resource efficiency
- Risk/reward balance

## Evaluation Criteria

### Primary Criteria

1. **Correctness**
   - Logical consistency
   - Scientific accuracy
   - Methodological validity
   - Statistical soundness

2. **Quality**
   - Clarity of presentation
   - Completeness of protocol
   - Experimental design rigor
   - Expected outcome specificity

3. **Novelty**
   - Advancement over existing work
   - Unique insights or approaches
   - Non-obvious connections
   - Potential for breakthrough

4. **Safety**
   - Ethical considerations
   - Potential for harm
   - Dual-use concerns
   - Responsible research practices

### Secondary Criteria

5. **Feasibility**
   - Resource requirements
   - Technical prerequisites
   - Timeline realism
   - Success probability

6. **Impact**
   - Scientific contribution
   - Practical applications
   - Field advancement potential
   - Societal benefit

## Tool Integration

### Literature Search Protocol
```
LiteratureSearch {
  primary_query: string
  variant_queries: list[string]
  date_range: string (optional)
  venue_filter: list[string] (optional)
  citation_threshold: int (optional)
}
```

### Evidence Collection
- Extract supporting citations
- Identify contradicting studies
- Assess evidence quality
- Track citation networks

### Claim Verification
- Cross-reference with databases
- Check experimental reproducibility
- Verify statistical claims
- Validate measurement methods

## State Management

### Read Operations
- Access hypothesis for review
- Retrieve prior review history
- Query related hypotheses for context
- Access reviewer feedback from Meta-review

### Write Operations
- Store complete review with all scores
- Update review statistics
- Log search queries and results
- Record evidence trails

## Adaptive Behavior

### Learning from Meta-review
1. **Criteria Weight Adjustment**
   - Increase weight for commonly missed issues
   - Decrease weight for over-emphasized aspects
   - Balance based on downstream success

2. **Pattern Recognition**
   - Identify review blind spots
   - Recognize hypothesis types requiring special attention
   - Adapt to domain-specific requirements

3. **Calibration Updates**
   - Adjust acceptance thresholds
   - Modify scoring distributions
   - Align with human expert standards

### Review Strategy Selection
- Choose review type based on:
  - Hypothesis characteristics
  - Prior review results
  - System objectives
  - Resource availability

## Quality Assurance

### Internal Consistency Checks
- Ensure scores align with recommendations
- Verify evidence supports critiques
- Check suggestion feasibility
- Validate citation accuracy

### Review Completeness
- All criteria addressed
- Sufficient evidence provided
- Clear actionable feedback
- Balanced assessment

## Error Handling

### Common Scenarios

1. **Literature Search Failures**
   - Use cached results if available
   - Proceed with limited grounding
   - Note evidence limitations
   - Adjust confidence accordingly

2. **Conflicting Evidence**
   - Present both perspectives
   - Weigh evidence quality
   - Suggest resolution approaches
   - Flag for expert review

3. **Ambiguous Hypotheses**
   - Request clarification points
   - Review under multiple interpretations
   - Highlight ambiguities in critique
   - Suggest specification improvements

4. **Resource Constraints**
   - Prioritize critical evaluations
   - Use lighter review variants
   - Queue for later deep review
   - Signal resource needs

## Integration Patterns

### With Supervisor Agent
- Receive review assignments
- Report completion and scores
- Request additional time for complex reviews
- Signal high-priority findings

### With Generation Agent
- Influence through review patterns
- Provide improvement templates
- Share common failure modes
- Guide generation strategies

### With Ranking Agent
- Provide normalized scores
- Share comparative insights
- Highlight distinguishing features
- Support ranking decisions

## Performance Metrics

The Reflection Agent's effectiveness is measured by:

1. **Review Accuracy**: Correlation with human expert reviews
2. **Prediction Success**: Downstream hypothesis performance
3. **Feedback Quality**: Actionability of suggestions
4. **Grounding Precision**: Citation relevance and accuracy
5. **Processing Efficiency**: Reviews per time unit
6. **False Positive/Negative Rates**: Calibration accuracy

## Configuration Parameters

```
ReflectionConfig {
  review_time_limits: dict[ReviewType, int]
  score_thresholds: dict[Criterion, float]
  evidence_requirements: dict[ReviewType, int]
  search_depth: int (default: 20)
  confidence_threshold: float (default: 0.7)
  enable_review_types: list[ReviewType]
  adaptation_rate: float (default: 0.1)
}
```

## Examples

### Initial Review Example
```
Input: Hypothesis about novel cancer immunotherapy
Review Time: 25 seconds
Result: "Reject - Logical flaw in mechanism"
- Missing: How therapy crosses blood-brain barrier
- Inconsistent: Claims about T-cell activation
- Incomplete: No control group in protocol
```

### Full Review Example
```
Input: Hypothesis about bacterial communication
Review Time: 5 minutes
Result: "Accept with Major Revisions"
- Novel: No prior work on this specific mechanism
- Grounded: 15 supporting citations found
- Concerns: Similar approach failed in 2019 study
- Suggestions: Modify protocol to address pH sensitivity
```

## Boundaries

**What the Reflection Agent Does**:
- Evaluates hypotheses across multiple dimensions
- Provides detailed, actionable feedback
- Grounds assessments in scientific literature
- Adapts evaluation strategies based on context
- Maintains consistent quality standards

**What the Reflection Agent Does Not Do**:
- Generate new hypotheses (Generation Agent's role)
- Modify existing hypotheses (Evolution Agent's role)
- Make final selection decisions (Ranking Agent's role)
- Synthesize cross-hypothesis insights (Meta-review Agent's role)
- Execute experiments (External validation)