"""Tests for BAML Review schema."""

import os
from pathlib import Path
import pytest
from typing import Dict, Any


class TestBAMLReviewSchema:
    """Test BAML Review schema definitions."""
    
    def test_review_schema_exists(self):
        """Test that Review schema is defined in models.baml."""
        models_path = Path("baml_src/models.baml")
        assert models_path.exists(), "models.baml should exist"
        
        content = models_path.read_text()
        assert "class Review" in content, "Review class should be defined"
        
    def test_review_type_enum_exists(self):
        """Test that ReviewType enum is defined."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        assert "enum ReviewType" in content, "ReviewType enum should be defined"
        
        review_types = [
            "initial",
            "full",
            "deep_verification",
            "observation",
            "simulation",
            "tournament",
        ]
        
        enum_section = self._extract_enum_section(content, "ReviewType")
        
        for review_type in review_types:
            assert review_type in enum_section, f"ReviewType should contain '{review_type}'"
            
    def test_review_decision_enum_exists(self):
        """Test that ReviewDecision enum is defined."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        assert "enum ReviewDecision" in content, "ReviewDecision enum should be defined"
        
        decisions = [
            "accept",
            "reject", 
            "revise",
        ]
        
        enum_section = self._extract_enum_section(content, "ReviewDecision")
        
        for decision in decisions:
            assert decision in enum_section, f"ReviewDecision should contain '{decision}'"
            
    def test_review_scores_schema_exists(self):
        """Test that ReviewScores schema is defined."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        assert "class ReviewScores" in content, "ReviewScores class should be defined"
        
        required_fields = [
            "correctness float",
            "quality float",
            "novelty float",
            "safety float",
            "feasibility float",
        ]
        
        scores_section = self._extract_class_section(content, "ReviewScores")
        
        for field in required_fields:
            assert field in scores_section, f"ReviewScores schema should contain '{field}'"
            
    def test_assumption_decomposition_schema_exists(self):
        """Test that AssumptionDecomposition schema is defined."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        assert "class AssumptionDecomposition" in content, "AssumptionDecomposition class should be defined"
        
        required_fields = [
            "assumption string",
            "validity string",
            "evidence string",
            "criticality string",
        ]
        
        decomp_section = self._extract_class_section(content, "AssumptionDecomposition")
        
        for field in required_fields:
            assert field in decomp_section, f"AssumptionDecomposition schema should contain '{field}'"
            
    def test_failure_point_schema_exists(self):
        """Test that FailurePoint schema is defined."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        assert "class FailurePoint" in content, "FailurePoint class should be defined"
        
        required_fields = [
            "step string",
            "probability float",
            "impact string",
        ]
        
        failure_section = self._extract_class_section(content, "FailurePoint")
        
        for field in required_fields:
            assert field in failure_section, f"FailurePoint schema should contain '{field}'"
            
    def test_simulation_results_schema_exists(self):
        """Test that SimulationResults schema is defined."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        assert "class SimulationResults" in content, "SimulationResults class should be defined"
        
        required_fields = [
            "mechanism_steps string[]",
            "failure_points FailurePoint[]",
            "predicted_outcomes string[]",
        ]
        
        sim_section = self._extract_class_section(content, "SimulationResults")
        
        for field in required_fields:
            assert field in sim_section, f"SimulationResults schema should contain '{field}'"
            
    def test_review_schema_fields(self):
        """Test that Review schema has all required fields."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        # Required fields from the Python model
        required_fields = [
            "id string",
            "hypothesis_id string",
            "reviewer_agent_id string",
            "review_type ReviewType",
            "decision ReviewDecision",
            "scores ReviewScores",
            "narrative_feedback string",
            "key_strengths string[]",
            "key_weaknesses string[]",
            "improvement_suggestions string[]",
            "confidence_level string",
            "created_at string",
        ]
        
        review_section = self._extract_class_section(content, "Review")
        
        for field in required_fields:
            assert field in review_section, f"Review schema should contain '{field}'"
            
    def test_review_optional_fields(self):
        """Test that optional fields are properly marked."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        # Optional fields from Review model
        optional_fields = [
            "assumption_decomposition AssumptionDecomposition[]?",
            "simulation_results SimulationResults?",
            "literature_citations Citation[]?",
            "time_spent_seconds float?",
        ]
        
        review_section = self._extract_class_section(content, "Review")
        
        for field in optional_fields:
            assert field in review_section or field.replace("?", " ?") in review_section, \
                   f"Review schema should contain optional field '{field}'"
                   
    def test_field_descriptions(self):
        """Test that Review fields have proper descriptions."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        review_section = self._extract_class_section(content, "Review")
        
        # Check for descriptions on key fields
        assert '@description(' in review_section, "Review fields should have descriptions"
        
    def test_validity_enum_values(self):
        """Test validity pattern in BAML matches Python model."""
        models_path = Path("baml_src/models.baml") 
        content = models_path.read_text()
        
        # Check if we have validity defined as an enum
        if "enum Validity" in content:
            enum_section = self._extract_enum_section(content, "Validity")
            assert "valid" in enum_section
            assert "questionable" in enum_section
            assert "invalid" in enum_section
            
    def test_criticality_enum_values(self):
        """Test criticality pattern in BAML matches Python model."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        # Check if we have criticality defined as an enum
        if "enum Criticality" in content:
            enum_section = self._extract_enum_section(content, "Criticality")
            assert "fundamental" in enum_section
            assert "peripheral" in enum_section
            
    def test_confidence_level_enum(self):
        """Test confidence level pattern in BAML matches Python model."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        # Check if we have confidence level defined as an enum
        if "enum ConfidenceLevel" in content:
            enum_section = self._extract_enum_section(content, "ConfidenceLevel")
            assert "high" in enum_section
            assert "medium" in enum_section
            assert "low" in enum_section
    
    def _extract_class_section(self, content: str, class_name: str) -> str:
        """Extract the content of a specific class from BAML file."""
        start_marker = f"class {class_name} "  # Add space to avoid partial matches
        if start_marker not in content:
            return ""
            
        start_idx = content.index(start_marker)
        
        # Find the closing brace by counting braces
        brace_count = 0
        i = start_idx
        while i < len(content):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return content[start_idx:i+1]
            i += 1
            
        return content[start_idx:]
        
    def _extract_enum_section(self, content: str, enum_name: str) -> str:
        """Extract the content of a specific enum from BAML file."""
        start_marker = f"enum {enum_name}"
        if start_marker not in content:
            return ""
            
        start_idx = content.index(start_marker)
        
        # Find the closing brace
        brace_count = 0
        i = start_idx
        while i < len(content):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return content[start_idx:i+1]
            i += 1
            
        return content[start_idx:]