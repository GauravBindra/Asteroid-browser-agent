#!/usr/bin/env python3
"""
Test script for field detection functionality.

This script tests the field_exists function against the hard form
to verify that it correctly identifies fields in different tabs.
"""

import os
import sys
import logging
import time
from nova_act import NovaAct

# Add the parent directory to the path to find the field_detection module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the field detection function
from field_detection import field_exists
import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("nova_form_automation")

def test_field_detection():
    """Test the field_exists function on various form fields."""
    logger.info("Starting field detection test")
    
    # Fields to test in each tab
    test_cases = [
        # Tab name, field label, expected result
        ("Contact Details", "Title", True),  # Should exist
        ("Contact Details", "First Name", True),  # Should exist
        ("Contact Details", "Non-existent Field", False),  # Should not exist
        ("Business Info", "Business Name", True),  # Should exist
        ("Business Info", "Contact Person", False),  # Should not exist
    ]
    
    try:
        # Initialize Nova-ACT
        with NovaAct(starting_page=config.HARD_FORM_URL) as nova:
            logger.info("Waiting for form to load")
            time.sleep(3)
            
            # Initial check on Contact Details tab (default tab)
            current_tab = "Contact Details"
            
            for tab, field_label, expected in test_cases:
                # Navigate to tab if needed
                if tab != current_tab:
                    logger.info(f"Navigating to {tab} tab")
                    nova.act(f"Click on the tab labeled '{tab}' at the top of the form")
                    time.sleep(2)
                    current_tab = tab
                
                # Test field detection
                logger.info(f"Testing field '{field_label}' in {tab} tab")
                result = field_exists(nova, field_label, current_tab)
                
                # Check if result matches expectation
                if result == expected:
                    logger.info(f"✅ PASS: Field '{field_label}' detection returned {result} as expected")
                else:
                    logger.error(f"❌ FAIL: Field '{field_label}' detection returned {result}, expected {expected}")
            
            logger.info("Field detection tests completed")
            
    except Exception as e:
        logger.exception(f"Error during field detection test: {e}")

if __name__ == "__main__":
    test_field_detection()
    logger.info("Test script execution completed")