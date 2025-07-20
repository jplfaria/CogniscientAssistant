"""Unit tests for the BAML wrapper integration."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.llm.baml_wrapper import BAMLWrapper
from baml_client.types import (
    AgentType,
    ComparisonResult,
    Hypothesis,
    ParsedResearchGoal,
    RequestType,
    ResearchPatterns,
    Review,
    ReviewType,
    ReviewDecision,
    SafetyCheck,
    SafetyLevel,
    SimilarityScore,
)


@pytest.fixture
def mock_hypothesis():
    """Create a mock hypothesis for testing."""
    return MagicMock(spec=Hypothesis, 
        id="hyp_001",
        summary="Test hypothesis",
        category="Therapeutic",
        full_description="Full description",
        novelty_claim="Novel claim",
        assumptions=["Assumption 1"],
        confidence_score=0.8,
        generation_method="literature_based",
        created_at=datetime.now().isoformat(),
    )


@pytest.fixture
def mock_review():
    """Create a mock review for testing."""
    return MagicMock(spec=Review,
        id="rev_001",
        hypothesis_id="hyp_001",
        reviewer_agent_id="agent_001",
        review_type=ReviewType.Initial,
        decision=ReviewDecision.Accept,
        narrative_feedback="Good hypothesis",
        key_strengths=["Strong evidence"],
        key_weaknesses=["Limited scope"],
        improvement_suggestions=["Expand scope"],
        confidence_level="High",
        created_at=datetime.now().isoformat(),
    )


@pytest.fixture
def baml_wrapper():
    """Create a BAML wrapper instance."""
    return BAMLWrapper()


class TestBAMLWrapper:
    """Test the BAML wrapper functionality."""
    
    @pytest.mark.asyncio
    async def test_generate_hypothesis(self, baml_wrapper):
        """Test hypothesis generation."""
        # Mock the BAML client
        mock_result = MagicMock(spec=Hypothesis, id="hyp_new")
        with patch.object(baml_wrapper._client, 'GenerateHypothesis', 
                         new_callable=AsyncMock, return_value=mock_result):
            
            result = await baml_wrapper.generate_hypothesis(
                goal="Test goal",
                constraints=["Constraint 1"],
                existing_hypotheses=[],
                generation_method="literature_based"
            )
            
            assert result.id == "hyp_new"
            baml_wrapper._client.GenerateHypothesis.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_evaluate_hypothesis(self, baml_wrapper, mock_hypothesis):
        """Test hypothesis evaluation."""
        mock_result = MagicMock(spec=Review, id="rev_new")
        with patch.object(baml_wrapper._client, 'EvaluateHypothesis',
                         new_callable=AsyncMock, return_value=mock_result):
            
            result = await baml_wrapper.evaluate_hypothesis(
                hypothesis=mock_hypothesis,
                review_type=ReviewType.Initial,
                evaluation_criteria=["Scientific merit"]
            )
            
            assert result.id == "rev_new"
            baml_wrapper._client.EvaluateHypothesis.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_perform_safety_check(self, baml_wrapper):
        """Test safety check functionality."""
        mock_result = MagicMock(spec=SafetyCheck, 
                               safety_level=SafetyLevel.Safe,
                               passed=True)
        with patch.object(baml_wrapper._client, 'PerformSafetyCheck',
                         new_callable=AsyncMock, return_value=mock_result):
            
            result = await baml_wrapper.perform_safety_check(
                target_type="hypothesis",
                target_content="Test content",
                trust_level="medium",
                safety_criteria=["No harm"]
            )
            
            assert result.safety_level == SafetyLevel.Safe
            assert result.passed is True
    
    @pytest.mark.asyncio
    async def test_compare_hypotheses(self, baml_wrapper, mock_hypothesis):
        """Test hypothesis comparison."""
        mock_result = MagicMock(spec=ComparisonResult,
                               winner_id="hyp_001",
                               confidence=0.85,
                               reasoning="Better evidence")
        with patch.object(baml_wrapper._client, 'CompareHypotheses',
                         new_callable=AsyncMock, return_value=mock_result):
            
            hypothesis2 = MagicMock(spec=Hypothesis, id="hyp_002")
            result = await baml_wrapper.compare_hypotheses(
                hypothesis1=mock_hypothesis,
                hypothesis2=hypothesis2,
                comparison_criteria=["Evidence quality"]
            )
            
            assert result.winner_id == "hyp_001"
            assert result.confidence == 0.85
    
    @pytest.mark.asyncio
    async def test_enhance_hypothesis(self, baml_wrapper, mock_hypothesis):
        """Test hypothesis enhancement."""
        mock_result = MagicMock(spec=Hypothesis, id="hyp_enhanced")
        with patch.object(baml_wrapper._client, 'EnhanceHypothesis',
                         new_callable=AsyncMock, return_value=mock_result):
            
            result = await baml_wrapper.enhance_hypothesis(
                original_hypothesis=mock_hypothesis,
                enhancement_strategy="refine",
                feedback=["Improve clarity"]
            )
            
            assert result.id == "hyp_enhanced"
    
    @pytest.mark.asyncio
    async def test_calculate_similarity(self, baml_wrapper, mock_hypothesis):
        """Test similarity calculation."""
        mock_result = MagicMock(spec=SimilarityScore,
                               overall_similarity=0.75,
                               shared_concepts=["Concept 1"])
        with patch.object(baml_wrapper._client, 'CalculateSimilarity',
                         new_callable=AsyncMock, return_value=mock_result):
            
            hypothesis2 = MagicMock(spec=Hypothesis, id="hyp_002")
            result = await baml_wrapper.calculate_similarity(
                hypothesis1=mock_hypothesis,
                hypothesis2=hypothesis2,
                similarity_aspects=["mechanism"]
            )
            
            assert result.overall_similarity == 0.75
            assert "Concept 1" in result.shared_concepts
    
    @pytest.mark.asyncio
    async def test_extract_research_patterns(self, baml_wrapper, mock_hypothesis, mock_review):
        """Test pattern extraction."""
        mock_result = MagicMock(spec=ResearchPatterns,
                               identified_patterns=["Pattern 1"],
                               recommendations=["Recommendation 1"])
        with patch.object(baml_wrapper._client, 'ExtractResearchPatterns',
                         new_callable=AsyncMock, return_value=mock_result):
            
            result = await baml_wrapper.extract_research_patterns(
                hypotheses=[mock_hypothesis],
                reviews=[mock_review],
                focus="methodology"
            )
            
            assert "Pattern 1" in result.identified_patterns
            assert "Recommendation 1" in result.recommendations
    
    @pytest.mark.asyncio
    async def test_parse_research_goal(self, baml_wrapper):
        """Test research goal parsing."""
        mock_result = MagicMock(spec=ParsedResearchGoal,
                               primary_objective="Find cure",
                               sub_objectives=["Identify targets"])
        with patch.object(baml_wrapper._client, 'ParseResearchGoal',
                         new_callable=AsyncMock, return_value=mock_result):
            
            result = await baml_wrapper.parse_research_goal(
                natural_language_goal="Find a cure for cancer",
                domain_context="oncology"
            )
            
            assert result.primary_objective == "Find cure"
            assert "Identify targets" in result.sub_objectives
    
    def test_convert_to_agent_request(self, baml_wrapper):
        """Test conversion to agent request format."""
        result = baml_wrapper.convert_to_agent_request(
            agent_type=AgentType.Generation,
            request_type=RequestType.Generate,
            prompt="Generate hypothesis",
            context={"goal": "Test goal"},
            parameters={"max_length": 1000}
        )
        
        assert result.agent_type == AgentType.Generation
        assert result.request_type == RequestType.Generate
        assert result.content.prompt == "Generate hypothesis"
        assert result.content.context["goal"] == "Test goal"
        assert result.content.parameters["max_length"] == "1000"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, baml_wrapper):
        """Test error handling in wrapper methods."""
        with patch.object(baml_wrapper._client, 'GenerateHypothesis',
                         side_effect=Exception("API Error")):
            
            with pytest.raises(Exception) as exc_info:
                await baml_wrapper.generate_hypothesis(
                    goal="Test",
                    constraints=[],
                    existing_hypotheses=[]
                )
            
            assert "API Error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_evaluate_hypothesis_error_handling(self, baml_wrapper, mock_hypothesis):
        """Test error handling in evaluate_hypothesis."""
        with patch.object(baml_wrapper._client, 'EvaluateHypothesis',
                         side_effect=Exception("Evaluation Error")):
            
            with pytest.raises(Exception) as exc_info:
                await baml_wrapper.evaluate_hypothesis(
                    hypothesis=mock_hypothesis,
                    review_type=ReviewType.Initial,
                    evaluation_criteria=["scientific_merit", "feasibility"],
                    context={"goal": "Test goal"}
                )
            
            assert "Evaluation Error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_perform_safety_check_error_handling(self, baml_wrapper):
        """Test error handling in perform_safety_check."""
        with patch.object(baml_wrapper._client, 'PerformSafetyCheck',
                         side_effect=Exception("Safety Check Error")):
            
            with pytest.raises(Exception) as exc_info:
                await baml_wrapper.perform_safety_check(
                    target_type="hypothesis",
                    target_content="Test content",
                    trust_level="high",
                    safety_criteria=["ethical", "safe"]
                )
            
            assert "Safety Check Error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_compare_hypotheses_error_handling(self, baml_wrapper, mock_hypothesis):
        """Test error handling in compare_hypotheses."""
        with patch.object(baml_wrapper._client, 'CompareHypotheses',
                         side_effect=Exception("Comparison Error")):
            
            with pytest.raises(Exception) as exc_info:
                await baml_wrapper.compare_hypotheses(
                    hypothesis1=mock_hypothesis,
                    hypothesis2=mock_hypothesis,
                    comparison_criteria=["novelty", "impact"],
                    debate_context="Test context"
                )
            
            assert "Comparison Error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_parse_research_goal_error_handling(self, baml_wrapper):
        """Test error handling in parse_research_goal."""
        with patch.object(baml_wrapper._client, 'ParseResearchGoal',
                         side_effect=Exception("Parse Error")):
            
            with pytest.raises(Exception) as exc_info:
                await baml_wrapper.parse_research_goal(
                    natural_language_goal="Test goal",
                    domain_context="Test context"
                )
            
            assert "Parse Error" in str(exc_info.value)