"""
Production-grade logging configuration for the backend.

Provides centralized logging setup with:
- Console output with colored formatting
- Optional file output with rotation
- Configurable log levels
- Module-specific loggers
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional


# ANSI color codes for console output
class LogColors:
    """ANSI color codes for log levels."""
    RESET = "\033[0m"
    DEBUG = "\033[36m"     # Cyan
    INFO = "\033[32m"      # Green
    WARNING = "\033[33m"   # Yellow
    ERROR = "\033[31m"     # Red
    CRITICAL = "\033[35m"  # Magenta
    TIMESTAMP = "\033[90m" # Gray
    MODULE = "\033[34m"    # Blue


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console."""
    
    LEVEL_COLORS = {
        logging.DEBUG: LogColors.DEBUG,
        logging.INFO: LogColors.INFO,
        logging.WARNING: LogColors.WARNING,
        logging.ERROR: LogColors.ERROR,
        logging.CRITICAL: LogColors.CRITICAL,
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Get color for this level
        level_color = self.LEVEL_COLORS.get(record.levelno, LogColors.RESET)
        
        # Format the timestamp
        timestamp = self.formatTime(record, self.datefmt)
        
        # Build the colored message
        parts = [
            f"{LogColors.TIMESTAMP}{timestamp}{LogColors.RESET}",
            f"{level_color}{record.levelname:<8}{LogColors.RESET}",
            f"{LogColors.MODULE}{record.name}{LogColors.RESET}",
            record.getMessage(),
        ]
        
        formatted = " | ".join(parts)
        
        # Add exception info if present
        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)
        
        return formatted


class PlainFormatter(logging.Formatter):
    """Plain text formatter for file output."""
    
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = False,
    log_file_path: str = "logs/app.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Configure application-wide logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to save logs to file
        log_file_path: Path to the log file
        max_bytes: Maximum size of each log file before rotation (default 10MB)
        backup_count: Number of backup files to keep (default 5)
    """
    # Parse log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter(datefmt="%Y-%m-%d %H:%M:%S"))
    root_logger.addHandler(console_handler)
    
    # File handler with rotation (if enabled)
    if log_to_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(PlainFormatter())
        root_logger.addHandler(file_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    # Log startup message
    logger = get_logger("logging")
    logger.info(f"Logging initialized: level={log_level}, file={log_to_file}")
    if log_to_file:
        logger.info(f"Log file: {log_file_path} (max {max_bytes // 1024 // 1024}MB, {backup_count} backups)")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically module name like 'agentbay', 'agent')
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = get_logger("agentbay")
        >>> logger.info("Session created")
        >>> logger.error("Connection failed", exc_info=True)
    """
    return logging.getLogger(name)

