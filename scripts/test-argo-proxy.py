#!/usr/bin/env python3
"""
Test script for Argo Proxy connectivity
Tests basic API endpoints and model availability
"""

import os
import sys
import json
import time
from typing import Dict, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PROXY_URL = os.getenv("ARGO_PROXY_URL", "http://localhost:8000/v1")
TIMEOUT = 10

# Test models
TEST_MODELS = [
    "gpt4o",
    "gpt-3.5-turbo",
    "claude-opus-4",
    "gemini-2.5-pro"
]

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_status(status: str, message: str):
    """Print colored status message"""
    color = {
        "success": Colors.GREEN,
        "warning": Colors.YELLOW,
        "error": Colors.RED,
        "info": Colors.BLUE
    }.get(status, Colors.END)
    
    symbol = {
        "success": "✓",
        "warning": "⚠",
        "error": "✗",
        "info": "ℹ"
    }.get(status, "-")
    
    print(f"{color}{symbol} {message}{Colors.END}")

def test_proxy_health():
    """Test if proxy is running and accessible"""
    print("\n1. Testing Proxy Health")
    print("-" * 40)
    
    try:
        # Try to connect to the base URL
        response = requests.get(PROXY_URL, timeout=TIMEOUT)
        if response.status_code == 200:
            print_status("success", f"Proxy is running at {PROXY_URL}")
            return True
        else:
            print_status("warning", f"Proxy returned status code: {response.status_code}")
            return True
    except requests.exceptions.ConnectionError:
        print_status("error", f"Cannot connect to proxy at {PROXY_URL}")
        print_status("info", "Make sure to run: ./scripts/start-argo-proxy.sh")
        return False
    except Exception as e:
        print_status("error", f"Unexpected error: {str(e)}")
        return False

def test_models_endpoint():
    """Test the models listing endpoint"""
    print("\n2. Testing Models Endpoint")
    print("-" * 40)
    
    try:
        response = requests.get(f"{PROXY_URL}/models", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            models = data.get("data", [])
            print_status("success", f"Found {len(models)} models")
            
            # List available models
            if models:
                print("\nAvailable models:")
                for model in models:
                    model_id = model.get("id", "unknown")
                    print(f"  - {model_id}")
            return True
        else:
            print_status("error", f"Models endpoint returned: {response.status_code}")
            return False
    except Exception as e:
        print_status("error", f"Failed to access models endpoint: {str(e)}")
        return False

def test_model_chat(model_name: str):
    """Test chat completion with a specific model"""
    print(f"\n3. Testing Chat Completion with {model_name}")
    print("-" * 40)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('ARGO_USER', '')}"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": "Say 'Hello from Argo!' in exactly 4 words."}
        ],
        "max_tokens": 20,
        "temperature": 0
    }
    
    try:
        response = requests.post(
            f"{PROXY_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            print_status("success", f"Model {model_name} responded: {content}")
            return True
        else:
            print_status("error", f"Chat completion failed with status: {response.status_code}")
            if response.text:
                print(f"  Response: {response.text[:200]}")
            return False
    except Exception as e:
        print_status("error", f"Failed to test {model_name}: {str(e)}")
        return False

def main():
    """Main test function"""
    print(f"{Colors.BLUE}Argo Proxy Connectivity Test{Colors.END}")
    print("=" * 40)
    
    # Test 1: Proxy health
    if not test_proxy_health():
        print("\n⚠️  Proxy is not running. Please start it first.")
        sys.exit(1)
    
    # Test 2: Models endpoint
    test_models_endpoint()
    
    # Test 3: Chat completions for each model
    print(f"\n{Colors.BLUE}Testing Model Access{Colors.END}")
    print("=" * 40)
    
    results = {}
    for model in TEST_MODELS:
        success = test_model_chat(model)
        results[model] = success
        time.sleep(1)  # Rate limiting
    
    # Summary
    print(f"\n{Colors.BLUE}Test Summary{Colors.END}")
    print("=" * 40)
    
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    print(f"\nModels tested: {total_count}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_count - success_count}")
    
    print("\nDetailed results:")
    for model, success in results.items():
        status = "success" if success else "error"
        print_status(status, f"{model}: {'✓ Working' if success else '✗ Failed'}")
    
    # Exit code based on results
    if success_count == 0:
        print_status("error", "\nNo models are accessible!")
        sys.exit(1)
    elif success_count < total_count:
        print_status("warning", f"\nSome models failed ({success_count}/{total_count} working)")
        sys.exit(0)
    else:
        print_status("success", "\nAll models are accessible!")
        sys.exit(0)

if __name__ == "__main__":
    main()