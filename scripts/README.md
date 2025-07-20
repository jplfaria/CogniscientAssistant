# Scripts Directory

This directory contains utility scripts for the AI Co-Scientist project.

## Directory Structure

```
scripts/
├── development/     # Scripts for development workflow
├── testing/         # Scripts for running tests and validation
└── maintenance/     # Scripts for maintenance and fixes
```

## Subdirectories

### development/
Contains scripts that help with the development workflow:
- `run-implementation-loop.sh` - Main implementation loop with quality gates
- `view-loop-logs.sh` - Interactive viewer for implementation logs

### testing/
Contains scripts for testing and validation:
- `run-baml-tests.sh` - Run BAML-specific unit tests
- `run-all-tests.sh` - Run complete test suite

### maintenance/
Contains scripts for fixes and maintenance:
- `fix-baml-issues.py` - Automated fixes for BAML configuration issues

## Usage

All scripts are executable. Run them from the project root:

```bash
# Development workflow
./scripts/development/run-implementation-loop.sh

# Testing
./scripts/testing/run-baml-tests.sh

# Maintenance
python ./scripts/maintenance/fix-baml-issues.py
```

## Logs

Implementation logs are stored in `.implementation_logs/` at the project root.
Test results are stored in the respective script directories.