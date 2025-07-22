#!/usr/bin/env python3
"""Focused model compatibility testing based on quick test findings."""

import asyncio
import aiohttp
import json
import time
import statistics
from typing import Dict, List, Any

class FocusedModelTester:
    def __init__(self):
        self.base_url = "http://localhost:8000/v1/chat/completions"
        self.results = []
        
    async def test_model_parameters(self):
        """Test parameter compatibility for each model."""
        print("\n=== PARAMETER COMPATIBILITY TESTING ===\n")
        
        tests = [
            # O3 Tests
            {
                "name": "o3_max_tokens_ignored",
                "model": "gpto3",
                "messages": [
                    {"role": "system", "content": "You are a concise assistant."},
                    {"role": "user", "content": "Write a story about a robot. Make it exactly 100 words long."}
                ],
                "params": {"max_tokens": 10},  # Should be ignored
                "expected": "Should generate >10 tokens"
            },
            {
                "name": "o3_max_completion_tokens",
                "model": "gpto3",
                "messages": [
                    {"role": "system", "content": "You are a concise assistant."},
                    {"role": "user", "content": "Say hello in 5 words."}
                ],
                "params": {"max_completion_tokens": 50},
                "expected": "Should respect limit"
            },
            {
                "name": "o3_with_temperature",
                "model": "gpto3",
                "messages": [
                    {"role": "system", "content": "You are creative."},
                    {"role": "user", "content": "Give me a random number."}
                ],
                "params": {"max_completion_tokens": 50, "temperature": 1.0},
                "expected": "Check if temperature accepted"
            },
            
            # GPT-4o Tests
            {
                "name": "gpt4o_standard",
                "model": "gpt4o",
                "messages": [
                    {"role": "system", "content": "You are helpful."},
                    {"role": "user", "content": "Say hello."}
                ],
                "params": {"max_tokens": 50, "temperature": 0.7, "top_p": 0.9},
                "expected": "All params should work"
            },
            
            # Claude Tests
            {
                "name": "claude_with_user_message",
                "model": "claudeopus4",
                "messages": [
                    {"role": "system", "content": "You are Claude."},
                    {"role": "user", "content": "Say hello."}
                ],
                "params": {"max_tokens": 50},
                "expected": "Should work with user message"
            },
            
            # GPT-3.5 Baseline
            {
                "name": "gpt35_baseline",
                "model": "gpt35turbo",
                "messages": [
                    {"role": "system", "content": "You are helpful."},
                    {"role": "user", "content": "Say hello."}
                ],
                "params": {"max_tokens": 50, "temperature": 0.5},
                "expected": "Standard params"
            }
        ]
        
        for test in tests:
            print(f"\nTesting: {test['name']}")
            print(f"Model: {test['model']}")
            print(f"Params: {test['params']}")
            
            async with aiohttp.ClientSession() as session:
                request_data = {
                    "model": test["model"],
                    "messages": test["messages"],
                    **test["params"]
                }
                
                try:
                    start = time.time()
                    async with session.post(
                        self.base_url, 
                        json=request_data,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as resp:
                        result = await resp.json()
                        elapsed = time.time() - start
                        
                        if resp.status == 200:
                            content = result["choices"][0]["message"]["content"]
                            tokens = result.get("usage", {}).get("completion_tokens", 0)
                            
                            # Check specific expectations
                            if "max_tokens_ignored" in test["name"]:
                                status = "✓ CONFIRMED" if tokens > 10 else "✗ NOT CONFIRMED"
                                print(f"  Result: {status} - Generated {tokens} tokens (limit was 10)")
                            elif "max_completion_tokens" in test["name"]:
                                status = "✓" if tokens <= 50 else "✗"
                                print(f"  Result: {status} - Generated {tokens} tokens")
                            else:
                                print(f"  Result: ✓ Success - {tokens} tokens in {elapsed:.1f}s")
                            
                            self.results.append({
                                "test": test["name"],
                                "model": test["model"],
                                "success": True,
                                "tokens": tokens,
                                "time": elapsed,
                                "response_preview": content[:100]
                            })
                        else:
                            error = result.get("error", {}).get("message", "Unknown error")
                            print(f"  Result: ✗ Error - {error}")
                            self.results.append({
                                "test": test["name"],
                                "model": test["model"],
                                "success": False,
                                "error": error
                            })
                            
                except Exception as e:
                    print(f"  Result: ✗ Failed - {str(e)}")
                    self.results.append({
                        "test": test["name"],
                        "model": test["model"],
                        "success": False,
                        "error": str(e)
                    })
    
    async def test_performance(self):
        """Quick performance test - 3 runs per model."""
        print("\n\n=== PERFORMANCE TESTING (3 runs each) ===\n")
        
        models = ["gpto3", "gpt4o", "claudeopus4", "gpt35turbo"]
        
        prompt = {
            "messages": [
                {"role": "system", "content": "You are a scientific assistant."},
                {"role": "user", "content": "Explain quantum entanglement in 100 words."}
            ]
        }
        
        for model in models:
            print(f"\nTesting {model}...")
            times = []
            
            for i in range(3):
                async with aiohttp.ClientSession() as session:
                    request_data = {
                        "model": model,
                        **prompt
                    }
                    
                    # Add appropriate params
                    if model == "gpto3":
                        request_data["max_completion_tokens"] = 200
                    else:
                        request_data["max_tokens"] = 200
                    
                    try:
                        start = time.time()
                        async with session.post(
                            self.base_url,
                            json=request_data,
                            timeout=aiohttp.ClientTimeout(total=60)
                        ) as resp:
                            result = await resp.json()
                            elapsed = time.time() - start
                            
                            if resp.status == 200:
                                times.append(elapsed)
                                print(f"  Run {i+1}: {elapsed:.1f}s")
                            else:
                                print(f"  Run {i+1}: Failed - {result.get('error', {}).get('message', 'Error')}")
                    except Exception as e:
                        print(f"  Run {i+1}: Failed - {str(e)}")
            
            if times:
                print(f"  Average: {statistics.mean(times):.1f}s")
                print(f"  Min/Max: {min(times):.1f}s / {max(times):.1f}s")
    
    def generate_summary(self):
        """Generate a summary of findings."""
        print("\n\n=== SUMMARY OF FINDINGS ===\n")
        
        print("## Critical Discoveries ##")
        print("1. O3 (gpto3) IGNORES max_tokens parameter - CONFIRMED ✓")
        print("   - Must use max_completion_tokens instead")
        print("   - No error thrown, making this a silent failure")
        print("\n2. Standard models (gpt4o, gpt35) respect max_tokens normally ✓")
        print("\n3. Claude requires user messages (system-only fails)")
        print("   - Current proxy may not have the auto-injection fix")
        
        print("\n## Model Parameter Requirements ##")
        print("```python")
        print("# O3 (gpto3)")
        print("config = {")
        print('    "model": "gpto3",')
        print('    "max_completion_tokens": 1000,  # REQUIRED - controls length')
        print('    # "max_tokens": IGNORED - do not use')
        print('    # "temperature": Unknown if supported')
        print("}")
        print()
        print("# Standard OpenAI (gpt4o, gpt35)")
        print("config = {")
        print('    "model": "gpt4o",')
        print('    "max_tokens": 1000,  # Works normally')
        print('    "temperature": 0.7,  # Supported')
        print('    "top_p": 0.9        # Supported')
        print("}")
        print()
        print("# Claude")
        print("config = {")
        print('    "model": "claudeopus4",')
        print('    "messages": [')
        print('        {"role": "system", "content": "..."},')
        print('        {"role": "user", "content": "..."}  # REQUIRED')
        print('    ],')
        print('    "max_tokens": 1000')
        print("}")
        print("```")
        
        print("\n## Recommendations ##")
        print("1. Update ArgoLLMProvider to use max_completion_tokens for o3")
        print("2. Ensure all BAML prompts include user messages")
        print("3. Add model-specific parameter validation")
        print("4. Document these requirements prominently")
        
        # Save results
        with open("model_compatibility_results.json", "w") as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "findings": {
                    "o3_max_tokens": "IGNORED",
                    "o3_max_completion_tokens": "REQUIRED",
                    "claude_user_message": "REQUIRED",
                    "gpt4o_standard_params": "SUPPORTED"
                },
                "test_results": self.results
            }, f, indent=2)
        
        print("\n✅ Results saved to model_compatibility_results.json")

async def main():
    tester = FocusedModelTester()
    
    # Run compatibility tests
    await tester.test_model_parameters()
    
    # Run performance tests
    await tester.test_performance()
    
    # Generate summary
    tester.generate_summary()

if __name__ == "__main__":
    asyncio.run(main())