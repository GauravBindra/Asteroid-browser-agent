#!/usr/bin/env python3
"""
Submission handler for Asteroid Form Challenge.
Responsible for handling the Coverage Options section and final submission of the form.
"""

import logging
import time
from nova_act import NovaAct, BOOL_SCHEMA
from field_detection import field_exists
from field_dependencies import should_process_field
from fill_fields import (
    fill_text_field,
    fill_date_field,
    select_dropdown_option,
    fill_checkbox
)
from navigation import click_button, navigate_to_section
from config import FIELD_TYPES

# Initialize logger
logger = logging.getLogger("nova_form_automation")

def handle_coverage_options(nova: NovaAct, form_data: dict) -> bool:
    """
    Handle the Coverage Options section of the form.
    
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
    if "coverage" in form_data:
        coverage_data.update(form_data["coverage"])
        logger.info("Found coverage data in form data")
    
    if "materialDamage" in form_data:
        coverage_data.update(form_data["materialDamage"])
        logger.info("Found material damage data in form data")
        
    if not coverage_data:
        logger.warning("No coverage data found in form data")
        # Still proceed since we need to get to the next step
        return click_button(nova, "Submit")
    
    success = True
    
    # Process each field in the coverage data
    for key, value in coverage_data.items():
        # Standard conversion for fields: camelCase -> Spaced Words
        label_words = []
        current_word = ""
        
        for char in key:
            if char.isupper():
                if current_word:
                    label_words.append(current_word)
                current_word = char
            else:
                current_word += char
        
        if current_word:
            label_words.append(current_word)
        
        label = " ".join(word.capitalize() for word in label_words)
        
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
        
        # Fill field based on type
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
            success = False
    
    # After filling all fields, click Next to proceed to review page
    if success:
        logger.info("Attempting to proceed to review page")
        if not click_button(nova, "Submit"):
            logger.warning("Failed to click Submit button")
            success = False
    
    logger.info(f"Coverage Options section processed {'successfully' if success else 'with errors'}")
    return success

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
    for button_text in ["Submit", "Confirm", "Submit Application", "Finish", "Complete", "Submit Quote"]:
        logger.info(f"Looking for '{button_text}' button")
        
        query = f"Is there a button or link labeled '{button_text}' or similar? Answer true or false."
        result = nova.act(query, schema=BOOL_SCHEMA)
        
        if result.parsed_response:
            logger.info(f"Found '{button_text}' button, clicking it")
            nova.act(f"Click the button labeled '{button_text}' or similar")
            
            # Wait for submission to process
            time.sleep(5)
            
            # Verify result
            return verify_submission_result(nova)
    
    # If we couldn't find any of the expected buttons, try a more general approach
    logger.warning("Could not find labeled submit button, trying to find any submit button")
    nova.act(
        "Find and click the submit button or main call-to-action button at the bottom of the page. "
        "Look for a prominent button that would finalize the form submission."
    )
    
    # Wait for submission to process
    time.sleep(5)
    
    # Verify result
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
    
    # Wait for submission to complete
    time.sleep(2)
    
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
    import os
    import sys
    from config import HARD_FORM_URL
    from utils_final import load_json_data
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    
    try:
        # Load data
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        data_file = os.path.join(parent_dir, "hard_form_data.json")
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