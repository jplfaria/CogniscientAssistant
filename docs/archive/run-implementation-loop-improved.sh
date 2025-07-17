#!/bin/bash

# Check for --letitrip flag
LETITRIP=false
if [[ "$1" == "--letitrip" ]]; then
    LETITRIP=true
fi

# Color codes for better visibility
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI Co-Scientist Implementation Loop ===${NC}"
if [ "$LETITRIP" = true ]; then
    echo -e "${YELLOW}Running in continuous mode (--letitrip). Will run until implementation is complete.${NC}"
else
    echo -e "${YELLOW}This will run implementation tasks, pausing between each for review.${NC}"
fi
echo -e "${CYAN}Full implementation process will be captured and displayed.${NC}"
echo -e "${YELLOW}Press Ctrl+C at any time to stop.${NC}\n"

# Track iterations
ITERATION=0
MAX_ITERATIONS=100  # Safety limit

while [ $ITERATION -lt $MAX_ITERATIONS ]; do
    ITERATION=$((ITERATION + 1))
    
    echo -e "\n${GREEN}=== Running implementation iteration $ITERATION ===${NC}"
    echo -e "${BLUE}--- Claude is implementing (capturing full output)... ---${NC}\n"
    
    # Create temporary file for full output
    TEMP_OUTPUT=".claude-implementation-output-$$.tmp"
    
    # Run Claude with verbose flag to capture implementation process
    cat prompt.md | claude -p --dangerously-skip-permissions 2>&1 | tee "$TEMP_OUTPUT"
    
    echo -e "\n${MAGENTA}--- End of Claude's implementation ---${NC}"
    
    # Check if implementation is complete by looking for completion markers
    if grep -q "Implementation complete\|All components implemented\|No more implementation tasks" "$TEMP_OUTPUT" 2>/dev/null; then
        echo -e "\n${GREEN}✅ Implementation complete!${NC}"
        echo -e "${GREEN}Total iterations: $ITERATION${NC}"
        rm -f "$TEMP_OUTPUT"
        break
    fi
    
    # Check IMPLEMENTATION_PLAN.md for uncompleted tasks
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
    git status --short
    
    # Show recent commits
    echo -e "\n${YELLOW}Recent commits:${NC}"
    git log --oneline -5
    
    # Show implementation progress
    echo -e "\n${YELLOW}Implementation progress:${NC}"
    if [ -f "IMPLEMENTATION_PLAN.md" ] && [ "$(cat IMPLEMENTATION_PLAN.md)" != "Nothing here yet" ]; then
        echo -e "${CYAN}Completed items:${NC}"
        grep -E "^\- \[x\]" IMPLEMENTATION_PLAN.md 2>/dev/null | head -10 || echo "None yet"
        
        echo -e "\n${CYAN}Remaining items:${NC}"
        grep -E "^\- \[ \]" IMPLEMENTATION_PLAN.md 2>/dev/null | head -10 || echo "None"
    else
        echo -e "${CYAN}Implementation plan not yet created${NC}"
    fi
    
    # Show which files were created/modified
    echo -e "\n${YELLOW}Latest files created/modified:${NC}"
    find src tests -type f -name "*.py" 2>/dev/null | head -10 || echo "No Python files yet"
    
    # Check if tests exist and their status
    if [ -d "tests" ]; then
        echo -e "\n${YELLOW}Test status:${NC}"
        if command -v pytest &> /dev/null; then
            pytest --tb=short --no-header -q 2>/dev/null || echo "Tests not passing yet"
        else
            echo "pytest not installed yet"
        fi
    fi
    
    # Cleanup temp file
    rm -f "$TEMP_OUTPUT"
    
    # Pause for review unless --letitrip is set
    if [ "$LETITRIP" = false ]; then
        echo -e "\n${CYAN}Press Enter to continue to next iteration, or Ctrl+C to stop...${NC}"
        read -r
    else
        echo -e "\n${CYAN}Continuing automatically in 2 seconds...${NC}"
        sleep 2
    fi
done

if [ $ITERATION -eq $MAX_ITERATIONS ]; then
    echo -e "\n${RED}⚠️  Reached maximum iterations ($MAX_ITERATIONS). Stopping to prevent infinite loop.${NC}"
fi

echo -e "\n${GREEN}=== Implementation loop finished ===${NC}"
echo -e "${YELLOW}Summary:${NC}"
echo -e "  ${GREEN}✓${NC} Total iterations: $ITERATION"
echo -e "  ${GREEN}✓${NC} Python files created: $(find src tests -name "*.py" 2>/dev/null | wc -l | tr -d ' ')"
echo -e "  ${GREEN}✓${NC} Implementation items: $(grep -E "^\- \[x\]" IMPLEMENTATION_PLAN.md 2>/dev/null | wc -l | tr -d ' ') completed"

echo -e "\n${YELLOW}To review:${NC}"
echo -e "  ${CYAN}Implementation plan:${NC} cat IMPLEMENTATION_PLAN.md"
echo -e "  ${CYAN}Source code:${NC} find src -name '*.py' -type f"
echo -e "  ${CYAN}Tests:${NC} find tests -name '*.py' -type f"
echo -e "  ${CYAN}Git history:${NC} git log --oneline"