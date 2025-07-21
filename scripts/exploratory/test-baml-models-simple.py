#!/usr/bin/env python3
"""
Simplified test script to diagnose model response formats.
This version tests raw API calls to understand response differences.
"""

import asyncio
import json
import aiohttp
import os
from datetime import datetime

# Test configuration
TEST_MODELS = [
    "gpt4o",
    "gpt35", 
    "claudeopus4",
    "gpto3",  # o3 model
]

ARGO_BASE_URL = "http://localhost:8000/v1"

# Test prompt that mimics BAML's ParseResearchGoal
TEST_PROMPT = """You are parsing a research goal into structured components.

Research Goal: Develop a hypothesis for improving cancer immunotherapy effectiveness

Domain: oncology

Analyze this goal and extract:
1. The primary research objective (one clear statement)
2. Sub-objectives that support the main goal
3. Implied constraints (ethical, practical, scientific)
4. Relevant hypothesis categories (mechanistic, therapeutic, etc.)
5. Key scientific terms and concepts
6. Success criteria - what outcomes would satisfy this goal

Be thorough but concise in your analysis.

Respond with a JSON object containing these fields:
{
    "primary_objective": "string",
    "sub_objectives": ["array of strings"],
    "implied_constraints": ["array of strings"],
    "suggested_categories": ["array of strings"],
    "key_terms": ["array of strings"],
    "success_criteria": ["array of strings"]
}"""


async def test_model_raw(session: aiohttp.ClientSession, model: str):
    """Test a model with raw API call"""
    print(f"\n{'='*60}")
    print(f"Testing Model: {model}")
    print(f"{'='*60}")
    
    # Prepare request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('ARGO_API_KEY', 'dummy-key')}"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": TEST_PROMPT}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        # Make API call
        async with session.post(
            f"{ARGO_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            
            if response.status == 200:
                data = await response.json()
                content = data['choices'][0]['message']['content']
                
                print(f"✅ SUCCESS - Got response from {model}")
                print(f"\nRaw Response (first 500 chars):")
                print(content[:500])
                
                # Try to parse as JSON
                try:
                    # Handle potential markdown code blocks
                    if "```json" in content:
                        json_start = content.find("```json") + 7
                        json_end = content.find("```", json_start)
                        json_str = content[json_start:json_end].strip()
                    elif "```" in content:
                        json_start = content.find("```") + 3
                        json_end = content.find("```", json_start)
                        json_str = content[json_start:json_end].strip()
                    else:
                        json_str = content.strip()
                    
                    parsed = json.loads(json_str)
                    print(f"\n✅ JSON Parsed Successfully!")
                    print(f"Fields found: {list(parsed.keys())}")
                    
                    return {
                        "model": model,
                        "status": "success",
                        "json_parseable": True,
                        "fields": list(parsed.keys()),
                        "sample_response": content[:200]
                    }
                    
                except json.JSONDecodeError as e:
                    print(f"\n⚠️  JSON Parse Failed: {e}")
                    print(f"Attempted to parse: {json_str[:100]}...")
                    
                    return {
                        "model": model,
                        "status": "success",
                        "json_parseable": False,
                        "parse_error": str(e),
                        "sample_response": content[:200]
                    }
                    
            else:
                error_text = await response.text()
                print(f"❌ API Error - Status: {response.status}")
                print(f"Error: {error_text[:200]}")
                
                return {
                    "model": model,
                    "status": "api_error",
                    "error": error_text[:200],
                    "status_code": response.status
                }
                
    except asyncio.TimeoutError:
        print(f"❌ Timeout - Model {model} took too long to respond")
        return {
            "model": model,
            "status": "timeout"
        }
    except Exception as e:
        print(f"❌ Exception - {type(e).__name__}: {str(e)}")
        return {
            "model": model,
            "status": "exception",
            "error": str(e),
            "error_type": type(e).__name__
        }


async def main():
    """Run tests on all models"""
    print("Model Response Format Testing")
    print(f"Testing API: {ARGO_BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Check if Argo proxy is accessible
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ARGO_BASE_URL}/models", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    print("✅ Argo proxy is accessible")
                else:
                    print(f"⚠️  Argo proxy returned status {resp.status}")
    except Exception as e:
        print(f"❌ Cannot connect to Argo proxy: {e}")
        print("Make sure to run: python scripts/argo_proxy.py")
        return
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        for model in TEST_MODELS:
            result = await test_model_raw(session, model)
            results.append(result)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for result in results:
        model = result['model']
        status = result['status']
        
        if status == "success":
            if result['json_parseable']:
                print(f"✅ {model}: Success - JSON parseable")
            else:
                print(f"⚠️  {model}: Success - JSON NOT parseable")
        else:
            print(f"❌ {model}: Failed - {status}")
    
    # Analysis
    print(f"\n{'='*60}")
    print("ANALYSIS")
    print(f"{'='*60}")
    
    json_parseable = [r for r in results if r.get('json_parseable', False)]
    json_not_parseable = [r for r in results if r['status'] == 'success' and not r.get('json_parseable', False)]
    
    if json_not_parseable:
        print(f"\nModels with non-JSON responses ({len(json_not_parseable)}):")
        for r in json_not_parseable:
            print(f"  - {r['model']}")
            print(f"    Sample: {r['sample_response'][:100]}...")
    
    if json_parseable:
        print(f"\nModels with valid JSON responses ({len(json_parseable)}):")
        for r in json_parseable:
            print(f"  - {r['model']}")
            print(f"    Fields: {r['fields']}")
    
    # Save results
    output_file = "test_results/model_response_format_test.json"
    os.makedirs("test_results", exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results
        }, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    # Recommendations
    if json_not_parseable:
        print(f"\n{'='*60}")
        print("RECOMMENDATIONS")
        print(f"{'='*60}")
        print("Some models are not returning valid JSON. Consider:")
        print("1. Adding explicit JSON formatting instructions to prompts")
        print("2. Using BAML's response parsing capabilities")
        print("3. Implementing model-specific response handlers")
        print("4. Adding response format validation and retry logic")


if __name__ == "__main__":
    asyncio.run(main())