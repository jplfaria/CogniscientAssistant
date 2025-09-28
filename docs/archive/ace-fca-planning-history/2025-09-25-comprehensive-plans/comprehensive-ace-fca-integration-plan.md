# Comprehensive ACE-FCA Integration Plan
*CogniscientAssistant Development Loop and Agent Framework Enhancement*

> Generated: September 25, 2025
> Status: Ready for Implementation
> Consolidates: Context Relevance Scoring, BAML Compression, Context Effectiveness Tracking
> Adds: Human Collaboration Patterns, Semantic Agent Tools

## Executive Summary

This comprehensive plan integrates ACE-FCA (Advanced Context Engineering - Frequent Intentional Compaction) principles into the CogniscientAssistant project to achieve:

- **40-70% context efficiency improvement** while maintaining 100% test compliance
- **Enhanced development loop workflow** with human-AI collaboration checkpoints
- **Semantic agent interfaces** replacing generic memory access patterns
- **Learning-based context optimization** that continuously improves over time
- **Three-phase development methodology** (Research → Planning → Implementation)

**Implementation Priority**: Start with development loop improvements for immediate `run-loop.sh` benefits, then expand to full agent framework integration.

## Part 1: Context Engineering Foundation

### Overview

The context engineering foundation implements intelligent context management across three core areas:

1. **Context Relevance Scoring** - Intelligent specification selection (30-50% reduction)
2. **BAML-Based Context Compression** - Memory footprint reduction (40-70%)
3. **Context Effectiveness Tracking** - Learning-based optimization over time

### 1. Context Relevance Scoring Implementation

#### Core Component: SpecificationRelevanceScorer
**Location**: `src/utils/context_relevance.py`

```python
class SpecificationRelevanceScorer:
    def __init__(self, specs_directory: str = "specs/"):
        self.specs_dir = specs_directory
        self.cache = {}
        self.critical_specs = ["001", "002", "003"]  # Always include foundation specs

    def score_specifications(self, current_task: str) -> List[Tuple[str, float]]:
        """Score specifications by relevance to current task."""
        task_keywords = self.extract_domain_keywords(current_task)
        task_type = self.detect_task_type(current_task)  # agent/test/infrastructure

        relevance_scores = []
        for spec_file in self.get_all_specs():
            spec_content = self.get_cached_content(spec_file)
            spec_keywords = self.extract_domain_keywords(spec_content)

            # Calculate base relevance using Jaccard similarity
            base_score = self.calculate_jaccard_similarity(task_keywords, spec_keywords)

            # Apply domain-specific weighting
            weighted_score = self.apply_domain_weighting(base_score, task_type, spec_file)

            relevance_scores.append((spec_file, weighted_score))

        return sorted(relevance_scores, key=lambda x: x[1], reverse=True)

    def select_optimal_specs(self, task: str, max_specs: int = 5) -> List[str]:
        """Select optimal specifications for task context."""
        scored_specs = self.score_specifications(task)

        # Always include critical specs
        selected = [spec for spec in self.critical_specs]

        # Add highest scoring non-critical specs
        remaining_slots = max_specs - len(selected)
        for spec_path, score in scored_specs:
            if remaining_slots <= 0:
                break
            if not any(critical in spec_path for critical in self.critical_specs):
                if score > 0.3:  # Relevance threshold
                    selected.append(spec_path)
                    remaining_slots -= 1

        return selected
```

#### Development Loop Integration
**Location**: `scripts/development/run-implementation-loop.sh:413-417`

Replace current `cat prompt.md` with intelligent context selection:

```bash
# Enhanced implementation replaces lines 413-417
optimize_context_selection() {
    echo "📖 Analyzing task context requirements..."

    # Extract current task
    CURRENT_TASK=$(extract_current_task)
    echo "🎯 Current task: $CURRENT_TASK"

    # Select relevant specifications
    RELEVANT_SPECS=$(python -c "
from src.utils.context_relevance import SpecificationRelevanceScorer
scorer = SpecificationRelevanceScorer()
specs = scorer.select_optimal_specs('$CURRENT_TASK', max_specs=5)
print(' '.join(specs))
")

    echo "📋 Selected specs: $RELEVANT_SPECS"

    # Generate optimized prompt
    generate_optimized_prompt "$CURRENT_TASK" "$RELEVANT_SPECS"
}

generate_optimized_prompt() {
    local task="$1"
    local specs="$2"

    cat > optimized_prompt.md << EOF
# CogniscientAssistant Implementation Task

## Current Task
$task

## Relevant Specifications
$(for spec in $specs; do
    echo "### $(basename $spec)"
    cat "specs/$spec"
    echo ""
done)

## Implementation Guidelines
$(cat CLAUDE.md)

## Quality Requirements
- Maintain 100% test pass rate
- Follow specification requirements exactly
- Implement atomic features only
- Use BAML for all content generation
EOF
}
```

