"""Unit tests for SafetyConfig dataclass."""

import json
from pathlib import Path
import pytest
from src.core.safety import SafetyConfig


class TestSafetyConfig:
    """Test suite for SafetyConfig dataclass."""
    
    def test_default_initialization(self):
        """Test SafetyConfig with default values."""
        config = SafetyConfig()
        
        assert config.enabled is True
        assert config.trust_level == "standard"
        assert config.log_only_mode is True
        assert config.log_directory == Path(".aicoscientist/safety_logs")
        assert config.blocking_threshold == 0.95
        assert config.retention_days == 30
    
    def test_custom_initialization(self):
        """Test SafetyConfig with custom values."""
        custom_path = Path("/custom/safety/logs")
        config = SafetyConfig(
            enabled=False,
            trust_level="trusted",
            log_only_mode=False,
            log_directory=custom_path,
            blocking_threshold=0.8,
            retention_days=60
        )
        
        assert config.enabled is False
        assert config.trust_level == "trusted"
        assert config.log_only_mode is False
        assert config.log_directory == custom_path
        assert config.blocking_threshold == 0.8
        assert config.retention_days == 60
    
    def test_trust_level_validation(self):
        """Test that trust level must be one of the allowed values."""
        valid_levels = ["trusted", "standard", "restricted"]
        
        for level in valid_levels:
            config = SafetyConfig(trust_level=level)
            assert config.trust_level == level
    
    def test_blocking_threshold_range(self):
        """Test blocking threshold must be between 0.0 and 1.0."""
        config = SafetyConfig(blocking_threshold=0.0)
        assert config.blocking_threshold == 0.0
        
        config = SafetyConfig(blocking_threshold=1.0)
        assert config.blocking_threshold == 1.0
        
        config = SafetyConfig(blocking_threshold=0.5)
        assert config.blocking_threshold == 0.5
    
    def test_to_dict(self):
        """Test conversion to dictionary for serialization."""
        config = SafetyConfig(
            enabled=True,
            trust_level="standard",
            log_only_mode=True,
            log_directory=Path(".aicoscientist/safety_logs"),
            blocking_threshold=0.95,
            retention_days=30
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["enabled"] is True
        assert config_dict["trust_level"] == "standard"
        assert config_dict["log_only_mode"] is True
        assert config_dict["log_directory"] == ".aicoscientist/safety_logs"
        assert config_dict["blocking_threshold"] == 0.95
        assert config_dict["retention_days"] == 30
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        config_dict = {
            "enabled": False,
            "trust_level": "trusted",
            "log_only_mode": False,
            "log_directory": "/custom/path",
            "blocking_threshold": 0.7,
            "retention_days": 45
        }
        
        config = SafetyConfig.from_dict(config_dict)
        
        assert config.enabled is False
        assert config.trust_level == "trusted"
        assert config.log_only_mode is False
        assert config.log_directory == Path("/custom/path")
        assert config.blocking_threshold == 0.7
        assert config.retention_days == 45
    
    def test_to_json(self):
        """Test JSON serialization."""
        config = SafetyConfig()
        json_str = config.to_json()
        
        # Should be valid JSON
        loaded = json.loads(json_str)
        assert loaded["enabled"] is True
        assert loaded["trust_level"] == "standard"
    
    def test_from_json(self):
        """Test creation from JSON string."""
        json_str = json.dumps({
            "enabled": True,
            "trust_level": "restricted",
            "log_only_mode": True,
            "log_directory": ".aicoscientist/safety_logs",
            "blocking_threshold": 0.9,
            "retention_days": 14
        })
        
        config = SafetyConfig.from_json(json_str)
        
        assert config.enabled is True
        assert config.trust_level == "restricted"
        assert config.log_only_mode is True
        assert config.blocking_threshold == 0.9
        assert config.retention_days == 14
    
    def test_get_trust_config(self):
        """Test getting trust level configuration."""
        config = SafetyConfig(trust_level="trusted")
        trust_config = config.get_trust_config()
        
        assert trust_config["description"] == "Minimal logging, no blocking"
        assert trust_config["safety_checks"] is False
        assert trust_config["logging_level"] == "minimal"
        
        config = SafetyConfig(trust_level="standard")
        trust_config = config.get_trust_config()
        
        assert trust_config["description"] == "Full logging, advisory warnings"
        assert trust_config["safety_checks"] is True
        assert trust_config["logging_level"] == "detailed"
        
        config = SafetyConfig(trust_level="restricted")
        trust_config = config.get_trust_config()
        
        assert trust_config["description"] == "Enhanced monitoring, possible delays"
        assert trust_config["safety_checks"] is True
        assert trust_config["logging_level"] == "verbose"
        assert trust_config["review_threshold"] == 0.5
    
    def test_equality(self):
        """Test SafetyConfig equality comparison."""
        config1 = SafetyConfig()
        config2 = SafetyConfig()
        config3 = SafetyConfig(trust_level="trusted")
        
        assert config1 == config2
        assert config1 != config3
    
    def test_log_directory_path_handling(self):
        """Test that log_directory is always a Path object."""
        # String path should be converted to Path
        config = SafetyConfig(log_directory="/some/string/path")
        assert isinstance(config.log_directory, Path)
        assert str(config.log_directory) == "/some/string/path"
        
        # Path object should remain as Path
        path_obj = Path("/some/path/object")
        config = SafetyConfig(log_directory=path_obj)
        assert config.log_directory == path_obj
        assert isinstance(config.log_directory, Path)