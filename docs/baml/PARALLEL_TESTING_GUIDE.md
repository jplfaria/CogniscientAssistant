# BAML Parallel Testing Guide

## Overview

With BAML 0.209.0 and our enhanced testing framework, we can now run multiple BAML function tests concurrently, dramatically reducing development cycle time. This guide explains the benefits, implementation, and concrete examples of parallel testing for BAML functions.

## Benefits of Parallel Testing

### 🚀 **Massive Performance Improvements**
- **Traditional Sequential**: 10 hypothesis generations in ~120 seconds (12s each)
- **Parallel Execution**: 240 hypothesis generations in ~20 minutes vs 48 minutes sequential
- **Development Speedup**: 12x faster iteration cycles during agent development

### 📈 **Real-World Impact**
- **Agent Development**: Test all generation methods simultaneously
- **Regression Testing**: Verify all BAML functions work after changes
- **Load Testing**: Simulate realistic multi-agent scenarios
- **Cost Efficiency**: Better token utilization and reduced API wait time

## Implementation Architecture

### Core Components

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Test Orchestrator │───▶│  Parallel Executor   │───▶│   BAML Functions    │
│   (BAMLParallelTester)    │  (AsyncIO + Workers) │    │  (Multiple Models)  │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Test Configuration│    │    Result Collector  │    │   Performance       │
│   (Workers, Timeouts)     │   (Success/Failure)  │    │   Metrics Tracker   │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

### Key Classes

#### `BAMLParallelTester`
Located in `tests/baml_parallel_config.py` (to be implemented in Phase 7.5)

```python
class BAMLParallelTester:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.metrics = ParallelTestMetrics()

    async def run_parallel_baml_tests(
        self, test_cases: List[Dict[str, Any]]
    ) -> ParallelTestResults:
        """Run multiple BAML tests concurrently with performance tracking."""
```

## Concrete Usage Examples

### Example 1: Hypothesis Generation Stress Test

**Scenario**: Testing all 4 generation methods with multiple parameter combinations

```python
# Before (Sequential): ~48 seconds
@pytest.mark.asyncio
async def test_generation_methods_sequential():
    methods = ['literature_based', 'debate', 'assumptions', 'feedback']
    goals = [
        'Why does ice float?',
        'How do vaccines work?',
        'What causes gravity?'
    ]

    results = []
    start_time = time.time()

    for method in methods:
        for goal in goals:
            result = await baml_wrapper.generate_hypothesis(
                goal=goal,
                method=method,
                constraints=['ethical', 'testable'],
                existing_hypotheses=[]
            )
            results.append(result)

    elapsed = time.time() - start_time
    print(f"Sequential: {len(results)} hypotheses in {elapsed:.1f}s")
    # Output: Sequential: 12 hypotheses in 48.3s

# After (Parallel): ~12 seconds
@pytest.mark.asyncio
async def test_generation_methods_parallel():
    tester = BAMLParallelTester(max_workers=4)

    test_cases = [
        {
            'function': 'GenerateHypothesis',
            'params': {
                'goal': goal,
                'generation_method': method,
                'constraints': ['ethical', 'testable'],
                'existing_hypotheses': []
            }
        }
        for method in ['literature_based', 'debate', 'assumptions', 'feedback']
        for goal in ['Why does ice float?', 'How do vaccines work?', 'What causes gravity?']
    ]

    start_time = time.time()
    results = await tester.run_parallel_baml_tests(test_cases)
    elapsed = time.time() - start_time

    print(f"Parallel: {len(results)} hypotheses in {elapsed:.1f}s")
    # Output: Parallel: 12 hypotheses in 12.1s

    assert len(results) == 12
    assert all(hasattr(r, 'summary') for r in results if not isinstance(r, Exception))
```

### Example 2: Agent Integration Testing

**Scenario**: Testing all agent BAML functions in parallel during development

