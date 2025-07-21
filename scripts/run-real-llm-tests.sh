#!/bin/bash
# Run real LLM tests with proper checks and reporting

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo -e "${BLUE}=== Real LLM Test Runner ===${NC}\n"

# Check if argo-proxy is running
check_argo_proxy() {
    echo -e "${YELLOW}Checking Argo proxy status...${NC}"
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${RED}❌ Argo proxy not running!${NC}"
        echo -e "Start it with: ${CYAN}./scripts/manage-argo-proxy.sh start${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Argo proxy is running${NC}\n"
}

# Count available real LLM tests
count_tests() {
    local count=$(find tests/integration -name "*_real.py" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo -e "${YELLOW}Found $count real LLM test files${NC}"
    
    if [ "$count" -eq 0 ]; then
        echo -e "${RED}No real LLM tests found!${NC}"
        echo "Real LLM tests should be named: test_phaseN_*_real.py"
        exit 1
    fi
    
    # List test files
    echo -e "\n${CYAN}Available test files:${NC}"
    find tests/integration -name "*_real.py" -type f | sort | while read -r file; do
        echo "  - $(basename "$file")"
    done
    echo ""
}

# Parse command line arguments
PHASE=""
VERBOSE=""
SHOW_TOKENS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --phase)
            PHASE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        --show-tokens)
            SHOW_TOKENS="true"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --phase N        Run tests for specific phase only"
            echo "  -v, --verbose    Verbose pytest output"
            echo "  --show-tokens    Show token usage (if available)"
            echo "  -h, --help       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h for help"
            exit 1
            ;;
    esac
done

# Main execution
check_argo_proxy
count_tests

# Determine which tests to run
if [ -n "$PHASE" ]; then
    TEST_PATTERN="tests/integration/test_phase${PHASE}_*_real.py"
    echo -e "${YELLOW}Running tests for Phase $PHASE only${NC}\n"
else
    TEST_PATTERN="tests/integration/*_real.py"
    echo -e "${YELLOW}Running all real LLM tests${NC}\n"
fi

# Check if pattern matches any files
if ! ls $TEST_PATTERN 2>/dev/null | grep -q .; then
    echo -e "${RED}No tests found matching pattern: $TEST_PATTERN${NC}"
    exit 1
fi

# Run the tests
echo -e "${BLUE}Starting test execution...${NC}"
echo -e "${CYAN}Command: pytest $TEST_PATTERN $VERBOSE --real-llm --tb=short${NC}\n"

# Create temporary file for output
TEMP_OUTPUT=$(mktemp)

# Run pytest and capture output
if pytest $TEST_PATTERN $VERBOSE --real-llm --tb=short 2>&1 | tee "$TEMP_OUTPUT"; then
    echo -e "\n${GREEN}✅ All real LLM tests passed!${NC}"
    EXIT_CODE=0
else
    echo -e "\n${RED}❌ Some tests failed${NC}"
    EXIT_CODE=1
fi

# Show summary
echo -e "\n${BLUE}=== Test Summary ===${NC}"

# Extract test counts
PASSED=$(grep -E "passed|PASSED" "$TEMP_OUTPUT" | tail -1 | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+" || echo "0")
FAILED=$(grep -E "failed|FAILED" "$TEMP_OUTPUT" | tail -1 | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+" || echo "0")
SKIPPED=$(grep -E "skipped|SKIPPED" "$TEMP_OUTPUT" | tail -1 | grep -oE "[0-9]+ skipped" | grep -oE "[0-9]+" || echo "0")

echo -e "${GREEN}Passed:${NC}  $PASSED"
echo -e "${RED}Failed:${NC}  $FAILED"
echo -e "${YELLOW}Skipped:${NC} $SKIPPED"

# Token usage estimation (if requested)
if [ "$SHOW_TOKENS" = "true" ]; then
    echo -e "\n${BLUE}=== Token Usage Estimate ===${NC}"
    echo "Tests run: $((PASSED + FAILED))"
    echo "Estimated tokens: ~$((($PASSED + $FAILED) * 100))"
    echo "Estimated cost: ~\$$(echo "scale=2; ($PASSED + $FAILED) * 100 * 0.00005" | bc)"
fi

# Cleanup
rm -f "$TEMP_OUTPUT"

# Show next steps
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed! AI behaviors verified.${NC}"
else
    echo -e "\n${YELLOW}Review failed tests to understand AI behavior issues.${NC}"
fi

exit $EXIT_CODE