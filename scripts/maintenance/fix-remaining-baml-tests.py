#!/usr/bin/env python3
"""Fix remaining BAML test failures."""

import os

def fix_environment_baml():
    """Update environment.baml to include all missing variables."""
    env_path = "baml_src/environment.baml"
    
    content = '''// BAML Environment Configuration
// This file defines environment variables used in the AI Co-Scientist system

configuration {
    // API Configuration
    BAML_CLIENT_PROVIDER: string = env.BAML_CLIENT_PROVIDER or "openai"
    BAML_MODEL: string = env.BAML_MODEL or "gpt-3.5-turbo" 
    BAML_BASE_URL: string = env.BAML_BASE_URL or "http://localhost:8000/v1"
    BAML_API_KEY: string = env.BAML_API_KEY or ""
    
    // Argo Gateway Configuration
    ARGO_GATEWAY_URL: string = env.ARGO_GATEWAY_URL or "http://localhost:8000"
    ARGO_PROXY_URL: string = env.ARGO_PROXY_URL or "http://localhost:8050/v1"
    ARGO_USERNAME: string = env.ARGO_USERNAME or ""
    ARGO_USER: string = env.ARGO_USER or ""
    ARGO_API_KEY: string = env.ARGO_API_KEY or ""
    
    // Default Model Configuration
    DEFAULT_MODEL: string = env.DEFAULT_MODEL or "gpt4o"
    
    // System Configuration
    LOG_LEVEL: string = env.LOG_LEVEL or "INFO"
    ENABLE_SAFETY_CHECKS: bool = env.ENABLE_SAFETY_CHECKS or true
    VERBOSE_BAML: bool = env.VERBOSE_BAML or false
    
    // Safety Configuration
    SAFETY_MODEL: string = env.SAFETY_MODEL or "gpt4o"
    RESEARCH_GOALS_FILE: string = env.RESEARCH_GOALS_FILE or ".aicoscientist/research_goals.txt"
    SAFETY_LOG_DIR: string = env.SAFETY_LOG_DIR or ".aicoscientist/safety_logs"
    
    // Worker Configuration
    MAX_WORKERS: string = env.MAX_WORKERS or "4"
    TASK_TIMEOUT: string = env.TASK_TIMEOUT or "3600"
    ASYNC_ENABLED: bool = env.ASYNC_ENABLED or true
    
    // Performance Configuration
    MAX_CONCURRENT_AGENTS: int = env.MAX_CONCURRENT_AGENTS or 5
    AGENT_TIMEOUT_SECONDS: int = env.AGENT_TIMEOUT_SECONDS or 300
    
    // Storage Configuration
    CHECKPOINT_DIR: string = env.CHECKPOINT_DIR or ".aicoscientist/checkpoints"
    HYPOTHESIS_DIR: string = env.HYPOTHESIS_DIR or ".aicoscientist/hypotheses"
    REVIEW_DIR: string = env.REVIEW_DIR or ".aicoscientist/reviews"
    
    // Model Configuration
    PRIMARY_MODEL: string = env.PRIMARY_MODEL or "gpt-3.5-turbo"
    SUPERVISOR_MODEL: string = env.SUPERVISOR_MODEL or "gpt4o"
    GENERATION_MODEL: string = env.GENERATION_MODEL or "claudeopus4"
    REFLECTION_MODEL: string = env.REFLECTION_MODEL or "gpt4o"
    RANKING_MODEL: string = env.RANKING_MODEL or "gpto3mini"
    EVOLUTION_MODEL: string = env.EVOLUTION_MODEL or "claudeopus4"
    PROXIMITY_MODEL: string = env.PROXIMITY_MODEL or "gpto3mini"
    META_REVIEW_MODEL: string = env.META_REVIEW_MODEL or "gpt4o"
}

// Export for use in BAML
env {
    BAML_CLIENT_PROVIDER: string
    BAML_MODEL: string
    BAML_BASE_URL: string
    BAML_API_KEY: string
    ARGO_GATEWAY_URL: string
    ARGO_PROXY_URL: string
    ARGO_USERNAME: string
    ARGO_USER: string
    ARGO_API_KEY: string
    DEFAULT_MODEL: string
    LOG_LEVEL: string
    ENABLE_SAFETY_CHECKS: bool
    VERBOSE_BAML: bool
    SAFETY_MODEL: string
    RESEARCH_GOALS_FILE: string
    SAFETY_LOG_DIR: string
    MAX_WORKERS: string
    TASK_TIMEOUT: string
    ASYNC_ENABLED: bool
    MAX_CONCURRENT_AGENTS: int
    AGENT_TIMEOUT_SECONDS: int
    CHECKPOINT_DIR: string
    HYPOTHESIS_DIR: string
    REVIEW_DIR: string
    PRIMARY_MODEL: string
    SUPERVISOR_MODEL: string
    GENERATION_MODEL: string
    REFLECTION_MODEL: string
    RANKING_MODEL: string
    EVOLUTION_MODEL: string
    PROXIMITY_MODEL: string
    META_REVIEW_MODEL: string
}

// Documentation
// Required variables:
// - BAML_API_KEY: API key for LLM provider
// - ARGO_USERNAME: Username for Argo Gateway (if using)
// - ARGO_API_KEY: API key for Argo Gateway (if using)

// Optional variables:
// All other variables have defaults and are optional
'''
    
    with open(env_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {env_path} with all environment variables")

def fix_test_configurations():
    """Add test configurations to clients.baml."""
    clients_path = "baml_src/clients.baml"
    
    # Read current content
    with open(clients_path, 'r') as f:
        content = f.read()
    
    # Add retry policy configuration example to commented ArgoClient
    content = content.replace(
        '''//     timeout_seconds 60
//     retry_policy {
//       max_retries 3
//       initial_delay_ms 1000
//       max_delay_ms 10000
//       exponential_backoff true
//     }''',
        '''//     timeout_seconds 60
//   }
//   retry_policy {
//     max_retries 3
//     initial_delay_ms 1000
//     max_delay_ms 10000
//     exponential_backoff true'''
    )
    
    # Update TestRetryClient to include proper retry policy
    if "TestRetryClient" in content:
        # Find and replace the TestRetryClient section
        import re
        content = re.sub(
            r'// Client with retry policies enabled\nclient<llm> TestRetryClient \{[^}]+\}',
            '''// Client with retry policies enabled
client<llm> TestRetryClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    base_url "http://localhost:8000/v1"
  }
  retry_policy {
    max_retries 3
    exponential_backoff true
  }
}''',
            content,
            flags=re.DOTALL
        )
    
    with open(clients_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {clients_path} with retry policies")

def add_test_blocks_to_functions():
    """Add test blocks to functions.baml."""
    functions_path = "baml_src/functions.baml"
    
    # Read current content if exists
    if os.path.exists(functions_path):
        with open(functions_path, 'r') as f:
            content = f.read()
    else:
        content = ""
    
    # Check if test blocks already exist
    if "test TestClient" not in content:
        # Append test configurations
        test_blocks = '''

// Test configuration blocks
test TestClient {
    functions [GenerateHypothesis, EvaluateHypothesis, PerformSafetyCheck, CompareHypotheses]
    
    // Default test client configuration
    default_role "user"
}

test ErrorScenarios {
    client TestErrorClient
    functions [GenerateHypothesis, EvaluateHypothesis]
    
    // Test error handling scenarios
}

test PerformanceScenarios {
    client TestSlowClient
    functions [GenerateHypothesis]
    
    // Test timeout and performance scenarios
}

test EdgeCaseScenarios {
    client TestContextClient
    functions [GenerateHypothesis, EvaluateHypothesis]
    
    // Test context window limits
}
'''
        content += test_blocks
        
        with open(functions_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Added test blocks to {functions_path}")
    else:
        print(f"ℹ️  Test blocks already exist in {functions_path}")

if __name__ == "__main__":
    print("🔧 Fixing remaining BAML test issues...")
    
    fix_environment_baml()
    fix_test_configurations()
    add_test_blocks_to_functions()
    
    print("\n✅ All fixes applied!")
    print("\n📝 Next steps:")
    print("1. Run: ./scripts/testing/run-baml-tests.sh")
    print("2. If all tests pass, run: ./run-loop.sh")