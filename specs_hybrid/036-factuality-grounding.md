# Factuality and Grounding Specification

**Type**: System-wide Process  
**Components**: All Agents, Tool Integration System, Context Memory, Safety Mechanisms

## Prerequisites
- Read: Generation Agent Specification
- Read: Reflection Agent Specification
- Read: Tool Integration Specification
- Read: Safety Mechanisms Specification
- Read: Evaluation Metrics Specification

## Purpose
This specification defines how the AI Co-Scientist system ensures factual accuracy and grounds its scientific hypotheses in existing literature and empirical evidence. It establishes behavioral requirements for preventing hallucinations, verifying claims, and maintaining scientific rigor throughout the hypothesis generation and evolution process.

## Core Behaviors

### Literature Grounding Process
The system MUST ground all scientific hypotheses in existing literature through:

1. **Iterative Literature Search**
   - Execute web searches for relevant scientific literature
   - Retrieve and analyze research articles, reviews, and datasets
   - Extract key findings, methodologies, and limitations
   - Identify gaps in current knowledge

2. **Citation Integration**
   - Attach relevant citations to each hypothesis component
   - Provide reasoning for how citations support claims
   - Distinguish between direct support and analogous evidence
   - Flag areas where literature support is limited or contradictory

3. **Knowledge Synthesis**
   - Summarize the state of prior work before generating novel ideas
   - Identify convergent and divergent findings across sources
   - Acknowledge limitations of available literature
   - Note when relying on open-access vs. paywalled sources

### Multi-Layer Verification Framework

The system MUST verify factuality through multiple independent mechanisms:

1. **Assumption Decomposition**
   - Break hypotheses into constituent assumptions
   - Decompose assumptions into fundamental sub-assumptions
   - Independently evaluate each sub-assumption for correctness
   - Track the dependency chain between assumptions

2. **Cross-Reference Validation**
   - Compare generated content against multiple sources
   - Identify potential contradictions with established knowledge
   - Explicitly state and justify any apparent contradictions
   - Flag claims that cannot be independently verified

3. **Plausibility Assessment**
   - Evaluate biological/chemical/physical plausibility
   - Check consistency with known mechanisms
   - Assess feasibility of proposed experiments
   - Identify potential confounding factors

## Grounding Requirements

### Input Sources
```
GroundingInput {
  hypothesis_content: string        // The hypothesis to be grounded
  research_context: ResearchGoal    // Domain and constraints
  prior_knowledge: List[Citation]   // Previously identified sources
  verification_depth: enum {
    BASIC,      // Quick literature check
    STANDARD,   // Normal grounding process
    DEEP        // Exhaustive verification
  }
}
```

### Output Format
```
GroundedHypothesis {
  hypothesis: {
    content: string
    confidence_score: float (0.0-1.0)
    factuality_assessment: {
      well_supported: List[Claim]      // Claims with strong evidence
      partially_supported: List[Claim]  // Claims with some evidence
      speculative: List[Claim]          // Novel but plausible claims
      contradictory: List[Claim]        // Claims that conflict with literature
    }
  }
  grounding_evidence: {
    primary_sources: List[Citation]    // Direct supporting literature
    analogous_evidence: List[Citation] // Related findings from other domains
    contradictory_evidence: List[Citation] // Conflicting findings
    knowledge_gaps: List[string]       // Areas lacking literature
  }
  verification_notes: {
    search_queries_used: List[string]
    sources_examined: int
    access_limitations: List[string]   // e.g., "paywalled articles"
    verification_timestamp: datetime
  }
}
```

## Behavioral Contracts

### Factuality Thresholds
The system MUST:
- Reject hypotheses with confidence_score < 0.3
- Flag hypotheses with 0.3 <= confidence_score < 0.6 for additional review
- Require explicit justification for speculative claims
- Never present ungrounded claims as established facts

### Literature Search Requirements
The system MUST:
- Execute at least 3 distinct search queries per hypothesis
- Examine at least 10 relevant sources when available
- Include both recent (< 2 years) and foundational literature
- Document when relevant literature is inaccessible

