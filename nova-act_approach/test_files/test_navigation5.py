#!/usr/bin/env python3
"""
Test script for hard_form_automation5.py implementation
Testing the click_next_button() function
"""

import os
import logging
import sys
import time
from dotenv import load_dotenv
from nova_act import NovaAct

# Import the functions to test and utility functions
from hard_form_automation5 import navigate_to_tab, click_next_button
from utils_final import setup_logging

# Load environment variables from .env file
load_dotenv()

# URL for the hard form
FORM_URL = "https://asteroid.ai/form"

def run_tests():
    """
    Run tests for the hard form click_next_button function.
    Testing navigation through form sections using the Next button.
    """
    logger = setup_logging()
    logger.info("Starting Next button navigation test")
    
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
            
            # Fill some required fields in the Contact Details section to enable the Next button
            # This is necessary as the Next button may be disabled until required fields are filled
            logger.info("Filling required fields to enable Next button")
            
            nova.act("Find the field labeled 'First Name' and enter 'Test'")
            time.sleep(0.5)
            
            nova.act("Find the field labeled 'Last Name' and enter 'User'")
            time.sleep(0.5)
            
            nova.act("Find the field labeled 'Phone Number' and enter '07700123456'")
            time.sleep(0.5)
            
            # Test 1: Click Next button from Contact Details to Business Info
            logger.info("TEST 1: Clicking Next from Contact Details to Business Info")
            next_success1 = click_next_button(nova)
            
            if next_success1:
                logger.info("Next button click from Contact Details to Business Info PASSED")
                time.sleep(2)  # Give some time to observe
            else:
                logger.error("Next button click from Contact Details to Business Info FAILED")
                return 1
            
            # Fill some required fields in the Business Info section to enable the Next button
            logger.info("Filling required fields to enable Next button")
            
            nova.act("Find the field labeled 'Business Name' and enter 'Test Company'")
            time.sleep(0.5)
            
            # Test 2: Click Next button from Business Info to Premises Details
            logger.info("TEST 2: Clicking Next from Business Info to Premises Details")
            next_success2 = click_next_button(nova)
            
            if next_success2:
                logger.info("Next button click from Business Info to Premises Details PASSED")
                time.sleep(2)  # Give some time to observe
            else:
                logger.error("Next button click from Business Info to Premises Details FAILED")
                return 1
            
            # Allow user to observe the results before continuing
            input("Navigation tests PASSED! Press Enter to continue...")
            return 0
                
    except Exception as e:
        logger.exception(f"Error during Next button test: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())