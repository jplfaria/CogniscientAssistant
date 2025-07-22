# Argo Gateway Complete Guide

This guide consolidates all documentation for setting up and using the Argo Gateway with the AI Co-Scientist system.

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Running the Proxy](#running-the-proxy)
6. [Available Models](#available-models)
7. [BAML Integration](#baml-integration)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)
10. [Known Issues](#known-issues)
11. [Security Best Practices](#security-best-practices)

## Overview

The Argo Gateway is Argonne National Laboratory's unified interface for accessing multiple LLM providers (OpenAI, Anthropic, Google) through a single API endpoint. It's available free for users on the Argonne VPN and provides a consistent interface across different model providers.

### Key Benefits
- Single API endpoint for multiple LLM providers
- Free access for Argonne VPN users
- Consistent OpenAI-compatible format
- Built-in model switching capabilities
- No need for individual API keys

## Prerequisites

1. **Argonne VPN Access**: You must be connected to the Argonne VPN
2. **Python 3.11+**: Required for the AI Co-Scientist system
3. **argo-proxy**: Install with `pip install argo-proxy`
4. **BAML**: Install with `pip install baml-py==0.202.1`

## Installation & Setup

### 1. Install argo-proxy

```bash
pip install argo-proxy
```

### 2. Create Configuration File

The argo-proxy requires a configuration file at `argo-config.yaml`:

```yaml
argo_embedding_url: https://apps.inside.anl.gov/argoapi/api/v1/resource/embed/
argo_stream_url: https://apps-dev.inside.anl.gov/argoapi/api/v1/resource/streamchat/
argo_url: https://apps-dev.inside.anl.gov/argoapi/api/v1/resource/chat/
host: 127.0.0.1
port: 8000
user: YOUR_USERNAME  # Replace with your Argonne username
verbose: true
```

### 3. Set Environment Variables

Create or update your `.env` file:

```bash
# Default model configuration
DEFAULT_MODEL=gpto3  # OpenAI o3 reasoning model

# BAML configuration
BAML_BASE_URL=http://localhost:8000/v1
BAML_API_KEY=dummy-key-for-argo
BAML_MODEL=gpto3

# Argo proxy URL
ARGO_PROXY_URL=http://localhost:8000/v1

# Optional per-agent model overrides
# GENERATION_MODEL=gpto3      # Deep reasoning for hypotheses
# REFLECTION_MODEL=claudeopus4 # Nuanced analysis for reviews
# RANKING_MODEL=gpt4o         # Fast comparisons for tournaments
```

## Configuration

### Model Names Mapping

Argo uses specific model identifiers that differ from standard names:

| Provider | Argo Model ID | Standard Name | Description |
|----------|---------------|---------------|-------------|
| OpenAI | gpto3 | GPT-o3 | Reasoning model with step-by-step thinking |
| OpenAI | gpt4o | GPT-4o | Fast, general purpose |
| OpenAI | gpt35 | GPT-3.5-turbo | Legacy, cost-effective |
| Anthropic | claudeopus4 | Claude 3 Opus | Nuanced analysis |
| Anthropic | claudesonnet4 | Claude 3 Sonnet | Balanced performance |
| Google | gemini25pro | Gemini 2.5 Pro | Multi-modal capable |

### Per-Agent Model Configuration

The system supports configuring different models for different agents:

```python
# In src/config/model_config.py
DEFAULT_MODEL = "gpto3"  # Default for all agents

# Optional overrides via environment variables:
# SUPERVISOR_MODEL=gpt4o
# GENERATION_MODEL=gpto3
# REFLECTION_MODEL=claudeopus4
```

## Running the Proxy

### Simple Start

```bash
# Start the proxy
python scripts/start-argo-proxy.sh

# Or run directly
argo-proxy --config argo-config.yaml
```

### As a Background Service

```bash
# Start in background
nohup argo-proxy --config argo-config.yaml > argo-proxy.log 2>&1 &

# Check if running
ps aux | grep argo-proxy

# View logs
tail -f argo-proxy.log
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Available Models

Test available models with:

```bash
python scripts/test-argo-proxy.py
```

Current models (as of January 2025):
- **OpenAI**: gpto3, gpt4o, gpt35
- **Anthropic**: claudeopus4, claudesonnet4  
- **Google**: gemini25pro

## BAML Integration

### BAML Client Configuration

The system uses BAML for type-safe LLM interactions. Key files:

1. **baml_src/clients.baml** - Defines LLM clients
2. **baml_src/functions.baml** - Defines LLM functions with JSON prompts
3. **baml_src/models.baml** - Defines data models

### ProductionClient

The main client used throughout the system:

```python
client<llm> ProductionClient {
  provider openai
  options {
    model env.DEFAULT_MODEL
    base_url "http://localhost:8000/v1"  // Argo proxy
    temperature 0.7
    max_tokens 4000
    timeout_seconds 60
  }
}
```

### Important: JSON Responses

All BAML functions must explicitly request JSON format in their prompts:

```python
prompt #"
    [Your prompt instructions here]
    
    Respond in valid JSON format matching the schema:
    {
      "field1": "description",
      "field2": ["array", "values"],
      ...
    }
"#
```

## Testing

### 1. Basic Connectivity Test

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt35",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 50
  }'
```

### 2. Real LLM Integration Tests

```bash
# Run all real LLM tests
./scripts/run-real-llm-tests.sh

# Run specific phase tests
pytest tests/integration/test_phase7_baml_real.py -v --real-llm
pytest tests/integration/test_phase8_argo_real.py -v --real-llm
```

### 3. Model Comparison Test

```bash
python scripts/compare-hypothesis-quality.py
```

## Troubleshooting

### Common Issues

1. **"AttributeError: 'NoneType' object has no attribute 'verbose'"**
   - **Cause**: Missing configuration file
   - **Fix**: Create `argo-config.yaml` with the template above

2. **"Connection refused" errors**
   - **Cause**: Proxy not running
   - **Fix**: Start proxy with `./scripts/start-argo-proxy.sh`

3. **"Model not found" errors**
   - **Cause**: Using wrong model identifier
   - **Fix**: Use Argo model IDs (e.g., "gpt4o" not "gpt-4o")

4. **No responses from Gemini models**
   - **Known Issue**: Gemini models may have availability issues
   - **Fix**: Use alternative models (gpt4o, claudeopus4)

5. **BAML parsing errors**
   - **Cause**: LLM returning narrative text instead of JSON
   - **Fix**: Ensure prompts explicitly request JSON format

### Debug Mode

Enable verbose logging:

```yaml
# In argo-config.yaml
verbose: true
```

Check proxy logs:
```bash
tail -f argo-proxy.log
```

## Known Issues

### argo-proxy v2.7.6 Configuration Bug

The argo-proxy has a bug where it doesn't handle missing configuration files gracefully:

**Error**: `AttributeError: 'NoneType' object has no attribute 'verbose'`

**Root Cause**: The `load_config()` function returns `None` when the config file doesn't exist, but the code tries to access attributes on it.

**Workaround**: Always ensure `argo-config.yaml` exists before starting the proxy.

**Note**: Despite this bug, the proxy works excellently once properly configured.

## Security Best Practices

1. **Never commit credentials**:
   - Don't commit `argo-config.yaml` with your username
   - Use `.env` for sensitive configuration
   - Add sensitive files to `.gitignore`

2. **VPN Required**:
   - Always connect to Argonne VPN before using Argo
   - The gateway will not respond without VPN access

3. **Local Proxy Only**:
   - Keep argo-proxy bound to localhost (127.0.0.1)
   - Don't expose to public networks

4. **Model Selection**:
   - Use GPT-o3 for sensitive reasoning tasks
   - Be aware that all requests go through Argonne's infrastructure

## Recommended Model Usage

Based on extensive testing:

- **GPT-4o** (gpt4o): **RECOMMENDED DEFAULT** - Fast (7s), reliable, handles all BAML formats
- **GPT-o3** (gpto3): Best for complex reasoning but very slow (60s+), use selectively
- **Claude Opus 4** (claudeopus4): Excellent quality but incompatible with BAML's content format
- **GPT-3.5** (gpt35): Reliable fallback, fastest responses

### Model Compatibility Issues

**Important**: BAML sends message content in OpenAI's structured format:
```json
"content": [{"type": "text", "text": "actual content"}]
```

This format works with all OpenAI models but causes errors with Claude models through argo-proxy:
- Error: "expected string or bytes-like object, got 'dict'"
- Claude models only work with simple string content through argo-proxy

### Performance Comparison

| Model | Response Time | BAML Compatible | Notes |
|-------|--------------|-----------------|-------|
| gpt4o | ~7 seconds | ✅ Yes | Best overall choice |
| gpto3 | ~60+ seconds | ✅ Yes | Too slow for regular use |
| claudeopus4 | ~3 seconds | ❌ No | Content format issue |
| gpt35 | ~2 seconds | ✅ Yes | Good for simple tasks |

### Edge Cases and Known Issues

1. **O-series models with certain prompts**: As discovered in conversation with Argo developers, some specific prompts may fail with o-series models when using `max_completion_tokens`. The issue is intermittent and prompt-dependent.

2. **BAML content format**: BAML uses OpenAI's structured content format which is not compatible with Claude models through argo-proxy. This is a limitation of the current argo-proxy implementation.

## Quick Reference

```bash
# Start proxy
./scripts/start-argo-proxy.sh

# Test connectivity
curl http://localhost:8000/health

# Run real LLM tests
./scripts/run-real-llm-tests.sh

# Check which models work
python scripts/test-argo-proxy.py
```

## Support

For issues specific to:
- **Argo Gateway**: Contact Argonne IT support
- **AI Co-Scientist**: Check project documentation
- **BAML Integration**: See BAML_AND_MODEL_INTEGRATION_LEARNINGS.md