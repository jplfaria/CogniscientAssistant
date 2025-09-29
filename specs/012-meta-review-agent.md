# Meta-review Agent Specification

**Type**: Agent  
**Interactions**: Supervisor Agent, Context Memory, All Other Agents (via feedback)

## Prerequisites
- Read: Reflection Agent Specification (for understanding review types)
- Read: Ranking Agent Specification (for tournament debate patterns)
- Understand: Feedback propagation concepts from System Overview

## Overview

The Meta-review Agent synthesizes insights from all reviews and tournament debates, identifying recurring patterns and generating feedback to improve the system's performance in subsequent iterations. It also produces comprehensive research overviews and identifies potential research contacts. This agent enables the AI Co-Scientist's continuous self-improvement without requiring back-propagation or fine-tuning.

## Core Behaviors

### Pattern Synthesis
- Analyzes all review outputs from Reflection Agent
- Examines tournament debate transcripts from Ranking Agent
- Identifies recurring themes, critiques, and recommendations
- Detects systematic issues across multiple hypotheses
- Recognizes successful patterns that lead to high-quality hypotheses

### Feedback Generation
- Creates actionable feedback for each agent type
- Tailors feedback to agent-specific responsibilities
- Prioritizes critical issues that affect hypothesis quality
- Balances comprehensive coverage with concise recommendations
- Ensures feedback improves future iterations without overfitting

### Research Overview Generation
- Synthesizes top-ranked hypotheses into coherent research directions
- Organizes hypotheses by thematic areas
- Justifies importance of each research direction
- Suggests specific experiments within each area
- Formats output according to specified templates (e.g., NIH Specific Aims)

### Research Contact Identification
- Analyzes literature references from hypothesis generation
- Identifies domain experts relevant to research hypotheses
- Provides reasoning for each suggested contact
- Groups contacts by expertise area
- Includes contact information when available in public sources

## Inputs

### From Supervisor Agent
```
Input Structure:
  - task_type: "generate_meta_review" | "create_research_overview"
  - iteration_number: integer
  - research_goal: string
  - target_format: string (optional, e.g., "NIH_specific_aims")
  - feedback_config:
    - include_all_agents: boolean
    - priority_threshold: float
    - synthesis_depth: "summary" | "detailed"
```

### From Context Memory
```
Retrieved Data:
  - reflection_reviews: List[
      - hypothesis_id: string
      - review_type: string
      - review_content: string
      - identified_issues: List[string]
      - strengths: List[string]
      - recommendations: List[string]
    ]
  - tournament_debates: List[
      - match_id: string
      - hypothesis_1_id: string
      - hypothesis_2_id: string
      - debate_transcript: string
      - decision_rationale: string
      - key_arguments: List[string]
    ]
  - hypothesis_rankings: List[
      - hypothesis_id: string
      - elo_rating: float
      - rank_position: integer
    ]
  - previous_meta_reviews: List[meta_review] (if any)
```

## Outputs

### Meta-review Critique
```
Critique Structure:
  - synthesis_summary: string
  - common_patterns: List[
      - pattern_type: string
      - frequency: integer
      - description: string
      - impact_on_quality: "high" | "medium" | "low"
      - examples: List[hypothesis_id]
    ]
  - agent_specific_feedback:
    - generation_agent:
      - strengths: List[string]
      - improvement_areas: List[string]
      - specific_recommendations: List[string]
    - reflection_agent:
      - missed_issues: List[string]
      - review_consistency: float
      - suggested_focus_areas: List[string]
    - ranking_agent:
      - debate_quality: string
      - ranking_consistency: float
      - improvement_suggestions: List[string]
    - evolution_agent:
      - evolution_effectiveness: string
      - diversity_assessment: string
      - strategy_recommendations: List[string]
  - iteration_improvements:
    - metrics_comparison: object
    - progress_indicators: List[string]
    - next_iteration_priorities: List[string]
```

### Research Overview
```
Overview Structure:
  - executive_summary: string
  - research_areas: List[
      - area_title: string
      - importance_justification: string
      - key_hypotheses: List[
          - hypothesis_id: string
          - hypothesis_summary: string
          - elo_rating: float
        ]
      - proposed_experiments: List[
          - experiment_description: string
          - expected_outcomes: string
          - resource_requirements: string
        ]
      - related_literature: List[citation]
    ]
  - cross_cutting_themes: List[string]
  - innovation_highlights: List[string]
  - risk_assessment: string
  - recommended_next_steps: List[string]
  - potential_collaborators: List[research_contact]
```

### Research Contacts
```
Contact Structure:
  - contacts: List[
      - name: string (redacted if needed)
      - institution: string
      - expertise_areas: List[string]
      - relevance_reasoning: string
      - relevant_publications: List[citation]
      - contact_priority: "high" | "medium" | "low"
    ]
  - expertise_gaps: List[string]
  - collaboration_opportunities: List[string]
```

## Behavioral Contracts

### Pattern Recognition
- MUST analyze ALL available reviews and debates
- MUST identify patterns that appear in >20% of reviews
- MUST distinguish between systematic and isolated issues
- MUST weight patterns by their impact on hypothesis quality
- SHOULD recognize both positive and negative patterns

