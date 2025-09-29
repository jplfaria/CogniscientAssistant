# BAML Model Configuration Guide

## Overview

This guide documents the complete model configuration for the AI Co-Scientist system using BAML (Boundary AI Markup Language). It covers model definitions, parameter requirements, and configuration strategies.

## Available Models

### GPT-5 Suite (New Default)
- **gpt5** - GPT-5 (advanced reasoning, new default)
  - Best for: Complex reasoning, multi-step analysis, verification tasks
  - Parameters: `max_completion_tokens` (required), `temperature`
- **gpt5mini** - GPT-5 Mini (balanced performance)
  - Best for: General tasks, good balance of speed and capability
  - Parameters: `max_completion_tokens` (required), `temperature`
- **gpt5nano** - GPT-5 Nano (fast and economical)
  - Best for: Simple tasks, quick responses, high-volume operations
  - Parameters: `max_completion_tokens` (required), `temperature`

### OpenAI Models
- **gpto3** - OpenAI o3 (previous default, advanced reasoning)
  - Best for: Step-by-step reasoning, verification, complex logic
  - Parameters: `max_completion_tokens` (required), `temperature`
- **gpt4o** - OpenAI GPT-4
  - Best for: Strong general capability, creative tasks
  - Parameters: `max_tokens`, `temperature`
- **gpt35** - OpenAI GPT-3.5 Turbo
  - Best for: Fast responses, economical usage
  - Parameters: `max_tokens`, `temperature`

### Claude Models
- **claudeopus41** - Claude Opus 4.1 (newest)
  - Best for: Complex analysis, nuanced understanding
  - Parameters: `max_tokens`, `temperature`
- **claudeopus4** - Claude Opus 4
  - Best for: Creative generation, thorough analysis
  - Parameters: `max_tokens`, `temperature`
- **claudesonnet4** - Claude Sonnet 4
  - Best for: Balanced performance, efficient processing
  - Parameters: `max_tokens`, `temperature`

### Gemini Models
- **gemini25pro** - Google Gemini 2.5 Pro
  - Best for: Multimodal tasks (when available)
  - Parameters: `max_tokens`, `temperature`
  - Note: May have availability issues

## Parameter Requirements

### Critical Differences

**GPT-5 and o3 Models** require `max_completion_tokens`:
```baml
client<llm> ArgoGPT5 {
  provider "openai"
  options {
    model "gpt-5"
    api_key env.BAML_API_KEY
    base_url env.BAML_BASE_URL
    max_completion_tokens 4096  // REQUIRED for GPT-5/o3
    temperature 0.7
  }
}
```

**All other models** use `max_tokens`:
```baml
client<llm> ArgoGPT4o {
  provider "openai"
  options {
    model "gpt-4o"
    api_key env.BAML_API_KEY
    base_url env.BAML_BASE_URL
    max_tokens 4096  // Standard parameter
    temperature 0.7
  }
}
```

## BAML Client Configuration

### Client Registry (baml_src/clients.baml)

```baml
// GPT-5 Suite (new models)
client<llm> ArgoGPT5 {
  provider "openai"
  options {
    model "gpt-5"
    api_key env.BAML_API_KEY
    base_url env.BAML_BASE_URL
    max_completion_tokens 4096
    temperature 0.7
  }
}

client<llm> ArgoGPT5Mini {
  provider "openai"
  options {
    model "gpt-5-mini"
    api_key env.BAML_API_KEY
    base_url env.BAML_BASE_URL
    max_completion_tokens 4096
    temperature 0.7
  }
}

// Production client - uses strategy pattern
client<llm> ProductionClient {
  provider "fallback"
  options {
    strategy [
      ArgoGPT5,       // Primary (new default)
      ArgoGPT5Mini,   // First fallback
      ArgoGPT4o,      // Second fallback
      ArgoGPT35       // Final fallback
    ]
  }
}
```

## Model Mapping

### Python Configuration (src/config/model_config.py)

```python
# Model name mapping for environment variables to BAML clients
MODEL_MAPPING = {
    # GPT-5 Suite (new)
    "gpt5": "ArgoGPT5",
    "gpt5mini": "ArgoGPT5Mini",
    "gpt5nano": "ArgoGPT5Nano",

    # OpenAI Models
    "gpto3": "ArgoO3",
    "gpt4o": "ArgoGPT4o",
    "gpt35": "ArgoGPT35",

    # Claude Models
    "claudeopus41": "ArgoClaudeOpus41",
    "claudeopus4": "ArgoClaudeOpus4",
    "claudesonnet4": "ArgoClaudeSonnet4",

    # Gemini Models
    "gemini25pro": "ArgoGemini25Pro",
}

# Default model (changed from gpto3 to gpt5)
DEFAULT_MODEL = "gpt5"
```

