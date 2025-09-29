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
│   ├── view-loop-logs.sh           # Interactive log viewer
│   └── setup-dev.sh                # Development environment setup
├── testing/
│   └── run-baml-tests.sh           # Run BAML unit tests
└── argo-proxy.sh                   # Argo Gateway proxy management
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

### 4. Managing Argo Proxy
```bash
# Start Argo proxy
./scripts/argo-proxy.sh start

# Check proxy status
./scripts/argo-proxy.sh status

# Stop proxy
./scripts/argo-proxy.sh stop
```

## Logs Location

- Implementation logs: `.implementation_logs/`
- Test results: Check script output or `.baml_test_results.log`

See `scripts/README.md` for detailed documentation.