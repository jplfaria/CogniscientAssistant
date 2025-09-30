# Specification: BAML Infrastructure Enhancements

## Overview

This specification defines enhanced error handling, logging, and reliability features for the BAML infrastructure in the AI Co-Scientist system. These enhancements leverage BAML 0.209.0 capabilities to provide production-ready resilience.

## Goals

1. **Reliability**: Gracefully handle transient failures with automatic retry
2. **Observability**: Comprehensive logging and metrics for debugging
3. **High Availability**: Automatic failover to backup clients
4. **Performance**: Efficient exponential backoff and circuit breaker patterns

## Non-Goals

- Complete rewrite of existing BAML infrastructure
- Creating duplicate agent implementations
- Changing existing BAML function signatures
- Implementing streaming features (deferred to future phase)

## Technical Requirements

### Enhanced Error Handling

The system MUST:
1. Categorize errors as recoverable or non-recoverable
2. Implement exponential backoff for recoverable errors
3. Track error history with metadata
4. Support fallback client selection
5. Integrate circuit breaker pattern

### Error Categories

**Recoverable Errors** (retry automatically):
- Network timeouts
- Rate limiting (HTTP 429)
- Service unavailable (HTTP 503)
- Temporary connection issues

**Non-Recoverable Errors** (fail immediately):
- Invalid request (HTTP 400)
- Authentication failure (HTTP 401)
- Forbidden access (HTTP 403)
- Invalid parameters

### Retry Configuration

```python
DEFAULT_RETRY_CONFIG = {
    "max_retries": 3,
    "initial_delay": 1.0,  # seconds
    "max_delay": 60.0,     # seconds
    "exponential_base": 2.0,
    "jitter": True,
}
```

### Logging Infrastructure

The system MUST provide:
1. Structured JSON logging for analysis
2. Separate logs for operations, performance, and errors
3. Privacy controls with configurable redaction
4. Automatic log rotation
5. Request/response tracking

### Circuit Breaker Pattern

Prevent cascading failures by:
1. Tracking failure rates per client
2. Opening circuit after threshold exceeded
3. Half-open state for recovery testing
4. Automatic reset after timeout

### Integration Points

The enhanced error handling MUST integrate with:
1. `BAMLWrapper` class in `src/llm/baml_wrapper.py`
2. All BAML function calls (generate_hypothesis, evaluate_hypothesis, etc.)
3. Existing LLM abstraction layer
4. Agent implementations via BAMLWrapper

## Implementation Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Agent     │───▶│ BAMLWrapper  │───▶│ BAMLErrorHandler│
└─────────────┘    └──────────────┘    └─────────────────┘
                           │                     │
                           ▼                     ▼
                    ┌──────────────┐    ┌─────────────────┐
                    │ BAML Client  │    │ Circuit Breaker │
                    └──────────────┘    └─────────────────┘
```

## Testing Requirements

### Unit Tests

Create comprehensive tests for:
1. Error categorization logic
2. Exponential backoff calculations
3. Retry mechanism behavior
4. Circuit breaker state transitions
5. Fallback client selection
6. Error history tracking

### Integration Tests

Verify:
1. End-to-end error handling flow
2. Retry behavior with real BAML calls
3. Logging output format and content
4. Circuit breaker integration
5. Performance under error conditions

## Success Criteria

1. **Coverage**: ≥80% test coverage for error handling code
2. **Reliability**: System remains operational during transient failures
3. **Performance**: Minimal overhead from error handling (<5%)
4. **Observability**: All errors logged with actionable context
5. **Integration**: Seamless with existing BAML infrastructure

## Usage Example

```python
# Automatic retry with exponential backoff
wrapper = BAMLWrapper()
try:
    result = await wrapper.generate_hypothesis(
        goal="Research goal",
        constraints=["constraint1"],
    )
except Exception as e:
    # After all retries exhausted
    logger.error(f"Failed after retries: {e}")
    # Error history available for debugging
    history = wrapper.error_handler.get_error_history()
```

## Dependencies

- BAML 0.209.0 or higher
- Python asyncio for async retry logic
- Standard logging library for structured logs
- Optional: monitoring integration (future)

## Migration Path

1. Integrate `BAMLErrorHandler` into existing `BAMLWrapper`
2. Update each BAML function call to use error handler
3. Add logging configuration
4. Deploy with monitoring
5. Gradually tune retry and circuit breaker parameters

## Future Enhancements

- Streaming support for long-form generation
- Advanced fallback strategies
- Custom retry policies per operation
- Integration with observability platforms