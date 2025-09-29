"""Unit tests to validate BAML prompt structure requirements.

These tests ensure all BAML functions follow the required pattern for
Claude and Gemini compatibility (system + user roles).
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

import pytest


class TestBAMLPromptStructure:
    """Validate BAML prompt structure across all functions."""
    
    @pytest.fixture
    def baml_files(self) -> List[Path]:
        """Find all BAML files in the project."""
        baml_dir = Path("baml_src")
        if not baml_dir.exists():
            pytest.skip("No baml_src directory found")
        
        # Find all .baml files except the template
        files = []
        for file in baml_dir.glob("*.baml"):
            if file.name != "TEMPLATE.baml":
                files.append(file)
        
        if not files:
            pytest.skip("No BAML files found to test")
            
        return files
    
    def extract_functions(self, content: str) -> List[Tuple[str, str]]:
        """Extract function names and their prompts from BAML content.
        
        Returns list of (function_name, prompt_content) tuples.
        """
        functions = []
        
        # Pattern to match BAML functions with prompts
        # Handles both single and multi-line function signatures
        function_pattern = r'function\s+(\w+)\s*\([^)]*\)[^{]*\{[^}]*prompt\s*#"([^"]+)"#'
        
        for match in re.finditer(function_pattern, content, re.DOTALL):
            func_name = match.group(1)
            prompt_content = match.group(2)
            functions.append((func_name, prompt_content))
            
        return functions
    
    def test_all_functions_have_system_and_user_roles(self, baml_files):
        """Ensure every BAML function has both system and user roles."""
        errors = []
        
        for file_path in baml_files:
            content = file_path.read_text()
            functions = self.extract_functions(content)
            
            for func_name, prompt in functions:
                has_system = "{{ _.role(\"system\") }}" in prompt or "{{ _.role('system') }}" in prompt
                has_user = "{{ _.role(\"user\") }}" in prompt or "{{ _.role('user') }}" in prompt
                
                if not has_system:
                    errors.append(f"{file_path.name}::{func_name} missing system role")
                if not has_user:
                    errors.append(f"{file_path.name}::{func_name} missing user role")
                    
        if errors:
            pytest.fail(
                "BAML functions missing required roles (Claude/Gemini compatibility):\n" + 
                "\n".join(f"  - {error}" for error in errors)
            )
    
    def test_no_system_only_prompts(self, baml_files):
        """Ensure no BAML functions use system-only messages."""
        system_only_functions = []
        
        for file_path in baml_files:
            content = file_path.read_text()
            functions = self.extract_functions(content)
            
            for func_name, prompt in functions:
                has_system = "{{ _.role(\"system\") }}" in prompt or "{{ _.role('system') }}" in prompt
                has_user = "{{ _.role(\"user\") }}" in prompt or "{{ _.role('user') }}" in prompt
                
                # Check if it's a system-only prompt (has system but no user)
                if has_system and not has_user:
                    system_only_functions.append(f"{file_path.name}::{func_name}")
                    
        if system_only_functions:
            pytest.fail(
                "BAML functions using system-only prompts (will fail with Claude/Gemini):\n" + 
                "\n".join(f"  - {func}" for func in system_only_functions)
            )
    
    def test_role_order_is_correct(self, baml_files):
        """Ensure system role comes before user role in all prompts."""
        order_errors = []
        
        for file_path in baml_files:
            content = file_path.read_text()
            functions = self.extract_functions(content)
            
            for func_name, prompt in functions:
                # Find positions of role declarations
                system_pos = -1
                user_pos = -1
                
                system_match = re.search(r'{{\s*_\.role\s*\(\s*["\']system["\']\s*\)\s*}}', prompt)
                user_match = re.search(r'{{\s*_\.role\s*\(\s*["\']user["\']\s*\)\s*}}', prompt)
                
                if system_match:
                    system_pos = system_match.start()
                if user_match:
                    user_pos = user_match.start()
                    
                # If both exist, system should come first
                if system_pos > -1 and user_pos > -1 and system_pos > user_pos:
                    order_errors.append(f"{file_path.name}::{func_name} has user role before system role")
                    
        if order_errors:
            pytest.fail(
                "BAML functions with incorrect role order (system should come first):\n" + 
                "\n".join(f"  - {error}" for error in order_errors)
            )
    
    def test_parameters_in_user_section(self, baml_files):
        """Verify that input parameters are referenced in the user section."""
        param_errors = []
        
        for file_path in baml_files:
            content = file_path.read_text()
            
            # Extract functions with more detailed parsing
            function_blocks = re.findall(
                r'function\s+(\w+)\s*\(([^)]*)\)[^{]*\{[^}]*prompt\s*#"([^"]+)"#',
                content,
                re.DOTALL
            )
            
            for func_name, params_str, prompt in function_blocks:
                # Extract parameter names
                param_names = []
                if params_str.strip():
                    # Simple parameter extraction (handles basic cases)
                    for param in params_str.split(','):
                        param = param.strip()
                        if ':' in param:
                            param_name = param.split(':')[0].strip()
                            param_names.append(param_name)
                
                # Split prompt by role sections
                user_section = ""
                if "{{ _.role(\"user\") }}" in prompt:
                    parts = prompt.split("{{ _.role(\"user\") }}")
                    if len(parts) > 1:
                        user_section = parts[1]
                elif "{{ _.role('user') }}" in prompt:
                    parts = prompt.split("{{ _.role('user') }}")
                    if len(parts) > 1:
                        user_section = parts[1]
                
                # Check if parameters are referenced in user section
                for param in param_names:
                    if param and f"{{{{ {param} }}}}" not in user_section:
                        param_errors.append(
                            f"{file_path.name}::{func_name} parameter '{param}' not in user section"
                        )
                        
        # This is a warning, not a failure (some functions might not need all params in prompt)
        if param_errors:
            print("\nWarning: Parameters not found in user section:")
            for error in param_errors:
                print(f"  - {error}")
    
    def test_template_file_exists(self):
        """Ensure TEMPLATE.baml exists for future implementations."""
        template_path = Path("baml_src/TEMPLATE.baml")
        assert template_path.exists(), "TEMPLATE.baml missing - needed for future BAML functions"
        
        # Verify template has correct structure
        content = template_path.read_text()
        assert "{{ _.role(\"system\") }}" in content, "Template missing system role example"
        assert "{{ _.role(\"user\") }}" in content, "Template missing user role example"
        assert "Claude" in content or "Gemini" in content, "Template missing model compatibility notes"


class TestBAMLValidation:
    """Additional validation tests for BAML compatibility."""
    
    @pytest.fixture
    def baml_files(self) -> List[Path]:
        """Find all BAML files in the project."""
        baml_dir = Path("baml_src")
        if not baml_dir.exists():
            pytest.skip("No baml_src directory found")
        
        # Find all .baml files except the template
        files = []
        for file in baml_dir.glob("*.baml"):
            if file.name != "TEMPLATE.baml":
                files.append(file)
        
        if not files:
            pytest.skip("No BAML files found to test")
            
        return files
    
    def test_no_array_content_in_prompts(self, baml_files):
        """Ensure prompts don't use array content format (breaks with some models)."""
        # This is more relevant for the actual API calls, but we can check for patterns
        array_pattern_errors = []
        
        for file_path in baml_files:
            content = file_path.read_text()
            
            # Look for patterns that might indicate array usage
            if '"type":' in content and '"text":' in content:
                array_pattern_errors.append(f"{file_path.name} may contain array content format")
                
        if array_pattern_errors:
            print("\nWarning: Potential array content format detected:")
            for error in array_pattern_errors:
                print(f"  - {error}")
    
    def test_client_configuration_exists(self):
        """Ensure client configurations reference both types of models."""
        clients_path = Path("baml_src/clients.baml")
        if not clients_path.exists():
            pytest.skip("No clients.baml file found")
            
        content = clients_path.read_text()
        
        # Check for model diversity in client configurations
        has_openai = "gpt" in content.lower() or "openai" in content.lower()
        has_claude = "claude" in content.lower() or "anthropic" in content.lower()
        has_gemini = "gemini" in content.lower() or "google" in content.lower()
        has_o_series = "gpto3" in content or "o3" in content or "o1" in content
        
        models_found = []
        if has_openai:
            models_found.append("OpenAI")
        if has_claude:
            models_found.append("Claude")
        if has_gemini:
            models_found.append("Gemini")
        if has_o_series:
            models_found.append("O-series")
            
        assert len(models_found) >= 2, (
            f"Client configuration should support multiple model types. "
            f"Found: {models_found}. Need at least OpenAI + Claude/Gemini for testing."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])