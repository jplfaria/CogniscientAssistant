# Test Coverage Strategy

## Overview

This document explains our test coverage approach, which separates unit and integration test coverage to provide more meaningful quality metrics.

## Coverage Requirements

### Unit Tests (80% threshold)
- **Location**: `tests/unit/`
- **Purpose**: Test individual components in isolation
- **Coverage Requirement**: Must achieve ≥80% code coverage
- **Enforcement**: Blocks iteration if threshold not met

### Integration Tests (Informational)
- **Location**: `tests/integration/`
- **Purpose**: Test system workflows and component interactions
- **Coverage Requirement**: No threshold - informational only
- **Enforcement**: Non-blocking, provides early warning of integration issues

## Why Separate Coverage?

1. **Different Test Goals**:
   - Unit tests should comprehensively test individual functions/classes
   - Integration tests verify workflows work correctly, not every code path

2. **More Accurate Metrics**:
   - Unit test coverage shows how well individual components are tested
   - Combined coverage can mask poorly tested components

3. **Better Development Flow**:
   - Developers focus on unit test coverage for their components
   - Integration tests catch interaction issues without blocking progress

## Implementation Details

### Run Script Changes
The `run-loop.sh` script now:
1. Runs all tests first to catch failures
2. Checks unit test coverage against 80% threshold
3. Runs integration test coverage for information only

### Configuration
- `pyproject.toml` includes test markers for categorization
- Coverage excludes `__init__.py` files and test directories
- Common non-testable patterns are excluded (TYPE_CHECKING, NotImplementedError, etc.)

## Running Tests Manually

```bash
# Run all tests
pytest tests/

# Run unit tests with coverage
pytest tests/unit/ --cov=src --cov-report=term-missing

# Run integration tests with coverage
pytest tests/integration/ --cov=src --cov-report=term-missing

# Run specific test categories
pytest -m unit        # Run tests marked as unit
pytest -m integration # Run tests marked as integration
```

## Future Improvements

1. Add per-module coverage requirements for critical components
2. Create coverage badges for unit and integration tests separately
3. Set up CI/CD to track coverage trends over time