# AI Co-Scientist

A multi-agent system for scientific hypothesis generation and research automation.

## Project Status

✅ **Specification Phase**: Complete (28 specs)  
🚧 **Implementation Phase**: Starting

## Quick Start for Implementation

```bash
# Run the implementation loop
./run-implementation-loop-improved.sh

# Or run continuously
./run-implementation-loop-improved.sh --letitrip
```

## Project Structure

```
.
├── specs/                    # Complete behavioral specifications (001-028)
├── src/                      # Implementation code (to be created)
├── tests/                    # Test suite (to be created)
├── docs/                     # Documentation
│   └── spec-development/     # Historical spec development files
├── IMPLEMENTATION_PLAN.md    # Current implementation tasks
├── CLAUDE.md                 # Implementation guidelines
├── prompt.md                 # Implementation task prompt
├── BAML_SCHEMAS.md          # BAML templates for agents
└── run-implementation-loop-improved.sh  # Implementation automation

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