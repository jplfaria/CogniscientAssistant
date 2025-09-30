"""BAML-specific logging configuration and utilities.

This module provides enhanced logging for BAML operations including:
- Structured logging for BAML function calls
- Performance metrics tracking
- Error context preservation
- Request/response logging with privacy controls
"""

import logging
import json
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path
import os


class BAMLLoggerConfig:
    """Configuration for BAML-specific logging."""

    def __init__(
        self,
        log_dir: Optional[str] = None,
        log_level: str = "INFO",
        enable_request_logging: bool = True,
        enable_response_logging: bool = True,
        enable_performance_logging: bool = True,
        max_log_size_mb: int = 100,
        backup_count: int = 5,
        log_privacy_mode: bool = False,
    ):
        """Initialize BAML logger configuration.

        Args:
            log_dir: Directory for log files (default: .aicoscientist/logs/baml)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            enable_request_logging: Log BAML requests
            enable_response_logging: Log BAML responses
            enable_performance_logging: Log performance metrics
            max_log_size_mb: Max size of each log file in MB
            backup_count: Number of backup log files to keep
            log_privacy_mode: If True, redact sensitive information
        """
        self.log_dir = log_dir or os.path.join(".aicoscientist", "logs", "baml")
        self.log_level = log_level
        self.enable_request_logging = enable_request_logging
        self.enable_response_logging = enable_response_logging
        self.enable_performance_logging = enable_performance_logging
        self.max_log_size_mb = max_log_size_mb
        self.backup_count = backup_count
        self.log_privacy_mode = log_privacy_mode

        # Ensure log directory exists
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)


