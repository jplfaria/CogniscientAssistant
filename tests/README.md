# AI Co-Scientist Test Suite

## Overview

This directory contains comprehensive tests for the AI Co-Scientist system, including unit tests, integration tests, and real LLM behavior tests.

## Test Organization

```
tests/
├── unit/                # Unit tests for individual components
├── integration/         # Integration tests for system workflows
├── conftest.py         # Shared test fixtures and BAML mocks
└── test_expectations.json  # Integration test expectations
```

### Test Types

1. **Unit Tests** (`unit/`): Test individual components in isolation
2. **Integration Tests** (`integration/`): Test system workflows and agent interactions
3. **Real LLM Tests** (`*_real.py`): Validate actual AI behavior with real models

## Running Tests

### All Tests (Default - Uses Mocks)
```bash
pytest tests/ -v
```

### Unit Tests Only
```bash
pytest tests/unit/ -v
```

### Integration Tests Only
```bash
pytest tests/integration/ -v
```

### Real LLM Tests (Requires Argo Gateway)
```bash
# Ensure Argo proxy is running first
./scripts/manage-argo-proxy.sh start

# Run real LLM tests
pytest tests/integration/*_real.py -v --real-llm
```

### Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html
# View report at htmlcov/index.html
```

## Test Structure

### Unit Test Naming
- File: `tests/unit/test_<module_name>.py`
- Example: `test_task_queue.py`, `test_generation_agent.py`
- Tests individual methods and edge cases

### Integration Test Naming
- File: `tests/integration/test_phase<N>_<feature>.py`
- Example: `test_phase3_queue_workflow.py`, `test_phase10_generation_agent.py`
- Tests complete workflows and agent interactions

### Real LLM Test Naming
- File: `tests/integration/test_phase<N>_<feature>_real.py`
- Decorator: `@pytest.mark.real_llm`
- Tests behavioral expectations with actual models

## BAML Mock Structure

The test suite uses comprehensive BAML mocks defined in `conftest.py`:

### Mock Types

1. **MockResponse**: Basic response structure
```python
@dataclass
class MockResponse:
    content: str = "Mocked response"
```

2. **MockBAMLType**: Complex BAML type responses
```python
@dataclass
class MockBAMLType:
    field1: str
    field2: List[str]
    # Implements to_dict() for serialization
```

3. **MockEnumValue**: Enum type responses
```python
@dataclass
class MockEnumValue:
    value: str
    # Used for GenerationMethod, SafetyCheck, etc.
```

### Mock Functions

Key BAML function mocks:

- **GenerateHypothesis**: Returns hypothesis with generation_method routing
- **ReviewHypothesis**: Provides review scores and feedback
- **PlanResearch**: Creates research subtasks
- **RankHypotheses**: Tournament-style ranking
- **CheckSafety**: Safety validation
- **SearchWeb**: Simulated web search results

### Generation Method Routing

The mocks implement realistic routing based on input:
```python
# In mock_generate_hypothesis
if "literature" in description.lower():
    generation_method = "LITERATURE"
elif "debate" in description.lower():
    generation_method = "DEBATE"
elif "assumption" in description.lower():
    generation_method = "ASSUMPTION"
elif "feedback" in description.lower():
    generation_method = "FEEDBACK"
else:
    generation_method = "LITERATURE"  # Default
```

## Test Expectations

The `test_expectations.json` file defines:

```json
{
  "must_pass": [
    // Critical tests that block progress
    "test_phase3_task_queue_workflow",
    "test_phase4_context_memory",
    // ...
  ],
  "may_fail": [
    // Tests allowed to fail (waiting for components)
    "test_hypothesis_diversity",
    "test_generation_creativity_metrics",
    // ...
  ],
  "real_llm_tests": [
    // Tests requiring actual models
    "test_hypothesis_creativity",
    "test_hypothesis_scientific_validity",
    // ...
  ],
  "must_use_baml": {
    // Methods that MUST call BAML functions
    "GenerationAgent": [
      "generate_hypothesis",
      "literature_based_generation"
    ],
    // ...
  }
}
```

## Writing Tests

### Unit Test Example
```python
# tests/unit/test_generation_agent.py
import pytest
from src.agents.generation import GenerationAgent

class TestGenerationAgent:
    @pytest.mark.asyncio
    async def test_initialization(self):
        agent = GenerationAgent()
        assert agent.model_name == "gpt5"  # New default
        assert agent.generation_strategies

    @pytest.mark.asyncio
    async def test_literature_generation(self):
        agent = GenerationAgent()
        hypothesis = await agent.generate_hypothesis(
            "Test literature-based generation"
        )
        assert hypothesis.generation_method == "LITERATURE"
