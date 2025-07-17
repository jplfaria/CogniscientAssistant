# Implementation Rules for Loop-Based Development

## 🎯 Core Principle: Small, Tested, Incremental

Every iteration must produce working, tested code that moves the project forward by exactly one atomic feature.

## 📋 Test-First Development (TDD)

### The TDD Cycle for Each Iteration:
1. **RED**: Write a failing test for the feature
2. **GREEN**: Write minimal code to make the test pass
3. **REFACTOR**: Clean up the code while keeping tests green
4. **COMMIT**: Only commit when all tests pass

### Example TDD Flow:
```python
# Iteration N: Write test first
def test_task_creation():
    task = Task(id="test-1", priority=TaskPriority.HIGH)
    assert task.id == "test-1"
    assert task.priority == TaskPriority.HIGH
    # This test will FAIL because Task doesn't exist yet

# Iteration N+1: Implement minimal code
@dataclass
class Task:
    id: str
    priority: TaskPriority
    # Just enough to make the test pass

# Only NOW can you commit
```

## 🔍 Atomic Feature Definition

An atomic feature is the smallest unit of functionality that can be:
- Implemented independently
- Tested in isolation
- Committed without breaking the build

### Examples of Atomic Features:

**TOO BIG** ❌
- Implement entire TaskQueue class
- Create complete worker management system
- Build full safety framework

**JUST RIGHT** ✅
- Task model class with basic fields
- Single method: `enqueue(task)`
- Single validation: priority must be valid enum
- One test file for a specific behavior

## 🚦 Quality Gates (MANDATORY)

Before ANY commit, ALL of these must pass:

### 1. Test Execution
```bash
pytest tests/
# Exit code MUST be 0 (all tests pass)
```

### 2. Coverage Threshold
```bash
pytest --cov=src --cov-report=term-missing
# Coverage MUST be ≥80%
```

### 3. Type Checking
```bash
mypy src/
# No type errors allowed
```

### 4. Linting
```bash
ruff check src/ tests/
# No linting errors allowed
```

**If ANY quality gate fails, DO NOT COMMIT. Fix the issues first.**

## 📊 Implementation Order Strategy

### Phase 1: Data Models First
- Define models without behavior
- Test model creation and validation
- Ensure serialization works

### Phase 2: Core Operations
- One method at a time
- Test each method thoroughly
- Handle edge cases

### Phase 3: Integration Points
- Connect components carefully
- Integration tests for interactions
- Verify contracts between components

### Phase 4: Error Handling
- Add error cases systematically
- Test failure scenarios
- Ensure graceful degradation

### Phase 5: Performance & Polish
- Optimize hot paths
- Add monitoring/metrics
- Refactor for clarity

## ⚡ Iteration Size Guidelines

### Time per iteration: 5-15 minutes
If an iteration takes longer, it's too big. Break it down further.

### Lines of code per iteration:
- Model/Data class: 10-30 lines
- Single method: 10-50 lines
- Test file: 20-100 lines
- Configuration: 5-20 lines

### Commit message format:
```
feat: add [specific feature] to [component]
test: add tests for [specific behavior]
fix: correct [specific issue] in [component]
refactor: simplify [specific code] in [component]
```

## 🚫 Common Mistakes to Avoid

### 1. Implementing Without Tests
**NEVER** write implementation code without a failing test first.

### 2. Big Bang Implementation
Don't implement multiple features in one iteration.

### 3. Skipping Quality Gates
Don't commit with failing tests "to fix later".

### 4. Over-Engineering
Implement ONLY what the current test requires.

### 5. Test After Implementation
Tests written after code often miss edge cases.

## 📈 Progress Tracking

After each iteration, update IMPLEMENTATION_PLAN.md:
```markdown
- [x] Create Task model class
- [x] Add Task model tests  
- [ ] Implement enqueue method
- [ ] Add enqueue tests
```

## 🔄 Refactoring Rules

### When to Refactor:
- After tests are green
- When you spot duplication
- When complexity grows
- Before adding new features

### When NOT to Refactor:
- When tests are failing
- In the middle of implementing a feature
- Without test coverage
- Just because you can

## 💡 Best Practices

1. **Keep It Simple**: The simplest solution that passes tests is best
2. **YAGNI**: You Aren't Gonna Need It - don't add unused features
3. **DRY**: Don't Repeat Yourself - but only after you see repetition
4. **Single Responsibility**: Each class/method does ONE thing well
5. **Explicit > Implicit**: Clear code beats clever code

## 🎮 The Implementation Game

Think of each iteration as a level in a game:
- **Objective**: Make the test pass
- **Constraint**: Minimal code
- **Score**: Coverage percentage
- **Boss Fight**: Integration tests
- **Victory**: All tests green, coverage ≥80%

Remember: Small steps lead to big victories. One test, one feature, one commit at a time.