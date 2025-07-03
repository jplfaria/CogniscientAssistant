# Ranking Agent Specification

**Type**: Agent  
**Interactions**: Supervisor Agent, Context Memory, Proximity Agent, Reflection Agent, Meta-review Agent

## Prerequisites
- Read: System Overview and Architecture Specification
- Read: Multi-Agent Framework Specification
- Read: Context Memory System Specification
- Read: Reflection Agent Specification

## Purpose

The Ranking Agent evaluates and prioritizes hypotheses through an Elo-based tournament system, conducting scientific debates to determine relative merit. It ensures computational resources focus on the most promising research directions by maintaining a dynamic ranking that reflects hypothesis quality across multiple dimensions.

## Agent Behavior

The Ranking Agent exhibits the following behaviors:

1. **Tournament Organization**: Manages pairwise hypothesis comparisons using an Elo rating system
2. **Scientific Debate Facilitation**: Conducts multi-turn debates between competing hypotheses
3. **Strategic Match Selection**: Optimizes tournament brackets based on similarity and ranking
4. **Dynamic Rating Maintenance**: Updates Elo scores based on tournament outcomes
5. **Resource-Aware Prioritization**: Allocates comparison depth based on hypothesis quality
6. **Performance Pattern Analysis**: Tracks win-loss trends for system improvement

## Inputs

### From Task Assignment
```
RankingTask {
  task_type: NewHypothesis | TournamentRound | GlobalRanking
  hypothesis_ids: list[string]
  tournament_parameters: TournamentConfig
  priority: int
  context: dict (optional)
}
```

### From Context Memory
```
HypothesisSet {
  hypotheses: list[Hypothesis]
  current_ratings: dict[hypothesis_id, EloRating]
  tournament_history: list[MatchResult]
  review_scores: dict[hypothesis_id, ReviewScore]
}
```

### From Proximity Agent
```
SimilarityGraph {
  similarity_matrix: dict[tuple[id, id], float]
  clusters: list[HypothesisCluster]
  recommended_matches: list[tuple[id, id]]
}
```

## Outputs

### Elo Rating Update
```
EloUpdate {
  hypothesis_id: string
  previous_rating: int
  new_rating: int
  match_count: int
  win_rate: float
  confidence_interval: tuple[int, int]
}
```

### Tournament Match Result
```
MatchResult {
  id: string
  hypothesis_a_id: string
  hypothesis_b_id: string
  winner_id: string
  debate_type: MultiTurn | SingleTurn
  debate_transcript: list[DebateTurn]
  decision_rationale: string
  criteria_scores: dict[Criterion, Comparison]
  timestamp: datetime
}
```

### Global Ranking
```
RankingReport {
  ranked_hypotheses: list[RankedHypothesis]
  rating_distribution: dict
  top_performers: list[hypothesis_id]
  emerging_candidates: list[hypothesis_id]
  performance_trends: dict
}

RankedHypothesis {
  hypothesis_id: string
  rank: int
  elo_rating: int
  match_record: WinLossRecord
  recent_form: list[MatchResult]
}
```

## Tournament Mechanics

### Elo Rating System

**Initial Configuration**:
- New hypotheses start with rating: 1200
- K-factor: 32 (determines rating volatility)
- Expected score calculation: E = 1 / (1 + 10^((Rb - Ra) / 400))
- Rating update: R_new = R_old + K * (S - E)

**Rating Brackets**:
```
Elite: > 1600
Strong: 1400-1600
Average: 1100-1400
Developing: 900-1100
New: 1200 (starting)
```

### Match Selection Algorithm

**Priority Factors**:
1. **Similarity Score**: Prefer matches between related hypotheses
2. **Rating Proximity**: Match hypotheses with similar Elo ratings
3. **Match Freshness**: Prioritize new hypotheses for evaluation
4. **Activity Balance**: Ensure all hypotheses receive matches

**Selection Process**:
```
MatchSelection {
  candidate_pool: FilterByActivity(all_hypotheses)
  similarity_boost: GetSimilarityWeights(proximity_graph)
  rating_factor: CalculateRatingProximity(candidates)
  priority_score: CombineFactors(similarity, rating, freshness)
  selected_match: SelectTopPair(priority_scores)
}
```

### Debate Protocols

#### Multi-Turn Scientific Debate (Top Hypotheses)

**Structure**:
- Rounds: 3-5 turns per participant
- Opening statements from each hypothesis
- Point-counterpoint exchanges
- Closing arguments
- Judge's decision with rationale

**Debate Flow**:
```
DebateTurn {
  speaker: HypothesisA | HypothesisB | Judge
  content: string
  claims: list[ScientificClaim]
  rebuttals: list[Rebuttal] (optional)
  evidence_cited: list[Citation] (optional)
}
```

**Evaluation Dimensions**:
1. **Novelty**: Advancement beyond existing knowledge
2. **Correctness**: Scientific validity and logical consistency
3. **Testability**: Feasibility of experimental validation
4. **Impact**: Potential scientific contribution
5. **Clarity**: Quality of argumentation

#### Single-Turn Comparison (Lower-Ranked Hypotheses)

**Structure**:
- Direct side-by-side comparison
- Summary of key strengths/weaknesses
- Quick decision based on primary criteria
- Brief rationale

## Ranking Strategies

### Dynamic Bracket Management

**Elite Tier Strategy**:
- Frequent high-stakes matches
- Multi-turn debates mandatory
- Cross-cluster competitions
- Defending champion challenges

**Development Tier Strategy**:
- Rapid evaluation cycles
- Single-turn comparisons
- Within-cluster matches preferred
- Promotion opportunities emphasized

