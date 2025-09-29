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
// FIXED: gpto3 (o3) now uses proper parameters for reasoning models
client<llm> ArgoGPTo3 {
  provider openai
  options {
    model "gpto3"
    base_url "http://localhost:8000/v1"  // Argo proxy
    api_key env.BAML_API_KEY
    max_tokens null  // REQUIRED: Set to null for reasoning models
    max_completion_tokens 4000  // FIXED: Use this instead of max_tokens
    timeout_seconds 60
    // NOTE: temperature and top_p are ignored by o3 API
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

// NEW GPT-5 Models - Next generation reasoning models
client<llm> ArgoGPT5 {
  provider openai
  options {
    model "gpt5"
    base_url "http://localhost:8000/v1"  // Argo proxy
    api_key env.BAML_API_KEY
    temperature 0.7
    top_p 0.9
    max_tokens null  // REQUIRED: Must be null for reasoning models
    max_completion_tokens 4000  // REQUIRED: Use this instead of max_tokens
    timeout_seconds 60
  }
}

client<llm> ArgoGPT5Mini {
  provider openai
  options {
    model "gpt5mini"
    base_url "http://localhost:8000/v1"  // Argo proxy
    api_key env.BAML_API_KEY
    temperature 0.7
    top_p 0.9
    max_tokens null  // REQUIRED: Must be null for reasoning models
    max_completion_tokens 4000  // REQUIRED: Use this instead of max_tokens
    timeout_seconds 60
  }
}

client<llm> ArgoGPT5Nano {
  provider openai
  options {
    model "gpt5nano"
    base_url "http://localhost:8000/v1"  // Argo proxy
    api_key env.BAML_API_KEY
    temperature 0.7
    top_p 0.9
    max_tokens null  // REQUIRED: Must be null for reasoning models
    max_completion_tokens 4000  // REQUIRED: Use this instead of max_tokens
    timeout_seconds 60
  }
}

// NEW Claude Opus 4.1 - Latest Anthropic reasoning model
client<llm> ArgoClaudeOpus41 {
  provider openai
  options {
    model "claudeopus41"
    base_url "http://localhost:8000/v1"  // Argo proxy
    api_key env.BAML_API_KEY
    temperature 0.7
    top_p 0.9
    max_tokens 4000  // CORRECT: Claude accepts max_tokens
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