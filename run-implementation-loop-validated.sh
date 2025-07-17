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