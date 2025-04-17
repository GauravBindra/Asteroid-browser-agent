#!/usr/bin/env python3
"""
Test script for the business info section with semantic field detection.

This test script focuses on testing the enhanced fill_business_info() function
in the hard_form_automation12.py module which uses semantic field detection
to handle fields that may not exist in the actual form.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime

# Nova-ACT imports
from nova_act import NovaAct

# Import functions from the hard form automation module with semantic detection
from hard_form_automation12 import fill_business_info, navigate_to_tab

# Import utilities for logging
from utils_final import setup_logging

# Set up logging
logger = setup_logging()

def main():
    """Main function to test the business info section handler with semantic detection."""
    logger.info("Starting business info section test with semantic field detection")
    
    # Load the hard form test data with more robust path handling
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        data_path = os.path.join(project_root, "hard_form_data.json")
        logger.info(f"Loading data from {data_path}")
        
        with open(data_path, "r") as f:
            form_data = json.load(f)
        logger.info("Successfully loaded form test data")
    except Exception as e:
        logger.error(f"Failed to load form test data: {e}")
        # Try relative path as fallback
        try:
            logger.info("Trying relative path as fallback")
            with open("hard_form_data.json", "r") as f:
                form_data = json.load(f)
            logger.info("Successfully loaded form test data via relative path")
        except Exception as fallback_error:
            logger.error(f"Failed to load form test data via fallback: {fallback_error}")
            return
    
    # Extract business data
    business_data = form_data.get("business", {})
    
    # Initialize Nova-ACT
    url = "https://asteroid.ai/form"
    logger.info(f"Initializing Nova-ACT and navigating to {url}")
    
    try:
        with NovaAct(starting_page=url) as nova:
            logger.info("Waiting for form to load")
            time.sleep(5)  # Extended wait for form to fully load
            
            # Skip contact details and go straight to business info
            logger.info("Navigating directly to Business Info tab")
            navigate_to_tab(nova, "Business Info")
            
            # Test the business info section handler
            logger.info("Testing fill_business_info function with semantic field detection")
            result = fill_business_info(nova, business_data, force_navigation=False)
            
            if result:
                logger.info("Successfully completed business info section test")
            else:
                logger.error("Failed to complete business info section test")
                
    except Exception as e:
        logger.exception(f"Error during business info test: {e}")

if __name__ == "__main__":
    main()
    logger.info("Business info section test with semantic detection completed")
    print("Detailed logs available through console output redirection")