```

### Integration Test Example
```python
# tests/integration/test_phase10_generation_agent.py
import pytest
from src.agents.generation import GenerationAgent
from src.core.models import ResearchContext

class TestPhase10GenerationIntegration:
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        agent = GenerationAgent()
        context = ResearchContext(topic="quantum computing")

        # Test full generation workflow
        hypothesis = await agent.generate_hypothesis(
            goal="Novel quantum error correction",
            context=context
        )

        assert hypothesis.title
        assert hypothesis.description
        assert hypothesis.generation_method
```

### Real LLM Test Example
```python
# tests/integration/test_phase10_generation_real.py
import pytest

class TestPhase10GenerationReal:
    @pytest.mark.real_llm
    @pytest.mark.asyncio
    async def test_hypothesis_creativity(self):
        """Test actual creative generation with GPT-5."""
        agent = GenerationAgent()
        hypothesis = await agent.generate_hypothesis(
            "Quantum error correction breakthrough"
        )

        # Behavioral expectations (not exact matches)
        assert len(hypothesis.description) > 100
        assert "quantum" in hypothesis.description.lower()
        # Check for reasoning markers (GPT-5 feature)
        assert any(marker in hypothesis.description.lower()
                  for marker in ["because", "therefore", "thus"])
```

## Model Configuration for Tests

### Using Environment Variables
```bash
# Test with specific model
DEFAULT_MODEL=gpt5 pytest tests/

# Test with agent overrides
GENERATION_MODEL=claudeopus41 pytest tests/unit/test_generation_agent.py

# Test with economical model
DEFAULT_MODEL=gpt5nano pytest tests/
```

### Mock Behavior by Model

The mocks adapt based on configured model:
```python
# In conftest.py
model_name = os.getenv("DEFAULT_MODEL", "gpt5")

if "gpt5" in model_name:
    # Return reasoning-focused responses
elif "claude" in model_name:
    # Return creative, nuanced responses
elif "gemini" in model_name:
    # Return comprehensive analysis
```

## Debugging Tests

### Verbose Output
```bash
pytest tests/ -vv -s
```

### Debug Specific Test
```bash
pytest tests/unit/test_generation_agent.py::TestGenerationAgent::test_literature_generation -vv
```

### Check BAML Mock Calls
```python
# In test
from unittest.mock import patch

@patch('baml_client.GenerateHypothesis')
async def test_with_spy(mock_generate):
    # Test code
    mock_generate.assert_called_once_with(
        description="Expected input"
    )
```

## Coverage Requirements

- **Minimum Coverage**: 80% for all components
- **Critical Paths**: 95% for safety mechanisms
- **Agent Coverage**: Each agent must have >85% coverage

Check coverage:
```bash
# HTML report
pytest tests/ --cov=src --cov-report=html

# Terminal report
pytest tests/ --cov=src --cov-report=term-missing
```

## Continuous Integration

Tests run automatically on:
- Pull requests
- Main branch commits
- Nightly scheduled runs

CI Configuration:
```yaml
# .github/workflows/test.yml
- name: Run Tests
  run: |
    pytest tests/unit/ -v
    pytest tests/integration/ -v
    # Real LLM tests run manually
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure PYTHONPATH includes project root
   - Check virtual environment activation

2. **BAML Mock Failures**
   - Verify mock is defined in conftest.py
   - Check function signature matches

3. **Async Test Failures**
   - Use `@pytest.mark.asyncio` decorator
   - Ensure proper await usage

4. **Real LLM Test Failures**
   - Verify Argo proxy is running
   - Check VPN connection
   - Confirm model availability

### Getting Help

- Check test output for detailed error messages
- Review conftest.py for mock implementations
- See docs/baml/BAML_TESTING_STRATEGY.md for BAML testing patterns
- Run with `-vv` for verbose output

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Mock External Services**: Use mocks for LLM calls in unit/integration tests
3. **Behavioral Testing**: Test behavior, not implementation details
4. **Clear Assertions**: Use descriptive assertion messages
5. **Cleanup**: Ensure tests clean up resources
6. **Documentation**: Document complex test scenarios

## Future Improvements

- [ ] Add performance benchmarks
- [ ] Implement load testing for agents
- [ ] Add mutation testing
- [ ] Create test data generators
- [ ] Add visual test reports