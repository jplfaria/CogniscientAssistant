"""Unit tests for Argo health check monitoring."""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import pytest

from src.llm.argo_provider import ArgoLLMProvider, ArgoConnectionError


class TestArgoHealthMonitor:
    """Test Argo health monitoring functionality."""
    
    @pytest.fixture
    def argo_provider(self):
        """Create an ArgoLLMProvider instance."""
        with patch.dict('os.environ', {
            'ARGO_PROXY_URL': 'http://localhost:8000/v1',
            'ARGO_AUTH_USER': 'test_user'
        }):
            return ArgoLLMProvider()
    
    @pytest.mark.asyncio
    async def test_health_monitor_initialization(self, argo_provider):
        """Test health monitor initialization."""
        # Health monitor should not be started by default
        assert argo_provider._health_monitor_task is None
        
        # Start health monitoring
        await argo_provider.start_health_monitoring(interval=5)
        
        # Verify monitor task is created
        assert argo_provider._health_monitor_task is not None
        assert isinstance(argo_provider._health_monitor_task, asyncio.Task)
        assert not argo_provider._health_monitor_task.done()
        
        # Stop monitoring
        await argo_provider.stop_health_monitoring()
        assert argo_provider._health_monitor_task is None
    
    @pytest.mark.asyncio
    async def test_health_monitor_periodic_checks(self, argo_provider):
        """Test that health monitor performs periodic checks."""
        check_count = 0
        health_statuses = []
        
        async def mock_get_health_status():
            nonlocal check_count
            check_count += 1
            status = {
                "status": "healthy" if check_count < 3 else "degraded",
                "timestamp": datetime.now().isoformat(),
                "check_number": check_count
            }
            health_statuses.append(status)
            return status
        
        argo_provider.get_health_status = mock_get_health_status
        
        # Start monitoring with short interval
        await argo_provider.start_health_monitoring(interval=0.1)
        
        # Wait for multiple checks
        await asyncio.sleep(0.35)
        
        # Stop monitoring
        await argo_provider.stop_health_monitoring()
        
        # Verify multiple checks were performed
        assert check_count >= 3
        assert len(health_statuses) >= 3
        
        # Verify status changed was detected
        assert health_statuses[0]["status"] == "healthy"
        assert health_statuses[-1]["status"] == "degraded"
    
    @pytest.mark.asyncio
    async def test_health_monitor_updates_model_availability(self, argo_provider):
        """Test that health monitor updates model availability based on health."""
        health_responses = [
            {
                "status": "healthy",
                "models": {
                    "gpt4o": {"status": "available"},
                    "claudeopus4": {"status": "available"},
                    "gemini25pro": {"status": "available"}
                }
            },
            {
                "status": "degraded",
                "models": {
                    "gpt4o": {"status": "available"},
                    "claudeopus4": {"status": "unavailable", "reason": "capacity"},
                    "gemini25pro": {"status": "available"}
                }
            }
        ]
        
        response_index = 0
        
        async def mock_get_health_status():
            nonlocal response_index
            response = health_responses[response_index % len(health_responses)]
            response_index += 1
            return response
        
        argo_provider.get_health_status = mock_get_health_status
        
        # Ensure claudeopus4 is initially available
        argo_provider.model_selector.mark_model_available("claudeopus4")
        available_models = argo_provider.model_selector.get_available_models()
        assert "claudeopus4" in available_models
        
        # Start monitoring
        await argo_provider.start_health_monitoring(interval=0.1)
        
        # Wait for exactly 2 health checks (at 0.1s intervals)
        # First check at ~0s, second check at ~0.1s
        await asyncio.sleep(0.15)
        
        # Stop monitoring
        await argo_provider.stop_health_monitoring()
        
        # Verify model was marked unavailable
        available_models = argo_provider.model_selector.get_available_models()
        assert "claudeopus4" not in available_models
        # These models should remain available
        if "gpt4o" in argo_provider.model_selector.model_costs:
            assert "gpt4o" in available_models
        if "gemini25pro" in argo_provider.model_selector.model_costs:
            assert "gemini25pro" in available_models
    
    @pytest.mark.asyncio
    async def test_health_monitor_handles_errors(self, argo_provider):
        """Test that health monitor handles errors gracefully."""
        error_count = 0
        
        async def mock_get_health_status():
            nonlocal error_count
            error_count += 1
            if error_count % 2 == 0:
                raise ArgoConnectionError("Connection failed")
            return {"status": "healthy"}
        
        argo_provider.get_health_status = mock_get_health_status
        
        # Start monitoring
        await argo_provider.start_health_monitoring(interval=0.1)
        
        # Wait for multiple checks
        await asyncio.sleep(0.35)
        
        # Stop monitoring
        await argo_provider.stop_health_monitoring()
        
        # Verify monitor continued despite errors
        assert error_count >= 3
    
    @pytest.mark.asyncio
    async def test_health_monitor_callback_integration(self, argo_provider):
        """Test health monitor with status change callbacks."""
        status_changes = []
        
        def on_status_change(old_status, new_status):
            status_changes.append({
                "old": old_status,
                "new": new_status,
                "timestamp": datetime.now()
            })
        
        health_responses = [
            {"status": "healthy"},
            {"status": "healthy"},
            {"status": "degraded"},
            {"status": "unhealthy"},
            {"status": "healthy"}
        ]
        
        response_index = 0
        
        async def mock_get_health_status():
            nonlocal response_index
            response = health_responses[response_index % len(health_responses)]
            response_index += 1
            return response
        
        argo_provider.get_health_status = mock_get_health_status
        
        # Start monitoring with callback
        await argo_provider.start_health_monitoring(
            interval=0.1,
            on_status_change=on_status_change
        )
        
        # Wait for status changes
        await asyncio.sleep(0.55)
        
        # Stop monitoring
        await argo_provider.stop_health_monitoring()
        
        # Verify status changes were detected
        assert len(status_changes) >= 3
        
        # Verify correct transitions
        assert any(change["old"] == "healthy" and change["new"] == "degraded" 
                  for change in status_changes)
        assert any(change["old"] == "degraded" and change["new"] == "unhealthy" 
                  for change in status_changes)
    
    @pytest.mark.asyncio
    async def test_health_monitor_circuit_breaker_integration(self, argo_provider):
        """Test health monitor resets circuit breakers when health improves."""
        # Simulate circuit breaker open for a model
        argo_provider._circuit_breakers["gpt4o"].record_failure()
        argo_provider._circuit_breakers["gpt4o"].record_failure()
        argo_provider._circuit_breakers["gpt4o"].record_failure()
        
        # Verify circuit is open
        assert argo_provider._circuit_breakers["gpt4o"].is_open()
        
        # Mock healthy status
        async def mock_get_health_status():
            return {
                "status": "healthy",
                "models": {
                    "gpt4o": {"status": "available"},
                    "claudeopus4": {"status": "available"}
                }
            }
        
        argo_provider.get_health_status = mock_get_health_status
        
        # Start monitoring
        await argo_provider.start_health_monitoring(interval=0.1)
        
        # Wait for health check
        await asyncio.sleep(0.15)
        
        # Stop monitoring  
        await argo_provider.stop_health_monitoring()
        
        # Verify circuit breaker was reset
        assert not argo_provider._circuit_breakers["gpt4o"].is_open()
    
    @pytest.mark.asyncio
    async def test_get_health_summary(self, argo_provider):
        """Test getting health summary information."""
        # Set up some health history
        argo_provider._health_history = [
            {"status": "healthy", "timestamp": datetime.now() - timedelta(minutes=5)},
            {"status": "degraded", "timestamp": datetime.now() - timedelta(minutes=3)},
            {"status": "healthy", "timestamp": datetime.now() - timedelta(minutes=1)}
        ]
        argo_provider._last_health_status = {"status": "healthy"}
        argo_provider._health_check_count = 10
        argo_provider._health_error_count = 2
        
        summary = argo_provider.get_health_summary()
        
        assert summary["current_status"] == "healthy"
        assert summary["total_checks"] == 10
        assert summary["error_count"] == 2
        assert summary["error_rate"] == 0.2
        assert summary["uptime_percentage"] > 0
        assert "last_status_change" in summary
        assert "monitoring_active" in summary