### Transparency Requirements
The system MUST:
- Clearly distinguish between established facts and speculation
- Provide traceable citations for all factual claims
- Acknowledge uncertainties and knowledge limitations
- Document the grounding process for audit purposes

## Integration with Other Components

### Generation Agent Integration
- Receives grounding requirements with hypothesis generation requests
- Incorporates literature findings during ideation
- Adjusts creativity based on factuality constraints

### Reflection Agent Integration  
- Applies grounding verification during all review types
- Flags insufficiently grounded hypotheses
- Suggests additional literature searches when needed

### Meta-review Agent Integration
- Identifies patterns in grounding failures
- Recommends improvements to search strategies
- Tracks coverage of literature domains

### Safety Mechanisms Integration
- Prevents generation of dangerous ungrounded claims
- Flags hypotheses that could mislead if factuality is uncertain
- Enforces stricter grounding for high-risk domains

## Performance Requirements

### Grounding Completeness
- 95% of factual claims must have traceable citations
- 100% of safety-critical claims must be verified
- 90% of hypotheses must achieve confidence_score >= 0.6

### Verification Speed
- Basic grounding: < 30 seconds
- Standard grounding: < 2 minutes  
- Deep verification: < 10 minutes

### Literature Coverage
- Access at least 3 different scientific databases/sources
- Include preprints when peer-reviewed sources are limited
- Document access limitations for transparency

## Error Handling

### Common Failure Modes
1. **Insufficient Literature**: Document knowledge gaps, proceed with appropriate caveats
2. **Contradictory Evidence**: Present all viewpoints, note controversies
3. **Access Limitations**: Use available sources, note potential biases
4. **Timeout Issues**: Return partial results with completion status

### Fallback Strategies
- Use analogous evidence from related domains
- Leverage meta-analyses and reviews when primary sources are unavailable
- Apply first-principles reasoning with explicit assumptions
- Request human expert input for critical uncertainties

## Configuration Parameters

```
GroundingConfig {
  min_sources_required: int = 10
  min_search_queries: int = 3  
  confidence_threshold: float = 0.6
  max_search_time_seconds: int = 120
  require_peer_reviewed: bool = false
  allow_preprints: bool = true
  include_patents: bool = true
  languages: List[string] = ["en"]
}
```

## Natural Language Examples

### Example 1: Well-Grounded Hypothesis
**Input**: "Generate hypothesis for treating liver fibrosis"

**Output**: 
"Hypothesis: Inhibition of LOXL2 enzyme activity reduces collagen cross-linking and fibrosis progression in liver tissue.

Grounding: This hypothesis is supported by:
- Chen et al. (2023) demonstrated LOXL2 upregulation in fibrotic liver tissue
- Rodriguez et al. (2022) showed LOXL2 inhibition reduced fibrosis in mouse models  
- Phase 2 trial (NCT01452308) of simtuzumab showed safety but limited efficacy

Confidence: 0.75 - Strong mechanistic support, but clinical translation remains uncertain."

### Example 2: Speculative but Plausible Hypothesis
**Input**: "Novel approach for Alzheimer's treatment"

**Output**:
"Hypothesis: Targeted ultrasound-mediated opening of blood-brain barrier enables clearance of tau aggregates through glymphatic activation.

Grounding: This speculative hypothesis combines:
- Established: BBB can be opened with focused ultrasound (Lipsman et al., 2018)
- Established: Glymphatic system clears brain waste (Iliff et al., 2012)
- Speculative: Combined approach might clear tau (no direct evidence)

Confidence: 0.45 - Individual components proven, but combination untested. Requires careful safety evaluation."

## Limitations and Considerations

The system acknowledges inherent limitations:
- Cannot access all scientific literature (paywall constraints)
- May miss non-English language research
- Recent findings may not be indexed yet
- Cannot verify unpublished or proprietary data
- Inherited biases from training data and search algorithms

Human expert validation remains essential for:
- Interpreting contradictory evidence
- Assessing clinical/practical feasibility
- Identifying missing contextual factors
- Validating novel mechanism proposals