# AI Co-Scientist Specification Guidelines

## Key Lessons from Previous Specification Exercises

### 1. **Start Complex, Then Simplify**
- First version can be comprehensive/complex
- Look for actual simplicity in source materials
- Don't add complexity that isn't there
- Follow the simplicity principles from references/12fa-content and references/12fa-template

### 2. **Multi-Agent Research Pattern**
*Note: This refers to using AI assistants to research and create specs, not the AI Co-Scientist's architecture*
- Use parallel agents for different aspects:
  - Architecture agent
  - Capabilities agent  
  - Interface agent
  - Examples/usage agent
- Synthesize findings AFTER all complete
- Wait for ALL agents before proceeding
- Example: Use Claude's Task tool to spawn parallel research agents
- Each agent should have a clear, focused prompt
- Gather all results before synthesizing into specs

### 3. **CLEANROOM Principles**
- NO implementation details
- Focus on WHAT, not HOW
- Define interfaces and contracts
- Specify inputs/outputs/behaviors
- Keep implementation choices open
- See CLAUDE.md for detailed CLEANROOM guidance

### 4. **Specification Structure**
Each spec should include:
- Prerequisites section (when the spec depends on understanding other specs)
- Input/Output specifications
- Behavioral contracts
- Error handling behavior
- Quality requirements
- Natural language examples
- Session management patterns from references/ai-that-works

**Prerequisites Section**:
When a specification depends on concepts from other specs, add a Prerequisites section near the top:
```markdown
## Prerequisites
- Read: [Required spec name] (for understanding X concept)
- Understand: [Key concept] from [Source spec]
```
This helps readers know what context they need before diving into the spec.

### 5. **Technology Decisions**
For AI Co-Scientist:
- Python 3.11+ with types
- BAML for ALL AI interactions
- Multiple LLM support via Argo Gateway:
  - o3, Gemini 2.5, Claude 4 Opus, and others
  - Access via argo-openai-proxy on localhost:8050
  - Use BAML openai-generic provider
- Simple file-based storage
- Event-driven architecture
- Follow 12-factor agent principles
- Modern development environment:
  - Use `uv` for fast package management and virtual environments
  - `pytest` for testing with ≥80% coverage requirement
  - `mypy` for type checking
  - `ruff` for linting
  - Integration testing with test_expectations.json

### 6. **Document Organization**
Create separate specs for:
1. Core agent behaviors (Generation, Reflection, Ranking, Evolution, Proximity, Meta-review)
2. Implementation architecture (multi-agent coordination)
3. Component specifications (tools, interfaces)
4. Advanced features (scientist interaction, feedback loops)
5. Data flow and formats (hypothesis structure, review formats, tournament results)
6. Workflow specifications (end-to-end research process, iteration cycles)

**File Naming Convention**:
- Use numbered prefixes for ordering: `001-system-overview.md`, `002-multi-agent-framework.md`
- Numbers help maintain logical reading order
- Use descriptive names after the number

### 7. **Key Questions to Answer**
- What agents exist and what do they do?
- How do agents communicate?
- What's the data flow?
- How does iteration/refinement work?
- What's the scientist interaction model?
- How is novelty measured?
- How do hypotheses evolve?
- What constitutes a research proposal?
- How do we validate the system works?
- What are the success criteria from the paper?

### 8. **Avoid Common Pitfalls**
- Don't invent features not in source
- Don't overcomplicate simple things
- Don't mix implementation with specification
- Don't forget the human-in-the-loop aspects
- Don't create unnecessary abstractions

### 9. **Argo Gateway Configuration**
Reference: specs-source/references/Argo Gateway API Documentation.md
- Use argo-openai-proxy for LLM access
- Configure BAML clients with:
  ```
  provider: "openai-generic"
  base_url: "http://localhost:8050/v1"
  ```
- Model names (e.g., "gpt4o", "claudeopus4", "gemini25pro")
- See references/README_argo-openai-proxy.md for setup

