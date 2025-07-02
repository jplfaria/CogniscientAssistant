# Reflection Agent Specification

**Type**: Core Research Agent  
**Interactions**: Supervisor Agent, Context Memory, Web Search, Generation Agent, Ranking Agent, Meta-review Agent

## Prerequisites
- Read: 001-system-overview.md
- Read: 004-multi-agent-architecture.md  
- Read: 005-supervisor-agent.md
- Read: 007-generation-agent.md
- Understand: Scientific peer review principles and practices

## Overview

The Reflection Agent simulates the role of a scientific peer reviewer within the AI Co-Scientist system. It critically examines hypotheses for correctness, quality, novelty, and safety through six distinct review types. The agent evaluates whether hypotheses provide improved explanations for existing research observations and identifies potential failure scenarios.

## Core Behaviors

### 1. Multi-Type Review System

The Reflection Agent MUST implement six distinct review types, each serving a specific evaluation purpose:

#### Initial Review (Resource-Efficient Filter)
- Assess correctness, quality, novelty, and preliminary safety WITHOUT external tools
- Quickly discard flawed, non-novel, or unsuitable hypotheses
- Provide rapid feedback to prevent resource waste on poor candidates
- Make binary decision: proceed to full review or reject

#### Full Review (Comprehensive Evaluation)
- Leverage web search and external tools for grounding
- Evaluate correctness, quality, and novelty against current literature
- Scrutinize underlying assumptions and reasoning chains
- Identify known vs. novel aspects of the hypothesis
- Produce detailed assessment with literature citations

#### Deep Verification Review (Assumption Analysis)
- Decompose hypothesis into constituent assumptions
- Break down each assumption into fundamental sub-assumptions
- Independently evaluate each sub-assumption for validity
- Identify which errors are fundamental vs. peripheral
- Use probing questions to expose logical flaws

#### Observation Review (Explanatory Power)
- Assess whether hypothesis explains existing experimental observations
- Focus on long-tail or under-explained phenomena from prior research
- Compare explanatory power against existing theories
- Summarize observations that support or contradict the hypothesis

#### Simulation Review (Mechanism Validation)
- Simulate the proposed mechanism or experimental protocol step-by-step
- Identify potential failure points in the causal chain
- Predict experimental outcomes based on the hypothesis
- Flag practical implementation challenges

#### Tournament Review (Adaptive Refinement)
- Analyze patterns from previous reviews and tournament results
- Identify recurring issues in hypothesis evaluation
- Adapt review criteria based on system learning
- Refine evaluation strategies for improved accuracy

### 2. Evaluation Criteria Application

The Reflection Agent MUST consistently apply these criteria across all review types:
- **Correctness**: Scientific accuracy and logical consistency
- **Quality**: Rigor, completeness, and clarity of presentation
- **Novelty**: Genuine advancement beyond existing knowledge
- **Safety**: Ethical considerations and potential risks
- **Feasibility**: Practical viability of proposed experiments

## Inputs

### Primary Input: Review Task
```
{
  "task_id": "unique identifier",
  "review_type": "initial|full|deep_verification|observation|simulation|tournament",
  "hypothesis": {
    "hypothesis_id": "from Generation Agent",
    "summary": "concise statement",
    "full_description": "detailed explanation",
    "experimental_protocol": "proposed experiments",
    "supporting_evidence": ["citations"],
    "assumptions": ["stated assumptions"],
    "category": "therapeutic|mechanistic|diagnostic|other"
  },
  "review_config": {
    "time_limit": "seconds",
    "tool_access": "boolean (false for initial review)",
    "focus_criteria": ["specific aspects to emphasize"],
    "prior_reviews": ["previous review results if applicable"]
  },
  "context": {
    "research_goal": "original research objective",
    "domain_knowledge": "relevant background information",
    "safety_constraints": ["ethical and safety guidelines"]
  }
}
```

### Secondary Input: System Knowledge Access
- Tournament results and patterns from Ranking Agent
- Meta-review synthesis from previous cycles
- Context Memory for historical review patterns
- Expert scientist feedback when available

## Outputs

### Primary Output: Review Result
```
{
  "task_id": "matching input task_id",
  "hypothesis_id": "reviewed hypothesis identifier",
  "review_type": "type of review performed",
  "decision": "accept|reject|revise",
  "scores": {
    "correctness": "0.0-1.0",
    "quality": "0.0-1.0", 
    "novelty": "0.0-1.0",
    "safety": "0.0-1.0",
    "feasibility": "0.0-1.0"
  },
  "detailed_feedback": {
    "strengths": ["positive aspects identified"],
    "weaknesses": ["issues and concerns"],
    "assumptions_analysis": {
      "valid": ["supported assumptions"],
      "questionable": ["assumptions needing evidence"],
      "invalid": ["incorrect assumptions"]
    },
    "novelty_assessment": {
      "novel_aspects": ["genuinely new contributions"],
      "known_aspects": ["existing knowledge"],
      "literature_gaps": ["unexplored areas addressed"]
    }
  },
  "recommendations": {
    "improvements": ["suggested modifications"],
    "additional_experiments": ["validation needs"],
    "safety_considerations": ["ethical concerns to address"]
  },
  "supporting_evidence": [
    {
      "source": "paper DOI or reference",
      "relevance": "how it supports/contradicts hypothesis"
    }
  ],
  "review_metadata": {
    "review_duration": "seconds",
    "tools_used": ["web_search", "literature_db"],
    "confidence_level": "high|medium|low"
  }
}
```

