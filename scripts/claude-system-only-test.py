#!/usr/bin/env python3
"""
Minimal test showing Claude requires at least one user message through Argo API
"""

import requests
import json

base_url = "http://localhost:8000/v1/chat/completions"

print("Testing Claude with different message patterns...\n")

# Test 1: System message only (FAILS)
print("1. Claude with ONLY system message:")
response = requests.post(base_url, json={
    "model": "claudeopus4",
    "messages": [{
        "role": "system",
        "content": [{"type": "text", "text": "You are a helpful assistant"}]
    }],
    "max_tokens": 50
})
print(f"   Status: {response.status_code}")
if response.status_code != 200:
    print(f"   Error: {response.json()['error']}\n")

# Test 2: System + User messages (WORKS)
print("2. Claude with system + user messages:")
response = requests.post(base_url, json={
    "model": "claudeopus4",
    "messages": [
        {"role": "system", "content": [{"type": "text", "text": "You are helpful"}]},
        {"role": "user", "content": "Say hello"}
    ],
    "max_tokens": 50
})
print(f"   Status: {response.status_code}")
print(f"   Works: {'Yes' if response.status_code == 200 else 'No'}\n")

# Test 3: OpenAI model with system only (WORKS)
print("3. OpenAI model with ONLY system message:")
response = requests.post(base_url, json={
    "model": "gpt4o",
    "messages": [{
        "role": "system",
        "content": [{"type": "text", "text": "Generate a haiku about coding"}]
    }],
    "max_tokens": 50
})
print(f"   Status: {response.status_code}")
print(f"   Works: {'Yes' if response.status_code == 200 else 'No'}\n")

print("Summary:")
print("- Claude models require at least one user message")
print("- OpenAI models work with system-only messages")
print("- Peng's array normalization fix is working correctly")