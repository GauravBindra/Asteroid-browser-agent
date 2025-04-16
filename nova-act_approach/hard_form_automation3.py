#!/usr/bin/env python3
"""
Streamlined hard form automation functions for Nova-ACT.

This module contains optimized functions for automating the hard form filling using Nova-ACT.
It reuses core functionality from form_automation_working.py while adding specialized
handlers for the multi-section hard form with optimized performance.
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
        # Simple direct command
        command = f"Click on the tab or section labeled '{tab_name}'"
        nova.act(command)
        time.sleep(1.5)  # Wait for tab to load
        
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
        # Simple direct command
        nova.act("Scroll to the bottom of the form and click the Next button")
        time.sleep(2)  # Wait for page transition
        
        logger.info("Successfully clicked Next button")
        return True
        
    except Exception as e:
        logger.exception(f"Error clicking Next button: {e}")
        return False

# Section handler functions for the hard form

def fill_contact_details(nova, contact_data):
    """
    Fill the Contact Details section of the hard form.
    
    Args:
        nova: NovaAct instance
        contact_data: Dictionary containing contact details
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Filling Contact Details section")
    
    try:
        # Select title
        if "title" in contact_data:
            select_dropdown_option(nova, "Title", contact_data["title"])
        
        # Fill name fields
        if "firstName" in contact_data:
            fill_text_field(nova, "First Name", contact_data["firstName"])
        
        if "lastName" in contact_data:
            fill_text_field(nova, "Last Name", contact_data["lastName"])
        
        # Fill date of birth
        if "dateOfBirth" in contact_data:
            fill_date_field(nova, "Date of Birth", contact_data["dateOfBirth"])
        
        # Fill phone number
        if "phoneNumber" in contact_data:
            fill_text_field(nova, "Phone Number", contact_data["phoneNumber"])
        
        # Fill years as landlord
        if "numberOfYearsAsLandlord" in contact_data:
            fill_text_field(nova, "Years as Landlord", str(contact_data["numberOfYearsAsLandlord"]))
        
        # Handle joint insured checkbox
        if "jointInsured" in contact_data:
            handle_checkbox(nova, "Joint Insured", contact_data["jointInsured"])
            
            # If joint insured is checked, fill the joint insured person name
            if contact_data["jointInsured"] and "jointInsuredPersonName" in contact_data:
                time.sleep(1)  # Wait for conditional field to appear
                fill_text_field(nova, "Joint Insured Person Name", contact_data["jointInsuredPersonName"])
        
        # Move to next section
        return click_next_button(nova)
        
    except Exception as e:
        logger.exception(f"Error filling Contact Details section: {e}")
        return False

# Placeholder for automate_hard_form - will be expanded later

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
    logger.info("Starting hard form automation")
    
    # Start with contact details section
    if "contact" in form_data:
        if not fill_contact_details(nova, form_data["contact"]):
            logger.error("Failed to fill Contact Details section")
            return False, None
    
    # More sections will be implemented in subsequent steps
    
    logger.warning("Hard form automation partially implemented")
    return False, None