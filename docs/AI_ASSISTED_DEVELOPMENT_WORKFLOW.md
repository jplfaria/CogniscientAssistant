# AI-Assisted Development Workflow: From Specs to Implementation

**Last Updated: July 2025 - Phase 8 (Argo Gateway Integration)**

This document captures the complete workflow and lessons learned from building the AI Co-Scientist project using AI-assisted development.

## Overview

This project demonstrates a disciplined approach to AI-assisted software development, starting from source materials, through CLEANROOM specification development, to implementation via an iterative, test-driven process.

## Phase 1: Specification Development

### The CLEANROOM Approach

We used a systematic CLEANROOM specification process where AI agents created implementation-free behavioral specifications from research papers and blog posts.

### Source Material Preparation
1. **Gathered comprehensive materials** in `specs-source/`:
   - `ai-coscientist-paper.md` - Technical research paper
   - `ai-coscientist-blog.md` - High-level overview
   - 11 PNG figures showing system architecture
   - Reference implementations from `ai-that-works` patterns

2. **Created spec development framework**:
   - `SPECS_CLAUDE.md` - Guidelines for AI agents writing specs
   - `specs-prompt.md` - Iterative prompt for spec creation
   - `SPECS_PLAN.md` - Started with "Nothing here yet"
   - `run-spec-loop-improved.sh` - Automation script

### The Spec Loop Process

Similar to implementation, we used an iterative loop:

1. **First iteration**: AI reads all sources and creates SPECS_PLAN.md
2. **Subsequent iterations**: AI implements one spec at a time
3. **Each iteration**:
   - Read source materials completely
   - Create one CLEANROOM specification
   - Update SPECS_PLAN.md checkbox
   - Commit individually

### Key Files in Spec Development
- `docs/spec-development/SPECS_CLAUDE.md` - Core rules for AI:
  - Complete read rule (no skimming)
  - WHAT not HOW principle
  - Behavioral specifications only
  - Individual commits per spec

- `docs/spec-development/run-spec-loop-improved.sh`:
  - Handles plan creation on first run
  - Iterates through unchecked items
  - Shows progress and remaining tasks
  - Supports `--letitrip` for continuous mode

### The Empty vs Hybrid Experiment
We tested two approaches:
1. **Empty approach**: Let AI create plan from scratch
2. **Hybrid approach**: Provide structured plan as guidance

The empty approach (which we used) allowed AI to organize specs based on its understanding of the system.

### Results: 28 Comprehensive Specs
- **001-003**: System foundation and principles
- **004-006**: Multi-agent framework and task queue
- **007-012**: Individual agent specifications
- **013-016**: Interfaces and tools
- **017-019**: User interaction
- **020-022**: Safety and validation
- **023-025**: Integration and deployment
- **026-028**: System completeness (added after gap analysis)

### Lessons from Spec Phase
- AI agents can create comprehensive plans when given good source materials
- CLEANROOM principles (WHAT not HOW) keep specs implementation-agnostic
- Complete reading of sources is critical - no skimming
- Individual commits per spec maintain clear history
- Gap analysis revealed missing temporal and resource specs

## Phase 2: Implementation Setup

### Initial Implementation Attempt
1. Created initial workflow files:
   - `CLAUDE.md` - AI implementation guidelines
   - `prompt.md` - Implementation prompt template
   - `run-implementation-loop.sh` - Basic automation script

### Problems Encountered
- AI would create implementation plans but exit immediately
- No enforcement of test-first development
- Quality gates not enforced
- Cascading failures from incomplete implementations

## Phase 3: Workflow Refinement

### Iteration 1: Basic Improvements
Created `run-implementation-loop-improved.sh` with:
- Better progress tracking
- Git status integration
- Implementation plan monitoring
- Continuous mode with `--letitrip`

### Iteration 2: Quality Gates
Created `IMPLEMENTATION_RULES.md` establishing:
- Test-first development (TDD) requirements
- Atomic feature definitions
- Quality gates (tests, coverage, linting)
- Iteration size guidelines

### Iteration 3: Validated Workflow
Created `run-implementation-loop-validated.sh` with:
- Enforced quality gates before commits
- Phase-aware testing
- Coverage requirements (≥80%)
- Automatic rollback on test failures

### Key Improvements Made
1. **Checkpoint System**: Tag-based checkpoints for clean resets
2. **Test-First Enforcement**: Can't commit without passing tests
3. **Atomic Iterations**: One small feature per iteration
4. **Quality Gates**: Automated checks before commits

