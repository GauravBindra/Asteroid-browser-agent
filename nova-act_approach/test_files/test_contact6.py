#!/usr/bin/env python3
"""
Test script for hard_form_automation6.py implementation
Testing the fill_contact_details() function
"""

import os
import logging
import sys
import time
import json
from dotenv import load_dotenv
from nova_act import NovaAct

# Import the functions to test and utility functions
from hard_form_automation6 import fill_contact_details
from utils_final import setup_logging

# Load environment variables from .env file
load_dotenv()

# URL for the hard form
FORM_URL = "https://asteroid.ai/form"

def run_tests():
    """
    Run tests for the fill_contact_details function of the hard form automation.
    Tests complete filling of the Contact Details section and navigation to next section.
    """
    logger = setup_logging()
    logger.info("Starting Contact Details section test")
    
    # Get API key from environment
    api_key = os.environ.get("NOVA_ACT_API_KEY")
    if not api_key:
        logger.error("No API key found. Please set NOVA_ACT_API_KEY in your .env file")
        return 1
    
    # Load test data
    try:
        with open("/Users/gauravbindra/Desktop/Asteroid/hard_form_data.json", "r") as f:
            form_data = json.load(f)
            contact_data = form_data.get("contact", {})
            
        if not contact_data:
            logger.error("No contact data found in hard_form_data.json")
            return 1
            
        logger.info(f"Loaded contact data successfully: {contact_data}")
            
    except Exception as e:
        logger.exception(f"Error loading form data: {e}")
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
            
            # Fill the Contact Details section with our data
            logger.info("TEST: Filling Contact Details section")
            contact_success = fill_contact_details(nova, contact_data)
            
            if contact_success:
                logger.info("Contact Details section filling PASSED")
                # Give some time to observe the Business Info section that should now be visible
                time.sleep(3)
            else:
                logger.error("Contact Details section filling FAILED")
                return 1
            
            # Allow user to observe the results before continuing
            input("Contact section test PASSED! Press Enter to continue...")
            return 0
                
    except Exception as e:
        logger.exception(f"Error during Contact Details section test: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())