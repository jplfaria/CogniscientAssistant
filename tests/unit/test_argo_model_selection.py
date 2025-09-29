"""Unit tests for Argo model selection logic."""

import pytest

from src.llm.argo_provider import ArgoLLMProvider, ModelSelector


class TestModelSelection:
    """Test model selection logic."""
    
    def test_model_selector_initialization(self):
        """Test ModelSelector initialization."""
        selector = ModelSelector()
        
        # Verify default model costs are set (tuples of input/output costs)
        assert selector.model_costs["gpt4o"][0] > 0  # Input cost
        assert selector.model_costs["gpt4o"][1] > 0  # Output cost
        assert selector.model_costs["gpt35"][0] > 0
        assert selector.model_costs["claudeopus4"][0] > 0
        assert selector.model_costs["gemini25pro"][0] > 0
        
        # Verify default capabilities
        assert "gpt4o" in selector.model_capabilities
        assert "reasoning" in selector.model_capabilities["gpt4o"]
    
    def test_select_model_for_task_type(self):
        """Test model selection based on task type."""
        selector = ModelSelector()
        
        # Test generation tasks
        model = selector.select_model_for_task("generation", budget_conscious=False)
        assert model in ["claudeopus4", "gpt4o"]  # High capability models
        
        # Test simple tasks with budget constraint
        model = selector.select_model_for_task("simple_query", budget_conscious=True)
        assert model in ["gpt35", "gemini25flash"]  # Cheaper models
        
        # Test reasoning tasks
        model = selector.select_model_for_task("reasoning", budget_conscious=False)
        assert model in ["gpto3", "gpt4o", "claudeopus4", "gemini25pro"]  # Strong reasoning models
    
    def test_get_model_cost(self):
        """Test getting model cost estimates."""
        selector = ModelSelector()
        
        # Test cost calculation
        cost = selector.get_estimated_cost("gpt4o", input_tokens=1000, output_tokens=500)
        assert cost > 0
        
        # Test that cheaper models have lower costs
        cheap_cost = selector.get_estimated_cost("gpt35", 1000, 500)
        expensive_cost = selector.get_estimated_cost("gpt4o", 1000, 500)
        assert cheap_cost < expensive_cost
    
    def test_track_usage(self):
        """Test usage tracking."""
        selector = ModelSelector()
        
        # Track some usage
        selector.track_usage("gpt4o", input_tokens=1000, output_tokens=500)
        selector.track_usage("gpt4o", input_tokens=500, output_tokens=250)
        
        # Check accumulated usage
        usage = selector.get_usage_stats()
        assert usage["gpt4o"]["total_input_tokens"] == 1500
        assert usage["gpt4o"]["total_output_tokens"] == 750
        assert usage["gpt4o"]["request_count"] == 2
    
    def test_model_routing_rules(self):
        """Test model routing based on rules."""
        selector = ModelSelector()
        
        # Test routing rules
        rules = {
            "supervisor": "gpt4o",
            "generation": "claudeopus4",
            "reflection": "gpt4o",
            "ranking": "gpt35",
            "evolution": "claudeopus4",
            "proximity": "gpt35",
            "meta_review": "gpt4o"
        }
        
        selector.set_routing_rules(rules)
        
        # Verify rule-based selection
        assert selector.select_model_for_agent("supervisor") == "gpt4o"
        assert selector.select_model_for_agent("generation") == "claudeopus4"
        assert selector.select_model_for_agent("ranking") == "gpt35"
    
    def test_model_availability_routing(self):
        """Test routing when models are unavailable."""
        selector = ModelSelector()
        
        # Mark a model as unavailable
        selector.mark_model_unavailable("gpt4o")
        
        # Should select alternative
        model = selector.select_model_for_task("reasoning", budget_conscious=False)
        assert model != "gpt4o"
        assert model in ["gpto3", "claudeopus4", "gemini25pro"]
        
        # Mark model as available again
        selector.mark_model_available("gpt4o")
        
        # Should be selectable again
        models = selector.get_available_models()
        assert "gpt4o" in models


class TestArgoProviderModelSelection:
    """Test ArgoLLMProvider model selection integration."""
    
    @pytest.mark.asyncio
    async def test_provider_model_selection(self):
        """Test model selection in provider."""
        provider = ArgoLLMProvider()
        
        # Test getting model for task
        model = provider.select_model_for_task("generation")
        assert model in provider.model_selector.available_models
        
        # Test cost estimation
        cost = provider.estimate_cost(model, 1000, 500)
        assert cost > 0
    
    @pytest.mark.asyncio
    async def test_provider_usage_tracking(self):
        """Test usage tracking in provider."""
        provider = ArgoLLMProvider()
        
        # Track usage
        provider.track_request("gpt4o", 1000, 500)
        
        # Get usage report
        report = provider.get_usage_report()
        assert "gpt4o" in report
        assert report["gpt4o"]["request_count"] == 1
        assert report["gpt4o"]["total_cost"] > 0