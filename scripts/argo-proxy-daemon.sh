#!/bin/bash
# Simple daemon script to run Argo proxy in background

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$PROJECT_DIR/.argo-proxy.pid"

# Create logs directory
mkdir -p "$LOG_DIR"

# Function to start the proxy
start_proxy() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Argo proxy is already running (PID: $PID)"
            return 0
        fi
    fi
    
    echo "Starting Argo proxy in background..."
    
    # Use expect to handle the interactive prompt
    if command -v expect >/dev/null 2>&1; then
        expect -c "
            spawn argo-proxy $PROJECT_DIR/argo-config.yaml --host 127.0.0.1 --port 8000
            expect \"Enter your username:\"
            send \"jplfaria\r\"
            expect \"Running on\"
            interact
        " > "$LOG_DIR/argo-proxy.log" 2>&1 &
        PID=$!
    else
        # Fallback: use echo to provide username
        echo "jplfaria" | argo-proxy "$PROJECT_DIR/argo-config.yaml" --host 127.0.0.1 --port 8000 > "$LOG_DIR/argo-proxy.log" 2>&1 &
        PID=$!
    fi
    
    echo $PID > "$PID_FILE"
    sleep 3
    
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Argo proxy started successfully (PID: $PID)"
        echo "Proxy running at: http://localhost:8000/v1"
        echo "Logs: $LOG_DIR/argo-proxy.log"
    else
        echo "❌ Failed to start Argo proxy"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop the proxy
stop_proxy() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Stopping Argo proxy (PID: $PID)..."
            kill $PID
            rm -f "$PID_FILE"
            echo "✅ Argo proxy stopped"
        else
            echo "Argo proxy is not running"
            rm -f "$PID_FILE"
        fi
    else
        echo "Argo proxy is not running"
    fi
}

# Function to check status
status_proxy() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "✅ Argo proxy is running (PID: $PID)"
            echo "Proxy URL: http://localhost:8000/v1"
            return 0
        fi
    fi
    echo "❌ Argo proxy is not running"
    return 1
}

# Main command handling
case "$1" in
    start)
        start_proxy
        ;;
    stop)
        stop_proxy
        ;;
    restart)
        stop_proxy
        sleep 2
        start_proxy
        ;;
    status)
        status_proxy
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac