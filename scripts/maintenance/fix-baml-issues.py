#!/usr/bin/env python3
"""Fix BAML configuration issues to match test expectations."""

import os
import re

def fix_baml_enums():
    """Update BAML enums to support case-insensitive matching."""
    models_path = "baml_src/models.baml"
    
    # Read current content
    with open(models_path, 'r') as f:
        content = f.read()
    
    # Add aliases for enum values to support both cases
    # This is a common pattern in BAML for backward compatibility
    
    # For SafetyLevel enum - add lowercase 'concerning'
    content = re.sub(
        r'enum SafetyLevel \{([^}]+)\}',
        lambda m: 'enum SafetyLevel {' + m.group(1).replace("Concerning", 'Concerning @alias("concerning")') + '}',
        content,
        flags=re.DOTALL
    )
    
    # Add similar aliases for other enums that tests expect in lowercase
    enum_fixes = [
        ('HypothesisCategory', [
            ('Mechanistic', 'mechanistic'),
            ('Therapeutic', 'therapeutic'),
            ('Diagnostic', 'diagnostic'),
            ('Biomarker', 'biomarker'),
            ('Methodology', 'methodology'),
            ('Other', 'other')
        ]),
        ('ReviewType', [
            ('Initial', 'initial'),
            ('Full', 'full'),
            ('DeepVerification', 'deep_verification'),
            ('Observation', 'observation'),
            ('Simulation', 'simulation'),
            ('Tournament', 'tournament')
        ]),
        ('ReviewDecision', [
            ('Accept', 'accept'),
            ('Reject', 'reject'),
            ('Revise', 'revise')
        ]),
        ('ConfidenceLevel', [
            ('High', 'high'),
            ('Medium', 'medium'),
            ('Low', 'low')
        ]),
        ('Validity', [
            ('Valid', 'valid'),
            ('Questionable', 'questionable'),
            ('Invalid', 'invalid')
        ]),
        ('Criticality', [
            ('Fundamental', 'fundamental'),
            ('Peripheral', 'peripheral')
        ])
    ]
    
    # Apply fixes for each enum
    for enum_name, mappings in enum_fixes:
        # Find the enum block
        enum_pattern = rf'enum {enum_name} \{{([^}}]+)\}}'
        match = re.search(enum_pattern, content, re.DOTALL)
        
        if match:
            enum_content = match.group(1)
            new_enum_content = enum_content
            
            # Add aliases for each value
            for pascal_case, lower_case in mappings:
                if pascal_case in new_enum_content and f'@alias("{lower_case}")' not in new_enum_content:
                    new_enum_content = new_enum_content.replace(
                        pascal_case,
                        f'{pascal_case} @alias("{lower_case}")'
                    )
            
            # Replace the enum content
            content = content.replace(
                f'enum {enum_name} {{{enum_content}}}',
                f'enum {enum_name} {{{new_enum_content}}}'
            )
    
    # Write updated content
    with open(models_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {models_path} with enum aliases")

def fix_client_configurations():
    """Fix client configurations to match test expectations."""
    clients_path = "baml_src/clients.baml"
    
    # Read current content
    with open(clients_path, 'r') as f:
        content = f.read()
    
    # Add DefaultClient with environment variable provider
    if "client<llm> DefaultClient" not in content:
        default_client = '''
// Default client using environment variables
client<llm> DefaultClient {
  provider env.BAML_CLIENT_PROVIDER
  options {
    model env.BAML_MODEL
    base_url env.BAML_BASE_URL
    api_key env.BAML_API_KEY
  }
}
'''
        content = content.replace(
            "// Production client (will use Argo Gateway in production)",
            default_client + "\n// Production client (will use Argo Gateway in production)"
        )
    
    # Add ArgoClient with proper env variable references
    if "// Production client" in content and "client<llm> ArgoClient" not in content:
        argo_client = '''
// Production client using Argo Gateway (commented out by default)
// client<llm> ArgoClient {
//   provider openai
//   options {
//     model env.DEFAULT_MODEL
//     base_url env.ARGO_GATEWAY_URL
//     api_key env.ARGO_API_KEY
//   }
// }
'''
        content = content.replace(
            "// Production client (will use Argo Gateway in production)",
            argo_client + "\n// Production client (will use Argo Gateway in production)"
        )
    
    # Update TestRetryClient to include retry configuration
    if "client<llm> TestRetryClient" in content:
        content = re.sub(
            r'client<llm> TestRetryClient \{[^}]+\}',
            '''client<llm> TestRetryClient {
  provider openai
  options {
    model "gpt-3.5-turbo"
    base_url "http://localhost:8000/v1"
    max_retries 3
  }
}''',
            content,
            flags=re.DOTALL
        )
    
    # Write updated content
    with open(clients_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {clients_path} with proper client configurations")

def fix_environment_config():
    """Create proper environment configuration."""
    env_path = "baml_src/environment.baml"
    
    env_content = '''// BAML Environment Configuration
// This file defines environment variables used in the AI Co-Scientist system

configuration {
    // API Configuration
    BAML_CLIENT_PROVIDER: string = env.BAML_CLIENT_PROVIDER or "openai"
    BAML_MODEL: string = env.BAML_MODEL or "gpt-3.5-turbo" 
    BAML_BASE_URL: string = env.BAML_BASE_URL or "http://localhost:8000/v1"
    BAML_API_KEY: string = env.BAML_API_KEY or ""
    
    // Argo Gateway Configuration (using expected variable names)
    ARGO_GATEWAY_URL: string = env.ARGO_GATEWAY_URL or "http://localhost:8000"
    ARGO_PROXY_URL: string = env.ARGO_PROXY_URL or "http://localhost:8000"
    ARGO_USERNAME: string = env.ARGO_USERNAME or ""
    ARGO_API_KEY: string = env.ARGO_API_KEY or ""
    
    // Default Model Configuration
    DEFAULT_MODEL: string = env.DEFAULT_MODEL or "gpt-3.5-turbo"
    
    // System Configuration
    LOG_LEVEL: string = env.LOG_LEVEL or "INFO"
    ENABLE_SAFETY_CHECKS: string = env.ENABLE_SAFETY_CHECKS or "true"
    
    // Safety Configuration
    SAFETY_MODEL: string = env.SAFETY_MODEL or "gpt-3.5-turbo"
    RESEARCH_GOALS_FILE: string = env.RESEARCH_GOALS_FILE or ".aicoscientist/research_goals.txt"
    SAFETY_LOG_DIR: string = env.SAFETY_LOG_DIR or ".aicoscientist/safety_logs"
    
    // Worker Configuration
    MAX_WORKERS: string = env.MAX_WORKERS or "4"
    TASK_TIMEOUT: string = env.TASK_TIMEOUT or "3600"
    ASYNC_ENABLED: string = env.ASYNC_ENABLED or "true"
    
    // Storage Configuration
    CHECKPOINT_DIR: string = env.CHECKPOINT_DIR or ".aicoscientist/checkpoints"
    HYPOTHESIS_DIR: string = env.HYPOTHESIS_DIR or ".aicoscientist/hypotheses"
    REVIEW_DIR: string = env.REVIEW_DIR or ".aicoscientist/reviews"
    
    // Model Configuration
    PRIMARY_MODEL: string = env.PRIMARY_MODEL or "gpt-3.5-turbo"
    SUPERVISOR_MODEL: string = env.SUPERVISOR_MODEL or "gpt-3.5-turbo"
    GENERATION_MODEL: string = env.GENERATION_MODEL or "gpt-3.5-turbo"
    REFLECTION_MODEL: string = env.REFLECTION_MODEL or "gpt-3.5-turbo"
    RANKING_MODEL: string = env.RANKING_MODEL or "gpt-3.5-turbo"
    EVOLUTION_MODEL: string = env.EVOLUTION_MODEL or "gpt-3.5-turbo"
    PROXIMITY_MODEL: string = env.PROXIMITY_MODEL or "gpt-3.5-turbo"
    META_REVIEW_MODEL: string = env.META_REVIEW_MODEL or "gpt-3.5-turbo"
}

// Export for use in BAML
env {
    BAML_CLIENT_PROVIDER: string
    BAML_MODEL: string
    BAML_BASE_URL: string
    BAML_API_KEY: string
    ARGO_PROXY_URL: string
    ARGO_USERNAME: string
    ARGO_API_KEY: string
    SAFETY_MODEL: string
    RESEARCH_GOALS_FILE: string
    SAFETY_LOG_DIR: string
    MAX_WORKERS: string
    TASK_TIMEOUT: string
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
        f.write(env_content)
    
    print(f"✅ Created proper {env_path} with configuration block")

def add_test_configurations():
    """Add test configurations to functions.baml."""
    functions_path = "baml_src/functions.baml"
    
    if not os.path.exists(functions_path):
        print(f"⚠️  {functions_path} not found, skipping test configurations")
        return
    
    with open(functions_path, 'r') as f:
        content = f.read()
    
    # Add test configurations if not present
    test_configs = '''

// Test configurations
test TestClient {
    functions [GenerateHypothesis, EvaluateHypothesis, PerformSafetyCheck, CompareHypotheses]
    
    // Test data can be added here
}

test ErrorScenarios {
    client TestErrorClient
    functions [GenerateHypothesis]
}

test PerformanceScenarios {
    client TestSlowClient  
    functions [GenerateHypothesis]
}

test EdgeCaseScenarios {
    client TestContextClient
    functions [GenerateHypothesis]
}
'''
    
    if "test TestClient" not in content:
        content += test_configs
        
        with open(functions_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Added test configurations to {functions_path}")

if __name__ == "__main__":
    print("🔧 Fixing BAML configuration issues...")
    
    fix_baml_enums()
    fix_client_configurations()
    fix_environment_config()
    add_test_configurations()
    
    print("\n✅ All BAML fixes applied!")
    print("\n📝 Next steps:")
    print("1. Run: pytest tests/unit/test_baml*.py -v")
    print("2. If tests pass, run: ./run-loop.sh")
    print("3. View logs with: ./view-logs.sh")