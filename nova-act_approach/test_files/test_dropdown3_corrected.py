#!/usr/bin/env python3
"""
Test script for the corrected hard_form_automation3_corrected.py implementation
Testing only the implemented functions:
1. select_dropdown_option()
2. fill_date_field()
"""

import os
import logging
import sys
import time
from dotenv import load_dotenv
from nova_act import NovaAct

# Import the functions to test and utility functions
from hard_form_automation3_corrected import select_dropdown_option, fill_date_field
from utils_final import setup_logging

# Load environment variables from .env file
load_dotenv()

# URL for the hard form
FORM_URL = "https://asteroid.ai/form"

def run_tests():
    """
    Run tests for the corrected hard form automation functions.
    Testing only select_dropdown_option and fill_date_field.
    """
    logger = setup_logging()
    logger.info("Starting corrected hard form automation function tests")
    
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
            
            # Initial page loading
            logger.info("Waiting for the form to load")
            time.sleep(4)  # Give the page time to load
            
            # Scroll to see the form fields
            logger.info("Scrolling to Contact Details section")
            nova.act("Scroll down until you can see the form fields in the Contact Details section")
            time.sleep(1)
            
            # ------------------------------------
            # Test 1: Dropdown Selection
            # ------------------------------------
            logger.info("TEST 1: Dropdown Selection")
            dropdown_success = select_dropdown_option(nova, "Title", "Prof")
            
            if dropdown_success:
                logger.info("Dropdown selection test PASSED")
            else:
                logger.error("Dropdown selection test FAILED")
                return 1
            
            # ------------------------------------
            # Test 2: Date Field
            # ------------------------------------
            logger.info("TEST 2: Date Field")
            date_success = fill_date_field(nova, "Date of Birth", "1985-06-15")
            
            if date_success:
                logger.info("Date field test PASSED")
            else:
                logger.error("Date field test FAILED")
                return 1
            
            # Allow user to observe the results before continuing
            input("All tests PASSED! Press Enter to continue...")
            return 0
                
    except Exception as e:
        logger.exception(f"Error during tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())