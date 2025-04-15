#!/usr/bin/env python3
"""
Main entry point for Nova-ACT form automation.

This module handles command-line arguments and orchestrates the form automation process.
"""

import argparse
import logging
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Import from our utils module
from utils_final import setup_logging, load_json_data

# Load environment variables from .env file
load_dotenv()

# Nova-ACT API key environment variable name
NOVA_ACT_API_KEY_ENV = "NOVA_ACT_API_KEY"

def parse_arguments():
    """
    Parse command-line arguments for the form automation tool.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Nova-ACT Form Automation for Asteroid Challenge",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required arguments
    parser.add_argument(
        "--data", 
        required=True,
        help="Path to JSON file containing form data"
    )
    
    # Optional arguments
    parser.add_argument(
        "--headless", 
        action="store_true",
        help="Run browser in headless mode"
    )
    
    return parser.parse_args()

def get_api_key():
    """
    Get the Nova-ACT API key from environment variable.
    
    Returns:
        str: The API key if found, None otherwise
    """
    logger = logging.getLogger("nova_form_automation")
    
    # Check environment variable
    api_key = os.environ.get(NOVA_ACT_API_KEY_ENV)
    if api_key:
        logger.info(f"Using API key from {NOVA_ACT_API_KEY_ENV} environment variable")
        return api_key
    
    # No API key found
    logger.error(f"No API key found. Please set {NOVA_ACT_API_KEY_ENV} in your .env file")
    return None

def main():
    """
    Main function to orchestrate the form automation process.
    
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    # Set up logging
    logger = setup_logging()
    logger.info("Starting Nova-ACT form automation")
    
    # Log parsed arguments
    logger.info(f"Data file: {args.data}")
    logger.info(f"Headless mode: {args.headless}")
    
    try:
        # Get the API key
        api_key = get_api_key()
        if not api_key:
            logger.error("API key is required to use Nova-ACT")
            return 1
        
        # Load form data
        logger.info(f"Loading form data from {args.data}")
        form_data = load_json_data(args.data)
        
        # Just print the data for now as a placeholder
        logger.info(f"Form data loaded: {form_data}")
        
        # TODO: Initialize Nova-ACT and perform form automation
        
        logger.info("Form automation completed successfully")
        return 0
        
    except Exception as e:
        logger.exception(f"Error during form automation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())