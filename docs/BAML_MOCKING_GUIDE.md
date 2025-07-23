# BAML Mocking Guide for Future Phases

## When Adding New BAML Functions

When implementing new phases that add BAML functions, update `/tests/conftest.py`:

1. **Add the new function mock** to the mock_b object:
```python
mock_b.YourNewFunction = AsyncMock()
```

2. **If the function returns complex data**, add a side_effect:
```python
def your_function_side_effect(*args, **kwargs):
    # Return appropriate mock data based on inputs
    return mock_response

mock_b.YourNewFunction = AsyncMock(side_effect=your_function_side_effect)
```

## When Adding New BAML Types

1. **Add the type** to mock_types:
```python
mock_types.YourNewType = MockBAMLType
```

2. **If it's an enum**, create it properly:
```python
mock_types.YourEnum = MagicMock()
mock_types.YourEnum.Value1 = MockEnumValue("Value1")
mock_types.YourEnum.Value2 = MockEnumValue("Value2")
```

## When Writing Integration Tests

1. **Don't hardcode specific content expectations** unless necessary
2. **Use the mock's actual behavior** rather than expecting specific strings
3. **Or update the mock** to return what your test needs

## Example for Future Phase

If Phase 11 (Reflection Agent) adds a `PerformReview` BAML function:

```python
# In conftest.py pytest_configure():

# Add the function mock
mock_b.PerformReview = AsyncMock()

# Add any new types
mock_types.ReviewResult = MockBAMLType
mock_types.ReviewScore = MockBAMLType

# Add side effect if needed
def perform_review_side_effect(*args, **kwargs):
    return MagicMock(
        score=0.85,
        feedback="Good hypothesis with strong evidence",
        suggestions=["Consider alternative mechanisms"],
        decision="Accept"
    )

mock_b.PerformReview = AsyncMock(side_effect=perform_review_side_effect)
```

## Preventing Integration Test Failures

1. **Check existing mocks** before writing tests that expect specific content
2. **Update mocks** to handle new test scenarios
3. **Use parameterized mocks** that adapt based on input rather than returning static content

## Key Principles

- **Mocks should be comprehensive** - cover all BAML functions and types
- **Mocks should be adaptive** - return different data based on inputs
- **Tests should be flexible** - avoid brittle string matching where possible
- **Document mock behavior** - so future implementers know what to expect