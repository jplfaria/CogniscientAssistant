# Tournament and Elo Rating System Specification

**Type**: System  
**Interactions**: Ranking Agent, Context Memory System, Proximity Agent, Meta-review Agent, Supervisor Agent

## Prerequisites
- Read: Ranking Agent Specification
- Read: Context Memory System Specification
- Read: Proximity Agent Specification
- Understand: Elo rating system concepts

## Purpose
The Tournament and Elo Rating System provides a competitive evaluation framework for scientific hypotheses, enabling efficient prioritization of research directions through pairwise comparisons and progressive quality improvement. The system establishes relative rankings among potentially hundreds of hypotheses while optimizing computational resources.

## Tournament System Behavior
1. Manages pairwise hypothesis comparisons through structured tournaments
2. Maintains Elo ratings as quality proxies for all hypotheses
3. Optimizes computational resources through tiered debate protocols
4. Tracks win-loss patterns for system improvement
5. Prioritizes matches based on similarity, recency, and ranking tiers
6. Generates tournament progress statistics and performance metrics
7. Enables self-improving feedback loops through pattern analysis

## Inputs

### Tournament Configuration
```
TournamentConfig:
  initial_elo_rating: int (default: 1200)
  k_factor: float (default: 32.0)
  multi_turn_threshold: int (default: 1400, Elo rating for multi-turn debates)
  match_batch_size: int (default: 10, matches per round)
  similarity_weight: float (default: 0.3, weight for proximity-based matching)
  recency_weight: float (default: 0.2, weight for newer hypotheses)
  rating_proximity_weight: float (default: 0.5, weight for similar-rated opponents)
```

### Match Request
```
MatchRequest:
  hypothesis_id: string
  current_elo: int
  creation_timestamp: datetime
  similarity_graph_id: string (reference to Proximity Agent data)
  priority: string (high|medium|low)
```

### Debate Outcome
```
DebateOutcome:
  match_id: string
  hypothesis_a_id: string
  hypothesis_b_id: string
  winner_id: string
  debate_type: string (multi_turn|single_turn)
  debate_summary: string
  evaluation_criteria: List[CriterionScore]
    - criterion: string (novelty|correctness|testability|merit)
    - score_a: float (0.0-1.0)
    - score_b: float (0.0-1.0)
```

## Outputs

### Elo Update
```
EloUpdate:
  hypothesis_id: string
  old_rating: int
  new_rating: int
  rating_change: int
  match_id: string
  timestamp: datetime
```

### Tournament Round Results
```
TournamentRoundResults:
  round_id: string
  matches_completed: int
  average_rating_change: float
  top_performers: List[HypothesisRanking]
    - hypothesis_id: string
    - current_elo: int
    - matches_played: int
    - win_rate: float
  computational_cost: ResourceMetrics
```

### Win-Loss Pattern Analysis
```
PatternAnalysis:
  winning_characteristics: List[string]
  losing_characteristics: List[string]
  debate_topic_trends: List[string]
  recommendation_for_generation: string
  confidence: float (0.0-1.0)
```

## Core Tournament Mechanics

### Match Selection Algorithm
The system selects matches through a weighted scoring function:
1. Calculates similarity scores from the Proximity Agent's graph
2. Applies recency bonus for newer hypotheses
3. Considers rating proximity to ensure competitive matches
4. Balances exploration (new hypotheses) with exploitation (validating top performers)

### Elo Rating Calculation
Standard Elo rating formula with scientific domain adaptations:
- Initial rating: 1200 for all new hypotheses
- K-factor: Configurable (default 32) for rating volatility
- Expected score calculation considers debate quality metrics
- Rating floors and ceilings to prevent extreme values

### Debate Protocol Selection
- **Multi-turn debates**: For hypotheses with Elo > 1400
  - Multiple rounds of scientific argumentation
  - Detailed evaluation across all criteria
  - Higher computational cost, higher decision confidence
- **Single-turn comparisons**: For lower-rated hypotheses
  - Quick evaluation focused on key differentiators
  - Efficient resource utilization
  - Enables broader hypothesis coverage

## Integration Patterns

### With Ranking Agent
- Ranking Agent requests tournament rounds through the Supervisor
- Tournament system provides match schedules and protocols
- Ranking Agent executes debates and returns outcomes
- Tournament system updates Elo ratings and provides new rankings

