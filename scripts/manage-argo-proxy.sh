#!/bin/bash
# Argo proxy service management script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$HOME/.argoproxy/argo-proxy.pid"
LOG_FILE="$HOME/.argoproxy/argo-proxy.log"

# Ensure config exists
if [ ! -f "$HOME/.argoproxy/config.yaml" ]; then
    echo "❌ No configuration found. Running setup..."
    "$SCRIPT_DIR/setup-argo-proxy.sh"
fi

case "$1" in
    start)
        echo "Starting Argo proxy..."
        
        # Check if already running
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "✅ Argo proxy is already running (PID: $PID)"
                exit 0
            fi
        fi
        
        # Start proxy in background
        nohup argo-proxy > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        
        # Wait for it to be ready
        echo -n "Waiting for proxy to start..."
        for i in {1..30}; do
            if curl -s http://localhost:8000/health > /dev/null 2>&1; then
                echo " ✅"
                echo "Argo proxy started successfully (PID: $(cat "$PID_FILE"))"
                exit 0
            fi
            echo -n "."
            sleep 1
        done
        
        echo " ❌"
        echo "Failed to start Argo proxy. Check logs at: $LOG_FILE"
        exit 1
        ;;
        
    stop)
        echo "Stopping Argo proxy..."
        
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                kill "$PID"
                rm -f "$PID_FILE"
                echo "✅ Argo proxy stopped"
            else
                echo "⚠️  Argo proxy was not running"
                rm -f "$PID_FILE"
            fi
        else
            echo "⚠️  No PID file found"
        fi
        ;;
        
    restart)
        "$0" stop
        sleep 2
        "$0" start
        ;;
        
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "✅ Argo proxy is running (PID: $PID)"
                echo "   Base URL: http://localhost:8000/v1"
                echo "   Log file: $LOG_FILE"
                
                # Test connectivity
                if curl -s http://localhost:8000/health > /dev/null 2>&1; then
                    echo "   Health check: ✅ Healthy"
                else
                    echo "   Health check: ❌ Not responding"
                fi
            else
                echo "❌ Argo proxy is not running (stale PID file)"
            fi
        else
            echo "❌ Argo proxy is not running"
        fi
        ;;
        
    logs)
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE"
        else
            echo "No log file found"
        fi
        ;;
        
    test)
        echo "Testing Argo proxy connection..."
        
        # Check if running
        if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "❌ Argo proxy is not running. Start it with: $0 start"
            exit 1
        fi
        
        # Test with a simple request
        echo "Testing with GPT-3.5..."
        curl -s -X POST http://localhost:8000/v1/chat/completions \
            -H "Content-Type: application/json" \
            -d '{
                "model": "gpt35",
                "messages": [{"role": "user", "content": "Say hello in 5 words or less"}],
                "max_tokens": 50
            }' | jq -r '.choices[0].message.content' || echo "❌ Test failed"
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|test}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the Argo proxy in background"
        echo "  stop    - Stop the Argo proxy"
        echo "  restart - Restart the Argo proxy"
        echo "  status  - Check if proxy is running"
        echo "  logs    - Tail the proxy logs"
        echo "  test    - Test proxy connectivity"
        exit 1
        ;;
esac