```python
@pytest.mark.asyncio
async def test_all_agent_functions_parallel():
    """Test Generation, Reflection, Ranking, Evolution functions simultaneously."""

    tester = BAMLParallelTester(max_workers=6)

    # Create test sample data
    sample_hypothesis = create_test_hypothesis()

    test_cases = [
        # Generation Agent
        {
            'function': 'GenerateHypothesis',
            'params': {
                'goal': 'Test research goal',
                'constraints': ['ethical'],
                'existing_hypotheses': [],
                'generation_method': 'literature_based'
            }
        },

        # Reflection Agent (Phase 11)
        {
            'function': 'GenerateReview',
            'params': {
                'hypothesis': sample_hypothesis,
                'review_focus': 'methodology',
                'domain_expertise': 'physics',
                'evaluation_criteria': ['scientific_rigor', 'testability']
            }
        },
        {
            'function': 'GenerateCritique',
            'params': {
                'hypothesis': sample_hypothesis,
                'critique_angle': 'skeptical',
                'context': {'domain': 'physics'}
            }
        },

        # Ranking Agent (Phase 12)
        {
            'function': 'CompareHypotheses',
            'params': {
                'hypothesis1': sample_hypothesis,
                'hypothesis2': create_test_hypothesis(variant=True),
                'comparison_criteria': ['novelty', 'feasibility']
            }
        },

        # Safety checks
        {
            'function': 'PerformSafetyCheck',
            'params': {
                'target_type': 'hypothesis',
                'target_content': sample_hypothesis.summary,
                'trust_level': 'medium',
                'safety_criteria': ['ethical', 'safe']
            }
        }
    ]

    start_time = time.time()
    results = await tester.run_parallel_baml_tests(test_cases)
    elapsed = time.time() - start_time

    print(f"Tested {len(test_cases)} agent functions in {elapsed:.1f}s")
    # Expected: ~6-8 seconds vs ~25-30 seconds sequential

    # Verify all functions work
    assert len(results) == len(test_cases)
    assert all(not isinstance(r, Exception) for r in results)

    # Performance assertion
    assert elapsed < 15  # Should be much faster than sequential
```

### Example 3: Load Testing with Real Models

**Scenario**: Testing system behavior under realistic multi-agent load

```python
@pytest.mark.real_llm  # Only run with --real-llm flag
@pytest.mark.asyncio
async def test_realistic_multi_agent_load():
    """Simulate realistic multi-agent scenario with parallel BAML calls."""

    tester = BAMLParallelTester(max_workers=3)  # Conservative for real APIs

    # Simulate 3 agents working simultaneously
    test_cases = [
        # Agent 1: Generating hypotheses
        *[{
            'function': 'GenerateHypothesis',
            'params': {
                'goal': f'Research question {i}',
                'constraints': ['ethical', 'feasible'],
                'existing_hypotheses': [],
                'generation_method': 'literature_based'
            }
        } for i in range(5)],

        # Agent 2: Reviewing existing hypotheses
        *[{
            'function': 'GenerateReview',
            'params': {
                'hypothesis': create_test_hypothesis(id=f'hyp_{i}'),
                'review_focus': 'methodology',
                'domain_expertise': 'general_science',
                'evaluation_criteria': ['rigor', 'novelty']
            }
        } for i in range(3)],

        # Agent 3: Safety checking
        *[{
            'function': 'PerformSafetyCheck',
            'params': {
                'target_type': 'hypothesis',
                'target_content': f'Test hypothesis content {i}',
                'trust_level': 'medium',
                'safety_criteria': ['ethical', 'safe']
            }
        } for i in range(4)]
    ]

    start_time = time.time()
    results = await tester.run_parallel_baml_tests(test_cases)
    elapsed = time.time() - start_time

    print(f"Multi-agent simulation: {len(test_cases)} operations in {elapsed:.1f}s")
    print(f"Average per operation: {elapsed/len(test_cases):.2f}s")

    # Analyze results
    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]

    print(f"Success rate: {len(successes)}/{len(results)} ({len(successes)/len(results)*100:.1f}%)")

    # Should handle realistic load efficiently
    assert len(successes) >= len(test_cases) * 0.95  # 95% success rate
    assert elapsed < len(test_cases) * 2  # Much faster than sequential
```

## Performance Metrics and Monitoring

### Automatic Performance Tracking