## Phase 4: Integration Testing Framework

### Challenge
How to test that implemented functionality actually works without adding production code that specs don't expect?

### Solution
Created integration testing framework:
- `INTEGRATION_TESTING_PLAN.md` - Testing strategy
- `tests/integration/` - Test harnesses (not production code)
- Phase-aware test execution
- Regression detection system

### Key Components
1. **Test Harnesses**: Validate functionality without modifying production code
2. **Phase Detection**: Run appropriate tests based on implementation progress (17 phases)
3. **Regression Tracking**: Detect when previously passing tests fail
4. **Implementation Error Detection**: Stop when new tests fail on first run
5. **Test Expectations**: `test_expectations.json` defines must_pass vs may_fail tests
6. **Non-blocking Failures**: Only expected failures are non-blocking

## Phase 5: BAML Integration and Test Organization

### BAML Integration (Phase 7-8)
We integrated BAML (Basically A Modeling Language) for LLM interactions:

1. **BAML Configuration Structure**:
   - `baml_src/` directory for all BAML files
   - `models.baml` - Data structures with aliases for flexibility
   - `clients.baml` - LLM client configurations
   - `environment.baml` - Environment variable mappings
   - `functions.baml` - LLM function definitions

2. **Key BAML Lessons**:
   - Keep environment variables synchronized between `.env.example` and `environment.baml`
   - Use aliases for enum values to support multiple formats
   - BAML handles all LLM interactions - no direct API calls
   - Test BAML schemas separately from implementation

### Test Organization Discovery

During Phase 8, we discovered a critical issue with test file placement:

1. **The Problem**: 
   - LLM module tests ended up in `tests/` root directory
   - Other tests correctly placed in `tests/unit/`
   - Caused misleading coverage reports (showing 21% when actual was 95%)

2. **Root Cause**:
   - No explicit test directory guidelines in IMPLEMENTATION_PLAN.md
   - Phase 6 mixed BAML schemas with LLM abstraction
   - Implementation happened at different times with inconsistent decisions

3. **The Fix**:
   - Added explicit test organization rules to CLAUDE.md
   - All unit tests must go in `tests/unit/`
   - All integration tests must go in `tests/integration/`
   - NO other subdirectories or root-level test files

4. **Coverage Reality**:
   - Moving tests to correct location revealed true coverage
   - Unit test coverage: 74.81% → 83.79%
   - Most LLM modules already had >90% coverage

### Test Coverage Strategy Update

We refined our approach to test coverage:

1. **Separate Coverage Metrics**:
   - Unit tests: 80% threshold (enforced)
   - Integration tests: Informational only (no threshold)
   - Run and report separately

2. **Why This Makes Sense**:
   - Unit tests should comprehensively test components
   - Integration tests verify workflows, not every code path
   - Combined coverage can mask poorly tested units

3. **Implementation in run-loop.sh**:
   ```bash
   # Unit tests with threshold
   pytest tests/unit/ --cov=src --cov-fail-under=80
   
   # Integration tests for information
   pytest tests/integration/ --cov=src --cov-report=term
   ```

## Phase 6: Current State

### Active Workflow Files
- `CLAUDE.md` - Simplified implementation guidelines (71% smaller, more focused)
- `prompt.md` - Implementation task prompt with test expectations awareness
- `run-implementation-loop-validated.sh` - Primary implementation script (handles all 17 phases)
- `IMPLEMENTATION_PLAN.md` - Living document tracking progress (includes integration test tasks)
- `INTEGRATION_TESTING_PLAN.md` - Testing strategy and milestones
- `tests/integration/test_expectations.json` - Defines critical vs optional tests per phase

### Workflow Process
1. Run implementation loop: `./run-implementation-loop-validated.sh`
2. AI reads specs and current state
3. Implements one atomic feature
4. Writes tests first (TDD)
5. Ensures quality gates pass
6. Commits only on success
7. Integration tests run at phase boundaries
8. Regression detection flags issues

## Phase 7: BAML and Model Integration Learnings

### Critical Discovery: Model-Specific Requirements

During Phase 7-8, we discovered that different LLM models have incompatible parameter and message format requirements that weren't initially documented:

1. **Claude/Gemini Message Requirements**:
   - These models REQUIRE at least one user message
   - System-only prompts fail with "messages: at least one message is required"
   - Initially thought it was a content format issue (array vs string)
   - Real issue: Missing user messages in BAML prompts

