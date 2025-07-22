#!/usr/bin/env python3
"""Quick test to verify model connectivity and o3 max_tokens behavior."""

import asyncio
import aiohttp
import json
import time

async def test_o3_max_tokens():
    """Test if o3 really ignores max_tokens parameter."""
    base_url = "http://localhost:8000/v1/chat/completions"
    
    # Test 1: o3 with very low max_tokens (should be ignored)
    print("Test 1: o3 with max_tokens=20 (should be ignored)")
    async with aiohttp.ClientSession() as session:
        request_data = {
            "model": "gpto3",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Count from 1 to 50. Just write the numbers."}
            ],
            "max_tokens": 20  # Very low - if respected, would cut off early
        }
        
        try:
            start = time.time()
            async with session.post(base_url, json=request_data, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                result = await resp.json()
                elapsed = time.time() - start
                
                if resp.status == 200:
                    content = result["choices"][0]["message"]["content"]
                    tokens = result.get("usage", {}).get("completion_tokens", 0)
                    print(f"✓ Success in {elapsed:.1f}s")
                    print(f"  Tokens generated: {tokens}")
                    print(f"  Content length: {len(content)} chars")
                    print(f"  First 100 chars: {content[:100]}...")
                    print(f"  Last 100 chars: ...{content[-100:]}")
                    print(f"  RESULT: max_tokens {'IGNORED' if tokens > 20 else 'RESPECTED'}")
                else:
                    print(f"✗ Error: {result}")
        except Exception as e:
            print(f"✗ Failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: o3 with max_completion_tokens (should work)
    print("Test 2: o3 with max_completion_tokens=20 (should be respected)")
    async with aiohttp.ClientSession() as session:
        request_data = {
            "model": "gpto3",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Count from 1 to 50. Just write the numbers."}
            ],
            "max_completion_tokens": 20  # Should limit response
        }
        
        try:
            start = time.time()
            async with session.post(base_url, json=request_data, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                result = await resp.json()
                elapsed = time.time() - start
                
                if resp.status == 200:
                    content = result["choices"][0]["message"]["content"]
                    tokens = result.get("usage", {}).get("completion_tokens", 0)
                    print(f"✓ Success in {elapsed:.1f}s")
                    print(f"  Tokens generated: {tokens}")
                    print(f"  Content: {content}")
                    print(f"  RESULT: max_completion_tokens {'RESPECTED' if tokens <= 20 else 'NOT RESPECTED'}")
                else:
                    print(f"✗ Error: {result}")
        except Exception as e:
            print(f"✗ Failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Compare with gpt4o using max_tokens
    print("Test 3: gpt4o with max_tokens=20 (should be respected)")
    async with aiohttp.ClientSession() as session:
        request_data = {
            "model": "gpt4o",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Count from 1 to 50. Just write the numbers."}
            ],
            "max_tokens": 20
        }
        
        try:
            start = time.time()
            async with session.post(base_url, json=request_data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                result = await resp.json()
                elapsed = time.time() - start
                
                if resp.status == 200:
                    content = result["choices"][0]["message"]["content"]
                    tokens = result.get("usage", {}).get("completion_tokens", 0)
                    print(f"✓ Success in {elapsed:.1f}s")
                    print(f"  Tokens generated: {tokens}")
                    print(f"  Content: {content}")
                    print(f"  RESULT: max_tokens {'RESPECTED' if tokens <= 20 else 'NOT RESPECTED'}")
                else:
                    print(f"✗ Error: {result}")
        except Exception as e:
            print(f"✗ Failed: {e}")

async def test_claude_messages():
    """Test Claude with system-only messages (should work with proxy fix)."""
    base_url = "http://localhost:8000/v1/chat/completions"
    
    print("\n" + "="*50 + "\n")
    print("Test 4: Claude with system-only message (proxy should auto-add user message)")
    
    async with aiohttp.ClientSession() as session:
        request_data = {
            "model": "claudeopus4",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant. Say 'Hello from Claude!'"}
            ],
            "max_tokens": 50
        }
        
        try:
            start = time.time()
            async with session.post(base_url, json=request_data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                result = await resp.json()
                elapsed = time.time() - start
                
                if resp.status == 200:
                    content = result["choices"][0]["message"]["content"]
                    print(f"✓ Success in {elapsed:.1f}s")
                    print(f"  Response: {content}")
                    print(f"  RESULT: Proxy successfully handled system-only message")
                else:
                    error_msg = result.get("error", {}).get("message", "Unknown error")
                    print(f"✗ Error: {error_msg}")
                    print(f"  RESULT: Proxy did NOT handle system-only message")
        except Exception as e:
            print(f"✗ Failed: {e}")

async def main():
    print("Quick Model Parameter Test")
    print("="*50)
    
    # Test o3 behavior
    await test_o3_max_tokens()
    
    # Test Claude
    await test_claude_messages()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())