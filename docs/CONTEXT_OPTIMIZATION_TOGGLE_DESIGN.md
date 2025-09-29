# Context Optimization Toggle Design

## Overview

This document defines the toggle mechanism for context optimization, allowing the system to be easily enabled/disabled based on context window size and model capabilities.

## Toggle Mechanisms

### 1. Environment Variables (Primary Control)

```bash
# Main toggle - controls all context optimization
CONTEXT_OPTIMIZATION_ENABLED=false  # Default: disabled

# Feature-specific toggles
LITERATURE_OPTIMIZATION_ENABLED=true   # Default: enabled if main toggle is true
MEMORY_OPTIMIZATION_ENABLED=true       # Default: enabled if main toggle is true
OUTPUT_VALIDATION_ENABLED=true         # Default: enabled if main toggle is true

# Thresholds for auto-activation
CONTEXT_OPTIMIZATION_AUTO_THRESHOLD=100000  # Auto-enable if context > 100k tokens
CONTEXT_OPTIMIZATION_CONFIDENCE_THRESHOLD=0.8  # Conservative default

# Model-specific settings
GPT5_CONTEXT_OPTIMIZATION=auto      # auto, enabled, disabled
CLAUDE_CONTEXT_OPTIMIZATION=auto    # auto, enabled, disabled
OLLAMA_CONTEXT_OPTIMIZATION=enabled # Local models benefit more
```

### 2. File-based Toggle (Override)

```bash
# Create to disable optimization completely
touch .context_optimization_disabled

# Create to enable optimization regardless of env vars
touch .context_optimization_enabled

# Create to use aggressive optimization
touch .context_optimization_aggressive
```

### 3. Configuration Class

```python
# src/config/context_optimization_config.py
from dataclasses import dataclass
from typing import Optional
import os
from pathlib import Path

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
    model_overrides: dict = None

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
        """Determine if optimization should be enabled for specific model."""

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
        """Map model name to configuration key."""
        model_lower = model_name.lower()

        if "gpt" in model_lower or "o3" in model_lower:
            return "gpt5"
        elif "claude" in model_lower:
            return "claude"
        elif "ollama" in model_lower or "llama" in model_lower:
            return "ollama"
        else:
            return "default"
```

### 4. Runtime Toggle API

```python
# src/utils/ace_fca_runtime.py
class ACEFCARuntimeControl:
    """Runtime control for ACE-FCA optimization."""

    def __init__(self):
        self._override_enabled = None
        self.config = ACEFCAConfig.from_environment()

    def enable_optimization(self, temporary: bool = True):
        """Enable optimization at runtime."""
        if temporary:
            self._override_enabled = True
        else:
            Path(".context_optimization_enabled").touch()
            self.config = ACEFCAConfig.from_environment()

    def disable_optimization(self, temporary: bool = True):
        """Disable optimization at runtime."""
        if temporary:
            self._override_enabled = False
        else:
            Path(".context_optimization_disabled").touch()
            self.config = ACEFCAConfig.from_environment()

    def is_enabled(self, model_name: str = None, context_size: int = 0) -> bool:
        """Check if optimization is currently enabled."""
        if self._override_enabled is not None:
            return self._override_enabled

        if model_name:
            return self.config.should_optimize_for_model(model_name, context_size)

        return self.config.optimization_enabled

    def get_metrics(self) -> dict:
        """Get current optimization metrics."""
        metrics_file = Path(".context_optimization_metrics.log")
        if not metrics_file.exists():
            return {"status": "no_metrics", "optimizations": 0}

        # Read last 10 lines for recent metrics
        with open(metrics_file) as f:
            lines = f.readlines()[-10:]

        return {
            "status": "active" if self.is_enabled() else "disabled",
            "recent_optimizations": len(lines),
            "last_optimization": lines[-1].strip() if lines else None
        }
```

## Usage Examples

### Basic Usage

```python
# In agent initialization
from src.config.ace_fca_config import ACEFCAConfig

class GenerationAgent:
    def __init__(self):
        self.ace_fca_config = ACEFCAConfig.from_environment()
        self.optimization_enabled = self.ace_fca_config.optimization_enabled

    async def generate_hypothesis(self, papers, context):
        if self.optimization_enabled and len(papers) > 8:
            # Use optimized context
            optimized_papers = self.optimize_literature_context(papers)
            return await self._generate_with_papers(optimized_papers, context)
        else:
            # Use full context
            return await self._generate_with_papers(papers, context)
```

### Model-Aware Usage

