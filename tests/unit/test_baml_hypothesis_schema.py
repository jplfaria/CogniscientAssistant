"""Tests for BAML Hypothesis schema."""

import os
from pathlib import Path
import pytest
from typing import Dict, Any


class TestBAMLHypothesisSchema:
    """Test BAML Hypothesis schema definitions."""
    
    def test_baml_directory_structure_exists(self):
        """Test that BAML directory structure is set up correctly."""
        baml_root = Path("baml_src")
        assert baml_root.exists(), "baml_src directory should exist"
        assert baml_root.is_dir(), "baml_src should be a directory"
        
        # Check for required BAML files
        models_file = baml_root / "models.baml"
        assert models_file.exists(), "models.baml should exist"
        
    def test_hypothesis_schema_exists(self):
        """Test that Hypothesis schema is defined in models.baml."""
        models_path = Path("baml_src/models.baml")
        assert models_path.exists(), "models.baml should exist"
        
        content = models_path.read_text()
        assert "class Hypothesis" in content, "Hypothesis class should be defined"
        
    def test_hypothesis_schema_fields(self):
        """Test that Hypothesis schema has all required fields."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        # Required fields from the Python model
        required_fields = [
            "id string",
            "summary string",
            "category string",
            "full_description string", 
            "novelty_claim string",
            "assumptions string[]",
            "experimental_protocol ExperimentalProtocol",
            "supporting_evidence Citation[]",
            "confidence_score float",
            "generation_method string",
            "created_at string",
        ]
        
        hypothesis_section = self._extract_class_section(content, "Hypothesis")
        
        for field in required_fields:
            assert field in hypothesis_section, f"Hypothesis schema should contain '{field}'"
            
    def test_citation_schema_exists(self):
        """Test that Citation schema is defined."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        assert "class Citation" in content, "Citation class should be defined"
        
        required_fields = [
            "authors string[]",
            "title string",
            "journal string?",
            "year int",
            "doi string?",
            "url string?",
        ]
        
        citation_section = self._extract_class_section(content, "Citation")
        
        for field in required_fields:
            assert field in citation_section, f"Citation schema should contain '{field}'"
            
    def test_experimental_protocol_schema_exists(self):
        """Test that ExperimentalProtocol schema is defined."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        assert "class ExperimentalProtocol" in content, "ExperimentalProtocol class should be defined"
        
        required_fields = [
            "objective string",
            "methodology string",
            "required_resources string[]",
            "timeline string",
            "success_metrics string[]",
            "potential_challenges string[]",
            "safety_considerations string[]",
        ]
        
        protocol_section = self._extract_class_section(content, "ExperimentalProtocol")
        
        for field in required_fields:
            assert field in protocol_section, f"ExperimentalProtocol schema should contain '{field}'"
            
    def test_hypothesis_summary_schema_exists(self):
        """Test that HypothesisSummary schema is defined."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        assert "class HypothesisSummary" in content, "HypothesisSummary class should be defined"
        
        required_fields = [
            "core_idea string",
            "scientific_impact string",
            "feasibility_assessment string",
            "next_steps string[]",
        ]
        
        summary_section = self._extract_class_section(content, "HypothesisSummary")
        
        for field in required_fields:
            assert field in summary_section, f"HypothesisSummary schema should contain '{field}'"
            
    def test_hypothesis_category_enum_exists(self):
        """Test that HypothesisCategory enum is defined."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        assert "enum HypothesisCategory" in content, "HypothesisCategory enum should be defined"
        
        categories = [
            "mechanistic",
            "therapeutic", 
            "diagnostic",
            "biomarker",
            "methodology",
            "other",
        ]
        
        enum_section = self._extract_enum_section(content, "HypothesisCategory")
        
        for category in categories:
            assert category in enum_section, f"HypothesisCategory should contain '{category}'"
            
    def test_field_descriptions(self):
        """Test that fields have proper descriptions."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        hypothesis_section = self._extract_class_section(content, "Hypothesis")
        
        # Check for descriptions on key fields
        assert '@description("Concise one-sentence description")' in hypothesis_section or \
               '@description("Concise one-sentence description' in hypothesis_section, \
               "summary field should have description"
        
        assert '@description("0-1 confidence score")' in hypothesis_section or \
               '@description("0-1 confidence score' in hypothesis_section, \
               "confidence_score field should have description"
               
    def test_optional_fields(self):
        """Test that optional fields are properly marked."""
        models_path = Path("baml_src/models.baml")
        content = models_path.read_text()
        
        # Optional fields from Hypothesis model
        optional_fields = [
            "elo_rating float?",
            "review_count int?",
            "evolution_count int?",
        ]
        
        hypothesis_section = self._extract_class_section(content, "Hypothesis")
        
        for field in optional_fields:
            assert field in hypothesis_section or field.replace("?", " ?") in hypothesis_section, \
                   f"Hypothesis schema should contain optional field '{field}'"
    
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