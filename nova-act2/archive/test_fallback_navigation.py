#!/usr/bin/env python3
"""
Test the fallback navigation strategy when a field fails to verify and the Next button doesn't work.

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
from field_detection import find_field, get_form_label
from fill_fields import select_dropdown_option
from verify3 import verify_field, verify_field_filled, verify_specific_fields
from error_handler import navigate_to_next_section

# Initialize logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("nova_form_automation")

def test_fallback_navigation():
    """
    Test the fallback navigation strategy when a field fails verification and Next button doesn't work.
    
    This simulates:
    1. A problematic field that fails both regular and specialized verification
    2. A Next button that doesn't work
    3. The fallback navigation strategy of clicking the next section tab
    """
    logger.info("Starting fallback navigation test")
    
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
            
            # Get current section index in FORM_SECTIONS
            current_section_index = FORM_SECTIONS.index("Premises Details")
            next_section = FORM_SECTIONS[current_section_index + 1]
            logger.info(f"Current section: Premises Details, Next section should be: {next_section}")
            
            # STEP 1: Simulate a field that fails to verify
            logger.info("Simulating a field that fails verification")
            
            # Create a failed field record
            failed_fields = [{
                "section": "Premises Details",
                "json_section": "premises",
                "subsection": "identity",
                "key": "type",
                "label": "Property Type",
                "expected_value": "Shop",  # Using a value that might not match what's actually selected
                "field_type": "dropdown"
            }]
            
            # Attempt specialized verification (this should fail because we're using a mismatched value)
            logger.info("Attempting specialized verification with incorrect values (should fail)")
            still_failed = verify_specific_fields(nova, failed_fields)
            
            if not still_failed:
                logger.error("❌ Test setup error: Specialized verification succeeded when it should have failed")
                return False
                
            logger.info("✅ Verification failed as expected for test scenario")
            
            # STEP 2: Simulate Next button not working
            logger.info("Simulating Next button not working")
            
            # Mock a failing click_button function by monkeypatching
            original_click_button = nova.act
            
            def mock_act_for_next_button(query, *args, **kwargs):
                if "click" in query.lower() and "next" in query.lower():
                    logger.info("Mocking failed Next button click")
                    return None  # Simulate failure
                return original_click_button(query, *args, **kwargs)
            
            # Apply the mock
            nova.act = mock_act_for_next_button
            
            # Try to click Next button (should fail due to our mock)
            logger.info("Attempting to click Next button (should fail)")
            next_success = click_button(nova, "Next")
            
            if next_success:
                logger.error("❌ Test setup error: Next button click succeeded when it should have failed")
                # Restore original function
                nova.act = original_click_button
                return False
                
            logger.info("✅ Next button click failed as expected for test scenario")
            
            # STEP 3: Test the fallback navigation strategy
            logger.info("Testing fallback navigation strategy")
            
            # Restore original function before testing navigation
            nova.act = original_click_button
            
            # Try the fallback navigation
            fallback_success = navigate_to_next_section(nova, "Premises Details")
            
            if not fallback_success:
                logger.error("❌ Fallback navigation failed")
                return False
                
            # Verify we are now on the next section
            nova.act("Wait for the page to load completely", max_steps=3)
            
            # Check if we're on the expected next section
            check_query = f"Are we on the {next_section} section? Answer true or false."
            result = nova.act(check_query, schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                logger.info(f"✅ Successfully navigated to {next_section} using fallback navigation")
                return True
            else:
                logger.error(f"❌ Failed to navigate to {next_section} using fallback navigation")
                return False
            
    except Exception as e:
        logger.exception(f"Error in fallback navigation test: {e}")
        return False

if __name__ == "__main__":
    success = test_fallback_navigation()
    
    if success:
        logger.info("✅ Fallback navigation test completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Fallback navigation test failed")
        sys.exit(1)