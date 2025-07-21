#!/usr/bin/env python3
"""
Test flexible parsing approaches that could work with narrative LLM outputs.

This explores alternatives to strict JSON parsing that might better accommodate
reasoning models like GPT-o3.
"""

import asyncio
import json
import re
from typing import Dict, Any, Optional
import httpx
from datetime import datetime


class FlexibleParser:
    """Parse structured data from various LLM output formats."""
    
    @staticmethod
    def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
        """Try to extract JSON from text that might contain other content."""
        # Look for JSON blocks in markdown
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # Look for raw JSON
        try:
            # Find first { and last }
            start = text.find('{')
            end = text.rfind('}')
            if start >= 0 and end > start:
                potential_json = text[start:end+1]
                return json.loads(potential_json)
        except:
            pass
        
        return None
    
    @staticmethod
    def extract_structured_from_narrative(text: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """Extract structured data from narrative text using patterns."""
        result = {}
        
        # Define extraction patterns for common structures
        patterns = {
            'primary_objective': [
                r'Primary (?:Research )?Objective:\s*(.+?)(?:\n|$)',
                r'1\.\s*\*?\*?Primary.*?:\s*(.+?)(?:\n|$)',
                r'Main (?:Research )?Goal:\s*(.+?)(?:\n|$)',
            ],
            'sub_objectives': [
                r'Sub-objectives?:\s*\n((?:[-•]\s*.+\n?)+)',
                r'2\.\s*\*?\*?Sub-objectives.*?:\s*\n((?:[-•]\s*.+\n?)+)',
            ],
            'constraints': [
                r'Constraints?:\s*\n((?:[-•]\s*.+\n?)+)',
                r'3\.\s*\*?\*?.*?Constraints.*?:\s*\n((?:[-•]\s*.+\n?)+)',
            ],
            'key_terms': [
                r'Key (?:Scientific )?Terms.*?:\s*\n((?:[-•]\s*.+\n?)+)',
                r'5\.\s*\*?\*?Key.*?Terms.*?:\s*\n((?:[-•]\s*.+\n?)+)',
            ]
        }
        
        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if field.endswith('_objective'):
                        result[field] = value.strip('•- ')
                    else:  # Lists
                        items = re.findall(r'[-•]\s*(.+)', value)
                        result[field] = [item.strip() for item in items]
                    break
        
        return result
    
    @staticmethod
    def hybrid_parse(text: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """Try JSON first, fall back to narrative extraction."""
        # First try to extract JSON
        json_data = FlexibleParser.extract_json_from_text(text)
        if json_data:
            return json_data
        
        # Fall back to narrative extraction
        return FlexibleParser.extract_structured_from_narrative(text, schema)


async def test_parsing_approaches():
    """Test different parsing approaches with actual LLM outputs."""
    
    # Test data: Mix of JSON and narrative formats
    test_cases = [
        {
            "name": "Pure JSON",
            "response": '{"primary_objective": "Test objective", "sub_objectives": ["Sub 1", "Sub 2"]}'
        },
        {
            "name": "JSON in Markdown",
            "response": '''Here's the analysis:
            
```json
{
    "primary_objective": "Test objective",
    "sub_objectives": ["Sub 1", "Sub 2"]
}
```'''
        },
        {
            "name": "Narrative Format (like o3)",
            "response": '''1. Primary Research Objective:
            To develop a cure for aging using nanotechnology
            
            2. Sub-objectives:
            - Map cellular aging mechanisms
            - Design biocompatible nanoparticles
            - Validate in vitro and in vivo
            
            3. Constraints:
            - Ethical: Patient safety and consent
            - Practical: Budget and resource limits
            - Scientific: Need mechanistic understanding'''
        },
        {
            "name": "Mixed Format",
            "response": '''Based on my analysis:
            
            Primary Objective: Develop aging cure with nanotech
            
            The sub-objectives include:
            • Mapping aging pathways
            • Creating delivery systems
            • Clinical validation
            
            Key constraints are ethical (safety), practical (cost), and scientific (mechanism).'''
        }
    ]
    
    parser = FlexibleParser()
    schema = {
        "primary_objective": "string",
        "sub_objectives": "array",
        "constraints": "array",
        "key_terms": "array"
    }
    
    print("Testing Flexible Parsing Approaches")
    print("=" * 60)
    
    for test in test_cases:
        print(f"\nTest Case: {test['name']}")
        print("-" * 40)
        
        # Try hybrid parsing
        result = parser.hybrid_parse(test['response'], schema)
        
        if result:
            print("✅ Successfully parsed!")
            print(f"Fields extracted: {list(result.keys())}")
            if 'primary_objective' in result:
                print(f"Primary objective: {result['primary_objective'][:50]}...")
        else:
            print("❌ Failed to parse")
        
        # Show what each method extracts
        json_result = parser.extract_json_from_text(test['response'])
        narrative_result = parser.extract_structured_from_narrative(test['response'], schema)
        
        print(f"  JSON extraction: {'✓' if json_result else '✗'}")
        print(f"  Narrative extraction: {'✓' if narrative_result else '✗'}")


async def test_with_real_llm():
    """Test with actual LLM to see how well flexible parsing works."""
    
    url = "http://localhost:8000/v1/chat/completions"
    
    # Test prompts that might produce different formats
    prompts = [
        {
            "name": "No format specified",
            "content": "Analyze the research goal: Develop a cure for aging. What is the primary objective and sub-objectives?"
        },
        {
            "name": "Structured request",
            "content": "Analyze the research goal: Develop a cure for aging. Provide: 1) Primary objective 2) Sub-objectives 3) Constraints"
        },
        {
            "name": "JSON requested",
            "content": "Analyze the research goal: Develop a cure for aging. Return as JSON with primary_objective and sub_objectives fields."
        }
    ]
    
    parser = FlexibleParser()
    schema = {"primary_objective": "string", "sub_objectives": "array"}
    
    print("\n\nTesting with Real LLM (gpto3)")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for prompt in prompts:
            print(f"\nPrompt type: {prompt['name']}")
            print("-" * 40)
            
            try:
                response = await client.post(url, json={
                    "model": "gpto3",
                    "messages": [{"role": "user", "content": prompt['content']}],
                    "temperature": 0.7,
                    "max_tokens": 500
                })
                
                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content']
                    print(f"Response preview: {content[:150]}...")
                    
                    # Try parsing
                    result = parser.hybrid_parse(content, schema)
                    if result:
                        print("✅ Successfully parsed!")
                        print(f"Extracted: {json.dumps(result, indent=2)[:200]}...")
                    else:
                        print("❌ Could not parse structured data")
                        
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_parsing_approaches())
    print("\n" + "="*60 + "\n")
    asyncio.run(test_with_real_llm())