2. **O-Series Parameter Quirks**:
   - O-series models (gpto3) SILENTLY IGNORE max_tokens parameter
   - Must use max_completion_tokens instead
   - No error thrown, making this hard to discover
   - Discovered through communication with Argo team

3. **BAML Prompt Structure**:
   - All BAML prompts were using system-only messages
   - Had to update all 8 BAML functions to include both system and user roles
   - Created TEMPLATE.baml to ensure future functions follow correct pattern

### The Debugging Journey

The path to discovering the real issue was complex:

1. **Initial Error**: Claude returning dict instead of string for system content
2. **First Theory**: Content format issue (array vs string)
3. **Attempted Fix**: Local patches to normalize content
4. **Real Discovery**: Argo API error revealed user message requirement
5. **Collaboration**: Worked with Argo team (Matt Dearing, Peng Ding) to understand
6. **Final Solution**: Update all BAML prompts to use system + user pattern

### Key Lessons for BAML Integration

1. **Always Use Both Roles**:
   ```baml
   prompt #"
     {{ _.role("system") }}
     General instructions here
     
     {{ _.role("user") }}
     Specific request with parameters here
   "#
   ```

2. **Test with Multiple Models Early**:
   - Don't assume all models have same requirements
   - Test Claude, Gemini, and OpenAI models from the start
   - Document model-specific quirks immediately

3. **Create Templates and Validation**:
   - TEMPLATE.baml for future functions
   - Unit tests to validate prompt structure
   - Update specs with requirements

## Phase 8: Real LLM Testing Integration

### The Need for Behavioral Testing

After resolving model compatibility issues, we realized that while mocked tests verify functionality, they don't verify AI behavior quality. This led to implementing a parallel real LLM testing strategy.

### Implementation Approach

1. **Separate Test Files**: `test_phaseN_*_real.py` pattern
2. **Consistent Marking**: `@pytest.mark.real_llm` (not environment variables)
3. **test_expectations.json Enhancement**:
   ```json
   {
     "phase_9": {
       "must_pass": [...],
       "may_fail": [...],
       "real_llm_tests": [
         "test_task_decomposition_quality",
         "test_o3_reasoning_visibility"
       ]
     }
   }
   ```

### Integration with Development Loop

The implementation loop now shows available real LLM tests:
```
💡 Real LLM Tests Available
Found 2 real LLM test files
Run with: pytest tests/integration/*_real.py -v --real-llm
```

### Key Benefits Discovered

1. **Early Detection**: Found that Gemini models often return empty responses
2. **Behavioral Validation**: Verified o3 actually shows step-by-step reasoning
3. **Model Selection**: Led to switching default from Gemini to GPT-o3
4. **Integration Confidence**: Actual LLM calls work through BAML/Argo

### Best Practices Established

1. **Write Alongside Regular Tests**: Same phase, different file
2. **Focus on Behaviors**: Test reasoning patterns, not exact text
3. **Minimal Token Usage**: Keep tests under 100 tokens each
4. **Optional Execution**: Not part of automated loop
5. **Helper Scripts**: `scripts/run-real-llm-tests.sh` for easy execution

## Lessons Learned

### What Works Well
1. **Detailed Specs First**: Having complete specs prevents scope creep
2. **Atomic Iterations**: Small, testable chunks prevent cascading failures
3. **Quality Gates**: Automated enforcement maintains code quality
4. **Test-First**: Writing tests first ensures testable, modular code
5. **Phase-Based Progress**: Clear milestones help track progress

### Common Pitfalls Avoided
1. **Big Bang Implementation**: Trying to build too much at once
2. **Test-After Development**: Tests written after miss edge cases
3. **No Quality Enforcement**: Leads to technical debt accumulation
4. **Missing Integration Tests**: Unit tests pass but system doesn't work
5. **No Regression Detection**: Breaking changes go unnoticed

### AI-Specific Insights
1. **Context Management**: Clear, focused prompts work better
2. **Explicit Rules**: AI follows explicit rules better than implicit
3. **Checkpoint Often**: Easy rollback when experiments fail
4. **Verify Output**: Always check AI's work with automated tests
5. **Iterative Refinement**: Workflow improves through usage
6. **Test Placement Matters**: Without explicit directory rules, AI makes inconsistent decisions
7. **Coverage Can Mislead**: Always check coverage at the right granularity
8. **BAML for LLM**: Using BAML eliminates direct API call complexity
9. **Sync Configuration**: Keep all config files (env, BAML, etc.) synchronized
10. **Fix Tests Immediately**: Two small test failures can block entire pipeline
11. **Real LLM Tests Valuable**: Behavioral verification catches issues mocked tests miss
12. **Separate Test Tracking**: Real LLM tests tracked separately from regular tests
13. **Model Selection Matters**: GPT-o3 for reasoning, Claude for creativity, GPT-3.5 for simple tasks