### 2. BAML-Based Context Compression

#### Core BAML Functions
**Location**: `baml_src/functions.baml` (additions)

```baml
function CompressHypotheses(
    hypotheses: Hypothesis[],
    compression_strategy: string,
    target_ratio: float,
    preserve_fields: string[]
) -> CompressedHypotheses {
    client ProductionClient

    prompt #"
        {{ _.role("system") }}
        You are an expert at compressing scientific research data while preserving critical information.
        You excel at identifying key patterns, removing redundancy, and maintaining scientific accuracy.

        {{ _.role("user") }}
        Please compress the following hypothesis collection using {{ compression_strategy }} strategy:

        Target compression ratio: {{ target_ratio }}
        Critical fields to preserve: {{ preserve_fields }}

        Hypotheses to compress:
        {% for hypothesis in hypotheses %}
        - ID: {{ hypothesis.id }}
        - Description: {{ hypothesis.description }}
        - Experimental Protocol: {{ hypothesis.experimental_protocol }}
        - Expected Outcomes: {{ hypothesis.expected_outcomes }}
        - Supporting Evidence: {{ hypothesis.supporting_evidence }}
        {% endfor %}

        Compress using {{ compression_strategy }} approach:
        - summary: Create concise summaries preserving key scientific concepts
        - hierarchical: Group related hypotheses and create multi-level summaries
        - semantic: Merge similar hypotheses while preserving distinct elements

        Maintain scientific accuracy and ensure compressed data remains actionable.
    "#
}

function ValidateCompressionQuality(
    original_data: string,
    compressed_data: string,
    domain_context: string
) -> CompressionQualityReport {
    client ProductionClient

    prompt #"
        {{ _.role("system") }}
        You are an expert at evaluating the quality of scientific data compression.
        You assess fidelity, completeness, and actionability of compressed scientific information.

        {{ _.role("user") }}
        Please evaluate the compression quality for this scientific data:

        Domain context: {{ domain_context }}

        Original data:
        {{ original_data }}

        Compressed data:
        {{ compressed_data }}

        Assess the compression across these dimensions:
        1. **Fidelity**: How accurately does compressed data represent the original?
        2. **Completeness**: What percentage of critical information is preserved?
        3. **Actionability**: Can the compressed data support the same research decisions?
        4. **Scientific Accuracy**: Are all scientific concepts correctly maintained?
        5. **Reconstructability**: How well could the original be reconstructed?

        Provide scores (0-1) for each dimension and overall quality assessment.
    "#
}
```

#### Compressed Context Memory Wrapper
**Location**: `src/core/compressed_context_memory.py`

```python
class CompressedContextMemory:
    def __init__(self, base_memory: ContextMemory, baml_wrapper: BAMLWrapper):
        self.base_memory = base_memory
        self.baml_wrapper = baml_wrapper
        self.compression_cache = {}
        self.compression_config = CompressionConfig()

    async def store_with_compression(self, key: str, data: Any,
                                   compression_strategy: str = "auto") -> None:
        """Store data with intelligent compression based on size and type."""

        # Determine if compression is beneficial
        if self.should_compress(data):
            compressed_data = await self.compress_data(data, compression_strategy)

            # Validate compression quality
            quality_report = await self.validate_compression_quality(data, compressed_data)

            if quality_report.overall_quality >= self.compression_config.quality_threshold:
                # Store compressed version
                await self.base_memory.set(f"{key}_compressed", compressed_data)
                await self.base_memory.set(f"{key}_metadata", {
                    "compressed": True,
                    "quality_score": quality_report.overall_quality,
                    "compression_ratio": compressed_data.compression_ratio
                })
            else:
                # Quality insufficient, store uncompressed
                await self.base_memory.set(key, data)
                await self.base_memory.set(f"{key}_metadata", {"compressed": False})
        else:
            # Data too small or unsuitable for compression
            await self.base_memory.set(key, data)

    async def retrieve_with_decompression(self, key: str,
                                        expansion_level: str = "full") -> Any:
        """Retrieve data with automatic decompression if needed."""

        metadata = await self.base_memory.get(f"{key}_metadata", {})

        if metadata.get("compressed", False):
            # Retrieve and decompress
            compressed_data = await self.base_memory.get(f"{key}_compressed")

            # Check cache for decompressed version
            cache_key = f"{key}_{expansion_level}"
            if cache_key in self.compression_cache:
                return self.compression_cache[cache_key]

            # Decompress using BAML
            decompressed_data = await self.decompress_data(compressed_data, expansion_level)

            # Cache decompressed version
            self.compression_cache[cache_key] = decompressed_data

            return decompressed_data
        else:
            # Return uncompressed data
            return await self.base_memory.get(key)
```

