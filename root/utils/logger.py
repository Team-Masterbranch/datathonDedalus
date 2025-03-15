"""Logger module for the project.

This module provides a centralized logging configuration for the entire project.
It sets up logging with proper formatting, file handling, and log levels.
"""

import sys
import logging
from datetime import datetime
from typing import Optional

from .config import (
    LOGS_DIR,
    LOG_FORMAT,
    DATE_FORMAT,
    LOG_LEVEL,
)

if sys.stdout.encoding != 'utf-8':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

__all__ = ['setup_logger']

# Use config constants and derive other values
LOG_FILE_NAME = f"app_{datetime.now().strftime('%Y%m%d')}.log"

def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Set up and configure logger instance."""
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))  # Convert string level to logging constant

    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    # Create file handler with UTF-8 encoding
    LOGS_DIR.mkdir(exist_ok=True)  # Create logs directory if it doesn't exist
    file_path = LOGS_DIR / (log_file or LOG_FILE_NAME)
    file_handler = logging.FileHandler(file_path, encoding='utf-8')
    file_handler.setLevel(getattr(logging, LOG_LEVEL))
    file_handler.setFormatter(formatter)

    # Create console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)  # Explicitly use stdout
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Create default logger instance
logger = setup_logger(__name__)