# AI Co-Scientist Development Guide

This document covers the implementation details, development workflow, and technical architecture for contributors and developers.

## 📊 Implementation Status

### Current Phase: 10/17 Complete

The project follows a 17-phase implementation plan, with each phase building on the previous ones.

#### ✅ Completed Phases (1-10)

1. **Project Setup** - Development environment, dependencies, initial structure
2. **Core Models** - Task, Hypothesis, Review, Citation data models
3. **Task Queue** - Complete queue operations with worker management and persistence
4. **Context Memory** - Hierarchical storage with checkpoints and conflict resolution
5. **Safety Framework** - Lightweight safety logging and metrics system
6. **LLM Abstraction** - Provider-agnostic interface for LLM interactions
7. **BAML Infrastructure** - Schema compilation and client generation
8. **Argo Gateway Integration** - Production LLM access with health monitoring
9. **Supervisor Agent** - Task orchestration with adaptive resource allocation
10. **Generation Agent** - Hypothesis generation with multiple strategies

#### 🔄 Upcoming Phases (11-17)

11. **Reflection Agent** - Hypothesis review and critique system
12. **Ranking Agent** - Tournament-based hypothesis evaluation
13. **Evolution Agent** - Hypothesis enhancement and refinement
14. **Proximity Agent** - Clustering and similarity analysis
15. **Meta-Review Agent** - Cross-hypothesis synthesis
16. **Natural Language Interface** - CLI and user interaction
17. **Integration and Polish** - Final integration and optimization

## 🛠️ Development Workflow

### AI-Assisted Development Loop

This project uses an innovative AI-assisted development approach:

```bash
# Run the development loop
./scripts/development/run-implementation-loop.sh

# Or run continuously
./scripts/development/run-implementation-loop.sh --letitrip

# View implementation logs
./scripts/development/view-loop-logs.sh
```

### Context Optimization (ACE-FCA)

The development loop includes advanced context optimization that reduces token usage by 66%:

```bash
# Check optimization status
./scripts/development/run-implementation-loop.sh --status

# View optimization report
./scripts/development/run-implementation-loop.sh --report

# Manual control
./scripts/development/run-implementation-loop.sh --enable-optimization
./scripts/development/run-implementation-loop.sh --disable-optimization
```

### Test-Driven Development

All development follows TDD principles:

1. Write failing tests first
2. Implement minimal code to pass
3. Ensure ≥80% test coverage
4. Integration tests validate workflows

```bash
# Run all tests
pytest tests/

# Run unit tests with coverage
pytest tests/unit/ --cov=src --cov-fail-under=80

# Run integration tests
pytest tests/integration/

# Run real LLM tests (manual, requires API access)
pytest tests/integration/*_real.py -v --real-llm
```

## 🏗️ Architecture Details

### Directory Structure

```
src/
├── core/                   # Core infrastructure
│   ├── models.py          # Data models
│   ├── task_queue.py      # Task queue implementation
│   ├── context_memory.py  # Memory management
│   └── safety.py          # Safety framework
├── llm/                   # LLM infrastructure
│   ├── base.py           # Abstract interface
│   ├── argo_provider.py  # Argo Gateway provider
│   ├── baml_wrapper.py   # BAML integration
│   └── circuit_breaker.py # Reliability patterns
├── agents/                # Agent implementations
│   ├── supervisor.py     # Orchestration agent
│   └── generation.py     # Hypothesis generation
└── utils/                 # Utilities
    ├── context_relevance.py     # ACE-FCA optimization
    └── optimization_analytics.py # Performance analytics
```

### BAML Integration

All LLM interactions go through BAML for structured, type-safe communication:

```
baml_src/
├── models.baml       # Data structures
├── functions.baml    # LLM functions
├── clients.baml      # Client configurations
└── environment.baml  # Environment variables
```

Key BAML patterns:
- Always use both `system` and `user` roles in prompts
- Model-specific parameter handling (e.g., `max_completion_tokens` for o-series)
- Comprehensive mocking in `tests/conftest.py`

### Test Organization

```
tests/
├── unit/              # Component tests
│   └── test_*.py     # One file per module
├── integration/       # Workflow tests
│   └── test_phase*_*.py  # Phase-based testing
└── conftest.py       # BAML mocking infrastructure
```

Test expectations are defined in `test_expectations.json`:
- `must_pass`: Critical tests that block progress
- `may_fail`: Tests allowed to fail (future components)
- `real_llm_tests`: Behavioral validation tests

## 🔧 Key Technologies

### Core Stack
- **Python 3.11+** - Modern async/await patterns
- **BAML** - Structured LLM interactions
- **pytest** - Comprehensive testing
- **uv** - Fast package management
- **mypy** - Static type checking
- **ruff** - Fast Python linting

### LLM Infrastructure
- **Argo Gateway** - Unified LLM access
- **Circuit Breakers** - Fault tolerance
- **Rate Limiting** - Cost control
- **Multiple Models** - GPT-o3, Claude, Gemini support

