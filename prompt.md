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

5. Implement the selected task:
   - For setup tasks: Create directories, install dependencies, configure tools
   - For components: Follow exact behavioral specifications from specs/
   - For agents: Use BAML for all LLM interactions
   - Always include safety checks and error handling
   - Write tests alongside implementation

6. Run quality checks (only after code exists):
   ```bash
   # Only run these if the tools are installed and code exists
   pytest tests/ 2>/dev/null || echo "Tests pending"
   mypy src/ 2>/dev/null || echo "Type checking pending"
   ruff check src/ 2>/dev/null || echo "Linting pending"
   ```

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

- ONE TASK PER ITERATION - Complete it fully before moving on
- SPECS ARE CANONICAL - If spec says X, implement X exactly
- CREATE REAL FILES - Don't just update the plan
- COMMIT WORKING CODE - Each commit should leave system functional
- INCREMENTAL PROGRESS - Small, complete changes are better

When in doubt, re-read the relevant specification. The specs define ALL required behaviors.