class BAMLLogger:
    """Enhanced logger for BAML operations."""

    def __init__(self, config: Optional[BAMLLoggerConfig] = None):
        """Initialize BAML logger.

        Args:
            config: Logger configuration (uses defaults if not provided)
        """
        self.config = config or BAMLLoggerConfig()
        self._setup_loggers()

    def _setup_loggers(self):
        """Set up specialized loggers for different aspects of BAML operations."""
        # Main BAML operations logger
        self.operations_logger = logging.getLogger("baml.operations")
        self.operations_logger.setLevel(getattr(logging, self.config.log_level))

        # Performance metrics logger
        self.performance_logger = logging.getLogger("baml.performance")
        self.performance_logger.setLevel(logging.INFO)

        # Error logger
        self.error_logger = logging.getLogger("baml.errors")
        self.error_logger.setLevel(logging.WARNING)

        # Set up file handlers
        self._setup_file_handlers()

    def _setup_file_handlers(self):
        """Set up rotating file handlers for each logger."""
        from logging.handlers import RotatingFileHandler

        max_bytes = self.config.max_log_size_mb * 1024 * 1024

        # Operations log
        operations_handler = RotatingFileHandler(
            os.path.join(self.config.log_dir, "operations.log"),
            maxBytes=max_bytes,
            backupCount=self.config.backup_count,
        )
        operations_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        self.operations_logger.addHandler(operations_handler)

        # Performance log
        performance_handler = RotatingFileHandler(
            os.path.join(self.config.log_dir, "performance.log"),
            maxBytes=max_bytes,
            backupCount=self.config.backup_count,
        )
        performance_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(message)s")
        )
        self.performance_logger.addHandler(performance_handler)

        # Error log
        error_handler = RotatingFileHandler(
            os.path.join(self.config.log_dir, "errors.log"),
            maxBytes=max_bytes,
            backupCount=self.config.backup_count,
        )
        error_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s\n"
                "%(exc_info)s"
            )
        )
        self.error_logger.addHandler(error_handler)

    def _redact_sensitive_data(self, data: Any) -> Any:
        """Redact sensitive information from data if privacy mode is enabled.

        Args:
            data: Data to redact (dict, str, etc.)

        Returns:
            Redacted data
        """
        if not self.config.log_privacy_mode:
            return data

        if isinstance(data, dict):
            redacted = {}
            for key, value in data.items():
                if any(
                    sensitive in key.lower()
                    for sensitive in ["password", "token", "key", "secret", "api"]
                ):
                    redacted[key] = "***REDACTED***"
                elif isinstance(value, dict):
                    redacted[key] = self._redact_sensitive_data(value)
                else:
                    redacted[key] = value
            return redacted
        elif isinstance(data, str):
            # Redact potential API keys or tokens in strings
            if len(data) > 20 and any(
                c.isalnum() for c in data
            ):
                # Looks like it might be a token
                return f"{data[:4]}...{data[-4:]}"
            return data
        else:
            return data

    def log_request(
        self,
        function_name: str,
        client_name: str,
        parameters: Dict[str, Any],
        request_id: Optional[str] = None,
    ):
        """Log a BAML function request.

        Args:
            function_name: Name of BAML function being called
            client_name: Name of BAML client being used
            parameters: Function parameters
            request_id: Optional request ID for tracking
        """
        if not self.config.enable_request_logging:
            return

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "request",
            "function": function_name,
            "client": client_name,
            "request_id": request_id,
            "parameters": self._redact_sensitive_data(parameters),
        }

        self.operations_logger.info(f"BAML Request: {json.dumps(log_entry)}")

    def log_response(
        self,
        function_name: str,
        client_name: str,
        success: bool,
        duration: float,
        request_id: Optional[str] = None,
        error: Optional[str] = None,
        response_summary: Optional[Dict[str, Any]] = None,
    ):
        """Log a BAML function response.

        Args:
            function_name: Name of BAML function
            client_name: Name of BAML client
            success: Whether call succeeded
            duration: Duration in seconds
            request_id: Optional request ID
            error: Error message if failed
            response_summary: Summary of response (not full response for privacy)
        """
        if not self.config.enable_response_logging:
            return

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "response",
            "function": function_name,
            "client": client_name,
            "request_id": request_id,
            "success": success,
            "duration_seconds": duration,
            "error": error,
            "response_summary": self._redact_sensitive_data(response_summary)
            if response_summary
            else None,
        }

        if success:
            self.operations_logger.info(f"BAML Response: {json.dumps(log_entry)}")
        else:
            self.error_logger.error(f"BAML Error: {json.dumps(log_entry)}")

    def log_performance(
        self,
        function_name: str,
        client_name: str,
        duration: float,
        tokens_used: Optional[int] = None,
        cache_hit: bool = False,
    ):
        """Log performance metrics for a BAML call.

        Args:
            function_name: Name of BAML function
            client_name: Name of BAML client
            duration: Duration in seconds
            tokens_used: Number of tokens consumed (if available)
            cache_hit: Whether response was cached
        """
        if not self.config.enable_performance_logging:
            return

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "function": function_name,
            "client": client_name,
            "duration_seconds": duration,
            "tokens_used": tokens_used,
            "cache_hit": cache_hit,
        }

        self.performance_logger.info(f"Performance: {json.dumps(metrics)}")

    def log_retry_attempt(
        self,
        function_name: str,
        client_name: str,
        attempt: int,
        max_attempts: int,
        error: str,
    ):
        """Log a retry attempt.

        Args:
            function_name: Name of BAML function
            client_name: Name of BAML client
            attempt: Current attempt number
            max_attempts: Maximum retry attempts
            error: Error that triggered retry
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "retry",
            "function": function_name,
            "client": client_name,
            "attempt": attempt,
            "max_attempts": max_attempts,
            "error": error[:200] if error else None,  # Truncate long errors
        }

        self.operations_logger.warning(f"BAML Retry: {json.dumps(log_entry)}")

    def log_fallback(
        self,
        function_name: str,
        from_client: str,
        to_client: str,
        reason: str,
        success: bool,
    ):
        """Log a client fallback event.

        Args:
            function_name: Name of BAML function
            from_client: Original client name
            to_client: Fallback client name
            reason: Reason for fallback
            success: Whether fallback succeeded
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "fallback",
            "function": function_name,
            "from_client": from_client,
            "to_client": to_client,
            "reason": reason,
            "success": success,
        }

        self.operations_logger.warning(f"BAML Fallback: {json.dumps(log_entry)}")

    def log_circuit_breaker_event(
        self,
        client_name: str,
        event_type: str,  # "opened", "closed", "half_open"
        failure_count: int,
    ):
        """Log a circuit breaker state change.

        Args:
            client_name: Name of BAML client
            event_type: Type of circuit breaker event
            failure_count: Number of failures that triggered event
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "circuit_breaker",
            "client": client_name,
            "event": event_type,
            "failure_count": failure_count,
        }

        self.error_logger.warning(f"Circuit Breaker: {json.dumps(log_entry)}")

    def get_performance_summary(
        self,
        since: Optional[datetime] = None,
        function_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get summary of performance metrics.

        Args:
            since: Only include metrics after this time
            function_name: Only include specific function

        Returns:
            Dictionary with performance statistics
        """
        # This is a simplified implementation
        # In production, you'd parse the performance log file
        return {
            "note": "Performance summary not yet implemented",
            "since": since.isoformat() if since else None,
            "function": function_name,
        }


# Global BAML logger instance
_baml_logger: Optional[BAMLLogger] = None


def get_baml_logger(config: Optional[BAMLLoggerConfig] = None) -> BAMLLogger:
    """Get or create the global BAML logger instance.

    Args:
        config: Logger configuration (only used on first call)

    Returns:
        BAML logger instance
    """
    global _baml_logger
    if _baml_logger is None:
        _baml_logger = BAMLLogger(config)
    return _baml_logger


def configure_baml_logging(**kwargs) -> BAMLLogger:
    """Configure BAML logging with custom settings.

    Args:
        **kwargs: Configuration parameters for BAMLLoggerConfig

    Returns:
        Configured BAML logger
    """
    config = BAMLLoggerConfig(**kwargs)
    global _baml_logger
    _baml_logger = BAMLLogger(config)
    return _baml_logger