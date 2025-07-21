#!/usr/bin/env python3
"""
Test script to diagnose BAML parsing issues across different models.
This will help determine if the issue is specific to o3 or a general BAML parsing problem.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import BAML client
from baml_client.baml_client import b

# Test configuration
TEST_MODELS = [
    ("gpt4o", "ArgoGPT4o"),
    ("gpt35", "ArgoGPT35"), 
    ("claudeopus4", "ArgoClaudeOpus4"),
    ("gpto3", "ArgoGPTo3"),  # o3 model
]

TEST_GOAL = "Develop a hypothesis for improving cancer immunotherapy effectiveness"
TEST_DOMAIN = "oncology"


async def test_model(model_name: str, client_name: str):
    """Test a specific model with ParseResearchGoal"""
    print(f"\n{'='*60}")
    print(f"Testing Model: {model_name} (Client: {client_name})")
    print(f"{'='*60}")
    
    try:
        # Set the environment variable for the model
        os.environ["DEFAULT_MODEL"] = model_name
        os.environ["AGENT_MODEL"] = model_name
        
        # Call ParseResearchGoal
        print(f"Calling ParseResearchGoal...")
        result = await b.ParseResearchGoal(
            natural_language_goal=TEST_GOAL,
            domain_context=TEST_DOMAIN
        )
        
        # Print successful result
        print(f"✅ SUCCESS - Model {model_name} parsed correctly")
        print(f"\nParsed Result:")
        print(f"  Primary Objective: {result.primary_objective}")
        print(f"  Sub-objectives: {result.sub_objectives}")
        print(f"  Constraints: {result.implied_constraints}")
        print(f"  Categories: {result.suggested_categories}")
        print(f"  Key Terms: {result.key_terms}")
        print(f"  Success Criteria: {result.success_criteria}")
        
        return {
            "model": model_name,
            "status": "success",
            "result": {
                "primary_objective": result.primary_objective,
                "sub_objectives": result.sub_objectives,
                "implied_constraints": result.implied_constraints,
                "suggested_categories": result.suggested_categories,
                "key_terms": result.key_terms,
                "success_criteria": result.success_criteria
            }
        }
        
    except Exception as e:
        print(f"❌ FAILED - Model {model_name} failed with error")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        
        # Try to get more details about the error
        if hasattr(e, 'response'):
            print(f"Response: {e.response}")
        if hasattr(e, '__dict__'):
            print(f"Error Details: {e.__dict__}")
            
        return {
            "model": model_name,
            "status": "failed",
            "error": str(e),
            "error_type": type(e).__name__
        }


async def test_raw_llm_call(model_name: str):
    """Test raw LLM call to see the actual model response"""
    print(f"\n--- Raw LLM Test for {model_name} ---")
    
    try:
        # Construct the prompt manually
        prompt = f"""You are parsing a research goal into structured components.
    
Research Goal: {TEST_GOAL}

Domain: {TEST_DOMAIN}

Analyze this goal and extract:
1. The primary research objective (one clear statement)
2. Sub-objectives that support the main goal
3. Implied constraints (ethical, practical, scientific)
4. Relevant hypothesis categories (mechanistic, therapeutic, etc.)
5. Key scientific terms and concepts
6. Success criteria - what outcomes would satisfy this goal

Be thorough but concise in your analysis.

Please provide your response in the following JSON format:
{{
    "primary_objective": "string",
    "sub_objectives": ["string1", "string2"],
    "implied_constraints": ["string1", "string2"],
    "suggested_categories": ["string1", "string2"],
    "key_terms": ["string1", "string2"],
    "success_criteria": ["string1", "string2"]
}}"""

        # This would need actual LLM API call - showing structure
        print(f"Prompt sent to {model_name}:")
        print(prompt[:500] + "...")
        
    except Exception as e:
        print(f"Raw test failed: {e}")


async def main():
    """Run tests on all models"""
    print("BAML Model Testing Script")
    print("Testing ParseResearchGoal across different models")
    print(f"Test Goal: {TEST_GOAL}")
    print(f"Test Domain: {TEST_DOMAIN}")
    
    # Ensure Argo proxy is running
    print("\n⚠️  Make sure Argo proxy is running at http://localhost:8000")
    print("Run: python scripts/argo_proxy.py")
    
    results = []
    
    # Test each model
    for model_name, client_name in TEST_MODELS:
        result = await test_model(model_name, client_name)
        results.append(result)
        
        # If model failed, try raw test to see response
        if result["status"] == "failed":
            await test_raw_llm_call(model_name)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    success_count = sum(1 for r in results if r["status"] == "success")
    fail_count = sum(1 for r in results if r["status"] == "failed")
    
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    
    print("\nModel Results:")
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"  {status_icon} {result['model']}: {result['status']}")
        if result["status"] == "failed":
            print(f"     Error: {result['error'][:100]}...")
    
    # Save results to file
    output_file = project_root / "test_results" / "baml_model_test_results.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {output_file}")
    
    # Provide recommendations
    print(f"\n{'='*60}")
    print("RECOMMENDATIONS")
    print(f"{'='*60}")
    
    if fail_count > 0:
        print("Some models failed to parse correctly. Consider:")
        print("1. Checking if the BAML prompt needs adjustment for specific models")
        print("2. Adding model-specific prompts or handling")
        print("3. Examining the raw responses to understand formatting differences")
        print("4. Updating BAML parsing logic to handle variations")
    else:
        print("All models parsed successfully! The BAML configuration is working correctly.")


if __name__ == "__main__":
    asyncio.run(main())