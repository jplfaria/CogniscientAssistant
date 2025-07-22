#!/usr/bin/env python3
"""Test if BAML correctly uses max_completion_tokens for o3."""

import asyncio
import json
import sys
sys.path.insert(0, "/Users/jplfaria/repos/CogniscientAssistant")
from baml_client.baml_client import b

async def test_o3_config():
    """Test o3 configuration through BAML."""
    print("Testing o3 configuration through BAML...\n")
    
    try:
        # Test with o3 using the updated client
        print("Calling ParseResearchGoal with ArgoGPTo3 client...")
        
        # A simple test that should produce limited output
        result = await b.ParseResearchGoal(
            natural_language_goal="Find a cure for aging",
            domain_context="Biology",
            baml_options={"client": b.ArgoGPTo3}
        )
        
        print(f"✓ Success! Got response:")
        print(f"  Primary objective: {result.primary_objective}")
        print(f"  Sub-objectives: {len(result.sub_objectives)} items")
        print(f"  Key terms: {result.key_terms[:3]}...")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print(f"  This might mean BAML doesn't support max_completion_tokens")

async def test_comparison():
    """Compare o3 with standard model."""
    print("\n\nComparing models...\n")
    
    test_goal = "Develop quantum computing applications for drug discovery"
    
    # Test with GPT-4o (standard)
    print("1. Testing with GPT-4o (standard max_tokens)...")
    try:
        result_gpt4 = await b.ParseResearchGoal(
            natural_language_goal=test_goal,
            baml_options={"client": b.ArgoGPT4o}
        )
        print(f"✓ GPT-4o Success")
    except Exception as e:
        print(f"✗ GPT-4o Error: {e}")
    
    # Test with o3
    print("\n2. Testing with o3 (max_completion_tokens)...")
    try:
        result_o3 = await b.ParseResearchGoal(
            natural_language_goal=test_goal,
            baml_options={"client": b.ArgoGPTo3}
        )
        print(f"✓ O3 Success")
    except Exception as e:
        print(f"✗ O3 Error: {e}")

async def main():
    print("BAML O3 Configuration Test")
    print("="*50)
    
    await test_o3_config()
    await test_comparison()
    
    print("\n\nNOTE: If o3 fails, we may need to:")
    print("1. Use a custom OpenAI client that supports max_completion_tokens")
    print("2. Wait for BAML to add support")
    print("3. Use environment variable workarounds")

if __name__ == "__main__":
    asyncio.run(main())