### 3. Context Effectiveness Tracking

#### Core Tracking Engine
**Location**: `src/core/context_effectiveness_tracker.py`

```python
@dataclass
class ContextUsage:
    """Records context selection and usage patterns."""
    context_id: str
    agent_type: str
    task_type: str
    context_items: List[str]  # IDs of context items used
    context_size_tokens: int
    selection_strategy: str
    timestamp: datetime
    session_id: str

@dataclass
class ContextEffectiveness:
    """Measures effectiveness of context selections."""
    context_id: str
    usage_id: str
    outcome_quality: float  # 0.0-1.0 based on task success
    hypothesis_quality: float  # From review scores
    agent_confidence: float
    task_completion_time: float
    resource_efficiency: float
    effectiveness_score: float  # Composite metric
    feedback_source: str  # "review", "ranking", "meta_analysis"
    timestamp: datetime

class ContextEffectivenessTracker:
    """Central engine for tracking and learning context effectiveness."""

    def __init__(self, context_memory: ContextMemory):
        self.context_memory = context_memory
        self.metrics_calculator = EffectivenessMetricsCalculator()
        self.pattern_learner = ContextPatternLearner()
        self.predictor = ContextEffectivenessPredictor()

    async def record_context_usage(self, usage: ContextUsage) -> str:
        """Record when context is selected and used."""
        usage_id = f"usage_{uuid4()}"
        await self.context_memory.set(f"usage_{usage_id}", usage)
        await self.context_memory.append_to_aggregate("context_usage_log", {
            "usage_id": usage_id,
            "timestamp": usage.timestamp.isoformat(),
            "agent_type": usage.agent_type,
            "task_type": usage.task_type,
            "context_size": usage.context_size_tokens
        })
        return usage_id

    async def record_effectiveness(self, effectiveness: ContextEffectiveness) -> None:
        """Record effectiveness outcome for a context usage."""
        await self.context_memory.set(f"effectiveness_{effectiveness.usage_id}", effectiveness)
        await self.context_memory.append_to_aggregate("effectiveness_log", {
            "usage_id": effectiveness.usage_id,
            "effectiveness_score": effectiveness.effectiveness_score,
            "timestamp": effectiveness.timestamp.isoformat()
        })

        # Trigger pattern learning if we have enough data
        await self.maybe_learn_patterns()

    async def get_recommendations(
        self,
        task_type: str,
        agent_type: str
    ) -> List[ContextRecommendation]:
        """Get context selection recommendations based on learned patterns."""
        patterns = await self.pattern_learner.get_patterns(task_type, agent_type)
        return await self.predictor.generate_recommendations(patterns)
```

## Implementation Phases

### Phase 1: Context Foundation (Week 1-2)
1. **Context Relevance Scoring** (2-3 iterations)
   - Implement SpecificationRelevanceScorer
   - Integrate with run-implementation-loop.sh
   - Test with Phase 11 ReflectionAgent as validation case

2. **BAML Compression Functions** (2-3 iterations)
   - Add compression functions to baml_src/functions.baml
   - Implement CompressedContextMemory wrapper
   - Create compression quality validation

### Phase 2: Effectiveness Tracking (Week 3-4)
1. **Tracking Infrastructure** (2-3 iterations)
   - Implement ContextEffectivenessTracker
   - Add usage and effectiveness recording
   - Create pattern learning algorithms

2. **Agent Integration** (2-3 iterations)
   - Enhance existing agents with effectiveness tracking
   - Implement learning-based context selection
   - Add performance monitoring

### Phase 3: Advanced Features (Week 5-6)
1. **Human Collaboration Patterns** (detailed in Part 2)
2. **Semantic Agent Tools** (detailed in Part 3)
3. **Three-Phase Workflow Integration** (detailed in Part 4)

## Success Metrics

### Quantitative Targets
- **Context Reduction**: 30-50% reduction in specification content per iteration
- **Memory Efficiency**: 40-70% reduction in memory footprint
- **Quality Preservation**: 100% must-pass test success rate
- **Learning Speed**: Pattern discovery within 100-200 usage samples

### Quality Gates
- All existing quality gates continue to pass
- Context relevance scores >0.3 for selected specs
- Compression quality scores >0.85 across all dimensions
- Effectiveness improvement >15% within 3 months

---

*This is Part 1 of the Comprehensive ACE-FCA Integration Plan. Continue with Part 2 for Human Collaboration Patterns.*