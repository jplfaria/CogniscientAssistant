# BAML Model Testing Scripts

These scripts help diagnose BAML parsing issues across different models, particularly focusing on the o3 model compatibility.

## Scripts

### 1. test-baml-models.py
Full BAML integration test that calls `ParseResearchGoal` with different models.

**Usage:**
```bash
# Ensure Argo proxy is running first
python scripts/argo_proxy.py

# In another terminal, run the test
python scripts/test-baml-models.py
```

**What it tests:**
- Calls BAML's `ParseResearchGoal` function with each model
- Tests models: gpt4o, gpt35, claudeopus4, gpto3
- Shows which models parse successfully vs fail
- Saves detailed results to `test_results/baml_model_test_results.json`

### 2. test-baml-models-simple.py
Simplified test that makes raw API calls to understand response formats.

**Usage:**
```bash
# Ensure Argo proxy is running first
python scripts/argo_proxy.py

# In another terminal, run the test
python scripts/test-baml-models-simple.py
```

**What it tests:**
- Makes direct API calls to each model
- Checks if responses are valid JSON
- Shows raw response samples
- Helps identify if models need special handling
- Saves results to `test_results/model_response_format_test.json`

## Interpreting Results

### Success Scenarios
- ✅ Model returns valid JSON that BAML can parse
- Response contains all required fields
- No parsing errors

### Failure Scenarios
- ❌ JSON parse error: Model returns non-JSON format
- ❌ Missing fields: JSON is valid but lacks required fields
- ❌ API error: Connection or authentication issues
- ❌ Timeout: Model takes too long to respond

## Common Issues and Solutions

### Issue: o3 returns narrative text instead of JSON
**Solution:** Update BAML prompt to be more explicit about JSON format:
```baml
prompt #"
    ...
    
    IMPORTANT: Respond ONLY with a valid JSON object, no additional text.
    The JSON must have exactly these fields:
    {
        "primary_objective": "string",
        "sub_objectives": ["array"],
        ...
    }
"#
```

### Issue: Some models wrap JSON in markdown code blocks
**Solution:** Add response parsing logic to handle markdown:
```python
if "```json" in content:
    # Extract JSON from markdown block
    json_str = extract_json_from_markdown(content)
```

### Issue: Model-specific formatting differences
**Solution:** Create model-specific clients or prompts in BAML:
```baml
// Special client for o3
client<llm> ArgoGPTo3 {
  provider openai
  options {
    model "gpto3"
    // Add response_format if supported
    response_format { type: "json_object" }
  }
}
```

## Next Steps

Based on test results:

1. **If all models pass:** The issue may be elsewhere in the system
2. **If only o3 fails:** Implement o3-specific handling
3. **If multiple models fail:** Update BAML prompts to be more explicit
4. **If JSON parsing varies:** Add robust response parsing logic

## Related Files
- `baml_src/functions.baml` - Contains ParseResearchGoal function
- `baml_src/models.baml` - Defines ParsedResearchGoal structure
- `baml_src/clients.baml` - Model client configurations
- `src/infrastructure/llm_abstraction.py` - LLM abstraction layer