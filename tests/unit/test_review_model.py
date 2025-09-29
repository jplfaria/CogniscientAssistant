"""Unit tests for the Review model."""

from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from src.core.models import (
    AssumptionDecomposition,
    FailurePoint,
    Review,
    ReviewDecision,
    ReviewScores,
    ReviewType,
    SimulationResults,
)


class TestReviewType:
    """Test the ReviewType enum."""
    
    def test_review_type_values(self):
        """Test that ReviewType has all required values."""
        assert ReviewType.INITIAL.value == "initial"
        assert ReviewType.FULL.value == "full"
        assert ReviewType.DEEP_VERIFICATION.value == "deep_verification"
        assert ReviewType.OBSERVATION.value == "observation"
        assert ReviewType.SIMULATION.value == "simulation"
        assert ReviewType.TOURNAMENT.value == "tournament"
    
    def test_review_type_members(self):
        """Test that ReviewType has exactly the required members."""
        expected_members = {
            "INITIAL", "FULL", "DEEP_VERIFICATION", 
            "OBSERVATION", "SIMULATION", "TOURNAMENT"
        }
        actual_members = {member.name for member in ReviewType}
        assert actual_members == expected_members


class TestReviewDecision:
    """Test the ReviewDecision enum."""
    
    def test_review_decision_values(self):
        """Test that ReviewDecision has expected values."""
        assert ReviewDecision.ACCEPT.value == "accept"
        assert ReviewDecision.REJECT.value == "reject"
        assert ReviewDecision.REVISE.value == "revise"


class TestReviewScores:
    """Test the ReviewScores model."""
    
    def test_scores_creation(self):
        """Test creating review scores."""
        scores = ReviewScores(
            correctness=0.8,
            quality=0.9,
            novelty=0.7,
            safety=1.0,
            feasibility=0.85
        )
        
        assert scores.correctness == 0.8
        assert scores.quality == 0.9
        assert scores.novelty == 0.7
        assert scores.safety == 1.0
        assert scores.feasibility == 0.85
    
    def test_scores_validation(self):
        """Test score validation (0-1 range)."""
        # Values must be between 0 and 1
        with pytest.raises(ValidationError):
            ReviewScores(
                correctness=1.5,  # Too high
                quality=0.5,
                novelty=0.5,
                safety=0.5,
                feasibility=0.5
            )
        
        with pytest.raises(ValidationError):
            ReviewScores(
                correctness=-0.1,  # Too low
                quality=0.5,
                novelty=0.5,
                safety=0.5,
                feasibility=0.5
            )
    
    def test_average_score(self):
        """Test average score calculation."""
        scores = ReviewScores(
            correctness=0.8,
            quality=0.9,
            novelty=0.7,
            safety=1.0,
            feasibility=0.6
        )
        
        expected_avg = (0.8 + 0.9 + 0.7 + 1.0 + 0.6) / 5
        assert scores.average_score() == expected_avg


class TestAssumptionDecomposition:
    """Test the AssumptionDecomposition model for deep verification reviews."""
    
    def test_assumption_creation(self):
        """Test creating an assumption decomposition."""
        decomp = AssumptionDecomposition(
            assumption="Metabolic gradients create persister niches",
            validity="questionable",
            evidence="Some supporting studies in biofilms",
            criticality="fundamental"
        )
        
        assert decomp.assumption == "Metabolic gradients create persister niches"
        assert decomp.validity == "questionable"
        assert decomp.evidence == "Some supporting studies in biofilms"
        assert decomp.criticality == "fundamental"
    
    def test_assumption_validation(self):
        """Test assumption validity values."""
        # Validity must be one of the allowed values
        with pytest.raises(ValidationError):
            AssumptionDecomposition(
                assumption="Test",
                validity="maybe",  # Invalid
                evidence="Evidence",
                criticality="fundamental"
            )
        
        # Criticality must be one of the allowed values
        with pytest.raises(ValidationError):
            AssumptionDecomposition(
                assumption="Test",
                validity="valid",
                evidence="Evidence",
                criticality="somewhat"  # Invalid
            )


