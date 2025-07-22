#!/usr/bin/env python3
"""
Minimal test case for Peng - reproduces BAML's exact request pattern
"""

import requests
import json
import time

def test_baml_request_pattern():
    """Send exactly what BAML sends to reproduce the issue."""
    
    base_url = "http://localhost:8000/v1/chat/completions"
    
    # This is the EXACT request BAML sends (from the logs)
    baml_request = {
        "model": "claudeopus4",
        "temperature": 0.7,
        "max_tokens": 4000,
        "timeout_seconds": 60,
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are parsing a research goal into structured components.\n\nResearch Goal: Develop a cure for aging using nanotechnology\n\nDomain: biomedical engineering\n\nAnalyze this goal and extract:\n1. The primary research objective (one clear statement)\n2. Sub-objectives that support the main goal\n3. Implied constraints (ethical, practical, scientific)\n4. Relevant hypothesis categories (mechanistic, therapeutic, etc.)\n5. Key scientific terms and concepts\n6. Success criteria - what outcomes would satisfy this goal\n\nBe thorough but concise in your analysis.\n\nRespond in valid JSON format matching the ParsedResearchGoal schema:\n{\n  \"primary_objective\": \"single clear statement\",\n  \"sub_objectives\": [\"array\", \"of\", \"objectives\"],\n  \"implied_constraints\": [\"ethical\", \"practical\", \"scientific\"],\n  \"hypothesis_categories\": [\"mechanistic\", \"therapeutic\", \"etc\"],\n  \"key_terms\": [\"important\", \"scientific\", \"terms\"],\n  \"success_criteria\": [\"measurable\", \"outcomes\"]\n}"
                    }
                ]
            }
        ]
    }
    
    print("Minimal test case for BAML + Claude issue")
    print("=" * 60)
    print("\nThis is the EXACT request BAML sends:")
    print(json.dumps(baml_request, indent=2)[:500] + "...")
    print("\nKey points:")
    print("1. Only has system message (no user message)")
    print("2. Content is in array format: [{\"type\": \"text\", \"text\": \"...\"}]")
    print("3. Includes timeout_seconds parameter")
    print("\nTesting...")
    
    try:
        start_time = time.time()
        response = requests.post(
            base_url,
            headers={"Content-Type": "application/json"},
            json=baml_request,
            timeout=65  # Slightly higher than the 60s in request
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ SUCCESS! Response time: {elapsed:.2f}s")
            print("Response preview:", str(result)[:200] + "...")
        else:
            print(f"\n❌ FAILED with status {response.status_code}")
            try:
                error = response.json()
                print(f"Error: {json.dumps(error, indent=2)}")
            except:
                print(f"Error: {response.text[:500]}")
                    
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out after 65 seconds")
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("\nTo reproduce:")
    print("1. Start argo-proxy with latest fix/system_message branch")
    print("2. Run this script")
    print("3. Should fail with: 'expected string or bytes-like object, got dict'")
    print("\nThe issue appears when:")
    print("- Request has ONLY a system message (no user message)")
    print("- System content is in array format")
    print("- Model is Claude")

if __name__ == "__main__":
    test_baml_request_pattern()