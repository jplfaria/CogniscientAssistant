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
    
    # Set up the mock to return different hypotheses based on input
    def generate_hypothesis_side_effect(*args, **kwargs):
        # Check generation method in kwargs
        generation_method = kwargs.get('generation_method', '')
        goal = kwargs.get('goal', '')
        constraints = kwargs.get('constraints', [])
        
        # Check if this is for debate generation
        if generation_method == 'debate' or 'debate' in str(kwargs):
            debate_hypothesis = MagicMock()
            debate_hypothesis.id = "debate-hypothesis-123"
            debate_hypothesis.summary = "Hypothesis about whale communication synthesized from 3 debate perspectives"
            debate_hypothesis.category = "theoretical"
            debate_hypothesis.full_description = "Novel theory on whale communication patterns"
            debate_hypothesis.novelty_claim = "Whales use communication for complex social structures"
            debate_hypothesis.assumptions = ["Whales have complex social needs", "Communication patterns are learnable"]
            debate_hypothesis.reasoning = "Synthesized from debate perspectives"
            debate_hypothesis.confidence_score = 0.75
            debate_hypothesis.generation_method = "simulated_debate"
            debate_hypothesis.created_at = "2024-01-01T00:00:00Z"
            debate_hypothesis.experimental_protocol = mock_protocol
            debate_hypothesis.supporting_evidence = []
            return debate_hypothesis
        
        # Check if this is for natural/plant constraints
        elif any('natural' in str(c).lower() or 'plant' in str(c).lower() for c in constraints):
            natural_hypothesis = MagicMock()
            natural_hypothesis.id = "natural-hypothesis-123"
            natural_hypothesis.summary = "Hypothesis addressing: Find treatments using only natural compounds"
            natural_hypothesis.category = "therapeutic"
            natural_hypothesis.full_description = "Using natural plant compounds to treat disease"
            natural_hypothesis.novelty_claim = "Novel use of natural compounds"
            natural_hypothesis.assumptions = ["Natural compounds are safer", "Plant-based treatments are effective"]
            natural_hypothesis.reasoning = "Based on traditional medicine"
            natural_hypothesis.confidence_score = 0.80
            natural_hypothesis.generation_method = "assumption_based"
            natural_hypothesis.created_at = "2024-01-01T00:00:00Z"
            natural_hypothesis.experimental_protocol = mock_protocol
            natural_hypothesis.supporting_evidence = []
            return natural_hypothesis
        
        # Check if this is for literature-based with citations
        elif generation_method == 'literature_based':
            lit_hypothesis = MagicMock()
            lit_hypothesis.id = "lit-hypothesis-123"
            lit_hypothesis.summary = "Test hypothesis for KIRA6 inhibition of IRE1α in AML treatment"
            lit_hypothesis.category = "therapeutic"
            lit_hypothesis.full_description = "KIRA6 selectively inhibits IRE1α kinase activity"
            lit_hypothesis.novelty_claim = "Novel use of KIRA6 for AML"
            lit_hypothesis.assumptions = ["IRE1α is overactive in AML"]
            lit_hypothesis.reasoning = "Based on literature"
            lit_hypothesis.confidence_score = 0.85
            lit_hypothesis.generation_method = "literature_based"
            lit_hypothesis.created_at = "2024-01-01T00:00:00Z"
            lit_hypothesis.experimental_protocol = mock_protocol
            lit_hypothesis.supporting_evidence = [{"doi": "10.1234/test", "citation": "Test et al., 2024"}]
            return lit_hypothesis
        
        # Default hypothesis
        return mock_hypothesis
    
    mock_b.GenerateHypothesis = AsyncMock(side_effect=generate_hypothesis_side_effect)
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
    
    # Create mock classes for BAML types that accept arguments
    class MockBAMLType:
        def __init__(self, **kwargs):
            # Store all kwargs as attributes
            self._data = kwargs
            for k, v in kwargs.items():
                setattr(self, k, v)
        
        def __getattr__(self, name):
            # If attribute exists in _data, return it
            if hasattr(self, '_data') and name in self._data:
                return self._data[name]
            # Otherwise return a mock
            mock = MagicMock()
            # Store it so subsequent accesses return the same mock
            setattr(self, name, mock)
            return mock
    
    mock_types.Hypothesis = MockBAMLType
    mock_types.SafetyCheck = MockBAMLType
    mock_types.ParsedResearchGoal = MockBAMLType
    mock_types.AgentRequest = MockBAMLType
    mock_types.AgentResponse = MockBAMLType
    
    # Create enum-like objects for AgentType
    class MockEnumValue:
        def __init__(self, value):
            self.value = value
    
    mock_types.AgentType = MagicMock()
    mock_types.AgentType.Generation = MockEnumValue("Generation")
    mock_types.AgentType.Reflection = MockEnumValue("Reflection")
    mock_types.AgentType.Ranking = MockEnumValue("Ranking")
    mock_types.AgentType.Evolution = MockEnumValue("Evolution")
    mock_types.AgentType.Proximity = MockEnumValue("Proximity")
    mock_types.AgentType.MetaReview = MockEnumValue("MetaReview")
    mock_types.ComparisonResult = MockBAMLType
    mock_types.Pattern = MockBAMLType
    mock_types.ResearchTopic = MockBAMLType
    mock_types.SimilarityResult = MockBAMLType
    mock_types.Review = MockBAMLType
    
    # Create enum-like objects for ReviewType
    mock_types.ReviewType = MagicMock()
    mock_types.ReviewType.Initial = MockEnumValue("Initial")
    mock_types.ReviewType.Deep = MockEnumValue("Deep")
    mock_types.ReviewType.Observation = MockEnumValue("Observation")
    mock_types.ReviewType.Simulation = MockEnumValue("Simulation")
    mock_types.ReviewType.Tournament = MockEnumValue("Tournament")
    
    mock_types.ExperimentalProtocol = MockBAMLType
    
    # Add missing types that tests are trying to use with spec
    mock_types.SimilarityScore = MockBAMLType
    mock_types.ResearchPatterns = MockBAMLType
    mock_types.Task = MockBAMLType
    mock_types.Citation = MockBAMLType
    mock_types.ReviewScores = MockBAMLType
    mock_types.AssumptionDecomposition = MockBAMLType
    mock_types.FailurePoint = MockBAMLType
    mock_types.SimulationResults = MockBAMLType
    mock_types.RequestContent = MockBAMLType
    mock_types.RequestType = MagicMock()
    mock_types.RequestType.Generate = MockEnumValue("Generate")
    
    # Add missing enums
    mock_types.SafetyLevel = MagicMock()
    mock_types.SafetyLevel.Safe = MockEnumValue("Safe")
    mock_types.SafetyLevel.Concerning = MockEnumValue("Concerning")
    mock_types.SafetyLevel.Dangerous = MockEnumValue("Dangerous")
    
    mock_types.HypothesisCategory = MagicMock()
    mock_types.HypothesisCategory.Therapeutic = MockEnumValue("Therapeutic")
    mock_types.HypothesisCategory.Observational = MockEnumValue("Observational")
    mock_types.HypothesisCategory.Theoretical = MockEnumValue("Theoretical")
    
    mock_types.ReviewDecision = MagicMock()
    mock_types.ReviewDecision.Accept = MockEnumValue("Accept")
    mock_types.ReviewDecision.Reject = MockEnumValue("Reject")
    mock_types.ReviewDecision.Revise = MockEnumValue("Revise")
    
    mock_baml_client.baml_client.types = mock_types
    
    # Register all the mock modules
    sys.modules['baml_client'] = mock_baml_client
    sys.modules['baml_client.baml_client'] = mock_baml_client.baml_client
    sys.modules['baml_client.baml_client.types'] = mock_types
    sys.modules['baml_client.types'] = mock_types