### Review-Type Specific Outputs

#### For Deep Verification Review
```
{
  "assumption_tree": {
    "root_assumption": "main hypothesis claim",
    "decomposition": [
      {
        "assumption": "sub-assumption",
        "validity": "valid|questionable|invalid",
        "evidence": "supporting or refuting evidence",
        "criticality": "fundamental|peripheral"
      }
    ]
  }
}
```

#### For Simulation Review
```
{
  "simulation_results": {
    "mechanism_steps": ["ordered causal chain"],
    "failure_points": [
      {
        "step": "where failure could occur",
        "probability": "likelihood estimate",
        "impact": "consequence if it fails"
      }
    ],
    "predicted_outcomes": ["expected experimental results"]
  }
}
```

## Behavioral Contracts

### Review Quality Standards

The Reflection Agent MUST:
- Complete initial reviews within 60 seconds without external tools
- Provide actionable feedback that improves hypothesis quality
- Maintain consistency in evaluation criteria across reviews
- Avoid bias toward conservative or radical hypotheses
- Document reasoning for all scores and decisions

### Tool Usage Protocols

The Reflection Agent MUST:
- Use NO external tools during initial reviews
- Efficiently query literature databases during full reviews
- Limit web searches to relevant scientific sources
- Cache search results to avoid redundant queries
- Prioritize recent publications and high-impact journals

### Adaptive Learning

The Reflection Agent MUST:
- Incorporate patterns identified by Meta-review Agent
- Adjust evaluation stringency based on tournament outcomes
- Learn from expert scientist corrections
- Refine detection of subtle flaws over time
- Balance thoroughness with computational efficiency

## Interaction Protocols

### With Supervisor Agent
1. Receive review task assignments with priority levels
2. Report completion status and basic metrics
3. Request additional resources for complex reviews
4. Signal when review backlogs develop

### With Context Memory
1. Store all review results with full provenance
2. Query historical reviews for similar hypotheses
3. Access accumulated domain knowledge
4. Update pattern database for future reference

### With Web Search Tool
1. Formulate precise queries for hypothesis validation
2. Request specific papers by DOI when cited
3. Search for contradicting evidence systematically
4. Verify experimental feasibility through literature

### With Meta-review Agent
1. Provide detailed review results for pattern analysis
2. Receive synthesized feedback on review quality
3. Implement suggested improvements in review strategy
4. Report on effectiveness of new review approaches

## Examples

### Example 1: Initial Review of AML Drug Repurposing
**Input**: Hypothesis suggesting KIRA6 for AML treatment

**Review Process**:
- Check logical consistency of ER stress targeting
- Assess whether mechanism is plausible without literature search
- Evaluate if experimental protocol is reasonable
- Make quick decision on proceeding to full review

**Output**: Accept for full review (scores: correctness=0.8, quality=0.7, novelty=0.6)

### Example 2: Deep Verification of Biofilm Resistance
**Input**: Hypothesis about metabolic heterogeneity creating persister niches

**Review Process**:
- Decompose into assumptions about metabolism, spatial gradients, dormancy
- Evaluate each assumption independently
- Identify that dormancy-resistance link is well-established
- Find that metabolic gradient assumption needs more evidence

**Output**: Revise recommendation with specific assumption clarifications needed

### Example 3: Simulation Review of NET-Fibrosis Mechanism
**Input**: Hypothesis linking neutrophil extracellular traps to liver fibrosis

**Review Process**:
- Simulate: NET formation → TLR activation → stellate cell response
- Identify failure point: TLR expression levels on stellate cells
- Predict experimental outcomes for TLR blocking studies
- Flag need for dose-response validation

**Output**: Accept with detailed experimental guidance and failure scenarios

## State Transitions

The Reflection Agent transitions through these states:
1. **Idle** - Awaiting review assignment
2. **Analyzing** - Processing hypothesis and preparing review
3. **Researching** - Conducting literature search (full review only)
4. **Evaluating** - Scoring and generating feedback
5. **Finalizing** - Compiling results and recommendations

## Error Handling

The Reflection Agent MUST handle:
- Malformed hypothesis inputs: Request clarification or make best effort
- Web search failures: Continue with cached knowledge, note limitation
- Time limit exceeded: Submit partial review with completed sections
- Conflicting evidence: Present both sides, indicate uncertainty
- Tool unavailability: Adapt review type or defer to later attempt

## Performance Characteristics

Expected behavior under normal conditions:
- Initial review: 30-60 seconds per hypothesis
- Full review: 3-5 minutes with literature search
- Deep verification: 5-10 minutes depending on complexity
- Simulation review: 2-4 minutes for mechanism modeling
- Process 50-100 reviews per session across types
- Maintain >90% consistency in repeated evaluations