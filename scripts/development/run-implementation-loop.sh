#!/bin/bash

# run-implementation-loop-validated.sh
# Implementation loop with quality gates and validation

# Create logs directory if it doesn't exist
mkdir -p .implementation_logs

# Function to log iteration results
log_iteration_result() {
    local status=$1
    local iteration=$2
    local timestamp=$(date '+%Y-%m-%d_%H-%M-%S')
    local log_file=".implementation_logs/iteration_${iteration}_${status}_${timestamp}.log"
    
    echo "=== Iteration $iteration - Status: $status ===" > "$log_file"
    echo "Timestamp: $timestamp" >> "$log_file"
    echo "" >> "$log_file"
    
    # Capture all output from the iteration
    if [ -f ".iteration_output_${iteration}.tmp" ]; then
        cat ".iteration_output_${iteration}.tmp" >> "$log_file"
    fi
    
    # Add summary log
    echo "" >> "$log_file"
    echo "=== Summary ===" >> "$log_file"
    echo "Status: $status" >> "$log_file"
    echo "Iteration: $iteration" >> "$log_file"
    
    # If failed, capture test failures
    if [ "$status" = "failed" ] && [ -f ".test_failures_${iteration}.tmp" ]; then
        echo "" >> "$log_file"
        echo "=== Test Failures ===" >> "$log_file"
        cat ".test_failures_${iteration}.tmp" >> "$log_file"
    fi
    
    echo "" >> "$log_file"
    echo "Log saved to: $log_file"
    
    # Create a latest symlink for easy access
    ln -sf "$(basename "$log_file")" ".implementation_logs/latest_${status}.log"
    
    # Clean up temp files
    rm -f ".iteration_output_${iteration}.tmp" ".test_failures_${iteration}.tmp"
}

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
    
    # Check phases in order - return the first one with uncompleted tasks
    for phase in $(seq 1 17); do
        # Get the phase header pattern
        case $phase in
            1) pattern="## Phase 1: Project Setup" ;;
            2) pattern="## Phase 2: Core Data Models" ;;
            3) pattern="## Phase 3: Task Queue" ;;
            4) pattern="## Phase 4: Context Memory" ;;
            5) pattern="## Phase 5: Safety Framework" ;;
            6) pattern="## Phase 6: LLM Abstraction" ;;
            7) pattern="## Phase 7: BAML Infrastructure" ;;
            8) pattern="## Phase 8: Supervisor Agent" ;;
            9) pattern="## Phase 9: Generation Agent" ;;
            10) pattern="## Phase 10: Reflection Agent" ;;
            11) pattern="## Phase 11: Ranking Agent" ;;
            12) pattern="## Phase 12: Evolution Agent" ;;
            13) pattern="## Phase 13: Proximity Agent" ;;
            14) pattern="## Phase 14: Meta-Review Agent" ;;
            15) pattern="## Phase 15: Natural Language" ;;
            16) pattern="## Phase 16: Integration" ;;
            17) pattern="## Phase 17: Final Validation" ;;
        esac
        
        # Check if this phase has uncompleted tasks
        if grep -A30 "$pattern" IMPLEMENTATION_PLAN.md | grep -q "^\- \[ \]"; then
            echo "$phase"
            return
        fi
    done
    
    # If we get here, all phases are complete or no phases found
    echo "17"  # Assume final phase if all complete
}

