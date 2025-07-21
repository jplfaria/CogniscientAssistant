#!/usr/bin/env python3
"""
Validate critical functionality before cleanup.
Focuses on what absolutely must work.
"""

import subprocess
import sys
import os
import asyncio
import httpx
from pathlib import Path


def check_critical_files():
    """Check that critical files exist."""
    print("1. Checking critical files...")
    critical = [
        "argo-config.yaml",
        ".env",
        "baml_src/clients.baml",
        "baml_src/functions.baml",
        "baml_src/models.baml",
        "src/llm/baml_wrapper.py",
        "src/config/model_config.py",
    ]
    
    all_exist = True
    for file in critical:
        exists = os.path.exists(file)
        print(f"  {'✅' if exists else '❌'} {file}")
        if not exists:
            all_exist = False
    
    return all_exist


async def check_argo_proxy():
    """Check if argo-proxy is running."""
    print("\n2. Checking argo-proxy...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Health check
            response = await client.get("http://localhost:8000/health")
            print(f"  ✅ Health check: {response.status_code}")
            
            # Simple LLM call
            response = await client.post(
                "http://localhost:8000/v1/chat/completions",
                json={
                    "model": "gpt35",
                    "messages": [{"role": "user", "content": "Say 'OK'"}],
                    "max_tokens": 5
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data:
                    print(f"  ✅ LLM call successful")
                    return True
            
            print(f"  ❌ LLM call failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Argo proxy not running: {e}")
        return False


def check_baml_imports():
    """Check BAML can be imported."""
    print("\n3. Checking BAML imports...")
    try:
        # Add project root to path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from baml_client.baml_client import b
        print("  ✅ BAML client imports successfully")
        
        from src.llm.baml_wrapper import BAMLWrapper
        print("  ✅ BAML wrapper imports successfully")
        
        from src.config.model_config import get_model_config
        config = get_model_config()
        print(f"  ✅ Model config loads (default: {config.default_model})")
        
        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False


def check_real_llm_tests():
    """Check if real LLM tests can run."""
    print("\n4. Checking real LLM test capability...")
    
    # Check if test files exist
    test_files = [
        "tests/integration/test_phase7_baml_real.py",
        "tests/integration/test_phase8_argo_real.py",
    ]
    
    all_exist = True
    for test_file in test_files:
        exists = os.path.exists(test_file)
        print(f"  {'✅' if exists else '❌'} {test_file}")
        if not exists:
            all_exist = False
    
    # Check if run script exists and is executable
    run_script = "scripts/run-real-llm-tests.sh"
    if os.path.exists(run_script):
        is_exec = os.access(run_script, os.X_OK)
        print(f"  {'✅' if is_exec else '❌'} {run_script} is executable")
    else:
        print(f"  ❌ {run_script} not found")
        all_exist = False
    
    return all_exist


def main():
    """Run all critical checks."""
    print("=" * 60)
    print("CRITICAL FUNCTIONALITY VALIDATION")
    print("=" * 60)
    
    results = []
    
    # Run checks
    results.append(("Critical files exist", check_critical_files()))
    results.append(("BAML imports work", check_baml_imports()))
    results.append(("Argo proxy running", asyncio.run(check_argo_proxy())))
    results.append(("Real LLM tests ready", check_real_llm_tests()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check, result in results:
        print(f"{'✅' if result else '❌'} {check}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL CRITICAL CHECKS PASSED - Safe to proceed with cleanup")
        print("\nRecommended cleanup order:")
        print("1. Consolidate documentation files")
        print("2. Move test scripts to proper directories")  
        print("3. Consolidate proxy startup scripts")
        print("4. Remove temporary files")
        print("\nAfter each step, run this script again to ensure nothing broke.")
        return True
    else:
        print("\n❌ CRITICAL CHECKS FAILED - Do not proceed with cleanup")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)