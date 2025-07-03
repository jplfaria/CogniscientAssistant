# Evaluation Metrics Specification

**Type**: System-wide Process Specification  
**Components**: All Agents, Context Memory, Meta-review Agent, Natural Language Interface

## Prerequisites
- Read: Ranking Agent Specification
- Read: Review Types and Processes Specification
- Read: Tournament and Elo Rating System Specification
- Read: Meta-review Agent Specification
- Understand: Scientific hypothesis quality assessment concepts

## Purpose

This specification defines the comprehensive evaluation metrics used throughout the AI Co-Scientist system to assess hypothesis quality, system performance, and research effectiveness. These metrics ensure objective measurement of scientific progress, enable continuous improvement, and provide transparency for human experts.

## Core Evaluation Framework

### Multi-Dimensional Assessment

The system evaluates hypotheses and research outputs across multiple independent dimensions, each contributing to an overall quality assessment. No single metric dominates; instead, the system synthesizes multiple signals to form comprehensive evaluations.

### Temporal Evolution Tracking

All metrics track changes over time, enabling the system to measure improvement, identify trends, and validate the effectiveness of the evolutionary process.

### Human-AI Concordance

Metrics are designed to align with human expert judgment while providing objective, reproducible measurements that exceed human consistency.

## Primary Evaluation Metrics

### 1. Elo Rating System

**Metric Type**: Dynamic competitive ranking  
**Range**: 900-1700+ (typical operational range)  
**Initial Value**: 1200 for new hypotheses

**Calculation Method**:
```
EloMetric {
  current_rating: int
  match_history: list[MatchResult]
  k_factor: int (default: 32)
  confidence_interval: tuple[int, int]
  
  update(match_result: MatchResult) -> int
  get_expected_score(opponent_rating: int) -> float
  calculate_confidence() -> tuple[int, int]
}
```

**Quality Indicators**:
- Rating > 1600: Exceptional quality
- Rating 1400-1600: High quality
- Rating 1200-1400: Standard quality
- Rating < 1200: Needs improvement

**Validation**: Positive correlation with GPQA benchmark accuracy demonstrates metric validity

### 2. Review Quality Scores

**Metric Type**: Multi-criteria assessment  
**Components**: Correctness, Novelty, Testability, Safety, Impact

**Assessment Structure**:
```
ReviewScore {
  correctness: float (0.0-1.0)
  novelty: float (0.0-1.0)
  testability: float (0.0-1.0)
  safety: float (0.0-1.0)
  impact: float (0.0-1.0)
  
  overall_score: float (weighted average)
  confidence: float (0.0-1.0)
  evidence_quality: float (0.0-1.0)
}
```

**Dimension Definitions**:

- **Correctness**: Scientific accuracy, logical consistency, grounding in established knowledge
- **Novelty**: Advancement beyond existing literature, unique insights, creative connections
- **Testability**: Experimental feasibility, clear predictions, measurable outcomes
- **Safety**: Ethical compliance, risk assessment, responsible research practices
- **Impact**: Potential scientific contribution, field advancement, practical applications

### 3. Literature Grounding Metrics

**Metric Type**: Evidence quality assessment  
**Measurement Approach**: Citation analysis and reference validation

**Grounding Indicators**:
```
GroundingMetrics {
  citation_count: int
  citation_quality: float (journal impact factors)
  citation_relevance: float (semantic similarity)
  citation_recency: float (publication date weighting)
  citation_diversity: float (source variety)
  
  unsupported_claims: list[Claim]
  grounding_score: float (0.0-1.0)
}
```

**Quality Thresholds**:
- Strong grounding: > 10 relevant citations, quality > 0.7
- Adequate grounding: 5-10 citations, quality > 0.5
- Weak grounding: < 5 citations or quality < 0.5

### 4. Evolutionary Progress Metrics

**Metric Type**: Improvement tracking  
**Measurement Focus**: Quality enhancement through iterations