### Feedback Quality
- MUST provide actionable, specific feedback
- MUST avoid overly general recommendations
- MUST tailor feedback to each agent's capabilities
- MUST prioritize high-impact improvements
- SHOULD balance criticism with recognition of strengths

### Overview Coherence
- MUST organize hypotheses into logical research areas
- MUST provide clear justification for each area's importance
- MUST ensure proposed experiments are feasible
- MUST maintain consistency with research goal
- SHOULD identify synergies between research areas

### Contact Identification
- MUST base suggestions on actual literature citations
- MUST provide clear reasoning for each contact
- MUST respect privacy (redact names when appropriate)
- SHOULD identify diverse expertise areas
- SHOULD prioritize based on relevance to hypotheses

## Interaction Protocols

### With Supervisor Agent
```
1. Receive meta-review generation task
2. Request relevant data from Context Memory
3. Process reviews and debates systematically
4. Generate comprehensive feedback and/or overview
5. Return results with confidence metrics
6. Update task status to "completed"
```

### With Context Memory
```
1. Query all reviews for current iteration
2. Retrieve tournament debates and results
3. Access hypothesis rankings and details
4. Fetch previous meta-reviews for comparison
5. Store generated meta-review and overview
6. Maintain version history
```

### Feedback Propagation
```
1. Feedback appended to agent prompts in next iteration
2. No direct agent communication required
3. Feedback persists across iterations
4. Agents adapt behavior based on feedback
5. System improves without fine-tuning
```

## Examples

### Example 1: Common Pattern Identification
```
Scenario: ALS drug repurposing research

Reviews analyzed: 45 hypothesis reviews, 120 tournament debates

Identified patterns:
1. Blood-brain barrier issue (38/45 reviews, 84%)
   - Many proposed drugs cannot cross BBB
   - Impact: High - renders hypothesis non-viable
   - Recommendation: Check BBB permeability early

2. Incomplete mechanism description (22/45 reviews, 49%)
   - Hypotheses lack detailed pathway analysis
   - Impact: Medium - affects experimental design
   - Recommendation: Require pathway diagrams

3. Missing dosage considerations (28/45 reviews, 62%)
   - Clinical relevance unclear without dosing
   - Impact: Medium - affects feasibility
   - Recommendation: Include therapeutic window analysis
```

### Example 2: Agent-Specific Feedback
```
Generation Agent Feedback:
- Strengths:
  - Excellent literature grounding (95% with citations)
  - Creative combination of existing drugs
  - Good coverage of different mechanism classes
  
- Improvement Areas:
  - Consider BBB permeability constraints upfront
  - Include more specific molecular targets
  - Address potential drug interactions
  
- Specific Recommendations:
  1. Add BBB permeability check to hypothesis template
  2. Require identification of specific protein targets
  3. Include preliminary safety assessment

Reflection Agent Feedback:
- Missed Issues:
  - Overlooked drug interaction risks in 30% of reviews
  - Inconsistent evaluation of novelty claims
  
- Suggested Focus Areas:
  1. Standardize novelty assessment criteria
  2. Always check for drug-drug interactions
  3. Verify experimental feasibility claims
```

### Example 3: Research Overview (NIH Format)
```
Research Goal: "Novel treatments for liver fibrosis"

SPECIFIC AIMS

The long-term goal is to develop effective therapies for liver fibrosis, 
a major cause of morbidity affecting millions worldwide. Based on our 
AI-assisted hypothesis generation, we propose three innovative approaches:

Aim 1: Investigate epigenetic modulators for fibrosis reversal
- Test BET inhibitors in hepatic stellate cells
- Evaluate HDAC6-specific inhibitors
- Assess combination epigenetic therapy

Aim 2: Develop targeted anti-fibrotic cytokine delivery
- Engineer IL-10 variants with enhanced stability
- Create hepatocyte-specific delivery vectors
- Test in humanized liver organoids

Aim 3: Explore CRISPR-based stellate cell reprogramming
- Design guide RNAs for key fibrotic genes
- Develop AAV-based delivery system
- Validate in patient-derived organoids

Expected Outcomes: These studies will identify 2-3 lead candidates
for preclinical development, potentially transforming fibrosis treatment.
```

## Performance Characteristics

### Processing Requirements
- Review analysis: O(n*m) where n=hypotheses, m=review types
- Pattern detection: O(n²) for cross-hypothesis patterns
- Feedback generation: O(a) where a=number of agents
- Overview synthesis: O(n log n) for hypothesis ranking

### Quality Metrics
- Pattern detection accuracy: >85% agreement with expert analysis
- Feedback actionability: >90% of recommendations implementable
- Overview coherence: >4.0/5.0 expert rating
- Contact relevance: >80% appropriate suggestions

### Timing Constraints
- Meta-review generation: Complete within 5 minutes
- Research overview: Format within 10 minutes
- Feedback propagation: Available for next iteration
- Contact identification: Real-time during overview generation