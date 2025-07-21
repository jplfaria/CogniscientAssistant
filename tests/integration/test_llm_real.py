"""Optional real LLM integration tests.

These tests actually call the LLM through Argo Gateway and are:
- Expensive (use real compute)
- Require VPN connection
- Can be flaky (network/service issues)

Run with: pytest tests/integration/test_llm_real.py -v -s --real-llm
"""

import pytest
import os
import asyncio
from typing import Dict, Any
import aiohttp
import json


# Marker for real LLM tests
pytestmark = pytest.mark.real_llm


class TestRealLLMIntegration:
    """Test real LLM connectivity through Argo Gateway."""
    
    @pytest.fixture
    def argo_base_url(self):
        """Get Argo proxy base URL."""
        return "http://localhost:8000/v1"
    
    async def call_llm(self, model: str, prompt: str, base_url: str) -> Dict[str, Any]:
        """Make a real LLM call through Argo proxy."""
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                return await response.json()
    
    @pytest.mark.asyncio
    async def test_simple_prompt_all_models(self, argo_base_url):
        """Test a simple prompt across all available models."""
        models = ["gpt4o", "gpt35", "claudeopus4", "claudesonnet4", "gemini25pro"]
        prompt = "What is 2+2? Answer in exactly one word."
        
        results = {}
        for model in models:
            try:
                response = await self.call_llm(model, prompt, argo_base_url)
                if "choices" in response and response["choices"]:
                    content = response["choices"][0]["message"]["content"].strip()
                    results[model] = content
                else:
                    results[model] = f"No response: {response.get('error', 'Unknown error')}"
            except Exception as e:
                results[model] = f"Error: {str(e)}"
        
        print("\n\nModel Responses:")
        print("-" * 50)
        for model, result in results.items():
            print(f"{model:<15}: {result}")
        
        # At least some models should work
        successful = [r for r in results.values() if "Error" not in r and "No response" not in r]
        assert len(successful) > 0, "No models responded successfully"
    
    @pytest.mark.asyncio
    async def test_model_capabilities(self, argo_base_url):
        """Test different capabilities across models."""
        test_cases = [
            ("Reasoning", "If all roses are flowers and some flowers fade quickly, can we conclude that some roses fade quickly? Answer yes or no with one sentence explanation."),
            ("Creativity", "Write a haiku about artificial intelligence."),
            ("Code", "Write a Python one-liner to reverse a string. Just the code, no explanation."),
        ]
        
        # Test with GPT-3.5 as it's most reliable
        model = "gpt35"
        
        for capability, prompt in test_cases:
            try:
                response = await self.call_llm(model, prompt, argo_base_url)
                if "choices" in response and response["choices"]:
                    content = response["choices"][0]["message"]["content"].strip()
                    print(f"\n{capability} Test ({model}):")
                    print(f"Prompt: {prompt}")
                    print(f"Response: {content}")
                    assert len(content) > 0, f"Empty response for {capability}"
                else:
                    pytest.skip(f"Model {model} not responding for {capability}")
            except Exception as e:
                pytest.skip(f"Error testing {capability}: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_streaming_response(self, argo_base_url):
        """Test streaming responses (if supported)."""
        payload = {
            "model": "gpt35",
            "messages": [{"role": "user", "content": "Count from 1 to 5."}],
            "max_tokens": 50,
            "temperature": 0.7,
            "stream": True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{argo_base_url}/chat/completions",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        chunks = []
                        async for line in response.content:
                            if line:
                                chunks.append(line.decode('utf-8'))
                        
                        assert len(chunks) > 0, "No streaming chunks received"
                        print(f"\nReceived {len(chunks)} streaming chunks")
                    else:
                        pytest.skip("Streaming not supported or failed")
        except Exception as e:
            pytest.skip(f"Streaming test error: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, argo_base_url):
        """Test error handling with invalid requests."""
        # Test invalid model
        response = await self.call_llm("invalid-model-xyz", "Hello", argo_base_url)
        assert "error" in response or response.get("choices") == [], "Invalid model should return error"
        
        # Test empty prompt
        payload = {
            "model": "gpt35",
            "messages": [],
            "max_tokens": 50
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{argo_base_url}/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                data = await response.json()
                assert response.status == 400 or "error" in data, "Empty messages should error"


