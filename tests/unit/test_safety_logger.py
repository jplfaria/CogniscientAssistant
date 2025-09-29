"""Unit tests for SafetyLogger class."""

import asyncio
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
import shutil
import tempfile
from unittest.mock import patch, AsyncMock, Mock
import pytest

from src.core.safety import SafetyConfig, SafetyLogger, SafetyCheck, SafetyLevel


class TestSafetyLogger:
    """Test suite for SafetyLogger class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test logs."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def config(self, temp_dir):
        """Create a test SafetyConfig."""
        return SafetyConfig(
            enabled=True,
            trust_level="standard",
            log_only_mode=True,
            log_directory=temp_dir / "safety_logs",
            blocking_threshold=0.95,
            retention_days=30
        )
    
    @pytest.fixture
    def disabled_config(self, temp_dir):
        """Create a disabled SafetyConfig."""
        return SafetyConfig(
            enabled=False,
            log_directory=temp_dir / "safety_logs"
        )
    
    @pytest.fixture
    async def logger(self, config):
        """Create a SafetyLogger instance."""
        return SafetyLogger(config)
    
    def test_initialization(self, config):
        """Test SafetyLogger initialization."""
        logger = SafetyLogger(config)
        
        assert logger.enabled == config.enabled
        assert logger.trust_level == config.trust_level
        assert logger.log_only == config.log_only_mode
        assert logger.config == config
        assert logger.log_directory == config.log_directory
    
    def test_log_directory_creation(self, config):
        """Test that log directory is created on initialization."""
        # Ensure directory doesn't exist
        if config.log_directory.exists():
            shutil.rmtree(config.log_directory)
        
        assert not config.log_directory.exists()
        
        logger = SafetyLogger(config)
        
        assert config.log_directory.exists()
        assert config.log_directory.is_dir()
    
    @pytest.mark.asyncio
    async def test_log_research_goal_disabled(self, disabled_config):
        """Test logging when safety is disabled."""
        logger = SafetyLogger(disabled_config)
        
        result = await logger.log_research_goal(
            "Test research goal",
            {"domain": "test", "user_role": "researcher"}
        )
        
        assert result.decision == SafetyLevel.SAFE
        assert result.safety_score == 1.0
        assert result.reasoning == "Safety logging disabled"
        assert result.input_hash is None
        
        # No log files should be created
        log_files = list(disabled_config.log_directory.glob("*.json"))
        assert len(log_files) == 0
    
    @pytest.mark.asyncio
    async def test_log_research_goal_enabled(self, logger, config):
        """Test logging a research goal with safety enabled."""
        goal = "Study protein folding in neurodegenerative diseases"
        context = {
            "domain": "neuroscience",
            "user_role": "researcher",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        result = await logger.log_research_goal(goal, context)
        
        assert result.decision == SafetyLevel.SAFE
        assert result.safety_score == 1.0
        assert result.reasoning == "Logged for monitoring"
        assert "log_id" in result.metadata
        assert result.input_hash is not None
        
        # Check that log file was created
        log_files = list(config.log_directory.glob("*.json"))
        assert len(log_files) > 0
    
    @pytest.mark.asyncio
    async def test_log_hypothesis(self, logger, config):
        """Test logging a hypothesis."""
        hypothesis_data = {
            "id": "hyp_001",
            "content": "Test hypothesis content",
            "research_goal_id": "goal_001",
            "generation_context": {"strategy": "literature_based"}
        }
        
        result = await logger.log_hypothesis(hypothesis_data)
        
        assert result.decision == SafetyLevel.SAFE
        assert result.safety_score == 1.0
        assert result.reasoning == "Hypothesis logged for pattern tracking"
        assert "log_id" in result.metadata
        
        # Verify log entry
        log_files = list(config.log_directory.glob("*.json"))
        assert len(log_files) > 0
    
    @pytest.mark.asyncio
    async def test_create_log_entry(self, logger):
        """Test creating a log entry."""
        content = "Test content"
        context = {"test": "context"}
        event_type = "test_event"
        
        log_entry = await logger._create_log_entry(content, context, event_type)
        
        assert log_entry.id is not None
        assert log_entry.timestamp is not None
        assert log_entry.event_type == event_type
        assert log_entry.content_hash is not None
        assert log_entry.metadata == context
        assert log_entry.trust_level == logger.trust_level
    
    @pytest.mark.asyncio
    async def test_hash_content(self, logger):
        """Test content hashing."""
        content = "Test content for hashing"
        
        hash1 = await logger._hash_content(content)
        hash2 = await logger._hash_content(content)
        hash3 = await logger._hash_content("Different content")
        
        # Same content should produce same hash
        assert hash1 == hash2
        # Different content should produce different hash
        assert hash1 != hash3
        # Should be a valid SHA-256 hex string (64 characters)
        assert len(hash1) == 64
        assert all(c in "0123456789abcdef" for c in hash1)
    
    @pytest.mark.asyncio
    async def test_write_log_entry(self, logger, config):
        """Test writing a log entry to disk."""
        log_entry = await logger._create_log_entry(
            "Test content",
            {"test": "metadata"},
            "test_event"
        )
        
        await logger._write_log_entry(log_entry)
        
        # Check that file was created
        expected_filename = f"{log_entry.timestamp.strftime('%Y%m%d')}_{log_entry.id}.json"
        log_file = config.log_directory / expected_filename
        
        assert log_file.exists()
        
        # Verify content
        with open(log_file, 'r') as f:
            data = json.load(f)
        
        assert data["id"] == log_entry.id
        assert data["event_type"] == log_entry.event_type
        assert data["content_hash"] == log_entry.content_hash
    
    @pytest.mark.asyncio
    async def test_generate_pattern_report(self, logger, config):
        """Test pattern report generation."""
        # Create some test log entries
        for i in range(5):
            await logger.log_research_goal(
                f"Research goal {i}",
                {"domain": "test_domain"}
            )
        
        for i in range(3):
            await logger.log_hypothesis({
                "id": f"hyp_{i}",
                "content": f"Hypothesis {i}",
                "research_goal_id": "goal_001"
            })
        
        report = await logger.generate_pattern_report("daily")
        
        assert report.report_id is not None
        assert report.period == "daily"
        assert len(report.patterns_observed) > 0
        assert report.total_events >= 8
        assert "goal_submission" in report.event_counts
        assert "hypothesis_generation" in report.event_counts
    
    @pytest.mark.asyncio
    async def test_cleanup_old_logs(self, logger, config):
        """Test cleanup of old log files."""
        # Create some old log files
        old_date = datetime.now(timezone.utc) - timedelta(days=config.retention_days + 5)
        old_filename = f"{old_date.strftime('%Y%m%d')}_test_old.json"
        old_file = config.log_directory / old_filename
        
        # Create old file
        old_file.write_text(json.dumps({"test": "old_data"}))
        
        # Create recent file
        recent_filename = f"{datetime.now(timezone.utc).strftime('%Y%m%d')}_test_recent.json"
        recent_file = config.log_directory / recent_filename
        recent_file.write_text(json.dumps({"test": "recent_data"}))
        
        assert old_file.exists()
        assert recent_file.exists()
        
        await logger.cleanup_old_logs()
        
        # Old file should be deleted
        assert not old_file.exists()
        # Recent file should remain
        assert recent_file.exists()
    
    @pytest.mark.asyncio
    async def test_get_audit_trail(self, logger, config):
        """Test getting audit trail for a time period."""
        # Create some log entries
        await logger.log_research_goal("Goal 1", {"domain": "test"})
        await logger.log_research_goal("Goal 2", {"domain": "test"})
        await logger.log_hypothesis({
            "id": "hyp_1",
            "content": "Hypothesis 1",
            "research_goal_id": "goal_1"
        })
        
        # Get audit trail for last hour
        start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        end_time = datetime.now(timezone.utc)
        
        audit_trail = await logger.get_audit_trail(start_time, end_time)
        
        assert len(audit_trail) == 3
        assert all(entry.timestamp >= start_time for entry in audit_trail)
        assert all(entry.timestamp <= end_time for entry in audit_trail)
    
    @pytest.mark.asyncio
    async def test_trust_level_behaviors(self):
        """Test different behaviors based on trust levels."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Test "trusted" level - minimal logging
            trusted_config = SafetyConfig(
                trust_level="trusted",
                log_directory=Path(temp_dir) / "trusted"
            )
            trusted_logger = SafetyLogger(trusted_config)
            
            result = await trusted_logger.log_research_goal("Test", {})
            assert result.reasoning == "Minimal logging for trusted level"
            
            # Test "restricted" level - verbose logging
            restricted_config = SafetyConfig(
                trust_level="restricted",
                log_directory=Path(temp_dir) / "restricted"
            )
            restricted_logger = SafetyLogger(restricted_config)
            
            result = await restricted_logger.log_research_goal("Test", {})
            assert "verbose" in result.reasoning.lower() or "enhanced" in result.reasoning.lower()
            
        finally:
            shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_concurrent_logging(self, logger):
        """Test that concurrent logging operations don't conflict."""
        # Create multiple concurrent log operations
        tasks = []
        for i in range(10):
            task = logger.log_research_goal(
                f"Concurrent goal {i}",
                {"index": i}
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(results) == 10
        assert all(r.decision == SafetyLevel.SAFE for r in results)
        
        # All should have unique log IDs
        log_ids = [r.metadata.get("log_id") for r in results if "log_id" in r.metadata]
        assert len(log_ids) == len(set(log_ids))  # All unique
    
    def test_is_safety_check_needed(self):
        """Test logic for determining if safety check is needed."""
        # Standard level should need checks
        config = SafetyConfig(trust_level="standard")
        logger = SafetyLogger(config)
        assert logger.is_safety_check_needed()
        
        # Trusted level should not need checks
        config = SafetyConfig(trust_level="trusted")
        logger = SafetyLogger(config)
        assert not logger.is_safety_check_needed()
        
        # Disabled safety should not need checks
        config = SafetyConfig(enabled=False)
        logger = SafetyLogger(config)
        assert not logger.is_safety_check_needed()