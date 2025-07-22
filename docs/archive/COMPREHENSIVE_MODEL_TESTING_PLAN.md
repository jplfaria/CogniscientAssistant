# Comprehensive Model Testing Plan for AI Co-Scientist Platform

## Executive Summary

A focused 3-4 hour testing sprint to definitively determine the optimal model configuration for the AI Co-Scientist platform, testing all available models through the Argo Gateway with their specific parameter requirements.

## Quick Testing Objectives

1. **Performance**: Measure response times (5 runs per model)
2. **Compatibility**: Verify BAML integration with model-specific parameters
3. **Quality**: Evaluate scientific reasoning output
4. **Decision**: Select optimal default and per-agent models

## Critical Findings from Argo Team

### Key Learnings from Developer Communication
1. **Matt Dearing (Argo Gateway)**: O-series models silently ignore max_tokens
2. **Peng Ding (argo-proxy)**: Added normalization for system messages and auto-injection of user messages
3. **Real Issue**: Argo API requires user messages for Claude/Gemini, not just content format

### 1. O-Series (gpto3) Parameter Behavior
- **max_tokens is SILENTLY IGNORED** - No error thrown, but parameter has no effect
- **Only max_completion_tokens controls response length** for o-series models
- This explains why tests "work" but responses aren't actually limited

