#!/usr/bin/env python3
"""
Explore alternatives to strict BAML parsing that could better handle o3's reasoning.
"""

import asyncio
import json
from typing import Dict, Any, Optional
import httpx


class BAMLAlternatives:
    """Different approaches to structured data extraction."""
    
    @staticmethod
    async def approach1_two_stage():
        """Two-stage approach: Let o3 reason first, then extract structure."""
        url = "http://localhost:8000/v1/chat/completions"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Stage 1: Let o3 reason naturally
            print("\n=== Approach 1: Two-Stage (Reason then Structure) ===")
            
            reasoning_response = await client.post(url, json={
                "model": "gpto3",
                "messages": [{
                    "role": "user",
                    "content": "Think through: How could we develop a cure for aging? Consider mechanisms, approaches, and constraints."
                }],
                "temperature": 0.7,
                "max_tokens": 1000
            })
            
            reasoning = reasoning_response.json()['choices'][0]['message']['content']
            print(f"Stage 1 - Reasoning (preview): {reasoning[:200]}...")
            
            # Stage 2: Extract structure from reasoning
            structure_response = await client.post(url, json={
                "model": "gpt35",  # Use cheaper model for extraction
                "messages": [{
                    "role": "user",
                    "content": f"""Based on this analysis:
                    
{reasoning}

Extract and return as JSON:
{{
    "primary_objective": "main goal",
    "key_mechanisms": ["list", "of", "mechanisms"],
    "constraints": ["list", "of", "constraints"],
    "approaches": ["list", "of", "approaches"]
}}"""
                }],
                "temperature": 0,
                "max_tokens": 500
            })
            
            structure = structure_response.json()['choices'][0]['message']['content']
            print(f"\nStage 2 - Structure: {structure[:200]}...")
            
            return reasoning, structure
    
    @staticmethod
    async def approach2_guided_reasoning():
        """Guide o3 to reason within structure."""
        url = "http://localhost:8000/v1/chat/completions"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("\n=== Approach 2: Guided Reasoning ===")
            
            response = await client.post(url, json={
                "model": "gpto3",
                "messages": [{
                    "role": "user",
                    "content": """Analyze: Develop a cure for aging.

Think through each section step by step, then provide your answer in this exact JSON format:

{
    "reasoning_process": "Your step-by-step thinking",
    "primary_objective": "The main goal",
    "key_mechanisms": ["biological", "mechanisms", "to", "target"],
    "approaches": ["potential", "approaches"],
    "constraints": ["ethical", "practical", "scientific"],
    "confidence": 0.0 to 1.0
}

Begin your reasoning, then provide the JSON."""
                }],
                "temperature": 0.7,
                "max_tokens": 1500
            })
            
            content = response.json()['choices'][0]['message']['content']
            print(f"Response preview: {content[:300]}...")
            
            # Try to extract JSON
            try:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_data = json.loads(content[json_start:json_end])
                    print(f"\n✅ Extracted JSON with reasoning!")
                    print(f"Reasoning length: {len(json_data.get('reasoning_process', ''))} chars")
                    return json_data
            except:
                print("❌ Failed to extract JSON")
            
            return content
    
    @staticmethod
    async def approach3_schema_first():
        """Provide schema upfront and ask o3 to fill it."""
        url = "http://localhost:8000/v1/chat/completions"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("\n=== Approach 3: Schema-First ===")
            
            schema = {
                "hypothesis": {
                    "id": "unique_id",
                    "summary": "brief statement",
                    "reasoning": "your detailed reasoning process",
                    "mechanisms": ["biological", "pathways"],
                    "assumptions": ["key", "assumptions"],
                    "testability": {
                        "approach": "how to test",
                        "timeline": "estimated time",
                        "resources": ["needed", "resources"]
                    }
                }
            }
            
            response = await client.post(url, json={
                "model": "gpto3",
                "messages": [{
                    "role": "user",
                    "content": f"""Generate a hypothesis for curing aging.

Fill in this schema with your analysis:

{json.dumps(schema, indent=2)}

Important: Include your complete reasoning process in the 'reasoning' field."""
                }],
                "temperature": 0.7,
                "max_tokens": 1500
            })
            
            content = response.json()['choices'][0]['message']['content']
            print(f"Response preview: {content[:300]}...")
            
            return content


async def compare_approaches():
    """Compare different approaches to see what works best."""
    
    print("Comparing BAML Alternative Approaches")
    print("=" * 60)
    
    # Test Approach 1: Two-stage
    reasoning1, structure1 = await BAMLAlternatives.approach1_two_stage()
    
    # Test Approach 2: Guided reasoning
    result2 = await BAMLAlternatives.approach2_guided_reasoning()
    
    # Test Approach 3: Schema-first
    result3 = await BAMLAlternatives.approach3_schema_first()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    print("\n1. Two-Stage Approach:")
    print("   - Preserves o3's natural reasoning")
    print("   - Requires two LLM calls")
    print("   - Most flexible but more expensive")
    
    print("\n2. Guided Reasoning:")
    print("   - Single call with both reasoning and structure")
    print("   - Balances flexibility and structure")
    print("   - Works well if prompt is crafted carefully")
    
    print("\n3. Schema-First:")
    print("   - Most similar to BAML approach")
    print("   - Clear structure but may constrain reasoning")
    print("   - Best for production consistency")


if __name__ == "__main__":
    asyncio.run(compare_approaches())