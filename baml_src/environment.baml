// BAML Environment Configuration
// This file defines environment variables used in the AI Co-Scientist system

configuration {
    // API Configuration
    BAML_CLIENT_PROVIDER: string = env.BAML_CLIENT_PROVIDER or "openai"
    BAML_MODEL: string = env.BAML_MODEL or "gpt-3.5-turbo" 
    BAML_BASE_URL: string = env.BAML_BASE_URL or "http://localhost:8000/v1"
    BAML_API_KEY: string = env.BAML_API_KEY or ""
    
    // Argo Gateway Configuration
    ARGO_GATEWAY_URL: string = env.ARGO_GATEWAY_URL or "http://localhost:8000"
    ARGO_PROXY_URL: string = env.ARGO_PROXY_URL or "http://localhost:8000/v1"
    ARGO_PROXY_HOST: string = env.ARGO_PROXY_HOST or "127.0.0.1"
    ARGO_PROXY_PORT: string = env.ARGO_PROXY_PORT or "8000"
    ARGO_USERNAME: string = env.ARGO_USERNAME or ""
    ARGO_USER: string = env.ARGO_USER or ""
    ARGO_API_KEY: string = env.ARGO_API_KEY or ""
    
    // Default Model Configuration
    DEFAULT_MODEL: string = env.DEFAULT_MODEL or "gpt4o"
    
    // System Configuration
    LOG_LEVEL: string = env.LOG_LEVEL or "INFO"
    ENABLE_SAFETY_CHECKS: bool = env.ENABLE_SAFETY_CHECKS or true
    VERBOSE_BAML: bool = env.VERBOSE_BAML or false
    
    // Safety Configuration
    SAFETY_MODEL: string = env.SAFETY_MODEL or "gpt4o"
    RESEARCH_GOALS_FILE: string = env.RESEARCH_GOALS_FILE or ".aicoscientist/research_goals.txt"
    SAFETY_LOG_DIR: string = env.SAFETY_LOG_DIR or ".aicoscientist/safety_logs"
    
    // Worker Configuration
    MAX_WORKERS: string = env.MAX_WORKERS or "4"
    TASK_TIMEOUT: string = env.TASK_TIMEOUT or "3600"
    ASYNC_ENABLED: bool = env.ASYNC_ENABLED or true
    
    // Performance Configuration
    MAX_CONCURRENT_AGENTS: int = env.MAX_CONCURRENT_AGENTS or 5
    AGENT_TIMEOUT_SECONDS: int = env.AGENT_TIMEOUT_SECONDS or 300
    
    // Storage Configuration
    CHECKPOINT_DIR: string = env.CHECKPOINT_DIR or ".aicoscientist/checkpoints"
    HYPOTHESIS_DIR: string = env.HYPOTHESIS_DIR or ".aicoscientist/hypotheses"
    REVIEW_DIR: string = env.REVIEW_DIR or ".aicoscientist/reviews"
    
    // Model Configuration
    PRIMARY_MODEL: string = env.PRIMARY_MODEL or "gpt-3.5-turbo"
    SUPERVISOR_MODEL: string = env.SUPERVISOR_MODEL or "gpt4o"
    GENERATION_MODEL: string = env.GENERATION_MODEL or "claudeopus4"
    REFLECTION_MODEL: string = env.REFLECTION_MODEL or "gpt4o"
    RANKING_MODEL: string = env.RANKING_MODEL or "gpto3mini"
    EVOLUTION_MODEL: string = env.EVOLUTION_MODEL or "claudeopus4"
    PROXIMITY_MODEL: string = env.PROXIMITY_MODEL or "gpto3mini"
    META_REVIEW_MODEL: string = env.META_REVIEW_MODEL or "gpt4o"
}

// Export for use in BAML
env {
    BAML_CLIENT_PROVIDER: string
    BAML_MODEL: string
    BAML_BASE_URL: string
    BAML_API_KEY: string
    ARGO_GATEWAY_URL: string  // Argo Gateway endpoint URL
    ARGO_PROXY_URL: string
    ARGO_PROXY_HOST: string
    ARGO_PROXY_PORT: string
    ARGO_USERNAME: string
    ARGO_USER: string
    ARGO_API_KEY: string
    DEFAULT_MODEL: string
    LOG_LEVEL: string
    ENABLE_SAFETY_CHECKS: bool
    VERBOSE_BAML: bool
    SAFETY_MODEL: string
    RESEARCH_GOALS_FILE: string
    SAFETY_LOG_DIR: string
    MAX_WORKERS: string
    TASK_TIMEOUT: string
    ASYNC_ENABLED: bool
    MAX_CONCURRENT_AGENTS: int
    AGENT_TIMEOUT_SECONDS: int
    CHECKPOINT_DIR: string
    HYPOTHESIS_DIR: string
    REVIEW_DIR: string
    PRIMARY_MODEL: string
    SUPERVISOR_MODEL: string
    GENERATION_MODEL: string
    REFLECTION_MODEL: string
    RANKING_MODEL: string
    EVOLUTION_MODEL: string
    PROXIMITY_MODEL: string
    META_REVIEW_MODEL: string
}

// Documentation
// Required variables:
// - BAML_API_KEY: API key for LLM provider
// - ARGO_USERNAME: Username for Argo Gateway (if using)
// - ARGO_API_KEY: API key for Argo Gateway (if using)

// Optional variables:
// All other variables have defaults and are optional
