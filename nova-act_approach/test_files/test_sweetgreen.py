#!/usr/bin/env python3
"""
Test script for the SweetGreen-style approach to filling the Contact Details section.
This demonstrates using a single, comprehensive act() call rather than modular functions.
"""

import os
import logging
import sys
import time
import json
from dotenv import load_dotenv
from nova_act import NovaAct

# Import the SweetGreen-style function
from sweetgreen_approach import fill_contact_details_sweetgreen_style
from utils_final import setup_logging

# Load environment variables
load_dotenv()

# URL for the hard form
FORM_URL = "https://asteroid.ai/form"

def run_test():
    """
    Run test for the SweetGreen-style approach to form filling.
    Demonstrates a simpler, more direct approach with a single, comprehensive prompt.
    """
    logger = setup_logging()
    logger.info("Starting Contact Details test with SweetGreen approach")
    
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
            
            # Fill the Contact Details section using the SweetGreen approach
            logger.info("TEST: Filling Contact Details with SweetGreen approach")
            start_time = time.time()
            contact_success = fill_contact_details_sweetgreen_style(nova, contact_data)
            end_time = time.time()
            
            if contact_success:
                logger.info(f"Contact Details section filling PASSED in {end_time - start_time:.2f} seconds")
                # Give some time to observe the Business Info section that should now be visible
                time.sleep(3)
            else:
                logger.error("Contact Details section filling FAILED")
                return 1
            
            # Allow user to observe the results before continuing
            input("SweetGreen approach test complete. Press Enter to continue...")
            return 0
                
    except Exception as e:
        logger.exception(f"Error during Contact Details section test: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_test())