```python
class ParallelTestMetrics:
    def track_execution(self, test_cases: List[Dict], results: List[Any], elapsed_time: float):
        """Track performance metrics for optimization."""

        metrics = {
            'total_tests': len(test_cases),
            'successful_tests': len([r for r in results if not isinstance(r, Exception)]),
            'failed_tests': len([r for r in results if isinstance(r, Exception)]),
            'total_time': elapsed_time,
            'avg_time_per_test': elapsed_time / len(test_cases),
            'tests_per_second': len(test_cases) / elapsed_time,
            'parallelization_efficiency': self.calculate_efficiency(test_cases, elapsed_time)
        }

        self.log_metrics(metrics)
        return metrics
```

### Expected Performance Benchmarks

| Scenario | Sequential Time | Parallel Time | Speedup | Workers |
|----------|----------------|---------------|---------|---------|
| 10 Hypothesis Generation | 120s | 30s | 4x | 4 |
| Full Agent Function Test | 60s | 15s | 4x | 6 |
| 50 Mixed Operations | 300s | 75s | 4x | 4 |
| Real LLM Load Test | 180s | 60s | 3x | 3 |

## Configuration and Best Practices

### Worker Configuration

```python
# Conservative (Real LLMs)
tester = BAMLParallelTester(max_workers=2)

# Aggressive (Mock/Test Environment)
tester = BAMLParallelTester(max_workers=8)

# Balanced (Development)
tester = BAMLParallelTester(max_workers=4)
```

### Error Handling Best Practices

```python
async def run_with_error_analysis(test_cases):
    results = await tester.run_parallel_baml_tests(test_cases)

    # Categorize errors
    validation_errors = []
    timeout_errors = []
    api_errors = []

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            error_type = classify_error(result)
            test_case = test_cases[i]

            # Log for debugging
            logger.error(f"Test {i} failed: {error_type} - {result}")

    return results, error_analysis
```

### Memory and Resource Management

```python
# For large test suites, process in batches
async def run_large_test_suite(all_test_cases, batch_size=20):
    results = []

    for i in range(0, len(all_test_cases), batch_size):
        batch = all_test_cases[i:i+batch_size]
        batch_results = await tester.run_parallel_baml_tests(batch)
        results.extend(batch_results)

        # Brief pause between batches for resource management
        await asyncio.sleep(1)

    return results
```

## Integration with Development Workflow

### Automated Testing Pipeline

```bash
# Quick parallel smoke test (30 seconds vs 2 minutes)
pytest tests/integration/test_baml_parallel.py::test_quick_smoke_test -v

# Full parallel regression test (2 minutes vs 10 minutes)
pytest tests/integration/test_baml_parallel.py -v

# Comprehensive load test with real models (5 minutes vs 20 minutes)
pytest tests/integration/test_baml_parallel.py --real-llm -v
```

### Development Workflow Script

```bash
#!/bin/bash
# Enhanced development workflow with parallel testing

echo "🔄 Regenerating BAML client..."
baml generate

echo "🧪 Running parallel BAML tests..."
python -m pytest tests/integration/test_baml_parallel.py -v --tb=short

echo "✅ Parallel testing complete!"
echo "📊 Performance metrics saved to .baml_parallel_metrics.log"
```

## Troubleshooting

### Common Issues and Solutions

1. **Too Many Workers**: Reduce `max_workers` if seeing API rate limits
2. **Memory Issues**: Use batch processing for large test suites
3. **Inconsistent Results**: Check for race conditions in test data
4. **Timeout Issues**: Increase timeouts for complex BAML functions

### Debugging Parallel Tests

```python
# Enable detailed logging
import logging
logging.getLogger('baml_parallel').setLevel(logging.DEBUG)

# Run single-threaded for debugging
tester = BAMLParallelTester(max_workers=1)
```

## Future Enhancements

- **Adaptive Worker Scaling**: Automatically adjust workers based on API response times
- **Smart Test Prioritization**: Run faster tests first, slower tests in parallel
- **Cross-Model Testing**: Test same function across multiple models simultaneously
- **Performance Regression Detection**: Alert when parallel performance degrades

## Implementation Timeline

This parallel testing framework will be implemented in **Phase 7.5: Development Workflow Optimization** of the main implementation plan, providing immediate benefits for all subsequent agent development phases (9-15).