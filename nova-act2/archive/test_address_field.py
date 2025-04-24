#!/usr/bin/env python3
"""
Test script for the Address field filling and verification.

This script focuses on testing just the business address field filling and verification
to debug and improve the address field handling.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from nova_act import NovaAct, BOOL_SCHEMA

# Import the necessary modules
from config import HARD_FORM_URL
from fill_fields import fill_text_field
from verify3 import verify_address_fields
from field_detection import find_field
from navigation import click_button, navigate_to_section

# Set up logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"address_field_test_{timestamp}.log")

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

def load_test_data():
    """Load the form data for testing."""
    try:
        # Find the hard_form_data.json file
        data_file = os.path.join(script_dir, "hard_form_data_actual.json")
        
        if not os.path.exists(data_file):
            # Try parent directory
            parent_dir = os.path.dirname(script_dir)
            data_file = os.path.join(parent_dir, "hard_form_data_actual.json")
            
            if not os.path.exists(data_file):
                # Try other variations
                data_file = os.path.join(script_dir, "hard_form_data.json")
                if not os.path.exists(data_file):
                    data_file = os.path.join(parent_dir, "hard_form_data.json")
        
        with open(data_file, "r") as f:
            data = json.load(f)
            
        logger.info(f"Successfully loaded form data with sections: {list(data.keys())}")
        return data
        
    except Exception as e:
        logger.error(f"Failed to load test data: {e}")
        return None

def fill_business_address(nova, address_data):
    """Fill the business address fields."""
    logger.info("Filling business address fields")
    
    # Field mappings for address components
    field_mappings = {
        "addressLine1": "Address Line 1",
        "addressLine2": "Address Line 2",
        "addressLine3": "Address Line 3",
        "city": "City"
    }
    
    success = True
    # Fill each address field
    for key, form_label in field_mappings.items():
        if key not in address_data or not address_data[key]:
            continue
            
        value = address_data[key]
        logger.info(f"Filling address field '{form_label}' with value '{value}'")
        
        field_success = fill_text_field(nova, form_label, str(value))
        
        if not field_success:
            logger.warning(f"Failed to fill address field '{form_label}'")
            success = False
    
    return success

def test_address_field_filling_and_verification():
    """Test the address field filling and verification."""
    logger.info("Starting Address field filling and verification test")
    
    # Load test data
    form_data = load_test_data()
    if not form_data:
        logger.error("Cannot proceed with testing - failed to load test data")
        return False
    
    # Extract business address data
    if "business" not in form_data or "address" not in form_data["business"]:
        logger.error("Business address data not found in form data")
        return False
    
    address_data = form_data["business"]["address"]
    logger.info(f"Business address data: {json.dumps(address_data, indent=2)}")
    
    try:
        # Initialize NovaAct and navigate to the form
        logger.info(f"Initializing Nova-ACT for form at {HARD_FORM_URL}")
        with NovaAct(starting_page=HARD_FORM_URL) as nova:
            logger.info("Browser started successfully")
            
            # Wait for the form to load
            logger.info("Waiting for form to load")
            time.sleep(3)
            
            # Navigate to Business Info section
            logger.info("Navigating to Business Info section")
            nav_success = navigate_to_section(nova, "Business Info")
            if not nav_success:
                logger.error("Failed to navigate to Business Info section")
                return False
            
            logger.info("Successfully navigated to Business Info section")
            
            # Fill the address fields
            logger.info("Filling business address fields")
            fill_success = fill_business_address(nova, address_data)
            
            if not fill_success:
                logger.warning("Some address fields could not be filled")
            
            # Wait for fields to settle
            time.sleep(2)
            
            # Verify the address fields
            logger.info("Verifying business address fields")
            failed_fields = verify_address_fields(nova, "Business Info", address_data)
            
            if failed_fields:
                logger.warning(f"Verification failed for {len(failed_fields)} address fields")
                for field in failed_fields:
                    logger.warning(f"Field: {field['label']} (expected: {field['expected_value']})")
                    if 'reason' in field:
                        logger.warning(f"Reason: {field['reason']}")
            else:
                logger.info("All address fields verified successfully")
            
            # Wait to observe the results
            logger.info("Waiting 5 seconds to observe the results...")
            time.sleep(5)
            
            return len(failed_fields) == 0
            
    except Exception as e:
        logger.exception(f"Error during address field test: {e}")
        return False

if __name__ == "__main__":
    success = test_address_field_filling_and_verification()
    sys.exit(0 if success else 1)