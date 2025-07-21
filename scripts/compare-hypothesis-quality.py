#!/usr/bin/env python3
"""
Compare hypothesis quality between models.
"""

import asyncio
import json
import httpx
from datetime import datetime


async def compare_hypothesis_generation():
    """Compare how different models generate scientific hypotheses."""
    
    url = "http://localhost:8000/v1/chat/completions"
    
    # Scientific hypothesis prompt
    prompt = """Generate a novel hypothesis for reversing cellular aging using nanotechnology.

Requirements:
- Must be testable with current technology
- Should address a specific aging mechanism
- Include potential risks

Format as JSON:
{
    "hypothesis": "clear statement of the hypothesis",
    "mechanism": "biological mechanism addressed",
    "approach": "how it would work",
    "testability": "how to test it",
    "risks": ["potential risks"],
    "novelty": "what makes this novel"
}"""
    
    models = [
        ("gpto3", "GPT-o3"),
        ("claudeopus4", "Claude Opus 4"),
        ("gpt4o", "GPT-4o"),
    ]
    
    print("Comparing Hypothesis Generation Quality")
    print("=" * 80)
    print(f"Prompt: Nanotechnology for cellular aging")
    print("=" * 80)
    
    results = {}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for model_id, model_name in models:
            print(f"\n{model_name}:")
            print("-" * 60)
            
            start_time = datetime.now()
            
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
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content']
                    
                    # Parse JSON
                    try:
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        hypothesis_data = json.loads(content[json_start:json_end])
                        
                        # Analyze quality
                        print(f"✅ Valid JSON response in {duration:.1f}s")
                        print(f"\nHypothesis: {hypothesis_data.get('hypothesis', 'N/A')[:150]}...")
                        print(f"Mechanism: {hypothesis_data.get('mechanism', 'N/A')[:100]}...")
                        print(f"Novelty: {hypothesis_data.get('novelty', 'N/A')[:100]}...")
                        
                        # Score quality factors
                        quality_score = {
                            "has_hypothesis": bool(hypothesis_data.get('hypothesis')),
                            "has_mechanism": bool(hypothesis_data.get('mechanism')),
                            "has_approach": bool(hypothesis_data.get('approach')),
                            "has_testability": bool(hypothesis_data.get('testability')),
                            "has_risks": bool(hypothesis_data.get('risks')),
                            "has_novelty": bool(hypothesis_data.get('novelty')),
                            "response_time": duration,
                            "hypothesis_length": len(hypothesis_data.get('hypothesis', '')),
                            "approach_length": len(hypothesis_data.get('approach', ''))
                        }
                        
                        completeness = sum([
                            quality_score['has_hypothesis'],
                            quality_score['has_mechanism'],
                            quality_score['has_approach'],
                            quality_score['has_testability'],
                            quality_score['has_risks'],
                            quality_score['has_novelty']
                        ])
                        
                        print(f"\nCompleteness: {completeness}/6 fields")
                        print(f"Detail level: {quality_score['hypothesis_length'] + quality_score['approach_length']} chars")
                        
                        results[model_name] = {
                            "data": hypothesis_data,
                            "quality": quality_score,
                            "completeness": completeness
                        }
                        
                    except Exception as e:
                        print(f"❌ JSON parsing failed: {e}")
                        print(f"Raw response: {content[:500]}...")
                        
            except Exception as e:
                print(f"❌ Request failed: {e}")
    
    # Summary comparison
    print("\n\n" + "="*80)
    print("SUMMARY COMPARISON")
    print("="*80)
    
    for model_name, result in results.items():
        if 'quality' in result:
            q = result['quality']
            print(f"\n{model_name}:")
            print(f"  Completeness: {result['completeness']}/6")
            print(f"  Response time: {q['response_time']:.1f}s")
            print(f"  Detail level: {q['hypothesis_length'] + q['approach_length']} chars")
            print(f"  Has all required fields: {'Yes' if result['completeness'] == 6 else 'No'}")
    
    # Recommendation
    print("\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)
    
    if results:
        # Find most complete
        most_complete = max(results.items(), key=lambda x: x[1].get('completeness', 0))
        # Find fastest
        fastest = min(results.items(), key=lambda x: x[1].get('quality', {}).get('response_time', 999))
        
        print(f"Most complete: {most_complete[0]} ({most_complete[1]['completeness']}/6 fields)")
        print(f"Fastest: {fastest[0]} ({fastest[1]['quality']['response_time']:.1f}s)")
        
        if most_complete[0] == fastest[0]:
            print(f"\n🏆 Winner: {most_complete[0]} - Best balance of quality and speed")
        else:
            print(f"\n⚖️  Trade-off: {most_complete[0]} for quality, {fastest[0]} for speed")


if __name__ == "__main__":
    asyncio.run(compare_hypothesis_generation())