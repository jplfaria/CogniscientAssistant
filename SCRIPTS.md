# Script Usage Guide

This project includes several utility scripts organized in the `scripts/` directory.

## Quick Access

For convenience, symlinks are provided in the root:
- `./run-loop.sh` → Main implementation loop
- `./view-logs.sh` → View implementation logs

## Full Script Organization

```
scripts/
├── development/
│   ├── run-implementation-loop.sh   # Main implementation loop with quality gates
│   └── view-loop-logs.sh           # Interactive log viewer
├── testing/
│   └── run-baml-tests.sh           # Run BAML unit tests
└── maintenance/
    └── fix-baml-issues.py          # Fix BAML configuration issues
```

## Common Workflows

### 1. Running the Implementation Loop
```bash
# From project root
./run-loop.sh

# Or full path
./scripts/development/run-implementation-loop.sh
```

### 2. Viewing Logs
```bash
# View latest logs
./view-logs.sh

# View specific failure
./view-logs.sh failed

# Search for test failures
./view-logs.sh failures
```

### 3. Running Tests
```bash
# Run BAML tests
./scripts/testing/run-baml-tests.sh

# Run all tests with coverage
pytest --cov=src --cov-report=term-missing
```

### 4. Fixing BAML Issues
```bash
# If BAML tests fail
python ./scripts/maintenance/fix-baml-issues.py
```

## Logs Location

- Implementation logs: `.implementation_logs/`
- Test results: Check script output or `.baml_test_results.log`

See `scripts/README.md` for detailed documentation.