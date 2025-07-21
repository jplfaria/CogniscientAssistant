# Argo Gateway Integration Specification

**Type**: Infrastructure Component  
**Interactions**: LLM Abstraction Layer, All Agents, External Model Providers  
**Prerequisites**: 
- Read: LLM Abstraction Layer Specification
- Read: Multi-Agent Architecture Specification
- Understand: Argo Gateway API and proxy configuration

## Purpose

The Argo Gateway Integration provides centralized access to multiple Large Language Model providers through Argonne National Laboratory's unified API gateway. This component enables the AI Co-Scientist system to leverage diverse models while maintaining consistent interfaces and managing resources efficiently.

## Core Behaviors

The Argo Gateway Integration:
- Routes agent requests to appropriate models via Argo's unified API
- Manages authentication and authorization for model access
- Implements intelligent model selection based on task requirements
- Handles provider-specific limitations and capabilities
- Provides fallback mechanisms for high availability
- Tracks usage and costs across all model providers

## Behavioral Requirements

### Gateway Connection Management

The integration MUST:
- Maintain persistent connections to the Argo proxy service
- Handle connection failures with automatic reconnection
- Implement health checks for gateway availability
- Queue requests during connection disruptions
- Provide clear status indicators for gateway health

The integration MUST NOT:
- Bypass Argo Gateway for direct model access
- Store or cache authentication credentials
- Expose internal gateway endpoints to agents

### Model Orchestration

When orchestrating multiple models, the system MUST:
1. Select appropriate models based on task complexity
2. Balance load across available providers
3. Optimize for cost when quality requirements are met
4. Fall back to alternative models on failure
5. Track performance metrics per model

## Input Specification

### Request Routing Format

```
{
  "routing_request": {
    "request_id": "unique_identifier",
    "priority": "high|normal|low",
    "requirements": {
      "min_context_length": integer,
      "multimodal": boolean,
      "streaming": boolean,
      "function_calling": boolean,
      "latency_requirement": "real-time|standard|batch"
    },
    "preferences": {
      "preferred_models": ["model_id_list"],
      "cost_sensitivity": "minimize|balanced|performance",
      "consistency_requirement": "high|medium|low"
    },
    "llm_request": {
      // Standard LLM abstraction layer request
    }
  }
}
```

### Model Selection Criteria

- **Task Complexity**: Complex reasoning → Advanced models (GPT-4o, Claude Opus)
- **Speed Requirements**: Real-time needs → Fast models (Gemini Flash, GPT-3.5)
- **Context Length**: Long documents → High-context models (Claude, Gemini)
- **Multimodal Needs**: Image/document analysis → Vision-capable models
- **Cost Optimization**: Simple tasks → Efficient models

## Output Specification

### Gateway Response Format

```
{
  "routing_response": {
    "request_id": "matching_request_id",
    "model_used": "argo:model-name",
    "routing_metadata": {
      "selection_reason": "capability|availability|cost|preference",
      "alternatives_considered": ["model_list"],
      "routing_time": float,
      "queue_time": float
    },
    "usage_metrics": {
      "estimated_cost": float,
      "tokens_processed": integer,
      "rate_limit_remaining": integer
    },
    "llm_response": {
      // Standard LLM abstraction layer response
    }
  }
}
```

## Configuration Management

### Argo Proxy Configuration

The integration MUST:
- Configure proxy endpoint from environment variables
- Support dynamic proxy URL updates without restart
- Validate proxy accessibility on startup
- Implement secure communication protocols

Example configuration:
```
ARGO_PROXY_URL=http://localhost:8000/v1
ARGO_AUTH_USER=scientist_id
ARGO_REQUEST_TIMEOUT=30
ARGO_MAX_RETRIES=3
```

### Model Mapping

The integration maintains mappings between:
- Logical model names → Argo model identifiers
- Model capabilities → Task requirements
- Cost profiles → Budget constraints
- Performance characteristics → SLA requirements

## Provider-Specific Handling

### OpenAI Models via Argo

When routing to OpenAI models:
- Map model names (e.g., "gpt-4o" → "argo:gpt-4o")
- Handle specific parameter constraints
- Respect rate limiting per model tier
- Implement appropriate retry strategies

### Google Models via Argo

When routing to Google models:
- Support Gemini 2.5 Pro for complex tasks
- Use Gemini 2.5 Flash for rapid responses
- Handle multimodal inputs appropriately
- Manage long context windows efficiently

