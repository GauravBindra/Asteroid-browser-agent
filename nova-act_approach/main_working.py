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
from datetime import datetime
from dotenv import load_dotenv
from nova_act import NovaAct

# Import from our utils module
from utils_final import setup_logging, load_json_data

# Import form automation functions
from form_automation_working import automate_easy_form

# Load environment variables from .env file
load_dotenv()

# Nova-ACT API key environment variable name
NOVA_ACT_API_KEY_ENV = "NOVA_ACT_API_KEY"

# Form URLs
FORM_URLS = {
    "easy": "https://asteroid.ai/form2",
    "hard": "https://asteroid.ai/form"
}

# Screenshot directory
SCREENSHOT_DIR = Path("nova-act_approach/screenshots")

def ensure_screenshot_dir():
    """
    Ensure screenshot directory exists.
    """
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

def generate_screenshot_path(form_type, description):
    """
    Generate a screenshot file path with timestamp.
    
    Args:
        form_type: Type of form ("easy" or "hard")
        description: Description of the screenshot
        
    Returns:
        Path: Path object for the screenshot file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{form_type}_form_{description}_{timestamp}.png"
    return SCREENSHOT_DIR / filename

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
    
    parser.add_argument(
        "--screenshots",
        action="store_true", 
        help="Capture screenshots during automation"
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
    
    # Initialize Nova-ACT
    try:
        # Using recommended viewport dimensions to avoid warnings
        nova = NovaAct(
            starting_page=form_url,
            headless=headless,
            screen_width=1920,
            screen_height=1200  # Within NovaAct's recommended bounds
        )
        
        logger.info("Nova-ACT initialized successfully")
        return nova
        
    except Exception as e:
        logger.exception(f"Error initializing Nova-ACT: {e}")
        raise

def capture_full_page_screenshot(nova, file_path):
    """
    Capture a full page screenshot.
    
    Args:
        nova: NovaAct instance
        file_path: Path to save the screenshot
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger = logging.getLogger("nova_form_automation")
    
    try:
        # Capture full page screenshot
        logger.info(f"Capturing full page screenshot to {file_path}")
        nova.page.screenshot(path=str(file_path), full_page=True)
        logger.info(f"Screenshot saved to {file_path}")
        return True
        
    except Exception as e:
        logger.exception(f"Error capturing screenshot: {e}")
        return False

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
    logger.info(f"Screenshots: {args.screenshots}")
    
    # Ensure screenshot directory exists if screenshots are enabled
    if args.screenshots:
        ensure_screenshot_dir()
    
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
            
            # Take initial screenshot if enabled
            if args.screenshots:
                screenshot_path = generate_screenshot_path(args.form, "initial")
                capture_full_page_screenshot(nova, screenshot_path)
            
            # Run form automation based on form type
            if args.form == "easy":
                logger.info("Running easy form automation")
                success, result_code = automate_easy_form(nova, form_data)
                
                # Take final screenshot if enabled
                if args.screenshots:
                    screenshot_path = generate_screenshot_path(args.form, "final")
                    capture_full_page_screenshot(nova, screenshot_path)
                
                # Report result
                if success:
                    logger.info(f"Form automation completed successfully! Result: {result_code}")
                    return 0
                else:
                    logger.error(f"Form automation failed. Result: {result_code}")
                    return 1
            else:
                # Hard form not implemented yet
                logger.error("Hard form automation not yet implemented")
                return 1
            
    except RuntimeError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Error during form automation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
