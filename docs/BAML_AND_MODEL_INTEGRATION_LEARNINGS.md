# BAML and Model Integration Learnings

This document captures the key learnings from implementing and testing BAML with multiple LLM models, particularly focusing on structured data extraction and reasoning transparency.

## Table of Contents
1. [Why We Need Structured JSON](#why-we-need-structured-json)
2. [The BAML Integration Challenge](#the-baml-integration-challenge)
3. [Model Behavior Discoveries](#model-behavior-discoveries)
4. [Solutions and Best Practices](#solutions-and-best-practices)
5. [Implementation Details](#implementation-details)
6. [Testing Strategy](#testing-strategy)

## Why We Need Structured JSON

### System Architecture Requirements

The AI Co-Scientist is a **multi-agent system** where structured data is essential:

1. **Inter-Agent Communication**: 
   - Agents exchange hypotheses, reviews, and rankings
   - Each agent expects specific data structures
   - Without JSON, agents would need custom parsing for each interaction

2. **Persistent Storage**:
   - Context Memory stores all data as JSON files on disk
   - Enables checkpoint/recovery functionality
   - Supports version tracking and temporal queries
   - Example: `hypotheses_v1.json`, `reviews_v2.json`

3. **Algorithmic Processing**:
   - **Elo Ranking**: Requires specific fields (id, winner, loser, scores)
   - **Similarity Calculations**: Needs consistent hypothesis structure
   - **Pattern Extraction**: Meta-review agent needs predictable data paths
   - **Tournament System**: Tracks wins, losses, and participation

4. **Output Generation**:
   - NIH proposals have strict formatting requirements
   - Research overviews need structured sections
   - Cannot reliably generate these from free-form text

### Example Data Flow
```
Generation Agent → Hypothesis (JSON) → Task Queue → Reflection Agent
     ↓                                                    ↓
  Storage                                              Review (JSON)
     ↓                                                    ↓
  Recovery                                           Ranking Agent
```

## The BAML Integration Challenge

### Initial Problem

When we first tested BAML with real LLMs, we discovered:

1. **BAML prompts didn't request JSON format**
   - Functions expected structured output but prompts produced narrative text
   - Example error: "Missing required field: primary_objective"

2. **Model-Specific Behaviors**
   - GPT-o3: Returned detailed markdown-formatted reasoning
   - Claude Opus 4: Provided structured arrays of observations
   - GPT-4o: Gave concise bullet points

3. **Version Coupling**
   - BAML generator version must match runtime version
   - We hit: Generator 0.202.1 vs Runtime 0.90.2

### Root Cause

BAML's default prompts produce human-readable responses, not JSON:
```
# What BAML was getting:
"1. Primary Research Objective:
To develop a cure for aging using nanotechnology..."

# What BAML expected:
{
  "primary_objective": "To develop a cure for aging using nanotechnology",
  ...
}
```

## Model Behavior Discoveries

### Key Finding: All Models Can Return JSON

Through extensive testing, we discovered:

1. **When explicitly asked for JSON, ALL models comply**:
   - GPT-o3 ✅
   - Claude Opus 4 ✅
   - GPT-4o ✅
   - GPT-3.5 ✅
   - Gemini 2.5 Pro ✅

2. **Reasoning Transparency**:
   - Initial concern: "o3 refuses to share private reasoning"
   - **Reality**: Both o3 and Claude share reasoning transparently
   - The key is HOW you ask for it

### Model Comparison Results

| Model | JSON Support | Reasoning Sharing | Response Time | Detail Level |
|-------|--------------|-------------------|---------------|--------------|
| GPT-o3 | ✅ Excellent | ✅ Transparent | ~13s | Very Detailed (800+ chars) |
| Claude Opus 4 | ✅ Excellent | ✅ Transparent | ~16s | Detailed (600+ chars) |
| GPT-4o | ✅ Excellent | ✅ Limited | ~3s | Concise (350+ chars) |

### Model Strengths

- **GPT-o3**: Best for deep reasoning, complex hypothesis generation
- **Claude Opus 4**: Best for nuanced analysis, thoughtful reviews
- **GPT-4o**: Best for rapid iteration, general tasks

## Solutions and Best Practices

### 1. Fix BAML Prompts (Implemented)

Add explicit JSON format requests to all BAML functions:

```python
# Before (produces narrative text):
prompt #"
  Analyze this goal and extract:
  1. The primary research objective
  2. Sub-objectives that support the main goal
  ...
  Be thorough but concise in your analysis.
"#

# After (produces JSON):
prompt #"
  Analyze this goal and extract:
  1. The primary research objective
  2. Sub-objectives that support the main goal
  ...
  
  Respond in valid JSON format matching the schema:
  {
    "primary_objective": "single clear statement",
    "sub_objectives": ["array", "of", "objectives"],
    ...
  }
"#
```

### 2. Model Configuration Strategy

We implemented a flexible configuration system:

```python
# In .env file:
DEFAULT_MODEL=gpto3  # o3 for everything by default

# Optional per-agent overrides (add to .env if desired):
# GENERATION_MODEL=gpto3      # Deep reasoning for hypotheses
# REFLECTION_MODEL=claudeopus4 # Nuanced analysis for reviews
# RANKING_MODEL=gpt4o         # Fast comparisons for tournaments
# EVOLUTION_MODEL=gpto3       # Creative enhancement
# PROXIMITY_MODEL=gpt4o       # Quick similarity calculations
# META_REVIEW_MODEL=gpto3     # Pattern synthesis
# SUPERVISOR_MODEL=gpt4o      # Fast orchestration decisions
```

**Suggested Model Assignments by Agent Type:**
- **Generation Agent**: GPT-o3 (best for complex reasoning and novel hypothesis creation)
- **Reflection Agent**: Claude Opus 4 (excellent for thoughtful, nuanced reviews)
- **Ranking Agent**: GPT-4o (fast comparisons, good enough quality)
- **Evolution Agent**: GPT-o3 (creative enhancement needs deep reasoning)
- **Proximity Agent**: GPT-4o (pattern matching is straightforward)
- **Meta-Review Agent**: GPT-o3 (synthesis requires deep understanding)
- **Supervisor Agent**: GPT-4o (orchestration decisions are typically simple)

### 3. Testing Strategy

Created comprehensive test suite:
- `test-baml-models.py`: Test BAML parsing with all models
- `test-baml-models-simple.py`: Test raw JSON responses
- `test-reasoning-behavior.py`: Compare reasoning transparency
- `test-flexible-parsing.py`: Test fallback parsing strategies

## Implementation Details

### Argo Proxy Integration

The Argo proxy translates between OpenAI format (expected by BAML) and Argo's internal format:

```
BAML → OpenAI Format → Argo Proxy → Argo Gateway → LLM
                                ↓
                        Translation Layer
```

Key files:
- `argo-config.yaml`: Proxy configuration
- `scripts/argo_proxy.py`: Fixed proxy implementation
- `.env`: Environment variables for BAML

### BAML Client Structure

```
baml_src/
├── clients.baml          # Client definitions (MockClient, ProductionClient, etc.)
├── functions.baml        # Function definitions with prompts
├── models.baml          # Data model definitions
└── environment.baml     # Documentation (comments only)

baml_client/             # Generated code
└── baml_client/
    ├── __init__.py
    ├── async_client.py
    └── types.py
```

### Real LLM Tests

Implemented optional real LLM tests:

```python
@pytest.mark.real_llm
class TestBAMLRealBehavior:
    """Test actual BAML behavior with real models."""
```

Run with: `pytest tests/integration/*_real.py -v --real-llm`

## Testing Strategy

### 1. Mock Tests (Fast, Default)
- Use MockClient in BAML
- Test system logic without LLM calls
- Part of main test suite

### 2. Real LLM Tests (Optional)
- Test actual model behavior
- Verify prompts work with all models
- Catch model-specific issues
- Run manually or in CI with flag

### 3. Test Organization
```
tests/
├── unit/                    # Fast, isolated tests
└── integration/
    ├── test_phase*_*.py    # Mock integration tests
    └── test_phase*_*_real.py # Real LLM tests
```

## Key Takeaways

1. **Explicit is Better**: Always explicitly request JSON format in prompts

2. **All Models Cooperate**: When asked properly, all modern models return structured data

3. **BAML Adds Value**: Despite initial challenges, BAML provides:
   - Type safety and validation
   - Centralized prompt management
   - Multi-model abstraction
   - Automatic retries

4. **Flexibility is Key**: The system supports:
   - Default model for all agents (gpto3)
   - Optional per-agent overrides
   - Easy model switching via environment variables

5. **Testing is Critical**: Real LLM tests revealed issues that mocks couldn't:
   - Prompt format problems
   - Model-specific behaviors
   - Response time variations

## Future Considerations

1. **Hybrid Approaches**: For maximum flexibility, consider:
   - BAML for structured agent communication
   - Direct API calls for creative tasks
   - Flexible parsing as fallback

2. **Model Evolution**: As models improve:
   - Test new models with existing test suite
   - Update prompts if needed
   - Leverage model-specific features

3. **Cost Optimization**: 
   - Use faster/cheaper models where appropriate
   - Cache common requests
   - Batch similar operations

## Conclusion

The journey to integrate BAML with multiple LLM models taught us that:
- Structured data is essential for multi-agent systems
- Explicit prompt engineering solves most parsing issues
- Modern LLMs are highly capable when properly instructed
- Flexibility in model selection optimizes for different tasks

The current implementation successfully balances structure (for system reliability) with flexibility (for model optimization), while maintaining the ability to leverage GPT-o3's superior reasoning capabilities as the default choice.