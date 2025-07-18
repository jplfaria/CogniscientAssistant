# Claude AI Co-Scientist Implementation Guidelines

**PLEASE FOLLOW THESE RULES EXACTLY - IMPLEMENTATION REQUIRES DISCIPLINE**

**Core Philosophy: IMPLEMENT FROM SPECS. Build behavior exactly as specified.**

**Secondary Philosophy: ALWAYS DELETE MORE THAN YOU ADD. Complexity compounds into disasters.**

## 🚨 THE COMPLETE SPEC READ RULE - THIS IS NOT OPTIONAL

### READ ALL SPECS BEFORE IMPLEMENTING ANYTHING
Read EVERY specification in specs/. Every AI that skims thinks they understand the system, then they BUILD COMPONENTS THAT DON'T INTEGRATE or MISS CRITICAL BEHAVIORS.

**ONCE YOU'VE READ ALL SPECS, YOU UNDERSTAND THE COMPLETE SYSTEM.** Trust your complete read. The specs define all behaviors and interactions.

## 🚨 THE COMPLETE READ RULE - THIS IS NOT OPTIONAL

### READ DEEPLY BEFORE CHANGING
Once implementation begins and files exist:
- **New file**: Read the ENTIRE file first
- **Small file (<500 lines)**: Read it ALL
- **Large file (500+ lines)**: Read at least 500 lines of context
- **UNDERSTAND before you MODIFY**

**Why?** Every AI that does partial reads DUPLICATES FUNCTIONALITY that already exists deeper in the file. You're better than that.

## 📋 WORKING MEMORY TODO LIST (Yes, even in loops!)

**Maintain this between iterations (especially without --letitrip):**

```markdown
## Current TODO List for AI Co-Scientist
1. [ ] Current task from IMPLEMENTATION_PLAN.md
2. [ ] Files I need to read fully before modifying
3. [ ] Tests that need to be written
4. [ ] Integration points to verify
5. [ ] Refactoring opportunities spotted
6. [ ] Duplicate code to remove
7. [ ] Complex abstractions to simplify
8. [ ] Safety checks to add
9. [ ] Error handling gaps
10. [ ] Performance bottlenecks noted
... (keep adding as you discover issues)
```

## 🗑️ THE DELETION REQUIREMENT

**Starting from iteration 10+, every file you touch should get SMALLER:**
- Remove duplicate implementations
- Consolidate similar functions
- Delete commented-out code
- Eliminate over-engineered abstractions
- Simplify complex logic

**Can't find anything to delete?** You're not looking hard enough.

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
    # Continue immediately to implementation - no exit
```

### Step 1: READ RELEVANT SPECS FOR CURRENT TASK
- Don't re-read ALL specs every iteration
- Read specs related to current component
- Trust the implementation plan order

### Step 2: IMPLEMENT ONE ATOMIC FEATURE PER ITERATION

**IMPORTANT: Break components into smallest testable units:**
- Don't implement entire TaskQueue in one iteration
- Example breakdown for TaskQueue:
  - Iteration 1: Task model class only
  - Iteration 2: Tests for Task model
  - Iteration 3: Basic enqueue method
  - Iteration 4: Tests for enqueue
  - Iteration 5: Basic dequeue method
  - Iteration 6: Tests for dequeue
  - etc.

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

### Step 5: QUALITY CHECK AND COMMIT
```bash
# Before committing, ALWAYS:
# 1. Run tests - MUST pass
pytest
# 2. Check coverage - MUST be ≥80%
pytest --cov=src --cov-report=term-missing

# Only if both pass:
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

### TEST-FIRST DEVELOPMENT
- Write failing tests BEFORE implementation
- Implement minimal code to make tests pass
- Refactor only after tests are green
- Each iteration MUST have passing tests before commit

### REAL IMPLEMENTATION ONLY
- Create actual Python files
- Write real code, not pseudocode
- Include docstrings and types
- Handle errors as specified

### INCREMENTAL BUT COMPLETE
- Each commit should work
- Don't break existing code
- ALL tests must pass before commit
- Coverage must meet 80% threshold
- Component must be complete with tests

### COMPLEXITY MANAGEMENT (After iteration 10)
- Count lines added vs deleted
- Aim for negative line count changes
- Question every abstraction
- Merge similar functionality
- Choose simple over clever

## 📖 READING RULES BY ITERATION

### Iterations 1-5: Building Foundation
- Read relevant specs completely
- No existing code to read yet
- Focus on correct implementation

### Iterations 6-15: Integration Phase
- Read EVERY file you're about to modify
- Read related files for context
- Start identifying duplication

### Iterations 16+: Simplification Phase
- Read with deletion in mind
- Every file should get smaller
- Consolidate and refactor
- Remove complexity debt

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

## 🏗️ REQUIRED PATTERNS FROM AI-THAT-WORKS

### BAML Implementation Pattern
- All AI interactions through BAML (no direct API calls)
- See: specs-source/references/ai-that-works/2025-07-01-ai-content-pipeline-2/backend/baml_src/
- Client configuration for Argo Gateway with proper error handling
- Structured agent functions with strong typing and validation
- BAML test files for each agent function

