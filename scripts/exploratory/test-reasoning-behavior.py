#!/usr/bin/env python3
"""
Test how different models handle reasoning requests, especially comparing o3 and Claude.
"""

import asyncio
import json
import httpx
from datetime import datetime


async def test_reasoning_transparency():
    """Test how different models respond to reasoning requests."""
    
    url = "http://localhost:8000/v1/chat/completions"
    
    # Test prompts that request reasoning
    test_prompts = [
        {
            "name": "Direct reasoning request",
            "prompt": """Generate a hypothesis for curing aging.

Include your complete reasoning process, then provide the result in JSON format:
{
    "reasoning": "your detailed step-by-step thinking",
    "hypothesis": "your conclusion",
    "confidence": 0.0 to 1.0
}"""
        },
        {
            "name": "Embedded reasoning",
            "prompt": """Think through how to cure aging step by step.

Format your response as:
{
    "thought_process": "your complete thinking",
    "conclusion": "final hypothesis",
    "key_insights": ["insight1", "insight2"]
}"""
        },
        {
            "name": "Natural reasoning flow",
            "prompt": """Analyze the challenge of curing aging. Show your reasoning process as you work through the problem, then summarize in JSON."""
        }
    ]
    
    models = [
        ("gpto3", "GPT-o3 (reasoning model)"),
        ("claudeopus4", "Claude Opus 4"),
        ("gpt4o", "GPT-4o"),
    ]
    
    print("Testing Model Reasoning Transparency")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for model_id, model_name in models:
            print(f"\n{'='*80}")
            print(f"MODEL: {model_name}")
            print(f"{'='*80}")
            
            for test in test_prompts:
                print(f"\nTest: {test['name']}")
                print("-" * 60)
                
                try:
                    response = await client.post(url, json={
                        "model": model_id,
                        "messages": [{
                            "role": "user",
                            "content": test['prompt']
                        }],
                        "temperature": 0.7,
                        "max_tokens": 2000
                    })
                    
                    if response.status_code == 200:
                        content = response.json()['choices'][0]['message']['content']
                        
                        # Check for reasoning content
                        print(f"Response length: {len(content)} chars")
                        
                        # Look for signs of hidden reasoning
                        if "private reasoning" in content.lower() or "can't share" in content.lower():
                            print("⚠️  Model refuses to share reasoning")
                        elif "reasoning" in content or "thought" in content.lower():
                            print("✅ Model shares reasoning")
                        else:
                            print("❓ Unclear if reasoning is shared")
                        
                        # Show preview
                        print(f"\nPreview: {content[:300]}...")
                        
                        # Try to extract JSON
                        try:
                            json_start = content.find('{')
                            json_end = content.rfind('}') + 1
                            if json_start >= 0 and json_end > json_start:
                                json_data = json.loads(content[json_start:json_end])
                                reasoning_field = json_data.get('reasoning') or json_data.get('thought_process') or json_data.get('reasoning_process')
                                if reasoning_field:
                                    print(f"\n📊 Reasoning length in JSON: {len(str(reasoning_field))} chars")
                                    if len(str(reasoning_field)) < 100:
                                        print(f"   Content: {reasoning_field}")
                                else:
                                    print("\n❌ No reasoning field in JSON")
                        except:
                            print("\n❌ Could not parse JSON")
                        
                except Exception as e:
                    print(f"Error: {e}")
                
                await asyncio.sleep(1)  # Rate limiting


async def test_specific_reasoning_formats():
    """Test specific formats that might work better with different models."""
    
    url = "http://localhost:8000/v1/chat/completions"
    
    print("\n\n" + "="*80)
    print("Testing Alternative Reasoning Formats")
    print("="*80)
    
    # Test different ways to get reasoning
    formats = [
        {
            "name": "Chain of Thought",
            "prompt": """Let's think step by step about curing aging.

Step 1: What are the main causes of aging?
Step 2: Which causes are most addressable?
Step 3: What interventions could work?
Step 4: Formulate a specific hypothesis.

After your analysis, provide a JSON summary."""
        },
        {
            "name": "Reasoning as Commentary",
            "prompt": """Generate a hypothesis for curing aging. As you develop it, explain your thinking process.

Use this format:
{
    "hypothesis": "your hypothesis",
    "development_notes": "how you arrived at this hypothesis",
    "assumptions": ["key assumptions made"],
    "confidence_rationale": "why you have this confidence level"
}"""
        },
        {
            "name": "Indirect Reasoning",
            "prompt": """What hypothesis would you generate for curing aging, and what factors influenced your choice?

Provide your answer as:
{
    "hypothesis": "the hypothesis",
    "influencing_factors": ["factor1", "factor2"],
    "decision_process": "how these factors led to your hypothesis"
}"""
        }
    ]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for model_id in ["gpto3", "claudeopus4"]:
            print(f"\n\nModel: {model_id}")
            print("-" * 40)
            
            for fmt in formats:
                print(f"\nFormat: {fmt['name']}")
                
                try:
                    response = await client.post(url, json={
                        "model": model_id,
                        "messages": [{
                            "role": "user",
                            "content": fmt['prompt']
                        }],
                        "temperature": 0.7,
                        "max_tokens": 1500
                    })
                    
                    if response.status_code == 200:
                        content = response.json()['choices'][0]['message']['content']
                        
                        # Quick analysis
                        has_steps = "step" in content.lower()
                        has_json = "{" in content
                        refuses = "private" in content.lower() or "can't share" in content.lower()
                        
                        print(f"  ✓ Has steps: {has_steps}")
                        print(f"  ✓ Has JSON: {has_json}")
                        print(f"  ⚠️  Refuses reasoning: {refuses}")
                        
                        if refuses:
                            print(f"  Refusal text: {content[:200]}")
                        
                except Exception as e:
                    print(f"  Error: {e}")
                
                await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(test_reasoning_transparency())
    asyncio.run(test_specific_reasoning_formats())