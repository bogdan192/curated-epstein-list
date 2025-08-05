"""Logging configuration for the Epstein List project."""

import logging
import sys
from pathlib import Path
from config import Config

def setup_logging(level=logging.INFO, enable_file_logging=True):
    """Set up logging configuration."""
    
    # Create logger
    logger = logging.getLogger('epstein_list')
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if enabled
    if enable_file_logging:
        log_file = Config.OUTPUT_DIRECTORY / 'epstein_list.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger():
    """Get the configured logger."""
    return logging.getLogger('epstein_list')