## Reproducible Process

To use this complete workflow for another project:

### Phase 1: Specification Development

1. **Gather Source Materials**
   ```bash
   mkdir -p specs-source/
   # Add research papers, blog posts, diagrams
   # Include reference implementations if available
   ```

2. **Set Up Spec Development Framework**
   ```bash
   # Copy spec development files:
   cp docs/spec-development/SPECS_CLAUDE.md new-project/
   cp docs/spec-development/specs-prompt.md new-project/
   cp docs/spec-development/run-spec-loop-improved.sh new-project/
   
   # Initialize empty plan:
   echo "Nothing here yet" > SPECS_PLAN.md
   ```

3. **Run Spec Development Loop**
   ```bash
   ./run-spec-loop-improved.sh
   # First run: AI creates SPECS_PLAN.md
   # Subsequent runs: AI creates individual specs
   
   # Or continuous mode:
   ./run-spec-loop-improved.sh --letitrip
   ```

4. **Review and Refine Specs**
   - Ensure CLEANROOM principles followed
   - Check for completeness
   - Run gap analysis if needed

### Phase 2: Implementation

1. **Set Up Development Environment**
   ```bash
   # Install uv for fast package management (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Set Up Implementation Framework**
   ```bash
   # Copy implementation files:
   cp CLAUDE.md new-project/
   cp prompt.md new-project/
   cp run-implementation-loop-validated.sh new-project/
   cp -r scripts/ new-project/scripts/
   
   # Initialize empty plan:
   echo "Nothing here yet" > IMPLEMENTATION_PLAN.md
   
   # Set up development environment
   ./scripts/setup-dev.sh
   ```

3. **Run Implementation Loop**
   ```bash
   ./run-implementation-loop-validated.sh
   # Or continuous mode:
   ./run-implementation-loop-validated.sh --letitrip
   ```

4. **Set Up Integration Testing**
   ```bash
   # Copy testing framework:
   cp INTEGRATION_TESTING_PLAN.md new-project/
   cp -r tests/integration/ new-project/tests/
   cp test_expectations.json new-project/
   ```

5. **Monitor Progress**
   - Check IMPLEMENTATION_PLAN.md for tasks (17 phases total)
   - Review git log for history
   - Watch for .implementation_flags (regression or implementation errors)
   - Integration tests run automatically per phase
   - Check test_expectations.json to understand test requirements

### Key Success Factors

1. **Quality Source Materials**: Good specs need good sources
2. **Empty Starting Point**: Let AI organize based on understanding
3. **Iterative Process**: One task per iteration prevents errors
4. **Quality Gates**: Automated enforcement maintains standards
5. **Integration Testing**: Validate functionality without disrupting flow

## Future Improvements

1. **Automated Spec Validation**: Ensure specs are complete/consistent
2. **Performance Benchmarking**: Track implementation performance
3. **Multi-AI Collaboration**: Different AIs for different tasks
4. **Automated Documentation**: Generate docs from implementation
5. **Continuous Deployment**: Automated deployment on quality gates

## The Loop Philosophy and Memory Model

### Why Loops Instead of Continuous Sessions?

The loop-based approach is fundamental to achieving reliable AI-assisted development:

1. **Fresh Perspective Each Iteration**
   - Each loop creates a new AI instance with no memory of previous iterations
   - Prevents assumption buildup and drift from specifications
   - Forces re-reading of specs and current state each time

2. **Spec-Driven Development**
   - Every iteration starts by reading specifications
   - Implementation decisions based on documented requirements, not memory
   - Ensures consistency with original design

3. **Quality Gates Between Iterations**
   - Tests must pass before proceeding
   - Coverage thresholds enforced
   - Human review points built in

### Memory Model: What Persists vs What Doesn't

#### What DOESN'T Persist Between Iterations:
- Specific implementation decisions from previous loops
- Temporary reasoning or assumptions
- Any "learning" from previous attempts
- Context about why certain choices were made

#### What DOES Persist (Via Files):
- **Git History**: Complete record of all changes
- **IMPLEMENTATION_PLAN.md**: Progress tracking with checkboxes
- **Source Code**: All created/modified files
- **Tests**: Documented expected behavior
- **Comments/Docstrings**: Implementation context

### The Workflow in Practice

```bash
# 1. Exit current Claude Code session
# 2. Run implementation loop
./run-implementation-loop-validated.sh

