# Evolution Agent Specification

**Type**: Agent  
**Interactions**: Supervisor Agent, Ranking Agent, Context Memory, Web Search Tools, Meta-review Agent

## Prerequisites
- Read: System Overview and Architecture Specification
- Read: Multi-Agent Framework Specification
- Read: Ranking Agent Specification
- Read: Context Memory System Specification
- Understand: Tournament and Elo Rating System concepts

## Purpose

The Evolution Agent continuously refines and improves existing hypotheses through iterative enhancement. It implements a self-improving cycle by taking top-ranked hypotheses from tournaments and creating enhanced versions using diverse refinement strategies. The Evolution Agent enables test-time compute scaling by generating increasingly sophisticated hypotheses through systematic refinement.

## Agent Behavior

The Evolution Agent exhibits the following behaviors:

1. **Hypothesis Enhancement**: Identifies weaknesses in existing hypotheses and creates improved versions through grounding and elaboration
2. **Coherence and Feasibility Improvement**: Addresses logical issues and practical constraints to create more viable hypotheses
3. **Hypothesis Combination**: Merges the best aspects of multiple top-ranking hypotheses into unified proposals
4. **Hypothesis Simplification**: Creates streamlined versions of complex hypotheses for easier testing and validation
5. **Out-of-Box Exploration**: Generates divergent hypotheses that move beyond existing paradigms
6. **Non-Destructive Refinement**: Always creates new hypotheses rather than modifying existing ones

## Inputs

### From Ranking Agent
```
TournamentResults {
  top_hypotheses: list[RankedHypothesis]
  elo_ratings: dict[hypothesis_id, float]
  tournament_metadata: dict
  debate_insights: list[DebateInsight]
}
```

### From Context Memory
```
EvolutionContext {
  hypothesis_history: list[Hypothesis]
  refinement_statistics: dict
  success_patterns: list[Pattern]
  failure_patterns: list[Pattern]
}
```

### From Meta-review Agent
```
EvolutionGuidance {
  improvement_priorities: list[string]
  successful_strategies: list[Strategy]
  areas_to_explore: list[string]
  refinement_feedback: dict
}
```

### From Research Configuration
```
ResearchGoal {
  goal_description: string
  constraints: list[string]
  preferences: dict
}
```

## Outputs

### Evolved Hypothesis Structure
```
EvolvedHypothesis {
  id: string
  parent_hypotheses: list[string]  # IDs of source hypotheses
  title: string
  summary: string
  full_description: string
  refinement_type: RefinementType
  improvements: list[Improvement]
  experimental_protocol: Protocol
  expected_outcomes: list[string]
  novelty_rationale: string
  grounding_citations: list[Citation]
  evolution_metadata: EvolutionMetadata
  timestamp: datetime
}
```

### Improvement Structure
```
Improvement {
  aspect: string  # What was improved
  before: string  # Previous state
  after: string   # Improved state
  rationale: string  # Why this improvement
  evidence: list[Citation]  # Supporting evidence
}
```

### Evolution Metadata
```
EvolutionMetadata {
  strategy_used: string
  parent_elo_ratings: list[float]
  refinement_depth: int  # Number of evolution iterations
  search_queries: list[string]
  articles_reviewed: int
}
```

## Refinement Strategies

### 1. Enhancement Through Grounding

**Behavior**:
- Analyzes hypothesis for weak or unsubstantiated claims
- Generates targeted literature search queries
- Retrieves and analyzes relevant research
- Incorporates findings to strengthen hypothesis
- Fills reasoning gaps with evidence-based details

**Process**:
1. Identify weakness points in hypothesis
2. Formulate specific search queries for each weakness
3. Retrieve and read relevant articles (typically 5-10)
4. Extract supporting evidence and counter-evidence
5. Create enhanced hypothesis incorporating new findings
6. Elaborate on mechanisms with discovered details

**Example Enhancement**:
- Original: "Drug X might affect pathway Y"
- Search: Recent studies on Drug X mechanisms
- Enhanced: "Drug X inhibits enzyme Z at 50nM IC50, leading to downstream effects on pathway Y through phosphorylation cascade"

### 2. Coherence, Practicality and Feasibility Improvements

**Behavior**:
- Identifies logical inconsistencies in hypotheses
- Rectifies invalid assumptions
- Addresses practical experimental constraints
- Ensures feasible validation protocols
- Creates more coherent narrative flow