# Function to analyze test failures against expectations
analyze_test_failures() {
    local phase=$1
    local test_output_file=$2
    local expectations_file="tests/integration/test_expectations.json"
    
    # Check if expectations file exists
    if [ ! -f "$expectations_file" ]; then
        return 1  # No expectations defined, use default behavior
    fi
    
    # Extract test names that failed
    local failed_tests=$(grep -E "FAILED|ERROR" "$test_output_file" | grep -oE "test_[a-zA-Z0-9_]+" | sort -u)
    
    # Get expectations for this phase using python for JSON parsing
    local must_pass_tests=$(python3 -c "
import json
with open('$expectations_file') as f:
    data = json.load(f)
    phase_key = 'phase_$phase'
    if phase_key in data:
        print(' '.join(data[phase_key].get('must_pass', [])))
" 2>/dev/null || echo "")
    
    local may_fail_tests=$(python3 -c "
import json
with open('$expectations_file') as f:
    data = json.load(f)
    phase_key = 'phase_$phase'
    if phase_key in data:
        print(' '.join(data[phase_key].get('may_fail', [])))
" 2>/dev/null || echo "")
    
    # Check if any must_pass tests failed
    local critical_failures=""
    for test in $failed_tests; do
        if echo "$must_pass_tests" | grep -q "$test"; then
            critical_failures="$critical_failures $test"
        fi
    done
    
    if [ -n "$critical_failures" ]; then
        echo "CRITICAL"
        echo "$critical_failures"
    else
        # Check if failures are in may_fail list
        local unexpected_failures=""
        for test in $failed_tests; do
            if ! echo "$may_fail_tests" | grep -q "$test"; then
                unexpected_failures="$unexpected_failures $test"
            fi
        done
        
        if [ -n "$unexpected_failures" ]; then
            echo "UNEXPECTED"
            echo "$unexpected_failures"
        else
            echo "EXPECTED"
            echo "$failed_tests"
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
            if ls tests/integration/test_phase${phase}_*.py 2>/dev/null | grep -q .; then
                test_files="$test_files tests/integration/test_phase${phase}_*.py"
            fi
        done
        
        if [ -n "$test_files" ]; then
            echo -e "${CYAN}Running integration tests for completed phases...${NC}"
            echo -e "${CYAN}Current implementation phase: $current_phase${NC}"
            
            # Save test output to analyze failures
            INTEGRATION_TEST_OUTPUT=".integration-test-output-$$.tmp"
            
            # Run the integration tests and capture output
            if pytest $test_files -v --tb=short 2>&1 | tee "$INTEGRATION_TEST_OUTPUT"; then
                echo -e "${GREEN}✅ Integration tests passed${NC}"
                # Save success state
                echo "LAST_INTEGRATION_STATUS=passed" > .integration_test_state
                echo "LAST_PASSING_PHASE=$current_phase" >> .integration_test_state
                echo "LAST_PASSING_TIMESTAMP=$(date -Iseconds)" >> .integration_test_state
            else
                # Analyze the failure type
                local skip_count=$(grep -c "SKIPPED" "$INTEGRATION_TEST_OUTPUT" || echo "0")
                local xfail_count=$(grep -c "XFAIL" "$INTEGRATION_TEST_OUTPUT" || echo "0")
                local fail_count=$(grep -c "FAILED" "$INTEGRATION_TEST_OUTPUT" || echo "0")
                local error_count=$(grep -c "ERROR" "$INTEGRATION_TEST_OUTPUT" || echo "0")
                
                # Check if this test file has run before for this phase
                local test_history_file=".integration_test_history_phase${current_phase}"
                local is_first_run=true
                if [ -f "$test_history_file" ]; then
                    is_first_run=false
                fi
                
                # Analyze failures against expectations
                local failure_analysis=$(analyze_test_failures "$current_phase" "$INTEGRATION_TEST_OUTPUT")
                local failure_type=$(echo "$failure_analysis" | head -1)
                local failed_test_names=$(echo "$failure_analysis" | tail -n +2)
                
                # Check if this is a regression
                if [ -f ".integration_test_state" ] && grep -q "LAST_INTEGRATION_STATUS=passed" .integration_test_state; then
                    echo -e "${RED}❌ REGRESSION DETECTED: Integration tests that were passing now fail!${NC}"
                    echo -e "${YELLOW}This indicates broken functionality in completed components.${NC}"
                    echo -e "${CYAN}This needs immediate attention before proceeding.${NC}"
                    
                    # Set regression flag for Claude to see
                    echo "INTEGRATION_REGRESSION=true" > .implementation_flags
                    echo "REGRESSION_DETECTED_AT=$(date -Iseconds)" >> .implementation_flags
                    echo "REGRESSION_PHASE=$current_phase" >> .implementation_flags
                # Check if critical tests failed (must_pass tests)
                elif [ "$failure_type" = "CRITICAL" ]; then
                    echo -e "${RED}❌ CRITICAL TEST FAILURE: Required tests for Phase $current_phase failed!${NC}"
                    echo -e "${YELLOW}Failed critical tests:${NC}$failed_test_names"
                    echo -e "${CYAN}These tests MUST pass according to test_expectations.json${NC}"
                    echo -e "${CYAN}Fix the implementation to make these tests pass before proceeding.${NC}"
                    
                    # Set implementation error flag
                    echo "IMPLEMENTATION_ERROR=true" > .implementation_flags
                    echo "ERROR_DETECTED_AT=$(date -Iseconds)" >> .implementation_flags
                    echo "ERROR_PHASE=$current_phase" >> .implementation_flags
                    echo "CRITICAL_TESTS_FAILED=$failed_test_names" >> .implementation_flags
                    
                    # Clean up and exit to force fix
                    rm -f "$INTEGRATION_TEST_OUTPUT"
                    return 2  # Special return code for implementation error
                # Check for unexpected failures
                elif [ "$failure_type" = "UNEXPECTED" ] && [ "$is_first_run" = true ]; then
                    echo -e "${RED}❌ UNEXPECTED TEST FAILURE: Tests not in may_fail list failed!${NC}"
                    echo -e "${YELLOW}Unexpected failures:${NC}$failed_test_names"
                    echo -e "${CYAN}Either fix the implementation or update test_expectations.json${NC}"
                    
                    # Set implementation error flag
                    echo "IMPLEMENTATION_ERROR=true" > .implementation_flags
                    echo "ERROR_DETECTED_AT=$(date -Iseconds)" >> .implementation_flags
                    echo "ERROR_PHASE=$current_phase" >> .implementation_flags
                    echo "UNEXPECTED_TESTS_FAILED=$failed_test_names" >> .implementation_flags
                    
                    # Clean up and exit to force fix
                    rm -f "$INTEGRATION_TEST_OUTPUT"
                    return 2  # Special return code for implementation error
                else
                    # Expected failures or informational
                    if [ "$failure_type" = "EXPECTED" ]; then
                        echo -e "${YELLOW}⚠️  Integration tests failed (expected - in may_fail list)${NC}"
                        echo -e "${CYAN}Failed tests that are allowed to fail:${NC}$failed_test_names"
                    else
                        echo -e "${YELLOW}⚠️  Integration tests failed (informational)${NC}"
                    fi
                    echo -e "${CYAN}This helps identify integration issues early${NC}"
                    echo -e "${CYAN}These failures are non-blocking${NC}"
                    if [ "$skip_count" -gt 0 ]; then
                        echo -e "${CYAN}Skipped tests: $skip_count (expected - waiting for future components)${NC}"
                    fi
                    if [ "$xfail_count" -gt 0 ]; then
                        echo -e "${CYAN}Expected failures: $xfail_count${NC}"
                    fi
                fi
                
                # Mark that we've run tests for this phase
                echo "FIRST_RUN_AT=$(date -Iseconds)" > "$test_history_file"
                
                # Save failure state
                echo "LAST_INTEGRATION_STATUS=failed" > .integration_test_state
                echo "LAST_FAILING_PHASE=$current_phase" >> .integration_test_state
                echo "LAST_FAILING_TIMESTAMP=$(date -Iseconds)" >> .integration_test_state
            fi
            
            # Clean up temp file
            rm -f "$INTEGRATION_TEST_OUTPUT"
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
        pytest tests/ --tb=short -v 2>&1 | tee ".test_output_${iteration}.tmp"
        test_exit_status=${PIPESTATUS[0]}
        
        if [ $test_exit_status -eq 0 ]; then
            echo -e "${GREEN}✅ All tests passed${NC}"
        else
            echo -e "${RED}❌ Tests failed! Cannot proceed to next iteration.${NC}"
            echo -e "${YELLOW}Fix the failing tests before continuing.${NC}"
            # Extract test failures for the log
            grep -E "FAILED|ERROR" ".test_output_${iteration}.tmp" > ".test_failures_${iteration}.tmp" 2>/dev/null || true
            rm -f ".test_output_${iteration}.tmp"
            return 1
        fi
        
        # 2. Check coverage (Unit tests only for threshold)
        echo -e "\n${YELLOW}Checking unit test coverage...${NC}"
        echo -e "${CYAN}Note: 80% coverage threshold applies to unit tests only${NC}"
        
        # Run unit tests with coverage threshold
        unit_coverage_output=$(pytest tests/unit/ --cov=src --cov-report=term-missing --cov-fail-under=$COVERAGE_THRESHOLD 2>&1)
        unit_coverage_status=$?
        
        echo "$unit_coverage_output" | tail -20  # Show last 20 lines of coverage report
        
        if [ $unit_coverage_status -eq 0 ]; then
            echo -e "${GREEN}✅ Unit test coverage meets ${COVERAGE_THRESHOLD}% threshold${NC}"
        else
            echo -e "${RED}❌ Unit test coverage below ${COVERAGE_THRESHOLD}% threshold!${NC}"
            echo -e "${YELLOW}Improve unit test coverage before continuing.${NC}"
            return 1
        fi
        
        # Run integration test coverage (informational only)
        if [ -d "tests/integration" ] && ls tests/integration/test_*.py 2>/dev/null | grep -q .; then
            echo -e "\n${YELLOW}Running integration test coverage (informational)...${NC}"
            integration_coverage_output=$(pytest tests/integration/ --cov=src --cov-report=term-missing 2>&1)
            echo "$integration_coverage_output" | tail -15  # Show coverage summary
            echo -e "${CYAN}Integration test coverage is informational only (no threshold)${NC}"
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
        local integration_result=$?
        
        # Check if integration tests found implementation errors
        if [ $integration_result -eq 2 ]; then
            echo -e "\n${RED}❌ Implementation error detected in integration tests!${NC}"
            echo -e "${YELLOW}The implementation doesn't match the specifications.${NC}"
            echo -e "${CYAN}Fix the implementation to match the expected behavior before continuing.${NC}"
            return 1  # Fail quality gates to stop the loop
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
    
    # Start capturing all output for this iteration
    exec 3>&1 4>&2
    exec 1> >(tee -a ".iteration_output_${ITERATION}.tmp")
    exec 2>&1
    
    echo -e "${BLUE}--- Claude is implementing... ---${NC}\n"
    
    # Create temporary file for output
    TEMP_OUTPUT=".claude-implementation-output-$$.tmp"
    
    # Read the prompt content
    PROMPT_CONTENT=$(cat prompt.md)
    
    # Run Claude with implementation prompt
    claude -p --dangerously-skip-permissions "$PROMPT_CONTENT" 2>&1 | tee "$TEMP_OUTPUT"
    
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
        
        # Restore original stdout/stderr
        exec 1>&3 2>&4
        exec 3>&- 4>&-
        
        # Log failed iteration
        log_iteration_result "failed" "$ITERATION"
        
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
    
    # Restore original stdout/stderr
    exec 1>&3 2>&4
    exec 3>&- 4>&-
    
    # Log successful iteration
    log_iteration_result "success" "$ITERATION"
    
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
    echo -e "${YELLOW}Unit Test Coverage:${NC}"
    pytest tests/unit/ --cov=src --cov-report=term-missing --tb=short -q
    
    if [ -d "tests/integration" ] && ls tests/integration/test_*.py 2>/dev/null | grep -q .; then
        echo -e "\n${YELLOW}Integration Test Coverage:${NC}"
        pytest tests/integration/ --cov=src --cov-report=term-missing --tb=short -q
    fi
fi

# Check for available real LLM tests
REAL_LLM_COUNT=$(find tests/integration -name "*_real.py" -type f 2>/dev/null | wc -l | tr -d ' ')
if [ "$REAL_LLM_COUNT" -gt 0 ]; then
    echo -e "\n${BLUE}💡 Real LLM Tests Available${NC}"
    echo -e "${YELLOW}Found $REAL_LLM_COUNT real LLM test files${NC}"
    echo -e "Run with: ${CYAN}pytest tests/integration/*_real.py -v --real-llm${NC}"
    
    # Get current phase
    CURRENT_PHASE=$(detect_implementation_phase)
    if [ -n "$CURRENT_PHASE" ]; then
        echo -e "For current phase: ${CYAN}pytest tests/integration/test_phase${CURRENT_PHASE}_*_real.py -v --real-llm${NC}"
    fi
fi

echo -e "\n${GREEN}✨ Implementation loop completed!${NC}"

# Create summary log
if [ -d ".implementation_logs" ]; then
    summary_file=".implementation_logs/session_summary_$(date '+%Y-%m-%d_%H-%M-%S').log"
    echo "=== Implementation Session Summary ===" > "$summary_file"
    echo "Total iterations: $ITERATION" >> "$summary_file"
    echo "" >> "$summary_file"
    echo "Logs created:" >> "$summary_file"
    ls -la .implementation_logs/iteration_*.log >> "$summary_file" 2>/dev/null || true
    echo "" >> "$summary_file"
    echo "Session summary saved to: $summary_file"
fi