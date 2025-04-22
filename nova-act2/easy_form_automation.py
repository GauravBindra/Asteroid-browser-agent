#!/usr/bin/env python3
"""
Easy form automation module for Asteroid challenge using Nova-ACT.

This module is specifically designed for the easy form (form2) version,
which has fewer fields and a simpler structure than the hard form.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from nova_act import NovaAct, BOOL_SCHEMA

# Import required functions from existing files
from config import EASY_FORM_URL
from fill_fields import (
    fill_text_field,
    fill_checkbox,
    select_dropdown_option
)
from date_helpers import fill_easy_form_date
from navigation import click_button
from utils_final import load_json_data

def verify_easy_form_field(nova, label, value, field_type="text"):
    """
    Verify if a field in the easy form contains the expected value.
    
    Args:
        nova: NovaAct instance
        label: The label of the field to verify
        value: The expected value in the field
        field_type: The type of field ("text", "dropdown", "checkbox", "date")
        
    Returns:
        bool: True if the field contains the expected value, False otherwise
    """
    logger = logging.getLogger("nova_form_automation")
    
    # Convert expected_value to string unless it's a boolean (for checkboxes)
    if not isinstance(value, bool):
        value = str(value)
    
    # Construct query based on field type
    if field_type == "checkbox":
        state = "checked" if value else "unchecked"
        logger.info(f"Verifying checkbox '{label}' is {state}")
        query = f"Is the checkbox labeled '{label}' {state}? Answer true or false."
    elif field_type == "dropdown":
        logger.info(f"Verifying dropdown '{label}' has '{value}' selected")
        query = f"Does the dropdown field labeled '{label}' have the option '{value}' selected? Answer true or false."
    elif field_type == "date":
        logger.info(f"Verifying date field '{label}' contains '{value}'")
        query = f"Does the date field labeled '{label}' contain the date '{value}'? Answer true or false."
    else:  # Default text field
        logger.info(f"Verifying text field '{label}' contains '{value}'")
        query = f"Does the field labeled '{label}' contain the value '{value}'? Answer true or false."
    
    try:
        result = nova.act(query, schema=BOOL_SCHEMA)
        
        if result.matches_schema and result.parsed_response:
            logger.info(f"✅ Verification successful: Field '{label}' contains expected value")
            return True
        else:
            logger.warning(f"❌ Verification failed: Field '{label}' does not contain expected value")
            return False
    except Exception as e:
        logger.exception(f"Error verifying field '{label}': {e}")
        return False

def verify_easy_form_section(nova, form_data):
    """
    Verify all fields in the easy form have been filled correctly.
    Similar to verify_section for hard forms but specific to easy form structure.
    
    Args:
        nova: NovaAct instance
        form_data: Dictionary containing the form data
        
    Returns:
        List[Dict]: List of fields that failed verification with their details
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Performing comprehensive verification of all fields in the easy form")
    
    # Define the fields to verify
    field_mapping = [
        {"key": "firstName", "label": "First Name", "type": "text"},
        {"key": "lastName", "label": "Last Name", "type": "text"},
        {"key": "dateOfBirth", "label": "Date of Birth", "type": "date"},
        {"key": "email", "label": "Email", "type": "text"},
        {"key": "phoneNumber", "label": "Phone Number", "type": "text"},
        {"key": "hasInsurance", "label": "Do you currently have insurance?", "type": "checkbox"},
        {"key": "wantsNewsletter", "label": "Would you like to receive our newsletter?", "type": "checkbox"},
        {"key": "agreeToTerms", "label": "I agree to the terms and conditions", "type": "checkbox"}
    ]
    
    # Track fields that failed verification
    failed_fields = []
    
    # Verify each field
    for field in field_mapping:
        key = field["key"]
        label = field["label"]
        field_type = field["type"]
        
        if key in form_data:
            value = form_data[key]
            
            # Perform verification
            logger.info(f"Verifying field '{label}' (type: {field_type}, expected value: {value})")
            verification_success = verify_easy_form_field(nova, label, value, field_type)
            
            if not verification_success:
                failed_fields.append({
                    "key": key,
                    "label": label,
                    "expected_value": value,
                    "field_type": field_type
                })
        else:
            logger.warning(f"Field '{key}' not in form data, skipping verification")
    
    if failed_fields:
        logger.warning(f"Found {len(failed_fields)} fields that failed verification")
    else:
        logger.info("All fields verified successfully")
    
    return failed_fields