## Environment Configuration

### Setting Models

```bash
# Set default model for all agents
export DEFAULT_MODEL=gpt5  # New default

# Override specific agents
export SUPERVISOR_MODEL=gpto3        # Use o3 for complex reasoning
export GENERATION_MODEL=claudeopus41 # Use Claude for creativity
export REFLECTION_MODEL=gpt5         # Use GPT-5 for analysis
```

### Required Environment Variables

```bash
# Argo Gateway configuration
export BAML_BASE_URL=http://localhost:8000/v1
export BAML_API_KEY=dummy-key-for-argo  # Argo uses username from proxy
```

## Adding New Models

### Step 1: Add BAML Client

In `baml_src/clients.baml`:
```baml
client<llm> ArgoNewModel {
  provider "openai"  // or "anthropic"
  options {
    model "new-model-name"
    api_key env.BAML_API_KEY
    base_url env.BAML_BASE_URL
    // Use correct parameter based on model type:
    max_completion_tokens 4096  // For GPT-5/o3 style models
    // OR
    max_tokens 4096  // For standard models
    temperature 0.7
  }
}
```

### Step 2: Update Model Mapping

In `src/config/model_config.py`:
```python
MODEL_MAPPING = {
    # ... existing models ...
    "newmodel": "ArgoNewModel",
}
```

### Step 3: Update Test Mocks

In `tests/conftest.py`, add mock for the new model:
```python
# In the appropriate mock function
if "newmodel" in model_name.lower():
    return MockResponse(content="Generated content")
```

### Step 4: Update Strategy (Optional)

If the model should be in the fallback chain, update `ProductionClient` in `baml_src/clients.baml`:
```baml
client<llm> ProductionClient {
  provider "fallback"
  options {
    strategy [
      ArgoNewModel,  // Add to strategy
      // ... other models ...
    ]
  }
}
```

## Testing Model Configuration

### Verify Configuration

```python
from src.llm.baml_integration import print_agent_configuration
print_agent_configuration()
```

### Test with Real Models

```bash
# Test specific model
DEFAULT_MODEL=gpt5 pytest tests/integration/test_phase*_real.py -v --real-llm

# Test with agent override
GENERATION_MODEL=claudeopus41 pytest tests/integration/test_phase10_generation_real.py -v --real-llm
```

### Mock Testing

```bash
# Standard tests use mocks automatically
pytest tests/ -v
```

## Troubleshooting

### Common Issues

1. **"Invalid parameter: max_completion_tokens"**
   - Model doesn't support this parameter
   - Use `max_tokens` instead

2. **"Invalid parameter: max_tokens"**
   - Model requires `max_completion_tokens` (GPT-5/o3)
   - Update client configuration

3. **Model not found**
   - Check MODEL_MAPPING in model_config.py
   - Verify BAML client exists
   - Ensure mock is configured for tests

4. **Argo connection failed**
   - Verify VPN connection
   - Check proxy is running: `./scripts/manage-argo-proxy.sh status`
   - Test connection: `./scripts/manage-argo-proxy.sh test`

## Best Practices

1. **Model Selection**
   - Use GPT-5 as default for best reasoning capability
   - Override specific agents based on their tasks
   - Use economical models (gpt5nano, gpt35) for testing

2. **Parameter Configuration**
   - Always specify correct token parameter (max_tokens vs max_completion_tokens)
   - Keep temperature consistent (0.7 default)
   - Adjust token limits based on task complexity

3. **Testing Strategy**
   - Use mocks for unit/integration tests
   - Reserve real LLM tests for behavioral validation
   - Test model fallback chains periodically

## Migration Notes

### From gpto3 to gpt5 (September 2025)

The default model has been changed from `gpto3` to `gpt5` for improved reasoning capabilities. Both models use the same parameter structure (`max_completion_tokens`), making migration seamless.

Key changes:
- Default model in `model_config.py` changed to "gpt5"
- ProductionClient strategy updated with GPT-5 models first
- All tests updated to handle new model responses

No code changes required for existing deployments - just update environment variables if needed.

## Related Documentation

- [BAML Testing Strategy](./BAML_TESTING_STRATEGY.md) - Testing approach for BAML functions
- [BAML Mocking Guide](./BAML_MOCKING_GUIDE.md) - How to mock BAML responses in tests
- [Argo Gateway Guide](../argo-gateway-complete-guide.md) - Complete Argo setup instructions