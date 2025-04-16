#!/usr/bin/env python3
"""
Hard form automation functions for Nova-ACT.

This module contains functions for automating the hard form filling using Nova-ACT.
It reuses core functionality from form_automation_working.py while adding specialized
handlers for the multi-section hard form.
"""

import logging
import time
import re

# Import functions from the easy form automation module
from form_automation_working import (
    fill_text_field,
    handle_checkbox,
    click_button,
    wait_for_form_load,
    extract_result_code,
    submit_form
)

# Core utility functions for hard form

def select_dropdown_option(nova, label, value):
    """
    Select an option from a dropdown field in the form.
    
    Args:
        nova: NovaAct instance
        label: Field label to look for
        value: Option value to select
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Selecting '{value}' for dropdown '{label}'")
    
    try:
        # Step 1: Formulate a clear, specific command for dropdown interaction
        command = f"find the dropdown field labeled '{label}' and select the option '{value}'"
        
        # Step 2: Use Nova-ACT's natural language capability to interact with the dropdown
        nova.act(command)
        
        # Step 3: Wait for the dropdown selection to complete and UI to update
        time.sleep(1)
        
        # Step 4: Attempt to verify the selection was made (optional)
        verification_command = f"check if the dropdown '{label}' has '{value}' selected"
        try:
            nova.act(verification_command)
            # If we get here without exception, assume verification passed
        except Exception:
            # If verification fails, log but don't fail the function
            # as Nova-ACT may not be able to verify the selection
            logger.warning(f"Could not verify selection of '{value}' for '{label}'")
        
        logger.info(f"Successfully selected '{value}' for '{label}' dropdown")
        return True
        
    except Exception as e:
        logger.exception(f"Error selecting '{value}' for '{label}' dropdown: {e}")
        
        # Step 5: Try a fallback approach for potential custom dropdowns
        try:
            logger.info(f"Attempting fallback method for '{label}' dropdown")
            
            # Alternative approach: Click on dropdown first, then select option
            click_command = f"click on the dropdown or select field labeled '{label}'"
            nova.act(click_command)
            
            # Wait for dropdown to open
            time.sleep(1)
            
            # Select the option by text
            select_command = f"select or click on the option '{value}' from the dropdown list"
            nova.act(select_command)
            
            # Wait for selection to take effect
            time.sleep(1)
            
            logger.info(f"Fallback method successfully selected '{value}' for '{label}'")
            return True
            
        except Exception as fallback_error:
            logger.exception(f"Fallback for '{label}' dropdown also failed: {fallback_error}")
            return False

def fill_date_field(nova, label, value):
    """
    Fill a date field in the form.
    
    Args:
        nova: NovaAct instance
        label: Field label to look for
        value: Date value to enter (YYYY-MM-DD format)
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Filling date field '{label}' with value '{value}'")
    
    try:
        # Format check - ensure value is in YYYY-MM-DD format
        # The form expects this format for date inputs
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
            logger.warning(f"Date value '{value}' doesn't match expected YYYY-MM-DD format")
            # Continue anyway, as Nova-ACT may be able to handle different formats
        
        # Try direct input approach
        command = f"find the date field labeled '{label}' and enter the date '{value}'"
        nova.act(command)
        
        # Wait for date picker to process the input
        time.sleep(1)
        
        # Try to verify the date was entered correctly
        try:
            verify_command = f"verify that the date field '{label}' contains '{value}'"
            nova.act(verify_command)
        except Exception:
            logger.warning(f"Could not verify date '{value}' was entered in field '{label}'")
        
        logger.info(f"Successfully filled date field '{label}' with '{value}'")
        return True
        
    except Exception as e:
        logger.exception(f"Error filling date field '{label}': {e}")
        
        # Try fallback approach - click then type
        try:
            logger.info(f"Attempting fallback method for date field '{label}'")
            
            # Click the date field first
            click_command = f"click on the date field labeled '{label}'"
            nova.act(click_command)
            time.sleep(0.5)
            
            # Clear any existing value if needed
            clear_command = f"clear the current value in the date field"
            nova.act(clear_command)
            time.sleep(0.5)
            
            # Type the date value
            type_command = f"type the date '{value}'"
            nova.act(type_command)
            time.sleep(0.5)
            
            # Press Tab to confirm the date
            tab_command = "press the Tab key to confirm the date"
            nova.act(tab_command)
            time.sleep(0.5)
            
            logger.info(f"Fallback method successfully entered date '{value}' in field '{label}'")
            return True
            
        except Exception as fallback_error:
            logger.exception(f"Fallback for date field '{label}' also failed: {fallback_error}")
            return False

# This skeleton will be expanded in steps according to our implementation plan

def automate_hard_form(nova, form_data):
    """
    Complete the entire hard form automation process.
    
    Args:
        nova: NovaAct instance
        form_data: Dictionary containing form data
        
    Returns:
        tuple: (success, result_code)
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Starting hard form automation - skeleton implementation")
    
    # This is a placeholder implementation that will be expanded
    # in later steps according to our implementation plan
    
    logger.warning("Hard form automation not yet fully implemented")
    return False, None

# More functions will be added in subsequent implementation steps