### Anthropic Models via Argo

When routing to Anthropic models:
- Leverage Claude Opus 4 for advanced reasoning
- Use Claude Sonnet variants for balanced performance
- Handle conversation memory effectively
- Respect model-specific safety boundaries

## Load Balancing and Failover

The integration MUST implement:

### Round-Robin Distribution
- Distribute requests evenly across equivalent models
- Track model availability in real-time
- Adjust distribution based on response times
- Maintain session affinity when required

### Intelligent Failover
- Detect model failures within 5 seconds
- Automatically route to next best alternative
- Preserve request context during failover
- Log failover events for monitoring

### Circuit Breaker Pattern
- Open circuit after 3 consecutive failures
- Attempt recovery after 30-second cooldown
- Gradually increase traffic on recovery
- Alert on persistent circuit breaks

## Performance Optimization

### Request Batching
The integration SHOULD:
- Batch compatible requests to same model
- Reduce overhead for small requests
- Maintain individual request SLAs
- Provide batch status updates

### Response Caching
The integration MAY:
- Cache responses for identical requests
- Implement cache invalidation policies
- Respect agent-specific cache preferences
- Monitor cache hit rates

## Monitoring and Observability

### Metrics Collection

Track per model:
- Request volume and latency
- Success/failure rates
- Token usage and costs
- Rate limit utilization
- Failover frequency

### Cost Tracking

Monitor:
- Cost per agent type
- Cost per research project
- Budget utilization rates
- Cost optimization opportunities
- Anomaly detection for spending

## Error Handling

### Argo-Specific Errors

Handle:
- Proxy connection failures → Retry with backoff
- Authentication errors → Alert and fail fast
- Model unavailability → Automatic failover
- Rate limiting → Queue and retry
- Invalid model names → Clear error messages

### Error Response Format

```
{
  "error": {
    "type": "argo_gateway_error",
    "code": "CONNECTION_FAILED|AUTH_ERROR|MODEL_UNAVAILABLE|RATE_LIMITED",
    "message": "Human-readable description",
    "details": {
      "attempted_model": "model_id",
      "fallback_available": boolean,
      "retry_after": integer
    }
  }
}
```

## Security Boundaries

The integration MUST:
- Validate all requests before forwarding
- Sanitize sensitive information in logs
- Implement request isolation
- Monitor for anomalous patterns
- Enforce model access policies

## Integration Examples

### Complex Research Task

Generation Agent requests hypothesis generation:
1. Integration evaluates complexity → Selects GPT-4o
2. Checks GPT-4o availability via Argo
3. Routes request with appropriate formatting
4. Monitors response time
5. Returns structured hypothesis

### High-Volume Ranking

Ranking Agent needs to evaluate 100 hypotheses:
1. Integration identifies batch opportunity
2. Selects Gemini Flash for speed
3. Batches requests efficiently
4. Handles partial failures gracefully
5. Aggregates results for agent

### Multimodal Analysis

Reflection Agent analyzes research figures:
1. Integration checks multimodal requirements
2. Routes to vision-capable model
3. Handles image preprocessing
4. Manages larger payload sizes
5. Returns structured analysis

## BAML Integration

Define Argo clients in BAML:

```baml
client<llm> ArgoGeminiPro {
  provider openai-generic
  options {
    base_url env.ARGO_PROXY_URL
    model "argo:gemini-2.5-pro"
    default_headers {
      "X-User-Id" env.ARGO_AUTH_USER
    }
  }
}

client<llm> ArgoClaudeOpus {
  provider openai-generic
  options {
    base_url env.ARGO_PROXY_URL
    model "argo:claude-opus-4"
    default_headers {
      "X-User-Id" env.ARGO_AUTH_USER
    }
  }
}
```

## Capacity Planning

The integration MUST:
- Track usage trends per model
- Predict capacity needs
- Alert on approaching limits
- Suggest optimization strategies
- Support usage reporting

## Disaster Recovery

In case of complete Argo Gateway failure:
1. Queue critical requests locally
2. Alert system administrators
3. Provide degraded service status
4. Maintain request logs for replay
5. Resume normal operation on recovery

The Argo Gateway Integration ensures the AI Co-Scientist system can leverage the best available models for each task while maintaining reliability, cost-effectiveness, and consistent behavior across all agents.