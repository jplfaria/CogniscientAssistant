# BAML Integration Improvements Implementation Plan

## Overview

Enhance our BAML integration to leverage 0.209.0 capabilities and implement missing functions required for upcoming agent phases. This plan addresses critical blocking issues for Phase 11 (Reflection Agent) development and unlocks major performance and feature improvements from the BAML 0.209.0 upgrade.

## Current State Analysis

Based on comprehensive research documented in `thoughts/shared/research/2025-09-30-baml-integration-improvements.md`:

### ✅ Strong Foundation
- 8 core BAML functions implemented (`baml_src/functions.baml:1-436`)
- 30+ type definitions in comprehensive schema (`baml_src/models.baml:1-314`)
- 19 client configurations supporting multiple models (`baml_src/clients.baml:1-259`)
- Robust integration layer with proper error handling (`src/llm/baml_wrapper.py:38-342`)
- Production-ready with Argo Gateway integration

### ❌ Critical Gaps
- **Missing Phase 11 functions**: `generate_review`, `generate_critique` (blocks Reflection Agent)
- **8+ additional missing functions** for Phases 12-15
- **Underutilized 0.209.0 features**: Enhanced error handling, streaming, performance optimizations
- **Basic testing workflow**: Not leveraging parallel testing capabilities

### Key Discoveries:
- All existing BAML functions follow proper system+user role pattern (`baml_src/functions.baml:18-24`)
- Type conversion patterns are well-established (`src/agents/generation.py:645-701`)
- Testing infrastructure supports both mocked and real LLM testing (`tests/conftest.py:16-196`)
- Model configuration system is flexible and extensible (`src/config/model_config.py:18-31`)

## Desired End State

After completion of this plan:
- All agent phases (11-15) have required BAML functions implemented
- Enhanced error handling and debugging capabilities from BAML 0.209.0
- Streaming support for long-form content generation
- Optimized development workflow with parallel testing
- Performance improvements from 0.209.0 features (6x trace uploads, cost optimization)

### Verification
- Phase 11 agents can be implemented without BAML function blockers
- Enhanced error reporting provides clear debugging information
- Streaming responses work for hypothesis generation
- Test suite runs significantly faster with parallel execution

## What We're NOT Doing

