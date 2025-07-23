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
    
    # Mock the specific async methods
    mock_b.GenerateHypothesis = AsyncMock()
    mock_b.EvaluateHypothesis = AsyncMock()
    mock_b.PerformSafetyCheck = AsyncMock()
    mock_b.CompareHypotheses = AsyncMock()
    mock_b.EnhanceHypothesis = AsyncMock()
    mock_b.CalculateSimilarity = AsyncMock()
    mock_b.ExtractResearchPatterns = AsyncMock()
    mock_b.ParseResearchGoal = AsyncMock()
    
    mock_baml_client.b = mock_b
    sys.modules['baml_client'] = mock_baml_client
    sys.modules['baml_client.types'] = MagicMock()