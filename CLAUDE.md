# Claude AI Co-Scientist Implementation Guidelines

**PLEASE FOLLOW THESE RULES EXACTLY - IMPLEMENTATION REQUIRES DISCIPLINE**

**Core Philosophy: IMPLEMENT FROM SPECS. Build behavior exactly as specified.**

## 🚨 THE COMPLETE SPEC READ RULE - THIS IS NOT OPTIONAL

### READ ALL SPECS BEFORE IMPLEMENTING ANYTHING
Read EVERY specification in specs/. Every AI that skims thinks they understand the system, then they BUILD COMPONENTS THAT DON'T INTEGRATE or MISS CRITICAL BEHAVIORS.

**ONCE YOU'VE READ ALL SPECS, YOU UNDERSTAND THE COMPLETE SYSTEM.** Trust your complete read. The specs define all behaviors and interactions.

## 📋 LOOP-BASED IMPLEMENTATION APPROACH

**You are running in an automated loop. Each iteration:**
1. Check IMPLEMENTATION_PLAN.md status
2. Implement ONE task completely
3. Update the plan
4. Commit your changes
5. Exit for next iteration

**CRITICAL: One task per loop iteration. Complete it fully.**

## Project Context

AI Co-Scientist is a multi-agent system for scientific hypothesis generation:
- Python 3.11+ with full type annotations
- BAML for all AI agent interactions
- Asynchronous task execution with queues
- File-based context memory in .aicoscientist/
- Tournament-based hypothesis ranking (Elo ratings)
- Multi-layer safety framework
- Natural language interface

## 🔄 THE LOOP IMPLEMENTATION WORKFLOW

### Step 0: CHECK IMPLEMENTATION_PLAN.md
```python
# If empty, create comprehensive plan
if implementation_plan == "Nothing here yet":
    create_implementation_plan()  # With ALL tasks needed
    exit("PLAN_CREATED - Run again to start implementing")
```

### Step 1: READ RELEVANT SPECS FOR CURRENT TASK
- Don't re-read ALL specs every iteration
- Read specs related to current component
- Trust the implementation plan order

### Step 2: IMPLEMENT ONE COMPONENT PER ITERATION
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

### Step 3: CREATE ACTUAL FILES AND CODE
```bash
# Example for first iteration - project setup
cat > pyproject.toml << 'EOF'
[project]
name = "ai-coscientist"
version = "0.1.0"
dependencies = [
    "pydantic>=2.0",
    "asyncio",
    "baml",
    "pytest>=7.0",
    "mypy>=1.0",
    "ruff>=0.1.0"
]
EOF

# Example for component iteration
cat > src/core/task_queue.py << 'EOF'
"""Task Queue implementation as specified in 006-task-queue-behavior.md"""
from enum import Enum
from typing import Dict, List, Optional
# ... actual implementation
EOF
```

### Step 4: ALWAYS UPDATE IMPLEMENTATION_PLAN.md
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

```markdown
# After implementing a task:
- [x] Set up project structure and pyproject.toml
- [ ] Install dependencies and configure tools
- [ ] Create TaskQueue class with state management
# ... mark completed, add new discovered tasks
```

### Step 5: COMMIT AND EXIT
```bash
# Every iteration ends with:
git add -A
git commit -m "feat: implement [component] - [what you did]"
# Then exit - the loop will continue
```

## 🚨 LOOP ITERATION RULES

### ONE TASK = ONE ITERATION
- Pick the FIRST unchecked [ ] task
- Implement it COMPLETELY
- Don't start multiple tasks
- Don't skip ahead

### REAL IMPLEMENTATION ONLY
- Create actual Python files
- Write real code, not pseudocode
- Include docstrings and types
- Handle errors as specified

### INCREMENTAL BUT COMPLETE
- Each commit should work
- Don't break existing code
- Tests can be pending if component isn't ready
- But component itself must be complete

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