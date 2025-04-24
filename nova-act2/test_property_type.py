#!/usr/bin/env python3
"""
Test script for verifying the "Property Type" field specifically.
This tests our improved verification approach on the previously problematic field.
"""

import logging
import sys
import time
from nova_act import NovaAct, BOOL_SCHEMA
from config import HARD_FORM_URL
from utils_final import load_json_data
from navigation import navigate_to_section
from field_detection import get_form_label, find_field
from fill_fields import select_dropdown_option
from verify3 import verify_field, verify_field_filled

# Initialize logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("nova_form_automation")

def test_property_type_field():
    """
    Test the Property Type field specifically to verify our improved approach works.
    """
    logger.info("Starting Property Type field test")
    
    try:
        # Load the form data
        import os
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
            
            # Now fill the field
            logger.info(f"Filling the Property Type field with '{property_type_value}'")
            fill_success = select_dropdown_option(nova, label, property_type_value)
            if not fill_success:
                logger.error("Failed to fill the Property Type field")
                return False
                
            # First try verification with regular verify_field
            logger.info("Attempting standard verification")
            standard_verification = verify_field(nova, label, property_type_value, "dropdown")
            
            if standard_verification:
                logger.info("✅ Standard verification successful")
            else:
                logger.warning("❌ Standard verification failed")
                
            # Now try with our specialized verification
            logger.info("Attempting specialized verification")
            specialized_verification = verify_field_filled(
                nova, 
                label, 
                property_type_value, 
                "dropdown", 
                section_name
            )
            
            if specialized_verification:
                logger.info("✅ Specialized verification successful")
            else:
                logger.error("❌ Specialized verification also failed")
            
            # Return overall result
            return standard_verification or specialized_verification
            
    except Exception as e:
        logger.exception(f"Error in property type test: {e}")
        return False

if __name__ == "__main__":
    success = test_property_type_field()
    
    if success:
        logger.info("✅ Property Type field test completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Property Type field test failed")
        sys.exit(1)