**Improvement Types**:
```
CoherenceImprovements {
  logical_consistency: boolean
  assumption_validity: boolean
  experimental_feasibility: boolean
  resource_requirements: Feasible | Challenging | Infeasible
  timeline_realism: boolean
}
```

**Example Improvements**:
- Fix contradictory claims within hypothesis
- Replace untestable predictions with measurable ones
- Adjust protocols to available resources
- Clarify ambiguous terminology

### 3. Hypothesis Combination

**Behavior**:
- Identifies complementary aspects of top hypotheses
- Merges non-conflicting elements
- Creates unified proposals with broader scope
- Preserves the strengths of each parent hypothesis
- Resolves conflicts through synthesis

**Combination Patterns**:
- **Mechanistic Merger**: Combine different pathway components
- **Scale Integration**: Unite molecular and systems-level insights
- **Method Synthesis**: Merge experimental approaches
- **Target Unification**: Combine related therapeutic targets

**Example Combination**:
```
Parent 1: "Inhibit kinase A to reduce inflammation"
Parent 2: "Target receptor B to modulate immune response"
Combined: "Dual inhibition of kinase A and receptor B for synergistic anti-inflammatory effect through coordinated pathway modulation"
```

### 4. Simplification

**Behavior**:
- Identifies overly complex hypotheses
- Extracts core testable claims
- Removes unnecessary complexity
- Creates streamlined validation protocols
- Maintains scientific rigor while improving clarity

**Simplification Criteria**:
- Reduce number of variables
- Focus on primary mechanism
- Streamline experimental design
- Clarify outcome measures
- Remove tangential elements

**Example Simplification**:
- Complex: Multi-pathway hypothesis with 10 targets
- Simplified: Focus on 2 key targets with clearest evidence
- Benefit: Faster validation, clearer results

### 5. Out-of-Box Thinking

**Behavior**:
- Deliberately moves away from conventional approaches
- Explores unconventional connections
- Challenges fundamental assumptions
- Generates paradigm-shifting proposals
- Balances novelty with scientific plausibility

**Divergence Strategies**:
- **Analogy Transfer**: Apply concepts from different fields
- **Assumption Reversal**: Question accepted premises
- **Scale Jumping**: Explore different biological scales
- **Time Perspective**: Consider evolutionary or developmental angles
- **Cross-Domain**: Connect disparate research areas

**Example Out-of-Box**:
- Conventional: "Target cancer cells directly"
- Out-of-Box: "Reprogram cancer cells to become antigen-presenting cells"

### 6. Inspiration from Existing Hypotheses

**Behavior**:
- Uses successful hypotheses as creative springboards
- Generates variations on proven themes
- Explores adjacent possibility space
- Maintains connection to validated concepts
- Creates novel extensions of existing ideas

**Inspiration Patterns**:
- **Target Variation**: Same mechanism, different target
- **Disease Translation**: Same approach, different condition
- **Method Adaptation**: Same goal, novel methodology
- **Mechanism Extension**: Deeper exploration of pathway

## Quality Control Mechanisms

### Pre-Evolution Validation
Before creating evolved hypotheses:
1. Verify parent hypotheses have minimum Elo rating
2. Check evolution would add meaningful improvement
3. Ensure compliance with research constraints
4. Validate scientific plausibility
5. Confirm novelty versus existing hypotheses

### Post-Evolution Verification
After generating evolved hypothesis:
1. Compare against parent hypotheses for improvement
2. Check for unintended degradation
3. Verify citations support claims
4. Ensure protocol remains feasible
5. Confirm maintains scientific rigor

## Tool Integration

### Literature Search Enhancement
```
EnhancementSearch {
  weakness_query: string
  evidence_type: Mechanistic | Clinical | Experimental
  recency_filter: string  # e.g., "last_3_years"
  quality_filter: HighImpact | PeerReviewed | All
}
```

### Hypothesis Analysis Tools
- Weakness detection algorithms
- Coherence checking systems
- Feasibility assessment protocols
- Novelty comparison metrics

## State Management

### Read Operations
- Access top-ranked hypotheses from tournaments
- Retrieve hypothesis evolution history
- Query successful refinement patterns
- Review meta-feedback on strategies

### Write Operations
- Store evolved hypotheses with full lineage
- Update refinement strategy statistics
- Log search queries and results
- Record improvement rationales

