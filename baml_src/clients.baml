// BAML Client Configuration for AI Co-Scientist
// This file defines the LLM clients and their configurations

// Mock client for testing purposes
client<llm> MockClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    base_url "http://localhost:8000/v1"  // Mock server endpoint
    timeout_seconds 10  // Shorter timeout for mock
  }
}

// Development client with basic configuration
client<llm> DevelopmentClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    temperature 0.7
    max_tokens 2000
    timeout_seconds 30
  }
}

// Default client using environment variables
client<llm> DefaultClient {
  provider env.BAML_CLIENT_PROVIDER
  options {
    model env.BAML_MODEL
    base_url env.BAML_BASE_URL
    api_key env.BAML_API_KEY
  }
}

// Production client using Argo Gateway (commented out by default)
// client<llm> ArgoClient {
//   provider openai
//   options {
//     model env.DEFAULT_MODEL
//     base_url env.ARGO_GATEWAY_URL
//     api_key env.ARGO_API_KEY
//     timeout_seconds 60
//   }
//   retry_policy {
//     max_retries 3
//     initial_delay_ms 1000
//     max_delay_ms 10000
//     exponential_backoff true
//   }
// }

// Production client (will use Argo Gateway in production)
client<llm> ProductionClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    temperature 0.7
    max_tokens 4000
    timeout_seconds 60
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
  }
}

// Client for testing slow responses and timeouts
client<llm> TestSlowClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    base_url "http://localhost:8000/v1"
    timeout_seconds 5  // Moderate timeout for testing
    // Simulated slow response via mock server
  }
}

// Client for testing rate limiting
client<llm> TestRateLimitedClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    base_url "http://localhost:8000/v1"
    max_retries 5
  }
}

// Client for testing context window limits
client<llm> TestContextClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    base_url "http://localhost:8000/v1"
    max_tokens 100  // Small limit for testing
  }
}

// Client with retry policies enabled
client<llm> TestRetryClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    base_url "http://localhost:8000/v1"
    max_retries 3
    exponential_backoff true
  }
}

// Client with retries disabled
client<llm> TestNoRetryClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    base_url "http://localhost:8000/v1"
    max_retries 0
  }
}

// Test configurations
test TestClient {
  default_client MockClient
  functions [GenerateHypothesis, EvaluateHypothesis, PerformSafetyCheck, CompareHypotheses]
}

test ErrorScenarios {
  default_client TestErrorClient
  functions [GenerateHypothesis]
}

test PerformanceScenarios {
  default_client TestSlowClient
  functions [GenerateHypothesis]
}

test EdgeCaseScenarios {
  default_client TestContextClient
  functions [GenerateHypothesis]
}