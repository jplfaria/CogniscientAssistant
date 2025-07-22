#!/usr/bin/env python3
"""
Test to see what's actually being sent to Argo API
"""

import requests
import json

# Intercept the actual request
class LoggingSession(requests.Session):
    def request(self, method, url, **kwargs):
        print(f"\n=== ACTUAL REQUEST TO {url} ===")
        if 'json' in kwargs:
            print("JSON payload:")
            print(json.dumps(kwargs['json'], indent=2))
        return super().request(method, url, **kwargs)

# Test both simple and BAML patterns
def test_requests():
    session = LoggingSession()
    base_url = "http://localhost:8000/v1/chat/completions"
    
    # Test 1: Simple request that works
    print("\n" + "="*60)
    print("TEST 1: Simple request (system + user)")
    simple_request = {
        "model": "claudeopus4",
        "messages": [
            {"role": "system", "content": [{"type": "text", "text": "You are helpful"}]},
            {"role": "user", "content": "Hi"}
        ],
        "max_tokens": 50
    }
    
    try:
        resp = session.post(base_url, json=simple_request, timeout=10)
        print(f"Response: {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: BAML pattern (system only)
    print("\n" + "="*60)
    print("TEST 2: BAML pattern (system only)")
    baml_request = {
        "model": "claudeopus4",
        "messages": [
            {"role": "system", "content": [{"type": "text", "text": "Parse this..."}]}
        ],
        "max_tokens": 50,
        "temperature": 0.7,
        "timeout_seconds": 60
    }
    
    try:
        resp = session.post(base_url, json=baml_request, timeout=10)
        print(f"Response: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Error: {resp.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_requests()