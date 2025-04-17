#!/usr/bin/env python3
"""
Improved hard form automation functions with enhanced field handling.

This module incorporates the enhanced_fill_text_field function for better handling
of difficult form fields, particularly focused on the Joint Insured Person Name field
and improved verification to prevent premature navigation.

Following our step-by-step implementation plan, this version includes:
1. Basic skeleton
2. select_dropdown_option() function 
3. fill_date_field() function
4. navigate_to_tab() function 
5. click_next_button() function
6. fill_contact_details() function with enhanced field handling
"""

import logging
import time
import re

# Import functions from the easy form automation module
from form_automation_working import (
    handle_checkbox,
    click_button,
    wait_for_form_load,
    extract_result_code,
    submit_form
)

# Import the enhanced text field function
from enhanced_field_functions import enhanced_fill_text_field

# Core utility functions for hard form - optimized for speed and reliability

def select_dropdown_option(nova, label, value):
    """
    Select an option from a dropdown field in the form - simplified approach.
    
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
        # Simpler command without extra clicks - following official examples
        command = f"Find the dropdown field labeled '{label}' and select '{value}'"
        nova.act(command)
        
        logger.info(f"Successfully selected '{value}' for '{label}' dropdown")
        return True
        
    except Exception as e:
        logger.exception(f"Error selecting '{value}' for '{label}' dropdown: {e}")
        
        # Fallback approach if the primary method fails
        try:
            logger.info(f"Trying fallback approach for dropdown '{label}'")
            
            fallback_command = (
                f"Find the field labeled '{label}', click on it, clear any existing text, "
                f"and enter '{value}'"
            )
            nova.act(fallback_command)
            
            logger.info(f"Fallback dropdown selection completed")
            return True
            
        except Exception as fallback_error:
            logger.exception(f"Dropdown fallback also failed: {fallback_error}")
            return False

def fill_date_field(nova, label, value):
    """
    Fill a date field in the form - simplified approach.
    
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
        
        # Simpler command without extra clicks - following official examples
        command = f"Find the date field labeled '{label}' and enter '{formatted_date}'"
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
                
                command = f"Find the date field labeled '{label}' and enter '{alt_formatted_date}'"
                nova.act(command)
                
                logger.info(f"Alternative date format attempt completed")
                return True
        except Exception as fallback_error:
            logger.exception(f"Date field fallback also failed: {fallback_error}")
            
        return False

# Navigation functions for multi-section hard form

def navigate_to_tab(nova, tab_name, check_current=True):
    """
    Navigate directly to a specific tab/section in the hard form.
    
    Args:
        nova: NovaAct instance
        tab_name: Name of the tab to navigate to 
                 (Options: "Contact Details", "Business Info", "Premises Details",
                  "Security & Safety", "Coverage Options")
        check_current: Whether to check if we're already on the requested tab
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Navigating to tab: '{tab_name}'")
    
    # If check_current is enabled, first check if we're already on this tab
    if check_current:
        try:
            from nova_act import BOOL_SCHEMA
            
            check_command = f"Am I already on the '{tab_name}' section of the form? Answer true or false."
            result = nova.act(check_command, schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                logger.info(f"Already on the '{tab_name}' tab, no navigation needed")
                return True
                
        except Exception as check_e:
            logger.warning(f"Error checking current tab: {check_e}, proceeding with navigation")
    
    try:
        # Simple, direct command - following official examples
        command = f"Click on the tab labeled '{tab_name}' at the top of the form"
        nova.act(command)
        
        # Brief pause to ensure the section is fully loaded and interactive
        time.sleep(1)
        
        logger.info(f"Successfully navigated to '{tab_name}' tab")
        return True
        
    except Exception as e:
        logger.exception(f"Error navigating to '{tab_name}' tab: {e}")
        
        # Fallback approach if the primary method fails
        try:
            logger.info(f"Trying fallback approach for navigating to '{tab_name}'")
            
            # More detailed instructions for fallback
            fallback_command = (
                f"Scroll to the top of the page to see the navigation tabs. "
                f"Find and click on the tab labeled '{tab_name}'"
            )
            nova.act(fallback_command)
            
            logger.info(f"Fallback navigation to '{tab_name}' tab completed")
            return True
            
        except Exception as fallback_error:
            logger.exception(f"Fallback navigation also failed: {fallback_error}")
            return False

def click_next_button(nova):
    """
    Click the Next button to proceed to the next section of the form.
    
    Args:
        nova: NovaAct instance
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Clicking Next button to proceed to next section")
    
    try:
        # Simple, direct command - following official examples
        command = "Scroll down and click the blue 'Next' button at the bottom of the form"
        nova.act(command)
        
        # Brief pause to allow for page transition
        time.sleep(2)
        
        logger.info("Successfully clicked Next button")
        return True
        
    except Exception as e:
        logger.exception(f"Error clicking Next button: {e}")
        
        # Fallback approach if the primary method fails
        try:
            logger.info("Trying fallback approach for clicking Next button")
            
            # More detailed instructions for fallback
            fallback_command = (
                "Scroll all the way to the bottom of the current form section. "
                "Find and click the blue button labeled 'Next'"
            )
            nova.act(fallback_command)
            
            # Additional wait after fallback
            time.sleep(2)
            
            logger.info("Fallback click Next button completed")
            return True
            
        except Exception as fallback_error:
            logger.exception(f"Fallback Next button click also failed: {fallback_error}")
            return False