class TestFailurePoint:
    """Test the FailurePoint model for simulation reviews."""
    
    def test_failure_point_creation(self):
        """Test creating a failure point."""
        fp = FailurePoint(
            step="TLR activation on stellate cells",
            probability=0.3,
            impact="Complete mechanism failure"
        )
        
        assert fp.step == "TLR activation on stellate cells"
        assert fp.probability == 0.3
        assert fp.impact == "Complete mechanism failure"
    
    def test_failure_point_probability_validation(self):
        """Test probability validation."""
        with pytest.raises(ValidationError):
            FailurePoint(
                step="Step",
                probability=1.5,  # Too high
                impact="Impact"
            )


class TestSimulationResults:
    """Test the SimulationResults model."""
    
    def test_simulation_results_creation(self):
        """Test creating simulation results."""
        fp = FailurePoint(
            step="Step 2",
            probability=0.2,
            impact="Partial failure"
        )
        
        results = SimulationResults(
            mechanism_steps=["Step 1", "Step 2", "Step 3"],
            failure_points=[fp],
            predicted_outcomes=["Outcome 1", "Outcome 2"]
        )
        
        assert len(results.mechanism_steps) == 3
        assert len(results.failure_points) == 1
        assert len(results.predicted_outcomes) == 2
    
    def test_simulation_results_validation(self):
        """Test that lists can't be empty."""
        with pytest.raises(ValidationError):
            SimulationResults(
                mechanism_steps=[],  # Empty
                failure_points=[],
                predicted_outcomes=["Outcome"]
            )