### With Context Memory System
- Stores complete tournament history
- Maintains current Elo ratings for all hypotheses
- Tracks match outcomes and debate summaries
- Provides historical data for pattern analysis

### With Proximity Agent
- Queries similarity scores for hypothesis pairs
- Uses clustering information for match selection
- Ensures diverse tournament brackets

### With Meta-review Agent
- Provides win-loss pattern analyses
- Receives synthesized insights about effective hypothesis characteristics
- Contributes to system-wide improvement feedback

## Tournament State Management

### Active Tournament State
```
TournamentState:
  current_round: int
  active_matches: List[MatchID]
  pending_matches: Queue[MatchRequest]
  hypothesis_ratings: Map[HypothesisID, EloRating]
  round_statistics: RoundStats
```

### Historical Tournament Data
```
TournamentHistory:
  completed_rounds: List[TournamentRoundResults]
  all_matches: List[DebateOutcome]
  rating_progression: Map[HypothesisID, List[EloUpdate]]
  pattern_analyses: List[PatternAnalysis]
```

## Performance Optimization

### Resource Allocation Strategy
1. Prioritizes top-tier hypotheses for thorough evaluation
2. Batches lower-tier comparisons for efficiency
3. Dynamically adjusts debate depth based on system load
4. Monitors computational budget per tournament round

### Convergence Criteria
- Tracks rating stability over rounds
- Identifies when rankings have stabilized
- Signals when additional tournaments provide diminishing returns
- Enables efficient termination decisions

## Error Handling

### Common Scenarios
1. **Incomplete Debates**: Stores partial results, flags for retry
2. **Rating Calculation Errors**: Validates rating changes, prevents corruption
3. **Timeout Handling**: Enforces time limits, declares draws if necessary
4. **Invalid Match Requests**: Validates hypothesis existence and eligibility

### Recovery Mechanisms
- Automatic retry for failed matches
- Rating rollback for corrupted updates
- Graceful degradation to single-turn debates under high load
- Match rescheduling for unavailable hypotheses

## Quality Metrics

### Tournament Effectiveness
```
EffectivenessMetrics:
  rating_convergence_rate: float
  top_10_stability: float (how often top 10 changes)
  computational_efficiency: float (decisions per compute unit)
  correlation_with_ground_truth: float (when available)
```

### System Health Indicators
- Average matches per hypothesis
- Rating distribution statistics
- Debate quality scores
- Pattern identification confidence

## Configuration Parameters

```
TournamentSystemConfig:
  tournament_parameters: TournamentConfig
  scheduling:
    rounds_per_session: int (default: 10)
    matches_per_round: int (default: 50)
    timeout_per_match: int (seconds, default: 300)
  optimization:
    min_matches_for_confidence: int (default: 5)
    rating_stability_threshold: float (default: 0.95)
    resource_budget_per_round: float (compute units)
  pattern_analysis:
    min_matches_for_analysis: int (default: 100)
    pattern_confidence_threshold: float (default: 0.7)
```

## Examples

### Example Tournament Round
```
Round 7 initiated with 150 active hypotheses:
- 15 multi-turn debates for hypotheses rated 1400+
- 35 single-turn comparisons for emerging hypotheses
- Focus on "drug repurposing for neurodegenerative diseases" cluster
- Average rating change: ±28 points
- Top performer: Hypothesis-042 (1456 → 1512)
- Computational cost: 847 units
```

### Example Pattern Analysis
```
After 500 matches analyzed:
- Winning characteristics: 
  - Clear experimental protocols
  - Novel molecular targets
  - Strong preliminary evidence citations
- Losing characteristics:
  - Vague success metrics
  - Limited testability
  - Overcomplicated mechanisms
- Recommendation: Emphasize protocol clarity in generation
- Confidence: 0.82
```

## Boundaries

**What the Tournament System Does**:
- Manages hypothesis competitions through structured tournaments
- Maintains and updates Elo ratings based on debate outcomes
- Optimizes match selection for efficient evaluation
- Generates insights from competition patterns
- Provides ranking stability metrics

**What the Tournament System Does Not Do**:
- Execute the actual scientific debates (Ranking Agent's responsibility)
- Generate new hypotheses (Generation Agent's responsibility)
- Make final research decisions (human expert's responsibility)
- Modify hypothesis content (Evolution Agent's responsibility)
- Store hypothesis details (Context Memory's responsibility)