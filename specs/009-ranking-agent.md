# Ranking Agent Specification

**Type**: Agent  
**Interactions**: Supervisor Agent, Context Memory, Proximity Agent  
**Prerequisites**: 
- Read: 007-generation-agent.md
- Read: 008-reflection-agent.md  
- Read: 011-proximity-agent.md (when available)
- Understand: Elo rating system concepts

## Overview

The Ranking Agent evaluates and prioritizes hypotheses through a tournament-based comparison system. It maintains Elo ratings for all hypotheses and conducts pairwise comparisons to determine relative scientific merit based on novelty, correctness, and testability.

## Core Behaviors

### Tournament Management
- Maintains an Elo-based rating system for all hypotheses
- Organizes pairwise hypothesis comparisons
- Prioritizes matches between similar hypotheses using proximity data
- Updates ratings based on comparison outcomes

### Scientific Debate Simulation
- Conducts multi-turn scientific debates for top-ranked hypotheses
- Performs single-turn comparisons for lower-ranked hypotheses
- Evaluates debates based on scientific merit criteria
- Generates structured debate outcomes with rationale

### Rating Maintenance
- Assigns initial Elo rating of 1200 to new hypotheses
- Updates ratings after each comparison using standard Elo formulas
- Maintains win/loss records for each hypothesis
- Tracks tournament participation history

## Inputs

### From Supervisor Agent
```
Input Structure:
  - task_type: "evaluate_hypotheses"
  - hypotheses_to_rank: List[hypothesis_id]
  - tournament_config:
    - max_comparisons: integer (resource limit)
    - debate_depth: "multi_turn" | "single_turn"
    - priority_threshold: float (Elo rating for multi-turn debates)
  - context_requirements:
    - include_proximity: boolean
    - include_reviews: boolean
```

### From Context Memory
```
Retrieved Data:
  - hypothesis_pool:
    - hypothesis_id: string
    - current_elo: float
    - win_count: integer
    - loss_count: integer
    - last_evaluated: timestamp
    - content: hypothesis details
  - tournament_state:
    - active_matches: List[match_id]
    - completed_matches: List[match_result]
```

### From Proximity Agent
```
Similarity Data:
  - similarity_graph:
    - hypothesis_pairs: List[{h1_id, h2_id, similarity_score}]
  - clusters:
    - cluster_id: string
    - member_hypotheses: List[hypothesis_id]
```

## Outputs

### Tournament Results
```
Output Structure:
  - updated_ratings:
    - hypothesis_id: string
    - new_elo: float
    - previous_elo: float
    - matches_played: integer
  - match_results:
    - match_id: string
    - hypothesis_1: hypothesis_id
    - hypothesis_2: hypothesis_id
    - winner: hypothesis_id
    - debate_summary: string
    - decision_rationale: string
```

### Ranking Report
```
Ranking Structure:
  - ranked_hypotheses: List[
      - rank: integer
      - hypothesis_id: string
      - elo_rating: float
      - win_rate: float
      - key_strengths: List[string]
    ]
  - tournament_metadata:
    - total_matches: integer
    - convergence_metric: float
    - computation_time: duration
```

## Behavioral Contracts

### Tournament Execution
- MUST compare each hypothesis at least once when resources allow
- MUST use proximity data to prioritize similar hypothesis comparisons
- MUST apply multi-turn debates only for hypotheses above priority_threshold
- MUST update Elo ratings immediately after each match
- MUST NOT compare a hypothesis against itself

### Scientific Evaluation
- MUST evaluate based on novelty, correctness, and testability
- MUST generate debate content that reflects scientific discourse
- MUST provide clear rationale for each comparison outcome
- SHOULD mitigate ordering bias through structured debate format
- SHOULD ensure consistent evaluation criteria across all matches

### Rating System
- MUST initialize new hypotheses with Elo rating of 1200
- MUST use standard Elo K-factor (typically 32) for rating updates
- MUST maintain monotonic consistency in rankings
- MUST preserve rating history for audit purposes

## Interaction Protocols

### With Supervisor Agent
```
1. Receive evaluation task with hypothesis list
2. Acknowledge task and estimate completion time
3. Report progress at 25%, 50%, 75% completion
4. Submit final rankings with full tournament results
5. Update task status to "completed"
```

### With Context Memory
```
1. Query current hypothesis pool and ratings
2. Lock hypotheses being evaluated
3. Write match results after each comparison
4. Update Elo ratings atomically
5. Release locks after evaluation
```

### With Proximity Agent
```
1. Request similarity graph for hypothesis set
2. Use similarity scores to create match priority queue
3. Prefer matches between hypotheses with similarity > 0.7
4. Fall back to random matching if no similar pairs available
```

## Examples

### Example 1: Multi-turn Scientific Debate
```
Input:
  - Hypothesis A: "CRISPR-edited T cells targeting CD19/CD22 dual antigens"
  - Hypothesis B: "CAR-T cells with synthetic Notch receptors for tumor specificity"
  - Current Elo: A=1450, B=1425
  - Debate type: multi_turn

Process:
  Round 1: Opening statements highlighting key innovations
  Round 2: Cross-examination of feasibility and safety
  Round 3: Evidence presentation from literature
  Round 4: Final arguments on clinical impact

Output:
  - Winner: Hypothesis A
  - New Elo: A=1466, B=1409
  - Rationale: "Superior safety profile and established clinical precedent"
```

### Example 2: Tournament Organization
```
Input:
  - 10 new hypotheses for liver fibrosis treatment
  - Max comparisons: 20
  - Priority threshold: 1300

Process:
  1. Query proximity agent for similarity clusters
  2. Create priority queue: similar pairs > high-rated > new
  3. Conduct 15 single-turn comparisons
  4. Conduct 5 multi-turn debates for top hypotheses
  5. Update all Elo ratings

Output:
  - Top 3 hypotheses with Elo > 1250
  - Complete ranking of all 10 hypotheses
  - Tournament efficiency: 0.85 (information gain per match)
```

### Example 3: Bias Mitigation
```
Scenario: Comparing two antimicrobial resistance hypotheses

Approach:
  - Hypothesis order randomized in debate
  - Evaluation criteria explicitly stated upfront
  - Both hypotheses argue from strengths first
  - Symmetric rebuttal opportunities
  - Decision based on predefined rubric
```

## Performance Characteristics

### Computational Efficiency
- Single-turn comparison: ~30 seconds
- Multi-turn debate: ~2-3 minutes  
- Full tournament (100 hypotheses): ~20-30 minutes
- Scales as O(n log n) with hypothesis count

### Quality Metrics
- Ranking stability: >0.9 correlation after 3n comparisons
- Inter-rater agreement: >0.85 with human expert rankings
- Bias detection: <0.1 correlation with hypothesis order
- Convergence rate: Elo ratings stabilize within 5 rounds

### Resource Usage
- LLM calls: 2-8 per comparison depending on debate depth
- Memory: O(n²) for similarity matrix, O(n) for ratings
- Concurrent matches: Up to 10 parallel evaluations
- State persistence: After every 5 matches