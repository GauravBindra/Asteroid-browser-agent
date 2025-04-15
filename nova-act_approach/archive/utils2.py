#!/usr/bin/env python3
"""
Utility functions for Nova-ACT form automation.
"""

import json
import logging
import os

def load_json_data(file_path):
    """
    Load and parse JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Loading data from {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            logger.debug(f"Successfully loaded data: {data}")
            return data
    except FileNotFoundError:
        logger.error(f"Error: File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error: Invalid JSON in {file_path}: {e}")
        raise

def setup_logging(log_level=logging.INFO):
    """
    Configure basic logging to console.
    
    Args:
        log_level: Logging level for console output
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("nova_form_automation")
    logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels
    
    # Remove any existing handlers (to avoid duplicates on multiple calls)
    if logger.handlers:
        logger.handlers.clear()
    
    # Create console handler and set level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

# Test function
if __name__ == "__main__":
    # Set up logging first
    logger = setup_logging(logging.INFO)
    logger.info("Testing utils module with logging")
    
    # Test JSON loading
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             "easy_form_data.json")
    
    logger.info(f"Testing with file: {file_path}")
    
    if os.path.exists(file_path):
        data = load_json_data(file_path)
        logger.info(f"Data loaded: {data}")
    else:
        logger.error(f"Test file not found: {file_path}")

#   Key additions:

#   1. Added a setup_logging function that:
#     - Creates a logger with the name "nova_form_automation"
#     - Sets up console output with a readable format (timestamp, level, message)
#     - Allows configuring the logging level (defaults to INFO)
#     - Handles cleaning up existing handlers to avoid duplicates
#     - Returns the configured logger for use in other functions
#   2. Updated the load_json_data function to:
#     - Use the logger instead of print statements
#     - Log at appropriate levels (info for operations, error for issues, debug for detailed data)
#   3. Modified the test code to:
#     - Initialize the logger first
#     - Use logger methods instead of print statements
#     - Demonstrate different logging levels