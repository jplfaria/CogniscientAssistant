#!/usr/bin/env python3
"""
Simple test of Claude's reasoning behavior.
"""

import asyncio
import json
import httpx


async def test_claude_reasoning():
    """Test Claude's behavior with reasoning requests."""
    
    url = "http://localhost:8000/v1/chat/completions"
    
    print("Testing Claude Opus 4 Reasoning Behavior")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # First, verify Claude is working
        print("\n1. Testing basic Claude response:")
        print("-" * 40)
        
        try:
            response = await client.post(url, json={
                "model": "claudeopus4",
                "messages": [{
                    "role": "user",
                    "content": "What is 2+2? Answer in one word."
                }],
                "temperature": 0,
                "max_tokens": 10
            })
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                print(f"✅ Claude responds: {content}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                return
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return
        
        # Test reasoning request
        print("\n2. Testing reasoning request:")
        print("-" * 40)
        
        try:
            response = await client.post(url, json={
                "model": "claudeopus4",
                "messages": [{
                    "role": "user",
                    "content": """Think step by step about how to cure aging.

Provide your response as:
{
    "reasoning": "your thinking process",
    "hypothesis": "your conclusion"
}"""
                }],
                "temperature": 0.7,
                "max_tokens": 1000
            })
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                print(f"Response length: {len(content)} chars")
                
                # Check for reasoning
                if "reasoning" in content.lower():
                    print("✅ Claude includes reasoning")
                else:
                    print("❓ No explicit reasoning field")
                
                print(f"\nPreview: {content[:400]}...")
                
                # Try to extract JSON
                try:
                    json_start = content.find('{')
                    if json_start >= 0:
                        json_data = json.loads(content[json_start:])
                        if 'reasoning' in json_data:
                            print(f"\n✅ Reasoning in JSON: {len(json_data['reasoning'])} chars")
                except:
                    print("\n❌ Could not parse as JSON")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Compare with o3
        print("\n\n3. Comparing with o3:")
        print("-" * 40)
        
        for model in ["claudeopus4", "gpto3"]:
            print(f"\n{model}:")
            try:
                response = await client.post(url, json={
                    "model": model,
                    "messages": [{
                        "role": "user",
                        "content": "Show me your reasoning for: How might we cure aging? Format as JSON with 'reasoning' and 'hypothesis' fields."
                    }],
                    "temperature": 0.7,
                    "max_tokens": 800
                })
                
                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content']
                    
                    # Quick checks
                    has_json = '{' in content
                    refuses = "private" in content.lower() or "can't share" in content.lower()
                    
                    print(f"  Has JSON: {has_json}")
                    print(f"  Refuses reasoning: {refuses}")
                    
                    if refuses:
                        print(f"  ⚠️ REFUSAL: {content[:200]}")
                    else:
                        print(f"  ✅ Shares reasoning")
                        print(f"  Preview: {content[:200]}...")
                        
            except Exception as e:
                print(f"  Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_claude_reasoning())