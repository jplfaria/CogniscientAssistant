# AI Co-Scientist Integration Testing Plan

This document outlines the integration testing strategy for the AI Co-Scientist implementation. Integration tests validate that implemented components work together to achieve the system's goals.

## Core Testing Principles

### 1. Test Scripts, Not Production Code
- **Location**: All integration tests live in `tests/integration/` or `scripts/testing/`
- **No Production Modifications**: Never add functionality to `src/` just for testing
- **Use Existing Interfaces**: Test only what's already built using public APIs
- **Example**:
  ```python
  # GOOD: tests/integration/phase3_queue_simulation.py
  from src.core.task_queue import TaskQueue  # Use existing interface
  
  # BAD: Adding test-only methods to src/core/task_queue.py
  def get_test_statistics():  # DON'T DO THIS
  ```

### 2. Test Expectations Configuration
The file `tests/integration/test_expectations.json` defines test requirements for each phase:
- **must_pass**: Tests that MUST pass for the phase to be considered complete
- **may_fail**: Tests that are allowed to fail (usually waiting for future components)

This allows the validation loop to distinguish between:
- Critical failures that block progress
- Expected failures that are informational only
- Unexpected failures that need investigation

### 3. Phase-Aligned Testing
- Tests are organized by implementation phase
- Only test functionality that has been implemented
- Tests build progressively as more components are added
- Integration tests start at Phase 3 (first integrable components)

### 4. Real Workflow Validation
- Test actual AI Co-Scientist use cases
- Simulate agent interactions without implementing agents
- Validate that components integrate correctly

## Testing Milestones by Phase

### Why Integration Tests Start at Phase 3
- **Phase 1**: Project setup - no code to integrate
- **Phase 2**: Core models - unit tests only, no integration needed
- **Phase 3**: First integrable component (Task Queue) - integration tests begin

### Milestone 1: Task Queue Workflow (Phase 3 - CURRENT)
**Status**: Ready to implement  
**Location**: `tests/integration/phase3_task_queue_workflow.py`

**Key Validations**:
- ✓ Can enqueue tasks with correct priorities
- ✓ Workers can register with capabilities
- ✓ Task assignment respects worker capabilities  
- ✓ Failed tasks get retried per policy
- ✓ Queue persists and recovers from disk
- ✓ Statistics accurately reflect queue state

**Test Scenarios**:
1. **Full Task Lifecycle**: Create → Enqueue → Assign → Execute → Complete
2. **Priority Handling**: High priority tasks processed first
3. **Worker Capability Matching**: Tasks assigned to capable workers only
4. **Failure Recovery**: Failed tasks retry with backoff
5. **Persistence**: Queue state survives restart

### Milestone 2: Memory + Queue Integration (Phase 4)
**Status**: Pending implementation  
**Location**: `tests/integration/phase4_memory_queue.py`

**Key Validations**:
- ✓ Memory stores task execution history
- ✓ Context retrieved for related tasks
- ✓ Hypothesis evolution tracked
- ✓ Thread isolation works correctly

**Test Scenarios**:
1. **Task Context Storage**: Task results stored in memory
2. **Context Retrieval**: Related context fetched for new tasks
3. **Thread Isolation**: Different threads don't interfere
4. **Evolution Tracking**: Hypothesis changes tracked over time

### Milestone 3: Safety Framework (Phase 5)
**Status**: Pending implementation  
**Location**: `tests/integration/phase5_safety_framework.py`

**Key Validations**:
- ✓ Safety checks integrated with queue
- ✓ Research goal validation works
- ✓ Hypothesis safety evaluation
- ✓ Pattern monitoring functions

**Test Scenarios**:
1. **Safety Integration**: Queue respects safety boundaries
2. **Goal Validation**: Unsafe research goals rejected
3. **Hypothesis Filtering**: Unsafe hypotheses blocked
4. **Monitoring**: Pattern detection works

### Milestone 4: LLM Abstraction (Phase 6)
**Status**: Pending implementation  
**Location**: `tests/integration/phase6_llm_abstraction.py`

**Key Validations**:
- ✓ LLM abstraction interface works
- ✓ Rate limiting functions
- ✓ Failover mechanism works
- ✓ Mock responses function

**Test Scenarios**:
1. **Interface Testing**: Abstraction layer works
2. **Rate Limiting**: Respects API limits
3. **Failover**: Handles LLM failures gracefully
4. **Mocking**: Test infrastructure works

### Milestone 5: BAML Infrastructure (Phase 7)
**Status**: Pending implementation  
**Location**: `tests/integration/phase7_baml_setup.py`

