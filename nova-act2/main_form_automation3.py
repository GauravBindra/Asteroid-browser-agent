#!/usr/bin/env python3
"""
Enhanced main orchestration module for Asteroid form automation with comprehensive verification.

This module is responsible for:
1. Loading the form data
2. Initializing Nova-ACT
3. Coordinating the filling of each form section using improved handlers
4. Verifying fields and sections with retry capabilities
5. Handling navigation failures with fallback mechanisms
6. Verifying final submission results
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

# Import improved section handlers with comprehensive verification
from contact_details_handler3 import handle_contact_details
from business_info_handler3 import handle_business_info
from premises_details_handler3 import handle_premises_details
from security_safety_handler3 import handle_security_safety
from submission3 import handle_coverage_options, handle_final_submission, verify_submission_result

# Import navigation utilities
from navigation import click_button, navigate_to_section
from section_detection import section_exists

# Import utility functions
from utils_final import load_json_data
from error_handler import navigate_to_next_section

def automate_form(data_file_path=None, form_url=None):
    """
    Run the full form automation process with comprehensive verification and error handling.
    
    This function:
    1. Loads the form data
    2. Opens the form with Nova-ACT
    3. Detects which section we're currently on
    4. Processes each section with the appropriate enhanced handler
    5. Navigates between sections with fallback mechanisms if needed
    6. Verifies the success code at the end
    
    Args:
        data_file_path: Path to the JSON data file (optional)
        form_url: URL of the form to automate (optional)
        
    Returns:
        bool: True if form was successfully completed, False otherwise
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Starting enhanced form automation with comprehensive verification")
    
    # Load form data
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        
        # If data_file_path is provided, clean it up (remove any leading/trailing whitespace)
        if data_file_path is not None:
            data_file_path = data_file_path.strip()
            logger.info(f"Using provided data file path: {data_file_path}")
        else:
            # Default path is now hard_form_data_actual.json
            data_file_path = os.path.join(script_dir, "hard_form_data_actual.json")
            logger.info(f"No path provided, using default: {data_file_path}")
        
        # Check if file exists at the provided/default path
        if not os.path.exists(data_file_path):
            logger.warning(f"File not found at {data_file_path}, checking alternative locations")
            
            # Try different potential locations in a specific order - prioritize actual data files
            potential_paths = [
                os.path.join(script_dir, "hard_form_data_actual.json"),  # First try actual in current dir
                os.path.join(parent_dir, "hard_form_data_actual.json"),  # Then actual in parent dir
                os.path.join(parent_dir, "data", "hard_form_data_actual.json"),  # Try in data subdirectory
                os.path.join(script_dir, "hard_form_data.json"),         # Then standard in current dir
                os.path.join(parent_dir, "hard_form_data.json")          # Finally standard in parent dir
            ]
            
            for potential_path in potential_paths:
                if os.path.exists(potential_path):
                    data_file_path = potential_path
                    logger.info(f"Found data file at: {data_file_path}")
                    break
            else:
                # If no file is found after trying all locations
                raise FileNotFoundError(f"Could not find form data file in any expected location")
                
        form_data = load_json_data(data_file_path)
        logger.info(f"Successfully loaded form data from {data_file_path}")
        logger.info(f"Form data contains sections: {list(form_data.keys())}")
    except Exception as e:
        logger.error(f"Failed to load form data: {e}")
        return False
    
    # Use the provided form URL or default to HARD_FORM_URL
    if form_url is None:
        form_url = HARD_FORM_URL
    
    try:
        # Initialize Nova-ACT and navigate to the form
        logger.info(f"Initializing Nova-ACT for form at {form_url}")
        with NovaAct(starting_page=form_url) as nova:
            logger.info("Browser started successfully")
            
            # Use default viewport size
            logger.info("Using default viewport size")
                
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
                    if verify_submission_result(nova):
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
                    
                    # Call the appropriate enhanced handler based on the current form section
                    # Each handler now returns a tuple (success, failed_fields)
                    failed_fields = []
                    
                    if current_section == "Contact Details":
                        success, section_failed_fields = handle_contact_details(nova, form_data)
                        failed_fields.extend(section_failed_fields)
                    elif current_section == "Business Info":
                        success, section_failed_fields = handle_business_info(nova, form_data)
                        failed_fields.extend(section_failed_fields)
                    elif current_section == "Premises Details":
                        success, section_failed_fields = handle_premises_details(nova, form_data)
                        failed_fields.extend(section_failed_fields)
                    elif current_section == "Security & Safety":
                        success, section_failed_fields = handle_security_safety(nova, form_data)
                        failed_fields.extend(section_failed_fields)
                    elif current_section == "Coverage Options":
                        success = handle_coverage_options(nova, form_data)
                    else:
                        logger.warning(f"No handler implemented for section '{current_section}', skipping")
                        success = click_button(nova, "Next")
                        
                    # Log any failed fields
                    if failed_fields:
                        logger.warning(f"Section '{current_section}' had {len(failed_fields)} fields that failed verification")
                    
                    if not success:
                        logger.error(f"Failed to process section '{current_section}'")
                        
                        # Try fallback navigation if regular navigation failed
                        logger.info(f"Attempting fallback navigation from section '{current_section}'")
                        fallback_success = navigate_to_next_section(nova, current_section)
                        
                        if not fallback_success:
                            logger.error(f"Fallback navigation also failed for section '{current_section}'")
                            return False
                        
                        logger.info(f"Fallback navigation successful for section '{current_section}'")
                else:
                    # No data for this section, just click Next
                    logger.info(f"No data for section {current_section}, skipping")
                    success = click_button(nova, "Next")
                    if not success:
                        logger.error(f"Failed to click Next button in section '{current_section}'")
                        
                        # Try fallback navigation if clicking Next failed
                        fallback_success = navigate_to_next_section(nova, current_section)
                        
                        if not fallback_success:
                            logger.error(f"Fallback navigation also failed for section '{current_section}'")
                            return False
                            
                        logger.info(f"Fallback navigation successful for section '{current_section}'")
                
                sections_processed += 1
                
                # Update index of last processed section
                for i, section in enumerate(FORM_SECTIONS):
                    if section == current_section:
                        last_processed_index = i
                        break
                
                # Check if we're at the end
                if sections_processed == max_sections:
                    logger.info("All sections processed, checking for success code")
                    return verify_submission_result(nova)
                
                # Wait for next section to load
                logger.info("Waiting for next section to load...")
                time.sleep(2)
            
            # If we get here, we've processed all sections
            logger.info("All sections processed, checking for success code")
            return verify_submission_result(nova)
            
    except Exception as e:
        logger.exception(f"Error during form automation: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Automate form filling using Nova-ACT with enhanced verification")
    parser.add_argument(
        "--json", 
        dest="json_file", 
        help="Path to the JSON file containing form data (default: hard_form_data_actual.json in script directory)",
        default=None
    )
    parser.add_argument(
        "--form-url", 
        dest="form_url", 
        help=f"URL of the form to automate (default: {HARD_FORM_URL})",
        default=HARD_FORM_URL
    )
    
    args = parser.parse_args()
    
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
    
    # Clean up inputs if they contain leading/trailing whitespace
    json_file_path = args.json_file.strip() if args.json_file else None
    form_url = args.form_url.strip() if args.form_url else HARD_FORM_URL
    
    # Log the actual parameters being used
    if json_file_path:
        logger.info(f"Using JSON file from command line: {json_file_path}")
    
    if form_url != HARD_FORM_URL:
        logger.info(f"Using custom form URL: {form_url}")
    
    # Run the form automation with the specified JSON file and form URL
    success = automate_form(json_file_path, form_url)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)