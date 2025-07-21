# Model Configuration Guide

## Overview

The AI Co-Scientist supports flexible model configuration, allowing you to:
- Set a default model for all agents
- Override models for specific agents
- Use any model available through Argo Gateway

## Available Models

- `gpto3` - OpenAI o3 (advanced reasoning, default)
- `gpt4o` - OpenAI GPT-4 (strong general capability)
- `gpt35` - OpenAI GPT-3.5 (fast and economical)
- `claudeopus4` - Claude Opus 4 (creative and thorough)
- `claudesonnet4` - Claude Sonnet 4 (balanced performance)
- `gemini25pro` - Google Gemini 2.5 Pro (multimodal, may have availability issues)

## Configuration

### Default Model

Set the default model for all agents:

```bash
export DEFAULT_MODEL=gpto3  # Now using o3 for better reasoning
```

### Per-Agent Overrides

Override models for specific agents:

```bash
# Supervisor agent uses GPT-4 for better orchestration
export SUPERVISOR_MODEL=gpt4o

# Generation agent uses Claude for creativity
export GENERATION_MODEL=claudeopus4

# Reflection agent uses GPT-4 for thorough analysis
export REFLECTION_MODEL=gpt4o

# Other agents available:
# RANKING_MODEL, EVOLUTION_MODEL, PROXIMITY_MODEL, META_REVIEW_MODEL
```

## Starting the System

1. **Ensure Argo proxy is running**:
```bash
./scripts/manage-argo-proxy.sh start
```

2. **Check proxy status**:
```bash
./scripts/manage-argo-proxy.sh status
```

3. **Test connectivity**:
```bash
./scripts/manage-argo-proxy.sh test
```

## Example Configurations

### Default Configuration (o3 for reasoning)
```bash
export DEFAULT_MODEL=gpto3  # Advanced reasoning model
```

### Hybrid Configuration
```bash
export DEFAULT_MODEL=gpt35              # Fast default
export SUPERVISOR_MODEL=gpt4o           # Smart orchestration
export GENERATION_MODEL=claudeopus4     # Creative hypotheses
export REFLECTION_MODEL=gpt4o           # Thorough evaluation
```

### Testing Configuration
```bash
export DEFAULT_MODEL=gpt35              # Economical for testing
```

## Checking Configuration

View current model assignments:

```python
from src.llm.baml_integration import print_agent_configuration
print_agent_configuration()
```

Output example:
```
Default model: gemini25pro

Agent-specific models:
  supervisor   -> gpt4o          (BAML: ArgoGPT4o) [override]
  generation   -> claudeopus4    (BAML: ArgoClaudeOpus4) [override]
  reflection   -> gemini25pro    (BAML: ArgoGemini25Pro)
  ranking      -> gemini25pro    (BAML: ArgoGemini25Pro)
  evolution    -> gemini25pro    (BAML: ArgoGemini25Pro)
  proximity    -> gemini25pro    (BAML: ArgoGemini25Pro)
  meta_review  -> gemini25pro    (BAML: ArgoGemini25Pro)
```

## Important Notes

1. **VPN Required**: You must be connected to Argonne VPN for Argo Gateway access
2. **No API Keys**: Argo uses your username (set during proxy setup)
3. **Proxy Must Run**: The argo-proxy must be running at http://localhost:8000
4. **Model Availability**: Not all models may respond to all queries (especially Gemini)
5. **Reasoning Model**: GPT-o3 is optimized for step-by-step reasoning and verification tasks