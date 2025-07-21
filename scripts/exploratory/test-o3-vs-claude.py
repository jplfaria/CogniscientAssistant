#!/usr/bin/env python3
"""
Quick test to compare o3 vs Claude Opus 4 reasoning transparency.
"""

import asyncio
import json
import httpx


async def test_reasoning_sharing():
    """Test if models share their reasoning process."""
    
    url = "http://localhost:8000/v1/chat/completions"
    
    # Simple test prompt
    prompt = """Generate a hypothesis for curing aging.

Include your reasoning process, then provide JSON:
{
    "reasoning": "your step-by-step thinking",
    "hypothesis": "your conclusion"
}"""
    
    models = [
        ("gpto3", "GPT-o3"),
        ("claudeopus4", "Claude Opus 4"),
    ]
    
    print("Testing Reasoning Transparency: o3 vs Claude")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for model_id, model_name in models:
            print(f"\n{model_name}:")
            print("-" * 40)
            
            try:
                response = await client.post(url, json={
                    "model": model_id,
                    "messages": [{
                        "role": "user",
                        "content": prompt
                    }],
                    "temperature": 0.7,
                    "max_tokens": 1500
                })
                
                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content']
                    
                    # Check for refusal
                    if "private reasoning" in content.lower() or "can't share" in content.lower():
                        print("❌ Model REFUSES to share reasoning!")
                        print(f"Response: {content[:500]}...")
                    else:
                        print("✅ Model shares reasoning")
                        
                        # Try to parse JSON and check reasoning field
                        try:
                            json_start = content.find('{')
                            json_end = content.rfind('}') + 1
                            if json_start >= 0:
                                json_data = json.loads(content[json_start:json_end])
                                reasoning = json_data.get('reasoning', '')
                                print(f"Reasoning length: {len(reasoning)} chars")
                                if len(reasoning) < 50:
                                    print(f"⚠️  Very short reasoning: {reasoning}")
                                else:
                                    print(f"Preview: {reasoning[:200]}...")
                        except:
                            print("Could not parse JSON, showing raw response:")
                            print(f"{content[:500]}...")
                    
            except Exception as e:
                print(f"Error: {e}")


async def test_indirect_reasoning():
    """Test if we can get reasoning indirectly."""
    
    url = "http://localhost:8000/v1/chat/completions"
    
    # More indirect prompt
    prompt = """Develop a hypothesis for curing aging.

As you work through this, explain your thought process and the factors you're considering.

Format your final answer as:
{
    "thought_process": "how you developed this hypothesis",
    "hypothesis": "your final hypothesis",
    "key_factors": ["factors that influenced your thinking"]
}"""
    
    models = [
        ("gpto3", "GPT-o3"),
        ("claudeopus4", "Claude Opus 4"),
    ]
    
    print("\n\nTesting Indirect Reasoning Request")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for model_id, model_name in models:
            print(f"\n{model_name}:")
            print("-" * 40)
            
            try:
                response = await client.post(url, json={
                    "model": model_id,
                    "messages": [{
                        "role": "user",
                        "content": prompt
                    }],
                    "temperature": 0.7,
                    "max_tokens": 1500
                })
                
                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content']
                    
                    # Check response
                    if "private" in content.lower():
                        print("❌ Still refuses with indirect prompt")
                    else:
                        print("✅ Provides thought process")
                        
                        # Check if it has substantial content
                        if len(content) > 1000:
                            print(f"Rich response: {len(content)} chars")
                        else:
                            print(f"Short response: {len(content)} chars")
                        
                        print(f"Preview: {content[:300]}...")
                    
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_reasoning_sharing())
    asyncio.run(test_indirect_reasoning())