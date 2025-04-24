#!/usr/bin/env python3
"""
Test the fallback navigation strategy for the Business Info section.

This script specifically tests the scenario where:
1. A field fails to verify even with our specialized approach
2. The Next button doesn't work
3. The system falls back to navigating by clicking on the next section tab
"""

import logging
import os
import sys
import time
from typing import List, Dict, Any, Tuple

from nova_act import NovaAct, BOOL_SCHEMA
from config import HARD_FORM_URL, FORM_SECTIONS
from utils_final import load_json_data
from navigation import navigate_to_section, click_button
from field_detection import get_form_label
from fill_fields import fill_text_field
from verify3 import verify_specific_fields
from error_handler import navigate_to_next_section

# Setup logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("next_section_fallback_logs.md")
    ]
)
logger = logging.getLogger("nova_form_automation")

class MockClickFailure(Exception):
    """Exception to simulate Next button failure"""
    pass

def test_fallback_navigation_business_info():
    """
    Test the fallback navigation strategy for the Business Info section when:
    1. Business Type field fails verification
    2. Next button doesn't work
    3. Fallback navigation to the next section tab is required
    """
    logger.info("Starting fallback navigation test for Business Info section")
    
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
        
        # Extract the business name value from the data
        if "business" not in form_data:
            logger.error("Business data not found in form data")
            return False
        
        # Get business name value or use a default
        business_name_value = form_data["business"].get("name", "Test Business")
        
        # Start Nova-ACT and navigate to the form
        with NovaAct(starting_page=HARD_FORM_URL) as nova:
            logger.info("Navigating to Business Info section")
            
            # Wait for form to load
            time.sleep(3)
            
            # Navigate to the Business Info section
            if not navigate_to_section(nova, "Business Info"):
                logger.error("Failed to navigate to Business Info section")
                return False
                
            # Allow time for the section to load
            time.sleep(2)
            
            # Verify that we're on the Business Info section
            query = "Is this the Business Info section of the form? Answer true or false."
            result = nova.act(query, schema=BOOL_SCHEMA)
            
            if not result.matches_schema or not result.parsed_response:
                logger.error("Failed to navigate to Business Info section")
                return False
                
            # Get current section index in FORM_SECTIONS
            current_section_index = FORM_SECTIONS.index("Business Info")
            next_section = FORM_SECTIONS[current_section_index + 1]
            logger.info(f"Current section: Business Info, Next section should be: {next_section}")
            
            # Fill in Business Name field to ensure we have some data filled
            logger.info("Filling in Business Name field")
            business_name_label = get_form_label("name", "Business Info")
            fill_text_field(nova, business_name_label, business_name_value)
            
            # STEP 1: Simulate a field that fails verification - Business Type
            logger.info("Simulating a field that fails verification")
            
            # Create a failed field record with incorrect expected value
            failed_fields = [{
                "section": "Business Info",
                "json_section": "business",
                "key": "type",
                "label": "Business Type",
                "expected_value": "Incorrect Business Type",  # Using a value that won't match
                "field_type": "dropdown"
            }]
            
            # Attempt specialized verification (this should fail because we're using a mismatched value)
            logger.info("Attempting specialized verification with incorrect values (should fail)")
            still_failed = verify_specific_fields(nova, failed_fields)
            
            if not still_failed:
                logger.error("❌ Test setup error: Specialized verification succeeded when it should have failed")
                return False
                
            logger.info("✅ Verification failed as expected for test scenario")
            
            # STEP 2: Test if we're still on Business Info section (should be)
            logger.info("Verifying we're still on Business Info section")
            still_on_business_info = nova.act(
                "Is this the Business Info section of the form? Answer true or false.",
                schema=BOOL_SCHEMA
            )
            
            if not still_on_business_info.matches_schema or not still_on_business_info.parsed_response:
                logger.error("❌ Test error: No longer on Business Info section after verification")
                return False
                
            logger.info("✅ Still on Business Info section after verification")
            
            # STEP 3: First try clicking the Next button (this will likely work in the test)
            logger.info("Attempting to click the Next button first")
            next_button_clicked = click_button(nova, "Next")
            
            # If Next button click succeeded, go back to Business Info to test the fallback
            if next_button_clicked:
                logger.info("Next button click succeeded, returning to Business Info to test fallback")
                time.sleep(1)
                navigate_to_section(nova, "Business Info")
                time.sleep(2)
                
                # Verify we're back on the Business Info section
                back_on_business = nova.act(
                    "Is this the Business Info section of the form? Answer true or false.",
                    schema=BOOL_SCHEMA
                )
                
                if not back_on_business.matches_schema or not back_on_business.parsed_response:
                    logger.error("Failed to navigate back to Business Info section")
                    return False
                
                logger.info("Successfully returned to Business Info section for fallback test")
            else:
                logger.info("Next button click failed, will try fallback navigation")
            
            # Now try the fallback navigation method (which is what should happen when Next fails)
            logger.info("Testing fallback navigation mechanism")
            fallback_success = navigate_to_next_section(nova, "Premises Details")
            
            if not fallback_success:
                logger.error("❌ Fallback navigation failed")
                return False
                
            # Verify we are now on the next section - wait for it to load
            time.sleep(2)
            
            # Check if we're on the expected next section
            logger.info(f"Verifying we're now on the {next_section} section")
            on_next_section = nova.act(
                f"Is this the {next_section} section of the form? Answer true or false.",
                schema=BOOL_SCHEMA
            )
            
            if on_next_section.matches_schema and on_next_section.parsed_response:
                logger.info(f"✅ Successfully navigated to {next_section} using fallback navigation")
                return True
            else:
                logger.error(f"❌ Failed to navigate to {next_section} using fallback navigation")
                return False
            
    except Exception as e:
        logger.exception(f"Error in Business Info fallback navigation test: {e}")
        return False

if __name__ == "__main__":
    success = test_fallback_navigation_business_info()
    
    if success:
        logger.info("✅ Business Info fallback navigation test completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Business Info fallback navigation test failed")
        sys.exit(1)