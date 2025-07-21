# Argo Proxy Setup Guide

The Argo proxy translates between OpenAI API format and Argo's internal API, allowing BAML and other OpenAI-compatible libraries to work with Argo's LLM gateway.

## Prerequisites

1. Be connected to the Argonne VPN
2. Have `argo-proxy` installed (`pip install argo-proxy`)
3. Have your Argonne username ready

## Quick Setup (Recommended)

We've created a daemon script that handles the proxy setup automatically:

```bash
# Start the proxy in background
./scripts/argo-proxy-daemon.sh start

# Check if it's running
./scripts/argo-proxy-daemon.sh status

# Stop the proxy
./scripts/argo-proxy-daemon.sh stop

# Restart the proxy
./scripts/argo-proxy-daemon.sh restart
```

The proxy will run at `http://localhost:8000/v1` and logs will be saved to `logs/argo-proxy.log`.

## Manual Setup

If you prefer to run the proxy manually:

```bash
./scripts/start-argo-proxy.sh
```

When prompted for username, enter your Argonne username (e.g., `jplfaria`).

## Configuration

The proxy uses `argo-config.yaml` which is automatically updated when you first run it. The key settings are:

- **user**: Your Argonne username
- **host**: 127.0.0.1 (localhost)
- **port**: 8000
- **argo_url**: The Argo API endpoint (automatically configured)

## Environment Variables

Make sure your `.env` file contains:

```bash
ARGO_PROXY_URL=http://localhost:8000/v1
ARGO_AUTH_USER=your_username
```

## Available Models

The following models are available through Argo:

- **GPT Models**: gpt4o, gpt35, gpt4turbo
- **Claude Models**: claudeopus4, claudesonnet4
- **Gemini Models**: gemini25pro, gemini25flash

## Troubleshooting

1. **Proxy won't start**: Make sure you're on the VPN
2. **Authentication errors**: Check your username in `.env`
3. **Connection refused**: Ensure no other service is using port 8000

## Testing

To test the connection:

```bash
python test_argo_connectivity.py
```

This will query three different models with a test prompt.