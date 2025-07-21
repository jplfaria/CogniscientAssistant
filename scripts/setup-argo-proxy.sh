#!/bin/bash
# Simple setup script for argo-proxy

set -e

echo "Setting up Argo Proxy..."

# Ensure config directory exists
CONFIG_DIR="$HOME/.argoproxy"
CONFIG_FILE="$CONFIG_DIR/config.yaml"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating Argo proxy configuration..."
    mkdir -p "$CONFIG_DIR"
    
    # Get username from environment or prompt
    ARGO_USER=${ARGO_USER:-$(whoami)}
    
    cat > "$CONFIG_FILE" << EOF
argo_url: "https://apps-dev.inside.anl.gov/argoapi/api/v1/resource/chat/"
argo_stream_url: "https://apps-dev.inside.anl.gov/argoapi/api/v1/resource/streamchat/"
argo_embedding_url: "https://apps.inside.anl.gov/argoapi/api/v1/resource/embed/"
user: "$ARGO_USER"
verbose: true
host: "127.0.0.1"
port: 8000
EOF
    
    echo "✅ Configuration created at: $CONFIG_FILE"
else
    echo "✅ Configuration already exists at: $CONFIG_FILE"
fi

echo ""
echo "To start the proxy, run:"
echo "  argo-proxy"
echo ""
echo "Or run in background:"
echo "  nohup argo-proxy > argo-proxy.log 2>&1 &"