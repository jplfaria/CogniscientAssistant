#!/bin/bash

# run-implementation-loop-validated.sh
# Implementation loop with quality gates and validation

# Color codes for better visibility
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
MAX_ITERATIONS=100
COVERAGE_THRESHOLD=80

echo -e "${GREEN}=== AI Co-Scientist Implementation Loop (Validated) ===${NC}"
echo -e "${YELLOW}This implementation loop includes quality gates and validation.${NC}"
echo -e "${CYAN}Each iteration must pass tests and coverage checks before proceeding.${NC}"
echo -e "${YELLOW}Press Ctrl+C at any time to stop.${NC}\n"

# Function to check if pytest is available
check_pytest() {
    if ! command -v pytest &> /dev/null; then
        echo -e "${RED}❌ pytest is not installed. Cannot proceed.${NC}"
        echo -e "${YELLOW}Run: pip install pytest pytest-cov${NC}"
        return 1
    fi
    return 0
}

# Function to detect current implementation phase
detect_implementation_phase() {
    if [ ! -f "IMPLEMENTATION_PLAN.md" ]; then
        echo "0"
        return
    fi
    
    # Check which phase we're in based on uncompleted tasks
    if grep -A30 "## Phase 4: Context Memory" IMPLEMENTATION_PLAN.md | grep -q "^\- \[ \]"; then
        echo "4"
    elif grep -A30 "## Phase 3: Task Queue" IMPLEMENTATION_PLAN.md | grep -q "^\- \[ \]"; then
        echo "3"
    elif grep -A30 "## Phase 5: Safety Framework" IMPLEMENTATION_PLAN.md | grep -q "^\- \[ \]"; then
        echo "5"
    elif grep -A30 "## Phase 6: LLM Abstraction" IMPLEMENTATION_PLAN.md | grep -q "^\- \[ \]"; then
        echo "6"
    elif grep -A30 "## Phase 7: Supervisor Agent" IMPLEMENTATION_PLAN.md | grep -q "^\- \[ \]"; then
        echo "7"
    elif grep -A30 "## Phase 8:" IMPLEMENTATION_PLAN.md | grep -q "^\- \[ \]"; then
        echo "8"
    elif grep -A30 "## Phase 9:" IMPLEMENTATION_PLAN.md | grep -q "^\- \[ \]"; then
        echo "9"
    elif grep -A30 "## Phase 10:" IMPLEMENTATION_PLAN.md | grep -q "^\- \[ \]"; then
        echo "10"
    elif grep -A30 "## Phase 11:" IMPLEMENTATION_PLAN.md | grep -q "^\- \[ \]"; then
        echo "11"
    else
        # Check if any phase 3 tasks are still pending
        if grep -A30 "## Phase 3: Task Queue" IMPLEMENTATION_PLAN.md | grep -q "^\- \[x\]"; then
            echo "3"  # Phase 3 completed
        else
            echo "0"  # Unknown or no phase detected
        fi
    fi
}

# Function to run phase-specific integration tests
run_phase_integration_tests() {
    local current_phase=$(detect_implementation_phase)
    
    echo -e "\n${BLUE}=== Phase Integration Testing ===${NC}"
    
    # Only run integration tests if we have completed phases
    if [ "$current_phase" -ge "3" ] && [ -d "tests/integration" ]; then
        # Find integration test files for current or previous phases
        local test_files=""
        for phase in $(seq 3 $current_phase); do
            if ls tests/integration/phase${phase}_*.py 2>/dev/null | grep -q .; then
                test_files="$test_files tests/integration/phase${phase}_*.py"
            fi
        done
        
        if [ -n "$test_files" ]; then
            echo -e "${CYAN}Running integration tests for completed phases...${NC}"
            echo -e "${CYAN}Current implementation phase: $current_phase${NC}"
            
            # Run the integration tests
            if pytest $test_files -v --tb=short; then
                echo -e "${GREEN}✅ Integration tests passed${NC}"
                # Save success state
                echo "LAST_INTEGRATION_STATUS=passed" > .integration_test_state
                echo "LAST_PASSING_PHASE=$current_phase" >> .integration_test_state
                echo "LAST_PASSING_TIMESTAMP=$(date -Iseconds)" >> .integration_test_state
            else
                # Check if this is a regression
                if [ -f ".integration_test_state" ] && grep -q "LAST_INTEGRATION_STATUS=passed" .integration_test_state; then
                    echo -e "${RED}❌ REGRESSION DETECTED: Integration tests that were passing now fail!${NC}"
                    echo -e "${YELLOW}This indicates broken functionality in completed components.${NC}"
                    echo -e "${CYAN}This needs immediate attention before proceeding.${NC}"
                    
                    # Set regression flag for Claude to see
                    echo "INTEGRATION_REGRESSION=true" > .implementation_flags
                    echo "REGRESSION_DETECTED_AT=$(date -Iseconds)" >> .implementation_flags
                    echo "REGRESSION_PHASE=$current_phase" >> .implementation_flags
                else
                    echo -e "${YELLOW}⚠️  Integration tests failed (informational)${NC}"
                    echo -e "${CYAN}This helps identify integration issues early${NC}"
                    echo -e "${CYAN}These failures are non-blocking but should be investigated${NC}"
                fi
                
                # Save failure state
                echo "LAST_INTEGRATION_STATUS=failed" > .integration_test_state
                echo "LAST_FAILING_PHASE=$current_phase" >> .integration_test_state
                echo "LAST_FAILING_TIMESTAMP=$(date -Iseconds)" >> .integration_test_state
            fi
        else
            echo -e "${CYAN}No integration tests available for phase $current_phase yet${NC}"
        fi
    else
        echo -e "${CYAN}Skipping integration tests - implementation not at testable phase yet${NC}"
    fi
}

