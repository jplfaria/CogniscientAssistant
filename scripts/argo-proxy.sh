#!/bin/bash
# Unified Argo Proxy Management Script
# Supports start, stop, status, and restart operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONFIG_FILE="argo-config.yaml"
PID_FILE="/tmp/argo-proxy.pid"
LOG_FILE="/tmp/argo-proxy.log"

# Default configuration
DEFAULT_HOST="127.0.0.1"
DEFAULT_PORT="8000"
DEFAULT_USER="jplfaria"

# Functions
show_help() {
    echo "Usage: $0 {start|stop|restart|status|setup}"
    echo ""
    echo "Commands:"
    echo "  start    - Start the Argo proxy server"
    echo "  stop     - Stop the Argo proxy server"
    echo "  restart  - Restart the Argo proxy server"
    echo "  status   - Check if the proxy is running"
    echo "  setup    - Create initial configuration"
}

create_config() {
    echo -e "${YELLOW}Creating Argo configuration...${NC}"
    
    # Get username from environment or use default
    USERNAME=${ARGO_USER:-$DEFAULT_USER}
    
    cat > "$CONFIG_FILE" << EOF
argo_embedding_url: https://apps.inside.anl.gov/argoapi/api/v1/resource/embed/
argo_stream_url: https://apps-dev.inside.anl.gov/argoapi/api/v1/resource/streamchat/
argo_url: https://apps-dev.inside.anl.gov/argoapi/api/v1/resource/chat/
host: $DEFAULT_HOST
port: $DEFAULT_PORT
user: $USERNAME
verbose: true
EOF
    
    echo -e "${GREEN}Configuration created at $CONFIG_FILE${NC}"
}

check_prereqs() {
    # Check if argo-proxy is installed
    if ! command -v argo-proxy &> /dev/null; then
        echo -e "${RED}Error: argo-proxy not installed!${NC}"
        echo "Install with: pip install argo-proxy"
        exit 1
    fi
    
    # Check if config exists
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${YELLOW}Configuration file not found.${NC}"
        create_config
    fi
    
    # Check VPN connection (simple ping test)
    if ! ping -c 1 -W 1 apps.inside.anl.gov &> /dev/null; then
        echo -e "${YELLOW}Warning: Cannot reach Argo servers. Are you on the VPN?${NC}"
    fi
}

start_proxy() {
    check_prereqs
    
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}Argo proxy is already running (PID: $PID)${NC}"
            return 0
        fi
    fi
    
    echo -e "${GREEN}Starting Argo proxy...${NC}"
    
    # Start in background
    nohup argo-proxy "$CONFIG_FILE" > "$LOG_FILE" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    
    # Wait for startup
    sleep 2
    
    # Check if started successfully
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}Argo proxy started successfully (PID: $PID)${NC}"
        echo "Access at: http://$DEFAULT_HOST:$DEFAULT_PORT/v1"
        echo "Logs at: $LOG_FILE"
    else
        echo -e "${RED}Failed to start Argo proxy${NC}"
        echo "Check logs at: $LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi
}

stop_proxy() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${YELLOW}Argo proxy is not running (no PID file)${NC}"
        return 0
    fi
    
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}Stopping Argo proxy (PID: $PID)...${NC}"
        kill "$PID"
        sleep 1
        
        # Force kill if needed
        if ps -p "$PID" > /dev/null 2>&1; then
            kill -9 "$PID"
        fi
        
        echo -e "${GREEN}Argo proxy stopped${NC}"
    else
        echo -e "${YELLOW}Argo proxy not running (stale PID file)${NC}"
    fi
    
    rm -f "$PID_FILE"
}

check_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${GREEN}Argo proxy is running (PID: $PID)${NC}"
            
            # Test connectivity
            if curl -s http://$DEFAULT_HOST:$DEFAULT_PORT/health > /dev/null 2>&1; then
                echo -e "${GREEN}Health check: OK${NC}"
            else
                echo -e "${YELLOW}Health check: Failed${NC}"
            fi
        else
            echo -e "${RED}Argo proxy is not running (stale PID file)${NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${YELLOW}Argo proxy is not running${NC}"
    fi
}

# Main script
case "$1" in
    start)
        start_proxy
        ;;
    stop)
        stop_proxy
        ;;
    restart)
        stop_proxy
        sleep 1
        start_proxy
        ;;
    status)
        check_status
        ;;
    setup)
        create_config
        ;;
    *)
        show_help
        exit 1
        ;;
esac