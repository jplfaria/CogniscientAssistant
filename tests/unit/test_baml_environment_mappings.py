"""Tests for BAML environment variable mappings."""

import os
import tempfile
from pathlib import Path
import pytest


class TestBAMLEnvironmentMappings:
    """Tests for environment variable mappings in BAML configuration."""

    def test_environment_variable_references_in_clients(self):
        """Test that clients.baml properly references environment variables."""
        clients_path = Path("baml_src/clients.baml")
        assert clients_path.exists(), "clients.baml should exist"
        
        content = clients_path.read_text()
        
        # Check that DefaultClient uses environment variables
        assert "provider env.BAML_CLIENT_PROVIDER" in content
        assert "model env.BAML_MODEL" in content
        
        # Check that commented ArgoClient shows proper env usage
        assert "base_url env.ARGO_GATEWAY_URL" in content
        assert "api_key env.ARGO_API_KEY" in content

    def test_environment_baml_file_exists(self):
        """Test that environment.baml file exists for env variable definitions."""
        env_path = Path("baml_src/environment.baml")
        assert env_path.exists(), "environment.baml should exist for env variable mappings"

    def test_environment_baml_structure(self):
        """Test that environment.baml has proper structure."""
        env_path = Path("baml_src/environment.baml")
        content = env_path.read_text()
        
        # Check for environment block
        assert "configuration {" in content or "env {" in content, "Should have configuration or env block"
        
        # Check for key environment variable definitions
        expected_vars = [
            "BAML_CLIENT_PROVIDER",
            "BAML_MODEL",
            "ARGO_GATEWAY_URL",
            "ARGO_API_KEY",
            "DEFAULT_MODEL",
            "LOG_LEVEL",
            "ENABLE_SAFETY_CHECKS"
        ]
        
        for var in expected_vars:
            assert var in content, f"Environment variable {var} should be defined"

    def test_environment_variable_defaults(self):
        """Test that environment.baml provides sensible defaults."""
        env_path = Path("baml_src/environment.baml")
        content = env_path.read_text()
        
        # Check for default values
        assert "openai" in content, "Should have default provider"
        assert "gpt-3.5-turbo" in content, "Should have default model"
        assert "INFO" in content, "Should have default log level"

    def test_model_specific_environment_variables(self):
        """Test agent-specific model environment variables."""
        env_path = Path("baml_src/environment.baml")
        content = env_path.read_text()
        
        # Check for agent-specific model variables
        agent_models = [
            "SUPERVISOR_MODEL",
            "GENERATION_MODEL", 
            "REFLECTION_MODEL",
            "RANKING_MODEL",
            "EVOLUTION_MODEL",
            "PROXIMITY_MODEL",
            "META_REVIEW_MODEL"
        ]
        
        for model_var in agent_models:
            assert model_var in content, f"Agent model variable {model_var} should be defined"

    def test_performance_configuration_variables(self):
        """Test performance-related environment variables."""
        env_path = Path("baml_src/environment.baml")
        content = env_path.read_text()
        
        # Check for performance variables
        perf_vars = [
            "MAX_CONCURRENT_AGENTS",
            "AGENT_TIMEOUT_SECONDS"
        ]
        
        for var in perf_vars:
            assert var in content, f"Performance variable {var} should be defined"

    def test_safety_configuration_variables(self):
        """Test safety-related environment variables."""
        env_path = Path("baml_src/environment.baml")
        content = env_path.read_text()
        
        # Check for safety variables
        assert "ENABLE_SAFETY_CHECKS" in content
        assert "SAFETY_MODEL" in content

    def test_client_can_use_environment_variables(self):
        """Test that BAML clients can properly reference environment variables."""
        clients_path = Path("baml_src/clients.baml")
        env_path = Path("baml_src/environment.baml")
        
        # Both files should exist
        assert clients_path.exists()
        assert env_path.exists()
        
        clients_content = clients_path.read_text()
        
        # Check that clients can reference env vars with proper syntax
        assert "env." in clients_content, "Clients should use env. prefix for environment variables"
        
    def test_environment_variable_type_safety(self):
        """Test that environment variables have proper type definitions."""
        env_path = Path("baml_src/environment.baml")
        content = env_path.read_text()
        
        # Check for type annotations or validation
        # BAML should define types for env vars (string, int, bool)
        assert "string" in content or "str" in content, "Should define string types"
        assert "int" in content or "number" in content, "Should define numeric types"
        assert "bool" in content or "boolean" in content, "Should define boolean types"

    def test_required_vs_optional_variables(self):
        """Test that environment.baml distinguishes required vs optional vars."""
        env_path = Path("baml_src/environment.baml")
        content = env_path.read_text()
        
        # Check for required variable indicators
        assert "required" in content or "optional" in content, "Should indicate required/optional variables"

    def test_environment_variable_documentation(self):
        """Test that environment variables are properly documented."""
        env_path = Path("baml_src/environment.baml")
        content = env_path.read_text()
        
        # Check for comments explaining each variable
        assert "//" in content or "/*" in content, "Should have comments documenting variables"
        
        # Check for descriptions of key variables
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "ARGO_GATEWAY_URL" in line:
                # Should have a comment before or on same line
                prev_line = lines[i-1] if i > 0 else ""
                assert "//" in line or "//" in prev_line, "ARGO_GATEWAY_URL should be documented"

    def test_env_example_sync(self):
        """Test that environment.baml is in sync with .env.example."""
        env_path = Path("baml_src/environment.baml")
        env_example_path = Path(".env.example")
        
        assert env_path.exists()
        assert env_example_path.exists()
        
        env_content = env_path.read_text()
        env_example_content = env_example_path.read_text()
        
        # Extract variable names from .env.example
        env_example_vars = []
        for line in env_example_content.split('\n'):
            if '=' in line and not line.strip().startswith('#'):
                var_name = line.split('=')[0].strip()
                env_example_vars.append(var_name)
        
        # Check that all .env.example vars are in environment.baml
        for var in env_example_vars:
            assert var in env_content, f"Variable {var} from .env.example should be in environment.baml"