```python
# Check if optimization should be used for current model
config = ACEFCAConfig.from_environment()
model_name = os.getenv("DEFAULT_MODEL", "gpt5")
context_size = len(full_context)

if config.should_optimize_for_model(model_name, context_size):
    # Use optimization
    optimized_context = optimize_context(full_context)
else:
    # Use full context
    optimized_context = full_context
```

### Runtime Control

```python
# Enable optimization temporarily for testing
from src.utils.ace_fca_runtime import ACEFCARuntimeControl

control = ACEFCARuntimeControl()
control.enable_optimization(temporary=True)

# Run some operations...

control.disable_optimization(temporary=True)
```

## Integration with Existing Code

### Minimal Changes Required

1. **Add configuration loading** to agent `__init__` methods
2. **Add conditional logic** before context-heavy operations
3. **Add fallback mechanisms** when optimization fails
4. **Add metrics logging** for optimization effectiveness

### Backward Compatibility

- **Default disabled**: No behavior change unless explicitly enabled
- **Graceful fallback**: System continues if optimization fails
- **Complete disable**: File-based override disables all optimization
- **Existing APIs unchanged**: No breaking changes to agent interfaces

## Testing Strategy

### Environment Testing

```bash
# Test with optimization disabled (default)
pytest tests/

# Test with optimization enabled
CONTEXT_OPTIMIZATION_ENABLED=true pytest tests/

# Test with aggressive optimization
touch .context_optimization_aggressive
pytest tests/
rm .context_optimization_aggressive

# Test auto-threshold behavior
CONTEXT_OPTIMIZATION_AUTO_THRESHOLD=10 pytest tests/unit/test_generation_agent.py
```

### Model-Specific Testing

```bash
# Test GPT-5 with optimization
DEFAULT_MODEL=gpt5 GPT5_CONTEXT_OPTIMIZATION=enabled pytest tests/

# Test Claude without optimization
DEFAULT_MODEL=claudeopus41 CLAUDE_CONTEXT_OPTIMIZATION=disabled pytest tests/

# Test local models with automatic optimization
DEFAULT_MODEL=ollama pytest tests/
```

## Monitoring and Metrics

### Optimization Metrics File

```json
{
  "timestamp": "2025-09-29T10:30:00Z",
  "optimization_type": "literature_context",
  "agent_type": "generation",
  "model": "gpt5",
  "original_size": 15,
  "optimized_size": 8,
  "reduction_percent": 46.7,
  "confidence_score": 0.85,
  "fallback_used": false
}
```

### Status Checking

```bash
# Check current optimization status
python3 -c "from src.utils.ace_fca_runtime import ACEFCARuntimeControl; print(ACEFCARuntimeControl().get_metrics())"

# View recent optimization activity
tail -20 .context_optimization_metrics.log
```

## Rollback Instructions

### Complete Rollback to Checkpoint

```bash
# Return to pre-ACE-FCA state
git checkout checkpoint-before-ace-fca-phase1

# Or reset to checkpoint keeping changes
git reset --soft checkpoint-before-ace-fca-phase1
```

### Disable Without Rollback

```bash
# Disable via file (fastest)
touch .context_optimization_disabled

# Disable via environment
export CONTEXT_OPTIMIZATION_ENABLED=false

# Verify disabled
python3 -c "from src.config.ace_fca_config import ACEFCAConfig; print('Disabled' if not ACEFCAConfig.from_environment().optimization_enabled else 'Enabled')"
```

## Configuration Examples

### Development Setup (Minimal Optimization)

```bash
export CONTEXT_OPTIMIZATION_ENABLED=true
export CONTEXT_OPTIMIZATION_CONFIDENCE_THRESHOLD=0.9
export LITERATURE_MAX_PAPERS=10
export MEMORY_MAX_ENTRIES=12
```

### Production Setup (Balanced Optimization)

```bash
export CONTEXT_OPTIMIZATION_ENABLED=true
export CONTEXT_OPTIMIZATION_CONFIDENCE_THRESHOLD=0.8
export LITERATURE_MAX_PAPERS=8
export MEMORY_MAX_ENTRIES=10
export CONTEXT_OPTIMIZATION_AUTO_THRESHOLD=50000
```

### Research Setup (Aggressive Optimization)

```bash
export CONTEXT_OPTIMIZATION_ENABLED=true
export CONTEXT_OPTIMIZATION_CONFIDENCE_THRESHOLD=0.6
export LITERATURE_MAX_PAPERS=5
export MEMORY_MAX_ENTRIES=6
# Or simply: touch .context_optimization_aggressive
```

This toggle design ensures ACE-FCA optimization can be easily controlled, monitored, and rolled back while maintaining complete backward compatibility with existing code.