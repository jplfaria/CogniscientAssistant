# Development Scripts

Scripts to support the iterative development workflow.

## Scripts

### setup-dev.sh
Sets up the development environment with either uv or pip.

**Features:**
- Detects and uses uv if available (faster)
- Falls back to standard pip if uv not found
- Creates virtual environment
- Installs all dependencies including dev extras

**Usage:**
```bash
./scripts/development/setup-dev.sh
```

### start-argo-proxy.sh
Starts the Argo proxy server for LLM access.

**Features:**
- Configures Argo Gateway connection
- Sets up API endpoints
- Manages authentication

**Usage:**
```bash
./scripts/development/start-argo-proxy.sh
```

### run-implementation-loop.sh
The main development loop that automates the implementation process with Claude.

**Features:**
- Runs Claude to implement next tasks from IMPLEMENTATION_PLAN.md
- Enforces quality gates (tests must pass, coverage > 80%)
- Runs integration tests for completed phases
- Automatically logs all output to `.implementation_logs/`
- Detects regressions and implementation errors

**Usage:**
```bash
./scripts/development/run-implementation-loop.sh
```

**Output:**
- Logs saved to `.implementation_logs/iteration_<N>_<status>_<timestamp>.log`
- Latest logs symlinked as `latest_success.log` or `latest_failed.log`

### view-loop-logs.sh
Interactive viewer for implementation loop logs.

**Features:**
- View latest successful/failed iterations
- Search for specific test failures
- List all iteration logs
- Interactive menu system

**Usage:**
```bash
# Interactive menu
./scripts/development/view-loop-logs.sh

# View latest successful iteration
./scripts/development/view-loop-logs.sh latest

# View latest failed iteration
./scripts/development/view-loop-logs.sh failed

# View all test failures
./scripts/development/view-loop-logs.sh failures

# List all logs
./scripts/development/view-loop-logs.sh list

# View specific log by number
./scripts/development/view-loop-logs.sh 3
```

## Logs Location

All logs are stored in `.implementation_logs/` at the project root:
```
.implementation_logs/
├── iteration_1_success_2024-01-19_10-30-00.log
├── iteration_2_failed_2024-01-19_10-35-00.log
├── latest_success.log -> iteration_1_success_2024-01-19_10-30-00.log
└── latest_failed.log -> iteration_2_failed_2024-01-19_10-35-00.log
```