#!/usr/bin/env python3
"""
Submission handler with comprehensive verification for Asteroid Form Challenge.
Responsible for handling the Coverage Options section and final submission of the form.
"""

import logging
import time
import os
from typing import List, Dict, Any, Tuple
from nova_act import NovaAct, BOOL_SCHEMA
from field_detection import field_exists, get_form_label
from field_dependencies import should_process_field
from fill_fields import (
    fill_text_field,
    fill_date_field,
    select_dropdown_option,
    fill_checkbox
)
from navigation import click_button, navigate_to_section
from config import FIELD_TYPES
from verify3 import verify_field, verify_section
from error_handler import retry_failed_fields, navigate_to_next_section

# Initialize logger
logger = logging.getLogger("nova_form_automation")

def handle_coverage_options(nova: NovaAct, form_data: dict) -> bool:
    """
    Handle the Coverage Options section of the form with comprehensive verification.
    For the Asteroid form challenge, this section may be empty, in which case
    we simply click Submit.
    
    Args:
        nova: NovaAct instance
        form_data: Dictionary containing form data
        
    Returns:
        bool: True if all fields were processed successfully
    """
    logger.info("Processing Coverage Options section")
    section_name = "Coverage Options"
    
    # Extract coverage data
    coverage_data = {}
    if "coverage" in form_data and form_data["coverage"]:
        coverage_data.update(form_data["coverage"])
        logger.info("Found coverage data in form data")
    
    if "materialDamage" in form_data and form_data["materialDamage"]:
        coverage_data.update(form_data["materialDamage"])
        logger.info("Found material damage data in form data")
        
    # Quick check for any visible fields
    query = "Are there any input fields, dropdowns, or checkboxes visible on this page? Answer true or false."
    result = nova.act(query, schema=BOOL_SCHEMA)
    has_visible_fields = result.matches_schema and result.parsed_response
    
    # If no coverage data or no visible fields, just proceed to submission
    if not coverage_data or not has_visible_fields:
        logger.info("No coverage data found or no fields visible - proceeding directly to submission")
        
        # Try to click Submit button
        submit_success = click_button(nova, "Submit Application")
        if not submit_success:
            logger.warning("Failed to click Submit button, trying Next button")
            return click_button(nova, "Next")
        return submit_success
    
    # If we have data and fields are visible, proceed with filling them
    logger.info("Found coverage fields to fill")
    success = True
    
    # Process each field in the coverage data
    for key, value in coverage_data.items():
        # Use centralized get_form_label function with section context
        label = get_form_label(key, section_name)
        
        # Check if field is in the mapping
        if key not in FIELD_TYPES:
            logger.warning(f"Field '{key}' not found in FIELD_TYPES configuration, skipping")
            continue
            
        # Get field type from configuration
        field_type = FIELD_TYPES[key]
        logger.info(f"Processing field '{label}' (key: {key}, type: {field_type}, value: {value})")
        
        # Check if field exists in the form
        if not field_exists(nova, label, section_name, field_type):
            logger.warning(f"Field '{label}' does not exist in the form, skipping")
            continue
        
        # Check if field should be processed based on dependencies
        if not should_process_field(coverage_data, key, section_name):
            logger.info(f"Skipping field '{label}' due to dependencies")
            continue
        
        # Fill field with immediate verification and retry
        field_filled = False
        max_attempts = 2  # Maximum number of attempts to fill a field
        
        for attempt in range(max_attempts):
            if attempt > 0:
                logger.info(f"Immediate retry attempt {attempt+1} for field '{label}'")
            
            # Fill the field
            if field_type == "text":
                field_success = fill_text_field(nova, label, str(value))
            elif field_type == "date":
                field_success = fill_date_field(nova, label, value)
            elif field_type == "dropdown":
                field_success = select_dropdown_option(nova, label, value)
            elif field_type == "checkbox":
                field_success = fill_checkbox(nova, label, value)
            else:
                logger.error(f"Unknown field type '{field_type}' for field '{label}'")
                field_success = False
            
            if not field_success:
                logger.error(f"Failed to fill field '{label}'")
                continue
            
            # Verify the field was filled correctly
            logger.info(f"Verifying field '{label}'")
            verification_success = verify_field(nova, label, value, field_type)
            
            if verification_success:
                logger.info(f"✅ Field '{label}' filled and verified successfully")
                field_filled = True
                break
            else:
                logger.warning(f"❌ Field '{label}' verification failed, will retry")
        
        if not field_filled:
            logger.warning(f"Could not fill field '{label}' correctly after {max_attempts} attempts")
            success = False
    
    # After filling all fields, perform section verification if we have data
    if coverage_data:
        logger.info("Performing comprehensive section verification")
        failed_fields = verify_section(nova, section_name, form_data)
        
        if failed_fields:
            logger.warning(f"Found {len(failed_fields)} fields that failed verification")
            
            # Retry filling failed fields
            retry_failed_fields(nova, failed_fields)
        else:
            logger.info("All fields verified successfully")
    
    # After filling all fields, click Submit to proceed to review page
    logger.info("Attempting to proceed to review page")
    submit_success = click_button(nova, "Submit")
    
    if not submit_success:
        logger.warning("Failed to click Submit button, trying Next button")
        next_success = click_button(nova, "Next")
        
        if not next_success:
            logger.error("Failed to click Submit or Next button")
            return False
    
    logger.info(f"Coverage Options section processed successfully")
    return True

