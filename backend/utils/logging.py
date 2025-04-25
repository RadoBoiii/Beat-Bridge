"""
Logging Utilities

This module provides utilities for logging in the BeatBridge application.
"""

import os
import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Set up logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, logs to console only)
    """
    # Convert log level string to constant
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler if log file is specified
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Suppress noisy loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('chardet').setLevel(logging.WARNING)
    logging.getLogger('googleapiclient').setLevel(logging.WARNING)
    
    logging.info(f"Logging configured with level {log_level}")


def log_error(logger, message: str, exc_info: Optional[Exception] = None) -> None:
    """
    Log an error message with exception info if provided.
    
    Args:
        logger: Logger instance
        message: Error message
        exc_info: Exception information (if available)
    """
    if exc_info:
        logger.error(f"{message}: {str(exc_info)}", exc_info=exc_info)
    else:
        logger.error(message)


def log_request(logger, method: str, url: str, params: Optional[dict] = None, status_code: Optional[int] = None) -> None:
    """
    Log an API request.
    
    Args:
        logger: Logger instance
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        params: Request parameters (optional)
        status_code: Response status code (optional)
    """
    message = f"{method} {url}"
    
    if params:
        # Mask sensitive parameters
        masked_params = {}
        for key, value in params.items():
            if key.lower() in ('token', 'key', 'secret', 'password', 'auth'):
                masked_params[key] = '********'
            else:
                masked_params[key] = value
        
        message += f" params={masked_params}"
    
    if status_code:
        message += f" status={status_code}"
    
    logger.debug(message)