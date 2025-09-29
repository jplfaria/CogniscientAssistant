# Multi-Provider API Abstraction Plan

## Executive Summary

Enable the AI Co-Scientist to work with multiple LLM providers (OpenAI, Anthropic, local models) beyond the current Argo Gateway, while maintaining full backward compatibility.

## Current State

- **Single Provider**: All LLM calls go through Argo Gateway (internal proxy)
- **BAML-Based**: Type-safe interfaces using Boundary AI Markup Language
- **Working Well**: System is stable with Argo, need to expand options

## Proposed Architecture

```
┌─────────────────────────────────────────────────┐
│                   Agents                        │
├─────────────────────────────────────────────────┤
│              BAML Interface Layer               │
│         (Type-safe contracts & prompts)         │
├─────────────────────────────────────────────────┤
│           Provider Selection Layer              │
│      (Dynamic routing based on config)          │
├────────┬────────┬────────┬────────┬────────────┤
│  Argo  │OpenAI  │Anthropic│ Local │   Other    │
│Provider│Direct  │ Direct  │Ollama │ Providers  │
└────────┴────────┴────────┴────────┴────────────┘
```

## Implementation Phases

### Phase 1: Provider Abstraction Layer
**Goal**: Add provider abstraction without changing current behavior

1. Create `src/config/provider_config.py`:
   - `ProviderConfig` class for provider settings
   - `MultiProviderConfig` for managing multiple providers
   - Environment variable loading

2. Create `src/llm/provider_factory.py`:
   - Factory pattern for creating providers
   - Initially only supports Argo

3. Update existing code to use new abstraction:
   - Modify `model_config.py` to use `ProviderConfig`
   - Ensure all tests pass

### Phase 2: OpenAI Direct Support
**Goal**: Add direct OpenAI API access

1. Create `baml_src/clients-openai.baml`:
   ```baml
   client<llm> OpenAIDirectGPT4 {
     provider openai
     options {
       model "gpt-4-turbo-preview"
       api_key env.OPENAI_API_KEY
       // No base_url - uses OpenAI default
     }
   }
   ```

2. Implement `src/llm/openai_provider.py`:
   - Direct OpenAI API integration
   - Parameter handling for GPT models

3. Environment variables:
   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-...
   ```

### Phase 3: Anthropic & Local Models
**Goal**: Support Claude and local models

1. Create provider-specific BAML clients:
   - `clients-anthropic.baml` for Claude
   - `clients-local.baml` for Ollama/vLLM

2. Implement provider classes:
   - `anthropic_provider.py`
   - `ollama_provider.py`

3. Add parameter transformation:
   - Handle provider-specific parameter differences
   - Map `max_tokens` vs `max_completion_tokens`

### Phase 4: Advanced Features
**Goal**: Multi-provider orchestration

1. Implement fallback chains:
   - Automatic failover between providers
   - Circuit breakers per provider

2. Per-agent provider configuration:
   ```bash
   GENERATION_PROVIDER=anthropic  # Creative tasks
   REFLECTION_PROVIDER=openai     # Analysis
   ```

3. Cost optimization routing:
   - Route simple tasks to cheaper models
   - Use premium models for complex reasoning

## Configuration Examples

### Basic Multi-Provider Setup
```bash
# Primary provider
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Fallback provider
LLM_FALLBACK_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Keep Argo as option
ARGO_PROXY_URL=http://localhost:8000/v1
```

### Per-Agent Configuration
```bash
# Default for most agents
DEFAULT_MODEL=gpt4o
LLM_PROVIDER=openai

# Specific agent overrides
GENERATION_PROVIDER=anthropic
GENERATION_MODEL=claude-3-opus

RANKING_PROVIDER=ollama
RANKING_MODEL=llama2:70b
```

### Local Development
```bash
# Use local Ollama for all agents
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=mistral:7b
```

## Key Implementation Files

### New Files to Create
- `src/config/provider_config.py` - Provider configuration management
- `src/llm/provider_factory.py` - Provider instantiation
- `src/llm/openai_provider.py` - OpenAI direct integration
- `src/llm/anthropic_provider.py` - Anthropic integration
- `src/llm/ollama_provider.py` - Local model support
- `baml_src/clients-openai.baml` - OpenAI BAML clients
- `baml_src/clients-anthropic.baml` - Anthropic BAML clients
- `baml_src/clients-local.baml` - Local model BAML clients

### Files to Modify
- `src/config/model_config.py` - Use new provider config
- `src/llm/baml_integration.py` - Support provider selection
- `tests/conftest.py` - Add multi-provider mocks

## Testing Strategy

### Unit Tests
```python
# Test provider factory
def test_provider_factory():
    config = ProviderConfig(provider_type="openai", ...)
    provider = ProviderFactory.create_provider(config)
    assert isinstance(provider, OpenAIDirectProvider)
```

### Integration Tests
```python
# Test fallback behavior
@pytest.mark.asyncio
async def test_provider_fallback():
    # Configure primary to fail
    # Verify fallback provider is used
    # Check response is valid
```

### Provider-Specific Tests
```bash
# Test with each provider
LLM_PROVIDER=openai pytest tests/
LLM_PROVIDER=anthropic pytest tests/
LLM_PROVIDER=ollama pytest tests/
```

## Migration Checklist

- [ ] Phase 1: Provider abstraction (no behavior change)
  - [ ] Create provider configuration classes
  - [ ] Implement provider factory
  - [ ] Update model config to use new abstraction
  - [ ] All tests pass

- [ ] Phase 2: OpenAI direct support
  - [ ] Create OpenAI BAML clients
  - [ ] Implement OpenAI provider
  - [ ] Test with real OpenAI API
  - [ ] Document configuration

- [ ] Phase 3: Anthropic and local models
  - [ ] Create respective BAML clients
  - [ ] Implement provider classes
  - [ ] Add parameter transformation
  - [ ] Test each provider

- [ ] Phase 4: Advanced features
  - [ ] Implement fallback chains
  - [ ] Add per-agent overrides
  - [ ] Cost optimization routing
  - [ ] Full integration testing

## Backward Compatibility

1. **No Breaking Changes**: Existing Argo setup continues to work
2. **Default to Argo**: If no provider specified, use Argo
3. **Environment Variables**: Old variables still supported
4. **BAML Clients**: Existing Argo clients unchanged

## Security Considerations

1. **API Keys**: Never log, always use environment variables
2. **Provider Isolation**: No credential leakage between providers
3. **Audit Logging**: Track usage per provider
4. **Rate Limiting**: Respect provider-specific limits

## Success Criteria

- [ ] Argo Gateway continues to work as default
- [ ] Can switch to OpenAI with single env var change
- [ ] Can switch to Anthropic with single env var change
- [ ] Can use local models for development
- [ ] All existing tests pass
- [ ] New provider tests pass
- [ ] Documentation is clear and complete

## Next Steps

1. **Review & Approve**: Team review of this plan
2. **Create Branch**: `feature/multi-provider-support`
3. **Implement Phase 1**: Provider abstraction layer
4. **Test Thoroughly**: Ensure no regression
5. **Proceed with Phases 2-4**: Based on priority

This plan enables flexible LLM provider support while maintaining the stability and type safety of the current BAML-based system.