**Progress Indicators**:
```
EvolutionMetrics {
  generation_number: int
  parent_elo: int
  current_elo: int
  improvement_rate: float
  
  enhancement_success_rate: float
  combination_novelty_score: float
  simplification_clarity_gain: float
  out_of_box_creativity_score: float
}
```

**Success Criteria**:
- Positive improvement rate over 3+ generations
- Enhancement success rate > 0.6
- Maintained or improved safety scores

### 5. Tournament Performance Metrics

**Metric Type**: Competitive assessment  
**Measurement Approach**: Win-loss analysis and debate quality

**Performance Tracking**:
```
TournamentMetrics {
  total_matches: int
  win_rate: float
  wins_against_higher_rated: int
  losses_against_lower_rated: int
  
  debate_quality_scores: list[float]
  argument_coherence: float
  rebuttal_effectiveness: float
  evidence_usage_score: float
}
```

**Performance Categories**:
- Elite performer: Win rate > 0.7 against similar ratings
- Strong performer: Win rate 0.5-0.7
- Developing: Win rate 0.3-0.5
- Needs improvement: Win rate < 0.3

## System Performance Metrics

### 1. Hypothesis Generation Efficiency

**Measurement Focus**: Quality vs computational resource usage

**Efficiency Indicators**:
```
GenerationEfficiency {
  hypotheses_per_hour: float
  quality_per_compute_hour: float (average Elo / compute hours)
  novel_hypotheses_rate: float
  safety_pass_rate: float
  iteration_improvement_curve: list[float]
}
```

### 2. Review Consistency Metrics

**Measurement Focus**: Reliability and reproducibility of evaluations

**Consistency Tracking**:
```
ReviewConsistency {
  inter_review_agreement: float (correlation between review types)
  temporal_stability: float (same hypothesis reviewed over time)
  human_ai_concordance: float
  false_positive_rate: float
  false_negative_rate: float
}
```

### 3. Research Goal Achievement

**Measurement Focus**: Alignment with user objectives

**Achievement Assessment**:
```
GoalAchievement {
  goal_relevance_score: float
  comprehensive_coverage: float
  actionable_output_rate: float
  user_satisfaction_rating: float (when available)
  experimental_validation_rate: float
}
```

## Meta-Level Evaluation Metrics

### 1. System Learning Rate

**Measurement Focus**: Improvement over time across sessions

**Learning Indicators**:
```
SystemLearning {
  average_quality_trend: list[float]
  error_reduction_rate: float
  pattern_recognition_improvement: float
  novel_approach_discovery_rate: float
}
```

### 2. Research Impact Potential

**Measurement Focus**: Predicted real-world significance

**Impact Assessment**:
```
ImpactMetrics {
  citation_potential_score: float
  clinical_relevance_score: float (for medical research)
  technological_readiness_level: int (1-9)
  societal_benefit_score: float
  economic_impact_estimate: float
}
```

## Human Expert Evaluation Integration

### Expert Rating Collection

**Interface for Expert Feedback**:
```
ExpertEvaluation {
  hypothesis_id: string
  expert_id: string
  
  ratings: {
    novelty: int (1-5)
    impact: int (1-5)
    feasibility: int (1-5)
    correctness: int (1-5)
  }
  
  qualitative_feedback: string
  would_pursue: boolean
  comparison_rank: int (relative to other hypotheses)
}
```

### Human-AI Correlation Metrics

**Correlation Tracking**:
- Pearson correlation between AI and expert rankings
- Agreement rate on top-10 selections
- Divergence analysis for improvement insights

## Validation Benchmark Metrics

### Real-World Validation Tracking

**Success Case Metrics** (from paper examples):

1. **Drug Repurposing Validation**
   - Time to identification: hours vs months
   - Experimental confirmation: IC50 values
   - Clinical relevance: therapeutic window assessment

2. **Target Discovery Validation**
   - Novel targets identified: count
   - Experimental validation rate: percentage
   - Statistical significance: p-values

