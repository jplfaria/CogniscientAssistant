# Meta-review Agent Specification

**Type**: Agent  
**Interactions**: Supervisor Agent, Generation Agent, Reflection Agent, Ranking Agent, Evolution Agent, Proximity Agent, Context Memory

## Prerequisites
- Read: Multi-Agent Framework Specification
- Read: Reflection Agent Specification
- Read: Ranking Agent Specification
- Read: Context Memory System Specification

## Purpose
The Meta-review Agent synthesizes insights across the entire AI Co-Scientist system, identifying patterns in reviews and tournament debates to enable continuous improvement. It transforms distributed knowledge from multiple agents into coherent research overviews and actionable feedback, serving as the system's primary learning and synthesis mechanism.

## Meta-review Agent Behavior
1. Synthesizes feedback from all review types and tournament debates into meta-review critiques
2. Identifies recurring patterns, common issues, and systemic gaps across agent activities
3. Generates comprehensive research overviews from top-ranked hypotheses
4. Suggests qualified domain experts based on literature analysis
5. Formats research documents according to standard publication templates
6. Provides targeted feedback to improve future agent performance
7. Maps the boundary of current knowledge relevant to the research goal
8. Enables system-wide learning without gradient-based optimization

## Inputs

```
MetaReviewRequest {
  tournament_results: TournamentState {
    debate_transcripts: list[ScientificDebate]
    ranking_history: list[RankingSnapshot]
    elo_updates: list[EloChange]
  }
  
  all_reviews: ReviewCollection {
    initial_reviews: list[InitialReview]
    full_reviews: list[FullReview]
    deep_verifications: list[DeepVerification]
    observation_reviews: list[ObservationReview]
    simulation_reviews: list[SimulationReview]
    tournament_reviews: list[TournamentReview]
  }
  
  top_hypotheses: list[RankedHypothesis] {
    hypothesis: Hypothesis
    rank: int
    elo_score: float
    review_summary: ReviewSummary
  }
  
  research_context: ResearchContext {
    research_goal: string
    domain: string
    prior_literature: list[LiteratureReference]
    iteration_count: int
  }
  
  synthesis_type: OverviewRequest | CritiqueRequest | ExpertSuggestion
}
```

## Outputs

```
MetaReviewOutput {
  meta_critique: MetaCritique {
    common_patterns: list[Pattern] {
      pattern_type: Strength | Weakness | Gap
      description: string
      frequency: int
      examples: list[string]
    }
    
    systemic_issues: list[Issue] {
      issue_description: string
      affected_agents: list[AgentType]
      severity: High | Medium | Low
      recommendation: string
    }
    
    improvement_suggestions: list[Suggestion] {
      target_agent: AgentType
      suggestion: string
      expected_impact: string
    }
  }
  
  research_overview: ResearchOverview (optional) {
    executive_summary: string
    research_areas: list[ResearchArea] {
      area_name: string
      justification: string
      key_hypotheses: list[HypothesisSummary]
      proposed_experiments: list[ExperimentOutline]
      priority: High | Medium | Low
    }
    
    knowledge_boundaries: KnowledgeMap {
      well_understood: list[string]
      emerging_areas: list[string]
      unknown_territories: list[string]
    }
    
    next_steps: list[ActionItem]
  }
  
  expert_contacts: list[ExpertSuggestion] (optional) {
    expert_name: string
    affiliation: string
    expertise_areas: list[string]
    relevance_reasoning: string
    contact_priority: High | Medium | Low
  }
  
  formatted_documents: list[FormattedDocument] (optional) {
    format_type: NIH_SpecificAims | NSF_ProjectSummary | Custom
    content: string
    metadata: DocumentMetadata
  }
}
```

## Synthesis Behaviors

