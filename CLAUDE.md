# Claude AI Co-Scientist Implementation Guidelines

**PLEASE FOLLOW THESE RULES EXACTLY - IMPLEMENTATION REQUIRES DISCIPLINE**

**Core Philosophy: IMPLEMENT FROM SPECS. Build behavior exactly as specified.**

## 🚨 THE COMPLETE SPEC READ RULE - THIS IS NOT OPTIONAL

### READ ALL SPECS BEFORE IMPLEMENTING ANYTHING
Read EVERY specification in specs/. Every AI that skims thinks they understand the system, then they BUILD COMPONENTS THAT DON'T INTEGRATE or MISS CRITICAL BEHAVIORS.

**ONCE YOU'VE READ ALL SPECS, YOU UNDERSTAND THE COMPLETE SYSTEM.** Trust your complete read. The specs define all behaviors and interactions.

## 📋 YOUR IMPLEMENTATION TODO LIST

**MAINTAIN THIS STRUCTURE FOR EACH COMPONENT:**

```markdown
## Current TODO List for AI Co-Scientist Implementation
1. [ ] Read ALL specs in specs/ folder (28 files)
2. [ ] Review IMPLEMENTATION_PLAN.md for current priorities
3. [ ] Set up project structure (src/, tests/, config/)
4. [ ] Implement core infrastructure first (Task Queue, Context Memory)
5. [ ] Build LLM Abstraction layer with BAML
6. [ ] Implement Supervisor Agent (orchestrates everything)
7. [ ] Add each specialized agent one by one
8. [ ] Integrate safety framework at each layer
9. [ ] Set up monitoring and logging
10. [ ] Create comprehensive test suite
11. [ ] Build CLI interface
12. [ ] Test multi-agent interactions
13. [ ] Verify safety boundaries work
14. [ ] Check tournament dynamics
15. [ ] Validate expert-in-the-loop flows
16. [ ] Run integration tests
17. [ ] Performance testing with concurrent agents
18. [ ] Document deployment requirements
19. [ ] Create example research scenarios
20. [ ] Update IMPLEMENTATION_PLAN.md progress
... (maintain 20+ items or you'll lose context)
```

## Project Context

AI Co-Scientist is a multi-agent system for scientific hypothesis generation:
- Python 3.11+ with full type annotations
- BAML for all AI agent interactions
- Asynchronous task execution with queues
- File-based context memory in .aicoscientist/
- Tournament-based hypothesis ranking (Elo ratings)
- Multi-layer safety framework
- Natural language interface

## 🔄 THE IMPLEMENTATION WORKFLOW THAT WORKS

### Step 1: UNDERSTAND THE COMPLETE SYSTEM FROM SPECS
- Read ALL 28 specifications thoroughly
- Map out agent interactions and data flows
- Identify shared infrastructure components
- Note safety checkpoints and boundaries

### Step 2: BUILD CORE INFRASTRUCTURE FIRST
```bash
# Set up project structure
mkdir -p src/{agents,core,interfaces,safety,tools}
mkdir -p tests/{unit,integration,e2e}
mkdir -p config
mkdir -p .aicoscientist/{context,threads,artifacts}

# Core components to build first:
# - Task Queue (src/core/task_queue.py)
# - Context Memory (src/core/context_memory.py)
# - LLM Abstraction (src/core/llm_abstraction.py)
# - Safety Framework (src/safety/)
```

### Step 3: IMPLEMENT AGENTS INCREMENTALLY
```python
# Start with Supervisor Agent - it orchestrates everything
class SupervisorAgent:
    """Orchestrates task execution across specialized agents."""
    
    def __init__(self, task_queue: TaskQueue, context: ContextMemory):
        self.task_queue = task_queue
        self.context = context
        self.agents = {}  # Will register other agents here
    
    async def process_research_goal(self, goal: str) -> ResearchSession:
        """Main entry point for research requests."""
        # Safety check first (as per specs)
        if not await self.safety_check_goal(goal):
            raise UnsafeResearchGoalError(goal)
        
        # Create research session
        session = await self.create_session(goal)
        
        # Queue initial generation tasks
        await self.queue_generation_tasks(session)
        
        # Start processing loop
        return await self.run_session(session)
```

