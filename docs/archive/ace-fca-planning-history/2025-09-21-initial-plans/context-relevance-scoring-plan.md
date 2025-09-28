# Context Relevance Scoring Implementation Plan

> Generated via ACE-FCA Planning Phase - September 21, 2025
> Status: Ready for Implementation

## Overview

This plan implements intelligent specification selection in the CogniscientAssistant workflow to achieve 30-50% context reduction while maintaining 100% test pass rates and specification compliance.

## Implementation Strategy

### **Target Integration Point**
- **Location**: `run-loop.sh:413-417` where `cat prompt.md` loads all specifications
- **Current Behavior**: Reads all 28 specifications unconditionally
- **Enhanced Behavior**: Intelligently select 3-7 most relevant specifications based on current task

### **Core Components**

#### 1. SpecificationRelevanceScorer (`src/utils/context_relevance.py`)
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

#### 2. Enhanced Task Detection (`run-loop.sh` modifications)
```bash
# Current implementation
detect_implementation_phase() {
    # Only returns phase number
    for phase in $(seq 1 17); do
        pattern="## Phase $phase:"
        if grep -A30 "$pattern" IMPLEMENTATION_PLAN.md | grep -q "^\- \[ \]"; then
            echo "$phase"
            return
        fi
    done
}

# Enhanced implementation
extract_current_task() {
    # Extract full task description for context scoring
    for phase in $(seq 1 17); do
        pattern="## Phase $phase:"
        unchecked_task=$(grep -A30 "$pattern" IMPLEMENTATION_PLAN.md | grep -m1 "^\- \[ \]" | sed 's/^- \[ \] //')
        if [ ! -z "$unchecked_task" ]; then
            echo "$unchecked_task"
            return
        fi
    done
    echo "No active task found"
}
```

#### 3. Context Optimization Pipeline (`run-loop.sh` integration)
```bash
# Replace line 413-417 in run-loop.sh
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

#### 4. Quality Validation Framework
```bash
validate_context_optimization() {
    echo "🔍 Validating context optimization..."

    # Check critical specifications included
    local task="$1"
    local selected_specs="$2"

    python -c "
from src.utils.context_relevance import validate_context_selection
result = validate_context_selection('$task', '$selected_specs')
print('PASS' if result.is_valid else 'FAIL')
print('Reason:', result.reason)
"
}
```

## Implementation Timeline

### **Day 1: Core Infrastructure (8 hours)**

#### Morning (4 hours)
1. **Create `src/utils/context_relevance.py`** (2 hours)
   - Implement SpecificationRelevanceScorer class
   - Add keyword extraction and domain weighting
   - Create relevance scoring algorithm
   - Add critical spec identification

2. **Update `run-loop.sh`** (2 hours)
   - Enhance task extraction function
   - Add context optimization pipeline
   - Create optimized prompt generation
   - Preserve existing error handling

#### Afternoon (4 hours)
3. **Create Context Validation** (2 hours)
   - Implement context selection validation
   - Add quality check functions
   - Create fallback mechanisms
   - Add logging and metrics

4. **Update `CLAUDE.md` Guidelines** (2 hours)
   - Add context optimization rules
   - Document fallback procedures
   - Update reading requirements
   - Preserve specification authority

### **Day 2: Quality Assurance and Testing (8 hours)**

#### Morning (4 hours)
1. **Integration Testing** (2 hours)
   - Test context optimization with known tasks
   - Validate critical spec inclusion
   - Test fallback mechanisms
   - Verify quality gate integration

2. **Unit Testing** (2 hours)
   - Test SpecificationRelevanceScorer
   - Test keyword extraction
   - Test relevance scoring algorithms
   - Test edge cases and error handling

#### Afternoon (4 hours)
3. **Phase 11 Validation** (2 hours)
   - Use Reflection Agent implementation as test case
   - Measure context reduction achieved
   - Validate test pass rates maintained
   - Document performance improvements

4. **Documentation and Refinement** (2 hours)
   - Document lessons learned
   - Refine scoring algorithms based on results
   - Update implementation guidelines
   - Prepare for broader rollout

## Success Metrics

### **Quantitative Targets**
- **Context Reduction**: 30-50% reduction in specification content per iteration
- **Quality Preservation**: 100% must-pass test success rate
- **Performance**: Faster iteration times with focused context
- **Accuracy**: >95% inclusion of task-relevant specifications

### **Validation Criteria**
- All existing quality gates continue to pass
- Phase 11 (Reflection Agent) implementation succeeds
- Context relevance scores >0.3 for selected specs
- Fallback to full context works when needed

## Risk Mitigation

### **Quality Degradation Prevention**
- Automatic fallback to full context on quality issues
- Critical specification always-include list
- Context validation in quality gates
- Continuous monitoring of test pass rates

### **Rollback Procedures**
1. **Immediate Rollback**: Revert `run-loop.sh` to `cat prompt.md`
2. **Emergency Fallback**: Environment variable to disable optimization
3. **Quality Gate Failure**: Automatic full context restoration
4. **Performance Issues**: Configurable optimization levels

## Integration Points

### **Existing Systems Enhanced**
- **Quality Gates**: Add context validation to existing checks
- **Test Framework**: Integrate with `test_expectations.json`
- **Implementation Loop**: Enhance without disrupting proven workflow
- **Specification System**: Preserve authority while optimizing selection

### **New Systems Added**
- **Context Relevance Engine**: Intelligent specification selection
- **Optimization Pipeline**: Context selection and prompt generation
- **Validation Framework**: Quality assurance for optimized context
- **Monitoring System**: Context effectiveness tracking

## Next Steps After Phase 1

1. **Phase 2**: BAML-based context compression for large specifications
2. **Phase 3**: Context effectiveness learning and adaptive optimization
3. **System-wide Rollout**: Expand to all implementation phases
4. **Advanced Optimization**: Cross-specification dependency analysis

---

*This implementation plan provides a complete roadmap for Phase 1 context relevance integration, following ACE-FCA methodology with precise specifications, quality gates, and validation procedures.*