### Development Tools
- **ACE-FCA** - Context optimization (66% reduction)
- **Automated Loop** - AI-assisted implementation
- **Quality Gates** - Enforced standards
- **Integration Testing** - Phase-based validation

## 📝 Development Guidelines

### Code Style
- Follow PEP 8 with 88-character line limit (Black formatting)
- Type hints for all function signatures
- Comprehensive docstrings for public APIs
- No comments unless absolutely necessary

### Commit Convention
```
feat: Add new feature
fix: Fix bug
refactor: Refactor code
test: Add/update tests
docs: Update documentation
chore: Maintenance tasks
```

### Quality Requirements
- All tests must pass
- ≥80% code coverage (unit tests)
- No linting errors (ruff)
- No type errors (mypy)

### BAML Function Requirements
All BAML functions MUST use both system and user roles:

```baml
function ExampleFunction(input: string) -> Output {
  client ProductionClient

  prompt #"
    {{ _.role("system") }}
    You are an expert at [task].

    {{ _.role("user") }}
    Please help with: {{ input }}
  "#
}
```

## 🚀 Getting Started as a Developer

### 1. Environment Setup
```bash
# Clone and setup
git clone <repository>
cd cogniscient-assistant
./scripts/development/setup-dev.sh

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Activate environment
source .venv/bin/activate
```

### 2. Understanding the Codebase
1. Read specifications in `specs/` directory
2. Review `IMPLEMENTATION_PLAN.md` for task breakdown
3. Check `test_expectations.json` for test requirements
4. Study existing implementations in `src/`

### 3. Making Contributions
1. Pick an unchecked task from `IMPLEMENTATION_PLAN.md`
2. Write tests first (TDD)
3. Implement minimal code to pass
4. Ensure quality gates pass
5. Submit PR with clear description

### 4. Running the Development Loop
```bash
# For AI-assisted implementation
./scripts/development/run-implementation-loop.sh

# This will:
# 1. Read specifications
# 2. Implement next task
# 3. Write and run tests
# 4. Commit on success
```

## 📊 Metrics and Analytics

### Context Optimization Metrics
```bash
# View optimization effectiveness
python src/utils/optimization_analytics.py --report

# Get latest metrics
python src/utils/optimization_analytics.py --latest 10

# Export as JSON
python src/utils/optimization_analytics.py --json
```

### Test Coverage Reports
```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html

# Terminal coverage summary
pytest --cov=src --cov-report=term-missing
```

## 🐛 Debugging

### Common Issues

#### BAML Compilation Errors
```bash
# Regenerate BAML clients
cd baml_src && baml generate
```

#### Argo Gateway Connection
```bash
# Check proxy status
./scripts/argo-proxy.sh status

# Restart proxy
./scripts/argo-proxy.sh restart
```

#### Test Failures
```bash
# Run specific test with verbose output
pytest tests/unit/test_specific.py::test_name -vv

# Debug with breakpoint
pytest tests/unit/test_specific.py --pdb
```

## 📚 Additional Resources

### Documentation
- [AI-Assisted Development Workflow](docs/AI_ASSISTED_DEVELOPMENT_WORKFLOW.md) - Complete development methodology
- [BAML Testing Strategy](docs/BAML_TESTING_STRATEGY.md) - BAML testing patterns
- [Argo Gateway Guide](docs/argo-gateway-complete-guide.md) - Argo setup and usage
- [Test Coverage Strategy](docs/test-coverage-strategy.md) - Testing requirements

### Specifications
- All behavioral specifications in `specs/` directory
- Each spec defines WHAT, not HOW
- Implementation must match specs exactly

### Planning Documents
- `IMPLEMENTATION_PLAN.md` - Task breakdown and progress
- `INTEGRATION_TESTING_PLAN.md` - Testing strategy
- `thoughts/` - Development insights and planning

## 🤝 Contributing Process

1. **Find a Task**: Check `IMPLEMENTATION_PLAN.md` for unchecked items
2. **Understand Context**: Read relevant specs and existing code
3. **Write Tests First**: Follow TDD principles
4. **Implement**: Write minimal code to pass tests
5. **Validate**: Ensure all quality gates pass
6. **Document**: Update relevant documentation
7. **Submit PR**: Include clear description and test results

## 📈 Project Metrics

### Current Statistics
- **Specifications**: 28 complete behavioral specs
- **Test Files**: 89 (67 unit, 22 integration)
- **Code Coverage**: Target ≥80% maintained
- **Context Optimization**: 66% reduction achieved
- **Implementation Progress**: Phase 10/17 complete

### Performance Achievements
- **Development Speed**: AI-assisted loop enables rapid iteration
- **Quality Maintenance**: All quality gates enforced
- **Token Efficiency**: 66% reduction via ACE-FCA
- **Test Reliability**: Comprehensive mocking infrastructure

---

For questions about the product and its capabilities, see [README.md](README.md).
For detailed workflow documentation, see [AI_ASSISTED_DEVELOPMENT_WORKFLOW.md](docs/AI_ASSISTED_DEVELOPMENT_WORKFLOW.md).