# BAML-Based Context Compression Implementation Plan

> Generated via ACE-FCA Planning Phase - September 21, 2025
> Status: Ready for Implementation After Phase 1

## Overview

This plan implements intelligent context compression using BAML functions to reduce memory footprint by 40-70% while maintaining scientific accuracy and actionability in the CogniscientAssistant system.

## Implementation Strategy

### **Core BAML Functions**

#### 1. Context Compression Function
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

function DecompressHypotheses(
    compressed_data: CompressedHypotheses,
    expansion_level: string
) -> Hypothesis[] {
    client ProductionClient

    prompt #"
        {{ _.role("system") }}
        You are an expert at reconstructing scientific research data from compressed representations.
        You excel at expanding summaries while maintaining scientific accuracy and logical consistency.

        {{ _.role("user") }}
        Please reconstruct hypotheses from the compressed data with {{ expansion_level }} expansion:

        Compressed data:
        {{ compressed_data.summary }}

        Reconstruction metadata:
        - Original count: {{ compressed_data.original_count }}
        - Compression method: {{ compressed_data.compression_method }}
        - Preserved elements: {{ compressed_data.preserved_elements }}

        Expansion level: {{ expansion_level }}
        - full: Reconstruct complete hypothesis objects with all fields
        - summary: Provide condensed but actionable hypothesis summaries
        - minimal: Return only essential information for current task

        Ensure reconstructed hypotheses maintain scientific validity and experimental feasibility.
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

#### 2. BAML Data Models
```baml
class CompressedHypotheses {
    summary string @description("Compressed representation of hypothesis collection")
    original_count int @description("Number of hypotheses in original collection")
    compressed_count int @description("Number of distinct elements in compressed form")
    compression_ratio float @description("Actual compression ratio achieved")
    compression_method string @description("Strategy used for compression")
    preserved_elements string[] @description("Critical elements that were fully preserved")
    metadata map<string, string> @description("Additional compression metadata")
    created_at string @description("Timestamp of compression")
}

class CompressionQualityReport {
    fidelity_score float @description("Accuracy of representation (0-1)")
    completeness_score float @description("Percentage of information preserved (0-1)")
    actionability_score float @description("Usability for decision making (0-1)")
    scientific_accuracy_score float @description("Correctness of scientific concepts (0-1)")
    reconstructability_score float @description("Potential for accurate reconstruction (0-1)")
    overall_quality float @description("Overall compression quality (0-1)")
    recommendations string[] @description("Suggestions for improvement")
    warnings string[] @description("Potential issues or concerns")
}
```

### **Agent Integration Architecture**

#### 1. CompressedContextMemory Wrapper
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

#### 2. CompressionAwareAgent Base Class
```python
class CompressionAwareAgent:
    def __init__(self):
        self.compressed_memory = CompressedContextMemory(
            self.context_memory,
            self.baml_wrapper
        )
        self.compression_preferences = {
            "hypotheses": {"strategy": "semantic", "expansion": "summary"},
            "reviews": {"strategy": "hierarchical", "expansion": "full"},
            "literature": {"strategy": "summary", "expansion": "minimal"}
        }

    async def store_data_efficiently(self, data_type: str, data: Any) -> None:
        """Store data using optimal compression strategy for type."""
        preferences = self.compression_preferences.get(data_type, {})
        strategy = preferences.get("strategy", "auto")

        await self.compressed_memory.store_with_compression(
            f"{data_type}_data",
            data,
            compression_strategy=strategy
        )

    async def retrieve_data_efficiently(self, data_type: str,
                                      task_context: str = None) -> Any:
        """Retrieve data with context-appropriate expansion level."""
        preferences = self.compression_preferences.get(data_type, {})
        expansion = self.determine_expansion_level(task_context, preferences)

        return await self.compressed_memory.retrieve_with_decompression(
            f"{data_type}_data",
            expansion_level=expansion
        )
```

### **Performance Optimization System**

#### 1. Multi-Level Caching
```python
class CompressionCacheManager:
    def __init__(self):
        self.l1_cache = {}  # Decompressed, frequently accessed
        self.l2_cache = {}  # Compressed, medium access
        self.l3_storage = ContextMemory()  # Disk-based, rarely accessed

        self.access_patterns = {}
        self.cache_metrics = CacheMetrics()

    async def adaptive_cache_management(self):
        """Automatically optimize cache based on access patterns."""

        # Analyze access patterns
        hot_data = self.identify_hot_data()
        cold_data = self.identify_cold_data()

        # Promote hot data to L1 (decompressed)
        for key in hot_data:
            if key not in self.l1_cache:
                await self.promote_to_l1(key)

        # Demote cold data to L3 (compressed, disk-based)
        for key in cold_data:
            if key in self.l1_cache:
                await self.demote_to_l3(key)

        # Update cache metrics
        self.cache_metrics.update_efficiency_metrics()

    def determine_compression_strategy(self, data_type: str,
                                     access_pattern: str) -> str:
        """Select optimal compression strategy based on usage patterns."""

        strategies = {
            ("hypotheses", "frequent"): "minimal",  # Fast decompression
            ("hypotheses", "batch"): "semantic",   # High compression
            ("reviews", "analysis"): "hierarchical", # Structured access
            ("literature", "reference"): "summary"   # Quick scanning
        }

        return strategies.get((data_type, access_pattern), "auto")
```

#### 2. Quality Monitoring System
```python
class CompressionQualityMonitor:
    def __init__(self, baml_wrapper: BAMLWrapper):
        self.baml_wrapper = baml_wrapper
        self.quality_history = []
        self.alert_thresholds = {
            "fidelity": 0.85,
            "completeness": 0.90,
            "actionability": 0.88
        }

    async def continuous_quality_assessment(self):
        """Continuously monitor compression quality and trigger alerts."""

        # Sample recent compressions for quality assessment
        recent_compressions = self.get_recent_compressions()

        for compression in recent_compressions:
            quality_report = await self.baml_wrapper.validate_compression_quality(
                compression.original_data,
                compression.compressed_data,
                compression.domain_context
            )

            # Check for quality degradation
            if self.detect_quality_issues(quality_report):
                await self.trigger_quality_alert(compression, quality_report)

            # Update quality history
            self.quality_history.append(quality_report)

        # Analyze trends and adjust strategies
        await self.adaptive_strategy_adjustment()

    async def trigger_quality_alert(self, compression: Any,
                                  quality_report: CompressionQualityReport):
        """Handle quality degradation alerts."""

        alert = {
            "type": "compression_quality_degradation",
            "compression_id": compression.id,
            "quality_scores": {
                "fidelity": quality_report.fidelity_score,
                "completeness": quality_report.completeness_score,
                "actionability": quality_report.actionability_score
            },
            "recommendations": quality_report.recommendations,
            "timestamp": datetime.now().isoformat()
        }

        # Log alert
        self.safety_logger.log_alert(alert)

        # Take corrective action
        if quality_report.overall_quality < 0.7:
            # Severe degradation - disable compression for this data type
            await self.disable_compression_temporarily(compression.data_type)
        elif quality_report.overall_quality < 0.8:
            # Moderate degradation - adjust compression strategy
            await self.adjust_compression_strategy(compression.data_type)
```

## Implementation Phases

### **Phase 1: Foundation (2-3 iterations)**
1. **BAML Function Implementation** (1 iteration)
   - Add compression functions to `baml_src/functions.baml`
   - Implement data models in `baml_src/models.baml`
   - Test function integration with existing BAML infrastructure

2. **Core Compression Engine** (1-2 iterations)
   - Implement CompressedContextMemory wrapper
   - Create CompressionAwareAgent base class
   - Add compression quality validation

### **Phase 2: Agent Integration (2-3 iterations)**
1. **SupervisorAgent Enhancement** (1 iteration)
   - Integrate compressed memory for resource tracking
   - Implement adaptive compression based on resource constraints
   - Add compression metrics to performance monitoring

2. **GenerationAgent Optimization** (1-2 iterations)
   - Use compressed literature context for hypothesis generation
   - Implement compressed hypothesis storage and retrieval
   - Optimize BAML calls with compressed context

### **Phase 3: Performance Optimization (2-3 iterations)**
1. **Caching Infrastructure** (1-2 iterations)
   - Implement multi-level caching system
   - Add adaptive cache management
   - Create access pattern analysis

2. **Strategy Optimization** (1 iteration)
   - Implement adaptive compression strategy selection
   - Add performance monitoring and tuning
   - Create compression effectiveness metrics

### **Phase 4: Quality Assurance (1-2 iterations)**
1. **Quality Monitoring** (1 iteration)
   - Implement continuous quality assessment
   - Add quality degradation alerts
   - Create quality trend analysis

2. **Integration Testing** (1 iteration)
   - Test full compression pipeline
   - Validate scientific accuracy preservation
   - Performance and reliability testing

### **Phase 5: System Integration (1-2 iterations)**
1. **Migration Strategy** (1 iteration)
   - Gradual rollout with feature flags
   - Data migration from uncompressed to compressed storage
   - Fallback mechanisms and emergency procedures

2. **Monitoring and Optimization** (1 iteration)
   - Real-time performance monitoring
   - Continuous optimization based on usage patterns
   - Documentation and knowledge transfer

## Success Metrics

### **Performance Targets**
- **Memory Efficiency**: 40-70% reduction in memory footprint
- **Cache Performance**: >80% hit rate for L1 cache, <5s decompression time
- **Storage Efficiency**: 60-80% reduction in disk storage requirements

### **Quality Preservation**
- **Fidelity**: >85% accuracy in compressed representation
- **Completeness**: >90% of critical information preserved
- **Actionability**: >88% usability for research decisions
- **Scientific Accuracy**: 100% preservation of scientific concepts

### **System Performance**
- **Response Time**: <10% increase in agent response times
- **Reliability**: >99.9% successful compression/decompression operations
- **Scalability**: Linear performance scaling with data volume

## Risk Mitigation

### **Quality Degradation Prevention**
- Continuous quality monitoring with automated alerts
- Automatic fallback to uncompressed data for low-quality compression
- Quality thresholds with configurable sensitivity
- Human review process for persistent quality issues

### **Performance Impact Mitigation**
- Asynchronous compression to avoid blocking operations
- Intelligent compression triggering based on data size and access patterns
- Emergency compression bypass for time-critical operations
- Performance monitoring with automatic optimization

### **Data Integrity Protection**
- Comprehensive backup of original data before compression
- Version control for compression algorithms and strategies
- Data validation at multiple stages of compression/decompression pipeline
- Automated data integrity verification

---

*This implementation plan provides a comprehensive roadmap for BAML-based context compression, leveraging existing infrastructure while adding sophisticated compression capabilities that maintain scientific accuracy and system performance.*