def retry_failed_easy_form_fields(nova, failed_fields):
    """
    Retry filling fields in the easy form that failed verification.
    
    Args:
        nova: NovaAct instance
        failed_fields: List of dictionaries containing information about failed fields
        
    Returns:
        bool: True if any fields were successfully fixed, False otherwise
    """
    logger = logging.getLogger("nova_form_automation")
    
    if not failed_fields:
        logger.info("No failed fields to retry")
        return True
        
    logger.info(f"Retrying {len(failed_fields)} failed fields")
    
    # Track if any fields were fixed
    any_fields_fixed = False
    
    for field_info in failed_fields:
        key = field_info["key"]
        label = field_info["label"]
        value = field_info["expected_value"]
        field_type = field_info["field_type"]
        
        logger.info(f"Retrying field '{label}' (type: {field_type}) with value '{value}'")
        
        # Use different filling strategies for retries
        max_retries = 3
        for retry in range(max_retries):
            try:
                # Fill field based on type with slightly different approach each time
                if field_type == "text":
                    if key == "phoneNumber":
                        # Special handling for phone field
                        queries = [
                            f"Find the field labeled '{label}', click precisely in the center of it, and carefully type '{value}'.",
                            f"Locate the phone number field with label '{label}'. Click it and enter: {value}",
                            f"Find input field '{label}'. Clear any existing text and type {value} very carefully."
                        ]
                        query = queries[retry % len(queries)]
                        nova.act(query, max_steps=8)
                        field_success = True
                    else:
                        field_success = fill_text_field(nova, label, str(value))
                elif field_type == "date":
                    field_success = fill_easy_form_date(nova, label, value)
                elif field_type == "checkbox":
                    field_success = fill_checkbox(nova, label, value)
                else:
                    logger.error(f"Unknown field type '{field_type}' for field '{label}'")
                    field_success = False
                
                if not field_success:
                    logger.warning(f"Failed to retry field '{label}' (attempt {retry+1}/{max_retries})")
                    continue
                
                # Verify the field again after retrying
                verification_success = verify_easy_form_field(nova, label, value, field_type)
                
                if verification_success:
                    logger.info(f"✅ Successfully fixed field '{label}' on retry {retry+1}")
                    any_fields_fixed = True
                    break
                else:
                    logger.warning(f"❌ Field '{label}' still not verified correctly after retry {retry+1}")
                    
            except Exception as e:
                logger.warning(f"Error in retry {retry+1} for field '{label}': {e}")
                # Wait before next retry
                time.sleep(1.5)
    
    return any_fields_fixed