# Function to run quality gates
run_quality_gates() {
    local iteration=$1
    echo -e "\n${BLUE}=== Running Quality Gates ===${NC}"
    
    # Only run if we have Python files to test
    if [ -d "src" ] && find src -name "*.py" -type f | grep -q .; then
        # 1. Run tests
        echo -e "${YELLOW}Running tests...${NC}"
        if pytest tests/ --tb=short -v; then
            echo -e "${GREEN}✅ All tests passed${NC}"
        else
            echo -e "${RED}❌ Tests failed! Cannot proceed to next iteration.${NC}"
            echo -e "${YELLOW}Fix the failing tests before continuing.${NC}"
            return 1
        fi
        
        # 2. Check coverage
        echo -e "\n${YELLOW}Checking code coverage...${NC}"
        coverage_output=$(pytest --cov=src --cov-report=term-missing --cov-fail-under=$COVERAGE_THRESHOLD 2>&1)
        coverage_status=$?
        
        echo "$coverage_output" | tail -20  # Show last 20 lines of coverage report
        
        if [ $coverage_status -eq 0 ]; then
            echo -e "${GREEN}✅ Coverage meets ${COVERAGE_THRESHOLD}% threshold${NC}"
        else
            echo -e "${RED}❌ Coverage below ${COVERAGE_THRESHOLD}% threshold!${NC}"
            echo -e "${YELLOW}Improve test coverage before continuing.${NC}"
            return 1
        fi
        
        # 3. Type checking (if mypy configured)
        if command -v mypy &> /dev/null && [ -f "mypy.ini" ]; then
            echo -e "\n${YELLOW}Running type checks...${NC}"
            if mypy src/; then
                echo -e "${GREEN}✅ Type checks passed${NC}"
            else
                echo -e "${YELLOW}⚠️  Type errors detected (non-blocking)${NC}"
            fi
        fi
        
        # 4. Linting (if ruff configured)
        if command -v ruff &> /dev/null && [ -f ".ruff.toml" ]; then
            echo -e "\n${YELLOW}Running linter...${NC}"
            if ruff check src/ tests/; then
                echo -e "${GREEN}✅ Linting passed${NC}"
            else
                echo -e "${YELLOW}⚠️  Linting issues detected (non-blocking)${NC}"
            fi
        fi
        
        # 5. Run phase-specific integration tests
        run_phase_integration_tests
    else
        echo -e "${CYAN}No Python files to test yet - skipping quality gates${NC}"
    fi
    
    return 0
}

# Track iterations
ITERATION=0

