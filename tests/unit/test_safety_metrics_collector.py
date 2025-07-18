"""Tests for SafetyMetricsCollector."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List
from unittest.mock import MagicMock, patch

import pytest

from src.core.safety import SafetyConfig, SafetyLevel, SafetyCheck, SafetyMetricsCollector


class TestSafetyMetricsCollector:
    """Test cases for SafetyMetricsCollector."""
    
    @pytest.fixture
    def config(self, tmp_path):
        """Create a test configuration."""
        return SafetyConfig(
            enabled=True,
            trust_level="standard",
            log_directory=tmp_path / "safety_logs"
        )
    
    @pytest.fixture
    def collector(self, config):
        """Create a SafetyMetricsCollector instance."""
        return SafetyMetricsCollector(config)
    
    def test_initialization(self, collector, config):
        """Test metrics collector initialization."""
        assert collector.config == config
        # Metrics should be initialized with structure, not empty
        assert "safety_checks" in collector.metrics
        assert "pattern_alerts" in collector.metrics
        assert collector.metrics["safety_checks"]["total"] == 0
        assert collector.metrics["pattern_alerts"]["total"] == 0
        assert collector._start_time is not None
    
    def test_record_safety_check(self, collector):
        """Test recording a safety check."""
        check = SafetyCheck(
            decision=SafetyLevel.SAFE,
            safety_score=0.95,
            reasoning="Test check"
        )
        
        collector.record_safety_check("research_goal", check)
        
        assert "safety_checks" in collector.metrics
        assert collector.metrics["safety_checks"]["total"] == 1
        assert collector.metrics["safety_checks"]["by_type"]["research_goal"] == 1
        assert collector.metrics["safety_checks"]["by_decision"]["safe"] == 1
    
    def test_record_multiple_checks(self, collector):
        """Test recording multiple safety checks."""
        checks = [
            SafetyCheck(SafetyLevel.SAFE, 0.95, "Safe check"),
            SafetyCheck(SafetyLevel.UNSAFE, 0.2, "Unsafe check"),
            SafetyCheck(SafetyLevel.REVIEW_REQUIRED, 0.6, "Review needed"),
            SafetyCheck(SafetyLevel.SAFE, 0.9, "Another safe check")
        ]
        
        for i, check in enumerate(checks):
            check_type = "research_goal" if i % 2 == 0 else "hypothesis"
            collector.record_safety_check(check_type, check)
        
        assert collector.metrics["safety_checks"]["total"] == 4
        assert collector.metrics["safety_checks"]["by_decision"]["safe"] == 2
        assert collector.metrics["safety_checks"]["by_decision"]["unsafe"] == 1
        assert collector.metrics["safety_checks"]["by_decision"]["review_required"] == 1
        assert collector.metrics["safety_checks"]["by_type"]["research_goal"] == 2
        assert collector.metrics["safety_checks"]["by_type"]["hypothesis"] == 2
    
    def test_record_pattern_alert(self, collector):
        """Test recording pattern alerts."""
        collector.record_pattern_alert("dual_use_concern", "high")
        collector.record_pattern_alert("biohazard_risk", "medium")
        collector.record_pattern_alert("dual_use_concern", "low")
        
        assert collector.metrics["pattern_alerts"]["total"] == 3
        assert collector.metrics["pattern_alerts"]["by_pattern"]["dual_use_concern"] == 2
        assert collector.metrics["pattern_alerts"]["by_pattern"]["biohazard_risk"] == 1
        assert collector.metrics["pattern_alerts"]["by_severity"]["high"] == 1
        assert collector.metrics["pattern_alerts"]["by_severity"]["medium"] == 1
        assert collector.metrics["pattern_alerts"]["by_severity"]["low"] == 1
    
    def test_calculate_safety_score_average(self, collector):
        """Test calculating average safety score."""
        checks = [
            SafetyCheck(SafetyLevel.SAFE, 0.9, "Check 1"),
            SafetyCheck(SafetyLevel.SAFE, 0.8, "Check 2"),
            SafetyCheck(SafetyLevel.REVIEW_REQUIRED, 0.6, "Check 3"),
            SafetyCheck(SafetyLevel.UNSAFE, 0.2, "Check 4")
        ]
        
        for check in checks:
            collector.record_safety_check("test", check)
        
        avg_score = collector.get_average_safety_score()
        assert avg_score == pytest.approx(0.625, rel=1e-3)
    
    def test_get_metrics_summary(self, collector):
        """Test getting a metrics summary."""
        # Record some checks and alerts
        for i in range(5):
            check = SafetyCheck(
                SafetyLevel.SAFE if i % 2 == 0 else SafetyLevel.REVIEW_REQUIRED,
                0.8 if i % 2 == 0 else 0.5,
                f"Check {i}"
            )
            collector.record_safety_check("research_goal", check)
        
        collector.record_pattern_alert("test_pattern", "medium")
        
        summary = collector.get_metrics_summary()
        
        assert summary["total_safety_checks"] == 5
        # 3 checks with 0.8 and 2 checks with 0.5: (3*0.8 + 2*0.5) / 5 = 0.68
        assert summary["average_safety_score"] == pytest.approx(0.68, rel=1e-2)
        assert summary["total_pattern_alerts"] == 1
        assert summary["uptime_seconds"] > 0
        assert "metrics_by_type" in summary
        assert "metrics_by_decision" in summary
    
    def test_get_hourly_metrics(self, collector):
        """Test getting hourly metrics."""
        # Record checks at different times
        base_time = datetime.now(timezone.utc)
        
        with patch('src.core.safety.datetime') as mock_datetime:
            # First hour
            mock_datetime.now.return_value = base_time
            for _ in range(3):
                check = SafetyCheck(SafetyLevel.SAFE, 0.9, "Hour 1 check")
                collector.record_safety_check("research_goal", check)
            
            # Second hour
            mock_datetime.now.return_value = base_time + timedelta(hours=1)
            for _ in range(2):
                check = SafetyCheck(SafetyLevel.REVIEW_REQUIRED, 0.6, "Hour 2 check")
                collector.record_safety_check("hypothesis", check)
        
        hourly = collector.get_hourly_metrics()
        assert len(hourly) == 2
        assert hourly[0]["count"] == 3
        assert hourly[1]["count"] == 2
    
    def test_reset_metrics(self, collector):
        """Test resetting metrics."""
        # Add some metrics
        collector.record_safety_check("test", SafetyCheck(SafetyLevel.SAFE, 0.9, "Test"))
        collector.record_pattern_alert("test_pattern", "low")
        
        assert collector.metrics["safety_checks"]["total"] > 0
        assert collector.metrics["pattern_alerts"]["total"] > 0
        
        # Reset
        collector.reset_metrics()
        
        # Metrics should be reset to initial structure, not empty
        assert collector.metrics["safety_checks"]["total"] == 0
        assert collector.metrics["pattern_alerts"]["total"] == 0
        assert collector.metrics["safety_checks"]["safety_scores"] == []
    
    def test_export_metrics(self, collector, tmp_path):
        """Test exporting metrics to file."""
        # Add some metrics
        for i in range(3):
            check = SafetyCheck(SafetyLevel.SAFE, 0.9, f"Check {i}")
            collector.record_safety_check("test", check)
        
        export_path = tmp_path / "metrics_export.json"
        collector.export_metrics(export_path)
        
        assert export_path.exists()
        
        # Verify contents
        import json
        with open(export_path) as f:
            exported = json.load(f)
        
        assert exported["total_safety_checks"] == 3
        assert "timestamp" in exported
        assert "metrics" in exported
    
    def test_concurrent_metrics_recording(self, collector):
        """Test thread-safe concurrent metrics recording."""
        import threading
        
        def record_checks():
            for i in range(10):
                check = SafetyCheck(SafetyLevel.SAFE, 0.9, f"Check {i}")
                collector.record_safety_check("concurrent", check)
        
        def record_alerts():
            for i in range(10):
                collector.record_pattern_alert(f"pattern_{i % 3}", "medium")
        
        # Run concurrent operations
        thread1 = threading.Thread(target=record_checks)
        thread2 = threading.Thread(target=record_alerts)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        assert collector.metrics["safety_checks"]["total"] == 10
        assert collector.metrics["pattern_alerts"]["total"] == 10
    
    def test_metrics_with_disabled_safety(self):
        """Test metrics collector when safety is disabled."""
        config = SafetyConfig(enabled=False)
        collector = SafetyMetricsCollector(config)
        
        # Should still record metrics even when safety is disabled
        check = SafetyCheck(SafetyLevel.SAFE, 0.9, "Test")
        collector.record_safety_check("test", check)
        
        assert collector.metrics["safety_checks"]["total"] == 1
    
    def test_get_metrics_by_time_range(self, collector):
        """Test getting metrics for a specific time range."""
        base_time = datetime.now(timezone.utc)
        
        # Record checks at different times
        with patch('src.core.safety.datetime') as mock_datetime:
            for i in range(10):
                mock_datetime.now.return_value = base_time + timedelta(minutes=i*10)
                check = SafetyCheck(SafetyLevel.SAFE, 0.9, f"Check {i}")
                collector.record_safety_check("test", check)
        
        # Get metrics for the last 30 minutes
        start_time = base_time + timedelta(minutes=30)
        end_time = base_time + timedelta(minutes=60)
        
        metrics = collector.get_metrics_by_time_range(start_time, end_time)
        
        # Should include checks from minutes 30-60 (4 checks)
        assert metrics["total_checks_in_range"] == 4
    
    def test_alert_thresholds(self, collector):
        """Test automatic alerts based on thresholds."""
        # Configure alert thresholds
        collector.set_alert_threshold("unsafe_rate", 0.3)  # Alert if >30% unsafe
        
        # Record mostly safe checks
        for _ in range(7):
            collector.record_safety_check("test", SafetyCheck(SafetyLevel.SAFE, 0.9, "Safe"))
        
        # No alert yet
        alerts = collector.get_active_alerts()
        assert len(alerts) == 0
        
        # Add unsafe checks to exceed threshold
        for _ in range(3):
            collector.record_safety_check("test", SafetyCheck(SafetyLevel.UNSAFE, 0.1, "Unsafe"))
        
        # Should trigger alert
        alerts = collector.get_active_alerts()
        assert len(alerts) == 1
        assert alerts[0]["type"] == "unsafe_rate"
        assert alerts[0]["current_value"] == 0.3