# AI Co-Scientist Specification Task

Read all materials in specs-source/ and any existing work in specs_hybrid/.

Your task: Implement the FIRST UNCHECKED item from SPECS_PLAN_hybrid.md by creating
CLEANROOM specifications (implementation-free behavioral specs).

## Requirements:
- Focus only on WHAT the system does, not HOW
- Define clear interfaces and capabilities
- Specify expected inputs/outputs
- Document behavioral contracts
- Follow the guidelines in specs-source/guidelines.md
- Consider the scientific method and research workflow

## Process:
1. Read SPECS_PLAN_hybrid.md to find the first unchecked [ ] item
2. Study all relevant materials in specs-source/, including:
   - ai-coscientist-blog.md and ai-coscientist-paper.md
   - All figure images (AICoScientist-*.png)
   - guidelines.md for specification patterns
3. Review any existing specs in specs_hybrid/ for context and consistency
4. Create a new specification file in specs_hybrid/ with appropriate naming
   - Use numbered prefixes: 001-system-overview.md, 002-multi-agent-framework.md, etc.
   - Follow document organization from guidelines.md section 6
   - For Phase 7 specs, consider documentation architecture patterns
5. Update SPECS_PLAN_hybrid.md to mark the item as complete [x]
6. Commit your changes with a descriptive message:
   - Use: git add specs_hybrid/[new-spec].md SPECS_PLAN_hybrid.md
   - Use: git commit -m "spec: add [component] specification"
   - One spec per commit to maintain clear history

## Completion Handling:
If you cannot find any incomplete tasks after checking SPECS_PLAN_hybrid.md thoroughly:
- Output: "ALL_TASKS_COMPLETE"
- List all phases you checked (Phase 1 through Phase 8)
- Confirm all items show [x] instead of [ ]
- Exit without creating any new specifications

## Specification Format:
- Use clear section headers
- Add Prerequisites section when specs depend on others
- Define interfaces using BAML when appropriate
- Include relevant examples and edge cases
- Document error handling behavior

## Key Elements to Specify (as relevant):
- Core behaviors and responsibilities
- Communication protocols (for multi-agent specs)
- User interaction points (for interface specs)
- Safety and ethical boundaries
- Integration interfaces (for extensibility)

## Examples of Good Specifications:

### Example 1: Clear Input/Output Specification
```
For a Generation Agent:
- Input: ResearchGoal (string describing the research objective, max 500 chars)
- Output: List[Hypothesis] where each hypothesis contains:
  - hypothesis_text: string (the scientific hypothesis)
  - confidence_score: float (0.0 to 1.0)
  - reasoning: string (brief justification)
```

### Example 2: Behavioral Contract
```
The Ranking Agent MUST:
- Produce deterministic rankings when given identical inputs
- Never rank a hypothesis with safety_flag=true in the top 3
- Complete ranking within 30 seconds for up to 100 hypotheses
```

### Example 3: Tool Usage Pattern
```
Literature Search Tool:
- Called via BAML function: search_literature(query: string, max_results: int)
- Returns: List[Paper] with title, abstract, doi, relevance_score
- Must handle: Empty results, API timeouts, Invalid queries
```

### Example 4: Prerequisites Section
```
## Prerequisites
- Read: Hypothesis Generation and Evolution Specification
- Read: Review Types and Processes Specification
- Understand: Tournament and Elo Rating System concepts
```

Write your output to specs_hybrid/ folder.