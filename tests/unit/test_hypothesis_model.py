"""Unit tests for the Hypothesis model."""

from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from src.core.models import (
    Citation,
    ExperimentalProtocol,
    Hypothesis,
    HypothesisCategory,
    HypothesisSummary,
)


class TestCitation:
    """Test the Citation model."""
    
    def test_citation_creation(self):
        """Test creating a citation."""
        citation = Citation(
            authors=["Smith, J.", "Doe, A."],
            title="A groundbreaking study",
            journal="Nature",
            year=2023,
            doi="10.1038/nature.2023.12345",
            url="https://doi.org/10.1038/nature.2023.12345"
        )
        
        assert citation.authors == ["Smith, J.", "Doe, A."]
        assert citation.title == "A groundbreaking study"
        assert citation.journal == "Nature"
        assert citation.year == 2023
        assert citation.doi == "10.1038/nature.2023.12345"
    
    def test_citation_minimal(self):
        """Test creating citation with minimal fields."""
        citation = Citation(
            authors=["Smith, J."],
            title="Study",
            year=2023
        )
        
        assert citation.journal is None
        assert citation.doi is None
        assert citation.url is None
    
    def test_citation_validation(self):
        """Test citation validation."""
        # Year must be reasonable
        with pytest.raises(ValidationError):
            Citation(
                authors=["Smith, J."],
                title="Study",
                year=1500  # Too old
            )
        
        # Authors list can't be empty
        with pytest.raises(ValidationError):
            Citation(
                authors=[],
                title="Study",
                year=2023
            )


class TestExperimentalProtocol:
    """Test the ExperimentalProtocol model."""
    
    def test_protocol_creation(self):
        """Test creating an experimental protocol."""
        protocol = ExperimentalProtocol(
            objective="Test drug efficacy in AML cells",
            methodology="1. Culture AML cell lines\n2. Apply drug at various concentrations\n3. Measure viability",
            required_resources=["AML cell lines", "Drug compound", "Viability assay kit"],
            timeline="2 weeks",
            success_metrics=["IC50 < 10μM", "Selective toxicity to AML cells"],
            potential_challenges=["Cell line availability", "Drug solubility"],
            safety_considerations=["BSL-2 containment required", "Handle drug with care"]
        )
        
        assert protocol.objective == "Test drug efficacy in AML cells"
        assert len(protocol.required_resources) == 3
        assert len(protocol.success_metrics) == 2
        assert protocol.timeline == "2 weeks"
    
    def test_protocol_validation(self):
        """Test protocol validation."""
        # All fields are required
        with pytest.raises(ValidationError):
            ExperimentalProtocol(
                objective="Test something"
                # Missing other required fields
            )


class TestHypothesisCategory:
    """Test the HypothesisCategory enum."""
    
    def test_category_values(self):
        """Test that HypothesisCategory has expected values."""
        assert HypothesisCategory.MECHANISTIC.value == "mechanistic"
        assert HypothesisCategory.THERAPEUTIC.value == "therapeutic"
        assert HypothesisCategory.DIAGNOSTIC.value == "diagnostic"
        assert HypothesisCategory.BIOMARKER.value == "biomarker"
        assert HypothesisCategory.METHODOLOGY.value == "methodology"
        assert HypothesisCategory.OTHER.value == "other"


