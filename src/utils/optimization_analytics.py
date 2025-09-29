"""
Context Optimization Analytics Module

Provides analytics and reporting for context optimization effectiveness in the development loop.
This module analyzes metrics from .context_optimization_metrics.log to provide insights into
optimization performance and recommendations for improvement.
"""

import csv
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

class ContextOptimizationAnalytics:
    """Analyzes context optimization effectiveness for the development loop."""

    def __init__(self, metrics_file: str = ".context_optimization_metrics.log"):
        self.metrics_file = metrics_file

    def load_metrics(self) -> Optional['pd.DataFrame']:
        """Load metrics from CSV log file."""
        if not PANDAS_AVAILABLE:
            return None

        try:
            if not os.path.exists(self.metrics_file):
                return None

            df = pd.read_csv(self.metrics_file)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except (FileNotFoundError, pd.errors.EmptyDataError):
            return None

    def load_metrics_basic(self) -> List[Dict[str, Any]]:
        """Load metrics without pandas (basic CSV parsing)."""
        try:
            if not os.path.exists(self.metrics_file):
                return []

            with open(self.metrics_file, 'r') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except (FileNotFoundError, OSError):
            return []

    def analyze_effectiveness(self) -> Dict[str, Any]:
        """Analyze context optimization effectiveness."""
        if PANDAS_AVAILABLE:
            df = self.load_metrics()
            if df is None or df.empty:
                return {"error": "No data available"}
            return self._analyze_with_pandas(df)
        else:
            data = self.load_metrics_basic()
            if not data:
                return {"error": "No data available"}
            return self._analyze_basic(data)

    def _analyze_with_pandas(self, df: 'pd.DataFrame') -> Dict[str, Any]:
        """Analyze effectiveness using pandas."""
        optimized = df[df['optimization_used'] == 'true']
        full_context = df[df['optimization_used'] == 'false']

        analysis = {
            "total_iterations": len(df),
            "optimization_usage_rate": len(optimized) / len(df) if len(df) > 0 else 0,
            "average_reduction": {},
            "by_phase": {}
        }

        # Calculate reduction ratios
        if len(optimized) > 0 and len(full_context) > 0:
            opt_avg_lines = optimized['line_count'].astype(int).mean()
            full_avg_lines = full_context['line_count'].astype(int).mean()
            opt_avg_specs = optimized['spec_count'].astype(int).mean()
            full_avg_specs = full_context['spec_count'].astype(int).mean()

            analysis["average_reduction"]["lines"] = opt_avg_lines / full_avg_lines if full_avg_lines > 0 else 1
            analysis["average_reduction"]["specs"] = opt_avg_specs / full_avg_specs if full_avg_specs > 0 else 1
        else:
            analysis["average_reduction"]["lines"] = 1
            analysis["average_reduction"]["specs"] = 1

        # Analyze by phase
        try:
            phase_analysis = df.groupby('task_phase').agg({
                'optimization_used': lambda x: (x == 'true').mean(),
                'line_count': lambda x: x.astype(int).mean(),
                'spec_count': lambda x: x.astype(int).mean()
            }).to_dict()
            analysis["by_phase"] = phase_analysis
        except Exception:
            analysis["by_phase"] = {}

        return analysis

    def _analyze_basic(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze effectiveness using basic Python (no pandas)."""
        optimized = [row for row in data if row.get('optimization_used') == 'true']
        full_context = [row for row in data if row.get('optimization_used') == 'false']

        analysis = {
            "total_iterations": len(data),
            "optimization_usage_rate": len(optimized) / len(data) if len(data) > 0 else 0,
            "average_reduction": {},
            "by_phase": {}
        }

        # Calculate reduction ratios
        if optimized and full_context:
            try:
                opt_avg_lines = sum(int(row.get('line_count', 0)) for row in optimized) / len(optimized)
                full_avg_lines = sum(int(row.get('line_count', 0)) for row in full_context) / len(full_context)
                opt_avg_specs = sum(int(row.get('spec_count', 0)) for row in optimized) / len(optimized)
                full_avg_specs = sum(int(row.get('spec_count', 0)) for row in full_context) / len(full_context)

                analysis["average_reduction"]["lines"] = opt_avg_lines / full_avg_lines if full_avg_lines > 0 else 1
                analysis["average_reduction"]["specs"] = opt_avg_specs / full_avg_specs if full_avg_specs > 0 else 1
            except (ValueError, ZeroDivisionError):
                analysis["average_reduction"]["lines"] = 1
                analysis["average_reduction"]["specs"] = 1
        else:
            analysis["average_reduction"]["lines"] = 1
            analysis["average_reduction"]["specs"] = 1

        # Analyze by phase (basic)
        phases = {}
        for row in data:
            phase = row.get('task_phase', 'unknown')
            if phase not in phases:
                phases[phase] = {'total': 0, 'optimized': 0, 'lines': [], 'specs': []}

            phases[phase]['total'] += 1
            if row.get('optimization_used') == 'true':
                phases[phase]['optimized'] += 1

            try:
                phases[phase]['lines'].append(int(row.get('line_count', 0)))
                phases[phase]['specs'].append(int(row.get('spec_count', 0)))
            except ValueError:
                pass

        phase_analysis = {}
        for phase, stats in phases.items():
            if stats['total'] > 0:
                phase_analysis[phase] = {
                    'optimization_used': stats['optimized'] / stats['total'],
                    'line_count': sum(stats['lines']) / len(stats['lines']) if stats['lines'] else 0,
                    'spec_count': sum(stats['specs']) / len(stats['specs']) if stats['specs'] else 0
                }

        analysis["by_phase"] = phase_analysis
        return analysis

    def generate_report(self) -> str:
        """Generate human-readable optimization report."""
        analysis = self.analyze_effectiveness()

        if "error" in analysis:
            return f"❌ {analysis['error']}"

        report = f"""📊 Context Optimization Effectiveness Report
============================================

📈 Usage Statistics:
  • Total iterations analyzed: {analysis['total_iterations']}
  • Optimization usage rate: {analysis['optimization_usage_rate']:.1%}

💾 Context Reduction:
  • Average line reduction: {(1 - analysis['average_reduction']['lines']):.1%}
  • Average spec reduction: {(1 - analysis['average_reduction']['specs']):.1%}
"""

        if analysis['by_phase']:
            report += "\n📋 By Phase Analysis:\n"
            for phase, metrics in analysis['by_phase'].items():
                if isinstance(metrics, dict) and 'optimization_used' in metrics:
                    report += f"  • Phase {phase}: {metrics['optimization_used']:.1%} optimization rate\n"

        # Add recommendations
        if analysis['optimization_usage_rate'] < 0.5:
            report += "\n💡 Recommendations:\n"
            report += "  • Consider reviewing fallback triggers - optimization usage is low\n"

        if analysis['average_reduction']['lines'] > 0.8:
            report += "\n⚠️  Warning:\n"
            report += "  • Low context reduction - optimization may not be effective\n"

        return report

    def get_latest_metrics(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get the latest N metrics entries."""
        data = self.load_metrics_basic()
        return data[-count:] if data else []

# CLI interface for easy access
if __name__ == "__main__":
    import sys

    analytics = ContextOptimizationAnalytics()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--report":
            print(analytics.generate_report())
        elif sys.argv[1] == "--latest":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            latest = analytics.get_latest_metrics(count)
            for entry in latest:
                print(f"Iteration {entry.get('iteration', '?')}: {entry.get('line_count', '?')} lines, optimization={entry.get('optimization_used', '?')}")
        elif sys.argv[1] == "--json":
            analysis = analytics.analyze_effectiveness()
            print(json.dumps(analysis, indent=2, default=str))
        else:
            print("Usage: python optimization_analytics.py [--report|--latest [N]|--json]")
    else:
        print(analytics.generate_report())