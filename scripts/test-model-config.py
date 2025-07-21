#!/usr/bin/env python3
"""Test model configuration and agent setup."""

import os
import sys
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm.baml_integration import print_agent_configuration
from src.config.model_config import get_model_config


def test_configurations():
    """Test different model configurations."""
    
    print("=== Testing Model Configuration ===\n")
    
    # Test 1: Default configuration
    print("1. Default Configuration (Gemini for all):")
    print("-" * 50)
    os.environ.pop("SUPERVISOR_MODEL", None)
    os.environ.pop("GENERATION_MODEL", None)
    os.environ["DEFAULT_MODEL"] = "gemini25pro"
    
    # Reset singleton
    import src.config.model_config
    src.config.model_config._model_config = None
    
    print_agent_configuration()
    
    # Test 2: Hybrid configuration
    print("\n\n2. Hybrid Configuration:")
    print("-" * 50)
    os.environ["DEFAULT_MODEL"] = "gpt35"
    os.environ["SUPERVISOR_MODEL"] = "gpt4o"
    os.environ["GENERATION_MODEL"] = "claudeopus4"
    os.environ["REFLECTION_MODEL"] = "gpt4o"
    
    # Reset singleton
    src.config.model_config._model_config = None
    
    print_agent_configuration()
    
    # Test 3: Show environment setup
    print("\n\n3. Environment Variables for Hybrid Setup:")
    print("-" * 50)
    print("export DEFAULT_MODEL=gpt35")
    print("export SUPERVISOR_MODEL=gpt4o")
    print("export GENERATION_MODEL=claudeopus4")
    print("export REFLECTION_MODEL=gpt4o")
    
    # Test 4: Invalid model handling
    print("\n\n4. Invalid Model Handling:")
    print("-" * 50)
    os.environ["DEFAULT_MODEL"] = "invalid-model"
    
    # Reset singleton
    src.config.model_config._model_config = None
    
    config = get_model_config()
    print(f"Validation passed: {config.validate()}")
    
    # Reset to valid config
    os.environ["DEFAULT_MODEL"] = "gemini25pro"
    os.environ.pop("SUPERVISOR_MODEL", None)
    os.environ.pop("GENERATION_MODEL", None)
    os.environ.pop("REFLECTION_MODEL", None)


if __name__ == "__main__":
    test_configurations()