### Rating Confidence

**Confidence Calculation**:
```
Confidence {
  match_count: int
  rating_stability: float (recent rating variance)
  opponent_diversity: float (variety of opponents faced)
  confidence_score: float (0.0 - 1.0)
}
```

**Minimum Match Requirements**:
- 5 matches for initial confidence
- 10 matches for stable rating
- 20 matches for high confidence

## Performance Optimization

### Resource Allocation

**Computational Budget Distribution**:
- Elite matches: 40% of debate compute
- Strong tier: 30% of debate compute
- Average tier: 20% of debate compute
- Development tier: 10% of debate compute

**Batch Processing**:
- Parallel match execution where possible
- Grouped evaluations by tier
- Asynchronous rating updates
- Cached debate templates

### Tournament Efficiency

**Early Stopping Conditions**:
- Clear winner emerges (rating gap > 400)
- Hypothesis repeatedly loses (5 consecutive losses)
- Stagnant ratings (no change over 10 matches)

**Acceleration Techniques**:
- Fast-track promising newcomers
- Skip redundant matchups
- Use historical patterns for predictions
- Compress debates for clear disparities

## Quality Assurance

### Bias Mitigation

**Ordering Effects**:
- Randomize presentation order in debates
- Alternate starting positions
- Use symmetric evaluation criteria
- Apply position-based corrections

**Recency Bias**:
- Normalize for hypothesis age
- Weight recent performance appropriately
- Maintain historical context
- Balance exploration vs exploitation

### Consistency Checks

**Rating Validation**:
- Transitivity tests (if A > B and B > C, verify A > C)
- Circular dependency detection
- Outlier identification
- Cross-validation with review scores

**Debate Quality**:
- Argument coherence verification
- Evidence grounding checks
- Decision rationale completeness
- Criteria application consistency

## State Management

### Read Operations
- Query current rankings and ratings
- Access tournament history
- Retrieve similarity recommendations
- Check hypothesis review scores

### Write Operations
- Update Elo ratings after matches
- Store complete debate transcripts
- Record match results and decisions
- Log performance patterns

## Integration Patterns

### With Proximity Agent
- Request similarity-based match recommendations
- Access hypothesis clustering information
- Coordinate cross-cluster tournaments
- Share ranking-based proximity insights

### With Reflection Agent
- Incorporate review scores in initial seeding
- Use review feedback to break ranking ties
- Validate tournament decisions against reviews
- Identify ranking-review discrepancies

### With Meta-review Agent
- Provide tournament performance patterns
- Share win-loss trend analysis
- Highlight consistent winners/losers
- Support meta-learning insights

### With Supervisor Agent
- Receive tournament scheduling tasks
- Report ranking updates
- Signal resource requirements
- Provide prioritized hypothesis lists

## Error Handling

### Common Scenarios

1. **Incomplete Hypotheses**
   - Skip from tournament
   - Flag for completion
   - Assign provisional rating
   - Queue for later evaluation

2. **Debate Generation Failures**
   - Retry with simpler format
   - Fall back to direct comparison
   - Use cached similar debates
   - Apply default decision rules

3. **Rating Anomalies**
   - Detect sudden rating spikes/drops
   - Investigate match irregularities
   - Apply smoothing algorithms
   - Request manual review if needed

4. **Resource Constraints**
   - Reduce debate depth
   - Prioritize critical matches
   - Defer lower-tier tournaments
   - Implement rating decay for inactive hypotheses

## Performance Metrics

The Ranking Agent's effectiveness is measured by:

1. **Rating Accuracy**: Correlation with downstream success
2. **Tournament Efficiency**: Matches to stable ranking
3. **Debate Quality**: Argument depth and validity
4. **System Concordance**: Agreement with human rankings
5. **Computational Efficiency**: Rankings per compute hour
6. **Predictive Power**: Early identification of winners

## Configuration Parameters

```
RankingConfig {
  initial_elo: int (default: 1200)
  k_factor: int (default: 32)
  debate_rounds: dict[Tier, int]
  min_matches_for_stability: int (default: 10)
  similarity_weight: float (default: 0.3)
  recency_weight: float (default: 0.2)
  elite_threshold: int (default: 1600)
  tournament_batch_size: int (default: 20)
  enable_fast_track: bool (default: true)
}
```

## Examples

### Elite Tier Match
```
Hypothesis A: "KIRA6 for AML treatment" (Elo: 1650)
Hypothesis B: "BET inhibitor combinations" (Elo: 1620)
Debate Type: 5-turn scientific debate
Winner: Hypothesis A
Rating Change: A: 1650 → 1665, B: 1620 → 1605
Rationale: "Superior mechanistic understanding and clearer path to clinical translation"
```

### Fast-Track Success
```
New Hypothesis: "Viral vector for cf-PICI spread" (Elo: 1200)
Match Record: Won 5 of first 6 matches
Fast-Track: Promoted directly to Strong tier
New Rating: 1425
Next: Scheduled for elite challenger match
```

## Boundaries

**What the Ranking Agent Does**:
- Organizes and executes hypothesis tournaments
- Maintains dynamic Elo-based rankings
- Facilitates scientific debates between hypotheses
- Optimizes computational resource allocation
- Provides prioritized lists for decision-making

**What the Ranking Agent Does Not Do**:
- Generate new hypotheses (Generation Agent's role)
- Evaluate individual hypothesis quality (Reflection Agent's role)
- Modify or improve hypotheses (Evolution Agent's role)
- Make final selection decisions (Scientist's role)
- Execute research experiments (External validation)