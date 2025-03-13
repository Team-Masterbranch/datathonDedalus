"""Logger module for the project.

This module provides a centralized logging configuration for the entire project.
It sets up logging with proper formatting, file handling, and log levels.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

__all__ = ['logger', 'setup_logger']

# Constants
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = logging.INFO
LOG_FILE_NAME = f"app_{datetime.now().strftime('%Y%m%d')}.log"
LOG_DIR = Path(__file__).parent.parent / "logs"

def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Set up and configure logger instance."""
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    # Create file handler
    LOG_DIR.mkdir(exist_ok=True)  # Create logs directory if it doesn't exist
    file_path = LOG_DIR / (log_file or LOG_FILE_NAME)
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Create default logger instance
logger = setup_logger(__name__)