# 3. After iteration completes, restart Claude Code to:
#    - Review what was implemented
#    - Run tests manually  
#    - Debug any issues
#    - Understand the code

# 4. Continue loop or fix issues
# 5. Repeat until complete
```

### Why This Works Better Than Continuous Sessions

1. **Prevents Drift**: Can't gradually move away from specs
2. **Enforces Discipline**: Must follow process each time
3. **Traceable Progress**: Everything documented in files
4. **Recoverable State**: Can always restart from known good state
5. **Parallel Development**: Multiple loops can work on different components

## The "Nothing Here Yet" Pattern

A critical discovery that enables the loop approach:

### Why It Works
1. **Forces Complete Understanding**: AI must read all materials to create a plan
2. **Reveals AI's Mental Model**: Shows how AI organizes complex systems
3. **Prevents Bias**: No human preconceptions about structure
4. **Enables Creativity**: AI might find novel ways to organize

### The Two-Step Process
1. **First Run**: AI reads everything and creates the plan
2. **Subsequent Runs**: AI executes the plan it created

This pattern combined with the loop approach ensures AI truly understands the system rather than just following a template.

## Conclusion

This workflow demonstrates that AI-assisted development can be highly effective when combined with:
- Clear specifications from source materials
- The "Nothing here yet" pattern for AI autonomy
- Disciplined iterative process
- Automated quality enforcement
- Continuous validation

The complete journey from research papers → specs → implementation shows that AI can handle complex software development tasks when given proper structure and verification. The key is treating AI as a powerful but fallible tool that requires clear guidance, quality gates, and continuous improvement to achieve reliable results.

## Phase 9: Model-Specific Configuration Management

### Late Discovery of Model Incompatibilities

One of our biggest challenges came from discovering model-specific requirements late in the development cycle. Here's what we learned:

1. **Different Models, Different Rules**:
   - OpenAI models: Standard parameters work
   - O-series (o3): Only max_completion_tokens, ignores max_tokens
   - Claude/Gemini: Require user messages, normalize array content
   - Each model family has unique quirks

2. **BAML's Role in Abstraction**:
   - BAML generates OpenAI-compatible format
   - But models interpret this format differently
   - Need model-specific handling at multiple layers

3. **Testing Strategy Evolution**:
   - Started with single model (mock) testing
   - Discovered issues only when testing real models
   - Should have tested multiple models from Phase 7

### How the Implementation Loop Should Handle This

If we knew about model requirements from the beginning:

1. **Phase 7 BAML Setup Would Include**:
   ```markdown
   ## Phase 7: BAML Infrastructure
   - [ ] Create TEMPLATE.baml with system+user pattern
   - [ ] Write model compatibility tests
   - [ ] Test with at least 3 different model families
   - [ ] Document model-specific parameters
   - [ ] Create validation for BAML prompt structure
   ```

2. **Specs Would Define Model Requirements**:
   ```markdown
   # Spec 023: LLM Abstraction
   
   ## Model-Specific Requirements
   - O-series: Use max_completion_tokens, not max_tokens
   - Claude/Gemini: Require user messages
   - All models: Support both system and user roles
   ```

3. **Test Expectations Would Include Model Tests**:
   ```json
   {
     "phase_7": {
       "must_pass": [
         "test_baml_prompt_structure",
         "test_claude_compatibility",
         "test_o_series_parameters"
       ]
     }
   }
   ```

## Implementing This Workflow From Scratch: Lessons Learned

If we were to start this project (or a similar one) from scratch today, knowing everything we've learned, here's how we would structure it differently to avoid the issues we encountered:

### 1. Pre-Project Setup

#### Create the Complete Framework First
```bash
# Create all workflow files before any implementation
mkdir -p new-project/{specs,specs-source,docs,tests/integration,scripts}
cd new-project
```

#### Essential Files to Create Upfront:

**CLAUDE.md** (Implementation Guidelines):
```markdown
# Implementation Guidelines

## Core Philosophy: IMPLEMENT FROM SPECS. Build behavior exactly as specified.

## Test Organization
- Unit tests: tests/unit/test_*.py
- Integration tests: tests/integration/test_phase*_*.py
- NO other test subdirectories
- NO tests in root tests/ directory

## Implementation Workflow
1. Check for flags: .implementation_flags (REGRESSION/ERROR)
2. One task per iteration from IMPLEMENTATION_PLAN.md
3. Write failing tests FIRST (TDD)
4. Implement minimal code to pass
5. All tests must pass before commit
6. Coverage must meet 80% threshold (unit tests only)

