#!/usr/bin/env python3
"""
Test script to verify Argo model access through the proxy.
Run this after starting the argo-proxy to ensure all models are accessible.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed")
    print("Please install it with: pip install openai")
    sys.exit(1)

# Initialize client
client = OpenAI(
    base_url=os.getenv("ARGO_PROXY_URL", "http://localhost:8000/v1"),
    api_key=""  # Argo proxy doesn't require an API key
)

# Models to test (using original Argo model names)
models = [
    ("gpt4o", "GPT-4o"),
    ("gpto3mini", "GPT-o3 Mini"),
    ("claudeopus4", "Claude 4 Opus"),
    ("gemini25pro", "Gemini 2.5 Pro"),
]

print("Testing Argo model access through proxy...")
print(f"Proxy URL: {os.getenv('ARGO_PROXY_URL', 'http://localhost:8000/v1')}")
print("-" * 60)

# Test each model
for model_id, model_name in models:
    print(f"\nTesting {model_name} (model: {model_id})...")
    
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "user", "content": "Say 'Hello from AI Co-Scientist' in exactly 5 words"}
            ],
            max_tokens=20,
            temperature=0
        )
        
        content = response.choices[0].message.content
        print(f"✓ SUCCESS: {content}")
        
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            print(f"✗ FAILED: Model not available")
        elif "connection" in error_msg.lower():
            print(f"✗ FAILED: Cannot connect to proxy (is it running?)")
        else:
            print(f"✗ FAILED: {error_msg}")

print("\n" + "-" * 60)
print("\nTest complete!")
print("\nNotes:")
print("- If connection failed, run: ./scripts/start-argo-proxy.sh")
print("- If models are not available, check with your Argo administrator")
print("- Ensure you're connected to Argonne VPN if working remotely")