"""Unit tests for SafetyMiddleware."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, call
import pytest

from src.core.safety import SafetyConfig, SafetyLogger, SafetyCheck, SafetyLevel, SafetyMiddleware


class TestSafetyMiddleware:
    """Test suite for SafetyMiddleware."""
    
    @pytest.fixture
    def mock_safety_logger(self):
        """Create a mock SafetyLogger."""
        logger = MagicMock(spec=SafetyLogger)
        logger.log_research_goal = AsyncMock(return_value=SafetyCheck(
            decision=SafetyLevel.SAFE,
            safety_score=1.0,
            reasoning="Test logging"
        ))
        logger.log_hypothesis = AsyncMock(return_value=SafetyCheck(
            decision=SafetyLevel.SAFE,
            safety_score=1.0,
            reasoning="Test logging"
        ))
        return logger
    
    @pytest.fixture
    def safety_config(self):
        """Create a test SafetyConfig."""
        return SafetyConfig(
            enabled=True,
            trust_level="standard",
            log_only_mode=True
        )
    
    @pytest.fixture
    def middleware(self, safety_config, mock_safety_logger):
        """Create SafetyMiddleware with mocked logger."""
        middleware = SafetyMiddleware(safety_config)
        middleware.logger = mock_safety_logger
        return middleware
    
    @pytest.mark.asyncio
    async def test_middleware_initialization(self, safety_config):
        """Test that SafetyMiddleware initializes correctly."""
        middleware = SafetyMiddleware(safety_config)
        
        assert middleware.config == safety_config
        assert isinstance(middleware.logger, SafetyLogger)
        assert middleware.enabled == safety_config.enabled
    
    @pytest.mark.asyncio
    async def test_process_research_goal(self, middleware, mock_safety_logger):
        """Test processing a research goal through middleware."""
        goal = "Test research goal"
        context = {"domain": "test", "user_role": "researcher"}
        
        result = await middleware.process_research_goal(goal, context)
        
        assert result.decision == SafetyLevel.SAFE
        assert result.safety_score == 1.0
        mock_safety_logger.log_research_goal.assert_called_once_with(goal, context)
    
    @pytest.mark.asyncio
    async def test_process_hypothesis(self, middleware, mock_safety_logger):
        """Test processing a hypothesis through middleware."""
        hypothesis_data = {
            "content": "Test hypothesis",
            "id": "test-123",
            "type": "experimental"
        }
        
        result = await middleware.process_hypothesis(hypothesis_data)
        
        assert result.decision == SafetyLevel.SAFE
        assert result.safety_score == 1.0
        mock_safety_logger.log_hypothesis.assert_called_once_with(hypothesis_data)
    
    @pytest.mark.asyncio
    async def test_middleware_disabled(self, safety_config):
        """Test that middleware passes through when disabled."""
        safety_config.enabled = False
        middleware = SafetyMiddleware(safety_config)
        
        goal_result = await middleware.process_research_goal("Test", {})
        hyp_result = await middleware.process_hypothesis({"content": "Test"})
        
        assert goal_result.decision == SafetyLevel.SAFE
        assert goal_result.reasoning == "Safety middleware disabled"
        assert hyp_result.decision == SafetyLevel.SAFE
        assert hyp_result.reasoning == "Safety middleware disabled"
    
    @pytest.mark.asyncio
    async def test_wrap_async_function(self, middleware, mock_safety_logger):
        """Test wrapping an async function with safety logging."""
        async def test_function(goal: str, context: dict):
            return {"result": "success", "goal": goal}
        
        wrapped = middleware.wrap_research_goal_handler(test_function)
        
        result = await wrapped("Test goal", {"domain": "test"})
        
        assert result["result"] == "success"
        assert result["goal"] == "Test goal"
        mock_safety_logger.log_research_goal.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_wrap_function_with_exception(self, middleware, mock_safety_logger):
        """Test that wrapped function exceptions are propagated."""
        async def failing_function(goal: str, context: dict):
            raise ValueError("Test error")
        
        wrapped = middleware.wrap_research_goal_handler(failing_function)
        
        with pytest.raises(ValueError) as exc_info:
            await wrapped("Test goal", {"domain": "test"})
        
        assert str(exc_info.value) == "Test error"
        # Safety logging should still occur
        mock_safety_logger.log_research_goal.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_batch_process_hypotheses(self, middleware, mock_safety_logger):
        """Test batch processing of multiple hypotheses."""
        hypotheses = [
            {"content": "Hypothesis 1", "id": "1"},
            {"content": "Hypothesis 2", "id": "2"},
            {"content": "Hypothesis 3", "id": "3"}
        ]
        
        results = await middleware.batch_process_hypotheses(hypotheses)
        
        assert len(results) == 3
        assert all(r.decision == SafetyLevel.SAFE for r in results)
        assert mock_safety_logger.log_hypothesis.call_count == 3
    
    @pytest.mark.asyncio
    async def test_middleware_with_blocking_threshold(self, safety_config):
        """Test middleware behavior with blocking threshold."""
        safety_config.log_only_mode = False
        safety_config.blocking_threshold = 0.5
        
        middleware = SafetyMiddleware(safety_config)
        
        # Mock logger to return unsafe result
        middleware.logger.log_research_goal = AsyncMock(return_value=SafetyCheck(
            decision=SafetyLevel.UNSAFE,
            safety_score=0.3,
            reasoning="Below blocking threshold"
        ))
        
        result = await middleware.process_research_goal("Unsafe goal", {})
        
        assert result.decision == SafetyLevel.UNSAFE
        assert result.safety_score == 0.3
    
    @pytest.mark.asyncio
    async def test_decorator_usage(self, middleware):
        """Test using middleware as a decorator."""
        @middleware.log_research_goal
        async def handle_goal(goal: str, context: dict):
            return {"processed": goal}
        
        result = await handle_goal("Test goal", {"domain": "test"})
        
        assert result["processed"] == "Test goal"
        middleware.logger.log_research_goal.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_context_manager(self, middleware, mock_safety_logger):
        """Test using middleware as a context manager for batch operations."""
        async with middleware.batch_safety_context() as batch:
            batch.log_goal("Goal 1", {"domain": "test"})
            batch.log_goal("Goal 2", {"domain": "test"})
            batch.log_hypothesis({"content": "Hypothesis 1"})
        
        # Verify all operations were logged
        assert mock_safety_logger.log_research_goal.call_count == 2
        assert mock_safety_logger.log_hypothesis.call_count == 1
    
    def test_get_safety_status(self, middleware):
        """Test getting current safety status."""
        status = middleware.get_safety_status()
        
        assert "enabled" in status
        assert "trust_level" in status
        assert "log_only_mode" in status
        assert status["enabled"] is True
        assert status["trust_level"] == "standard"
        assert status["log_only_mode"] is True
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self, middleware, mock_safety_logger):
        """Test concurrent processing of multiple safety checks."""
        goals = [f"Goal {i}" for i in range(10)]
        
        # Process all goals concurrently
        tasks = [
            middleware.process_research_goal(goal, {"id": i})
            for i, goal in enumerate(goals)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert all(r.decision == SafetyLevel.SAFE for r in results)
        assert mock_safety_logger.log_research_goal.call_count == 10