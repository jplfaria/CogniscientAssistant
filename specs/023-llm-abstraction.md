# LLM Abstraction Layer Specification

**Type**: Infrastructure Component  
**Interactions**: All Agents, Argo Gateway Integration  
**Prerequisites**: 
- Read: Multi-Agent Architecture Specification
- Read: Agent Interaction Protocols Specification
- Understand: BAML (Basically A Modeling Language) concepts

## Purpose

The LLM Abstraction Layer provides a model-agnostic interface for all agent-to-LLM interactions within the AI Co-Scientist system. This layer ensures the system can leverage various LLM providers without requiring changes to agent logic.

## Core Behaviors

The LLM Abstraction Layer:
- Provides uniform interfaces for text generation, analysis, and reasoning
- Maintains provider-agnostic communication protocols
- Handles model-specific capabilities transparently
- Supports multimodal inputs when available
- Manages context windows appropriately for each model

## Behavioral Requirements

### Model Independence

The abstraction layer MUST:
- Accept requests in a standardized format regardless of underlying model
- Return responses in a consistent structure across all providers
- Handle provider-specific errors uniformly
- Support switching between models without agent modification

The abstraction layer MUST NOT:
- Expose model-specific parameters to agents
- Require agents to know which LLM is being used
- Allow implementation details to leak through the interface

### Request Handling

When an agent submits a request, the abstraction layer MUST:
1. Validate the request format
2. Transform the request to provider-specific format
3. Submit to the appropriate LLM endpoint
4. Parse the provider response
5. Return standardized response to the agent

## Input Specification

### Agent Request Format

```
{
  "request_id": "unique_identifier",
  "agent_type": "generation|reflection|ranking|evolution|proximity|meta-review",
  "request_type": "generate|analyze|evaluate|compare",
  "content": {
    "prompt": "natural language instruction",
    "context": {
      "previous_results": [...],
      "domain_knowledge": [...],
      "constraints": [...]
    },
    "parameters": {
      "max_length": integer,
      "temperature": float (0.0-1.0),
      "response_format": "text|structured|list"
    }
  }
}
```

### Supported Request Types

- **generate**: Create new content (hypotheses, protocols, text)
- **analyze**: Evaluate existing content for specific criteria
- **evaluate**: Score or rank content against criteria
- **compare**: Assess relative merits of multiple items

## Output Specification

### Standard Response Format

```
{
  "request_id": "matching_input_id",
  "status": "success|error|partial",
  "response": {
    "content": "generated or analyzed content",
    "metadata": {
      "model_used": "identifier",
      "tokens_used": integer,
      "processing_time": float
    }
  },
  "error": {
    "code": "error_type",
    "message": "human_readable_description",
    "recoverable": boolean
  }
}
```

## Provider Management

The abstraction layer MUST support:
- Multiple concurrent providers
- Fallback strategies when primary provider fails
- Load balancing across equivalent models
- Provider-specific rate limiting
- Automatic retry with exponential backoff

## Model Capabilities

The abstraction layer MUST:
- Track capabilities of each available model
- Route requests to appropriate models based on requirements
- Handle capability mismatches gracefully
- Provide clear feedback when requested operations exceed model capabilities

### Capability Matrix Example

```
{
  "model_capabilities": {
    "gemini-2.0": {
      "max_context": 1000000,
      "multimodal": true,
      "streaming": true,
      "function_calling": true
    },
    "gpt-4": {
      "max_context": 128000,
      "multimodal": true,
      "streaming": true,
      "function_calling": true
    },
    "claude-3": {
      "max_context": 200000,
      "multimodal": true,
      "streaming": true,
      "function_calling": false
    }
  }
}
```

## Context Management

The abstraction layer MUST:
- Track context usage per request
- Implement smart truncation when context exceeds limits
- Preserve critical information during truncation
- Warn agents when approaching context limits
- Support conversation memory across multiple requests

## Integration Requirements

### With Agents

- All agents access LLMs exclusively through this abstraction
- Agents remain unaware of underlying model changes
- Response formats remain consistent regardless of provider

### With Argo Gateway

- Abstraction layer connects to Argo Gateway for model access
- Handles authentication and routing transparently
- Manages connection pooling and resource optimization

## Error Handling

The abstraction layer MUST handle:
- Network timeouts with automatic retry
- Rate limiting with request queuing
- Model unavailability with fallback options
- Invalid responses with error transformation
- Context overflow with intelligent truncation

## Performance Requirements

- Response latency MUST NOT exceed 2x the underlying model latency
- Abstraction overhead MUST remain under 100ms
- Support for concurrent requests limited only by provider quotas
- Automatic request batching when beneficial

## Safety Boundaries

The abstraction layer MUST:
- Filter requests that violate safety policies
- Log all requests and responses for audit
- Implement content filtering based on configured rules
- Prevent prompt injection attempts
- Maintain request isolation between agents

## Examples

### Hypothesis Generation Request

Agent submits:
```
{
  "request_id": "gen-001",
  "agent_type": "generation",
  "request_type": "generate",
  "content": {
    "prompt": "Generate novel hypotheses for repurposing metformin for Acute Myeloid Leukemia treatment",
    "context": {
      "domain_knowledge": ["AML pathophysiology", "metformin mechanisms"],
      "constraints": ["focus on metabolic pathways", "consider combination therapies"]
    },
    "parameters": {
      "max_length": 2000,
      "temperature": 0.8,
      "response_format": "structured"
    }
  }
}
```

Abstraction layer returns:
```
{
  "request_id": "gen-001",
  "status": "success",
  "response": {
    "content": {
      "hypotheses": [
        {
          "summary": "Metformin enhances chemotherapy sensitivity in AML",
          "mechanism": "AMPK activation leads to mTOR inhibition...",
          "evidence_level": "preclinical"
        }
      ]
    },
    "metadata": {
      "model_used": "gemini-2.0",
      "tokens_used": 1523,
      "processing_time": 2.3
    }
  }
}
```

### Model Failover Scenario

1. Agent submits request to abstraction layer
2. Primary model (Gemini 2.0) returns timeout error
3. Abstraction layer automatically retries with fallback (GPT-4)
4. Response returned to agent with appropriate metadata
5. Agent remains unaware of the failover

## Integration with BAML

The abstraction layer interfaces are defined using BAML to ensure:
- Type-safe communication between components
- Automatic client generation for multiple languages
- Consistent error handling across implementations
- Easy addition of new providers

The BAML definitions specify the interface contracts while allowing flexible implementation choices for model integration.