def fill_easy_form_fields(nova, form_data):
    """
    Fill all fields in the easy form.
    
    Args:
        nova: NovaAct instance
        form_data: Dictionary containing form data
        
    Returns:
        bool: True if all fields were filled successfully
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Filling fields for easy form")
    
    # Define field mapping (JSON key to form label and type)
    field_mapping = [
        {"key": "firstName", "label": "First Name", "type": "text"},
        {"key": "lastName", "label": "Last Name", "type": "text"},
        {"key": "dateOfBirth", "label": "Date of Birth", "type": "date"},
        {"key": "email", "label": "Email", "type": "text"},
        {"key": "phoneNumber", "label": "Phone Number", "type": "text"},
        {"key": "hasInsurance", "label": "Do you currently have insurance?", "type": "checkbox"},
        {"key": "wantsNewsletter", "label": "Would you like to receive our newsletter?", "type": "checkbox"},
        {"key": "agreeToTerms", "label": "I agree to the terms and conditions", "type": "checkbox"}
    ]
    
    # Fill each field
    success = True
    for field in field_mapping:
        key = field["key"]
        label = field["label"]
        field_type = field["type"]
        
        if key in form_data:
            value = form_data[key]
            
            # Retry up to 3 times for each field
            max_attempts = 3
            field_filled = False
            
            for attempt in range(max_attempts):
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt+1}/{max_attempts} for field '{label}'")
                    # Add a small delay between retries
                    time.sleep(1.5)
                
                try:
                    # Fill the field based on its type
                    if field_type == "text":
                        if key == "phoneNumber":
                            # Use a slightly different approach for phone number
                            logger.info(f"Using enhanced approach for phone number field '{label}'")
                            query = f"Find the field labeled '{label}', click precisely in the center of it, and type '{value}'."
                            nova.act(query, max_steps=8)
                            field_success = True
                        else:
                            field_success = fill_text_field(nova, label, str(value))
                    elif field_type == "date":
                        field_success = fill_easy_form_date(nova, label, value)
                    elif field_type == "checkbox":
                        field_success = fill_checkbox(nova, label, value)
                    else:
                        logger.error(f"Unknown field type '{field_type}' for field '{label}'")
                        field_success = False
                        
                    if not field_success:
                        logger.warning(f"Failed to fill field '{label}' on attempt {attempt+1}")
                        continue
                    
                    # Verify the field was filled correctly
                    verification_success = verify_easy_form_field(nova, label, value, field_type)
                    if verification_success:
                        logger.info(f"Field '{label}' successfully filled and verified on attempt {attempt+1}")
                        field_filled = True
                        break
                    else:
                        logger.warning(f"Field '{label}' verification failed on attempt {attempt+1}")
                        
                except Exception as e:
                    logger.warning(f"Error on attempt {attempt+1} for field '{label}': {e}")
                    
            # Update overall success status
            if not field_filled:
                logger.error(f"Failed to fill/verify field '{label}' after {max_attempts} attempts")
                success = False
        else:
            logger.warning(f"Missing '{key}' in form data")
            success = False
    
    if success:
        logger.info("All fields filled and verified successfully")
    else:
        logger.warning("Some fields could not be filled or verified")
    
    return success

def submit_easy_form(nova):
    """
    Submit the easy form by clicking the Review and Submit buttons.
    
    Args:
        nova: NovaAct instance
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Submitting easy form")
    
    try:
        # Try multiple approaches to find and click the Review button
        for approach in range(3):
            try:
                if approach == 0:
                    # Approach 1: First try scrolling to bottom and clicking Review
                    logger.info("Approach 1: Scrolling to bottom and looking for Review button")
                    try:
                        nova.act("Scroll down slowly until you see the Review button at the bottom of the form.")
                        time.sleep(1)
                    except Exception as e:
                        logger.warning(f"Error scrolling: {e}")
                        # Continue anyway, button might still be visible
                        
                    if click_button(nova, "Review"):
                        logger.info("Successfully clicked Review button")
                        break
                        
                elif approach == 1:
                    # Approach 2: Direct instruction to find and click Review
                    logger.info("Approach 2: Direct instruction to find and click Review button")
                    nova.act(
                        "Find and click the Review button at the bottom of the form. "
                        "Look for a button that would take you to the review page."
                    )
                    time.sleep(1)
                    logger.info("Direct Review button click instruction completed")
                    break
                    
                else:
                    # Approach 3: Try to tab to the button
                    logger.info("Approach 3: Looking for any button at bottom of form")
                    nova.act(
                        "Find any button at the bottom of the form that looks like it would proceed "
                        "to the next step or review page. Click this button."
                    )
                    time.sleep(1)
                    logger.info("Alternative button click instruction completed")
                    break
                    
            except Exception as e:
                logger.warning(f"Approach {approach+1} failed: {e}")
                if approach < 2:
                    logger.info("Trying next approach...")
                    time.sleep(1)
                else:
                    logger.error("All approaches to find Review button failed")
                    return False
        
        # Wait for review page to load
        logger.info("Waiting for review page to load")
        time.sleep(2)
        
        # Try multiple approaches to click Submit button
        for approach in range(3):
            try:
                if approach == 0:
                    # Approach 1: Standard click
                    logger.info("Approach 1: Clicking Submit button")
                    if click_button(nova, "Submit"):
                        logger.info("Successfully clicked Submit button")
                        break
                        
                elif approach == 1:
                    # Approach 2: Direct instruction
                    logger.info("Approach 2: Direct instruction to find and click Submit button")
                    nova.act(
                        "Find and click the submit button or main call-to-action button. "
                        "Look for a prominent button that would finalize the form submission."
                    )
                    time.sleep(1)
                    logger.info("Direct Submit button click instruction completed")
                    break
                    
                else:
                    # Approach 3: Try any button that looks like a submit
                    logger.info("Approach 3: Looking for any submission-related button")
                    nova.act(
                        "Look for a button that says 'Submit', 'Finish', 'Complete', or similar. "
                        "Click this button to finalize the form submission."
                    )
                    time.sleep(1)
                    logger.info("Alternative Submit button click instruction completed")
                    break
                    
            except Exception as e:
                logger.warning(f"Submit approach {approach+1} failed: {e}")
                if approach < 2:
                    logger.info("Trying next submit approach...")
                    time.sleep(1)
                else:
                    logger.error("All approaches to find Submit button failed")
                    return False
        
        # Wait for submission to complete
        logger.info("Waiting for submission to complete")
        time.sleep(3)
        
        logger.info("Form submitted successfully")
        return True
        
    except Exception as e:
        logger.exception(f"Error during form submission: {e}")
        
        # Try one last desperate approach
        try:
            logger.info("Trying final emergency submission approach")
            nova.act(
                "Find any button at the bottom of the page that could finalize the form. "
                "Look for Review, Submit, Complete, or any similar button and click it."
            )
            time.sleep(3)
            return True
        except Exception as e2:
            logger.exception(f"Emergency approach also failed: {e2}")
            return False