def handle_final_submission(nova: NovaAct) -> bool:
    """
    Handle the final review and submission page.
    
    Args:
        nova: NovaAct instance
        
    Returns:
        bool: True if successfully submitted
    """
    logger.info("Processing final submission page")
    
    # Wait for the review page to load
    time.sleep(2)
    
    # Check if we're already on a results page with ASTEROID code
    if verify_submission_result(nova):
        logger.info("Already on results page with ASTEROID_1 code!")
        return True
    
    # Check if we're on the review page
    query = (
        "Is this a review or summary page that shows all the information entered in the form? "
        "Answer true or false."
    )
    result = nova.act(query, schema=BOOL_SCHEMA)
    
    if not result.parsed_response:
        logger.warning("Not clearly on a review page, attempting to proceed anyway")
    else:
        logger.info("Confirmed on review/summary page")
    
    # Scroll to review all information
    logger.info("Scrolling through the review page")
    nova.act("Scroll down to see all information and find the submission button")
    
    # Try to find and click the final submission button
    # Try various common button texts
    for button_text in ["Submit", "Confirm", "Submit Application", "Finish", "Complete", "Submit Quote", "Submit Form"]:
        logger.info(f"Looking for '{button_text}' button")
        
        query = f"Is there a button or link labeled '{button_text}' or similar? Answer true or false."
        result = nova.act(query, schema=BOOL_SCHEMA)
        
        if result.parsed_response:
            logger.info(f"Found '{button_text}' button, clicking it")
            nova.act(f"Click the button labeled '{button_text}' or similar")
            
            # Wait for submission to process
            time.sleep(3)
            
            # Verify result
            if verify_submission_result(nova):
                return True
    
    # If we couldn't find any of the expected buttons, try a more general approach
    logger.warning("Could not find labeled submit button, trying to find any submit button")
    nova.act(
        "Find and click the submit button or main call-to-action button at the bottom of the page. "
        "Look for a prominent button that would finalize the form submission."
    )
    
    # Wait for submission to process
    time.sleep(3)
    
    # Check result
    return verify_submission_result(nova)

def verify_submission_result(nova: NovaAct) -> bool:
    """
    Verify if the form was successfully submitted and shows the ASTEROID_1 code.
    
    Args:
        nova: NovaAct instance
        
    Returns:
        bool: True if ASTEROID_1 code found
    """
    logger.info("Verifying form submission result")
    
    # Check for success message containing ASTEROID_1
    query = "Look for a success code on the page. Is there a code that says 'ASTEROID_1'? Answer true or false."
    result = nova.act(query, schema=BOOL_SCHEMA)
    
    if result.matches_schema and result.parsed_response:
        logger.info("✅ SUCCESS: ASTEROID_1 code found!")
        return True
    
    # Check for ASTEROID_0 (data mistake)
    query = "Is there a code that says 'ASTEROID_0' on the page? Answer true or false."
    result = nova.act(query, schema=BOOL_SCHEMA)
    
    if result.matches_schema and result.parsed_response:
        logger.error("Found ASTEROID_0 code - there was a mistake in the submitted data")
    else:
        logger.error("No ASTEROID code found - form may not have submitted correctly")
    
    return False

if __name__ == "__main__":
    import sys
    from config import HARD_FORM_URL
    from utils_final import load_json_data
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    
    try:
        # Load data from hard_form_data_actual.json
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(script_dir, "hard_form_data_actual.json")
        
        # Check if the file exists in current directory, otherwise try parent directory
        if not os.path.exists(data_file):
            logger.info(f"File not found at {data_file}, checking parent directory")
            parent_dir = os.path.dirname(script_dir)
            data_file = os.path.join(parent_dir, "hard_form_data_actual.json")
            
            # If still not found, fall back to hard_form_data.json
            if not os.path.exists(data_file):
                logger.warning("hard_form_data_actual.json not found, falling back to hard_form_data.json")
                data_file = os.path.join(script_dir, "hard_form_data.json")
                if not os.path.exists(data_file):
                    data_file = os.path.join(parent_dir, "hard_form_data.json")
        
        logger.info(f"Loading data from: {data_file}")
        data = load_json_data(data_file)
        
        # Initialize Nova-ACT and navigate to the form
        with NovaAct(starting_page=HARD_FORM_URL) as nova:
            logger.info("Starting Coverage Options and Submission test")
            
            # Wait for the form to load
            time.sleep(3)
            
            # Navigate to the Coverage Options section
            # This assumes we've already completed previous sections
            logger.info("Attempting to navigate directly to Coverage Options section")
            if not navigate_to_section(nova, "Coverage Options"):
                logger.error("Failed to navigate to Coverage Options section")
                sys.exit(1)
                
            # Allow time for the section to load
            time.sleep(2)
            logger.info("Successfully navigated to Coverage Options section")
                
            # Process Coverage Options section
            coverage_result = handle_coverage_options(nova, data)
            
            if coverage_result:
                logger.info("✅ Coverage Options section processed successfully")
                
                # Now handle final submission
                submission_result = handle_final_submission(nova)
                
                if submission_result:
                    logger.info("✅ Form submitted successfully! ASTEROID_1 code found.")
                else:
                    logger.error("❌ Form submission failed or ASTEROID_0 code found.")
                
                result = submission_result
            else:
                logger.error("❌ Coverage Options section processed with errors")
                result = False
                
    except Exception as e:
        logger.exception(f"Error in Coverage Options and Submission test: {e}")
        sys.exit(1)
    
    sys.exit(0 if result else 1)