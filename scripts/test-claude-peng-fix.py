#!/usr/bin/env python3
"""
Test Claude compatibility with Peng's official fix for array content format.
"""

import requests
import json
import time

def test_claude_with_array_format():
    """Test Claude with BAML's array format using Peng's fix."""
    
    base_url = "http://localhost:8000/v1/chat/completions"
    
    # This is exactly what BAML sends
    test_data = {
        "model": "claudeopus4",
        "messages": [
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a helpful assistant"}]
            },
            {
                "role": "user",
                "content": "Say hello in 5 words or less"
            }
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    print("Testing Claude with Peng's fix for array content format...")
    print("Model: claudeopus4")
    print("System content format: Array [{'type': 'text', 'text': '...'}]")
    print("-" * 60)
    
    try:
        start_time = time.time()
        response = requests.post(
            base_url,
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"✅ SUCCESS! Response time: {elapsed:.2f}s")
            print(f"Response: {content}")
            print("\nPeng's fix is working! Claude now accepts array format for system messages.")
        else:
            print(f"❌ FAILED with status {response.status_code}")
            try:
                error = response.json()
                print(f"Error: {json.dumps(error, indent=2)}")
            except:
                print(f"Error: {response.text[:500]}")
            print("\nPeng's fix may need adjustment or there's another issue.")
                    
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 30 seconds")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    # Check if proxy is running
    try:
        health = requests.get("http://localhost:8000/health", timeout=2)
        print(f"Proxy health check: {health.status_code}")
    except:
        print("❌ Argo proxy not running! Start with: ./scripts/argo-proxy.sh start")
        exit(1)
    
    test_claude_with_array_format()