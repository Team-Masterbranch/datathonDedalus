import sys
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

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

def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Set up and configure logger instance."""
    # Create logger
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Set the base level from config
        logger.setLevel(getattr(logging, LOG_LEVEL))

        # Create formatters
        formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

        # Create file handler
        LOGS_DIR.mkdir(exist_ok=True)
        file_path = LOGS_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        if log_file:
            file_path = LOGS_DIR / log_file
            
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(getattr(logging, LOG_LEVEL))
        file_handler.setFormatter(formatter)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, LOG_LEVEL))
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Configure root logger
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT
)

# Create module logger
logger = setup_logger(__name__)
