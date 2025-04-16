#!/usr/bin/env python3
"""
Streamlined hard form automation functions for Nova-ACT.

This module contains optimized functions for automating the hard form filling using Nova-ACT.
It reuses core functionality from form_automation_working.py while adding specialized
handlers for the multi-section hard form with optimized performance.

Following our step-by-step implementation plan, this version includes:
1. Basic skeleton
2. select_dropdown_option() function
3. fill_date_field() function
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

# Core utility functions for hard form - optimized for speed and reliability

def select_dropdown_option(nova, label, value):
    """
    Select an option from a dropdown field in the form - optimized approach.
    
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
        # Single command with clear instructions
        command = (
            f"Find the dropdown field labeled '{label}', clear any existing text, "
            f"then type '{value}' into it. Then click somewhere else on the page to confirm."
        )
        nova.act(command)
        
        logger.info(f"Successfully selected '{value}' for '{label}' dropdown")
        return True
        
    except Exception as e:
        logger.exception(f"Error selecting '{value}' for '{label}' dropdown: {e}")
        return False

def fill_date_field(nova, label, value):
    """
    Fill a date field in the form - optimized approach.
    
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
        # Convert from YYYY-MM-DD to DD/MM/YYYY format (most common for EU forms)
        parts = value.split('-')
        if len(parts) == 3:
            year, month, day = parts
            formatted_date = f"{day}/{month}/{year}"
            logger.info(f"Converted date format from {value} to {formatted_date}")
        else:
            formatted_date = value
            logger.warning(f"Could not parse date format for {value}, using as is")
        
        # Single command with format specifics
        command = (
            f"Find the date field labeled '{label}', clear any existing text, "
            f"then type '{formatted_date}' (day/month/year format) into it. "
            f"Then click somewhere else on the page to confirm."
        )
        nova.act(command)
        
        logger.info(f"Successfully filled date field '{label}' with '{formatted_date}'")
        return True
        
    except Exception as e:
        logger.exception(f"Error filling date field '{label}': {e}")
        
        # If primary approach fails, try MM/DD/YYYY format instead
        try:
            if len(parts) == 3:
                alt_formatted_date = f"{month}/{day}/{year}"
                logger.info(f"Trying alternative format: {alt_formatted_date}")
                
                command = (
                    f"Find the date field labeled '{label}', clear any existing text, "
                    f"then type '{alt_formatted_date}' (month/day/year format) into it. "
                    f"Then click somewhere else on the page to confirm."
                )
                nova.act(command)
                
                logger.info(f"Alternative date format attempt completed")
                return True
        except Exception as fallback_error:
            logger.exception(f"Date field fallback also failed: {fallback_error}")
            
        return False

# Placeholder for next functions in our implementation plan
# (navigate_to_tab and click_next_button will be implemented next)

# Placeholder for automate_hard_form function - will be expanded later

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