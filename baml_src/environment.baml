// BAML Environment Variable Documentation
// 
// This file documents the environment variables used by the AI Co-Scientist system.
// BAML itself doesn't support environment variable configuration blocks,
// so this is purely documentation.
//
// Required Environment Variables:
// - ARGO_API_KEY: API key for Argo Gateway authentication (Phase 8)
// - ARGO_USER: Username for Argo authentication (Phase 8)
//
// Optional Environment Variables:
// - BAML_CLIENT_PROVIDER: LLM provider ("openai", "anthropic", "custom")
// - BAML_MODEL: Default model name (e.g., "gpt-3.5-turbo")
// - ARGO_GATEWAY_URL: URL for Argo Gateway (default: "http://localhost:8050/v1")
// - DEFAULT_MODEL: Default model for all agents
// - ENABLE_SAFETY_CHECKS: Enable safety checks (true/false)
// - LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
// - MAX_CONCURRENT_AGENTS: Maximum concurrent agent executions
// - AGENT_TIMEOUT_SECONDS: Timeout for agent operations
//
// Agent-Specific Model Overrides:
// - SUPERVISOR_MODEL: Model for supervisor agent
// - GENERATION_MODEL: Model for generation agent
// - REFLECTION_MODEL: Model for reflection agent
// - RANKING_MODEL: Model for ranking agent
// - EVOLUTION_MODEL: Model for evolution agent
// - PROXIMITY_MODEL: Model for proximity agent
// - META_REVIEW_MODEL: Model for meta-review agent
//
// These environment variables should be set in your .env file or system environment
// before running the AI Co-Scientist system.