- Migrating away from current BAML integration patterns (they're working well)
- Changing existing function signatures (maintain backward compatibility)
- Implementing all advanced BAML features at once (phased approach)
- Rewriting existing working BAML functions
- Changing the core BAMLWrapper abstraction layer

## Implementation Approach

**Incremental Enhancement Strategy**: Build upon our solid foundation by adding missing functions and gradually adopting 0.209.0 features. Prioritize blocking issues first, then value-adding improvements.

**Risk Mitigation**: Each phase includes comprehensive testing and can be rolled back independently. Maintain backward compatibility throughout.

## Phase 1: Critical Reflection Agent Functions

### Overview
Implement the two missing BAML functions required for Phase 11 (Reflection Agent) development: `generate_review` and `generate_critique`. This unblocks immediate development priorities.

### Changes Required:

#### 1. BAML Function Definitions
**File**: `baml_src/functions.baml`
**Changes**: Add two new functions following existing patterns

```baml
// Generate detailed review of a hypothesis
function GenerateReview(
  hypothesis: Hypothesis @description("Hypothesis to review"),
  review_focus: string @description("Specific aspect to focus on: methodology, evidence, assumptions"),
  domain_expertise: string @description("Domain knowledge to apply"),
  evaluation_criteria: string[] @description("Specific criteria for evaluation")
) -> Review {
  client ProductionClient

  prompt #"
    {{ _.role("system") }}
    You are a peer reviewer with expertise in {{ domain_expertise }}.
    You provide thorough, constructive reviews focusing on scientific rigor and methodology.
    You evaluate hypotheses objectively and provide specific improvement suggestions.

    {{ _.role("user") }}
    Please review the following hypothesis with focus on {{ review_focus }}:

    Hypothesis: {{ hypothesis.summary }}
    Description: {{ hypothesis.full_description }}
    Assumptions: {{ hypothesis.assumptions }}

    Evaluation Criteria:
    {% for criterion in evaluation_criteria %}
    - {{ criterion }}
    {% endfor %}

    Provide a comprehensive review including scores, strengths, weaknesses, and specific improvement suggestions.
  "#
}

// Generate critical analysis of a hypothesis
function GenerateCritique(
  hypothesis: Hypothesis @description("Hypothesis to critique"),
  critique_angle: string @description("Perspective for critique: skeptical, methodological, ethical"),
  context: map<string, string>? @description("Additional context for critique")
) -> Review {
  client ProductionClient

  prompt #"
    {{ _.role("system") }}
    You are a critical analyst who challenges scientific hypotheses from a {{ critique_angle }} perspective.
    You identify potential flaws, oversights, and weaknesses while remaining constructive.
    You help strengthen hypotheses through rigorous criticism.

    {{ _.role("user") }}
    Please critique the following hypothesis from a {{ critique_angle }} angle:

    Hypothesis: {{ hypothesis.summary }}
    Description: {{ hypothesis.full_description }}
    Experimental Protocol: {{ hypothesis.experimental_protocol.methodology }}

    {% if context %}
    Additional Context:
    {% for key, value in context %}
    {{ key }}: {{ value }}
    {% endfor %}
    {% endif %}

    Identify potential issues, methodological concerns, and areas for improvement.
    Focus on constructive criticism that strengthens the hypothesis.
  "#
}
```

#### 2. BAMLWrapper Integration
**File**: `src/llm/baml_wrapper.py`
**Changes**: Add wrapper methods for new functions

```python
async def generate_review(
    self,
    hypothesis: Hypothesis,
    review_focus: str,
    domain_expertise: str,
    evaluation_criteria: List[str],
) -> Review:
    """Generate a review using BAML."""
    try:
        result = await self._client.GenerateReview(
            hypothesis=hypothesis,
            review_focus=review_focus,
            domain_expertise=domain_expertise,
            evaluation_criteria=evaluation_criteria,
        )

        logger.info(f"Generated review for hypothesis: {hypothesis.id}")
        return result

    except Exception as e:
        logger.error(f"Error generating review: {e}")
        raise

async def generate_critique(
    self,
    hypothesis: Hypothesis,
    critique_angle: str,
    context: Optional[Dict[str, str]] = None,
) -> Review:
    """Generate a critique using BAML."""
    try:
        result = await self._client.GenerateCritique(
            hypothesis=hypothesis,
            critique_angle=critique_angle,
            context=context or {},
        )

        logger.info(f"Generated critique for hypothesis: {hypothesis.id}")
        return result

    except Exception as e:
        logger.error(f"Error generating critique: {e}")
        raise
```

#### 3. Test Mocking Support
**File**: `tests/conftest.py`
**Changes**: Add mock implementations for new functions

```python
# Add to existing mock setup
def create_review_mock(review_type="critique"):
    return MockBAMLType(
        id=f"review_{uuid4().hex[:8]}",
        hypothesis_id="hyp_test",
        reviewer_agent_id="agent_test",
        review_type=review_type,
        decision="revise",
        scores=MockBAMLType(
            correctness=0.8,
            quality=0.7,
            novelty=0.9,
            safety=0.95,
            feasibility=0.75
        ),
        narrative_feedback=f"Generated {review_type} feedback",
        key_strengths=["strength1", "strength2"],
        key_weaknesses=["weakness1"],
        improvement_suggestions=["suggestion1", "suggestion2"],
        confidence_level="medium",
        created_at="2025-09-30T01:00:00Z"
    )

mock_b.GenerateReview = AsyncMock(return_value=create_review_mock("full"))
mock_b.GenerateCritique = AsyncMock(return_value=create_review_mock("critique"))
```

#### 4. Update Test Expectations
**File**: `tests/integration/test_expectations.json`
**Changes**: Remove `generate_review` and `generate_critique` from may_fail lists (if present)

### Success Criteria:

#### Automated Verification:
- [ ] BAML client regenerates successfully: `baml generate`
- [ ] All unit tests pass: `python -m pytest tests/unit/ -v`
- [ ] Integration tests pass: `python -m pytest tests/integration/ -v`
- [ ] Type checking passes: `mypy src/`
- [ ] Linting passes: `ruff check src/`

#### Manual Verification:
- [ ] New BAML functions can be called without errors
- [ ] Functions return properly structured Review objects
- [ ] Generated reviews include meaningful feedback and scores
- [ ] Mock implementations work correctly in tests

## Phase 2: Enhanced Error Handling & Debugging

### Overview
Leverage BAML 0.209.0's enhanced error handling features including fallback history exposure and improved debugging capabilities.

### Changes Required:

#### 1. Enhanced Error Handling in BAMLWrapper
**File**: `src/llm/baml_wrapper.py`
**Changes**: Implement comprehensive error handling with BAML 0.209.0 features

```python
import logging
from typing import Optional, Dict, Any
from baml_client.baml_client import types as baml_types

class BAMLWrapper:
    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider
        self._client = b
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def _handle_baml_call(
        self,
        operation: str,
        baml_func: callable,
        **kwargs
    ) -> Any:
        """Enhanced error handling for BAML calls with 0.209.0 features."""
        try:
            result = await baml_func(**kwargs)
            self.logger.info(f"BAML {operation} successful")
            return result

        except baml_types.BAMLValidationError as e:
            # Enhanced validation error with schema details
            self.logger.error(f"BAML validation error in {operation}: {e}")
            self.logger.error(f"Fallback history: {getattr(e, 'fallback_history', 'Not available')}")
            raise ValueError(f"Invalid response format in {operation}: {e}")

        except baml_types.BAMLRuntimeError as e:
            # Runtime errors with detailed context
            self.logger.error(f"BAML runtime error in {operation}: {e}")
            self.logger.error(f"Request context: {getattr(e, 'request_context', 'Not available')}")
            raise RuntimeError(f"BAML execution failed in {operation}: {e}")

        except Exception as e:
            # Catch-all with enhanced logging
            self.logger.error(f"Unexpected error in BAML {operation}: {e}")
            self.logger.error(f"Operation args: {kwargs}")
            raise

    # Update existing methods to use enhanced error handling
    async def generate_hypothesis(self, **kwargs) -> Hypothesis:
        return await self._handle_baml_call(
            "GenerateHypothesis",
            self._client.GenerateHypothesis,
            **kwargs
        )
```

#### 2. Enhanced Logging Configuration
**File**: `src/config/logging_config.py` (new file)
**Changes**: Add BAML-specific logging configuration

```python
import logging
from typing import Dict, Any

def configure_baml_logging(level: str = "INFO") -> None:
    """Configure enhanced logging for BAML operations."""

    # BAML-specific logger
    baml_logger = logging.getLogger("baml_client")
    baml_logger.setLevel(getattr(logging, level.upper()))

    # Wrapper logger
    wrapper_logger = logging.getLogger("src.llm.baml_wrapper")
    wrapper_logger.setLevel(getattr(logging, level.upper()))

    # Enhanced formatter with BAML context
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - '
        'Context: %(context)s',
        defaults={'context': 'None'}
    )

    # Add file handler for BAML operations
    file_handler = logging.FileHandler('.baml_operations.log')
    file_handler.setFormatter(formatter)

    baml_logger.addHandler(file_handler)
    wrapper_logger.addHandler(file_handler)
```

#### 3. Error Recovery Mechanisms
**File**: `src/llm/baml_retry.py` (new file)
**Changes**: Implement retry logic with BAML 0.209.0 capabilities

```python
import asyncio
from typing import TypeVar, Callable, Any
from functools import wraps

T = TypeVar('T')

class BAMLRetryConfig:
    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
        retry_on_validation_error: bool = False
    ):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_on_validation_error = retry_on_validation_error

def with_baml_retry(config: BAMLRetryConfig):
    """Decorator for BAML operations with intelligent retry logic."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)

                except Exception as e:
                    last_exception = e

                    # Don't retry validation errors unless configured
                    if "validation" in str(e).lower() and not config.retry_on_validation_error:
                        raise

                    if attempt < config.max_retries:
                        delay = config.backoff_factor ** attempt
                        await asyncio.sleep(delay)
                        continue

                    # Final attempt failed
                    raise last_exception

        return wrapper
    return decorator
```

### Success Criteria:

#### Automated Verification:
- [ ] Enhanced error handling compiles: `python -c "from src.llm.baml_wrapper import BAMLWrapper"`
- [ ] Logging configuration works: `python -c "from src.config.logging_config import configure_baml_logging; configure_baml_logging()"`
- [ ] All existing tests pass: `python -m pytest tests/ -v`
- [ ] Error handling tests pass: `python -m pytest tests/unit/test_baml_wrapper.py::test_error_handling -v`

#### Manual Verification:
- [ ] Enhanced error messages provide clear debugging information
- [ ] Fallback history is logged when available
- [ ] Retry mechanisms work correctly for transient failures
- [ ] Error logs include sufficient context for debugging

## Phase 3: Streaming Integration

### Overview
Implement BAML 0.209.0 streaming capabilities for long-form content generation, starting with hypothesis generation.

### Changes Required:

#### 1. Streaming BAML Function
**File**: `baml_src/functions.baml`
**Changes**: Add streaming version of hypothesis generation

```baml
function GenerateHypothesisStream(
  goal: string @description("Research goal or objective"),
  constraints: string[] @description("Constraints to consider"),
  existing_hypotheses: Hypothesis[] @description("Already generated hypotheses"),
  focus_area: string? @description("Specific area to focus on"),
  generation_method: string @description("Method to use")
) -> stream<Hypothesis> {
  client ProductionClient

  prompt #"
    {{ _.role("system") }}
    You are a brilliant research scientist specialized in generating novel hypotheses.
    You excel at creating scientifically plausible hypotheses that respect constraints.
    You will generate the hypothesis incrementally, building it piece by piece.

    {{ _.role("user") }}
    Research Goal: {{ goal }}

    Constraints to consider:
    {{ constraints }}

    {% if existing_hypotheses %}
    Already explored hypotheses (avoid duplication):
    {% for hyp in existing_hypotheses %}
    - {{ hyp.summary }}
    {% endfor %}
    {% endif %}

    Generate a novel hypothesis incrementally, providing partial results as you build it.
    Start with the core idea, then add details, methodology, and supporting evidence.
  "#
}
```

#### 2. Streaming Support in BAMLWrapper
**File**: `src/llm/baml_wrapper.py`
**Changes**: Add streaming method with proper async iteration

```python
from typing import AsyncIterator
from baml_client.baml_client.stream_types import GenerateHypothesisStreamType

async def generate_hypothesis_stream(
    self,
    goal: str,
    constraints: List[str],
    existing_hypotheses: List[Hypothesis],
    focus_area: Optional[str] = None,
    generation_method: str = "literature_based",
    on_partial: Optional[Callable[[Any], None]] = None
) -> AsyncIterator[Hypothesis]:
    """Generate hypothesis with streaming for real-time updates."""
    try:
        stream = self._client.GenerateHypothesisStream(
            goal=goal,
            constraints=constraints,
            existing_hypotheses=existing_hypotheses,
            focus_area=focus_area,
            generation_method=generation_method,
        )

        async for partial in stream:
            if on_partial:
                on_partial(partial)

            # Yield complete hypothesis objects as they become available
            if hasattr(partial, 'summary') and partial.summary:
                yield partial

    except Exception as e:
        logger.error(f"Error in streaming hypothesis generation: {e}")
        raise
```

#### 3. Agent Integration
**File**: `src/agents/generation.py`
**Changes**: Add streaming support to generation agent

```python
async def generate_from_literature_stream(
    self,
    research_goal: ResearchGoal,
    literature_context: Dict[str, Any],
    on_partial_update: Optional[Callable[[str], None]] = None
) -> AsyncIterator[Hypothesis]:
    """Stream hypothesis generation with real-time updates."""

    # Prepare parameters
    constraints = research_goal.constraints + self._get_ethical_constraints()
    existing_hypotheses = await self._get_existing_hypotheses(research_goal)

    # Stream generation
    async for hypothesis in self.baml_wrapper.generate_hypothesis_stream(
        goal=research_goal.description,
        constraints=constraints,
        existing_hypotheses=existing_hypotheses,
        focus_area=literature_context.get('focus_area'),
        generation_method='literature_based',
        on_partial=on_partial_update
    ):
        # Convert and yield
        converted_hypothesis = self._convert_baml_hypothesis(hypothesis)
        yield converted_hypothesis
```

### Success Criteria:

#### Automated Verification:
- [ ] BAML client regenerates with streaming: `baml generate`
- [ ] Streaming functions import correctly: `python -c "from baml_client.baml_client import b; print(hasattr(b, 'GenerateHypothesisStream'))"`
- [ ] All tests pass: `python -m pytest tests/ -v`
- [ ] Type checking passes: `mypy src/`

#### Manual Verification:
- [ ] Streaming hypothesis generation provides real-time updates
- [ ] Partial results are meaningful and build incrementally
- [ ] Final streamed result matches quality of non-streaming version
- [ ] Stream can be cancelled mid-generation without errors

## Phase 4: Testing Optimization

### Overview
Implement BAML 0.209.0 parallel testing capabilities and enhance development workflow.

### Changes Required:

#### 1. Parallel Test Configuration
**File**: `tests/baml_parallel_config.py` (new file)
**Changes**: Configure parallel testing for BAML functions

```python
import pytest
import asyncio
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

class BAMLParallelTester:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def run_parallel_baml_tests(
        self,
        test_cases: List[Dict[str, Any]]
    ) -> List[Any]:
        """Run multiple BAML function tests in parallel."""

        tasks = []
        for test_case in test_cases:
            task = asyncio.create_task(
                self._run_single_test(test_case)
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def _run_single_test(self, test_case: Dict[str, Any]) -> Any:
        """Run a single BAML test case."""
        function_name = test_case['function']
        params = test_case['params']

        # Import and call BAML function
        from baml_client.baml_client import b
        baml_function = getattr(b, function_name)

        return await baml_function(**params)
```

#### 2. Enhanced Test Suite
**File**: `tests/integration/test_baml_parallel.py` (new file)
**Changes**: Parallel integration tests for BAML functions

```python
import pytest
import asyncio
from tests.baml_parallel_config import BAMLParallelTester

@pytest.mark.asyncio
async def test_parallel_hypothesis_generation():
    """Test parallel generation of multiple hypotheses."""

    tester = BAMLParallelTester(max_workers=4)

    test_cases = [
        {
            'function': 'GenerateHypothesis',
            'params': {
                'goal': f'Research goal {i}',
                'constraints': ['ethical', 'feasible'],
                'existing_hypotheses': [],
                'generation_method': 'literature_based'
            }
        }
        for i in range(10)  # Generate 10 hypotheses in parallel
    ]

    start_time = asyncio.get_event_loop().time()
    results = await tester.run_parallel_baml_tests(test_cases)
    end_time = asyncio.get_event_loop().time()

    # Verify results
    assert len(results) == 10
    assert all(hasattr(result, 'summary') for result in results if not isinstance(result, Exception))

    # Performance assertion - should be significantly faster than sequential
    execution_time = end_time - start_time
    assert execution_time < 30  # Should complete in under 30 seconds

    print(f"Generated 10 hypotheses in {execution_time:.2f} seconds")

@pytest.mark.real_llm
async def test_parallel_real_model_performance():
    """Test parallel execution with real models."""

    tester = BAMLParallelTester(max_workers=2)  # Conservative for real LLMs

    test_cases = [
        {
            'function': 'GenerateHypothesis',
            'params': {
                'goal': 'Why does ice float on water?',
                'constraints': ['physics-based', 'testable'],
                'existing_hypotheses': [],
                'generation_method': 'literature_based'
            }
        },
        {
            'function': 'PerformSafetyCheck',
            'params': {
                'target_type': 'hypothesis',
                'target_content': 'Test hypothesis content',
                'trust_level': 'medium',
                'safety_criteria': ['ethical', 'safe']
            }
        }
    ]

    results = await tester.run_parallel_baml_tests(test_cases)

    # Verify both functions executed successfully
    assert len(results) == 2
    assert all(not isinstance(result, Exception) for result in results)
```

#### 3. Development Workflow Script
**File**: `scripts/baml_dev_workflow.py` (new file)
**Changes**: Enhanced development workflow script

```python
#!/usr/bin/env python3
"""Enhanced BAML development workflow with 0.209.0 features."""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import List

async def regenerate_baml_client():
    """Regenerate BAML client with error checking."""
    import subprocess

    try:
        result = subprocess.run(
            ['baml', 'generate'],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ BAML client regenerated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ BAML client generation failed: {e.stderr}")
        return False

async def run_baml_tests(parallel: bool = True):
    """Run BAML tests with optional parallel execution."""
    import subprocess

    cmd = ['python', '-m', 'pytest', 'tests/integration/test_baml_*.py', '-v']

    if parallel:
        cmd.extend(['-n', 'auto'])  # pytest-xdist parallel execution

    try:
        result = subprocess.run(cmd, check=True)
        print("✅ All BAML tests passed")
        return True
    except subprocess.CalledProcessError:
        print("❌ BAML tests failed")
        return False

async def main():
    parser = argparse.ArgumentParser(description='BAML development workflow')
    parser.add_argument('--regenerate', action='store_true', help='Regenerate BAML client')
    parser.add_argument('--test', action='store_true', help='Run BAML tests')
    parser.add_argument('--parallel', action='store_true', default=True, help='Run tests in parallel')

    args = parser.parse_args()

    success = True

    if args.regenerate:
        success &= await regenerate_baml_client()

    if args.test:
        success &= await run_baml_tests(parallel=args.parallel)

    if not success:
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
```

### Success Criteria:

#### Automated Verification:
- [ ] Parallel test configuration works: `python -c "from tests.baml_parallel_config import BAMLParallelTester; BAMLParallelTester()"`
- [ ] Development workflow script runs: `python scripts/baml_dev_workflow.py --test --parallel`
- [ ] Parallel tests complete faster than sequential: `python -m pytest tests/integration/test_baml_parallel.py -v`

#### Manual Verification:
- [ ] Parallel testing shows significant performance improvement
- [ ] Development workflow is smoother and faster
- [ ] Test results are consistent between parallel and sequential execution

## Phase 5: Advanced Agent Functions

### Overview
Implement remaining BAML functions for Phases 12-15 (Ranking, Evolution, Proximity, Meta-Review agents).

### Changes Required:

#### 1. Ranking Agent Functions
**File**: `baml_src/functions.baml`
**Changes**: Add comparison reasoning function

```baml
function GenerateComparisonReasoning(
  hypothesis1: Hypothesis @description("First hypothesis"),
  hypothesis2: Hypothesis @description("Second hypothesis"),
  comparison_criteria: string[] @description("Criteria for comparison"),
  context: map<string, string>? @description("Additional context")
) -> ComparisonResult {
  client ProductionClient

  prompt #"
    {{ _.role("system") }}
    You are an expert scientific judge who provides detailed reasoning for hypothesis comparisons.
    You analyze hypotheses objectively and explain your decision-making process clearly.

    {{ _.role("user") }}
    Compare these hypotheses and provide detailed reasoning:

    Hypothesis 1: {{ hypothesis1.summary }}
    Novelty: {{ hypothesis1.novelty_claim }}

    Hypothesis 2: {{ hypothesis2.summary }}
    Novelty: {{ hypothesis2.novelty_claim }}

    Comparison Criteria:
    {% for criterion in comparison_criteria %}
    - {{ criterion }}
    {% endfor %}

    Provide detailed reasoning for your comparison decision.
  "#
}
```

#### 2. Evolution Agent Functions
**File**: `baml_src/functions.baml`
**Changes**: Add evolution-specific functions

```baml
function EvolveHypothesis(
  hypothesis: Hypothesis @description("Hypothesis to evolve"),
  evolution_strategy: string @description("Strategy: mutation, recombination, selection"),
  fitness_criteria: string[] @description("Criteria for fitness evaluation"),
  mutation_rate: float @description("Rate of mutation (0-1)")
) -> Hypothesis {
  client ProductionClient

  prompt #"
    {{ _.role("system") }}
    You are a research evolution specialist who improves hypotheses through {{ evolution_strategy }}.
    You apply evolutionary principles to enhance scientific hypotheses systematically.

    {{ _.role("user") }}
    Evolve this hypothesis using {{ evolution_strategy }} strategy:

    Original: {{ hypothesis.summary }}
    Description: {{ hypothesis.full_description }}

    Fitness Criteria:
    {% for criterion in fitness_criteria %}
    - {{ criterion }}
    {% endfor %}

    Mutation Rate: {{ mutation_rate }}

    Generate an evolved version that improves on the original.
  "#
}

function CrossoverHypotheses(
  parent1: Hypothesis @description("First parent hypothesis"),
  parent2: Hypothesis @description("Second parent hypothesis"),
  crossover_points: string[] @description("Aspects to combine: methodology, assumptions, evidence")
) -> Hypothesis {
  client ProductionClient

  prompt #"
    {{ _.role("system") }}
    You are a genetic algorithm specialist who combines the best aspects of two hypotheses.
    You create novel hypotheses by intelligently merging complementary insights.

    {{ _.role("user") }}
    Combine these hypotheses at the specified crossover points:

    Parent 1: {{ parent1.summary }}
    {{ parent1.full_description }}

    Parent 2: {{ parent2.summary }}
    {{ parent2.full_description }}

    Crossover Points:
    {% for point in crossover_points %}
    - {{ point }}
    {% endfor %}

    Generate a novel hypothesis that combines the best aspects of both parents.
  "#
}
```

#### 3. Proximity and Meta-Review Functions
**File**: `baml_src/functions.baml`
**Changes**: Add remaining functions for Phases 14-15

```baml
function GenerateClusterSummary(
  hypotheses: Hypothesis[] @description("Hypotheses in the cluster"),
  cluster_theme: string @description("Common theme or pattern"),
  analysis_depth: string @description("Level of analysis: surface, detailed, comprehensive")
) -> ResearchPatterns {
  client ProductionClient

  prompt #"
    {{ _.role("system") }}
    You are a research cluster analyst who identifies patterns and themes across related hypotheses.
    You provide {{ analysis_depth }} analysis of hypothesis clusters.

    {{ _.role("user") }}
    Analyze this cluster of hypotheses with theme: {{ cluster_theme }}

    Hypotheses in cluster:
    {% for hyp in hypotheses %}
    - {{ hyp.summary }} ({{ hyp.category }})
    {% endfor %}

    Provide a comprehensive cluster summary identifying patterns, relationships, and insights.
  "#
}

function SynthesizeFindings(
  research_corpus: map<string, string> @description("Research findings to synthesize"),
  synthesis_focus: string @description("Focus area for synthesis"),
  output_format: string @description("Format: narrative, structured, executive_summary")
) -> ResearchPatterns {
  client ProductionClient

  prompt #"
    {{ _.role("system") }}
    You are a research synthesis expert who creates comprehensive overviews of research findings.
    You excel at identifying key insights and presenting them in {{ output_format }} format.

    {{ _.role("user") }}
    Synthesize these research findings focusing on {{ synthesis_focus }}:

    {% for key, content in research_corpus %}
    {{ key }}: {{ content }}
    {% endfor %}

    Create a comprehensive synthesis that captures key insights, patterns, and implications.
  "#
}
```

### Success Criteria:

#### Automated Verification:
- [ ] All new BAML functions compile: `baml generate`
- [ ] BAMLWrapper methods added for all new functions
- [ ] All tests pass: `python -m pytest tests/ -v`
- [ ] Type checking passes: `mypy src/`

#### Manual Verification:
- [ ] All agent phases 12-15 have required BAML functions available
- [ ] Functions generate appropriate responses for their specific domains
- [ ] Integration with future agent implementations works correctly

## Testing Strategy

### Unit Tests:
- Mock all new BAML functions in `tests/conftest.py`
- Test BAMLWrapper methods with proper error handling
- Validate type conversions and edge cases
- Test streaming functionality with mock data

### Integration Tests:
- End-to-end testing of each new BAML function
- Parallel execution testing with real performance metrics
- Error handling validation with enhanced debugging
- Streaming response validation

### Manual Testing Steps:
1. Generate BAML client and verify no compilation errors
2. Test each new function individually with realistic parameters
3. Verify enhanced error handling provides useful debugging information
4. Test streaming functionality with cancellation and partial results
5. Validate parallel testing performance improvements
6. Ensure all agent phases can access their required functions

## Performance Considerations

### BAML 0.209.0 Optimizations:
- 6x improvement in trace upload performance for debugging
- Enhanced streaming latencies for real-time processing
- Better memory management reducing resource usage
- Cost optimization features reducing inference costs by 2/3

### Implementation Optimizations:
- Parallel testing reduces development cycle time significantly
- Streaming reduces perceived latency for long-form generation
- Enhanced error handling reduces debugging time
- Retry mechanisms improve reliability

## Migration Notes

### BAML Client Regeneration:
- All phases require `baml generate` after function additions
- Generated client maintains backward compatibility
- Existing function signatures remain unchanged

### Testing Migration:
- New parallel testing is opt-in and backward compatible
- Existing tests continue to work without modification
- Enhanced error handling is non-breaking

### Environment Configuration:
- No changes required to existing BAML environment variables
- New debugging features are automatically available
- Streaming capabilities are opt-in per function

## References

- Original research: `thoughts/shared/research/2025-09-30-baml-integration-improvements.md`
- BAML 0.209.0 documentation: https://docs.boundaryml.com/home
- Current implementation: `src/llm/baml_wrapper.py:38-342`
- Test expectations: `tests/integration/test_expectations.json`
- BAML function patterns: `baml_src/functions.baml:1-436`