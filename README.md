# AI Co-Scientist

A multi-agent system for scientific hypothesis generation and research automation.

## Project Status

✅ **Specification Phase**: Complete (28 specs)  
🚧 **Implementation Phase**: In Progress (Phase 3 - Queue Mechanics)

## Quick Start for Implementation

```bash
# Run the validated implementation loop
./run-implementation-loop-validated.sh

# Or run continuously with automatic progression
./run-implementation-loop-validated.sh --letitrip
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
└── run-implementation-loop-validated.sh  # Primary implementation automation

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
- pytest for testing
- Argo Gateway for model access

## Safety First

All components implement multi-layer safety checks as specified in spec 020.