def verify_submission_success(nova):
    """
    Verify if the form submission was successful and extracted the ASTEROID_1 code.
    
    Args:
        nova: NovaAct instance
        
    Returns:
        bool: True if successful and ASTEROID_1 code found
    """
    logger = logging.getLogger("nova_form_automation")
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

def automate_easy_form(data_file_path=None, form_url=None):
    """
    Run the full easy form automation process.
    
    Args:
        data_file_path: Path to the JSON data file (optional)
        form_url: URL of the form to automate (optional)
        
    Returns:
        bool: True if form was successfully completed, False otherwise
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Starting easy form automation")
    
    # Load form data
    try:
        if data_file_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            data_file_path = os.path.join(parent_dir, "easy_form_data.json")
        
        # Check if file exists
        if not os.path.exists(data_file_path):
            logger.warning(f"File not found at {data_file_path}, checking alternative locations")
            # Try different locations
            if os.path.exists(os.path.join(script_dir, "easy_form_data.json")):
                data_file_path = os.path.join(script_dir, "easy_form_data.json")
                
        form_data = load_json_data(data_file_path)
        logger.info(f"Successfully loaded form data from {data_file_path}")
    except Exception as e:
        logger.error(f"Failed to load form data: {e}")
        return False
    
    # Use the provided form URL or default to EASY_FORM_URL
    if form_url is None:
        form_url = EASY_FORM_URL
    
    try:
        # Initialize Nova-ACT and navigate to the form
        logger.info(f"Initializing Nova-ACT for easy form at {form_url}")
        with NovaAct(starting_page=form_url) as nova:
            logger.info("Browser started successfully")
            
            # Use default viewport size
            logger.info("Using default viewport size")
                
            # Wait for form to load
            logger.info("Waiting for form to load")
            time.sleep(3)
            
            # Fill all fields
            if not fill_easy_form_fields(nova, form_data):
                logger.warning("Some issues encountered during initial field filling")
                # Continue anyway as we'll verify and retry
            
            # Perform comprehensive verification of all fields
            logger.info("Performing comprehensive verification of all fields")
            failed_fields = verify_easy_form_section(nova, form_data)
            
            if failed_fields:
                logger.warning(f"Found {len(failed_fields)} fields that failed verification, attempting to fix them")
                
                # Retry filling failed fields
                retry_success = retry_failed_easy_form_fields(nova, failed_fields)
                
                if not retry_success:
                    logger.error("Failed to fix all fields after retry")
                    # Continue anyway and try to submit, might still work
            else:
                logger.info("All fields verified successfully")
            
            # Submit the form
            if not submit_easy_form(nova):
                logger.error("Failed to submit the form")
                return False
            
            # Verify the result
            if verify_submission_success(nova):
                logger.info("Easy form automation completed successfully!")
                return True
            else:
                logger.error("Easy form automation failed to obtain ASTEROID_1 code")
                
                # Last attempt to verify and fix any issues before giving up
                logger.info("Performing final verification before giving up")
                failed_fields = verify_easy_form_section(nova, form_data)
                
                if failed_fields:
                    logger.warning(f"Found {len(failed_fields)} fields with issues in final check")
                    retry_failed_easy_form_fields(nova, failed_fields)
                    
                    # Try submitting one more time
                    if submit_easy_form(nova) and verify_submission_success(nova):
                        logger.info("Final retry successful!")
                        return True
                
                return False
                
    except Exception as e:
        logger.exception(f"Error during easy form automation: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Automate easy form filling using Nova-ACT")
    parser.add_argument(
        "--json", 
        dest="json_file", 
        help="Path to the JSON file containing form data (default: easy_form_data.json in parent directory)",
        default=None
    )
    parser.add_argument(
        "--form-url", 
        dest="form_url", 
        help=f"URL of the form to automate (default: {EASY_FORM_URL})",
        default=EASY_FORM_URL
    )
    
    args = parser.parse_args()
    
    # Set up logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"easy_form_automation_{timestamp}.log")
    
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
    
    # Run the form automation with the specified JSON file and form URL
    success = automate_easy_form(args.json_file, args.form_url)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)