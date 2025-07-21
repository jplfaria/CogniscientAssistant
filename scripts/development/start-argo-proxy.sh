#!/bin/bash
# Start the argo-proxy service if not already running
# This proxy translates between Argo's API format and OpenAI's format

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if argo-proxy is installed
if ! command -v argo-proxy &> /dev/null; then
    echo -e "${RED}Error: argo-proxy is not installed${NC}"
    echo "Please install it with: pip install argo-proxy"
    exit 1
fi

# Check if proxy is already running
if pgrep -f "argo-proxy" > /dev/null; then
    echo -e "${YELLOW}argo-proxy is already running${NC}"
    echo "To check logs: tail -f ~/.argo-proxy.log"
    exit 0
fi

# Start the proxy
echo -e "${GREEN}Starting argo-proxy...${NC}"
nohup argo-proxy > ~/.argo-proxy.log 2>&1 &

# Wait a moment for startup
sleep 2

# Check if it started successfully
if pgrep -f "argo-proxy" > /dev/null; then
    echo -e "${GREEN}✓ argo-proxy started successfully on port 8000${NC}"
    echo "Logs are available at: ~/.argo-proxy.log"
    echo ""
    echo "To stop the proxy: pkill -f argo-proxy"
    echo "To check status: ps aux | grep argo-proxy"
else
    echo -e "${RED}✗ Failed to start argo-proxy${NC}"
    echo "Check the logs at: ~/.argo-proxy.log"
    exit 1
fi