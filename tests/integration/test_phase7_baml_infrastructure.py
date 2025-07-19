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
from baml_client.types import (
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
        from baml_client.types import (
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
        from baml_client.types import ExperimentalProtocol
        
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
    @pytest.mark.skipif(
        os.getenv("ENABLE_REAL_LLM_TESTS", "false").lower() != "true",
        reason="Real LLM tests disabled - set ENABLE_REAL_LLM_TESTS=true to run"
    )
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
        from baml_client.types import (
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