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

# Import from our utils module
from utils_final import setup_logging, load_json_data

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
    
    parser.add_argument(
        "--api-key",
        help=f"Nova-ACT API key (can also be set via {NOVA_ACT_API_KEY_ENV} environment variable)"
    )
    
    return parser.parse_args()

def get_api_key(args):
    """
    Get the Nova-ACT API key from command-line argument or environment variable.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        str: The API key if found, None otherwise
    """
    logger = logging.getLogger("nova_form_automation")
    
    # Check command-line argument first
    if args.api_key:
        logger.info("Using API key from command-line argument")
        return args.api_key
    
    # Check environment variable
    api_key = os.environ.get(NOVA_ACT_API_KEY_ENV)
    if api_key:
        logger.info(f"Using API key from {NOVA_ACT_API_KEY_ENV} environment variable")
        return api_key
    
    # No API key found
    logger.error(f"No API key provided. Please specify --api-key or set {NOVA_ACT_API_KEY_ENV} environment variable")
    return None

def set_api_key(api_key):
    """
    Set the Nova-ACT API key as an environment variable.
    
    Args:
        api_key: The API key to set
    """
    logger = logging.getLogger("nova_form_automation")
    
    if api_key:
        logger.info("Setting Nova-ACT API key environment variable")
        os.environ[NOVA_ACT_API_KEY_ENV] = api_key
    else:
        logger.error("Cannot set empty API key")

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
        # Get and set the API key
        api_key = get_api_key(args)
        if not api_key:
            logger.error("API key is required to use Nova-ACT")
            return 1
        
        set_api_key(api_key)
        
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

#  main2.py with API key handling functionality
