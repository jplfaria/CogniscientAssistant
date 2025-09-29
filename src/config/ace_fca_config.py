"""ACE-FCA Context Optimization Configuration.

This module provides configuration management for the ACE-FCA (Advanced Context
Engineering - Focused Context Analytics) context optimization system.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


@dataclass
class ACEFCAConfig:
    """Configuration for ACE-FCA context optimization."""

    # Main toggles
    optimization_enabled: bool = False
    literature_optimization: bool = True
    memory_optimization: bool = True
    output_validation: bool = True

    # Thresholds
    confidence_threshold: float = 0.8
    auto_enable_threshold: int = 100000  # tokens
    literature_max_papers: int = 8
    memory_max_entries: int = 10

    # Model-specific overrides
    model_overrides: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_environment(cls) -> "ACEFCAConfig":
        """Load configuration from environment variables."""

        # Check file overrides first
        if Path(".context_optimization_disabled").exists():
            return cls(optimization_enabled=False)

        if Path(".context_optimization_enabled").exists():
            optimization_enabled = True
        else:
            optimization_enabled = os.getenv("CONTEXT_OPTIMIZATION_ENABLED", "false").lower() == "true"

        if Path(".context_optimization_aggressive").exists():
            confidence_threshold = 0.6
            literature_max_papers = 5
            memory_max_entries = 6
        else:
            confidence_threshold = float(os.getenv("CONTEXT_OPTIMIZATION_CONFIDENCE_THRESHOLD", "0.8"))
            literature_max_papers = int(os.getenv("LITERATURE_MAX_PAPERS", "8"))
            memory_max_entries = int(os.getenv("MEMORY_MAX_ENTRIES", "10"))

        return cls(
            optimization_enabled=optimization_enabled,
            literature_optimization=optimization_enabled and os.getenv("LITERATURE_OPTIMIZATION_ENABLED", "true").lower() == "true",
            memory_optimization=optimization_enabled and os.getenv("MEMORY_OPTIMIZATION_ENABLED", "true").lower() == "true",
            output_validation=optimization_enabled and os.getenv("OUTPUT_VALIDATION_ENABLED", "true").lower() == "true",
            confidence_threshold=confidence_threshold,
            auto_enable_threshold=int(os.getenv("CONTEXT_OPTIMIZATION_AUTO_THRESHOLD", "100000")),
            literature_max_papers=literature_max_papers,
            memory_max_entries=memory_max_entries,
            model_overrides={
                "gpt5": os.getenv("GPT5_CONTEXT_OPTIMIZATION", "auto"),
                "claude": os.getenv("CLAUDE_CONTEXT_OPTIMIZATION", "auto"),
                "ollama": os.getenv("OLLAMA_CONTEXT_OPTIMIZATION", "enabled")
            }
        )

    def should_optimize_for_model(self, model_name: str, context_size: int = 0) -> bool:
        """Determine if optimization should be enabled for specific model.

        Args:
            model_name: Name of the model being used
            context_size: Size of the context in tokens

        Returns:
            True if optimization should be enabled for this model/context
        """

        if not self.optimization_enabled:
            return False

        # Check model-specific override
        model_key = self._get_model_key(model_name)
        override = self.model_overrides.get(model_key, "auto")

        if override == "enabled":
            return True
        elif override == "disabled":
            return False
        elif override == "auto":
            # Auto-enable based on context size
            return context_size > self.auto_enable_threshold

        return self.optimization_enabled

    def _get_model_key(self, model_name: str) -> str:
        """Map model name to configuration key.

        Args:
            model_name: Name of the model

        Returns:
            Configuration key for the model type
        """
        model_lower = model_name.lower()

        if "gpt" in model_lower or "o3" in model_lower:
            return "gpt5"
        elif "claude" in model_lower:
            return "claude"
        elif "ollama" in model_lower or "llama" in model_lower:
            return "ollama"
        else:
            return "default"

    def get_literature_config(self) -> Dict[str, any]:
        """Get configuration for literature optimization.

        Returns:
            Literature optimization configuration
        """
        return {
            "enabled": self.literature_optimization,
            "max_papers": self.literature_max_papers,
            "confidence_threshold": self.confidence_threshold
        }

    def get_memory_config(self) -> Dict[str, any]:
        """Get configuration for memory optimization.

        Returns:
            Memory optimization configuration
        """
        return {
            "enabled": self.memory_optimization,
            "max_entries": self.memory_max_entries,
            "confidence_threshold": self.confidence_threshold
        }

    def get_validation_config(self) -> Dict[str, any]:
        """Get configuration for output validation.

        Returns:
            Output validation configuration
        """
        return {
            "enabled": self.output_validation,
            "confidence_threshold": self.confidence_threshold
        }