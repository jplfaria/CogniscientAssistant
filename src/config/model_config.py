"""Model configuration for AI Co-Scientist agents."""

import os
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for model selection."""
    
    # Default model for all agents
    default_model: str
    
    # Optional per-agent overrides
    agent_models: Dict[str, str]
    
    # Available models mapping to BAML clients
    AVAILABLE_MODELS = {
        "gpto3": "ArgoGPTo3",  # OpenAI o3 reasoning model
        "gpt4o": "ArgoGPT4o",
        "gpt35": "ArgoGPT35",
        "claudeopus4": "ArgoClaudeOpus4",
        "claudesonnet4": "ArgoClaudeSonnet4",
        "gemini25pro": "ArgoGemini25Pro",
    }
    
    # Agent types
    AGENT_TYPES = [
        "supervisor",
        "generation", 
        "reflection",
        "ranking",
        "evolution",
        "proximity",
        "meta_review"
    ]
    
    @classmethod
    def from_env(cls) -> "ModelConfig":
        """Load configuration from environment variables."""
        # Default model (GPT-o3 for better reasoning)
        default = os.getenv("DEFAULT_MODEL", "gpto3")
        
        # Per-agent overrides (optional)
        agent_models = {}
        
        # Check for agent-specific models
        for agent in cls.AGENT_TYPES:
            env_var = f"{agent.upper()}_MODEL"
            if model := os.getenv(env_var):
                agent_models[agent] = model
        
        return cls(
            default_model=default,
            agent_models=agent_models
        )
    
    def get_model_for_agent(self, agent_type: str) -> str:
        """Get the model to use for a specific agent type."""
        # Check for specific override
        if agent_type.lower() in self.agent_models:
            return self.agent_models[agent_type.lower()]
        
        # Fall back to default
        return self.default_model
    
    def validate(self) -> bool:
        """Validate that all configured models are available."""
        all_models = [self.default_model] + list(self.agent_models.values())
        
        for model in all_models:
            if model not in self.AVAILABLE_MODELS:
                print(f"Warning: Model '{model}' not in available models")
                print(f"Available models: {list(self.AVAILABLE_MODELS.keys())}")
                return False
        
        return True
    
    def get_baml_client(self, agent_type: str) -> str:
        """Get the BAML client name for a specific agent type."""
        model = self.get_model_for_agent(agent_type)
        return self.AVAILABLE_MODELS.get(model, "ProductionClient")


# Singleton instance
_model_config: Optional[ModelConfig] = None

def get_model_config() -> ModelConfig:
    """Get the model configuration singleton."""
    global _model_config
    if _model_config is None:
        _model_config = ModelConfig.from_env()
        if not _model_config.validate():
            print("Using default model for invalid configurations")
    return _model_config

def configure_baml_for_agent(agent_type: str) -> None:
    """Configure BAML environment for a specific agent.
    
    This sets the AGENT_MODEL environment variable that the
    DynamicClient in BAML will use.
    """
    config = get_model_config()
    model = config.get_model_for_agent(agent_type)
    os.environ["AGENT_MODEL"] = model
    
    # Also set DEFAULT_MODEL if not already set
    if "DEFAULT_MODEL" not in os.environ:
        os.environ["DEFAULT_MODEL"] = config.default_model