## Integration Testing
- Phase 3+: Integration tests define behavior
- test_expectations.json defines must_pass vs may_fail
- Unit tests may need updates when implementing advanced features

## Critical Rules
1. Follow specs exactly - no deviations
2. Every file should get smaller after iteration 10+
3. One atomic feature per iteration
4. Read ENTIRE file before modifying
5. Use BAML for all LLM interactions
6. Keep .env.example and environment.baml synchronized
```

**prompt.md** (Implementation Task Template):
```markdown
Please implement the next unchecked task from IMPLEMENTATION_PLAN.md.

Follow these steps:
1. Write failing tests first (TDD)
2. Implement minimal code to pass tests
3. Ensure all tests pass
4. Update IMPLEMENTATION_PLAN.md checkbox

For Phase 3+: Check test_expectations.json for integration test requirements.
If unit tests fail after implementing integration test features, update unit tests to match the new behavior.

Focus on atomic, testable features. Exit after one task completion.
```

**test_expectations.json**:
```json
{
  "phase_3": {
    "must_pass": [
      "test_task_queue_basic_operations",
      "test_worker_registration",
      "test_task_assignment"
    ],
    "may_fail": [
      "test_supervisor_agent",
      "test_generation_agent"
    ]
  }
}
```

### 2. Specification Phase Changes

#### Key Change: Define Integration Test Points in Specs

When writing specs, explicitly mark "integration points" where functionality can be tested:

```markdown
# Spec 004: Task Queue

## Integration Points
- Phase 3: Basic queue operations testable
- Phase 8: Queue + Worker coordination testable
- Phase 16: Full system integration testable

## Behavior Specification
...
```

This allows the implementation plan to know when to add integration tests.

### 3. Implementation Plan Structure

#### Generate Plan with Test Awareness

The initial IMPLEMENTATION_PLAN.md should include:

```markdown
# Implementation Plan

## Phase 1: Project Setup and Dependencies
- [ ] Set up project structure
- [ ] Create development environment setup script
- [ ] Write project setup tests

## Phase 2: Core Models
- [ ] Implement Task model
- [ ] Implement Hypothesis model
- [ ] Write comprehensive model tests

## Phase 3: Task Queue (FIRST INTEGRATION POINT)
- [ ] Implement basic task queue operations
- [ ] Write unit tests for queue
- [ ] **Write Phase 3 integration tests**
- [ ] Ensure integration tests pass

## Phase 4: Context Memory
...
```

### 4. Modified Implementation Loop

**run-implementation-loop-validated.sh** changes:

```bash
#!/bin/bash

# Add pre-flight checks
if [ ! -f "test_expectations.json" ]; then
    echo "❌ Missing test_expectations.json - required for integration testing"
    exit 1
fi

# Detect current phase from IMPLEMENTATION_PLAN.md
CURRENT_PHASE=$(grep -E "^## Phase [0-9]+" IMPLEMENTATION_PLAN.md | grep -B1 "\[ \]" | head -1 | sed 's/.*Phase \([0-9]\+\).*/\1/')

# Run tests with proper exit status handling
pytest tests/ --tb=short -v 2>&1 | tee ".test_output_${iteration}.tmp"
test_exit_status=${PIPESTATUS[0]}

if [ $test_exit_status -eq 0 ]; then
    echo "✅ All tests passed"
else
    echo "❌ Tests failed!"
    return 1
fi

# Separate coverage for unit and integration tests
echo "Checking unit test coverage..."
pytest tests/unit/ --cov=src --cov-fail-under=80

echo "Running integration test coverage (informational)..."
if [ "$CURRENT_PHASE" -ge 3 ]; then
    pytest tests/integration/ --cov=src --cov-report=term
fi
```

### 5. Key Process Improvements

#### A. Start with Integration Test Skeletons

Create empty integration tests for each phase upfront:

```python
# tests/integration/test_phase_3_task_queue.py
import pytest

@pytest.mark.integration
@pytest.mark.phase_3
async def test_task_queue_basic_operations():
    """Test basic queue operations work as specified."""
    pytest.skip("Implement when Phase 3 is complete")

@pytest.mark.integration  
@pytest.mark.phase_3
async def test_worker_registration():
    """Test worker registration and management."""
    pytest.skip("Implement when Phase 3 is complete")
