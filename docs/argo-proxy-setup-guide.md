# Argo Proxy Setup Guide - Two Approaches

This guide provides two working solutions for integrating Argo with BAML:

1. **Fixed Argo Proxy** - The official tool with our bug fix
2. **Custom Proxy** - A reliable alternative based on CONCORDIA's approach

## Quick Start

```bash
# Switch to custom proxy (recommended for reliability)
./scripts/manage-argo-proxy.py switch custom

# Or use the fixed official proxy
./scripts/manage-argo-proxy.py switch fixed

# Check status
./scripts/manage-argo-proxy.py status

# Test the connection
./scripts/manage-argo-proxy.py test
```

## Approach 1: Fixed Argo Proxy

### What It Is
- The official `argo-proxy` tool with a fix for the configuration bug
- Maintains compatibility with the official tool
- Good for reporting the bug to developers

### How to Use
```bash
# Start the fixed proxy
./scripts/argo-proxy-fixed.py

# Or use the manager
./scripts/manage-argo-proxy.py start fixed
```

### BAML Configuration
```baml
client<llm> ArgoProxyFixed {
  provider openai-generic
  options {
    base_url "http://localhost:8000/v1"
    model "gpt4o"
    api_key ""
  }
}
```

### Pros
- Uses official tool (with fix)
- Demonstrates the bug clearly
- Minimal changes to existing code

### Cons
- Still depends on buggy package
- May break with package updates

## Approach 2: Custom Proxy (Recommended)

### What It Is
- A custom FastAPI server that translates between OpenAI and Argo formats
- Based on CONCORDIA's proven approach
- More reliable and maintainable

### How to Use
```bash
# Start the custom proxy
./scripts/custom-argo-proxy.py

# Or use the manager
./scripts/manage-argo-proxy.py start custom
```

### BAML Configuration
```baml
client<llm> ArgoCustomProxy {
  provider openai-generic
  options {
    base_url "http://localhost:8000/v1"
    model "gpt4o"
    api_key ""
  }
}
```

### Pros
- Complete control over behavior
- No dependency on buggy packages
- Better error handling and logging
- Supports streaming

### Cons
- Another service to maintain
- Duplicates some functionality

## Using the Management Script

The `manage-argo-proxy.py` script makes it easy to switch between approaches:

```bash
# Show status of all proxies
./scripts/manage-argo-proxy.py status

# Switch between proxies (stops one, starts the other)
./scripts/manage-argo-proxy.py switch custom
./scripts/manage-argo-proxy.py switch fixed

# Start/stop individual proxies
./scripts/manage-argo-proxy.py start custom
./scripts/manage-argo-proxy.py stop custom

# Test current configuration
./scripts/manage-argo-proxy.py test
```

## Environment Configuration

Both approaches use these environment variables:

```bash
# Required
ARGO_USER=jplfaria

# Automatically set by manage-argo-proxy.py
ARGO_PROXY_URL=http://localhost:8000/v1  # or 8000 for fixed

# Optional model defaults
DEFAULT_MODEL=gemini25pro
```

## Available Models

All approaches support these Argo models:
- `gpt4o` - OpenAI GPT-4o
- `gpt35` - OpenAI GPT-3.5 Turbo
- `claudeopus4` - Claude Opus 4
- `claudesonnet4` - Claude Sonnet 4
- `gemini25pro` - Gemini 2.5 Pro
- `gemini25flash` - Gemini 2.5 Flash

## Testing

Test any configuration with:

```bash
# Using the manager
./scripts/manage-argo-proxy.py test

# Or directly
python test_argo_direct.py
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000  # or :8000

# Kill the process if needed
kill -9 <PID>
```

### Proxy Won't Start
1. Check you're on the VPN
2. Verify ARGO_USER is set
3. Check logs in the terminal

### BAML Can't Connect
1. Verify proxy is running: `./scripts/manage-argo-proxy.py status`
2. Check ARGO_PROXY_URL in .env matches the running proxy
3. Restart BAML/your application after changing proxies

## For Developers

To report the bug in argo-proxy:
1. Share `docs/argo-proxy-bug-report.md`
2. Point to the working fix in `scripts/argo-proxy-fixed.py`
3. Suggest the fix be applied to `prepare_app()` in the package

## Next Steps

1. Choose your preferred approach (we recommend custom for reliability)
2. Update your BAML clients to use the appropriate configuration
3. Run `./scripts/manage-argo-proxy.py switch <choice>` to start

Both solutions are production-ready and handle all Argo models correctly!