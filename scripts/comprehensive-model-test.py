#!/usr/bin/env python3
"""
Comprehensive Model Testing Script for AI Co-Scientist Platform
Tests all available models through Argo Gateway with specific parameters
"""

import os
import asyncio
import json
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional
import aiohttp
from dataclasses import dataclass, field
from enum import Enum

# Ensure we're on VPN
import subprocess

class TestType(Enum):
    COMPATIBILITY = "compatibility"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    EDGE_CASE = "edge_case"

@dataclass
class TestResult:
    model: str
    test_type: TestType
    test_name: str
    success: bool
    response_time: float
    error: Optional[str] = None
    response: Optional[Dict] = None
    metadata: Dict = field(default_factory=dict)

class ModelTester:
    def __init__(self):
        self.base_url = os.getenv("ARGO_PROXY_URL", "http://localhost:8000/v1")
        self.results: List[TestResult] = []
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def call_model(self, config: Dict) -> TestResult:
        """Make a single model call and return result."""
        model = config["model"]
        test_name = config.get("test_name", "unnamed_test")
        test_type = config.get("test_type", TestType.COMPATIBILITY)
        
        start_time = time.time()
        
        try:
            # Prepare request
            request_data = {
                "model": model,
                "messages": config["messages"],
            }
            
            # Add model-specific parameters
            if model == "gpto3":
                # O-series models use max_completion_tokens
                if "max_completion_tokens" in config:
                    request_data["max_completion_tokens"] = config["max_completion_tokens"]
                if "max_tokens" in config:
                    # Test if it's really ignored
                    request_data["max_tokens"] = config["max_tokens"]
            else:
                # Standard models
                if "max_tokens" in config:
                    request_data["max_tokens"] = config["max_tokens"]
                if "temperature" in config:
                    request_data["temperature"] = config["temperature"]
                if "top_p" in config:
                    request_data["top_p"] = config["top_p"]
            
            # Make request
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                response_time = time.time() - start_time
                response_data = await response.json()
                
                if response.status == 200:
                    return TestResult(
                        model=model,
                        test_type=test_type,
                        test_name=test_name,
                        success=True,
                        response_time=response_time,
                        response=response_data,
                        metadata={
                            "tokens_used": response_data.get("usage", {}),
                            "model_used": response_data.get("model"),
                        }
                    )
                else:
                    return TestResult(
                        model=model,
                        test_type=test_type,
                        test_name=test_name,
                        success=False,
                        response_time=response_time,
                        error=f"HTTP {response.status}: {response_data.get('error', {}).get('message', 'Unknown error')}",
                        response=response_data
                    )
                    
        except asyncio.TimeoutError:
            return TestResult(
                model=model,
                test_type=test_type,
                test_name=test_name,
                success=False,
                response_time=time.time() - start_time,
                error="Request timeout after 120 seconds"
            )
        except Exception as e:
            return TestResult(
                model=model,
                test_type=test_type,
                test_name=test_name,
                success=False,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def test_compatibility(self):
        """Hour 1: Test parameter compatibility for all models."""
        print("\n=== HOUR 1: COMPATIBILITY TESTING ===\n")
        
        # Test o3 parameter behavior
        print("Testing o3 (gpto3) parameter handling...")
        
        o3_tests = [
            {
                "model": "gpto3",
                "test_name": "o3_with_max_completion_tokens",
                "test_type": TestType.COMPATIBILITY,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Count from 1 to 100."}
                ],
                "max_completion_tokens": 100  # Should limit response
            },
            {
                "model": "gpto3",
                "test_name": "o3_with_max_tokens_ignored",
                "test_type": TestType.COMPATIBILITY,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Count from 1 to 100."}
                ],
                "max_tokens": 50  # Should be IGNORED - we'll get full response
            },
            {
                "model": "gpto3",
                "test_name": "o3_with_both_parameters",
                "test_type": TestType.COMPATIBILITY,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Count from 1 to 100."}
                ],
                "max_tokens": 50,  # Ignored
                "max_completion_tokens": 100  # This one counts
            }
        ]
        
        for test in o3_tests:
            result = await self.call_model(test)
            self.results.append(result)
            self.print_result(result)
        
        # Test Claude with different message formats
        print("\nTesting Claude (claudeopus4) message requirements...")
        
        claude_tests = [
            {
                "model": "claudeopus4",
                "test_name": "claude_with_system_and_user",
                "test_type": TestType.COMPATIBILITY,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, Claude!"}
                ],
                "max_tokens": 100
            },
            {
                "model": "claudeopus4",
                "test_name": "claude_system_only_should_work_with_proxy",
                "test_type": TestType.COMPATIBILITY,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant. Respond with 'Hello!'"}
                ],
                "max_tokens": 100
            }
        ]
        
        for test in claude_tests:
            result = await self.call_model(test)
            self.results.append(result)
            self.print_result(result)
        
        # Test standard OpenAI models
        print("\nTesting standard OpenAI models...")
        
        openai_tests = [
            {
                "model": "gpt4o",
                "test_name": "gpt4o_standard_params",
                "test_type": TestType.COMPATIBILITY,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say hello!"}
                ],
                "max_tokens": 100,
                "temperature": 0.7,
                "top_p": 0.9
            },
            {
                "model": "gpt35turbo",
                "test_name": "gpt35_baseline",
                "test_type": TestType.COMPATIBILITY,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say hello!"}
                ],
                "max_tokens": 100,
                "temperature": 0.5
            }
        ]
        
        for test in openai_tests:
            result = await self.call_model(test)
            self.results.append(result)
            self.print_result(result)
    
    async def test_performance(self):
        """Hour 2: Test performance across models."""
        print("\n\n=== HOUR 2: PERFORMANCE TESTING ===\n")
        
        # Standard test prompt for performance
        perf_messages = [
            {"role": "system", "content": "You are a scientific hypothesis generator."},
            {"role": "user", "content": """Generate a novel hypothesis about the relationship between 
            quantum entanglement and biological systems. Include potential mechanisms and testable predictions.
            Format as JSON with fields: title, mechanism, predictions (array), feasibility_score (1-10)."""}
        ]
        
        models_to_test = ["gpto3", "gpt4o", "claudeopus4", "gpt35turbo"]
        
        for model in models_to_test:
            print(f"\nTesting {model} performance (5 runs)...")
            timings = []
            
            for i in range(5):
                config = {
                    "model": model,
                    "test_name": f"{model}_performance_run_{i+1}",
                    "test_type": TestType.PERFORMANCE,
                    "messages": perf_messages,
                }
                
                # Add appropriate parameters
                if model == "gpto3":
                    config["max_completion_tokens"] = 500
                else:
                    config["max_tokens"] = 500
                    config["temperature"] = 0.7
                
                result = await self.call_model(config)
                self.results.append(result)
                
                if result.success:
                    timings.append(result.response_time)
                    print(f"  Run {i+1}: {result.response_time:.2f}s")
                else:
                    print(f"  Run {i+1}: FAILED - {result.error}")
            
            # Calculate statistics
            if timings:
                print(f"\n{model} Performance Summary:")
                print(f"  Mean: {statistics.mean(timings):.2f}s")
                print(f"  Median: {statistics.median(timings):.2f}s")
                print(f"  Min: {min(timings):.2f}s")
                print(f"  Max: {max(timings):.2f}s")
                if len(timings) > 1:
                    print(f"  StdDev: {statistics.stdev(timings):.2f}s")
    
    async def test_quality(self):
        """Test quality of responses for different task types."""
        print("\n\n=== QUALITY TESTING ===\n")
        
        quality_tests = [
            {
                "name": "hypothesis_generation",
                "messages": [
                    {"role": "system", "content": "You are an expert scientific hypothesis generator."},
                    {"role": "user", "content": """Generate 3 novel hypotheses about dark matter. 
                    Format as JSON: {"hypotheses": [{"id": 1, "title": "...", "description": "...", "testable": true/false}]}"""}
                ]
            },
            {
                "name": "review_analysis",
                "messages": [
                    {"role": "system", "content": "You are a rigorous scientific reviewer."},
                    {"role": "user", "content": """Review this hypothesis: 'Consciousness emerges from quantum coherence in microtubules.'
                    Format as JSON: {"strengths": [...], "weaknesses": [...], "evidence_quality": 1-10, "recommendation": "accept/revise/reject"}"""}
                ]
            }
        ]
        
        models = ["gpto3", "gpt4o", "claudeopus4"]
        
        for test in quality_tests:
            print(f"\nTesting {test['name']}...")
            for model in models:
                config = {
                    "model": model,
                    "test_name": f"{model}_{test['name']}",
                    "test_type": TestType.QUALITY,
                    "messages": test["messages"],
                }
                
                if model == "gpto3":
                    config["max_completion_tokens"] = 1000
                else:
                    config["max_tokens"] = 1000
                    config["temperature"] = 0.7
                
                result = await self.call_model(config)
                self.results.append(result)
                
                if result.success:
                    # Try to parse JSON response
                    try:
                        content = result.response["choices"][0]["message"]["content"]
                        json_data = json.loads(content)
                        print(f"  {model}: ✓ Valid JSON response")
                    except:
                        print(f"  {model}: ✗ Invalid JSON format")
                else:
                    print(f"  {model}: ✗ Failed - {result.error}")
    
    def print_result(self, result: TestResult):
        """Print a single test result."""
        status = "✓" if result.success else "✗"
        print(f"{status} {result.test_name}: ", end="")
        
        if result.success:
            if result.response and "choices" in result.response:
                content = result.response["choices"][0]["message"]["content"]
                # For o3 max_tokens test, check response length
                if "max_tokens_ignored" in result.test_name:
                    tokens = result.response.get("usage", {}).get("completion_tokens", 0)
                    print(f"Generated {tokens} tokens (max_tokens=50 was {'IGNORED' if tokens > 50 else 'RESPECTED'})")
                else:
                    print(f"{result.response_time:.2f}s")
            else:
                print(f"{result.response_time:.2f}s")
        else:
            print(f"ERROR: {result.error}")
    
    def generate_report(self):
        """Generate final report of all tests."""
        print("\n\n=== COMPREHENSIVE TEST REPORT ===\n")
        
        # Compatibility Summary
        print("## PARAMETER COMPATIBILITY MATRIX ##\n")
        print("| Model | max_tokens | max_completion_tokens | temperature | System-only msg |")
        print("|-------|------------|----------------------|-------------|-----------------|")
        
        # Analyze results
        compatibility_results = {}
        for result in self.results:
            if result.test_type == TestType.COMPATIBILITY:
                model = result.model
                if model not in compatibility_results:
                    compatibility_results[model] = {
                        "max_tokens": "?",
                        "max_completion_tokens": "?",
                        "temperature": "?",
                        "system_only": "?"
                    }
                
                # Check what was tested
                if "max_tokens_ignored" in result.test_name and result.success:
                    tokens_generated = result.response.get("usage", {}).get("completion_tokens", 0)
                    compatibility_results[model]["max_tokens"] = "❌ Ignored" if tokens_generated > 50 else "✓"
                elif "max_completion_tokens" in result.test_name:
                    compatibility_results[model]["max_completion_tokens"] = "✓" if result.success else "❌"
                elif "system_only" in result.test_name:
                    compatibility_results[model]["system_only"] = "✓" if result.success else "❌"
                elif "standard_params" in result.test_name:
                    compatibility_results[model]["temperature"] = "✓" if result.success else "❌"
        
        for model, compat in compatibility_results.items():
            print(f"| {model} | {compat['max_tokens']} | {compat['max_completion_tokens']} | {compat['temperature']} | {compat['system_only']} |")
        
        # Performance Summary
        print("\n## PERFORMANCE SUMMARY ##\n")
        perf_by_model = {}
        for result in self.results:
            if result.test_type == TestType.PERFORMANCE and result.success:
                model = result.model
                if model not in perf_by_model:
                    perf_by_model[model] = []
                perf_by_model[model].append(result.response_time)
        
        print("| Model | Mean Time | Median | Min | Max | Success Rate |")
        print("|-------|-----------|--------|-----|-----|--------------|")
        for model, times in perf_by_model.items():
            if times:
                total_runs = sum(1 for r in self.results if r.model == model and r.test_type == TestType.PERFORMANCE)
                success_rate = len(times) / total_runs * 100
                print(f"| {model} | {statistics.mean(times):.2f}s | {statistics.median(times):.2f}s | {min(times):.2f}s | {max(times):.2f}s | {success_rate:.0f}% |")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"model_test_report_{timestamp}.json"
        
        with open(report_file, "w") as f:
            json.dump({
                "timestamp": timestamp,
                "results": [
                    {
                        "model": r.model,
                        "test_type": r.test_type.value,
                        "test_name": r.test_name,
                        "success": r.success,
                        "response_time": r.response_time,
                        "error": r.error,
                        "metadata": r.metadata
                    } for r in self.results
                ]
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: {report_file}")

async def main():
    """Run comprehensive model tests."""
    print("Starting Comprehensive Model Testing")
    print("=" * 50)
    
    # Check if we're on VPN
    print("\nChecking VPN connection...")
    try:
        result = subprocess.run(["curl", "-s", "http://localhost:8000/health"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print("⚠️  Warning: argo-proxy might not be running. Make sure you're on VPN and proxy is started.")
            print("Run: ./scripts/argo-proxy.sh")
            return
    except:
        print("⚠️  Cannot reach argo-proxy. Please ensure VPN is connected and proxy is running.")
        return
    
    print("✓ Connected to argo-proxy")
    
    async with ModelTester() as tester:
        # Run tests in sequence
        await tester.test_compatibility()
        await tester.test_performance()
        await tester.test_quality()
        
        # Generate final report
        tester.generate_report()

if __name__ == "__main__":
    asyncio.run(main())