### 10. **Follow Established Patterns**
- Study references/12fa-content for agent principles
- Use references/12fa-template for implementation patterns
- Apply storage patterns from references/ai-that-works
- Keep implementations minimal and focused

### 11. **AI Co-Scientist Specific Patterns**
- See CLAUDE.md "Understanding the System" section for detailed agent descriptions
- Agents operate asynchronously with task queues
- Tournament-based evolution using Elo ratings
- Multiple review types (initial, full, deep verification, observation, simulation, tournament)
- Research proposals follow NIH Specific Aims format
- Safety reviews at multiple levels

### 12. **Agent Communication Patterns**
- Supervisor agent orchestrates via task queue
- Agents share state through Context Memory
- Meta-review agent provides feedback to all agents
- Tournament results influence agent behaviors
- No direct agent-to-agent communication (all through supervisor)

### 13. **Scientific Method Integration**
- Generate → Debate → Evolve approach
- Self-play for hypothesis refinement
- Grounding through literature search
- Experimental validation considerations
- Novelty assessment mechanisms

### 14. **Key Behavioral Specifications**
When specifying agent behaviors:
- Define input: research goals in natural language
- Define output: ranked hypotheses and research proposals
- Specify iteration and refinement cycles
- Document feedback mechanisms
- Include safety checkpoints

### 15. **BAML Interface Patterns**
For each agent, specify:
- Input classes (ResearchGoal, Hypothesis, Review, etc.)
- Output classes (GeneratedHypothesis, ReviewResult, RankingResult, etc.)
- Tool call interfaces
- Error and retry patterns

### 16. **Development Environment Setup**
When implementing the AI Co-Scientist:
1. **Project Setup Phase** should include:
   - Install `uv` for package management: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Create development setup script in `scripts/setup-dev.sh`
   - Use `uv` for virtual environment: `uv venv`
   - Install dependencies with `uv`: `uv pip install -e ".[dev]"`
   - Configure pyproject.toml with all dependencies
   
2. **Testing Infrastructure**:
   - Unit tests in `tests/unit/`
   - Integration tests in `tests/integration/`
   - Use `test_expectations.json` to define must_pass vs may_fail tests
   - Run tests with pytest: `pytest --cov=src --cov-fail-under=80`
   
3. **Implementation Loop**:
   - Use `run-implementation-loop-validated.sh` for automated development
   - Loop enforces quality gates (tests, coverage, linting)
   - Integration tests run after each phase
   - Regression detection prevents breaking existing functionality

### 17. **Validation Framework**
The AI Co-Scientist paper demonstrates three successful validations:
1. **Drug Repurposing for AML**: KIRA6 showed IC50 of 13 nM in KG-1 cells
2. **Liver Fibrosis Targets**: 4 epigenetic targets reduced fibroblast activity
3. **AMR Mechanism Discovery**: Independently discovered cf-PICI mechanism in 2 days

While these are complex lab validations, our implementation should include attainable tests:

**Functional Validation** (Can the system work?):
- Generate hypotheses for a simple research goal
- Agents complete their assigned tasks
- Tournament produces Elo rankings
- System outputs ranked hypotheses

**Behavioral Validation** (Does it work correctly?):
- Hypothesis quality improves over iterations (rising Elo scores)
- Different review types produce distinct feedback
- Evolution agent creates variations of top hypotheses
- Meta-review synthesizes patterns across reviews

**Simplified Test Cases**:
1. **Literature-based drug repurposing**: Can it suggest metformin for cancer (well-documented)?
2. **Known mechanism discovery**: Can it explain why aspirin reduces heart disease risk?
3. **Simple hypothesis ranking**: Do better hypotheses get higher Elo scores?

**Success Criteria**:
- System completes full workflow without errors
- Hypotheses are grounded in literature (citations present)
- Rankings are justifiable (good hypotheses rank higher)
- Iterative improvement is measurable