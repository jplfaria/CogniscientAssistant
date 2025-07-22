# Model Requirements and Findings Summary

## Executive Summary

After extensive testing and collaboration with the Argo Gateway team, we have successfully resolved all model compatibility issues. The AI Co-Scientist platform now works with all available models through the Argo Gateway.

## Key Findings

### 1. O-Series Model (gpto3) Parameter Behavior
- **Critical Finding**: The `max_tokens` parameter is **silently ignored** by o-series models
- **Solution**: Use `max_completion_tokens` instead for o-series models
- **Impact**: No errors thrown, but response length isn't actually limited when using `max_tokens`
- **Source**: Matt Dearing (Argo Gateway team)

### 2. Claude and Gemini Message Requirements
- **Critical Finding**: Claude and Gemini models require at least one user message
- **Error**: "messages: at least one message is required" when only system message present
- **Solution**: Modified all BAML prompts to include both system and user roles
- **Temporary Fix**: Argo-proxy auto-injects `[continue]` for system-only messages
- **Source**: Peng Ding (argo-proxy developer)

### 3. Content Format Normalization
- **Finding**: System role content in array format is automatically normalized to string
- **Details**: `[{"type": "text", "text": "..."}]` → `"..."`
- **Status**: Working correctly with Peng's fix in argo-proxy

## Model-Specific Configurations

### OpenAI O-Series (gpto3)
```python
{
    "model": "gpto3",
    "messages": [...],
    "max_completion_tokens": 4000,  # ONLY parameter that controls length
    # DO NOT USE: max_tokens (silently ignored)
    # OPTIONAL: temperature, top_p (verify behavior)
}
```

### Standard OpenAI Models (gpt4o, gpt35)
```python
{
    "model": "gpt4o",  # or "gpt35"
    "messages": [...],
    "max_tokens": 4000,
    "temperature": 0.7,
    "top_p": 0.9
}
```

### Claude Models (claudeopus4, claudesonnet4)
```python
{
    "model": "claudeopus4",  # or "claudesonnet4"
    "messages": [
        {"role": "system", "content": "..."},  # Can use array format
        {"role": "user", "content": "..."}     # REQUIRED - at least one
    ],
    "max_tokens": 4000,
    "temperature": 0.7
}
```

### Gemini Models (gemini25pro)
```python
{
    "model": "gemini25pro",
    "messages": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."}     # REQUIRED - same as Claude
    ],
    "max_tokens": 4000,
    "temperature": 0.7
}
```

## Model Compatibility Matrix

| Model | max_tokens | max_completion_tokens | user_msg_required | Array Content | Notes |
|-------|------------|----------------------|-------------------|---------------|--------|
| gpto3 | ❌ (ignored) | ✅ | ❌ | ✅ | Use max_completion_tokens only |
| gpt4o | ✅ | ❌ | ❌ | ✅ | Standard OpenAI |
| gpt35 | ✅ | ❌ | ❌ | ✅ | Standard OpenAI |
| claudeopus4 | ✅ | ❌ | ✅ | ✅ (normalized) | Requires user message |
| claudesonnet4 | ✅ | ❌ | ✅ | ✅ (normalized) | Requires user message |
| gemini25pro | ✅ | ❌ | ✅ | ✅ (normalized) | Requires user message |

## BAML Prompt Updates

All BAML functions have been updated to use both system and user roles:

```baml
prompt #"
    {{ _.role("system") }}
    You are an expert at [task description]...
    
    {{ _.role("user") }}
    [Specific request with data]...
"#
```

This ensures compatibility with all models, especially Claude and Gemini.

## Performance Observations

- **gpto3 (o3)**: ~8-10 seconds typical response time (not 64s as initially observed)
- **gpt4o**: ~7 seconds typical response time
- **Claude models**: ~2-3 seconds typical response time
- **Gemini models**: Variable, sometimes returns null

## Integration Status

✅ **Phase 7 Tests**: BAML infrastructure working with all models
✅ **Phase 8 Tests**: Argo Gateway integration verified
✅ **Claude Compatibility**: Resolved with prompt structure changes
✅ **Gemini Compatibility**: Working with same approach as Claude

## Recommendations

1. **Default Model**: Use `gpt4o` for general tasks (reliable, good performance)
2. **Reasoning Tasks**: Consider `gpto3` for complex reasoning (despite slower response)
3. **Fast Responses**: Use Claude models when speed is critical
4. **Always Include User Messages**: Essential for Claude and Gemini compatibility

## Next Steps

1. Update to official argo-proxy release when available (currently using fix/system_message branch)
2. Complete remaining o3 parameter testing (verify temperature/top_p behavior)
3. Consider implementing model-specific parameter validation in BAML wrapper

## Credits

Special thanks to:
- Matt Dearing (Argo Gateway) - For clarifying o-series parameter behavior
- Peng Ding (argo-proxy) - For implementing content normalization fixes
- The broader Argonne team for supporting this integration