# AI Co-Scientist Implementation Task

Read all specifications in specs/ and implement the AI Co-Scientist system according to the IMPLEMENTATION_PLAN.md.

## Your Task:

1. Study specs/* to understand the complete system behavior (28 specifications)

2. Study any existing src/* to understand current implementation state

3. Review IMPLEMENTATION_PLAN.md and select the highest-priority unimplemented item

4. Implement the selected component following:
   - Exact behavioral specifications from specs/
   - Technical requirements in CLAUDE.md
   - Safety-first approach
   - Test-driven development

5. Ensure quality:
   - All tests pass
   - Type checking passes (mypy)
   - Linting passes (ruff)
   - BAML generation succeeds

6. Update IMPLEMENTATION_PLAN.md:
   - Mark completed items with [x]
   - Add any discovered subtasks
   - Note integration points

7. Commit your changes:
   ```bash
   git add -A
   git commit -m "feat: implement [component] as specified in [spec-number]"
   ```

## Implementation Priorities:

1. Core Infrastructure (Task Queue, Context Memory)
2. LLM Abstraction with BAML
3. Supervisor Agent
4. Specialized Agents (in order)
5. Safety Framework
6. User Interfaces
7. Integration Testing

## Remember:

- SPECS ARE YOUR REQUIREMENTS - implement exactly what's specified
- NO FEATURES NOT IN SPECS - avoid scope creep
- SAFETY CHECKS FIRST - every component needs safety integration
- TEST AS YOU GO - each component needs unit tests
- DOCUMENT INTEGRATION POINTS - other components depend on your interfaces

When in doubt, re-read the relevant specification. The specs are complete and define all behaviors needed.