### 2. Claude and Gemini Model Requirements  
- **Claude and Gemini require at least one user message** - system-only messages fail
- **System role content gets normalized from array to string** by argo-proxy (Peng's fix)
- Array format `[{"type": "text", "text": "..."}]` is auto-converted to string for system role
- BAML has been updated to always include both system and user messages
- Argo-proxy auto-injects `[continue]` for system-only messages (temporary fix)

## Critical: Model-Specific Parameters

### OpenAI O-Series (gpto3)
```python
# O-series models have specific requirements
# IMPORTANT: Per Matt Dearing - max_tokens is SILENTLY IGNORED by o3
test_configs = {
    "gpto3_with_max_completion": {
        "model": "gpto3",
        "messages": messages,
        "max_completion_tokens": 4000,  # O-series specific - ONLY parameter that controls length
        # NO temperature, top_p, or max_tokens
    },
    "gpto3_with_max_tokens": {
        "model": "gpto3", 
        "messages": messages,
        "max_tokens": 4000,  # SILENTLY IGNORED - won't error but won't limit response
        "temperature": 0.7,  # Test if accepted
    },
    "gpto3_verify_max_tokens_ignored": {
        "model": "gpto3",
        "messages": messages,
        "max_tokens": 50,  # Set very low to verify it's ignored
        # Should still get full response, proving max_tokens is ignored
    }
}
```

### Standard OpenAI (gpt4o, gpt35)
```python
test_configs = {
    "gpt4o_standard": {
        "model": "gpt4o",
        "messages": messages,
        "max_tokens": 4000,
        "temperature": 0.7,
        "top_p": 0.9
    }
}
```

### Claude Models (claudeopus4, claudesonnet4)
```python
# Test message requirements
# IMPORTANT: Claude requires at least one user message
test_configs = {
    "claude_with_user": {
        "model": "claudeopus4",
        "messages": [
            {"role": "system", "content": [{"type": "text", "text": "You are helpful"}]},
            {"role": "user", "content": "Hello"}  # REQUIRED - at least one user message
        ]
    },
    "claude_system_only": {
        "model": "claudeopus4",
        "messages": [{
            "role": "system",
            "content": [{"type": "text", "text": "test"}]  # WILL FAIL - needs user message
        }]
        # Error: "messages: at least one message is required"
    },
    "claude_standard": {
        "model": "claudeopus4",
        "messages": [
            {"role": "system", "content": "You are a helpful AI"},
            {"role": "user", "content": "Generate a hypothesis about aging"}
        ],
        "max_tokens": 4000,
        "temperature": 0.7
    }
}
```

### Gemini Models (gemini25pro)
```python
# Gemini has same requirements as Claude
test_configs = {
    "gemini_with_user": {
        "model": "gemini25pro",
        "messages": [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"}  # REQUIRED
        ]
    },
    "gemini_system_only": {
        "model": "gemini25pro",
        "messages": [{
            "role": "system",
            "content": "test"  # WILL FAIL - needs user message
        }]
    }
}
```

## 3-Hour Testing Sprint

### Hour 1: Compatibility & Parameter Testing (45 min)

#### Test Matrix
| Model | Test Cases |
|-------|------------|
| gpto3 | 1. With max_completion_tokens only<br>2. With max_tokens (verify silently ignored)<br>3. With very low max_tokens=50 (verify still get full response)<br>4. With temperature (test acceptance) |
| gpt4o | 1. Standard OpenAI params<br>2. High token count (8000)<br>3. Temperature variations |
| claudeopus4 | 1. Array content with user role (should work)<br>2. Array content with system role (will fail)<br>3. String content with system role (required)<br>4. Mixed format test |
| gpt35 | 1. Standard params<br>2. Baseline performance |
| claudesonnet4 | Same as opus4 |
| gemini25pro | 1. Standard params<br>2. Multi-modal readiness |

### Hour 2: Performance & Quality Testing (60 min)

#### Performance Tests (5 runs each)
```python
async def test_performance(model, config):
    timings = []
    for i in range(5):
        start = time.time()
        response = await call_model(model, config)
        timings.append(time.time() - start)
    
    return {
        "mean": mean(timings),
        "median": median(timings),
        "min": min(timings),
        "max": max(timings),
        "stdev": stdev(timings) if len(timings) > 1 else 0
    }
```

#### Quality Test Prompts
1. **Hypothesis Generation**:
   ```
   Generate 3 novel hypotheses about the relationship between 
   quantum entanglement and information theory. Format as JSON:
   {
     "hypotheses": [
       {"id": 1, "title": "...", "description": "...", "testable": true/false}
     ]
   }
   ```

2. **Review Analysis**:
   ```
   Review this hypothesis: "Dark matter consists of primordial black holes 
   formed in the early universe." Provide a structured review:
   {
     "strengths": ["..."],
     "weaknesses": ["..."],
     "evidence_quality": 1-10,
     "recommendation": "accept/revise/reject"
   }
   ```

3. **Complex Ranking**:
   ```
   Compare these hypotheses for researching quantum computing:
   A: "Topological qubits using anyons"
   B: "Photonic quantum circuits"
   Return: {"winner": "A/B", "score_diff": 0-10, "reasoning": "..."}
   ```

### Hour 3: Edge Cases & Analysis (60 min)

#### Edge Case Tests
1. **Long Context Handling**:
   - 4000 token prompt
   - Test max_tokens vs max_completion_tokens limits
   - Multi-turn conversation memory

2. **Complex JSON Schemas**:
   - Nested objects (3+ levels)
   - Arrays of objects
   - Mixed types

3. **Error Recovery**:
   - Invalid parameters
   - Timeout handling
   - Retry logic

4. **BAML-Specific Issues**:
   - Content array format compatibility
   - System vs user role handling
   - JSON parsing reliability

### Hour 4: Implementation & Documentation (45 min)

1. Update configurations based on results
2. Document model-specific requirements
3. Create quick reference guide
4. Implement model-specific parameter handling

## Test Implementation Structure

```python
# tests/model_evaluation/comprehensive_test.py

class ModelTester:
    def __init__(self):
        self.results = {}
        
    async def test_model(self, model_name):
        results = {
            "compatibility": await self.test_compatibility(model_name),
            "performance": await self.test_performance(model_name),
            "quality": await self.test_quality(model_name),
            "edge_cases": await self.test_edge_cases(model_name),
            "parameters": await self.test_parameters(model_name)
        }
        return results
    
    async def test_parameters(self, model_name):
        """Test model-specific parameter requirements"""
        if model_name == "gpto3":
            return await self.test_o_series_params()
        elif model_name.startswith("claude"):
            return await self.test_claude_formats()
        else:
            return await self.test_standard_params()
```

## Expected Outputs

### 1. Parameter Compatibility Matrix
```markdown
| Model | max_tokens | max_completion_tokens | temperature | top_p | content_array | user_msg_required |
|-------|------------|---------------------|-------------|-------|---------------|------------------|
| gpto3 | ❌ (ignored) | ✅ | ❓ | ❓ | ✅ | ❌ |
| gpt4o | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ |
| claudeopus4 | ✅ | ❌ | ✅ | ✅ | ✅ (normalized) | ✅ |
| claudesonnet4 | ✅ | ❌ | ✅ | ✅ | ✅ (normalized) | ✅ |
| gemini25pro | ✅ | ❌ | ✅ | ✅ | ✅ (normalized) | ✅ |
| gpt35 | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ |
```

### 2. Performance Summary
```markdown
| Model | Mean Time | Median | Min | Max | Reliability |
|-------|-----------|--------|-----|-----|-------------|
| gpt4o | 7.2s | 7.0s | 6.5s | 8.1s | 100% |
| gpto3 | 12.5s | 10.0s | 8.0s | 45.0s | 95% |
```

### 3. Quality Scores
```markdown
| Model | Hypothesis | Review | Ranking | JSON Format | Overall |
|-------|------------|--------|---------|-------------|---------|
| gpto3 | 10/10 | 9/10 | 9/10 | 10/10 | 9.5/10 |
| gpt4o | 8/10 | 8/10 | 9/10 | 10/10 | 8.8/10 |
```

## Model-Specific Configuration Recommendations

Based on test results, create specific configurations:

```python
# For gpto3 (O-series)
GPTO3_CONFIG = {
    "max_completion_tokens": 4000,
    # NO max_tokens, temperature, top_p
}

# For gpt4o (standard)
GPT4O_CONFIG = {
    "max_tokens": 4000,
    "temperature": 0.7,
    "top_p": 0.9
}

# For Claude (working configuration)
CLAUDE_CONFIG = {
    "max_tokens": 4000,
    "temperature": 0.7,
    # IMPORTANT: Always include user message
    # System content array format is auto-normalized by argo-proxy
}

# For Gemini
GEMINI_CONFIG = {
    "max_tokens": 4000,
    "temperature": 0.7,
    # Same requirements as Claude
}
```

## Quick Execution Commands

```bash
# Run all tests with proper parameters
python -m pytest tests/model_evaluation/ -v --tb=short

# Test specific model with parameters
python scripts/test_model_params.py --model gpto3 --test-params

# Generate comprehensive report
python scripts/generate_model_report.py --detailed

# Quick compatibility check
python scripts/check_model_compatibility.py --all-models
```

## Decision Criteria

1. **Must Support BAML Format**: ✅ All models work with updated prompts
2. **Response Time**: <15s for 90% of requests (o3 ~8-10s typical)
3. **Quality Score**: ≥7/10 for scientific tasks
4. **Parameter Compatibility**: Works with required params
5. **Reliability**: >95% success rate
6. **Message Requirements**: Handle models that require user messages

## Final Deliverables

1. **MODEL_PARAMETER_GUIDE.md**: Exact parameters for each model
2. **Updated model_config.py**: With model-specific handling
3. **BAML client updates**: Handle model quirks
4. **.env.example**: Recommended configurations
5. **Quick reference card**: Model selection flowchart

This plan ensures we test the critical model-specific parameters that could make or break our implementation!