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

echo -e "${GREEN}=== AI Co-Scientist Spec Creation Loop ===${NC}"
if [ "$LETITRIP" = true ]; then
    echo -e "${YELLOW}Running in continuous mode (--letitrip). Will run until all specs are complete.${NC}"
else
    echo -e "${YELLOW}This will run until all specs are complete, pausing between each for review.${NC}"
fi
echo -e "${CYAN}Full thought process will be captured and displayed.${NC}"
echo -e "${YELLOW}Press Ctrl+C at any time to stop.${NC}\n"

# Track iterations
ITERATION=0
MAX_ITERATIONS=50  # Safety limit

while [ $ITERATION -lt $MAX_ITERATIONS ]; do
    ITERATION=$((ITERATION + 1))
    
    echo -e "\n${GREEN}=== Running spec creation iteration $ITERATION ===${NC}"
    echo -e "${BLUE}--- Claude is thinking (capturing full output)... ---${NC}\n"
    
    # Create temporary file for full output
    TEMP_OUTPUT=".claude-full-output-$$.tmp"
    
    # Run Claude with verbose flag to capture thinking process
    cat specs-prompt.md | claude -p --dangerously-skip-permissions 2>&1 | tee "$TEMP_OUTPUT"
    
    echo -e "\n${MAGENTA}--- End of Claude's response ---${NC}"
    
    # Check if all tasks are complete by looking for unchecked items
    UNCHECKED_COUNT=$(grep -E "^\- \[ \]" SPECS_PLAN.md | wc -l | tr -d ' ')
    
    if [ "$UNCHECKED_COUNT" -eq 0 ]; then
        echo -e "\n${GREEN}✅ All specifications completed!${NC}"
        echo -e "${GREEN}Total iterations: $ITERATION${NC}"
        rm -f "$TEMP_OUTPUT"
        break
    fi
    
    # Check for specific completion markers in output
    if grep -q "No more specs to create\|All specs have been created\|All tasks completed" "$TEMP_OUTPUT" 2>/dev/null; then
        echo -e "\n${GREEN}✅ Claude reports all tasks completed!${NC}"
        rm -f "$TEMP_OUTPUT"
        break
    fi
    
    # Show what was created/modified
    echo -e "\n${YELLOW}Recent changes:${NC}"
    git status --short
    
    # Show recent commits
    echo -e "\n${YELLOW}Recent commits:${NC}"
    git log --oneline -5
    
    # Show ALL progress on SPECS_PLAN.md (not just first 10)
    echo -e "\n${YELLOW}Complete progress on SPECS_PLAN.md:${NC}"
    echo -e "${CYAN}Completed specs:${NC}"
    grep -E "^\- \[x\]" SPECS_PLAN.md | nl -nln -w2 -s'. '
    
    echo -e "\n${CYAN}Remaining specs ($UNCHECKED_COUNT):${NC}"
    grep -E "^\- \[ \]" SPECS_PLAN.md | head -5
    if [ "$UNCHECKED_COUNT" -gt 5 ]; then
        echo -e "${CYAN}... and $((UNCHECKED_COUNT - 5)) more${NC}"
    fi
    
    # Show which spec was likely just created
    echo -e "\n${YELLOW}Latest spec file created/modified:${NC}"
    ls -t specs/*.md 2>/dev/null | head -3
    
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

echo -e "\n${GREEN}=== Spec creation loop finished ===${NC}"
echo -e "${YELLOW}Summary:${NC}"
echo -e "  ${GREEN}✓${NC} Total iterations: $ITERATION"
echo -e "  ${GREEN}✓${NC} Specs created: $(ls specs/*.md 2>/dev/null | wc -l | tr -d ' ')"
echo -e "  ${GREEN}✓${NC} Remaining tasks: $UNCHECKED_COUNT"
echo -e "\n${YELLOW}To review:${NC}"
echo -e "  ${CYAN}All changes:${NC} git status"
echo -e "  ${CYAN}All specs:${NC} ls -la specs/"
echo -e "  ${CYAN}Full plan:${NC} cat SPECS_PLAN.md"