// BAML Client Configuration for AI Co-Scientist
// This file defines the LLM clients and their configurations

// Mock client for testing purposes
client<llm> MockClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    base_url "http://localhost:8000/v1"  // Mock server endpoint
    default_role "assistant"
  }
}

// Development client with basic configuration
client<llm> DevelopmentClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    temperature 0.7
    max_tokens 2000
    default_role "assistant"
  }
}

// Future Argo Gateway configuration (to be implemented in Phase 8)
// client<llm> ArgoClient {
//   provider custom
//   options {
//     base_url env.ARGO_GATEWAY_URL
//     api_key env.ARGO_API_KEY
//     model "gpt4o"
//     temperature 0.7
//     max_tokens 4000
//     timeout_seconds 60
//     retry_policy {
//       max_retries 3
//       initial_delay_ms 1000
//       max_delay_ms 10000
//       exponential_backoff true
//     }
//   }
// }

// Default client selection based on environment
client<llm> DefaultClient {
  provider env.BAML_CLIENT_PROVIDER
  options {
    model env.BAML_MODEL
    temperature 0.7
    max_tokens 2000
    default_role "assistant"
  }
}

// Test Clients for Different Scenarios

// Client for testing error handling
client<llm> TestErrorClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    base_url "http://localhost:8001/v1"  // Non-existent server for errors
    timeout_seconds 1  // Very short timeout to trigger errors
    default_role "assistant"
  }
}

// Client for testing slow responses and timeouts
client<llm> TestSlowClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    base_url "http://localhost:8000/v1"
    timeout_seconds 5  // Moderate timeout for testing
    default_role "assistant"
    // Simulated slow response via mock server
  }
}

// Client for testing rate limiting
client<llm> TestRateLimitedClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    base_url "http://localhost:8000/v1"
    default_role "assistant"
    retry_policy {
      max_retries 2
      initial_delay_ms 100
      max_delay_ms 1000
      exponential_backoff false
    }
  }
}

// Client for testing context window limits
client<llm> TestContextClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    base_url "http://localhost:8000/v1"
    max_tokens 100  // Small limit for testing
    default_role "assistant"
  }
}

// Client with retry policies enabled
client<llm> TestRetryClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    base_url "http://localhost:8000/v1"
    default_role "assistant"
    retry_policy {
      max_retries 3
      initial_delay_ms 500
      max_delay_ms 5000
      exponential_backoff true
    }
  }
}

// Client with retries disabled
client<llm> TestNoRetryClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    base_url "http://localhost:8000/v1"
    default_role "assistant"
    retry_policy {
      max_retries 0
    }
  }
}

// Test configuration for unit tests
test TestClient {
  // Uses MockClient for all tests by default
  functions [
    GenerateHypothesis
    ReviewHypothesis
    PerformSafetyCheck
  ]
  default_client MockClient
}

// Test configuration for error scenarios
test ErrorScenarios {
  functions [
    GenerateHypothesis
    ReviewHypothesis
    PerformSafetyCheck
  ]
  default_client TestErrorClient
}

// Test configuration for performance scenarios
test PerformanceScenarios {
  functions [
    GenerateHypothesis
    ReviewHypothesis
    PerformSafetyCheck
  ]
  default_client TestSlowClient
}

// Test configuration for edge case scenarios
test EdgeCaseScenarios {
  functions [
    GenerateHypothesis
    ReviewHypothesis
    PerformSafetyCheck
  ]
  default_client TestContextClient
}