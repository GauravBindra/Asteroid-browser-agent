#!/usr/bin/env python3
"""
Form automation functions for Nova-ACT.

This module contains functions for automating form filling using Nova-ACT.
"""

import logging
import time

def wait_for_form_load(nova):
    """
    Wait for the form to fully load.
    
    Args:
        nova: NovaAct instance
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Waiting for form to load...")
    
    try:
        # Use a simple wait for now
        time.sleep(2)
        
        # Use Nova-ACT's natural language capability to wait for the form
        nova.act("wait for the form to be fully loaded and interactive")
        
        logger.info("Form loaded successfully")
        return True
        
    except Exception as e:
        logger.exception(f"Error waiting for form load: {e}")
        return False

def fill_text_field(nova, label, value):
    """
    Fill a text field in the form.
    
    Args:
        nova: NovaAct instance
        label: Field label to look for
        value: Value to enter
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Filling text field '{label}' with value '{value}'")
    
    try:
        # Use Nova-ACT's natural language capability to fill the field
        command = f"find the field labeled '{label}' and enter '{value}'"
        nova.act(command)
        
        # Brief pause to ensure the field is properly filled
        time.sleep(0.5)
        
        logger.info(f"Successfully filled '{label}' field")
        return True
        
    except Exception as e:
        logger.exception(f"Error filling '{label}' field: {e}")
        return False

def fill_easy_form_text_fields(nova, form_data):
    """
    Fill all text fields in the easy form.
    
    Args:
        nova: NovaAct instance
        form_data: Dictionary containing form data
        
    Returns:
        bool: True if all fields were filled successfully
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Filling text fields for easy form")
    
    # Make sure the form is loaded
    if not wait_for_form_load(nova):
        logger.error("Form failed to load properly.")
        return False
    
    # Define the text fields to fill
    text_fields = [
        {"label": "First Name", "key": "firstName"},
        {"label": "Last Name", "key": "lastName"},
        {"label": "Date of Birth", "key": "dateOfBirth"},
        {"label": "Email", "key": "email"},
        {"label": "Phone Number", "key": "phoneNumber"}
    ]
    
    # Fill each text field
    success = True
    for field in text_fields:
        label = field["label"]
        key = field["key"]
        
        if key in form_data:
            value = form_data[key]
            field_success = fill_text_field(nova, label, value)
            if not field_success:
                success = False
        else:
            logger.warning(f"Missing '{key}' in form data")
            success = False
    
    if success:
        logger.info("All text fields filled successfully")
    else:
        logger.warning("Some text fields could not be filled")
    
    return success

def handle_checkbox(nova, label, should_check):
    """
    Check or uncheck a checkbox in the form.
    
    Args:
        nova: NovaAct instance
        label: Checkbox label to look for
        should_check: Whether the checkbox should be checked (True) or unchecked (False)
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    action = "check" if should_check else "uncheck"
    logger.info(f"{action.capitalize()}ing checkbox '{label}'")
    
    try:
        # Use Nova-ACT's natural language capability to handle the checkbox
        command = f"find the checkbox labeled '{label}' and {action} it"
        nova.act(command)
        
        # Brief pause to ensure the checkbox state is properly changed
        time.sleep(0.5)
        
        logger.info(f"Successfully {action}ed checkbox '{label}'")
        return True
        
    except Exception as e:
        logger.exception(f"Error {action}ing checkbox '{label}': {e}")
        return False

def handle_easy_form_checkboxes(nova, form_data):
    """
    Handle all checkboxes in the easy form.
    
    Args:
        nova: NovaAct instance
        form_data: Dictionary containing form data
        
    Returns:
        bool: True if all checkboxes were handled successfully
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Handling checkboxes for easy form")
    
    # Define the checkboxes to handle
    checkboxes = [
        {"label": "Do you currently have insurance?", "key": "hasInsurance"},
        {"label": "Would you like to receive our newsletter?", "key": "wantsNewsletter"},
        {"label": "I agree to the terms and conditions", "key": "agreeToTerms"}
    ]
    
    # Handle each checkbox
    success = True
    for checkbox in checkboxes:
        label = checkbox["label"]
        key = checkbox["key"]
        
        if key in form_data:
            should_check = form_data[key]
            checkbox_success = handle_checkbox(nova, label, should_check)
            if not checkbox_success:
                success = False
        else:
            logger.warning(f"Missing '{key}' in form data")
            success = False
    
    if success:
        logger.info("All checkboxes handled successfully")
    else:
        logger.warning("Some checkboxes could not be handled")
    
    return success


#   1. handle_checkbox(nova, label, should_check) function:
#     - Takes a checkbox label and a boolean indicating whether it should be checked
#     - Uses Nova-ACT to find and check/uncheck the checkbox based on the boolean value
#     - Includes proper error handling and logging
#     - Returns success/failure status
#   2. handle_easy_form_checkboxes(nova, form_data) function:
#     - Maps checkbox labels to form data keys
#     - Iterates through all checkboxes in the easy form
#     - Calls handle_checkbox() for each checkbox with the appropriate state
#     - Tracks success/failure for each checkbox operation
#     - Returns overall success status

