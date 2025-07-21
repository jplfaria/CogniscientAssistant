# Claude AI Co-Scientist Implementation Guidelines

**Core Philosophy: IMPLEMENT FROM SPECS. Build behavior exactly as specified.**

## 📖 Reading Requirements

### Before Implementation
- Read ALL specs in specs/ directory first
- Understand the complete system before coding
- Trust the specs - they define all behaviors

### During Implementation
- **New file**: Read ENTIRE file before modifying
- **Small file (<500 lines)**: Read completely
- **Large file (500+ lines)**: Read at least 1500 lines
- **ALWAYS** understand existing code before adding new code

## 📁 Test Organization

### Test Directory Structure
- **Unit tests**: `tests/unit/test_*.py` - Test individual components
- **Integration tests**: `tests/integration/test_phase*_*.py` - Test system workflows
- **NO other test subdirectories** - Don't create tests/baml/, tests/agents/, etc.
- **NO tests in root tests/ directory** - All tests must be in unit/ or integration/

### Test Naming Convention
- Unit test: `tests/unit/test_<module_name>.py`
- Integration test: `tests/integration/test_phase<N>_<feature>.py`
- Example: `tests/unit/test_task_queue.py`, `tests/integration/test_phase3_queue_workflow.py`

## 🔄 Implementation Workflow

### 1. Check Status
```bash
# At start of each iteration, check for errors
if [ -f ".implementation_flags" ]; then
    if grep -q "INTEGRATION_REGRESSION=true" .implementation_flags; then
        echo "❌ Fix regression before continuing"
    elif grep -q "IMPLEMENTATION_ERROR=true" .implementation_flags; then
        echo "❌ Fix implementation to match specs"
    fi
    # After fixing: rm .implementation_flags
fi
```

### 2. One Task Per Iteration
- Pick FIRST unchecked [ ] task from IMPLEMENTATION_PLAN.md
- Implement it COMPLETELY with tests
- Don't start multiple tasks
- Each iteration MUST have passing tests before commit

### 3. Test-First Development
- Write failing tests BEFORE implementation
- Implement minimal code to pass tests
- All tests must pass (pytest)
- Coverage must meet 80% threshold
- Integration tests use test_expectations.json

### 4. Commit and Continue
```bash
# Only if all tests pass:
git add -A
git commit -m "feat: implement [component] - [what you did]"
# Then exit - the loop will continue
```

## 🧪 Testing Requirements

### Integration Test Categories
- **✅ Pass**: Implementation correct
- **⚠️ Expected Failure**: Tests in `may_fail` list
- **❌ Critical Failure**: Tests in `must_pass` list failed
- **❌ Unexpected Failure**: Unlisted tests failed
- **❌ Regression**: Previously passing test fails

### Test Expectations
The file `tests/integration/test_expectations.json` defines:
- `must_pass`: Critical tests that block progress
- `may_fail`: Tests allowed to fail (waiting for future components)
- `real_llm_tests`: Optional tests that verify actual AI behavior

## 🤖 Real LLM Testing

### Purpose
Verify that agents exhibit expected AI behaviors with actual models (not mocked).

### Implementation
- Write alongside regular integration tests
- Use naming: `test_phaseN_component_real.py`
- Mark with `@pytest.mark.real_llm`
- Test behaviors, not exact outputs
- Keep token usage minimal (<100 per test)

### Example Structure
```python
@pytest.mark.real_llm
async def test_supervisor_real_orchestration():
    """Test Supervisor exhibits planning behavior with o3."""
    supervisor = SupervisorAgent()
    result = await supervisor.plan_research("Why does ice float?")
    
    # Test behavioral expectations
    assert len(result.subtasks) >= 3  # Proper decomposition
    assert "density" in str(result).lower()  # Key concepts
    # Verify o3 shows reasoning steps
    assert any(marker in result.reasoning.lower() 
              for marker in ["step", "first", "then"])
```

### When to Write
- For agent phases (9+) that use LLMs
- Focus on model-specific behaviors (o3 reasoning, Claude creativity)
- Not needed for infrastructure phases

### Execution
- NOT part of automated loop (too slow/expensive)
- Run manually: `pytest tests/integration/*_real.py -v --real-llm`
- Run before major releases or when debugging AI behavior

## 🛡️ Safety & Security

### Argo Gateway Security
- **NEVER** commit usernames or API keys
- Use environment variables for configuration
- Keep argo-api-documentation.md in .gitignore
- Ensure VPN connection for Argo access

### Safety Framework
- Check research goals before processing
- Filter unsafe hypotheses
- Monitor research directions
- Log everything for auditing

## 🏗️ Technical Stack

### Core Technologies
- **Python 3.11+**: Async/await for concurrency
- **BAML**: ALL LLM interactions (no direct API calls)
- **pytest**: Comprehensive testing with ≥80% coverage
- **File-based storage**: .aicoscientist/ directory

### Implementation Phases (1-17)
1. **Project Setup**: Structure and dependencies
2. **Core Models**: Task, Hypothesis, Review
3. **Task Queue**: First integrable component
4. **Context Memory**: Persistent state management
5. **Safety Framework**: Multi-layer protection
6. **LLM Abstraction**: Interface layer
7. **BAML Infrastructure**: Argo Gateway setup
8. **Supervisor Agent**: Orchestration
9. **Generation Agent**: Hypothesis creation
10. **Reflection Agent**: Review system
11. **Ranking Agent**: Tournament system
12. **Evolution Agent**: Enhancement
13. **Proximity Agent**: Clustering
14. **Meta-Review Agent**: Synthesis
15. **Natural Language Interface**: CLI
16. **Integration and Polish**: Full system
17. **Final Validation**: Complete testing

## 🚨 Critical Rules

1. **Follow specs exactly** - no deviations
2. **Integration tests start at Phase 3** (first integrable component)
3. **Every file should get smaller after iteration 10+**
4. **Use BAML for all AI interactions**
5. **Maintain ≥80% test coverage always**
6. **One atomic feature per iteration**
7. **Update IMPLEMENTATION_PLAN.md after each task**

## 📋 Working Memory

Maintain a TODO list between iterations:
```markdown
## Current TODO List
1. [ ] Current task from IMPLEMENTATION_PLAN.md
2. [ ] Files to read before modifying
3. [ ] Tests to write
4. [ ] Integration points to verify
5. [ ] Refactoring opportunities
6. [ ] Duplicate code to remove
```

Remember: The specs are your truth. Implement exactly what's specified.