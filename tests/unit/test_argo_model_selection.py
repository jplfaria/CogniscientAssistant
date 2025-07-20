"""Unit tests for Argo model selection logic."""

import pytest

from src.llm.argo_provider import ArgoLLMProvider, ModelSelector


class TestModelSelection:
    """Test model selection logic."""
    
    def test_model_selector_initialization(self):
        """Test ModelSelector initialization."""
        selector = ModelSelector()
        
        # Verify default model costs are set (tuples of input/output costs)
        assert selector.model_costs["gpt-4o"][0] > 0  # Input cost
        assert selector.model_costs["gpt-4o"][1] > 0  # Output cost
        assert selector.model_costs["gpt-3.5-turbo"][0] > 0
        assert selector.model_costs["claude-opus-4"][0] > 0
        assert selector.model_costs["gemini-2.5-pro"][0] > 0
        
        # Verify default capabilities
        assert "gpt-4o" in selector.model_capabilities
        assert "reasoning" in selector.model_capabilities["gpt-4o"]
    
    def test_select_model_for_task_type(self):
        """Test model selection based on task type."""
        selector = ModelSelector()
        
        # Test generation tasks
        model = selector.select_model_for_task("generation", budget_conscious=False)
        assert model in ["claude-opus-4", "gpt-4o"]  # High capability models
        
        # Test simple tasks with budget constraint
        model = selector.select_model_for_task("simple_query", budget_conscious=True)
        assert model in ["gpt-3.5-turbo", "gemini-2.5-flash"]  # Cheaper models
        
        # Test reasoning tasks
        model = selector.select_model_for_task("reasoning", budget_conscious=False)
        assert model in ["gpt-4o", "claude-opus-4"]  # Strong reasoning models
    
    def test_get_model_cost(self):
        """Test getting model cost estimates."""
        selector = ModelSelector()
        
        # Test cost calculation
        cost = selector.get_estimated_cost("gpt-4o", input_tokens=1000, output_tokens=500)
        assert cost > 0
        
        # Test that cheaper models have lower costs
        cheap_cost = selector.get_estimated_cost("gpt-3.5-turbo", 1000, 500)
        expensive_cost = selector.get_estimated_cost("gpt-4o", 1000, 500)
        assert cheap_cost < expensive_cost
    
    def test_track_usage(self):
        """Test usage tracking."""
        selector = ModelSelector()
        
        # Track some usage
        selector.track_usage("gpt-4o", input_tokens=1000, output_tokens=500)
        selector.track_usage("gpt-4o", input_tokens=500, output_tokens=250)
        
        # Check accumulated usage
        usage = selector.get_usage_stats()
        assert usage["gpt-4o"]["total_input_tokens"] == 1500
        assert usage["gpt-4o"]["total_output_tokens"] == 750
        assert usage["gpt-4o"]["request_count"] == 2
    
    def test_model_routing_rules(self):
        """Test model routing based on rules."""
        selector = ModelSelector()
        
        # Test routing rules
        rules = {
            "supervisor": "gpt-4o",
            "generation": "claude-opus-4",
            "reflection": "gpt-4o",
            "ranking": "gpt-3.5-turbo",
            "evolution": "claude-opus-4",
            "proximity": "gpt-3.5-turbo",
            "meta_review": "gpt-4o"
        }
        
        selector.set_routing_rules(rules)
        
        # Verify rule-based selection
        assert selector.select_model_for_agent("supervisor") == "gpt-4o"
        assert selector.select_model_for_agent("generation") == "claude-opus-4"
        assert selector.select_model_for_agent("ranking") == "gpt-3.5-turbo"
    
    def test_model_availability_routing(self):
        """Test routing when models are unavailable."""
        selector = ModelSelector()
        
        # Mark a model as unavailable
        selector.mark_model_unavailable("gpt-4o")
        
        # Should select alternative
        model = selector.select_model_for_task("reasoning", budget_conscious=False)
        assert model != "gpt-4o"
        assert model in ["claude-opus-4", "gemini-2.5-pro"]
        
        # Mark model as available again
        selector.mark_model_available("gpt-4o")
        
        # Should be selectable again
        models = selector.get_available_models()
        assert "gpt-4o" in models


class TestArgoProviderModelSelection:
    """Test ArgoLLMProvider model selection integration."""
    
    @pytest.mark.asyncio
    async def test_provider_model_selection(self):
        """Test model selection in provider."""
        provider = ArgoLLMProvider()
        
        # Test getting model for task
        model = provider.select_model_for_task("generation")
        assert model in provider.model_mapping
        
        # Test cost estimation
        cost = provider.estimate_cost(model, 1000, 500)
        assert cost > 0
    
    @pytest.mark.asyncio
    async def test_provider_usage_tracking(self):
        """Test usage tracking in provider."""
        provider = ArgoLLMProvider()
        
        # Track usage
        provider.track_request("gpt-4o", 1000, 500)
        
        # Get usage report
        report = provider.get_usage_report()
        assert "gpt-4o" in report
        assert report["gpt-4o"]["request_count"] == 1
        assert report["gpt-4o"]["total_cost"] > 0