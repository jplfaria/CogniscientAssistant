"""ACE-FCA Runtime Control for context optimization.

This module provides runtime control capabilities for the ACE-FCA context
optimization system, including dynamic enable/disable, metrics collection,
and status monitoring.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from src.config.ace_fca_config import ACEFCAConfig

logger = logging.getLogger(__name__)


class ACEFCARuntimeControl:
    """Runtime control for ACE-FCA optimization."""

    def __init__(self):
        """Initialize runtime control with current configuration."""
        self._override_enabled = None
        self.config = ACEFCAConfig.from_environment()
        self.metrics_file = Path(".context_optimization_metrics.log")

    def enable_optimization(self, temporary: bool = True):
        """Enable optimization at runtime.

        Args:
            temporary: If True, enable only for this session. If False,
                      create persistent file override.
        """
        if temporary:
            self._override_enabled = True
            logger.info("ACE-FCA optimization enabled temporarily for this session")
        else:
            Path(".context_optimization_enabled").touch()
            self.config = ACEFCAConfig.from_environment()
            logger.info("ACE-FCA optimization enabled persistently")

    def disable_optimization(self, temporary: bool = True):
        """Disable optimization at runtime.

        Args:
            temporary: If True, disable only for this session. If False,
                      create persistent file override.
        """
        if temporary:
            self._override_enabled = False
            logger.info("ACE-FCA optimization disabled temporarily for this session")
        else:
            Path(".context_optimization_disabled").touch()
            self.config = ACEFCAConfig.from_environment()
            logger.info("ACE-FCA optimization disabled persistently")

    def is_enabled(self, model_name: Optional[str] = None, context_size: int = 0) -> bool:
        """Check if optimization is currently enabled.

        Args:
            model_name: Optional model name for model-specific checks
            context_size: Optional context size for auto-threshold checks

        Returns:
            True if optimization should be enabled
        """
        # Check temporary override first
        if self._override_enabled is not None:
            return self._override_enabled

        # Check model-specific configuration if provided
        if model_name:
            return self.config.should_optimize_for_model(model_name, context_size)

        # Return general optimization status
        return self.config.optimization_enabled

    def get_metrics(self) -> Dict[str, Any]:
        """Get current optimization metrics.

        Returns:
            Dictionary containing optimization metrics and status
        """
        if not self.metrics_file.exists():
            return {
                "status": "no_metrics",
                "optimizations": 0,
                "enabled": self.is_enabled()
            }

        try:
            # Read last 10 lines for recent metrics
            with open(self.metrics_file, 'r') as f:
                lines = f.readlines()[-10:]

            recent_metrics = []
            for line in lines:
                try:
                    metric = json.loads(line.strip())
                    recent_metrics.append(metric)
                except json.JSONDecodeError:
                    continue

            # Aggregate metrics
            total_optimizations = len(recent_metrics)
            avg_reduction = 0.0
            avg_confidence = 0.0

            if recent_metrics:
                reductions = [m.get('reduction_percent', 0) for m in recent_metrics]
                confidences = [m.get('confidence_score', 0) for m in recent_metrics]

                avg_reduction = sum(reductions) / len(reductions)
                avg_confidence = sum(confidences) / len(confidences)

            return {
                "status": "active" if self.is_enabled() else "disabled",
                "recent_optimizations": total_optimizations,
                "average_reduction_percent": avg_reduction,
                "average_confidence": avg_confidence,
                "last_optimization": recent_metrics[-1] if recent_metrics else None,
                "enabled": self.is_enabled()
            }

        except Exception as e:
            logger.warning(f"Failed to read metrics file: {e}")
            return {
                "status": "error",
                "error": str(e),
                "enabled": self.is_enabled()
            }

    def log_optimization_metric(self, optimization_type: str, agent_type: str,
                               original_size: int, optimized_size: int,
                               confidence_score: float, fallback_used: bool = False,
                               model_name: Optional[str] = None):
        """Log an optimization metric.

        Args:
            optimization_type: Type of optimization (literature_context, memory_context, etc.)
            agent_type: Type of agent that used optimization
            original_size: Original context size
            optimized_size: Optimized context size
            confidence_score: Confidence score for the optimization
            fallback_used: Whether fallback to full context was used
            model_name: Optional model name used
        """
        # Calculate reduction percentage
        reduction_percent = 0.0
        if original_size > 0:
            reduction_percent = ((original_size - optimized_size) / original_size) * 100

        metric = {
            'timestamp': datetime.now().isoformat(),
            'optimization_type': optimization_type,
            'agent_type': agent_type,
            'model': model_name or 'unknown',
            'original_size': original_size,
            'optimized_size': optimized_size,
            'reduction_percent': reduction_percent,
            'confidence_score': confidence_score,
            'fallback_used': fallback_used
        }

        try:
            # Append metric to log file
            with open(self.metrics_file, 'a') as f:
                f.write(json.dumps(metric) + '\n')

            logger.debug(f"Logged {optimization_type} optimization: "
                        f"{original_size} -> {optimized_size} "
                        f"({reduction_percent:.1f}% reduction)")

        except Exception as e:
            logger.warning(f"Failed to log optimization metric: {e}")

    def get_status_report(self) -> str:
        """Generate a human-readable status report.

        Returns:
            Formatted status report string
        """
        metrics = self.get_metrics()

        report = "🎯 ACE-FCA Context Optimization Status\n"
        report += "=" * 40 + "\n\n"

        # Status
        status_emoji = "✅" if metrics["enabled"] else "❌"
        report += f"{status_emoji} Status: {'Enabled' if metrics['enabled'] else 'Disabled'}\n"

        if metrics["status"] == "no_metrics":
            report += "📊 No optimization metrics available yet\n"
            return report

        if metrics["status"] == "error":
            report += f"⚠️  Error reading metrics: {metrics['error']}\n"
            return report

        # Recent activity
        report += f"📈 Recent optimizations: {metrics['recent_optimizations']}\n"

        if metrics["recent_optimizations"] > 0:
            report += f"📉 Average reduction: {metrics['average_reduction_percent']:.1f}%\n"
            report += f"🎯 Average confidence: {metrics['average_confidence']:.2f}\n"

            if metrics["last_optimization"]:
                last = metrics["last_optimization"]
                report += f"\n🕒 Last optimization:\n"
                report += f"   Type: {last.get('optimization_type', 'unknown')}\n"
                report += f"   Agent: {last.get('agent_type', 'unknown')}\n"
                report += f"   Reduction: {last.get('reduction_percent', 0):.1f}%\n"
                report += f"   Time: {last.get('timestamp', 'unknown')}\n"

        # Configuration summary
        report += f"\n⚙️  Configuration:\n"
        report += f"   Literature max: {self.config.literature_max_papers} papers\n"
        report += f"   Memory max: {self.config.memory_max_entries} entries\n"
        report += f"   Confidence threshold: {self.config.confidence_threshold:.2f}\n"

        return report

    def cleanup_old_metrics(self, days_to_keep: int = 7):
        """Clean up old metrics files.

        Args:
            days_to_keep: Number of days of metrics to keep
        """
        if not self.metrics_file.exists():
            return

        try:
            cutoff_timestamp = datetime.now().timestamp() - (days_to_keep * 24 * 3600)

            with open(self.metrics_file, 'r') as f:
                lines = f.readlines()

            # Filter lines to keep only recent ones
            recent_lines = []
            for line in lines:
                try:
                    metric = json.loads(line.strip())
                    metric_time = datetime.fromisoformat(metric.get('timestamp', ''))
                    if metric_time.timestamp() > cutoff_timestamp:
                        recent_lines.append(line)
                except (json.JSONDecodeError, ValueError):
                    # Keep malformed lines for now
                    recent_lines.append(line)

            # Write back filtered metrics
            if len(recent_lines) < len(lines):
                with open(self.metrics_file, 'w') as f:
                    f.writelines(recent_lines)

                removed_count = len(lines) - len(recent_lines)
                logger.info(f"Cleaned up {removed_count} old metric entries")

        except Exception as e:
            logger.warning(f"Failed to cleanup old metrics: {e}")

    def get_optimization_effectiveness(self, agent_type: Optional[str] = None) -> Dict[str, float]:
        """Calculate optimization effectiveness metrics.

        Args:
            agent_type: Optional filter by agent type

        Returns:
            Dictionary with effectiveness metrics
        """
        if not self.metrics_file.exists():
            return {"effectiveness": 0.0, "sample_count": 0}

        try:
            with open(self.metrics_file, 'r') as f:
                lines = f.readlines()

            relevant_metrics = []
            for line in lines:
                try:
                    metric = json.loads(line.strip())
                    if not agent_type or metric.get('agent_type') == agent_type:
                        relevant_metrics.append(metric)
                except json.JSONDecodeError:
                    continue

            if not relevant_metrics:
                return {"effectiveness": 0.0, "sample_count": 0}

            # Calculate effectiveness based on:
            # 1. Average reduction achieved
            # 2. Average confidence maintained
            # 3. Fallback rate (lower is better)

            reductions = [m.get('reduction_percent', 0) for m in relevant_metrics]
            confidences = [m.get('confidence_score', 0) for m in relevant_metrics]
            fallbacks = [m.get('fallback_used', False) for m in relevant_metrics]

            avg_reduction = sum(reductions) / len(reductions)
            avg_confidence = sum(confidences) / len(confidences)
            fallback_rate = sum(fallbacks) / len(fallbacks)

            # Effectiveness score (0-1)
            # Balanced between reduction achieved and quality maintained
            reduction_score = min(avg_reduction / 50.0, 1.0)  # 50% reduction = 1.0
            confidence_score = avg_confidence
            fallback_penalty = fallback_rate * 0.3  # Penalty for fallbacks

            effectiveness = (reduction_score * 0.4 + confidence_score * 0.6) - fallback_penalty
            effectiveness = max(0.0, min(1.0, effectiveness))

            return {
                "effectiveness": effectiveness,
                "sample_count": len(relevant_metrics),
                "average_reduction": avg_reduction,
                "average_confidence": avg_confidence,
                "fallback_rate": fallback_rate
            }

        except Exception as e:
            logger.warning(f"Failed to calculate effectiveness: {e}")
            return {"effectiveness": 0.0, "sample_count": 0, "error": str(e)}

    def reset_configuration(self):
        """Reset configuration to environment defaults."""
        # Remove any file overrides
        for override_file in [".context_optimization_enabled",
                             ".context_optimization_disabled",
                             ".context_optimization_aggressive"]:
            path = Path(override_file)
            if path.exists():
                path.unlink()

        # Reset temporary overrides
        self._override_enabled = None

        # Reload configuration from environment
        self.config = ACEFCAConfig.from_environment()

        logger.info("ACE-FCA configuration reset to environment defaults")


class AgentContextMetrics:
    """Specialized metrics collection for agent context optimization."""

    def __init__(self):
        """Initialize metrics collector."""
        self.runtime_control = ACEFCARuntimeControl()

    def log_literature_optimization(self, agent_type: str,
                                  original_papers: int,
                                  optimized_papers: int,
                                  quality_score: float,
                                  model_name: Optional[str] = None):
        """Log literature context optimization metrics.

        Args:
            agent_type: Type of agent using optimization
            original_papers: Number of papers in original context
            optimized_papers: Number of papers after optimization
            quality_score: Quality/confidence score for optimization
            model_name: Optional model name
        """
        self.runtime_control.log_optimization_metric(
            optimization_type='literature_context',
            agent_type=agent_type,
            original_size=original_papers,
            optimized_size=optimized_papers,
            confidence_score=quality_score,
            model_name=model_name
        )

    def log_memory_optimization(self, agent_type: str,
                              original_memories: int,
                              optimized_memories: int,
                              quality_score: float,
                              model_name: Optional[str] = None):
        """Log memory context optimization metrics.

        Args:
            agent_type: Type of agent using optimization
            original_memories: Number of memories in original context
            optimized_memories: Number of memories after optimization
            quality_score: Quality/confidence score for optimization
            model_name: Optional model name
        """
        self.runtime_control.log_optimization_metric(
            optimization_type='memory_context',
            agent_type=agent_type,
            original_size=original_memories,
            optimized_size=optimized_memories,
            confidence_score=quality_score,
            model_name=model_name
        )

    def generate_agent_optimization_report(self) -> str:
        """Generate comprehensive agent optimization effectiveness report.

        Returns:
            Formatted report string
        """
        report = "📊 Agent Context Optimization Report\n"
        report += "=" * 40 + "\n\n"

        # Get metrics for different agent types
        agent_types = ['generation', 'reflection', 'ranking', 'evolution']

        for agent_type in agent_types:
            effectiveness = self.runtime_control.get_optimization_effectiveness(agent_type)

            if effectiveness['sample_count'] > 0:
                report += f"🤖 {agent_type.title()} Agent:\n"
                report += f"   Effectiveness: {effectiveness['effectiveness']:.2f}\n"
                report += f"   Average reduction: {effectiveness['average_reduction']:.1f}%\n"
                report += f"   Average confidence: {effectiveness['average_confidence']:.2f}\n"
                report += f"   Fallback rate: {effectiveness['fallback_rate']:.1%}\n"
                report += f"   Samples: {effectiveness['sample_count']}\n\n"

        # Overall summary
        overall_effectiveness = self.runtime_control.get_optimization_effectiveness()
        if overall_effectiveness['sample_count'] > 0:
            report += f"📈 Overall System:\n"
            report += f"   Effectiveness: {overall_effectiveness['effectiveness']:.2f}\n"
            report += f"   Total optimizations: {overall_effectiveness['sample_count']}\n"
            report += f"   System-wide reduction: {overall_effectiveness['average_reduction']:.1f}%\n"

        return report