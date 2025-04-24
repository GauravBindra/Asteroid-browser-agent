#!/usr/bin/env python3
"""
Test script for Premises Details section only.
Bypass normal navigation and directly test the premises handler.
"""

import os
import sys
import json
import logging
import time
from nova_act import NovaAct, BOOL_SCHEMA

# Import needed functions but bypass normal navigation
from premises_details_handler3 import handle_premises_details
from config import HARD_FORM_URL
from utils_final import load_json_data

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/premises_test.log")
    ]
)
logger = logging.getLogger("nova_form_automation")

def direct_to_premises():
    """Force direct navigation to Premises Details tab."""
    # Load test data 
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, "hard_form_data_actual.json")
    if not os.path.exists(data_file):
        data_file = os.path.join(script_dir, "hard_form_data.json")
        
    logger.info(f"Loading data from: {data_file}")
    data = load_json_data(data_file)
    
    with NovaAct(starting_page=HARD_FORM_URL) as nova:
        logger.info("Browser launched successfully")
        
        # Wait for form to load
        logger.info("Waiting for form to load")
        time.sleep(3)
        
        # Force direct click on Premises tab with explicit commands
        logger.info("Force-clicking Premises Details tab")
        try:
            # Extra forceful approach
            click_command = (
                "Look at the navigation tabs at the top of the form. "
                "Find the tab labeled 'Premises Details' and click directly on it. "
                "Make sure to click on the tab itself, not any other element."
            )
            nova.act(click_command, max_steps=4)
            time.sleep(2)
            
            # Verify we're on Premises Details tab
            check = nova.act(
                "Are we currently on the Premises Details tab of the form? Look at the active tab. Answer true or false.",
                schema=BOOL_SCHEMA
            )
            
            if check.matches_schema and check.parsed_response:
                logger.info("✅ Successfully reached Premises Details tab")
            else:
                # First fallback - try sequential navigation
                logger.warning("Direct tab click failed, trying sequential navigation")
                # Click through Contact Details
                nova.act("Find and click the 'Next' button", max_steps=3)
                time.sleep(1)
                # Click through Business Info
                nova.act("Find and click the 'Next' button", max_steps=3)
                time.sleep(1)
            
            # Double check we're on Premises Details
            check_again = nova.act(
                "Confirm we are on the Premises Details section of the form. Answer true or false.",
                schema=BOOL_SCHEMA
            )
            
            if not (check_again.matches_schema and check_again.parsed_response):
                logger.error("❌ Failed to reach Premises Details section")
                return False
                
            # Now test the Premises Details handler
            logger.info("Running Premises Details handler")
            result = handle_premises_details(nova, data)
            
            if result:
                logger.info("✅ Premises Details section processed successfully")
            else:
                logger.error("❌ Premises Details section processed with errors")
                
            # Wait to observe the results
            logger.info("Waiting to observe results...")
            time.sleep(5)
            
            return result
            
        except Exception as e:
            logger.exception(f"Error during test: {e}")
            return False

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Run the test
    result = direct_to_premises()
    
    # Exit with appropriate code
    sys.exit(0 if result else 1)