#!/bin/bash
# Startup script for Argo Proxy
# This script starts the Argo proxy server with proper configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Argo Proxy...${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure your settings."
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Validate required environment variables
if [ -z "$ARGO_USER" ]; then
    echo -e "${RED}Error: ARGO_USER not set in .env file!${NC}"
    echo "Please set your Argo username in the .env file."
    exit 1
fi

# Set default values if not provided
ARGO_PROXY_HOST=${ARGO_PROXY_HOST:-127.0.0.1}
ARGO_PROXY_PORT=${ARGO_PROXY_PORT:-8000}

# Update configuration with username
python -c "
import yaml
import os

config = {
    'verbose': True,
    'real_stream': True,
    'username': os.environ.get('ARGO_USER'),
    'host': os.environ.get('ARGO_PROXY_HOST', '127.0.0.1'),
    'port': int(os.environ.get('ARGO_PROXY_PORT', '8000')),
    'base_url': 'https://argo.kube-system.svc.cluster.local/api/v1'
}

with open('argo-config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Host: $ARGO_PROXY_HOST"
echo "  Port: $ARGO_PROXY_PORT"
echo "  User: $ARGO_USER"
echo ""

# Start the proxy server
echo -e "${GREEN}Starting proxy server...${NC}"
echo "Access the proxy at: http://${ARGO_PROXY_HOST}:${ARGO_PROXY_PORT}/v1"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run argo-proxy with the configuration
exec argo-proxy argo-config.yaml --host "$ARGO_PROXY_HOST" --port "$ARGO_PROXY_PORT"