class TestHypothesis:
    """Test the Hypothesis model."""
    
    def test_hypothesis_creation_minimal(self):
        """Test creating a hypothesis with minimal fields."""
        protocol = ExperimentalProtocol(
            objective="Test hypothesis",
            methodology="Standard protocol",
            required_resources=["Resource 1"],
            timeline="1 week",
            success_metrics=["Metric 1"],
            potential_challenges=["Challenge 1"],
            safety_considerations=["Safety 1"]
        )
        
        hypothesis = Hypothesis(
            summary="A novel therapeutic approach for AML",
            category=HypothesisCategory.THERAPEUTIC,
            full_description="Detailed description of the hypothesis",
            novelty_claim="This is novel because...",
            assumptions=["Assumption 1", "Assumption 2"],
            experimental_protocol=protocol,
            supporting_evidence=[],
            confidence_score=0.8,
            generation_method="literature_exploration"
        )
        
        assert isinstance(hypothesis.id, UUID)
        assert hypothesis.summary == "A novel therapeutic approach for AML"
        assert hypothesis.category == HypothesisCategory.THERAPEUTIC
        assert hypothesis.confidence_score == 0.8
        assert isinstance(hypothesis.created_at, datetime)
    
    def test_hypothesis_with_citations(self):
        """Test hypothesis with supporting evidence."""
        citation = Citation(
            authors=["Smith, J."],
            title="Supporting study",
            journal="Cell",
            year=2023
        )
        
        protocol = ExperimentalProtocol(
            objective="Test hypothesis",
            methodology="Standard protocol",
            required_resources=["Resource 1"],
            timeline="1 week",
            success_metrics=["Metric 1"],
            potential_challenges=["Challenge 1"],
            safety_considerations=["Safety 1"]
        )
        
        hypothesis = Hypothesis(
            summary="A novel approach",
            category=HypothesisCategory.MECHANISTIC,
            full_description="Description",
            novelty_claim="Novel because...",
            assumptions=["Assumption 1"],
            experimental_protocol=protocol,
            supporting_evidence=[citation],
            confidence_score=0.9,
            generation_method="simulated_debate"
        )
        
        assert len(hypothesis.supporting_evidence) == 1
        assert hypothesis.supporting_evidence[0].authors == ["Smith, J."]
    
    def test_hypothesis_confidence_validation(self):
        """Test confidence score validation."""
        protocol = ExperimentalProtocol(
            objective="Test",
            methodology="Method",
            required_resources=["R1"],
            timeline="1w",
            success_metrics=["M1"],
            potential_challenges=["C1"],
            safety_considerations=["S1"]
        )
        
        # Confidence must be between 0 and 1
        with pytest.raises(ValidationError):
            Hypothesis(
                summary="Summary",
                category=HypothesisCategory.THERAPEUTIC,
                full_description="Description",
                novelty_claim="Novel",
                assumptions=["A1"],
                experimental_protocol=protocol,
                supporting_evidence=[],
                confidence_score=1.5,  # Too high
                generation_method="method"
            )
        
        with pytest.raises(ValidationError):
            Hypothesis(
                summary="Summary",
                category=HypothesisCategory.THERAPEUTIC,
                full_description="Description",
                novelty_claim="Novel",
                assumptions=["A1"],
                experimental_protocol=protocol,
                supporting_evidence=[],
                confidence_score=-0.1,  # Too low
                generation_method="method"
            )
    
    def test_hypothesis_assumptions_validation(self):
        """Test that assumptions list can't be empty."""
        protocol = ExperimentalProtocol(
            objective="Test",
            methodology="Method",
            required_resources=["R1"],
            timeline="1w",
            success_metrics=["M1"],
            potential_challenges=["C1"],
            safety_considerations=["S1"]
        )
        
        with pytest.raises(ValidationError):
            Hypothesis(
                summary="Summary",
                category=HypothesisCategory.THERAPEUTIC,
                full_description="Description",
                novelty_claim="Novel",
                assumptions=[],  # Empty list
                experimental_protocol=protocol,
                supporting_evidence=[],
                confidence_score=0.8,
                generation_method="method"
            )
    
    def test_hypothesis_serialization(self):
        """Test hypothesis serialization."""
        protocol = ExperimentalProtocol(
            objective="Test",
            methodology="Method",
            required_resources=["R1"],
            timeline="1w",
            success_metrics=["M1"],
            potential_challenges=["C1"],
            safety_considerations=["S1"]
        )
        
        hypothesis = Hypothesis(
            summary="Summary",
            category=HypothesisCategory.THERAPEUTIC,
            full_description="Description",
            novelty_claim="Novel",
            assumptions=["A1"],
            experimental_protocol=protocol,
            supporting_evidence=[],
            confidence_score=0.8,
            generation_method="method"
        )
        
        # Serialize to dict with JSON mode
        h_dict = hypothesis.model_dump(mode='json')
        assert h_dict["id"] == str(hypothesis.id)
        assert h_dict["category"] == "therapeutic"
        assert h_dict["confidence_score"] == 0.8
        
        # Deserialize
        h2 = Hypothesis.model_validate(h_dict)
        assert str(h2.id) == str(hypothesis.id)
        assert h2.summary == hypothesis.summary


class TestHypothesisSummary:
    """Test the HypothesisSummary model."""
    
    def test_summary_creation(self):
        """Test creating a hypothesis summary."""
        summary = HypothesisSummary(
            core_idea="Use existing drug for new indication",
            scientific_impact="Could provide immediate treatment option",
            feasibility_assessment="High - drug already approved",
            next_steps=["Obtain drug", "Culture cells", "Run assays"]
        )
        
        assert summary.core_idea == "Use existing drug for new indication"
        assert len(summary.next_steps) == 3
    
    def test_summary_validation(self):
        """Test summary validation."""
        # Next steps can't be empty
        with pytest.raises(ValidationError):
            HypothesisSummary(
                core_idea="Idea",
                scientific_impact="Impact",
                feasibility_assessment="High",
                next_steps=[]  # Empty list
            )