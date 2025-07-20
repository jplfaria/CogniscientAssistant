#!/bin/bash

# Script to view implementation loop logs

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
MAGENTA='\033[0;35m'
NC='\033[0m'

echo -e "${GREEN}=== Implementation Loop Logs ===${NC}\n"

# Check if logs directory exists
if [ ! -d ".implementation_logs" ]; then
    echo -e "${RED}No logs found. Run the implementation loop first.${NC}"
    exit 1
fi

# Function to list all logs
list_logs() {
    echo -e "${YELLOW}Available logs:${NC}"
    ls -la .implementation_logs/iteration_*.log 2>/dev/null | nl -w2 -s'. '
    echo ""
}

# Function to view latest success/failure
view_latest() {
    local type=$1
    if [ -f ".implementation_logs/latest_${type}.log" ]; then
        echo -e "${CYAN}=== Latest ${type} log ===${NC}"
        less ".implementation_logs/latest_${type}.log"
    else
        echo -e "${RED}No ${type} logs found yet.${NC}"
    fi
}

# Function to view specific log
view_log() {
    local log_number=$1
    local log_file=$(ls .implementation_logs/iteration_*.log 2>/dev/null | sed -n "${log_number}p")
    
    if [ -n "$log_file" ]; then
        echo -e "${CYAN}=== Viewing: $(basename "$log_file") ===${NC}"
        less "$log_file"
    else
        echo -e "${RED}Invalid log number.${NC}"
    fi
}

# Function to view failures only
view_failures() {
    echo -e "${YELLOW}Searching for test failures in logs...${NC}\n"
    
    for log in .implementation_logs/iteration_*_failed_*.log; do
        if [ -f "$log" ]; then
            echo -e "${RED}=== $(basename "$log") ===${NC}"
            grep -A5 -B5 "FAILED\|ERROR\|Test Failures" "$log" | head -20
            echo -e "${CYAN}---${NC}\n"
        fi
    done
}

# Main menu
if [ "$1" = "latest" ]; then
    view_latest "success"
elif [ "$1" = "failed" ]; then
    view_latest "failed"
elif [ "$1" = "failures" ]; then
    view_failures
elif [ "$1" = "list" ]; then
    list_logs
elif [[ "$1" =~ ^[0-9]+$ ]]; then
    view_log "$1"
else
    echo -e "${CYAN}Usage:${NC}"
    echo "  ./view-loop-logs.sh           - Interactive menu"
    echo "  ./view-loop-logs.sh latest    - View latest successful log"
    echo "  ./view-loop-logs.sh failed    - View latest failed log"
    echo "  ./view-loop-logs.sh failures  - View all test failures"
    echo "  ./view-loop-logs.sh list      - List all logs"
    echo "  ./view-loop-logs.sh <number>  - View specific log by number"
    echo ""
    
    # Interactive menu
    echo -e "${YELLOW}Choose an option:${NC}"
    echo "1. View latest successful log"
    echo "2. View latest failed log"
    echo "3. View all test failures"
    echo "4. List all logs"
    echo "5. View specific log"
    echo "0. Exit"
    
    read -p "Enter choice: " choice
    
    case $choice in
        1) view_latest "success" ;;
        2) view_latest "failed" ;;
        3) view_failures ;;
        4) list_logs ;;
        5) 
            list_logs
            read -p "Enter log number: " num
            view_log "$num"
            ;;
        0) exit 0 ;;
        *) echo -e "${RED}Invalid choice${NC}" ;;
    esac
fi