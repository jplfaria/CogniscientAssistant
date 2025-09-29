# Testing Scripts

Scripts for running various test suites and validations.

## Scripts

### test-argo-models.py
Tests connectivity and access to Argo Gateway models.

**Features:**
- Verifies Argo proxy is running
- Tests access to available models
- Validates API key and permissions
- Checks model response times

**Usage:**
```bash
python ./scripts/testing/test-argo-models.py
```

### run-baml-tests.sh
Runs BAML-specific unit tests and provides a summary.

**Features:**
- Runs all tests matching `test_baml*.py`
- Provides pass/fail summary
- Logs full output to `.baml_test_results.log`

**Usage:**
```bash
./scripts/testing/run-baml-tests.sh
```

**Output:**
- Full test output saved to `.baml_test_results.log`
- Summary shows count of passed/failed tests
- Exit code 0 if all pass, 1 if any fail

### run-all-tests.sh (coming soon)
Will run the complete test suite including:
- Unit tests
- Integration tests
- Coverage report
- Type checking
- Linting

## Test Organization

Tests are organized in the `tests/` directory:
```
tests/
├── unit/               # Unit tests for individual components
├── integration/        # Integration tests by phase
├── baml/              # BAML-specific tests
└── test_expectations.json  # Expected test results by phase
```

## Coverage Requirements

- Minimum coverage: 80%
- Coverage checked automatically in implementation loop
- Run coverage manually: `pytest --cov=src --cov-report=term-missing`