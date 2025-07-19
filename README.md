# AI Co-Scientist

A multi-agent system for scientific hypothesis generation and research automation.

## Project Status

✅ **Specification Phase**: Complete (28 specs)  
🚧 **Implementation Phase**: In Progress (Phase 4 - Context Memory)

## Development Setup

### Using uv (Recommended - Fast)

```bash
# Install uv (one time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up development environment
./scripts/development/setup-dev.sh

# Activate virtual environment
source .venv/bin/activate
```

### Using pip (Traditional)

```bash
# Set up development environment
./scripts/development/setup-dev.sh

# Activate virtual environment
source venv/bin/activate
```

### Argo Gateway Setup

The system uses Argo gateway for LLM access. See [docs/argo-setup.md](docs/argo-setup.md) for detailed setup instructions.

```bash
# Install argo-proxy
pip install argo-proxy

# Configure environment
cp .env.example .env
# Edit .env and set ARGO_USER

# Start the proxy
./scripts/start-argo-proxy.sh
```

## Quick Start for Implementation

```bash
# After environment setup, run the validated implementation loop
./run-loop.sh

# Or run continuously with automatic progression
./run-loop.sh --letitrip
```

## Project Structure

```
.
├── specs/                          # Complete behavioral specifications (001-028)
├── src/                            # Implementation code
│   └── core/                       # Core infrastructure components
│       ├── models.py               # Data models (Task, Worker, etc.)
│       └── task_queue.py           # Task queue implementation
├── tests/                          # Test suite
│   ├── unit/                       # Unit tests
│   └── integration/                # Integration test harnesses
├── docs/                           # Documentation
│   ├── spec-development/           # Historical spec development
│   ├── archive/                    # Archived workflow files
│   └── AI_ASSISTED_DEVELOPMENT_WORKFLOW.md  # Complete workflow guide
├── IMPLEMENTATION_PLAN.md          # Current implementation tasks (living document)
├── INTEGRATION_TESTING_PLAN.md     # Integration testing strategy
├── CLAUDE.md                       # Implementation guidelines for AI
├── prompt.md                       # Implementation task prompt
├── run-loop.sh                     # Quick access symlink
├── view-logs.sh                    # Quick access symlink
└── scripts/                        # Utility scripts (see SCRIPTS.md)

```

## Key Specifications

- **001-003**: System foundation and principles
- **004-006**: Multi-agent framework and task queue
- **007-012**: Core agents (Generation, Reflection, Ranking, Evolution, Proximity, Meta-review)
- **013-016**: Interfaces and tools
- **017-019**: User interaction and outputs
- **020-022**: Safety and validation
- **023-025**: Integration and deployment
- **026-028**: System completeness (timing, resources, states)

## Implementation Order

1. Project setup and structure
2. Core infrastructure (Task Queue, Context Memory)
3. Safety framework and LLM abstraction
4. Supervisor Agent
5. Specialized agents in dependency order
6. User interfaces
7. Integration testing

## Technologies

- Python 3.11+
- BAML for LLM interactions
- asyncio for concurrency
- pytest for testing (≥80% coverage required)
- Argo Gateway for model access
- uv for package management (optional but recommended)
- mypy for type checking
- ruff for linting

## Safety First

All components implement multi-layer safety checks as specified in spec 020.