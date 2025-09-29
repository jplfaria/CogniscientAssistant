"""BAML integration for AI Co-Scientist agents."""

import os
from typing import Dict, Any, Optional
from baml_client import b
from src.config.model_config import get_model_config, configure_baml_for_agent


class BAMLAgent:
    """Base class for BAML-powered agents."""
    
    def __init__(self, agent_type: str):
        """Initialize agent with specific model configuration.
        
        Args:
            agent_type: Type of agent (e.g., 'supervisor', 'generation')
        """
        self.agent_type = agent_type
        self.model_config = get_model_config()
        
        # Configure BAML for this agent
        configure_baml_for_agent(agent_type)
        
        # Get the appropriate BAML client
        self.client_name = self.model_config.get_baml_client(agent_type)
        
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the model being used."""
        return {
            "agent_type": self.agent_type,
            "model": self.model_config.get_model_for_agent(self.agent_type),
            "baml_client": self.client_name,
        }


# Agent-specific implementations
class SupervisorAgent(BAMLAgent):
    """Supervisor agent using BAML."""
    
    def __init__(self):
        super().__init__("supervisor")
        
    async def orchestrate(self, task: str) -> str:
        """Orchestrate task execution."""
        # This will use the configured model via BAML
        # Implementation depends on BAML functions defined
        pass


class GenerationAgent(BAMLAgent):
    """Generation agent using BAML."""
    
    def __init__(self):
        super().__init__("generation")
        
    async def generate_hypothesis(self, context: str) -> str:
        """Generate a hypothesis."""
        # This will use the configured model via BAML
        # Will call b.GenerateHypothesis when implemented
        pass


class ReflectionAgent(BAMLAgent):
    """Reflection agent using BAML."""
    
    def __init__(self):
        super().__init__("reflection")
        
    async def evaluate_hypothesis(self, hypothesis: str) -> str:
        """Evaluate a hypothesis."""
        # This will use the configured model via BAML
        # Will call b.EvaluateHypothesis when implemented
        pass


class RankingAgent(BAMLAgent):
    """Ranking agent using BAML."""
    
    def __init__(self):
        super().__init__("ranking")
        
    async def compare_hypotheses(self, hyp1: str, hyp2: str) -> str:
        """Compare two hypotheses."""
        # This will use the configured model via BAML
        # Will call b.CompareHypotheses when implemented
        pass


class EvolutionAgent(BAMLAgent):
    """Evolution agent using BAML."""
    
    def __init__(self):
        super().__init__("evolution")
        
    async def evolve_hypothesis(self, hypothesis: str, feedback: str) -> str:
        """Evolve a hypothesis based on feedback."""
        # This will use the configured model via BAML
        pass


class ProximityAgent(BAMLAgent):
    """Proximity agent using BAML."""
    
    def __init__(self):
        super().__init__("proximity")
        
    async def cluster_hypotheses(self, hypotheses: list) -> Dict[str, list]:
        """Cluster similar hypotheses."""
        # This will use the configured model via BAML
        pass


class MetaReviewAgent(BAMLAgent):
    """Meta-review agent using BAML."""
    
    def __init__(self):
        super().__init__("meta_review")
        
    async def synthesize_findings(self, reviews: list) -> str:
        """Synthesize findings from multiple reviews."""
        # This will use the configured model via BAML
        pass


# Utility function for testing
def print_agent_configuration():
    """Print the current agent configuration."""
    config = get_model_config()
    print(f"Default model: {config.default_model}")
    print("\nAgent-specific models:")
    
    for agent_type in config.AGENT_TYPES:
        model = config.get_model_for_agent(agent_type)
        client = config.get_baml_client(agent_type)
        override = agent_type in config.agent_models
        
        print(f"  {agent_type:<12} -> {model:<15} (BAML: {client}){' [override]' if override else ''}")