### Pattern Recognition
The Meta-review Agent identifies patterns across multiple dimensions:
- **Review patterns**: Common strengths, weaknesses, and gaps in hypotheses
- **Debate patterns**: Recurring arguments and counterarguments in tournaments
- **Evolution patterns**: How hypotheses improve or degrade through iterations
- **Safety patterns**: Common safety concerns or ethical considerations

### Feedback Generation
Creates targeted feedback for system improvement:
- **For Generation Agent**: Areas to explore, patterns to avoid, promising directions
- **For Reflection Agent**: Review blind spots, consistency issues, evaluation criteria refinements
- **For Evolution Agent**: Successful evolution strategies, combination patterns that work
- **For Ranking Agent**: Debate quality improvements, ranking criteria adjustments

### Research Overview Formulation
Synthesizes top hypotheses into coherent research roadmaps:
- Groups related hypotheses into research themes
- Identifies logical progression of experiments
- Maps dependencies between research areas
- Highlights high-impact opportunities

## Integration Patterns

### With Ranking Agent
- Receives: Complete tournament state including all debates and ranking outcomes
- Analyzes: Debate quality, argument patterns, ranking consistency
- Provides: Insights on improving tournament effectiveness

### With Reflection Agent
- Receives: All six types of reviews across all hypotheses
- Analyzes: Review thoroughness, consistency, and coverage
- Provides: Meta-level feedback on review quality and blind spots

### With Generation Agent
- Receives: History of generated hypotheses through Context Memory
- Analyzes: Generation patterns, creativity vs. feasibility balance
- Provides: Strategic guidance for future hypothesis generation

### With Context Memory
- Writes: Synthesized insights, meta-reviews, research overviews
- Reads: Historical patterns, prior meta-analyses, accumulated knowledge
- Maintains: Institutional memory of what works and what doesn't

### With Supervisor Agent
- Receives: Synthesis requests and timing triggers
- Provides: Research overviews and meta-critiques for system orchestration
- Enables: Adaptive system behavior based on accumulated insights

## Periodic Synthesis

The Meta-review Agent operates on configurable triggers:
- **After N tournament rounds**: Synthesize debate patterns
- **After M hypotheses reviewed**: Identify review patterns
- **On demand**: Generate research overview for external presentation
- **At iteration boundaries**: Provide comprehensive system feedback

## Quality Assurance

### Continuous Improvement Loop
```
1. Collect agent outputs and interactions
2. Identify patterns and anomalies
3. Generate actionable feedback
4. Append feedback to agent prompts
5. Monitor improvement in next iteration
```

### Critical Factor Tracking
Maintains awareness of domain-specific critical factors:
- For drug discovery: Blood-brain barrier, toxicity, selectivity
- For materials science: Stability, scalability, cost
- For climate solutions: Feasibility, impact scale, implementation barriers

## Examples

### Example Meta-Critique Pattern
```
Input: 50 drug repurposing hypotheses with reviews
Common Pattern Identified:
- Type: Weakness
- Description: "Hypotheses frequently overlook drug-drug interactions with common ALS medications"
- Frequency: 32/50 hypotheses
- Recommendation: "Generation Agent should query drug interaction databases for all proposed compounds"
```

### Example Research Overview Structure
```
Research Area: "Targeting Protein Aggregation in ALS"
Justification: "7 of top 10 hypotheses focus on protein aggregation mechanisms"
Key Hypotheses:
1. "Repurpose HSP90 inhibitors to prevent SOD1 aggregation"
2. "Combine autophagy enhancers with aggregation inhibitors"
Proposed Experiments:
1. In vitro aggregation assays with patient-derived cells
2. Mouse model studies with combination therapies
```

## Boundaries

### The Meta-review Agent Does:
- Synthesize patterns across all agent activities
- Generate high-level research strategies
- Identify systemic improvements
- Format documents for publication
- Suggest domain experts for consultation

### The Meta-review Agent Does Not:
- Generate new hypotheses directly
- Perform individual hypothesis reviews
- Execute experiments or simulations
- Make final research decisions
- Override safety boundaries
- Contact experts directly