class TestReview:
    """Test the Review model."""
    
    def test_review_creation_minimal(self):
        """Test creating a review with minimal fields."""
        scores = ReviewScores(
            correctness=0.8,
            quality=0.9,
            novelty=0.7,
            safety=1.0,
            feasibility=0.85
        )
        
        review = Review(
            hypothesis_id=UUID("12345678-1234-5678-1234-567812345678"),
            reviewer_agent_id="reflection-agent-1",
            review_type=ReviewType.INITIAL,
            decision=ReviewDecision.ACCEPT,
            scores=scores,
            narrative_feedback="Good hypothesis with strong potential",
            key_strengths=["Novel approach", "Well-grounded"],
            key_weaknesses=["Limited preliminary data"],
            improvement_suggestions=["Add dose-response analysis"],
            confidence_level="high"
        )
        
        assert isinstance(review.id, UUID)
        assert review.hypothesis_id == UUID("12345678-1234-5678-1234-567812345678")
        assert review.review_type == ReviewType.INITIAL
        assert review.decision == ReviewDecision.ACCEPT
        assert review.scores.correctness == 0.8
        assert isinstance(review.created_at, datetime)
    
    def test_review_with_deep_verification(self):
        """Test review with deep verification data."""
        scores = ReviewScores(
            correctness=0.7,
            quality=0.8,
            novelty=0.9,
            safety=1.0,
            feasibility=0.6
        )
        
        assumptions = [
            AssumptionDecomposition(
                assumption="Assumption 1",
                validity="valid",
                evidence="Strong evidence",
                criticality="fundamental"
            ),
            AssumptionDecomposition(
                assumption="Assumption 2",
                validity="questionable",
                evidence="Limited evidence",
                criticality="peripheral"
            )
        ]
        
        review = Review(
            hypothesis_id=UUID("12345678-1234-5678-1234-567812345678"),
            reviewer_agent_id="reflection-agent-2",
            review_type=ReviewType.DEEP_VERIFICATION,
            decision=ReviewDecision.REVISE,
            scores=scores,
            narrative_feedback="Needs assumption clarification",
            key_strengths=["Strong theoretical basis"],
            key_weaknesses=["Assumption 2 needs support"],
            improvement_suggestions=["Validate assumption 2"],
            confidence_level="medium",
            assumption_decomposition=assumptions
        )
        
        assert review.review_type == ReviewType.DEEP_VERIFICATION
        assert len(review.assumption_decomposition) == 2
        assert review.assumption_decomposition[0].validity == "valid"
    
    def test_review_with_simulation(self):
        """Test review with simulation results."""
        scores = ReviewScores(
            correctness=0.9,
            quality=0.85,
            novelty=0.8,
            safety=0.95,
            feasibility=0.7
        )
        
        sim_results = SimulationResults(
            mechanism_steps=["NET formation", "TLR activation", "Stellate response"],
            failure_points=[
                FailurePoint(
                    step="TLR activation",
                    probability=0.3,
                    impact="Mechanism failure"
                )
            ],
            predicted_outcomes=["Reduced fibrosis markers", "Lower collagen deposition"]
        )
        
        review = Review(
            hypothesis_id=UUID("12345678-1234-5678-1234-567812345678"),
            reviewer_agent_id="reflection-agent-3",
            review_type=ReviewType.SIMULATION,
            decision=ReviewDecision.ACCEPT,
            scores=scores,
            narrative_feedback="Mechanism is plausible with caveats",
            key_strengths=["Clear mechanism"],
            key_weaknesses=["TLR activation uncertainty"],
            improvement_suggestions=["Validate TLR expression levels"],
            confidence_level="medium",
            simulation_results=sim_results
        )
        
        assert review.review_type == ReviewType.SIMULATION
        assert review.simulation_results is not None
        assert len(review.simulation_results.mechanism_steps) == 3
    
    def test_review_validation(self):
        """Test review validation rules."""
        scores = ReviewScores(
            correctness=0.8,
            quality=0.9,
            novelty=0.7,
            safety=1.0,
            feasibility=0.85
        )
        
        # Key strengths can't be empty
        with pytest.raises(ValidationError):
            Review(
                hypothesis_id=UUID("12345678-1234-5678-1234-567812345678"),
                reviewer_agent_id="agent-1",
                review_type=ReviewType.INITIAL,
                decision=ReviewDecision.ACCEPT,
                scores=scores,
                narrative_feedback="Good",
                key_strengths=[],  # Empty
                key_weaknesses=["None"],
                improvement_suggestions=["None"],
                confidence_level="high"
            )
        
        # Invalid confidence level
        with pytest.raises(ValidationError):
            Review(
                hypothesis_id=UUID("12345678-1234-5678-1234-567812345678"),
                reviewer_agent_id="agent-1",
                review_type=ReviewType.INITIAL,
                decision=ReviewDecision.ACCEPT,
                scores=scores,
                narrative_feedback="Good",
                key_strengths=["Strong"],
                key_weaknesses=["None"],
                improvement_suggestions=["None"],
                confidence_level="very_high"  # Invalid
            )
    
    def test_review_serialization(self):
        """Test review serialization."""
        scores = ReviewScores(
            correctness=0.8,
            quality=0.9,
            novelty=0.7,
            safety=1.0,
            feasibility=0.85
        )
        
        review = Review(
            hypothesis_id=UUID("12345678-1234-5678-1234-567812345678"),
            reviewer_agent_id="agent-1",
            review_type=ReviewType.INITIAL,
            decision=ReviewDecision.ACCEPT,
            scores=scores,
            narrative_feedback="Good",
            key_strengths=["Strong"],
            key_weaknesses=["None"],
            improvement_suggestions=["Continue"],
            confidence_level="high"
        )
        
        # Serialize to dict with JSON mode
        review_dict = review.model_dump(mode='json')
        assert review_dict["id"] == str(review.id)
        assert review_dict["hypothesis_id"] == "12345678-1234-5678-1234-567812345678"
        assert review_dict["review_type"] == "initial"
        assert review_dict["decision"] == "accept"
        
        # Deserialize
        review2 = Review.model_validate(review_dict)
        assert str(review2.id) == str(review.id)
        assert review2.decision == review.decision