### Step 4: USE BAML FOR ALL AI INTERACTIONS
```python
# In baml_src/aicoscientist.baml
class Hypothesis {
  summary string @description("Brief hypothesis statement")
  description string @description("Full scientific hypothesis")
  experimental_protocol string @description("How to test this hypothesis")
  confidence float @description("0.0 to 1.0")
  safety_score float @description("0.0 to 1.0")
}

function generate_hypotheses(goal: string, context: string) -> Hypothesis[] {
  client ArgoAI
  prompt #"
    Given this research goal: {{ goal }}
    And this context: {{ context }}
    
    Generate novel scientific hypotheses following these criteria:
    1. Scientifically plausible
    2. Testable with current methods
    3. Novel contributions to the field
    4. Safe and ethical
    
    Return 3-5 hypotheses.
  "#
}
```

### Step 5: IMPLEMENT SAFETY AT EVERY LAYER
```python
# Safety checks as specified in specs
class SafetyFramework:
    async def check_research_goal(self, goal: str) -> SafetyResult:
        """Initial safety review of research goals."""
        # Check against prohibited topics
        # Evaluate dual-use potential
        # Assess ethical implications
        
    async def check_hypothesis(self, hypothesis: Hypothesis) -> SafetyResult:
        """Safety review of generated hypotheses."""
        # Similar checks at hypothesis level
        
    async def monitor_research_direction(self, session: ResearchSession) -> SafetyResult:
        """Continuous monitoring by Meta-review agent."""
        # Check if research is drifting into unsafe territory
```

### Step 6: TEST EVERYTHING
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests after each component
pytest tests/unit/test_task_queue.py
pytest tests/unit/test_context_memory.py
pytest tests/integration/test_agent_interactions.py

# Check coverage
pytest --cov=src --cov-report=term-missing
```

## 🛠️ TECHNICAL REQUIREMENTS FROM SPECS

### Core Technologies:
- **Python 3.11+** - Async/await for agent concurrency
- **BAML** - All LLM interactions (no direct API calls)
- **asyncio** - Asynchronous task execution
- **pydantic** - Data validation and serialization
- **pytest** - Comprehensive testing

### Infrastructure Components:
1. **Task Queue** - Distributes work to agents
2. **Context Memory** - Shared state and history
3. **LLM Abstraction** - BAML-based AI interface
4. **Safety Framework** - Multi-layer protection
5. **Worker Pool** - Concurrent agent execution

### Agent Implementation Order:
1. Supervisor Agent (orchestrator)
2. Generation Agent (hypothesis creation)
3. Reflection Agent (review system)
4. Ranking Agent (tournament system)
5. Evolution Agent (hypothesis enhancement)
6. Proximity Agent (similarity clustering)
7. Meta-review Agent (feedback synthesis)

## 🚫 CRITICAL RULES - FROM SPECS TO CODE

### FOLLOW THE SPECS EXACTLY
- Every behavior in specs MUST be implemented
- No features not in specs
- Interfaces must match spec definitions
- Safety boundaries are non-negotiable

### ASYNCHRONOUS EVERYTHING
- Agents run as async worker processes
- Non-blocking I/O for all operations
- Proper error propagation
- Graceful degradation

### SAFETY FIRST
- Check research goals before processing
- Filter unsafe hypotheses
- Monitor research directions
- Log everything for auditing

## 📊 VERIFICATION AGAINST SPECS

**After implementing each component:**
- [ ] Re-read the relevant spec
- [ ] Verify ALL behaviors are implemented
- [ ] Check input/output formats match
- [ ] Test error conditions
- [ ] Validate safety boundaries
- [ ] Confirm integration points
- [ ] Update IMPLEMENTATION_PLAN.md

## ✅ IMPLEMENTATION CHECKLIST

**Track your progress:**
- [ ] Project structure created
- [ ] Core infrastructure implemented
- [ ] BAML schemas defined
- [ ] Supervisor Agent working
- [ ] Generation Agent creating hypotheses
- [ ] Reflection Agent reviewing
- [ ] Ranking Agent running tournaments
- [ ] Evolution Agent enhancing
- [ ] Proximity Agent clustering
- [ ] Meta-review Agent synthesizing
- [ ] Safety framework integrated
- [ ] CLI interface functional
- [ ] Integration tests passing
- [ ] Documentation complete

## 🚨 REMEMBER: THE SPECS ARE YOUR TRUTH

**The specs define WHAT to build. This guide helps with HOW. Never deviate from specified behaviors.**

When implementing:
1. Read the spec for the component
2. Implement exactly what's specified
3. Test against spec requirements
4. Move to next component

**CRITICAL: We're building from specs. If the spec says it does X, make it do X. No more, no less.**