## Performance Characteristics

### Refinement Depth
- Each hypothesis can undergo multiple evolution cycles
- Depth tracked to prevent over-refinement
- Diminishing returns after 3-5 iterations
- Balance exploration vs exploitation

### Strategy Selection
- Adaptive based on hypothesis characteristics
- Guided by meta-review feedback
- Considers past success rates
- Rotates strategies to ensure diversity

### Resource Allocation
- Prioritize evolution of highest Elo hypotheses
- Limit concurrent refinements
- Balance compute across strategies
- Cache literature search results

## Error Handling

### Common Scenarios
1. **Literature Search Failures**
   - Proceed with available information
   - Note data limitations in output
   - Attempt alternative search strategies

2. **Incompatible Combination**
   - Detect conflicting mechanisms early
   - Pivot to single-parent refinement
   - Document why combination failed

3. **Over-Simplification**
   - Detect loss of essential complexity
   - Revert to previous version
   - Adjust simplification parameters

4. **Divergence Too Extreme**
   - Apply plausibility checks
   - Scale back unconventional elements
   - Maintain scientific grounding

## Integration Patterns

### With Ranking Agent
- Receive tournament winners for evolution
- Submit evolved hypotheses back to tournaments
- Use Elo ratings to guide refinement priority
- Incorporate debate insights into improvements

### With Supervisor Agent
- Accept evolution tasks with parameters
- Report completion and statistics
- Request additional resources as needed
- Signal when refinement plateaus

### With Meta-review Agent
- Receive guidance on successful strategies
- Adjust approach based on patterns
- Focus on identified improvement areas
- Avoid strategies with poor outcomes

### With Generation Agent
- Operates in parallel but independently
- No direct hypothesis exchange
- Complementary roles in hypothesis ecosystem
- Different optimization objectives

## Success Metrics

The Evolution Agent's effectiveness is measured by:
1. **Elo Improvement Rate**: Average rating increase in evolved hypotheses
2. **Strategy Success Rate**: Percentage of improvements by strategy type
3. **Refinement Quality**: Expert assessment of improvements
4. **Diversity Maintenance**: Avoiding convergence to local optima
5. **Computational Efficiency**: Quality gain per compute hour

## Configuration Parameters

```
EvolutionConfig {
  min_parent_elo: float (default: 1200)
  max_evolution_depth: int (default: 5)
  strategies_per_hypothesis: int (default: 2)
  literature_search_depth: int (default: 10)
  combination_compatibility_threshold: float (default: 0.7)
  out_of_box_probability: float (default: 0.2)
  simplification_aggressiveness: float (default: 0.5)
  parallel_evolutions: int (default: 4)
}
```

## Examples

### Drug Mechanism Enhancement
```
Parent: "KIRA6 might help in AML through stress pathways"
Strategy: Enhancement through grounding
Evolution: "KIRA6 selectively inhibits IRE1α kinase activity, preventing XBP1 splicing and inducing AML cell apoptosis through ER stress amplification, with IC50 of 13nM in KG-1 cells"
```

### Hypothesis Combination for Liver Fibrosis
```
Parent 1: "Target epigenetic regulators in hepatic stellate cells"
Parent 2: "Inhibit TGF-β signaling in fibroblasts"
Strategy: Combination
Evolution: "Dual targeting of BRD4 and TGF-β receptor creates synergistic anti-fibrotic effect by simultaneously blocking epigenetic activation and pro-fibrotic signaling"
```

### Simplification for Testing
```
Parent: "Complex multi-target intervention with 8 components"
Strategy: Simplification
Evolution: "Focus on top 2 synergistic targets (HDAC6 and BRD4) for initial validation with clear readouts"
```

## Boundaries

**What the Evolution Agent Does**:
- Creates new, improved versions of existing hypotheses
- Employs multiple refinement strategies adaptively
- Grounds improvements in scientific literature
- Maintains hypothesis quality through non-destructive refinement
- Enables iterative improvement through tournaments

**What the Evolution Agent Does Not Do**:
- Modify original hypotheses (preserves them intact)
- Generate hypotheses from scratch (Generation Agent's role)
- Evaluate hypothesis quality (Reflection Agent's role)
- Determine evolution priorities (Supervisor's role)
- Guarantee improvements (must prove worth in tournaments)