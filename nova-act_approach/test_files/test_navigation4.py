#!/usr/bin/env python3
"""
Test script for hard_form_automation4.py implementation
Testing the navigate_to_tab() function
"""

import os
import logging
import sys
import time
from dotenv import load_dotenv
from nova_act import NovaAct

# Import the functions to test and utility functions
from hard_form_automation4 import navigate_to_tab
from utils_final import setup_logging

# Load environment variables from .env file
load_dotenv()

# URL for the hard form
FORM_URL = "https://asteroid.ai/form"

def run_tests():
    """
    Run tests for the hard form automation navigation function.
    Testing navigate_to_tab() functionality across different form sections.
    """
    logger = setup_logging()
    logger.info("Starting hard form navigation test")
    
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
            
            # Define the tab sections to test
            tab_sections = [
                "Contact Details",  # Should already be on this tab initially
                "Business Info",
                "Premises Details",
                "Security & Safety",
                "Coverage Options",
                "Contact Details"  # Navigate back to first tab to complete the test
            ]
            
            # Test navigation to each tab
            for tab_name in tab_sections:
                logger.info(f"Testing navigation to '{tab_name}' tab")
                
                success = navigate_to_tab(nova, tab_name)
                
                if success:
                    logger.info(f"Navigation to '{tab_name}' tab PASSED")
                    # Pause briefly to observe the navigation visually
                    time.sleep(2)
                else:
                    logger.error(f"Navigation to '{tab_name}' tab FAILED")
                    return 1
            
            # Allow user to observe the results before continuing
            input("All navigation tests PASSED! Press Enter to continue...")
            return 0
                
    except Exception as e:
        logger.exception(f"Error during navigation tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())