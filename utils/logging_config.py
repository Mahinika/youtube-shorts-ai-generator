"""
Logging configuration for the YouTube Shorts generation project.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configure logging system with file and console handlers.

    Args:
        log_level: Logging level (e.g., logging.DEBUG, logging.INFO)
        log_file: Path to log file. If None, uses default 'logs/script_generation.log'
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep

    Returns:
        Configured logger instance
    """

    # Create logs directory if it doesn't exist
    if log_file is None:
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        log_file = logs_dir / "script_generation.log"
    else:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

    # Get or create logger
    logger = logging.getLogger("youtube_shorts")
    logger.setLevel(log_level)

    # Avoid duplicate handlers if logger is already configured
    if logger.handlers:
        return logger

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )

    # File handler with rotation
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Log the setup
    logger.info(f"Logging configured - Level: {logging.getLevelName(log_level)}, File: {log_file}")

    return logger


def get_logger(name: str = "youtube_shorts") -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (should be a child of youtube_shorts)

    Returns:
        Logger instance
    """
    return logging.getLogger(f"youtube_shorts.{name}")


# Global logger instance
logger = setup_logging()
