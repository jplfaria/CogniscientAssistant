// BAML Client Configuration for AI Co-Scientist
// This file defines the LLM clients and their configurations
//
// IMPORTANT BAML LIMITATIONS:
// 1. The 'provider' field MUST be a literal string (e.g., "openai", "anthropic")
//    It does NOT support environment variables like env.PROVIDER
//    To switch providers dynamically, use different client definitions
// 2. BAML test blocks exist but we don't use them - we use pytest for all testing
// 3. Retry policies are available but not implemented - we use circuit breakers in Python
// 4. environment.baml is documentation only - BAML doesn't support config blocks

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
  provider openai
  options {
    model env.BAML_MODEL
    base_url env.BAML_BASE_URL
    api_key env.BAML_API_KEY
  }
}

// Dynamic client for agent-specific models
client<llm> DynamicClient {
  provider openai
  options {
    model env.AGENT_MODEL
    base_url "http://localhost:8000/v1"  // Argo proxy
    temperature 0.7
    max_tokens 4000
    timeout_seconds 60
  }
}

// Argo Gateway Clients for each available model
// IMPORTANT: gpto3 (o3) IGNORES max_tokens parameter
// O3 requires max_completion_tokens but BAML doesn't support it yet
// This is a known limitation - o3 responses may be longer than expected
client<llm> ArgoGPTo3 {
  provider openai
  options {
    model "gpto3"
    base_url "http://localhost:8000/v1"  // Argo proxy
    // WARNING: max_tokens is IGNORED by o3 models
    // O3 needs max_completion_tokens which BAML doesn't support
    // Consider using shorter prompts or post-processing responses
    max_tokens 4000  // This has NO EFFECT on o3 but required by BAML
    timeout_seconds 60
  }
}

// Argo Gateway Clients for each available model
client<llm> ArgoGPT4o {
  provider openai
  options {
    model "gpt4o"
    base_url "http://localhost:8000/v1"  // Argo proxy
    temperature 0.7
    max_tokens 4000
    timeout_seconds 60
  }
}

client<llm> ArgoGPT35 {
  provider openai
  options {
    model "gpt35"
    base_url "http://localhost:8000/v1"  // Argo proxy
    temperature 0.7
    max_tokens 4000
    timeout_seconds 60
  }
}

client<llm> ArgoClaudeOpus4 {
  provider openai
  options {
    model "claudeopus4"
    base_url "http://localhost:8000/v1"  // Argo proxy
    temperature 0.7
    max_tokens 4000
    timeout_seconds 60
  }
}

client<llm> ArgoClaudeSonnet4 {
  provider openai
  options {
    model "claudesonnet4"
    base_url "http://localhost:8000/v1"  // Argo proxy
    temperature 0.7
    max_tokens 4000
    timeout_seconds 60
  }
}

client<llm> ArgoGemini25Pro {
  provider openai
  options {
    model "gemini25pro"
    base_url "http://localhost:8000/v1"  // Argo proxy
    temperature 0.7
    max_tokens 4000
    timeout_seconds 60
  }
}

// Production client (uses model config)
client<llm> ProductionClient {
  provider openai
  options {
    model env.DEFAULT_MODEL
    base_url "http://localhost:8000/v1"  // Argo proxy
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

// Test configurations would go here