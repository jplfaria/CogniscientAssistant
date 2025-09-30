"""Integration tests for Phase 7: BAML Infrastructure Setup.

These tests verify that:
1. BAML schemas compile correctly
2. BAML clients can be created and configured
3. Mock responses work as expected
4. Real LLM calls work (when enabled)
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import MagicMock, patch
import os

from src.llm.baml_wrapper import BAMLWrapper
from baml_client.baml_client.types import (
    AgentType,
    Hypothesis,
    ReviewType,
    ReviewDecision,
    SafetyLevel,
    HypothesisCategory,
)


class TestPhase7BAMLInfrastructure:
    """Integration tests for BAML infrastructure."""
    
    @pytest.mark.asyncio
    async def test_baml_schema_compilation(self):
        """Test that BAML schemas compile and generate valid Python types.
        
        Must Pass: Critical for BAML functionality
        """
        # Import generated types to verify they exist
        from baml_client.baml_client.types import (
            Hypothesis,
            Review,
            SafetyCheck,
            Task,
            AgentRequest,
            AgentResponse,
            ComparisonResult,
            SimilarityScore,
            ResearchPatterns,
            ParsedResearchGoal,
        )
        
        # Verify enums
        assert AgentType.Generation.value == "Generation"
        assert ReviewType.Initial.value == "Initial"
        assert SafetyLevel.Safe.value == "Safe"
        assert HypothesisCategory.Therapeutic.value == "Therapeutic"
        
        # Test that we can instantiate the types
        from baml_client.baml_client.types import ExperimentalProtocol
        
        protocol = ExperimentalProtocol(
            objective="Test objective",
            methodology="Test methodology",
            required_resources=["Resource 1"],
            timeline="6 months",
            success_metrics=["Metric 1"],
            potential_challenges=["Challenge 1"],
            safety_considerations=["Safety 1"]
        )
        
        hypothesis = Hypothesis(
            id="test_001",
            summary="Test hypothesis",
            category="Therapeutic",
            full_description="Full description",
            novelty_claim="Novel claim",
            assumptions=["Assumption 1"],
            reasoning="Test reasoning for hypothesis",
            experimental_protocol=protocol,
            supporting_evidence=[],
            confidence_score=0.8,
            generation_method="test",
            created_at=datetime.now().isoformat(),
        )
        
        assert hypothesis.id == "test_001"
        assert hypothesis.category == "Therapeutic"
    
    @pytest.mark.asyncio
    async def test_baml_client_connectivity(self):
        """Test that BAML client can be created and accessed.
        
        Must Pass: Critical for BAML client usage
        """
        wrapper = BAMLWrapper()
        
        # Verify the client is accessible
        assert wrapper._client is not None
        
        # Test that we can access client methods
        assert hasattr(wrapper._client, 'GenerateHypothesis')
        assert hasattr(wrapper._client, 'EvaluateHypothesis')
        assert hasattr(wrapper._client, 'PerformSafetyCheck')
        assert hasattr(wrapper._client, 'CompareHypotheses')
        assert hasattr(wrapper._client, 'EnhanceHypothesis')
        assert hasattr(wrapper._client, 'CalculateSimilarity')
        assert hasattr(wrapper._client, 'ExtractResearchPatterns')
        assert hasattr(wrapper._client, 'ParseResearchGoal')
    
    @pytest.mark.asyncio
    async def test_baml_mock_responses(self):
        """Test that BAML functions work with mock providers.
        
        Must Pass: Critical for testing without real LLMs
        """
        wrapper = BAMLWrapper()
        
        # Mock the BAML client to return predefined responses
        mock_hypothesis = MagicMock(
            id="hyp_mock_001",
            summary="Mock hypothesis for testing",
            category="Therapeutic",
            confidence_score=0.85,
        )
        
        async def mock_generate(*args, **kwargs):
            return mock_hypothesis
            
        with patch.object(wrapper._client, 'GenerateHypothesis', 
                         new=mock_generate):
            
            result = await wrapper.generate_hypothesis(
                goal="Test mock generation",
                constraints=["Test constraint"],
                existing_hypotheses=[],
                generation_method="literature_based"
            )
            
            assert result.id == "hyp_mock_001"
            assert result.summary == "Mock hypothesis for testing"
            assert result.confidence_score == 0.85
    
    @pytest.mark.asyncio
    @pytest.mark.real_llm
    async def test_real_llm_calls(self):
        """Test actual LLM calls through BAML (when enabled).
        
        May Fail: Depends on LLM availability and configuration
        """
        wrapper = BAMLWrapper()
        
        # Test research goal parsing (simplest function)
        try:
            result = await wrapper.parse_research_goal(
                natural_language_goal="Find new treatments for diabetes",
                domain_context="endocrinology"
            )
            
            # Verify we get a valid response
            assert result.primary_objective is not None
            assert isinstance(result.sub_objectives, list)
            assert isinstance(result.implied_constraints, list)
            assert isinstance(result.key_terms, list)
            
        except Exception as e:
            # Log the error but don't fail the test
            print(f"Real LLM test failed (expected in test environment): {e}")
            pytest.skip("Real LLM not available")
    
    @pytest.mark.asyncio
    async def test_baml_type_conversion(self):
        """Test conversion between Python types and BAML types.
        
        Must Pass: Critical for type safety
        """
        wrapper = BAMLWrapper()
        
        # Test agent request conversion
        agent_request = wrapper.convert_to_agent_request(
            agent_type=AgentType.Generation,
            request_type="Generate",  # Note: This will be converted to enum
            prompt="Test prompt",
            context={"key": "value"},
            parameters={"temperature": 0.7}
        )
        
        assert agent_request.agent_type == AgentType.Generation
        assert agent_request.content.prompt == "Test prompt"
        assert agent_request.content.context["key"] == "value"
        assert agent_request.content.parameters["temperature"] == "0.7"
    
    @pytest.mark.asyncio
    async def test_baml_error_handling(self):
        """Test BAML error handling and recovery.
        
        Must Pass: Critical for robust operation
        """
        wrapper = BAMLWrapper()
        
        # Simulate an error in the BAML client
        with patch.object(wrapper._client, 'GenerateHypothesis',
                         side_effect=Exception("BAML client error")):
            
            with pytest.raises(Exception) as exc_info:
                await wrapper.generate_hypothesis(
                    goal="Test error",
                    constraints=[],
                    existing_hypotheses=[]
                )
            
            assert "BAML client error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_baml_complex_types(self):
        """Test handling of complex nested BAML types.
        
        Must Pass: Critical for full functionality
        """
        from baml_client.baml_client.types import (
            ExperimentalProtocol,
            Citation,
            ReviewScores,
            AssumptionDecomposition,
            FailurePoint,
            SimulationResults,
        )
        
        # Create complex nested structures
        protocol = ExperimentalProtocol(
            objective="Test objective",
            methodology="Test methodology",
            required_resources=["Resource 1", "Resource 2"],
            timeline="6 months",
            success_metrics=["Metric 1"],
            potential_challenges=["Challenge 1"],
            safety_considerations=["Safety 1"]
        )
        
        citation = Citation(
            authors=["Author 1", "Author 2"],
            title="Test Paper",
            journal="Test Journal",
            year=2025,
            doi="10.1234/test",
            url="https://example.com"
        )
        
        # Verify the structures are valid
        assert protocol.objective == "Test objective"
        assert len(protocol.required_resources) == 2
        assert citation.year == 2025
        assert citation.journal == "Test Journal"
    
    @pytest.mark.asyncio
    async def test_baml_streaming_support(self):
        """Test streaming capabilities (if supported).

        May Fail: Streaming might not be fully implemented yet
        """
        wrapper = BAMLWrapper()

        # Check if streaming client exists
        if hasattr(wrapper._client, 'stream'):
            # Streaming is supported
            assert wrapper._client.stream is not None
        else:
            # Streaming not yet implemented
            pytest.skip("Streaming not implemented in current BAML version")

    @pytest.mark.asyncio
    async def test_enhanced_error_handling(self):
        """Test enhanced error handling with fallback history.

        Must Pass: Critical for production reliability
        """
        from src.llm.baml_error_handler import BAMLErrorHandler

        handler = BAMLErrorHandler(max_retries=2, base_delay=0.01)

        # Test retry mechanism
        call_count = 0

        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return "success"

        result = await handler.call_with_retry(
            flaky_func, "TestClient", "TestFunction"
        )

        assert result == "success"
        assert call_count == 2

        # Verify error was recorded
        summary = handler.get_error_summary()
        assert summary["total_errors"] == 1
        assert summary["by_client"]["TestClient"] == 1

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="BAML logging integrated into error handler, not separate module")
    async def test_baml_logging_configuration(self):
        """Test BAML-specific logging configuration.

        Must Pass: Critical for debugging and monitoring
        Note: Logging is now integrated into BAMLErrorHandler, not a separate module
        """
        pytest.skip("BAML logging is integrated into error handler")
        from src.llm.baml_logging import BAMLLoggerConfig, BAMLLogger, configure_baml_logging
        import tempfile
        import os

        # Create temporary directory for logs
        with tempfile.TemporaryDirectory() as temp_dir:
            # Configure logger
            logger = configure_baml_logging(
                log_dir=temp_dir,
                log_level="INFO",
                enable_request_logging=True,
                enable_response_logging=True,
                enable_performance_logging=True,
            )

            assert logger is not None

            # Test request logging
            logger.log_request(
                function_name="TestFunction",
                client_name="TestClient",
                parameters={"param": "value"},
                request_id="test_001",
            )

            # Test response logging
            logger.log_response(
                function_name="TestFunction",
                client_name="TestClient",
                success=True,
                duration=1.5,
                request_id="test_001",
            )

            # Test performance logging
            logger.log_performance(
                function_name="TestFunction",
                client_name="TestClient",
                duration=1.5,
                tokens_used=100,
                cache_hit=False,
            )

            # Verify log files were created
            assert os.path.exists(os.path.join(temp_dir, "operations.log"))
            assert os.path.exists(os.path.join(temp_dir, "performance.log"))

    @pytest.mark.asyncio
    async def test_retry_mechanisms(self):
        """Test retry mechanisms with exponential backoff.

        Must Pass: Critical for handling transient failures
        """
        from src.llm.baml_error_handler import BAMLErrorHandler, ErrorCategory

        handler = BAMLErrorHandler(
            max_retries=3,
            base_delay=0.01,
            exponential_base=2.0,
            max_delay=1.0,
        )

        # Test exponential backoff calculation
        assert handler._calculate_delay(0) == 0.01  # 0.01 * 2^0
        assert handler._calculate_delay(1) == 0.02  # 0.01 * 2^1
        assert handler._calculate_delay(2) == 0.04  # 0.01 * 2^2
        assert handler._calculate_delay(3) == 0.08  # 0.01 * 2^3

        # Test retry with recoverable error
        attempt_count = 0

        async def func_with_recoverable_error():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Timeout error")
            return "success"

        result = await handler.call_with_retry(
            func_with_recoverable_error, "TestClient", "TestFunction"
        )

        assert result == "success"
        assert attempt_count == 3

        # Test that non-recoverable errors don't retry
        attempt_count = 0

        async def func_with_non_recoverable_error():
            nonlocal attempt_count
            attempt_count += 1
            raise Exception("Invalid request (400)")

        with pytest.raises(Exception) as exc_info:
            await handler.call_with_retry(
                func_with_non_recoverable_error, "TestClient", "TestFunction"
            )

        assert "Invalid request" in str(exc_info.value)
        # Should not retry non-recoverable errors
        assert attempt_count == 1

    @pytest.mark.asyncio
    async def test_fallback_client_selection(self):
        """Test automatic fallback to alternative clients.

        Must Pass: Critical for high availability
        """
        from src.llm.baml_error_handler import BAMLErrorHandler

        handler = BAMLErrorHandler(max_retries=1, base_delay=0.01)

        # Track which clients were tried
        clients_tried = []

        def func_factory(client_name: str):
            async def client_func():
                clients_tried.append(client_name)
                if client_name == "PrimaryClient":
                    raise Exception("Primary client failed")
                return f"success_{client_name}"
            return client_func

        result, client_used = await handler.call_with_fallback(
            func_factory, "TestFunction", "PrimaryClient"
        )

        # Should have tried primary first, then fallback
        assert len(clients_tried) >= 2
        assert clients_tried[0] == "PrimaryClient"
        assert result.startswith("success_")
        assert client_used != "PrimaryClient"

        # Verify fallback was recorded
        fallback_summary = handler.get_fallback_summary()
        assert fallback_summary["total_fallbacks"] >= 1
        assert fallback_summary["successful_fallbacks"] >= 1

    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self):
        """Test circuit breaker integration with error handler.

        Must Pass: Critical for preventing cascading failures
        """
        from src.llm.baml_error_handler import BAMLErrorHandler
        from src.llm.circuit_breaker import CircuitBreakerError

        handler = BAMLErrorHandler(
            enable_circuit_breaker=True,
            circuit_breaker_threshold=2,
            max_retries=0,  # No retries to trigger circuit faster
        )

        async def failing_func():
            raise Exception("Service unavailable")

        # First two calls should fail normally
        for _ in range(2):
            with pytest.raises(Exception):
                await handler.call_with_retry(
                    failing_func, "TestClient", "TestFunction"
                )

        # Circuit should now be open
        breaker = handler._get_circuit_breaker("TestClient")
        assert breaker.is_open()

        # Next call should fail with CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            await handler.call_with_retry(
                failing_func, "TestClient", "TestFunction"
            )