### 12-Factor Agent Architecture  
- Thread-based conversation state management
- Event-driven agent communication pattern
- See: specs-source/references/ai-that-works/2025-04-22-twelve-factor-agents/
- Persistent state management between agent calls
- Proper separation of configuration from code
- Disposable agents with shared nothing architecture

### Storage Patterns
- File-based context memory in .aicoscientist/
- Thread events stored as JSON with timestamps
- See: ai-that-works/2025-07-15-decaying-resolution-memory/ for memory patterns
- Versioned storage for hypothesis evolution tracking
- Atomic file operations to prevent corruption

### Agent Communication Patterns
- Async message passing via task queue
- No direct agent-to-agent communication
- All coordination through Supervisor agent
- Event sourcing for audit trails
- See: ai-that-works async agent examples

### Testing Patterns
- BAML test blocks for all AI functions
- Mock responses for deterministic testing
- Integration tests with real LLM calls
- See: ai-that-works test examples in baml_src directories

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

## 🔒 SECURITY REQUIREMENTS - ARGO GATEWAY

### NEVER COMMIT SENSITIVE INFORMATION
- **Username**: Your Argo username (e.g., jplfaria) must NEVER appear in code
- **API Documentation**: The argo-api-documentation.md file is already in .gitignore
- **API Keys**: Even though Argo doesn't require keys, never hardcode credentials
- **URLs**: Internal Argonne URLs should not be in public code

### SECURE CONFIGURATION PATTERN
```python
# GOOD: Use environment variables
user = os.getenv("ARGO_USER")  # Set in local .env file

# BAD: Never do this
user = "jplfaria"  # NEVER hardcode usernames
```

### ARGO PROXY SETUP
1. **Install**: `pip install argo-proxy`
2. **Configure**: Run `argo-proxy` for interactive setup
3. **Start**: Use `./scripts/start-argo-proxy.sh`
4. **Test**: Run `./scripts/test-argo-models.py`

### ENVIRONMENT FILES
- `.env.example` - Template with dummy values (commit this)
- `.env` - Your actual configuration (NEVER commit this)
- Ensure `.env` is in `.gitignore`

### VPN REQUIREMENTS
- Must be connected to Argonne VPN for Argo access
- Proxy runs locally on your machine (localhost:8050)
- All LLM calls go through the local proxy

## 🧪 INTEGRATION TEST FAILURES

### REGRESSION FAILURES
**When you see "INTEGRATION_REGRESSION=true" in .implementation_flags:**
1. **STOP** - Do not implement new features
2. **INVESTIGATE** - Review recent changes that could affect integration
3. **FIX** - Repair the regression before proceeding
4. **VERIFY** - Ensure integration tests for COMPLETED phases pass
5. **CLEAR FLAG** - Remove .implementation_flags after fixing

### IMPLEMENTATION ERRORS (NEW!)
**When you see "IMPLEMENTATION_ERROR=true" in .implementation_flags:**
1. **STOP** - The implementation doesn't match specifications
2. **READ** - Review the failing integration test to understand expected behavior
3. **ANALYZE** - Compare your implementation against the spec
4. **FIX** - Correct the implementation to match specifications
5. **VERIFY** - Ensure the integration test now passes
6. **CLEAR FLAG** - Remove .implementation_flags after fixing

**Check for errors at start of each iteration:**
```bash
if [ -f ".implementation_flags" ]; then
    if grep -q "INTEGRATION_REGRESSION=true" .implementation_flags; then
        echo "❌ CRITICAL: Integration test regression detected!"
        # Fix the regression first
    elif grep -q "IMPLEMENTATION_ERROR=true" .implementation_flags; then
        echo "❌ CRITICAL: Implementation doesn't match specifications!"
        # Fix the implementation to match specs
    fi
    # After fixing either issue: rm .implementation_flags
fi
```

**Integration Test Categories:**
- **✅ Pass**: Implementation works correctly
- **⚠️ Expected Failure**: Tests in `may_fail` list or marked with @pytest.mark.skip
- **❌ Regression**: Previously passing test now fails
- **❌ Critical Failure**: Tests in `must_pass` list failed - blocks progress
- **❌ Unexpected Failure**: Tests not in `may_fail` list failed - blocks progress
- **ℹ️ Informational**: Non-critical failures to investigate later

**Test Expectations System:**
The file `tests/integration/test_expectations.json` defines which tests MUST pass vs MAY fail for each phase:
```json
{
  "phase_4": {
    "must_pass": ["test_memory_storage_and_retrieval"],  // Critical tests
    "may_fail": ["test_agent_memory_integration"]       // Can fail if agents not ready
  }
}
```

When integration tests fail:
1. **must_pass** failures → Implementation error, must fix
2. **may_fail** failures → Expected, non-blocking
3. Unlisted failures → Unexpected error, must fix or update expectations

## 📊 VERIFICATION AGAINST SPECS

**After implementing each component:**
- [ ] Re-read the relevant spec
- [ ] Verify ALL behaviors are implemented
- [ ] Check input/output formats match
- [ ] Test error conditions
- [ ] Validate safety boundaries
- [ ] Confirm integration points
- [ ] Update IMPLEMENTATION_PLAN.md
- [ ] Run integration tests if available

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