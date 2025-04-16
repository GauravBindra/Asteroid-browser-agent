#!/usr/bin/env python3
"""
Hard form automation functions for Nova-ACT (Improved Version).

This module contains functions for automating the hard form filling using Nova-ACT.
It reuses core functionality from form_automation_working.py while adding specialized
handlers for the multi-section hard form with improved interaction patterns.
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
        # Step 1: Find and focus the dropdown
        nova.act(f"Find and click on the dropdown field labeled '{label}'")
        time.sleep(1)
        
        # Step 2: Clear any existing selection
        nova.act("Clear any existing text in this field")
        time.sleep(1)
        
        # Step 3: Type the selection directly - using modified approach without Tab key
        # Using separate press Enter to avoid issues with tab clearing the field
        nova.act(f"Type '{value}' in this field and press Enter to confirm")
        time.sleep(2)
        
        # Step 4: Click elsewhere to move focus away without using Tab
        nova.act("Click on an empty area of the form to move focus away from this field")
        time.sleep(1)
        
        logger.info(f"Successfully selected '{value}' for '{label}' dropdown using step-by-step approach")
        return True
        
    except Exception as e:
        logger.exception(f"Error selecting '{value}' for '{label}' dropdown: {e}")
        
        # Alternative fallback approach
        try:
            logger.info(f"Attempting alternative method for '{label}' dropdown")
            
            # Simple direct command without Tab key
            command = (
                f"Find the dropdown field labeled '{label}', "
                f"clear it, and type '{value}' without pressing Tab afterward"
            )
            
            nova.act(command)
            time.sleep(2)
            
            logger.info(f"Alternative method successfully selected '{value}' for '{label}'")
            return True
            
        except Exception as fallback_error:
            logger.exception(f"Alternative method for '{label}' dropdown also failed: {fallback_error}")
            return False

def fill_date_field(nova, label, value):
    """
    Fill a date field in the form with format detection and conversion.
    
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
        # Step 1: Detect the expected date format by examining the field
        logger.info("Examining date field to determine expected format")
        format_detect_cmd = f"Look at the date field labeled '{label}' and tell me what date format it expects based on placeholder or hint text"
        format_response = nova.act(format_detect_cmd)
        time.sleep(1)
        
        # Parse the response to determine format
        expected_format = "dd/mm/yyyy"  # Default assumption
        
        if "mm/dd" in format_response.lower() or "month/day" in format_response.lower():
            expected_format = "mm/dd/yyyy"
            logger.info(f"Detected expected date format: {expected_format}")
        else:
            logger.info(f"Using default date format: {expected_format}")
        
        # Step 2: Format the date according to the expected format
        date_parts = value.split('-')
        if len(date_parts) == 3:
            year, month, day = date_parts
            
            if expected_format == "mm/dd/yyyy":
                formatted_date = f"{month}/{day}/{year}"
                logger.info(f"Converting to mm/dd/yyyy format: {formatted_date}")
            else:
                formatted_date = f"{day}/{month}/{year}" 
                logger.info(f"Converting to dd/mm/yyyy format: {formatted_date}")
        else:
            formatted_date = value  # Keep original if not in expected format
            logger.warning(f"Could not parse date format for {value}, using as is")
        
        # Step 3: Enter the date using step-by-step approach
        # Step 3.1: Find and focus the date field
        nova.act(f"Find and click on the date field labeled '{label}'")
        time.sleep(1)
        
        # Step 3.2: Clear any existing value
        nova.act("Clear any existing text in this field")
        time.sleep(1)
        
        # Step 3.3: Type the date value directly
        nova.act(f"Type '{formatted_date}' in this field")
        time.sleep(2)
        
        # Step 3.4: Click elsewhere to move focus away
        nova.act("Click on an empty area of the form to move focus away from this field")
        time.sleep(1)
        
        # Step 4: Verify what was entered
        verify_cmd = f"Look at the date field labeled '{label}' and tell me what date value it currently shows"
        actual_value = nova.act(verify_cmd)
        logger.info(f"Date field verification result: {actual_value}")
        
        # If verification shows issues, try alternative format
        if "incorrect" in actual_value.lower() or "invalid" in actual_value.lower() or "error" in actual_value.lower():
            logger.warning("Date format may be incorrect, trying alternative format")
            
            # Try opposite format
            if expected_format == "dd/mm/yyyy":
                alternative_date = f"{month}/{day}/{year}"  # mm/dd/yyyy
                logger.info(f"Trying alternative format mm/dd/yyyy: {alternative_date}")
            else:
                alternative_date = f"{day}/{month}/{year}"  # dd/mm/yyyy
                logger.info(f"Trying alternative format dd/mm/yyyy: {alternative_date}")
            
            # Re-enter with alternative format
            nova.act(f"Find and click on the date field labeled '{label}'")
            time.sleep(1)
            nova.act("Clear any existing text in this field")
            time.sleep(1)
            nova.act(f"Type '{alternative_date}' in this field")
            time.sleep(2)
            nova.act("Click on an empty area of the form to move focus away from this field")
            time.sleep(1)
        
        logger.info(f"Successfully filled date field '{label}' with appropriate date format")
        return True
        
    except Exception as e:
        logger.exception(f"Error filling date field '{label}': {e}")
        
        # Simple fallback approach as last resort
        try:
            logger.info(f"Attempting simplified fallback for date field '{label}'")
            
            # Assume dd/mm/yyyy as the format most likely to work
            if "-" in value and len(value.split('-')) == 3:
                year, month, day = value.split('-')
                simplified_date = f"{day}/{month}/{year}"
            else:
                simplified_date = value
            
            # Single direct command
            command = f"Find the date field labeled '{label}', clear it, and type '{simplified_date}'"
            nova.act(command)
            time.sleep(2)
            
            logger.info(f"Simplified fallback completed for date field '{label}'")
            return True
            
        except Exception as fallback_error:
            logger.exception(f"All approaches failed for date field '{label}': {fallback_error}")
            return False

def navigate_to_tab(nova, tab_name):
    """
    Navigate to a specific tab in the form.
    
    Args:
        nova: NovaAct instance
        tab_name: Name of the tab to navigate to
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Navigating to tab '{tab_name}'")
    
    try:
        # Use specific instruction to find and click the tab
        command = f"Find and click on the tab labeled '{tab_name}'"
        nova.act(command)
        
        # Longer wait for tab navigation to complete
        time.sleep(2)
        
        # Confirm we're on the right tab
        confirm_command = f"Look at the page and confirm you are now on the '{tab_name}' tab or section"
        nova.act(confirm_command)
        
        logger.info(f"Successfully navigated to '{tab_name}' tab")
        return True
        
    except Exception as e:
        logger.exception(f"Error navigating to '{tab_name}' tab: {e}")
        return False

def click_next_button(nova):
    """
    Click the "Next" button to move to the next section of the form.
    
    Args:
        nova: NovaAct instance
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Clicking Next button")
    
    try:
        # Scroll to make sure the Next button is visible
        nova.act("Scroll down to make sure the Next button is visible")
        time.sleep(1)
        
        # Use explicit instruction to find and click the Next button
        command = "Find and click the button labeled 'Next'"
        nova.act(command)
        
        # Longer wait for page transition to complete
        time.sleep(3)
        
        logger.info("Successfully clicked Next button")
        return True
        
    except Exception as e:
        logger.exception(f"Error clicking Next button: {e}")
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