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