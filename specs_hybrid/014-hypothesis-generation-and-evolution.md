# Hypothesis Generation and Evolution Specification

**Type**: Core Functionality  
**Interactions**: Generation Agent, Evolution Agent, Reflection Agent, Ranking Agent, Proximity Agent, Meta-review Agent, Supervisor Agent, Context Memory

## Prerequisites
- Read: Generation Agent Specification
- Read: Evolution Agent Specification  
- Read: Ranking Agent Specification
- Read: Context Memory System Specification
- Understand: Tournament and Elo Rating System concepts

## Overview

The Hypothesis Generation and Evolution system implements a "generate, debate, and evolve" approach to scientific hypothesis creation. The system produces increasingly novel and high-quality scientific hypotheses through iterative refinement cycles, tournament-based selection, and multiple evolution strategies.

## Core Behaviors

### Initial Hypothesis Generation

The system MUST generate initial hypotheses from a research goal through:
- Literature exploration via iterative web searches
- Simulated scientific debates using self-critique
- Systematic assumption identification and analysis
- Incorporation of experimental constraints

### Hypothesis Evolution Cycle

The system MUST evolve hypotheses through six distinct strategies:

1. **Enhancement through grounding** - Strengthen evidence and fill reasoning gaps
2. **Coherence and feasibility improvements** - Address logical inconsistencies and practical constraints
3. **Inspiration from existing hypotheses** - Create variations of successful patterns
4. **Combination** - Synthesize best aspects of multiple hypotheses
5. **Simplification** - Reduce complexity for easier verification
6. **Out-of-box thinking** - Explore divergent ideas away from existing clusters

### Tournament-Based Selection

The system MUST:
- Select hypotheses for evolution based on Elo ratings from tournaments
- Prioritize evolution of top-ranked hypotheses
- Maintain diversity by considering proximity relationships
- Protect existing hypotheses by generating new ones rather than modifying

### Iterative Improvement

The system MUST implement continuous improvement through:
- Meta-review synthesis across all hypothesis reviews
- Feedback incorporation into subsequent generation cycles
- Performance-based resource allocation
- Learning without backpropagation

## Inputs

### Research Goal Configuration
```
ResearchGoal {
  goal_description: string (natural language, max 1000 chars)
  constraints: List[string] (experimental or practical limitations)
  preferences: List[string] (scientist priorities)
  existing_hypotheses: List[Hypothesis] (optional, for tournament inclusion)
}
```

### Evolution Selection Criteria
```
EvolutionCriteria {
  top_k_hypotheses: int (number of top-ranked to evolve)
  diversity_threshold: float (minimum distance for out-of-box)
  evolution_strategies: List[EvolutionStrategy] (which strategies to apply)
}
```

## Outputs

### Generated Hypothesis
```
Hypothesis {
  id: string (unique identifier)
  summary: string (concise statement, max 200 chars)
  full_description: string (detailed explanation)
  experimental_protocol: string (testable methodology)
  grounding_citations: List[Citation] (supporting literature)
  novelty_justification: string (why this is novel)
  confidence_score: float (0.0 to 1.0)
  evolution_history: List[EvolutionStep] (optional, ancestry trace)
}
```

### Evolution Result
```
EvolutionResult {
  parent_hypothesis_ids: List[string] (source hypotheses)
  evolution_strategy: EvolutionStrategy (method used)
  new_hypothesis: Hypothesis (evolved result)
  improvement_rationale: string (why this evolution helps)
}
```

## Behavioral Contracts

### Generation Guarantees

The Generation process MUST:
- Always ground hypotheses in retrieved literature when available
- Generate at least 3 distinct hypotheses per research goal
- Complete initial generation within reasonable time bounds
- Include experimental protocols for all hypotheses
- Provide novelty justification relative to existing knowledge

### Evolution Guarantees

The Evolution process MUST:
- Never modify existing hypotheses directly (create new ones)
- Apply at least one evolution strategy per selected hypothesis
- Maintain traceability through evolution_history
- Ensure evolved hypotheses remain relevant to research goal
- Balance exploitation of successful patterns with exploration

### Quality Assurance

The system MUST ensure:
- All hypotheses undergo initial review before ranking
- Tournament comparisons use scientific debate format
- Safety flags prevent dangerous hypotheses from ranking highly
- Diversity metrics guide evolution strategy selection
- Meta-review patterns improve future generation quality

## Interaction Patterns

### With Generation Agent
- Receives: Research goals and meta-review feedback
- Produces: Initial hypothesis sets
- Triggers: Literature searches and assumption analysis

### With Evolution Agent  
- Receives: Top-ranked hypotheses and evolution criteria
- Produces: New evolved hypotheses
- Applies: One or more evolution strategies

### With Reflection Agent
- Receives: All generated and evolved hypotheses
- Obtains: Multiple review types for quality assessment
- Uses: Review scores in tournament seeding

### With Ranking Agent
- Sends: Hypothesis pairs for tournament comparison
- Receives: Elo ratings and ranking updates
- Prioritizes: Similar hypotheses for meaningful debates

### With Proximity Agent
- Queries: Similarity between hypothesis pairs
- Receives: Proximity graph for diversity analysis
- Uses: Distance metrics for out-of-box evolution

### With Meta-review Agent
- Provides: All reviews and rankings for pattern synthesis
- Receives: System-wide feedback for improvement
- Incorporates: Insights into next generation cycle

## Error Handling

The system MUST handle:
- **Empty generation results**: Retry with modified prompts
- **Evolution failures**: Fall back to alternative strategies
- **Timeout conditions**: Return partial results with status
- **Invalid hypotheses**: Filter before tournament entry
- **Circular evolution**: Detect and prevent hypothesis loops

## Natural Language Examples

### Research Goal Input
```
"Identify novel therapeutic targets for treating drug-resistant tuberculosis 
by focusing on metabolic pathways unique to dormant mycobacteria, with 
constraints on targeting human homologs"
```

### Generated Hypothesis Summary
```
"Target the DosR regulon-controlled triacylglycerol synthase (tgs1) to 
disrupt lipid storage in dormant M. tuberculosis, preventing survival 
during latency without affecting human lipid metabolism"
```

### Evolution Example (Combination Strategy)
```
Parent 1: "Inhibit WhiB3 to disrupt redox homeostasis"
Parent 2: "Target lipid metabolism for dormancy disruption"
Combined: "Dual inhibition of WhiB3-regulated lipid biosynthesis pathways 
to simultaneously disrupt redox balance and energy storage in dormant TB"
```

## Performance Expectations

While avoiding implementation details, the system exhibits these behavioral characteristics:
- Generates initial hypotheses within minutes of receiving research goal
- Evolves hypotheses continuously as compute resources allow
- Improves hypothesis quality measurably across iterations
- Maintains diverse hypothesis portfolio throughout process
- Converges on high-quality candidates through tournament selection

## Safety and Ethics

The system MUST:
- Flag hypotheses with potential safety concerns
- Prevent ranking of dangerous proposals in top positions
- Consider ethical implications in experimental protocols
- Maintain transparency in evolution history
- Allow expert oversight at critical decision points