**Key Validations**:
- ✓ BAML schemas compile correctly
- ✓ Can call BAML functions with mocks
- ✓ Response parsing works
- ✓ Error handling functions

**Test Scenarios**:
1. **Schema Validation**: BAML files compile without errors
2. **Mock LLM Calls**: Test functions with predictable responses
3. **Error Handling**: Graceful handling of LLM errors
4. **Response Parsing**: Structured data extracted correctly

### Milestone 6: Supervisor Agent (Phase 8)
**Status**: Pending implementation  
**Location**: `tests/integration/phase8_supervisor_orchestration.py`

**Key Validations**:
- ✓ Supervisor creates correct tasks
- ✓ Tasks appear in queue with right priorities
- ✓ Supervisor tracks task completion
- ✓ Error handling works

**Test Scenarios**:
1. **Research Initiation**: Goal creates appropriate tasks
2. **Task Orchestration**: Tasks created in correct order
3. **Completion Tracking**: Supervisor knows when done
4. **Error Recovery**: Failed tasks handled appropriately

### Milestone 7: Generation Agent (Phase 9)
**Status**: Pending implementation  
**Location**: `tests/integration/phase9_generation_agent.py`

**Key Validations**:
- ✓ Generation creates valid hypotheses
- ✓ Different generation strategies work
- ✓ Web search integration functions
- ✓ Safety checks applied

**Test Scenarios**:
1. **Hypothesis Generation**: Valid hypotheses created
2. **Strategy Testing**: All strategies function
3. **External Integration**: Web search works
4. **Safety Compliance**: Unsafe content filtered

### Milestone 8: Reflection Agent (Phase 10)
**Status**: Pending implementation  
**Location**: `tests/integration/phase10_reflection_agent.py`

**Key Validations**:
- ✓ Generation creates valid hypotheses
- ✓ Reflection provides structured feedback
- ✓ Memory tracks both steps
- ✓ Queue coordinates agents

**Test Scenarios**:
1. **Hypothesis Generation**: Valid hypotheses created
2. **Reflection Process**: Structured reviews generated
3. **Pipeline Flow**: Generation → Reflection works
4. **Context Passing**: Information flows between agents

### Milestone 9: Ranking Agent (Phase 11)
**Status**: Pending implementation  
**Location**: `tests/integration/phase11_ranking_agent.py`

**Key Validations**:
- ✓ Elo ratings update correctly
- ✓ Tournament pairs hypotheses properly
- ✓ Rankings reflect quality
- ✓ History preserved

**Test Scenarios**:
1. **Tournament Setup**: Hypotheses paired correctly
2. **Elo Calculation**: Ratings update properly
3. **Ranking Accuracy**: Better hypotheses rank higher
4. **History Tracking**: All comparisons recorded

### Milestone 10: Evolution Agent (Phase 12)
**Status**: Pending implementation  
**Location**: `tests/integration/phase12_evolution_agent.py`

**Key Validations**:
- ✓ Evolution strategies work
- ✓ Hypothesis enhancement functions
- ✓ Combination logic works
- ✓ Quality improves

**Test Scenarios**:
1. **Enhancement**: Hypotheses get better
2. **Combination**: Merging works correctly
3. **Simplification**: Complexity reduction works
4. **Paradigm Shifts**: Novel approaches generated

### Milestone 11: Proximity Agent (Phase 13)
**Status**: Pending implementation  
**Location**: `tests/integration/phase13_proximity_agent.py`

**Key Validations**:
- ✓ Similarity calculations work
- ✓ Clustering functions correctly
- ✓ Integration with other agents
- ✓ Performance acceptable

**Test Scenarios**:
1. **Similarity**: Calculations are accurate
2. **Clustering**: Groups form correctly
3. **Integration**: Works with hypothesis flow
4. **Scale**: Handles many hypotheses

### Milestone 12: Meta-Review Agent (Phase 14)
**Status**: Pending implementation  
**Location**: `tests/integration/phase14_meta_review.py`

**Key Validations**:
- ✓ Pattern extraction works
- ✓ Feedback generation functions
- ✓ Research synthesis accurate
- ✓ Integrates all agent outputs

**Test Scenarios**:
1. **Pattern Detection**: Finds research themes
2. **Feedback Quality**: Actionable insights
3. **Synthesis**: Coherent overview
4. **Integration**: Uses all agent data

### Milestone 13: Natural Language Interface (Phase 15)
**Status**: Pending implementation  
**Location**: `tests/integration/phase15_cli_interface.py`

