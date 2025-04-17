#!/usr/bin/env python3
"""
Test script for improved hard_form_automation2.py functions
"""

import os
import logging
import sys
import time
from dotenv import load_dotenv
from nova_act import NovaAct

# Import the functions to test and utility functions
from hard_form_automation2 import select_dropdown_option, fill_date_field
from utils_final import setup_logging

# Load environment variables from .env file
load_dotenv()

# URL for the hard form
FORM_URL = "https://asteroid.ai/form"

def run_tests():
    """
    Run tests for improved hard form automation functions.
    """
    logger = setup_logging()
    logger.info("Starting improved hard form automation function tests")
    
    # Get API key from environment
    api_key = os.environ.get("NOVA_ACT_API_KEY")
    if not api_key:
        logger.error("No API key found. Please set NOVA_ACT_API_KEY in your .env file")
        return 1
    
    try:
        # Initialize Nova-ACT
        logger.info(f"Initializing Nova-ACT for hard form at {FORM_URL}")
        nova = NovaAct(
            starting_page=FORM_URL,
            headless=False,  # Use non-headless mode for visual verification
            screen_width=1920,
            screen_height=1200
        )
        
        # Use Nova-ACT in a context manager
        with nova:
            logger.info("Browser started successfully")
            
            # Wait for form to load with explicit timeout
            logger.info("Waiting for the form to load")
            time.sleep(5)  # Explicit wait to ensure page has loaded
            
            # First, explicitly tell the agent that the page is loaded and explore it
            logger.info("Exploring the form")
            nova.act("The page is fully loaded now. Scroll down to explore the entire form page from top to bottom.")
            time.sleep(2)
            
            # ------------------------------------
            # Test 1: Improved Dropdown Selection
            # ------------------------------------
            logger.info("TEST 1: Improved Dropdown Selection")
            
            # First explicitly scroll to the form section
            logger.info("Scrolling to the Contact Details section of the form")
            nova.act("Scroll down to the Contact Details section where you can see form fields")
            time.sleep(2)
            
            # Test dropdown selection - Title field
            logger.info("Testing improved dropdown selection for 'Title' field")
            dropdown_success = select_dropdown_option(nova, "Title", "Prof")
            
            if dropdown_success:
                logger.info("Improved dropdown selection test PASSED")
            else:
                logger.error("Improved dropdown selection test FAILED")
                return 1
            
            # ------------------------------------
            # Test 2: Improved Date Field
            # ------------------------------------
            logger.info("TEST 2: Improved Date Field")
            
            # Make sure we're still in the Contact Details section
            logger.info("Ensuring we're in the Contact Details section")
            nova.act("Make sure you are in the Contact Details section of the form")
            time.sleep(1)
            
            # Test date field filling - Date of Birth field with improved function
            logger.info("Testing improved date field filling for 'Date of Birth' field")
            date_success = fill_date_field(nova, "Date of Birth", "1985-06-15")
            
            if date_success:
                logger.info("Improved date field test PASSED")
            else:
                logger.error("Improved date field test FAILED")
                return 1
            
            # Allow user to observe the results before continuing
            input("All tests PASSED! Press Enter to continue...")
            return 0
                
    except Exception as e:
        logger.exception(f"Error during tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())