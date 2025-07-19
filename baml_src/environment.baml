// BAML Environment Variable Configuration
// This file defines environment variables used throughout the AI Co-Scientist system

// Environment configuration block
configuration {
  // Core BAML Configuration
  // Provider for BAML clients (e.g., "openai", "anthropic", "custom")
  BAML_CLIENT_PROVIDER string = env.BAML_CLIENT_PROVIDER ?? "openai"
  
  // Default model to use for BAML clients
  BAML_MODEL string = env.BAML_MODEL ?? "gpt-3.5-turbo"
  
  // Argo Gateway Configuration (Phase 8)
  // URL for Argo Gateway proxy server
  ARGO_GATEWAY_URL string = env.ARGO_GATEWAY_URL ?? "http://localhost:8050/v1"
  
  // API key for Argo Gateway authentication (required for production)
  ARGO_API_KEY string = env.ARGO_API_KEY ?? ""
  
  // Argo username for authentication
  ARGO_USER string = env.ARGO_USER ?? ""
  
  // Argo Proxy URL (alias for ARGO_GATEWAY_URL)
  ARGO_PROXY_URL string = env.ARGO_PROXY_URL ?? "http://localhost:8050/v1"
  
  // Model Selection
  // Default model for all agents
  DEFAULT_MODEL string = env.DEFAULT_MODEL ?? "gpt-3.5-turbo"
  
  // Agent-Specific Model Configuration
  // Each agent can have its own model override
  SUPERVISOR_MODEL string = env.SUPERVISOR_MODEL ?? env.DEFAULT_MODEL ?? "gpt-3.5-turbo"
  GENERATION_MODEL string = env.GENERATION_MODEL ?? env.DEFAULT_MODEL ?? "gpt-3.5-turbo"
  REFLECTION_MODEL string = env.REFLECTION_MODEL ?? env.DEFAULT_MODEL ?? "gpt-3.5-turbo"
  RANKING_MODEL string = env.RANKING_MODEL ?? env.DEFAULT_MODEL ?? "gpt-3.5-turbo"
  EVOLUTION_MODEL string = env.EVOLUTION_MODEL ?? env.DEFAULT_MODEL ?? "gpt-3.5-turbo"
  PROXIMITY_MODEL string = env.PROXIMITY_MODEL ?? env.DEFAULT_MODEL ?? "gpt-3.5-turbo"
  META_REVIEW_MODEL string = env.META_REVIEW_MODEL ?? env.DEFAULT_MODEL ?? "gpt-3.5-turbo"
  
  // Safety Configuration
  // Enable or disable safety checks (true/false)
  ENABLE_SAFETY_CHECKS bool = env.ENABLE_SAFETY_CHECKS ?? true
  
  // Model to use for safety checks
  SAFETY_MODEL string = env.SAFETY_MODEL ?? env.DEFAULT_MODEL ?? "gpt-3.5-turbo"
  
  // Logging Configuration
  // Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  LOG_LEVEL string = env.LOG_LEVEL ?? "INFO"
  
  // Enable verbose BAML logging
  VERBOSE_BAML bool = env.VERBOSE_BAML ?? false
  
  // Performance Configuration
  // Maximum number of concurrent agents
  MAX_CONCURRENT_AGENTS int = env.MAX_CONCURRENT_AGENTS ?? 5
  
  // Timeout for agent operations in seconds
  AGENT_TIMEOUT_SECONDS int = env.AGENT_TIMEOUT_SECONDS ?? 300
}

// Export environment variables for use in BAML clients
// These can be referenced in clients.baml using env.VARIABLE_NAME syntax
env {
  // Core BAML variables
  string BAML_CLIENT_PROVIDER = configuration.BAML_CLIENT_PROVIDER
  string BAML_MODEL = configuration.BAML_MODEL
  
  // Argo Gateway variables
  string ARGO_GATEWAY_URL = configuration.ARGO_GATEWAY_URL
  string ARGO_API_KEY = configuration.ARGO_API_KEY  // optional: will be empty string if not set
  string ARGO_USER = configuration.ARGO_USER  // optional: will be empty string if not set
  string ARGO_PROXY_URL = configuration.ARGO_PROXY_URL
  
  // Model selection variables
  string DEFAULT_MODEL = configuration.DEFAULT_MODEL
  string SUPERVISOR_MODEL = configuration.SUPERVISOR_MODEL
  string GENERATION_MODEL = configuration.GENERATION_MODEL
  string REFLECTION_MODEL = configuration.REFLECTION_MODEL
  string RANKING_MODEL = configuration.RANKING_MODEL
  string EVOLUTION_MODEL = configuration.EVOLUTION_MODEL
  string PROXIMITY_MODEL = configuration.PROXIMITY_MODEL
  string META_REVIEW_MODEL = configuration.META_REVIEW_MODEL
  
  // Safety variables
  bool ENABLE_SAFETY_CHECKS = configuration.ENABLE_SAFETY_CHECKS
  string SAFETY_MODEL = configuration.SAFETY_MODEL
  
  // Logging variables
  string LOG_LEVEL = configuration.LOG_LEVEL
  bool VERBOSE_BAML = configuration.VERBOSE_BAML
  
  // Performance variables
  int MAX_CONCURRENT_AGENTS = configuration.MAX_CONCURRENT_AGENTS
  int AGENT_TIMEOUT_SECONDS = configuration.AGENT_TIMEOUT_SECONDS
}

// Type definitions for environment variables
// These ensure type safety when using environment variables
types {
  // Provider type enumeration
  Provider enum {
    openai
    anthropic
    custom
    mock
  }
  
  // Log level enumeration
  LogLevel enum {
    DEBUG
    INFO
    WARNING
    ERROR
    CRITICAL
  }
  
  // Model name type (for validation)
  ModelName string {
    // Common model patterns
    pattern: "^(gpt-|claude-|gemini-|mock-)"
  }
}

// Required vs Optional Variables Documentation
// Required variables (must be set for production):
// - ARGO_API_KEY: Required when using Argo Gateway in production
// - ARGO_USER: Required for Argo authentication
//
// Optional variables (have sensible defaults):
// - All other variables have defaults and are optional
// - Agent-specific models fall back to DEFAULT_MODEL if not set
// - DEFAULT_MODEL falls back to "gpt-3.5-turbo" if not set
//
// Development defaults:
// - Mock/test configurations use localhost URLs
// - Safety checks are enabled by default
// - Logging is set to INFO level by default