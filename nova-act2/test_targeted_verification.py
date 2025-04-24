#!/usr/bin/env python3
"""
Test the targeted verification approach for form fields that failed during initial processing.

This script specifically tests the functionality where only fields that failed 
during the initial fill or verification process are re-verified using the specialized
verify_field_filled function with multiple query variants.
"""

import logging
import os
import sys
import time
from typing import List, Dict, Any, Tuple

from nova_act import NovaAct, BOOL_SCHEMA
from config import HARD_FORM_URL
from utils_final import load_json_data
from navigation import navigate_to_section
from field_detection import find_field, get_form_label
from fill_fields import select_dropdown_option, fill_text_field
from verify3 import verify_field, verify_field_filled, verify_specific_fields

# Initialize logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("nova_form_automation")

def test_targeted_verification():
    """
    Test scenario: "Property Type" dropdown field fails initial verification but passes
    specialized verification with multiple query variants.
    """
    logger.info("Starting targeted verification test")
    
    try:
        # Load the form data
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(script_dir, "hard_form_data_actual.json")
        
        # Check for file existence
        if not os.path.exists(data_file):
            parent_dir = os.path.dirname(script_dir)
            data_file = os.path.join(parent_dir, "hard_form_data_actual.json")
            
            if not os.path.exists(data_file):
                data_file = os.path.join(script_dir, "hard_form_data.json")
                
                if not os.path.exists(data_file):
                    data_file = os.path.join(parent_dir, "hard_form_data.json")
        
        logger.info(f"Loading data from: {data_file}")
        form_data = load_json_data(data_file)
        
        # Extract the property type value from the data
        if "premises" not in form_data or "identity" not in form_data["premises"]:
            logger.error("Premises identity data not found in form data")
            return False
        
        property_type_value = form_data["premises"]["identity"].get("type")
        if not property_type_value:
            logger.error("Property type value not found in form data")
            return False
            
        logger.info(f"Testing with property type value: '{property_type_value}'")
        
        # Start Nova-ACT and navigate to the form
        with NovaAct(starting_page=HARD_FORM_URL) as nova:
            logger.info("Navigating to Premises Details section")
            
            # Wait for form to load
            time.sleep(3)
            
            # Navigate to the Premises Details section
            if not navigate_to_section(nova, "Premises Details"):
                logger.error("Failed to navigate to Premises Details section")
                return False
                
            # Allow time for the section to load
            time.sleep(2)
            
            # Get the proper form label for Property Type
            section_name = "Premises Details"
            label = get_form_label("type", section_name)
            logger.info(f"Using label '{label}' for property type field")
            
            # First, find the field
            logger.info(f"Finding the Property Type field")
            if not find_field(nova, label, section_name, "dropdown"):
                logger.error("Could not find the Property Type field")
                return False
            
            # Part 1: Fill the field
            logger.info(f"Filling the Property Type field with '{property_type_value}'")
            fill_success = select_dropdown_option(nova, label, property_type_value)
            if not fill_success:
                logger.error("Failed to fill the Property Type field")
                return False
                
            # Part 2: Simulate standard verification failure
            logger.info("Skipping standard verification to simulate failure")
            logger.warning("❌ Simulated standard verification failure for test purposes")
            
            # Create a failed field record
            failed_fields = [{
                "section": section_name,
                "json_section": "premises",
                "subsection": "identity",
                "key": "type",
                "label": label,
                "expected_value": property_type_value,
                "field_type": "dropdown"
            }]
            
            # Part 3: Perform targeted verification on the failed field
            logger.info(f"Performing targeted verification on {len(failed_fields)} failed fields")
            still_failed = verify_specific_fields(nova, failed_fields)
            
            if still_failed:
                logger.error(f"❌ Targeted verification also failed for {len(still_failed)} fields")
                logger.error("Test failed: Specialized verification did not succeed")
                return False
            else:
                logger.info("✅ All fields passed targeted verification with specialized approach")
                logger.info("Test passed: Specialized verification succeeded where standard verification failed")
                return True
            
    except Exception as e:
        logger.exception(f"Error in targeted verification test: {e}")
        return False

if __name__ == "__main__":
    success = test_targeted_verification()
    
    if success:
        logger.info("✅ Targeted verification test completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Targeted verification test failed")
        sys.exit(1)