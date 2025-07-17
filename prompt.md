# AI Co-Scientist Implementation Task

Read all specifications in specs/ and implement the AI Co-Scientist system according to the IMPLEMENTATION_PLAN.md.

## Your Task:

1. Check IMPLEMENTATION_PLAN.md:
   - If it contains "Nothing here yet", CREATE a comprehensive implementation plan with:
     a. Project setup and structure tasks
     b. Core infrastructure components (from specs)
     c. Agent implementation tasks (in dependency order)
     d. Integration and testing tasks
     e. Use checkbox format: `- [ ] Task description`
   - If plan exists, proceed to implementation

2. Study specs/* to understand the complete system behavior (28 specifications)

3. Study any existing src/* to understand current implementation state

4. Select the FIRST unchecked [ ] item from IMPLEMENTATION_PLAN.md

5. Implement the selected task using TEST-FIRST development:
   - FIRST: Write failing tests for the feature
   - THEN: Implement minimal code to make tests pass
   - For setup tasks: Create directories, install dependencies, configure tools
   - For components: Follow exact behavioral specifications from specs/
   - For agents: Use BAML for all LLM interactions
   - Always include safety checks and error handling
   - Break large tasks into atomic features (one testable unit per iteration)

6. Run MANDATORY quality checks before ANY commit:
   ```bash
   # Tests MUST pass (exit code 0)
   pytest tests/
   
   # Coverage MUST be ≥80%
   pytest --cov=src --cov-report=term-missing --cov-fail-under=80
   
   # Type checking (if mypy installed)
   mypy src/ 2>/dev/null || echo "Type checking pending"
   
   # Linting (if ruff installed)
   ruff check src/ 2>/dev/null || echo "Linting pending"
   ```
   
   DO NOT COMMIT if tests fail or coverage is below 80%!

7. Update IMPLEMENTATION_PLAN.md:
   - Mark completed items with [x]
   - Add any discovered subtasks as new [ ] items
   - Keep plan organized by component

8. Commit your changes with descriptive message:
   ```bash
   git add -A
   git commit -m "feat: [what you did] - [component/file affected]"
   ```

## Exit Conditions:

If ALL of the following are true, output "IMPLEMENTATION_COMPLETE":
- All items in IMPLEMENTATION_PLAN.md are marked [x]
- Core infrastructure is implemented
- All agents are implemented
- Tests are passing
- No pending tasks remain

## Implementation Order (follow this sequence):

1. **Project Setup**
   - Create directory structure
   - Set up pyproject.toml with dependencies
   - Configure development tools
   - Create __init__.py files

2. **Core Infrastructure** (specs 006, 015, 026-028)
   - Task Queue with worker pool
   - Context Memory with persistence
   - State management systems

3. **Safety & LLM Layer** (specs 020, 023)
   - Safety framework
   - BAML schemas for all agents
   - LLM abstraction layer

4. **Agents in Order** (specs 005, 007-012)
   - Supervisor Agent first (orchestrates others)
   - Generation Agent
   - Reflection Agent  
   - Ranking Agent
   - Evolution Agent
   - Proximity Agent
   - Meta-review Agent

5. **Interfaces & Integration** (specs 014, 016-019)
   - Web search interface
   - External tools
   - Natural language interface
   - Output formatters

## Remember:

- TEST FIRST - Write failing test, then implementation
- ONE ATOMIC FEATURE PER ITERATION - If task is big, break it down
- QUALITY GATES ARE MANDATORY - No commits with failing tests or low coverage
- SPECS ARE CANONICAL - If spec says X, implement X exactly
- CREATE REAL FILES - Don't just update the plan
- COMMIT ONLY PASSING CODE - Each commit must have all tests green
- INCREMENTAL PROGRESS - Small, tested changes are better

Example of atomic features:
- Bad: "Implement TaskQueue class" (too big)
- Good: "Create Task model", "Add enqueue method", "Add dequeue method" (atomic)

When in doubt:
1. Re-read the relevant specification
2. Check IMPLEMENTATION_RULES.md for TDD guidelines
3. Ensure tests pass before moving on