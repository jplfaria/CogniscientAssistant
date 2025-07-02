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

### 3. **CLEANROOM Principles**
- NO implementation details
- Focus on WHAT, not HOW
- Define interfaces and contracts
- Specify inputs/outputs/behaviors
- Keep implementation choices open
- See CLAUDE.md for detailed CLEANROOM guidance

### 4. **Specification Structure**
Each spec should include:
- Input/Output specifications
- Behavioral contracts
- Error handling behavior
- Quality requirements
- Natural language examples
- Session management patterns from references/ai-that-works

### 5. **Technology Decisions**
For AI Co-Scientist:
- Python with types
- BAML for ALL AI interactions
- Multiple LLM support via Argo Gateway:
  - o3, Gemini 2.5, Claude 4 Opus, and others
  - Access via argo-openai-proxy on localhost:8050
  - Use BAML openai-generic provider
- Simple file-based storage
- Event-driven architecture
- Follow 12-factor agent principles

### 6. **Document Organization**
Create separate specs for:
1. Core agent behaviors (Generation, Reflection, Ranking, Evolution, Proximity, Meta-review)
2. Implementation architecture (multi-agent coordination)
3. Component specifications (tools, interfaces)
4. Advanced features (scientist interaction, feedback loops)
5. Data flow and formats (hypothesis structure, review formats, tournament results)
6. Workflow specifications (end-to-end research process, iteration cycles)

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

### 16. **Validation Framework**
The AI Co-Scientist paper demonstrates three successful validations:
1. **Drug Repurposing for AML**: KIRA6 showed IC50 of 13 nM in KG-1 cells
2. **Liver Fibrosis Targets**: 4 epigenetic targets reduced fibroblast activity
3. **AMR Mechanism Discovery**: Independently discovered cf-PICI mechanism in 2 days

Our implementation should:
- Include test cases based on these examples
- Define success criteria (e.g., hypothesis quality, ranking accuracy)
- Specify how to measure if the system "works"
- Include both automated tests and manual validation protocols