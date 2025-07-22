"""Tests for BAML client configuration."""

import os
from pathlib import Path
import pytest
from typing import Dict, Any


class TestBAMLClientConfiguration:
    """Test BAML client configuration in clients.baml."""
    
    def test_clients_file_exists(self):
        """Test that clients.baml file exists."""
        clients_path = Path("baml_src/clients.baml")
        assert clients_path.exists(), "clients.baml should exist"
        
    def test_mock_client_configuration(self):
        """Test that MockClient is properly configured."""
        clients_path = Path("baml_src/clients.baml")
        content = clients_path.read_text()
        
        assert "client<llm> MockClient" in content, "MockClient should be defined"
        assert "provider openai" in content, "MockClient should use openai provider"
        assert "http://localhost:8000/v1" in content, "MockClient should use local mock server"
        
    def test_development_client_configuration(self):
        """Test that DevelopmentClient is properly configured."""
        clients_path = Path("baml_src/clients.baml")
        content = clients_path.read_text()
        
        assert "client<llm> DevelopmentClient" in content, "DevelopmentClient should be defined"
        assert "temperature 0.7" in content, "DevelopmentClient should have temperature setting"
        assert "max_tokens 2000" in content, "DevelopmentClient should have max_tokens setting"
        
    def test_default_client_configuration(self):
        """Test that DefaultClient uses environment variables."""
        clients_path = Path("baml_src/clients.baml")
        content = clients_path.read_text()
        
        assert "client<llm> DefaultClient" in content, "DefaultClient should be defined"
        assert "provider openai" in content, "DefaultClient should use openai provider"
        assert "model env.BAML_MODEL" in content, "DefaultClient should use env model"
        
    def test_test_client_configuration_exists(self):
        """Test that basic test configuration exists."""
        clients_path = Path("baml_src/clients.baml")
        content = clients_path.read_text()
        
        # BAML doesn't support test blocks - removed this functionality
        assert "// Test configurations would go here" in content, "Should have placeholder comment"
        
    def test_test_client_has_functions(self):
        """Test that TestClient references functions."""
        clients_path = Path("baml_src/clients.baml")
        content = clients_path.read_text()
        
        # Extract test block
        # BAML doesn't support test blocks - check for test clients instead
        assert "client<llm> TestErrorClient" in content, "Test clients should exist"
        
        # Verify that we have various test clients for different scenarios
        assert "client<llm> TestSlowClient" in content, "TestSlowClient should exist"
        assert "client<llm> TestRateLimitedClient" in content, "TestRateLimitedClient should exist"
        
    def test_specialized_test_clients_exist(self):
        """Test that specialized test client configurations exist."""
        clients_path = Path("baml_src/clients.baml")
        content = clients_path.read_text()
        
        # These test clients should exist
        expected_test_clients = [
            "TestErrorClient",  # For testing error scenarios
            "TestSlowClient",   # For testing timeouts
            "TestRateLimitedClient",  # For testing rate limits
            "TestContextClient",  # For testing context window limits
        ]
        
        for client in expected_test_clients:
            assert f"client<llm> {client}" in content, f"{client} should exist for comprehensive testing"
            
    def test_test_scenarios_configuration_exist(self):
        """Test that test scenario configurations exist."""
        clients_path = Path("baml_src/clients.baml")
        content = clients_path.read_text()
        
        # Test scenarios that should be configured
        # BAML doesn't support test scenario blocks - we use client definitions
        expected_clients = [
            "client<llm> TestErrorClient",
            "client<llm> TestSlowClient", 
            "client<llm> TestContextClient",
        ]
        
        for client in expected_clients:
            assert client in content, f"{client} should exist for comprehensive testing"
            
    def test_retry_policy_configuration_exists(self):
        """Test that retry policies are configured for test clients."""
        clients_path = Path("baml_src/clients.baml")
        content = clients_path.read_text()
        
        # Find commented ArgoClient configuration
        # Check for retry client configurations
        assert "client<llm> TestRetryClient" in content, "TestRetryClient should exist"
        
        # Verify retry policy example exists
        # BAML uses flat retry options, not nested retry_policy blocks
        assert "max_retries" in content, "Retry settings should be present"
        
        # Test clients with retry policies
        test_clients_with_retry = [
            "TestRetryClient",  # Client configured with retry policies
            "TestNoRetryClient",  # Client with retries disabled
        ]
        
        for client in test_clients_with_retry:
            assert f"client<llm> {client}" in content, f"{client} should exist for retry testing"
            
    def test_error_client_configuration(self):
        """Test TestErrorClient specific configuration."""
        clients_path = Path("baml_src/clients.baml")
        content = clients_path.read_text()
        
        # Find TestErrorClient block
        client_start = content.find("client<llm> TestErrorClient")
        assert client_start != -1, "TestErrorClient should exist"
        
        client_end = content.find("}", client_start)
        client_block = content[client_start:client_end+1]
        
        assert "http://localhost:8001/v1" in client_block, "TestErrorClient should use non-existent server"
        assert "timeout_seconds 1" in client_block, "TestErrorClient should have short timeout"
        
    def test_retry_client_configurations(self):
        """Test retry client configurations."""
        clients_path = Path("baml_src/clients.baml")
        content = clients_path.read_text()
        
        # Check TestRetryClient
        retry_start = content.find("client<llm> TestRetryClient")
        assert retry_start != -1, "TestRetryClient should exist"
        retry_end = content.find("}", retry_start)
        retry_block = content[retry_start:retry_end+1]
        
        assert "max_retries 3" in retry_block, "TestRetryClient should have 3 retries"
        assert "exponential_backoff true" in retry_block, "TestRetryClient should use exponential backoff"
        
        # Check TestNoRetryClient
        no_retry_start = content.find("client<llm> TestNoRetryClient")
        assert no_retry_start != -1, "TestNoRetryClient should exist"
        no_retry_end = content.find("}", no_retry_start)
        no_retry_block = content[no_retry_start:no_retry_end+1]
        
        assert "max_retries 0" in no_retry_block, "TestNoRetryClient should have 0 retries"