```

#### B. Dual Test Strategy from Day One

1. **Unit Tests**: Implementation details, internal APIs
2. **Integration Tests**: Spec behavior, external interfaces

Make this distinction clear in CLAUDE.md.

#### C. Phase-Aware Quality Gates

```python
# scripts/check_quality_gates.py
def get_required_tests(phase):
    """Return tests that must pass for current phase."""
    with open('test_expectations.json') as f:
        expectations = json.load(f)
    
    must_pass = []
    for p in range(1, phase + 1):
        phase_key = f"phase_{p}"
        if phase_key in expectations:
            must_pass.extend(expectations[phase_key]["must_pass"])
    
    return must_pass
```

### 6. Avoiding Common Pitfalls

#### A. Duplicate Method Problem
Add to CLAUDE.md:
```markdown
## Code Hygiene Rules
- NEVER create duplicate method definitions
- If modifying behavior, UPDATE existing method
- Run `grep -n "def method_name"` before adding methods
```

#### B. API Contract Changes
Add to test strategy:
```markdown
## Handling API Evolution
- Unit tests may need updates when implementing advanced features
- Integration tests define the contract - they should NOT change
- Document API changes in method docstrings
```

#### C. The "Trust the Process" Trap
Be explicit about what the loop can and cannot do:
```markdown
## Loop Capabilities
✓ CAN: Implement new features from specs
✓ CAN: Write tests for new functionality
✓ CAN: Fix implementation bugs

✗ CANNOT: Reconcile unit test vs integration test conflicts
✗ CANNOT: Decide if API changes are intentional
✗ CANNOT: Update tests without human review
```

### 7. Test Organization Best Practices

#### Preventing Test Location Issues

Based on our Phase 8 experience, enforce test organization from day one:

1. **Pre-create test directories**:
   ```bash
   mkdir -p tests/{unit,integration}
   touch tests/__init__.py
   touch tests/unit/__init__.py
   touch tests/integration/__init__.py
   ```

2. **Add .gitkeep files**:
   ```bash
   # Ensure directories exist in git
   touch tests/unit/.gitkeep
   touch tests/integration/.gitkeep
   ```

3. **Add validation to implementation loop**:
   ```bash
   # Check for misplaced tests
   MISPLACED_TESTS=$(find tests -name "test_*.py" -type f | \
                     grep -v "/unit/" | grep -v "/integration/" | \
                     grep -v "__pycache__")
   
   if [ -n "$MISPLACED_TESTS" ]; then
       echo "❌ Tests found in wrong location:"
       echo "$MISPLACED_TESTS"
       echo "Move to tests/unit/ or tests/integration/"
       exit 1
   fi
   ```

### 8. Optimal Project Structure

```
project/
├── CLAUDE.md                    # Implementation guidelines with test rules
├── prompt.md                    # Task prompt template
├── IMPLEMENTATION_PLAN.md       # Progress tracking (starts empty)
├── test_expectations.json       # Phase-based test requirements
├── run-implementation-loop-validated.sh
├── specs/
│   ├── 001-system-overview.md
│   └── ... (all specs with integration points marked)
├── tests/
│   ├── __init__.py
│   ├── unit/               # ALL unit tests go here
│   │   ├── __init__.py
│   │   └── test_*.py
│   └── integration/        # ALL integration tests go here
│       ├── __init__.py
│       ├── test_phase_3_*.py
│       └── conftest.py
├── baml_src/              # BAML configuration
│   ├── models.baml
│   ├── clients.baml
│   ├── environment.baml
│   └── functions.baml
└── scripts/
    ├── setup-dev.sh
    └── check_quality_gates.py
```

### 9. First Day Checklist

1. ✓ Create all workflow files (don't evolve them)
2. ✓ Write specs with integration points marked  
3. ✓ Create test_expectations.json for all phases
4. ✓ Set up integration test skeletons
5. ✓ Configure quality gates for Phase 1
6. ✓ Run spec loop to generate IMPLEMENTATION_PLAN.md
7. ✓ Review plan for integration test tasks
8. ✓ Start implementation loop

### 10. BAML-Specific Project Setup

If using BAML for LLM interactions (highly recommended), set up from day one:

#### BAML Directory Structure
```
baml_src/
├── TEMPLATE.baml          # Prompt structure template
├── models.baml            # Data models with aliases
├── clients.baml           # Model configurations
├── environment.baml       # Environment variables
├── functions.baml         # LLM function definitions
└── test_scenarios.baml    # Test configurations
```

#### Critical BAML Template (TEMPLATE.baml)
```baml
// CRITICAL: All functions MUST follow this pattern
// for Claude/Gemini compatibility