# Section handler functions - implemented according to our step-by-step plan

def fill_contact_details(nova, contact_data, force_navigation=False):
    """
    Fill the Contact Details section of the hard form using enhanced field handling.
    
    Args:
        nova: NovaAct instance
        contact_data: Dictionary containing contact section data
        force_navigation: Force navigation to Contact Details tab even if not needed
        
    Returns:
        bool: True if successful and proceeded to next section
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Filling Contact Details section with enhanced field handling")
    
    try:
        # The form opens on Contact Details by default, so only navigate if forced
        # or if we're coming back to this section from elsewhere
        if force_navigation:
            if not navigate_to_tab(nova, "Contact Details"):
                logger.warning("Failed to navigate to Contact Details tab")
        
        # Fill in the title field (dropdown)
        if "title" in contact_data:
            if not select_dropdown_option(nova, "Title", contact_data["title"]):
                logger.warning("Failed to select title")
        
        # Fill in first name (text field) - using enhanced function
        if "firstName" in contact_data:
            if not enhanced_fill_text_field(nova, "First Name", contact_data["firstName"]):
                logger.warning("Failed to fill first name")
        
        # Fill in last name (text field) - using enhanced function
        if "lastName" in contact_data:
            if not enhanced_fill_text_field(nova, "Last Name", contact_data["lastName"]):
                logger.warning("Failed to fill last name")
        
        # Fill in date of birth (date field)
        if "dateOfBirth" in contact_data:
            if not fill_date_field(nova, "Date of Birth", contact_data["dateOfBirth"]):
                logger.warning("Failed to fill date of birth")
        
        # Fill in phone number (text field) - using enhanced function
        if "phoneNumber" in contact_data:
            if not enhanced_fill_text_field(nova, "Phone Number", contact_data["phoneNumber"]):
                logger.warning("Failed to fill phone number")
        
        # Handle joint insured checkbox
        if "jointInsured" in contact_data:
            if not handle_checkbox(nova, "Joint Insured", contact_data["jointInsured"]):
                logger.warning("Failed to handle joint insured checkbox")
            
            # Fill in joint insured name if the checkbox is checked - using enhanced function with higher retry count
            if contact_data["jointInsured"] and "jointInsuredPersonName" in contact_data:
                if not enhanced_fill_text_field(nova, "Joint Insured Person Name", contact_data["jointInsuredPersonName"], max_retries=5):
                    logger.warning("Failed to fill joint insured person name despite multiple attempts")
                    
                    # Special fallback for this troublesome field
                    try:
                        logger.info("Trying special fallback for Joint Insured Person Name field")
                        
                        special_command = (
                            "The Joint Insured Person Name field appears below the Joint Insured checkbox. "
                            "Look carefully for this field - it should be a text input field that appears "
                            "only when the Joint Insured checkbox is checked. "
                            f"Click directly on this field and carefully type '{contact_data['jointInsuredPersonName']}'. "
                            "After entering the text, click elsewhere on the form to ensure it is saved."
                        )
                        nova.act(special_command)
                        
                        logger.info("Special fallback for Joint Insured Person Name field completed")
                    except Exception as special_error:
                        logger.exception(f"Special fallback for Joint Insured Person Name field failed: {special_error}")
        
        # Fill in number of years as landlord (text field) - using enhanced function
        if "numberOfYearsAsLandlord" in contact_data:
            if not enhanced_fill_text_field(nova, "Number of Years as Landlord", str(contact_data["numberOfYearsAsLandlord"])):
                logger.warning("Failed to fill number of years as landlord")
        
        # Improved verification step that doesn't navigate away
        logger.info("Verifying all Contact Details fields are filled correctly")
        verification_command = (
            "Check the current Contact Details section of the form only. "
            "DO NOT click any navigation buttons or tabs. "
            "Verify that all required fields are filled correctly: "
            "Title, First Name, Last Name, Date of Birth, Phone Number, "
            "Joint Insured checkbox, and if checked, Joint Insured Person Name, "
            "and Number of Years as Landlord. "
            "If any field is empty or incorrect, report which fields need attention "
            "but do not navigate away from this section or click any buttons."
        )
        nova.act(verification_command)
        
        # Click Next to proceed to the next section
        if not click_next_button(nova):
            logger.error("Failed to click Next button after filling Contact Details")
            return False
        
        logger.info("Successfully completed Contact Details section and moved to next section")
        return True
        
    except Exception as e:
        logger.exception(f"Error filling Contact Details section: {e}")
        return False

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