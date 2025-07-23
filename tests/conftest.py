"""Shared test configuration and fixtures."""

import sys
from unittest.mock import MagicMock, AsyncMock

# Mock BAML client to avoid import errors during testing
def pytest_configure(config):
    """Configure pytest - runs before tests."""
    # Create mock for baml_client
    mock_baml_client = MagicMock()
    
    # Create a mock b with async methods
    mock_b = MagicMock()
    
    # Mock the specific async methods with default return values
    # Create a mock hypothesis return value
    mock_hypothesis = MagicMock()
    mock_hypothesis.id = "test-hypothesis-123"
    mock_hypothesis.summary = "Test hypothesis for KIRA6 inhibition of IRE1α in AML treatment"
    mock_hypothesis.category = "therapeutic"
    mock_hypothesis.full_description = "KIRA6 selectively inhibits IRE1α kinase activity to reduce ER stress in AML cells"
    mock_hypothesis.novelty_claim = "Novel use of KIRA6 as repurposed drug for AML"
    mock_hypothesis.assumptions = ["IRE1α is overactive in AML cells", "KIRA6 can penetrate cell membranes"]
    mock_hypothesis.reasoning = "Based on literature showing increased ER stress in AML"
    mock_hypothesis.confidence_score = 0.85
    mock_hypothesis.generation_method = "literature_based"
    mock_hypothesis.created_at = "2024-01-01T00:00:00Z"
    
    # Create mock experimental protocol
    mock_protocol = MagicMock()
    mock_protocol.objective = "Test KIRA6 efficacy in AML cell lines"
    mock_protocol.methodology = "In vitro testing with AML cell lines"
    mock_protocol.required_resources = ["KIRA6 compound", "AML cell lines", "Cell culture facilities"]
    mock_protocol.timeline = "6 months"
    mock_protocol.success_metrics = ["Cell viability reduction", "IRE1α activity measurement"]
    mock_protocol.potential_challenges = ["Drug solubility", "Cell line variability"]
    mock_protocol.safety_considerations = ["BSL-2 safety protocols", "Chemical handling procedures"]
    
    mock_hypothesis.experimental_protocol = mock_protocol
    mock_hypothesis.supporting_evidence = []
    
    # Set up the mock to return this hypothesis
    mock_b.GenerateHypothesis = AsyncMock(return_value=mock_hypothesis)
    mock_b.EvaluateHypothesis = AsyncMock()
    mock_b.PerformSafetyCheck = AsyncMock()
    mock_b.CompareHypotheses = AsyncMock()
    mock_b.EnhanceHypothesis = AsyncMock()
    mock_b.CalculateSimilarity = AsyncMock()
    mock_b.ExtractResearchPatterns = AsyncMock()
    mock_b.ParseResearchGoal = AsyncMock()
    
    # Add future BAML functions that will be needed in upcoming phases
    # Phase 9-10: Supervisor and Generation
    mock_b.PlanResearchStrategy = AsyncMock()
    mock_b.DetermineTaskPriority = AsyncMock()
    mock_b.ConductScientificDebate = AsyncMock()
    mock_b.AnalyzeLiteratureForHypothesis = AsyncMock()
    
    # Phase 11: Reflection
    mock_b.PerformQuickReview = AsyncMock()
    mock_b.SimulateExperimentalMechanism = AsyncMock()
    
    # Phase 15: Meta-Review
    mock_b.GenerateAgentFeedback = AsyncMock()
    mock_b.FormatResearchOverview = AsyncMock()
    
    # Phase 16: Natural Language Interface
    mock_b.InterpretUserFeedback = AsyncMock()
    mock_b.SummarizeResearchProgress = AsyncMock()
    
    # Create nested baml_client module for the actual import path
    mock_baml_client.baml_client = MagicMock()
    mock_baml_client.baml_client.b = mock_b
    
    # Mock type definitions with proper class structure
    mock_types = MagicMock()
    
    # Create mock classes for BAML types
    mock_types.Hypothesis = type('Hypothesis', (), {})
    mock_types.SafetyCheck = type('SafetyCheck', (), {})
    mock_types.ParsedResearchGoal = type('ParsedResearchGoal', (), {})
    mock_types.AgentRequest = type('AgentRequest', (), {})
    mock_types.AgentResponse = type('AgentResponse', (), {})
    mock_types.AgentType = MagicMock()
    mock_types.AgentType.Generation = "Generation"
    mock_types.AgentType.Reflection = "Reflection"
    mock_types.AgentType.Ranking = "Ranking"
    mock_types.AgentType.Evolution = "Evolution"
    mock_types.AgentType.Proximity = "Proximity"
    mock_types.AgentType.MetaReview = "MetaReview"
    mock_types.ComparisonResult = type('ComparisonResult', (), {})
    mock_types.Pattern = type('Pattern', (), {})
    mock_types.ResearchTopic = type('ResearchTopic', (), {})
    mock_types.SimilarityResult = type('SimilarityResult', (), {})
    mock_types.Review = type('Review', (), {})
    mock_types.ReviewType = MagicMock()
    mock_types.ReviewType.Initial = "Initial"
    mock_types.ReviewType.Deep = "Deep"
    mock_types.ReviewType.Observation = "Observation"
    mock_types.ReviewType.Simulation = "Simulation"
    mock_types.ReviewType.Tournament = "Tournament"
    mock_types.ExperimentalProtocol = type('ExperimentalProtocol', (), {})
    
    mock_baml_client.baml_client.types = mock_types
    
    # Register all the mock modules
    sys.modules['baml_client'] = mock_baml_client
    sys.modules['baml_client.baml_client'] = mock_baml_client.baml_client
    sys.modules['baml_client.baml_client.types'] = mock_types
    sys.modules['baml_client.types'] = mock_types