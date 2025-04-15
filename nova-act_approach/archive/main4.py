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
from nova_act import NovaAct

# Import from our utils module
from utils_final import setup_logging, load_json_data

# Load environment variables from .env file
load_dotenv()

# Nova-ACT API key environment variable name
NOVA_ACT_API_KEY_ENV = "NOVA_ACT_API_KEY"

# Form URLs
FORM_URLS = {
    "easy": "https://asteroid.ai/form2",
    "hard": "https://asteroid.ai/form"
}

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
    
    parser.add_argument(
        "--form",
        choices=["easy", "hard"],
        required=True,
        help="Form type to automate (easy or hard)"
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
        str: The API key
        
    Raises:
        RuntimeError: If the API key is not found
    """
    logger = logging.getLogger("nova_form_automation")
    
    # Check environment variable
    api_key = os.environ.get(NOVA_ACT_API_KEY_ENV)
    if api_key:
        logger.info(f"Using API key from {NOVA_ACT_API_KEY_ENV} environment variable")
        return api_key
    
    # No API key found - raise exception
    error_msg = f"No API key found. Please set {NOVA_ACT_API_KEY_ENV} in your .env file"
    logger.error(error_msg)
    raise RuntimeError(error_msg)

def initialize_nova_act(form_type, headless=False):
    """
    Initialize the Nova-ACT browser for form automation.
    
    Args:
        form_type: Type of form to automate ("easy" or "hard")
        headless: Whether to run in headless mode
        
    Returns:
        NovaAct: Initialized NovaAct instance
        
    Raises:
        ValueError: If the form type is unknown
        Exception: If Nova-ACT initialization fails
    """
    logger = logging.getLogger("nova_form_automation")
    
    # Get form URL based on form type
    form_url = FORM_URLS.get(form_type)
    if not form_url:
        error_msg = f"Unknown form type: {form_type}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info(f"Initializing Nova-ACT for {form_type} form at {form_url}")
    
    # Initialize Nova-ACT (without video recording)
    try:
        nova = NovaAct(
            starting_page=form_url,
            headless=headless
        )
        
        logger.info("Nova-ACT initialized successfully")
        return nova
        
    except Exception as e:
        logger.exception(f"Error initializing Nova-ACT: {e}")
        raise

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
    logger.info(f"Form type: {args.form}")
    logger.info(f"Data file: {args.data}")
    logger.info(f"Headless mode: {args.headless}")
    
    try:
        # Get the API key - will raise an exception if not found
        api_key = get_api_key()
        
        # Load form data
        logger.info(f"Loading form data from {args.data}")
        form_data = load_json_data(args.data)
        if not form_data:
            logger.error("Failed to load form data")
            return 1
        
        # Initialize Nova-ACT
        nova = initialize_nova_act(args.form, args.headless)
        
        # Use Nova-ACT in a context manager to ensure proper cleanup
        with nova:
            logger.info("Browser started successfully")
            
            # TODO: Implement form automation
            logger.info("Starting form automation")
            
            # Just a simple test to verify basic browser functionality
            logger.info("Taking screenshot to verify browser functionality")
            screenshot_path = f"{args.form}_form_screenshot.png"
            nova.page.screenshot(path=screenshot_path)
            logger.info(f"Screenshot saved to {screenshot_path}")
            
            logger.info("Form automation completed successfully")
            
        return 0
        
    except RuntimeError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Error during form automation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())