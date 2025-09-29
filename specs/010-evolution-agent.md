# Evolution Agent Specification

**Type**: Agent  
**Interactions**: Supervisor Agent, Ranking Agent, Meta-review Agent, Context Memory, Web Search Interface

## Prerequisites
- Read: 009-ranking-agent.md - Tournament system and Elo ratings
- Read: 012-meta-review-agent.md - Feedback synthesis (when available)
- Understand: Hypothesis structure and tournament dynamics

## Overview

The Evolution Agent continuously refines and improves top-ranked hypotheses through various evolutionary strategies. It creates new hypothesis variants that must compete in tournaments, enabling the system to iteratively improve research quality through natural selection of ideas.

## Core Behaviors

### Evolution Strategies

The Evolution Agent MUST implement four primary evolution strategies:

1. **Enhancement**
   - Identify weaknesses in existing hypotheses
   - Search literature for supporting evidence
   - Improve coherence, practicality, and feasibility
   - Address invalid assumptions and reasoning gaps

2. **Combination**
   - Merge best aspects of multiple top-ranked hypotheses
   - Create synthetic hypotheses that integrate complementary ideas
   - Preserve strengths while mitigating weaknesses

3. **Simplification**
   - Reduce hypothesis complexity for easier testing
   - Extract core insights from complex proposals
   - Improve clarity without losing essential content

4. **Out-of-Box Thinking**
   - Generate divergent variations of existing hypotheses
   - Apply analogical reasoning from other domains
   - Explore unconventional approaches inspired by top performers

### Hypothesis Protection

The Evolution Agent MUST:
- Create NEW hypothesis instances rather than modifying existing ones
- Preserve the integrity of tournament-validated hypotheses
- Ensure all evolved hypotheses compete for ranking

## Inputs

```yaml
evolution_task:
  task_id: string
  strategy: enum[enhancement, combination, simplification, out_of_box]
  source_hypotheses:
    - hypothesis_id: string
      elo_rating: number
      tournament_wins: number
      tournament_losses: number
      content:
        summary: string
        full_description: string
        experimental_protocol: string
        testability_score: number
  meta_review_feedback: optional
    synthesis: string
    improvement_suggestions: list[string]
  context:
    research_goal: string
    domain_constraints: list[string]
    existing_hypothesis_count: number
```

## Outputs

```yaml
evolved_hypothesis:
  task_id: string
  parent_hypotheses: list[string]  # IDs of source hypotheses
  evolution_strategy: string
  hypothesis:
    summary: string
    full_description: string
    experimental_protocol: string
    key_improvements: list[string]
    evolution_rationale: string
  metadata:
    created_timestamp: datetime
    evolution_path: string  # e.g., "enhancement->combination"
```

## Behavioral Contracts

### Enhancement Strategy
The agent MUST:
- Identify at least one specific weakness in the source hypothesis
- Provide literature-backed improvements when using web search
- Maintain the core research direction while addressing gaps
- Document the enhancement rationale

### Combination Strategy
The agent MUST:
- Select 2-5 complementary hypotheses for combination
- Identify non-conflicting elements from each source
- Create a coherent merged hypothesis, not a simple concatenation
- Explain how the combination improves upon individual components

### Simplification Strategy
The agent MUST:
- Reduce experimental complexity by at least 30%
- Maintain the core scientific insight
- Improve testability score
- Document what was removed and why

### Out-of-Box Strategy
The agent MUST:
- Generate variations that differ substantially from source
- Apply cross-domain analogies when possible
- Maintain scientific plausibility
- Explain the divergent thinking approach used

## Interaction Protocols

### With Ranking Agent
1. Receive top-ranked hypotheses (typically Elo rating > 1200)
2. Access tournament performance data
3. Submit evolved hypotheses for new tournament evaluation

### With Meta-review Agent
1. Receive synthesis of feedback patterns
2. Incorporate improvement suggestions into evolution process
3. Align evolution strategies with identified research gaps

### With Web Search Interface
1. Query literature for enhancement evidence
2. Find analogies for out-of-box thinking
3. Validate feasibility of evolved approaches

### With Context Memory
1. Store evolution lineage for each hypothesis
2. Track which strategies produce successful variants
3. Access full tournament state and hypothesis repository

## Examples

### Example 1: Enhancement Strategy
```yaml
Input:
  strategy: enhancement
  source_hypothesis:
    summary: "JAK inhibitors for AML treatment"
    weakness: "Limited evidence for combination therapy"

Output:
  evolved_hypothesis:
    summary: "JAK inhibitors combined with BCL-2 inhibitors for AML"
    key_improvements:
      - "Added synergistic BCL-2 targeting based on recent Nature paper"
      - "Specified biomarker-driven patient selection criteria"
    evolution_rationale: "Literature search revealed promising JAK/BCL-2 combination data in preclinical AML models"
```

### Example 2: Combination Strategy
```yaml
Input:
  strategy: combination
  source_hypotheses:
    - "STING pathway activation for liver fibrosis"
    - "Macrophage reprogramming in fibrotic disease"

Output:
  evolved_hypothesis:
    summary: "STING-mediated macrophage reprogramming for liver fibrosis reversal"
    key_improvements:
      - "Integrated STING activation with macrophage targeting"
      - "Combined molecular mechanism with cellular approach"
    evolution_rationale: "STING pathway can drive macrophage polarization, creating synergy"
```

### Example 3: Simplification Strategy
```yaml
Input:
  strategy: simplification
  source_hypothesis:
    summary: "Multi-omics approach with proteomics, metabolomics, and transcriptomics for AMR detection"

Output:
  evolved_hypothesis:
    summary: "Targeted metabolomics panel for rapid AMR detection"
    key_improvements:
      - "Focused on metabolomics alone for faster results"
      - "Reduced from 3 platforms to 1"
      - "Decreased time to result from 72h to 6h"
    evolution_rationale: "Metabolomics showed strongest signal in preliminary data"
```

### Example 4: Out-of-Box Strategy
```yaml
Input:
  strategy: out_of_box
  source_hypothesis:
    summary: "Small molecule inhibitors for antimicrobial resistance"

Output:
  evolved_hypothesis:
    summary: "Engineered bacteriophage cocktails with CRISPR payloads for precision AMR treatment"
    key_improvements:
      - "Shifted from chemical to biological intervention"
      - "Applied synthetic biology approach"
      - "Enabled strain-specific targeting"
    evolution_rationale: "Applied viral engineering concepts from cancer immunotherapy to infectious disease"
```

## Performance Characteristics

The Evolution Agent SHOULD:
- Process evolution tasks within 60 seconds
- Generate hypotheses that achieve >20% tournament win rate
- Produce at least 1 successful variant per 5 attempts
- Adapt strategy selection based on tournament feedback

## Error Handling

The agent MUST handle:
- Insufficient source hypotheses for combination (fallback to enhancement)
- Web search failures (proceed with cached knowledge)
- Invalid evolution strategies (log error, skip task)
- Hypothesis generation failures (report to Supervisor, retry with different strategy)