# Main loop
while [ $ITERATION -lt $MAX_ITERATIONS ]; do
    ITERATION=$((ITERATION + 1))
    
    echo -e "\n${GREEN}=== Running implementation iteration $ITERATION ===${NC}"
    echo -e "${BLUE}--- Claude is implementing... ---${NC}\n"
    
    # Create temporary file for output
    TEMP_OUTPUT=".claude-implementation-output-$$.tmp"
    
    # Run Claude with implementation prompt
    cat prompt.md | claude -p --dangerously-skip-permissions 2>&1 | tee "$TEMP_OUTPUT"
    
    echo -e "\n${MAGENTA}--- End of Claude's implementation ---${NC}"
    
    # Check if implementation is complete
    if grep -q "Implementation complete\|All components implemented\|No more implementation tasks" "$TEMP_OUTPUT" 2>/dev/null; then
        echo -e "\n${GREEN}✅ Implementation complete!${NC}"
        echo -e "${GREEN}Total iterations: $ITERATION${NC}"
        rm -f "$TEMP_OUTPUT"
        break
    fi
    
    # Check IMPLEMENTATION_PLAN.md for progress
    if [ -f "IMPLEMENTATION_PLAN.md" ]; then
        UNCHECKED_COUNT=$(grep -E "^\- \[ \]" IMPLEMENTATION_PLAN.md 2>/dev/null | wc -l | tr -d ' ')
        
        if [ "$UNCHECKED_COUNT" -eq 0 ] && [ "$(cat IMPLEMENTATION_PLAN.md)" != "Nothing here yet" ]; then
            echo -e "\n${GREEN}✅ All implementation tasks completed!${NC}"
            echo -e "${GREEN}Total iterations: $ITERATION${NC}"
            rm -f "$TEMP_OUTPUT"
            break
        fi
    fi
    
    # Show what was created/modified
    echo -e "\n${YELLOW}Recent changes:${NC}"
    git status --short | head -10
    
    # Show implementation progress
    echo -e "\n${YELLOW}Implementation progress:${NC}"
    if [ -f "IMPLEMENTATION_PLAN.md" ] && [ "$(cat IMPLEMENTATION_PLAN.md)" != "Nothing here yet" ]; then
        echo -e "${CYAN}Recently completed:${NC}"
        grep -E "^\- \[x\]" IMPLEMENTATION_PLAN.md 2>/dev/null | tail -5 || echo "None yet"
        
        echo -e "\n${CYAN}Next tasks:${NC}"
        grep -E "^\- \[ \]" IMPLEMENTATION_PLAN.md 2>/dev/null | head -5 || echo "None"
    fi
    
    # Run quality gates
    if ! run_quality_gates $ITERATION; then
        echo -e "\n${RED}⚠️  Quality gates failed!${NC}"
        echo -e "${YELLOW}Please fix the issues above before continuing.${NC}"
        echo -e "${CYAN}The implementation has been paused.${NC}"
        
        # Show helpful commands
        echo -e "\n${YELLOW}Helpful commands:${NC}"
        echo -e "  ${CYAN}Run tests:${NC} pytest tests/ -v"
        echo -e "  ${CYAN}Check coverage:${NC} pytest --cov=src --cov-report=term-missing"
        echo -e "  ${CYAN}Type check:${NC} mypy src/"
        echo -e "  ${CYAN}Lint:${NC} ruff check src/ tests/"
        echo -e "  ${CYAN}Integration tests:${NC} pytest tests/integration/ -v"
        
        rm -f "$TEMP_OUTPUT"
        exit 1
    fi
    
    # Show latest commits
    echo -e "\n${YELLOW}Recent commits:${NC}"
    git log --oneline -5
    
    # Cleanup temp file
    rm -f "$TEMP_OUTPUT"
    
    # Pause for review
    echo -e "\n${GREEN}✅ Quality gates passed!${NC}"
    echo -e "${CYAN}Press Enter to continue to next iteration, or Ctrl+C to stop...${NC}"
    read -r
done

if [ $ITERATION -eq $MAX_ITERATIONS ]; then
    echo -e "\n${RED}⚠️  Reached maximum iterations ($MAX_ITERATIONS). Stopping to prevent infinite loop.${NC}"
fi

# Final summary
echo -e "\n${GREEN}=== Implementation Summary ===${NC}"
echo -e "${YELLOW}Total iterations:${NC} $ITERATION"

if [ -d "src" ]; then
    echo -e "${YELLOW}Python files created:${NC} $(find src -name "*.py" -type f 2>/dev/null | wc -l | tr -d ' ')"
fi

if [ -d "tests" ]; then
    echo -e "${YELLOW}Test files created:${NC} $(find tests -name "*.py" -type f 2>/dev/null | wc -l | tr -d ' ')"
fi

if [ -f "IMPLEMENTATION_PLAN.md" ]; then
    COMPLETED=$(grep -E "^\- \[x\]" IMPLEMENTATION_PLAN.md 2>/dev/null | wc -l | tr -d ' ')
    REMAINING=$(grep -E "^\- \[ \]" IMPLEMENTATION_PLAN.md 2>/dev/null | wc -l | tr -d ' ')
    echo -e "${YELLOW}Tasks completed:${NC} $COMPLETED"
    echo -e "${YELLOW}Tasks remaining:${NC} $REMAINING"
fi

# Run final quality check
if [ -d "src" ] && find src -name "*.py" -type f | grep -q .; then
    echo -e "\n${BLUE}=== Final Quality Report ===${NC}"
    pytest --cov=src --cov-report=term-missing --tb=short -q
fi

echo -e "\n${GREEN}✨ Implementation loop completed!${NC}"