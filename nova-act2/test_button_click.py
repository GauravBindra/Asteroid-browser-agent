#!/usr/bin/env python3
"""
Simple test script that tests the navigation functions on the hard form.
"""

import os
import sys
import logging
import time
from datetime import datetime
from nova_act import NovaAct

# Import the config and utility functions
from config import HARD_FORM_URL
from navigation import click_button

# Set up logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# Create logs in a subdirectory
script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"button_click_test_{timestamp}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("nova_form_automation")
logger.info(f"Logging to {log_file}")

def test_button_click():
    """Test clicking the 'Next' button on the hard form."""
    logger.info("Starting button click test for 'Next' button")
    
    try:
        # Initialize Nova-ACT and navigate to the hard form
        with NovaAct(starting_page=HARD_FORM_URL) as nova:
            logger.info("Browser started successfully")
            
            # Wait for the form to load
            logger.info("Waiting for form to load")
            time.sleep(3)
            
            # Try to find and click the 'Next' button
            logger.info("Attempting to click the 'Next' button")
            result = click_button(nova, "Next")
            
            # Check the result
            if result:
                logger.info("✅ SUCCESS: Successfully clicked the 'Next' button")
            else:
                logger.error("❌ FAILURE: Failed to click the 'Next' button")
            
            # Wait to see the result (next page should load)
            logger.info("Waiting to observe the result")
            time.sleep(5)
            
            # Try to determine if we advanced to the next page
            # This is a simple check that could be improved
            # nova.act("What page or section are we on now?")
            
            logger.info("Test completed")
            return result
            
    except Exception as e:
        logger.exception(f"Error during button click test: {e}")
        return False

if __name__ == "__main__":
    success = test_button_click()
    sys.exit(0 if success else 1)
