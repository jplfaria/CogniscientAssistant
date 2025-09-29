# BAML Testing Strategy

## Overview
This document outlines the testing strategy for BAML integration to prevent test collection failures and ensure smooth implementation across all phases.

## Problem Statement
When BAML client code is imported in tests, it can fail if:
1. BAML hasn't been compiled (`baml_client` package doesn't exist)
2. The import path structure doesn't match the mock structure
3. Integration tests try to use actual BAML types that are mocked

## Solution Approach

### 1. Centralized BAML Mocking in conftest.py
The root `tests/conftest.py` provides comprehensive BAML mocking that:
- Creates the nested module structure (`baml_client.baml_client`)
- Provides mock implementations of all BAML functions as AsyncMock
- Creates mock type classes that can be used with `spec=`
- Registers all modules in `sys.modules` before any imports

### 2. Test Categories

#### Unit Tests
- Should use mocked BAML client from conftest.py
- Never import actual BAML types directly
- Mock return values at the BAMLWrapper level

#### Integration Tests  
- Can import BAML types but must handle them being mocked
- Should focus on testing integration between components
- For actual BAML testing, use the `@pytest.mark.real_llm` decorator

#### Real LLM Tests
- Marked with `@pytest.mark.real_llm`
- Only run with `--real-llm` flag
- Import and use actual BAML client
- Test actual AI behaviors, not mocked responses

### 3. Implementation Guidelines

#### When Adding New BAML Functions
1. Add the function mock to conftest.py:
   ```python
   mock_b.NewFunction = AsyncMock()
   ```

2. Add any new types to the mock types:
   ```python
   mock_types.NewType = type('NewType', (), {})
   ```

3. If the type is an enum, mock it appropriately:
   ```python
   mock_types.NewEnum = MagicMock()
   mock_types.NewEnum.Value1 = "Value1"
   mock_types.NewEnum.Value2 = "Value2"
   ```

#### When Writing Tests
1. **Unit tests**: Mock at the method level
   ```python
   wrapper = BAMLWrapper()
   wrapper.generate_hypothesis = AsyncMock(return_value=mock_hypothesis)
   ```

2. **Integration tests**: Mock the BAML client responses
   ```python
   from unittest.mock import patch
   
   @patch('baml_client.baml_client.b.GenerateHypothesis')
   async def test_integration(mock_generate):
       mock_generate.return_value = create_mock_hypothesis()
       # Test the integration
   ```

3. **Real LLM tests**: No mocking needed
   ```python
   @pytest.mark.real_llm
   async def test_real_generation():
       # This will use actual BAML client
       result = await b.GenerateHypothesis(...)
   ```

### 4. Future-Proofing

As we implement Phases 11-17, each adding new agents with BAML dependencies:

1. **Before each phase**: Review what BAML functions will be added
2. **Update conftest.py**: Add mocks for new functions and types
3. **Test first**: Write tests with mocks before implementing
4. **Document changes**: Update this strategy doc with new patterns

### 5. Common Pitfalls to Avoid

1. **Don't add conftest.py files in subdirectories** that override BAML mocking
2. **Don't import BAML types in test files** unless necessary
3. **Don't forget to mock new BAML functions** when adding them
4. **Don't mix real and mocked BAML** in the same test run

### 6. Debugging Import Issues

If you encounter BAML import errors:

1. Check if the import path matches the mock structure
2. Verify all required types are mocked in conftest.py
3. Ensure conftest.py runs before any BAML imports
4. Look for any local conftest.py files that might interfere

## Quick Reference

### Adding a New BAML Function
```python
# In conftest.py pytest_configure():
mock_b.YourNewFunction = AsyncMock()
```

### Adding a New BAML Type
```python
# In conftest.py pytest_configure():
mock_types.YourNewType = type('YourNewType', (), {})
```

### Mocking BAML in Tests
```python
# In your test file:
from unittest.mock import patch

@patch('baml_client.baml_client.b.YourFunction')
async def test_something(mock_func):
    mock_func.return_value = your_mock_data
```

## Maintenance Checklist

Before each implementation phase:
- [ ] Review specs for new BAML functions
- [ ] Update conftest.py with new mocks
- [ ] Test that all tests still collect properly
- [ ] Document any new patterns discovered