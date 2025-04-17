#!/usr/bin/env python3
"""
Test script for optimized hard_form_automation3.py functions
"""

import os
import logging
import sys
import time
from dotenv import load_dotenv
from nova_act import NovaAct

# Import the functions to test and utility functions
from hard_form_automation3 import select_dropdown_option, fill_date_field, fill_contact_details
from utils_final import setup_logging, load_json_data

# Load environment variables from .env file
load_dotenv()

# URL for the hard form
FORM_URL = "https://asteroid.ai/form"

def run_tests():
    """
    Run tests for optimized hard form automation functions.
    """
    logger = setup_logging()
    logger.info("Starting optimized hard form automation function tests")
    
    # Get API key from environment
    api_key = os.environ.get("NOVA_ACT_API_KEY")
    if not api_key:
        logger.error("No API key found. Please set NOVA_ACT_API_KEY in your .env file")
        return 1
    
    # Load test data
    try:
        form_data = load_json_data("/Users/gauravbindra/Desktop/Asteroid/hard_form_data.json")
        if not form_data or "contact" not in form_data:
            logger.error("Invalid or missing test data")
            return 1
        contact_data = form_data["contact"]
    except Exception as e:
        logger.exception(f"Error loading test data: {e}")
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
            
            # Initial page exploration
            logger.info("Scrolling to see the form")
            nova.act("Scroll down until you can see the Contact Details section of the form")
            time.sleep(1)
            
            # Test Option 1: Individual Field Tests
            if False:  # Set to True to run individual field tests
                # ------------------------------------
                # Test 1: Optimized Dropdown Selection
                # ------------------------------------
                logger.info("TEST 1: Optimized Dropdown Selection")
                dropdown_success = select_dropdown_option(nova, "Title", contact_data["title"])
                
                if dropdown_success:
                    logger.info("Optimized dropdown selection test PASSED")
                else:
                    logger.error("Optimized dropdown selection test FAILED")
                    return 1
                
                # ------------------------------------
                # Test 2: Optimized Date Field
                # ------------------------------------
                logger.info("TEST 2: Optimized Date Field")
                date_success = fill_date_field(nova, "Date of Birth", contact_data["dateOfBirth"])
                
                if date_success:
                    logger.info("Optimized date field test PASSED")
                else:
                    logger.error("Optimized date field test FAILED")
                    return 1
            
            # Test Option 2: Complete Section Test
            else:
                # ------------------------------------
                # Test 3: Complete Contact Section
                # ------------------------------------
                logger.info("TEST 3: Complete Contact Section")
                section_success = fill_contact_details(nova, contact_data)
                
                if section_success:
                    logger.info("Complete contact section test PASSED")
                else:
                    logger.error("Complete contact section test FAILED")
                    return 1
            
            # Allow user to observe the results before continuing
            input("Tests completed! Press Enter to continue...")
            return 0
                
    except Exception as e:
        logger.exception(f"Error during tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())