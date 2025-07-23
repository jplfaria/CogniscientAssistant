"""Unit tests for literature-based generation in GenerationAgent."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from src.agents.generation import GenerationAgent
from src.core.models import (
    Hypothesis,
    HypothesisCategory,
    Citation,
    ExperimentalProtocol,
    ResearchGoal
)
from src.core.task_queue import TaskQueue
from src.core.context_memory import ContextMemory
from src.llm.base import LLMProvider
from src.llm.baml_wrapper import BAMLWrapper


@pytest.fixture
def mock_dependencies():
    """Create mock dependencies for GenerationAgent."""
    task_queue = AsyncMock(spec=TaskQueue)
    context_memory = AsyncMock(spec=ContextMemory)
    llm_provider = AsyncMock(spec=LLMProvider)
    
    # Set up default return values
    context_memory.get.return_value = None
    context_memory.set.return_value = None
    
    return task_queue, context_memory, llm_provider


@pytest.fixture
def generation_agent(mock_dependencies):
    """Create a GenerationAgent instance."""
    task_queue, context_memory, llm_provider = mock_dependencies
    return GenerationAgent(
        task_queue=task_queue,
        context_memory=context_memory,
        llm_provider=llm_provider
    )


class TestLiteratureBasedGeneration:
    """Test literature-based hypothesis generation."""
    
    @pytest.mark.asyncio
    async def test_generate_from_literature_with_baml(self, generation_agent):
        """Test that literature-based generation properly uses BAML wrapper."""
        research_goal = ResearchGoal(
            description="Develop novel cancer therapeutics",
            constraints=["Must target solid tumors", "Minimal side effects"]
        )
        
        literature = [
            {
                'title': 'PD-1 blockade in cancer therapy',
                'abstract': 'Recent advances in immunotherapy show promise...',
                'doi': '10.1234/cancer.2024.001',
                'journal': 'Nature Cancer',
                'relevance': 0.95
            },
            {
                'title': 'CAR-T cell engineering approaches',
                'abstract': 'Novel modifications to CAR-T cells improve efficacy...',
                'doi': '10.1234/cancer.2024.002',
                'journal': 'Cell',
                'relevance': 0.90
            }
        ]
        
        # Mock BAML wrapper response
        mock_baml_wrapper = AsyncMock(spec=BAMLWrapper)
        mock_hypothesis = Mock()
        mock_hypothesis.id = str(uuid4())
        mock_hypothesis.summary = "Combined PD-1 blockade with engineered CAR-T cells"
        mock_hypothesis.category = "therapeutic"
        mock_hypothesis.full_description = "A novel approach combining checkpoint inhibition..."
        mock_hypothesis.novelty_claim = "First to combine these two modalities"
        mock_hypothesis.assumptions = ["CAR-T cells can be engineered for solid tumors"]
        # Set up experimental protocol mock
        mock_protocol = Mock(spec=ExperimentalProtocol)
        mock_protocol.objective = "Test objective"
        mock_protocol.methodology = "Test methodology"
        mock_protocol.required_resources = ["Resource 1"]
        mock_protocol.timeline = "6 months"
        mock_protocol.success_metrics = ["Metric 1"]
        mock_protocol.potential_challenges = ["Challenge 1"]
        mock_protocol.safety_considerations = ["Safety 1"]
        
        mock_hypothesis.experimental_protocol = mock_protocol
        mock_hypothesis.supporting_evidence = []
        mock_hypothesis.confidence_score = 0.85
        mock_hypothesis.generation_method = "literature_based"
        mock_hypothesis.created_at = "2024-01-01T00:00:00Z"
        
        mock_baml_wrapper.generate_hypothesis.return_value = mock_hypothesis
        
        # Inject mock BAML wrapper
        generation_agent.baml_wrapper = mock_baml_wrapper
        
        # Execute
        result = await generation_agent.generate_from_literature(research_goal, literature)
        
        # Verify BAML was called correctly
        mock_baml_wrapper.generate_hypothesis.assert_called_once()
        call_args = mock_baml_wrapper.generate_hypothesis.call_args
        
        # Check the arguments passed to BAML
        assert call_args.kwargs['goal'] == research_goal.description
        assert call_args.kwargs['constraints'] == research_goal.constraints
        assert call_args.kwargs['generation_method'] == 'literature_based'
        assert 'focus_area' in call_args.kwargs
        
        # Verify the focus area contains literature context
        focus_area = call_args.kwargs['focus_area']
        assert 'PD-1 blockade' in focus_area or 'CAR-T' in focus_area
        
        # Verify result
        assert isinstance(result, Hypothesis)
        assert result.summary == mock_hypothesis.summary
        assert len(result.supporting_evidence) > 0  # Should add citations
        assert result.supporting_evidence[0].doi == '10.1234/cancer.2024.001'
    
    @pytest.mark.asyncio
    async def test_literature_context_preparation(self, generation_agent):
        """Test that literature context is properly prepared for BAML."""
        literature = [
            {
                'title': 'Study on protein folding mechanisms',
                'abstract': 'We discovered that chaperones play a crucial role...',
                'doi': '10.1234/protein.2024.001',
                'relevance': 0.9
            },
            {
                'title': 'Heat shock proteins in disease',
                'abstract': 'HSP90 is implicated in cancer progression...',
                'doi': '10.1234/protein.2024.002',
                'relevance': 0.85
            },
            {
                'title': 'Protein aggregation in neurodegeneration',
                'abstract': 'Misfolded proteins form toxic aggregates...',
                'doi': '10.1234/neuro.2024.001',
                'relevance': 0.8
            }
        ]
        
        context = generation_agent._prepare_literature_context(literature)
        
        # Verify context structure
        assert 'focus_area' in context
        assert 'key_findings' in context
        
        # Should include titles from most relevant papers
        assert 'protein folding' in context['focus_area'].lower()
        assert 'heat shock' in context['focus_area'].lower()
        
        # Should include abstracts from most relevant papers
        assert 'chaperones' in context['key_findings'].lower()
        assert 'hsp90' in context['key_findings'].lower()
    
    @pytest.mark.asyncio
    async def test_hypothesis_conversion_from_baml(self, generation_agent):
        """Test proper conversion of BAML hypothesis to our model."""
        # Create a mock BAML hypothesis
        mock_baml_hyp = Mock()
        mock_baml_hyp.id = "baml-hyp-123"
        mock_baml_hyp.summary = "Test hypothesis summary"
        mock_baml_hyp.category = "mechanistic"
        mock_baml_hyp.full_description = "Detailed description of the hypothesis"
        mock_baml_hyp.novelty_claim = "Novel because..."
        mock_baml_hyp.assumptions = ["Assumption 1", "Assumption 2"]
        mock_baml_hyp.experimental_protocol = Mock()
        mock_baml_hyp.experimental_protocol.objective = "Test objective"
        mock_baml_hyp.experimental_protocol.methodology = "Test methodology"
        mock_baml_hyp.experimental_protocol.required_resources = ["Resource 1"]
        mock_baml_hyp.experimental_protocol.timeline = "6 months"
        mock_baml_hyp.experimental_protocol.success_metrics = ["Metric 1"]
        mock_baml_hyp.experimental_protocol.potential_challenges = ["Challenge 1"]
        mock_baml_hyp.experimental_protocol.safety_considerations = ["Safety 1"]
        mock_baml_hyp.supporting_evidence = []
        mock_baml_hyp.confidence_score = 0.9
        mock_baml_hyp.generation_method = "literature_based"
        mock_baml_hyp.created_at = "2024-01-01T00:00:00Z"
        
        # Convert
        result = generation_agent._convert_baml_hypothesis(mock_baml_hyp)
        
        # Verify conversion
        assert isinstance(result, Hypothesis)
        assert result.summary == mock_baml_hyp.summary
        assert result.category == HypothesisCategory.MECHANISTIC
        assert result.full_description == mock_baml_hyp.full_description
        assert result.novelty_claim == mock_baml_hyp.novelty_claim
        assert result.assumptions == mock_baml_hyp.assumptions
        assert result.confidence_score == mock_baml_hyp.confidence_score
        assert result.generation_method == mock_baml_hyp.generation_method
        
        # Verify experimental protocol
        assert result.experimental_protocol.objective == "Test objective"
        assert result.experimental_protocol.methodology == "Test methodology"
    
    @pytest.mark.asyncio
    async def test_citation_extraction_from_literature(self, generation_agent):
        """Test extraction of citations from literature."""
        literature = [
            {
                'title': 'Important discovery',
                'doi': '10.1234/test.2024.001',
                'journal': 'Nature',
                'year': 2024,
                'authors': 'Smith J, Doe A'
            },
            {
                'title': 'Another finding',
                'doi': '10.1234/test.2024.002',
                'journal': 'Science',
                'year': 2024
            },
            {
                'title': 'No DOI paper',
                'journal': 'Local Journal'
                # Missing DOI, should be skipped
            }
        ]
        
        citations = generation_agent._extract_citations(literature)
        
        # Should only extract papers with DOIs
        assert len(citations) == 2
        assert citations[0].doi == '10.1234/test.2024.001'
        assert citations[0].title == 'Important discovery'
        assert citations[0].journal == 'Nature'
        assert citations[1].doi == '10.1234/test.2024.002'
    
    @pytest.mark.asyncio
    async def test_error_handling_in_literature_generation(self, generation_agent):
        """Test error handling when BAML generation fails."""
        research_goal = ResearchGoal(description="Test goal for BAML generation")
        literature = []
        
        # Mock BAML wrapper to raise exception
        mock_baml_wrapper = AsyncMock(spec=BAMLWrapper)
        mock_baml_wrapper.generate_hypothesis.side_effect = Exception("BAML API error")
        generation_agent.baml_wrapper = mock_baml_wrapper
        
        # Should raise RuntimeError with meaningful message
        with pytest.raises(RuntimeError, match="Generation failed"):
            await generation_agent.generate_from_literature(research_goal, literature)
    
    @pytest.mark.asyncio
    async def test_hypothesis_storage_after_generation(self, generation_agent):
        """Test that generated hypotheses are properly stored in context memory."""
        research_goal = ResearchGoal(description="Test goal for BAML generation")
        literature = []
        
        # Mock BAML response
        mock_baml_wrapper = AsyncMock(spec=BAMLWrapper)
        mock_hypothesis = Mock()
        mock_hypothesis.id = str(uuid4())
        mock_hypothesis.summary = "Test hypothesis"
        mock_hypothesis.category = "mechanistic"
        mock_hypothesis.generation_method = "literature_based"
        # Add all required fields for the mock
        mock_hypothesis.full_description = "Full description"
        mock_hypothesis.novelty_claim = "Novel claim"
        mock_hypothesis.assumptions = ["Test assumption 1"]
        # Set up experimental protocol mock
        mock_protocol = Mock(spec=ExperimentalProtocol)
        mock_protocol.objective = "Test objective"
        mock_protocol.methodology = "Test methodology"
        mock_protocol.required_resources = ["Resource 1"]
        mock_protocol.timeline = "6 months"
        mock_protocol.success_metrics = ["Metric 1"]
        mock_protocol.potential_challenges = ["Challenge 1"]
        mock_protocol.safety_considerations = ["Safety 1"]
        
        mock_hypothesis.experimental_protocol = mock_protocol
        mock_hypothesis.supporting_evidence = []
        mock_hypothesis.confidence_score = 0.8
        mock_hypothesis.created_at = "2024-01-01T00:00:00Z"
        
        mock_baml_wrapper.generate_hypothesis.return_value = mock_hypothesis
        generation_agent.baml_wrapper = mock_baml_wrapper
        
        # Generate hypothesis
        result = await generation_agent.generate_from_literature(research_goal, literature)
        
        # Verify storage was called
        generation_agent.context_memory.set.assert_called()
        
        # Check that statistics were updated
        calls = generation_agent.context_memory.set.call_args_list
        stats_call = next((c for c in calls if c[0][0] == 'generation_statistics'), None)
        assert stats_call is not None
        
        stats = stats_call[0][1]
        assert stats['total_generated'] == 1
        assert stats['literature_based_count'] == 1