3. **Mechanism Discovery Validation**
   - Independent discovery confirmation
   - Time advantage: days vs years
   - Completeness of mechanism description

### Simplified Validation Metrics

**For System Testing**:
```
ValidationMetrics {
  known_fact_rediscovery_rate: float
  literature_consistency_score: float
  logical_coherence_rating: float
  testable_prediction_rate: float
}
```

## Metric Aggregation and Reporting

### Dashboard Metrics

**Real-Time Monitoring**:
```
DashboardMetrics {
  current_session: {
    active_hypotheses: int
    average_elo: float
    top_hypothesis_elo: int
    generation_rate: float
    review_backlog: int
  }
  
  historical_trends: {
    quality_improvement: float
    efficiency_gains: float
    safety_record: float
  }
}
```

### Research Summary Metrics

**End-of-Session Report**:
```
ResearchSummary {
  total_hypotheses_generated: int
  top_10_hypotheses: list[HypothesisSummary]
  
  quality_distribution: {
    elite: int
    high_quality: int
    standard: int
    rejected: int
  }
  
  key_insights: list[string]
  recommended_next_steps: list[string]
  
  computational_summary: {
    total_compute_hours: float
    efficiency_score: float
  }
}
```

## Metric Quality Assurance

### Metric Validation

**Validation Approaches**:
- Cross-validation with held-out data
- A/B testing of metric variations
- Expert panel metric audits
- Correlation with downstream success

### Metric Calibration

**Calibration Process**:
```
MetricCalibration {
  collect_ground_truth() -> list[GroundTruth]
  calculate_metric_accuracy() -> float
  identify_biases() -> list[Bias]
  adjust_weights() -> MetricConfig
  validate_adjustments() -> bool
}
```

## Configuration and Customization

### Metric Weight Configuration

```
MetricConfiguration {
  elo_weight: float (default: 0.3)
  review_weight: float (default: 0.3)
  grounding_weight: float (default: 0.2)
  evolution_weight: float (default: 0.1)
  safety_weight: float (default: 0.1)
  
  domain_specific_weights: map[Domain, WeightConfig]
  
  quality_thresholds: {
    minimum_acceptable: float
    publication_ready: float
    breakthrough_potential: float
  }
}
```

### Custom Metric Definition

**Extension Interface**:
```
CustomMetric {
  name: string
  description: string
  
  calculate(hypothesis: Hypothesis, context: Context) -> float
  aggregate(scores: list[float]) -> float
  visualize(scores: list[float]) -> Visualization
}
```

## Performance Requirements

### Computation Targets
- Elo update calculation: < 100ms
- Review score computation: < 1 second
- Full metric dashboard update: < 5 seconds
- Validation metric batch: < 30 seconds

### Accuracy Requirements
- Human-AI correlation: > 0.7
- Metric stability: < 5% variance on recomputation
- Predictive validity: > 0.8 for downstream success

## Natural Language Examples

### Metric Reporting
System: "The top hypothesis achieved an Elo rating of 1,654 after winning 8 of 10 tournament matches. It scores 0.89 for novelty, 0.92 for correctness, and 0.86 for testability. The hypothesis shows strong grounding with 23 relevant citations from high-impact journals."

### Progress Update
System: "After 3 evolutionary cycles, hypothesis quality improved by 23%. The average Elo rating increased from 1,287 to 1,582. The system generated 156 hypotheses with a 94% safety pass rate."

### Expert Correlation
System: "Expert evaluations show 0.82 correlation with system rankings. Experts rated the top AI-selected hypothesis 4.2/5 for novelty and 3.8/5 for impact. The system successfully identified 9 of 10 expert-preferred hypotheses."

## Future Metric Enhancements

### Planned Improvements
- Causal impact estimation metrics
- Reproducibility prediction scores
- Collaboration potential metrics
- Resource requirement estimates
- Long-term impact tracking
- Cross-domain generalization metrics
- Uncertainty quantification
- Bias detection and mitigation metrics