function ExampleFunction(param: string) -> ReturnType {
  client ProductionClient
  
  prompt #"
    {{ _.role("system") }}
    You are an expert at [task].
    [General capabilities]
    
    {{ _.role("user") }}
    [Specific request]
    
    Input: {{ param }}
    
    [Task instructions]
  "#
}

// Model-Specific Notes:
// - o3: Use max_completion_tokens (NOT max_tokens)
// - Claude/Gemini: REQUIRE user message
// - All models: Support system+user pattern
```

#### Model Configuration (clients.baml)
```baml
client ProductionClient {
  provider argo
  options {
    model_map {
      "default": "gpt4o",
      "reasoning": "gpto3",
      "creative": "claudeopus4",
      "fast": "gpt35"
    }
  }
}
```

#### BAML Validation Tests
Create `tests/unit/test_baml_prompt_structure.py`:
```python
def test_all_functions_have_system_and_user_roles():
    """Ensure BAML functions work with all models."""
    # Validates all prompts have both roles
    # Prevents Claude/Gemini failures
```

### 11. The Complete Workflow Command Sequence

```bash
# Day 1: Setup and Specs
git init
cp -r workflow-template/* .  # All files from section 7

# Set up BAML structure
mkdir -p baml_src
cp templates/TEMPLATE.baml baml_src/
cp templates/test_baml_prompt_structure.py tests/unit/

# Run spec development
./run-spec-loop-improved.sh --letitrip
git tag -a "specs-complete" -m "All specifications complete"

# Day 2+: Implementation  
./run-implementation-loop-validated.sh --letitrip
# Loop handles everything: planning, implementation, testing

# When issues arise:
# 1. Stop loop (Ctrl+C)
# 2. Fix issues manually
# 3. Commit fixes
# 4. Resume loop
```

### Key Insight: Front-Load the Structure

The main lesson is that investing time in creating the complete workflow structure upfront prevents numerous issues:
- No confusion about when to write integration tests
- Clear phase boundaries with test requirements
- Explicit handling of unit vs integration test conflicts  
- No API drift or duplicate implementations

This approach would have avoided the Phase 3 unit test issues entirely because:
1. Integration tests would exist from the start
2. test_expectations.json would clarify what must pass
3. CLAUDE.md would explain how to handle conflicts
4. The implementation would follow integration tests, not unit tests

The workflow remains simple (just run the loop), but the structure ensures it handles edge cases correctly from day one.

## Key Takeaways: Model Integration and BAML

### The Hidden Complexity of "Model-Agnostic" Systems

Our journey revealed that true model agnosticism requires understanding model-specific requirements:

1. **Message Format Requirements**:
   - What works: System + User messages (all models)
   - What doesn't: System-only messages (fails on Claude/Gemini)
   - Discovery method: Error messages from actual API calls

2. **Parameter Handling**:
   - Standard models: Use max_tokens
   - O-series: Use max_completion_tokens (max_tokens silently ignored)
   - Discovery method: Observing unexpected behavior + vendor documentation

3. **Content Format Normalization**:
   - BAML sends OpenAI format: `[{"type": "text", "text": "..."}]`
   - Some models expect strings for system role
   - Solution: Proxy layer normalization

### What We'd Do Differently

1. **Multi-Model Testing from Day One**:
   - Don't wait until Phase 8 to test real models
   - Test at least one model from each family in Phase 7
   - Include model compatibility in test_expectations.json

2. **Explicit BAML Requirements in Specs**:
   - Document prompt structure requirements
   - Specify model parameter mappings
   - Include validation tests in implementation plan

3. **Vendor Communication Earlier**:
   - Engage with API providers during design phase
   - Document all model quirks in central location
   - Share findings with community

### The Value of Debugging Scripts

Our exploratory scripts proved invaluable:
- `claude-system-only-test.py`: Isolated the user message requirement
- `test-claude-peng-fix.py`: Validated proxy fixes
- Keep these as regression tests

### Final Workflow Enhancement

Add to initial project setup:
```bash
# Create model testing structure
mkdir -p tests/model_compatibility
cp templates/test_all_models.py tests/model_compatibility/

# Add to IMPLEMENTATION_PLAN.md template:
# Phase 7: BAML Infrastructure
# - [ ] Test prompts with OpenAI, Claude, and Gemini
# - [ ] Document model-specific parameters
# - [ ] Create model compatibility matrix
```

This ensures future projects avoid the 2-day debugging journey we experienced!