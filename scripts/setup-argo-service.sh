#!/bin/bash
# Setup script to run Argo proxy as a persistent background service

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Setting up Argo Proxy as a background service...${NC}"

# Create a launch agent plist for macOS
PLIST_FILE="$HOME/Library/LaunchAgents/com.aicoscientist.argo-proxy.plist"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Create the plist file
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aicoscientist.argo-proxy</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which argo-proxy)</string>
        <string>$PROJECT_DIR/argo-config.yaml</string>
        <string>--host</string>
        <string>127.0.0.1</string>
        <string>--port</string>
        <string>8000</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/argo-proxy.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/argo-proxy.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>$(echo $PATH)</string>
    </dict>
</dict>
</plist>
EOF

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

echo -e "${YELLOW}Created launch agent at: $PLIST_FILE${NC}"

# Load the service
echo -e "${GREEN}Loading Argo proxy service...${NC}"
launchctl load "$PLIST_FILE" 2>/dev/null || true

# Start the service
echo -e "${GREEN}Starting Argo proxy service...${NC}"
launchctl start com.aicoscientist.argo-proxy

# Check status
sleep 2
if launchctl list | grep -q "com.aicoscientist.argo-proxy"; then
    echo -e "${GREEN}✅ Argo proxy service is running!${NC}"
    echo -e "${YELLOW}The proxy will now start automatically when you log in.${NC}"
    echo ""
    echo -e "${YELLOW}Useful commands:${NC}"
    echo "  Check status:  launchctl list | grep argo-proxy"
    echo "  View logs:     tail -f $PROJECT_DIR/logs/argo-proxy.log"
    echo "  Stop service:  launchctl stop com.aicoscientist.argo-proxy"
    echo "  Disable:       launchctl unload $PLIST_FILE"
    echo ""
    echo -e "${GREEN}The Argo proxy is now running at: http://localhost:8000/v1${NC}"
else
    echo -e "${RED}❌ Failed to start Argo proxy service${NC}"
    echo "Check the logs at: $PROJECT_DIR/logs/argo-proxy.error.log"
fi