**Key Validations**:
- ✓ CLI commands work
- ✓ Goal parsing functions
- ✓ Interactive mode works
- ✓ Output formatting correct

**Test Scenarios**:
1. **Command Testing**: All commands work
2. **Input Parsing**: Goals understood
3. **Interaction**: Responsive interface
4. **Output**: Clear, formatted results

### Milestone 14: Full Integration (Phase 16)
**Status**: Pending implementation  
**Location**: `tests/integration/phase16_full_integration.py`

**Key Validations**:
- ✓ Complete research cycle works
- ✓ All agents collaborate
- ✓ Output formatting works
- ✓ Performance acceptable

**Test Scenarios**:
1. **End-to-End**: Goal → Results works
2. **Agent Coordination**: Smooth handoffs
3. **Output Quality**: Publication-ready
4. **Performance**: Reasonable time/resources

### Milestone 15: Final Validation (Phase 17)
**Status**: Pending implementation  
**Location**: `tests/integration/phase17_final_validation.py`

**Key Validations**:
- ✓ Complete research cycle works
- ✓ All agents collaborate
- ✓ Results improve over iterations
- ✓ Safety boundaries respected

**Test Scenarios**:
1. **End-to-End Research**: Goal → Hypotheses → Rankings
2. **Multi-Agent Coordination**: All agents work together
3. **Iterative Improvement**: Quality increases over time
4. **Safety Compliance**: Unsafe content filtered

## Running Integration Tests

### Manual Execution
```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific phase tests
pytest tests/integration/phase3_*.py -v

# Run with coverage
pytest tests/integration/ --cov=src --cov-report=term-missing
```

### Automated Execution
Integration tests run automatically in `run-implementation-loop-validated.sh` after unit tests pass.

### Test Output Interpretation
- **✅ Green**: Integration working as expected
- **⚠️ Yellow**: Non-blocking issues found (informational)
- **❌ Red (Regression)**: Previously passing test now fails
- **❌ Red (Implementation Error)**: New test fails on first run - implementation doesn't match spec

## Writing New Integration Tests

### Template Structure
```python
"""Integration tests for Phase X: [Component Name]."""
import asyncio
import pytest
from src.core.[component] import [Component]

class TestPhaseXIntegration:
    """Test [component] integration with existing system."""
    
    @pytest.mark.asyncio
    async def test_key_workflow(self):
        """Test [specific workflow description]."""
        # 1. Setup components
        # 2. Execute workflow
        # 3. Validate integration
        # 4. Check side effects
```

### Best Practices
1. **Use Existing APIs**: Only call public methods
2. **Test Workflows**: Focus on multi-component interactions
3. **Avoid Mocking**: Use real components when possible
4. **Document Intent**: Clear test names and docstrings
5. **Check Side Effects**: Verify all expected changes
6. **Mark Expected Failures**: Use pytest markers for tests that need future components

### Handling Missing Components
When writing integration tests that require components not yet implemented:

```python
@pytest.mark.skip(reason="Requires Evolution Agent from Phase 8")
async def test_hypothesis_evolution_tracking():
    """Test that hypothesis evolution is tracked through memory."""
    # This test will be skipped until Evolution Agent is implemented
    pass

@pytest.mark.xfail(reason="Ranking Agent not implemented yet")
async def test_tournament_workflow():
    """Test tournament-based hypothesis ranking."""
    # This test is expected to fail until Ranking Agent exists
    # But we can still write and run it to see progress
    pass
```

This ensures:
- Tests waiting for future components don't block the implementation loop
- Clear documentation of dependencies
- Easy to enable tests once components are ready

## Maintenance

### When to Add Tests
- After completing each implementation phase
- When components need to interact
- Before major refactoring
- When bugs reveal integration issues

### When to Update Tests
- When interfaces change
- When workflows evolve
- When new components affect existing ones
- When specifications change

### Test Organization
```
tests/
├── unit/                         # Component-level tests
├── integration/                  # Phase-based integration tests
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── phase3_task_queue_workflow.py
│   ├── phase4_memory_queue.py
│   └── ...
└── e2e/                         # Future: Full system tests
```

## Success Criteria

Each milestone's tests should demonstrate:
1. **Functional Correctness**: Components work as specified
2. **Integration Success**: Components work together
3. **Workflow Validation**: Real use cases succeed
4. **Error Resilience**: Failures handled gracefully
5. **Performance Adequacy**: Reasonable response times

Integration testing ensures that as we build the AI Co-Scientist, each phase produces working functionality that integrates properly with what came before.