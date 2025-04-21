#!/usr/bin/env python3
"""
Main orchestration module for Asteroid form automation.

This module is responsible for:
1. Loading the form data
2. Initializing Nova-ACT
3. Coordinating the filling of each form section
4. Verifying final submission results
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from nova_act import NovaAct, BOOL_SCHEMA

# Import configuration
from config import HARD_FORM_URL, FORM_SECTIONS, SECTION_MAPPING

# Import section handlers
from contact_details_handler import handle_contact_details
from business_info_handler import handle_business_info
from premises_details_handler import handle_premises_details
from security_safety_handler import handle_security_safety

# Import navigation utilities
from navigation import click_button
from section_detection import section_exists

# Import utility functions
from utils_final import setup_logging, load_json_data

def verify_success_code(nova):
    """
    Verify if the form was successfully submitted and received the ASTEROID_1 code.
    
    Args:
        nova: NovaAct instance
        
    Returns:
        bool: True if success code was found, False otherwise
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Verifying form submission result")
    
    try:
        # Wait a moment for any success message to appear
        time.sleep(3)
        
        # Ask Nova-ACT to check for the success code
        query = "Look for a success code on the page. Is there a code that says 'ASTEROID_1'? Answer true or false."
        result = nova.act(query, schema=BOOL_SCHEMA)
        
        if result.matches_schema and result.parsed_response:
            logger.info("✅ SUCCESS: ASTEROID_1 code found!")
            return True
        else:
            logger.error("❌ FAILURE: ASTEROID_1 code not found")
            
            # Check for ASTEROID_0 (data mistake)
            query = "Is there a code that says 'ASTEROID_0' on the page? Answer true or false."
            result = nova.act(query, schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                logger.error("Found ASTEROID_0 code - there was a mistake in the submitted data")
            else:
                logger.error("No ASTEROID code found - form may not have submitted correctly")
                
            return False
            
    except Exception as e:
        logger.exception(f"Error verifying success code: {e}")
        return False

def automate_form(data_file_path=None):
    """
    Run the full form automation process.
    
    This function:
    1. Loads the form data
    2. Opens the form with Nova-ACT
    3. Detects which section we're currently on
    4. Processes each section with the appropriate handler
    5. Moves to the next section via the "Next" button (clicked by handlers)
    6. Verifies the success code at the end
    
    Args:
        data_file_path: Path to the JSON data file (optional)
        
    Returns:
        bool: True if form was successfully completed, False otherwise
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Starting full form automation")
    
    # Load form data
    try:
        if data_file_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            data_file_path = os.path.join(parent_dir, "hard_form_data.json")
        
        form_data = load_json_data(data_file_path)
        logger.info(f"Successfully loaded form data with sections: {list(form_data.keys())}")
    except Exception as e:
        logger.error(f"Failed to load form data: {e}")
        return False
    
    try:
        # Initialize Nova-ACT and navigate to the form
        logger.info(f"Initializing Nova-ACT for form at {HARD_FORM_URL}")
        with NovaAct(starting_page=HARD_FORM_URL) as nova:
            logger.info("Browser started successfully")
            
            # Set viewport size to reduce scrolling
            # try:
            #     nova.page.set_viewport_size({"width": 2000, "height": 5000})
            #     logger.info("Browser viewport size set to 2000x5000")
            # except Exception as e:
            #     logger.warning(f"Could not set viewport size: {e}")
            
            # Wait for form to load
            logger.info("Waiting for form to load")
            time.sleep(3)
            
            # Process form sections in sequence as they appear
            sections_processed = 0
            max_sections = len(FORM_SECTIONS)
            last_processed_index = -1  # No section processed yet
            
            while sections_processed < max_sections:
                # Detect the current section we're on, but check in a smarter order
                current_section = None
                
                # Get the expected next section based on the last processed section
                expected_index = last_processed_index + 1
                if expected_index < len(FORM_SECTIONS):
                    expected_section = FORM_SECTIONS[expected_index]
                    # Check the expected section first
                    logger.info(f"Checking for expected next section: {expected_section}")
                    if section_exists(nova, expected_section):
                        current_section = expected_section
                        last_processed_index = expected_index
                
                # If we didn't find the expected section, check all sections
                if not current_section:
                    for i, section in enumerate(FORM_SECTIONS):
                        # Skip sections we've already processed
                        if i <= last_processed_index:
                            continue
                        if section_exists(nova, section):
                            current_section = section
                            last_processed_index = i
                            break
                
                if not current_section:
                    logger.error(f"Failed to detect current section after processing {sections_processed} sections")
                    # Check if we might be at the completion screen
                    if verify_success_code(nova):
                        logger.info("Found success code, form completed successfully!")
                        return True
                    return False
                
                logger.info(f"Currently on section: {current_section} ({sections_processed + 1}/{max_sections})")
                
                # Find the JSON section(s) that correspond to this form section
                json_sections = []
                for js, fs in SECTION_MAPPING.items():
                    if fs == current_section and js in form_data:
                        json_sections.append(js)
                
                # If we have data for this section, process it
                if json_sections:
                    logger.info(f"Processing section {current_section} with data from {json_sections}")
                    
                    # Call the appropriate handler based on the current form section
                    if current_section == "Contact Details":
                        success = handle_contact_details(nova, form_data)
                    elif current_section == "Business Info":
                        success = handle_business_info(nova, form_data)
                    elif current_section == "Premises Details":
                        success = handle_premises_details(nova, form_data)
                    elif current_section == "Security & Safety":
                        success = handle_security_safety(nova, form_data)
                    elif current_section == "Coverage Options":
                        logger.info("Coverage Options handler not implemented yet, skipping")
                        success = click_button(nova, "Next")
                    else:
                        logger.warning(f"No handler implemented for section '{current_section}', skipping")
                        success = click_button(nova, "Next")
                    
                    if not success:
                        logger.error(f"Failed to process section '{current_section}'")
                        return False
                else:
                    # No data for this section, just click Next
                    logger.info(f"No data for section {current_section}, skipping")
                    success = click_button(nova, "Next")
                    if not success:
                        logger.error(f"Failed to click Next button in section '{current_section}'")
                        return False
                
                sections_processed += 1
                
                # Update index of last processed section
                for i, section in enumerate(FORM_SECTIONS):
                    if section == current_section:
                        last_processed_index = i
                        break
                
                # Check if we're at the end
                if sections_processed == max_sections:
                    logger.info("All sections processed, checking for success code")
                    return verify_success_code(nova)
                
                # Wait for next section to load
                logger.info("Waiting for next section to load...")
                time.sleep(2)
            
            # If we get here, we've processed all sections
            logger.info("All sections processed, checking for success code")
            return verify_success_code(nova)
            
    except Exception as e:
        logger.exception(f"Error during form automation: {e}")
        return False

if __name__ == "__main__":
    # Set up logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"form_automation_{timestamp}.log")
    
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file)
        ]
    )
    
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Logging to {log_file}")
    
    # Run the form automation
    success = automate_form()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)