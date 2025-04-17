#!/usr/bin/env python3
"""
Improved hard form automation functions with structured verification and recovery.

This module incorporates a structured verification approach with JSON schema
and an intelligent recovery loop for missing fields. It addresses the coordinate
mismatch issues between filling and verification phases.

Following our step-by-step implementation plan, this version includes:
1. All functionality from hard_form_automation9.py
2. Added structured verification with schema
3. Added intelligent recovery loop for missing fields
"""

import logging
import time
import re
import json

# Import functions from the easy form automation module
from form_automation_working import (
    handle_checkbox,
    click_button,
    wait_for_form_load,
    extract_result_code,
    submit_form
)

# Import the enhanced text field function and scroll reset
from enhanced_field_functions import enhanced_fill_text_field, scroll_reset

# Import BOOL_SCHEMA from Nova-ACT
from nova_act import BOOL_SCHEMA

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
    logger.info("Attempting to click the Next button")
    
    try:
        # Click the Next button with optimized instructions
        command = "Find and click the Next button to proceed to the next section"
        nova.act(command)
        
        # Brief pause to ensure the next section is loaded
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
                "Scroll to the bottom of the form to find the navigation buttons. "
                "Find and click on the button labeled 'Next'"
            )
            nova.act(fallback_command)
            
            # Brief pause to ensure the next section is loaded
            time.sleep(2)
            
            logger.info("Fallback Next button click completed")
            return True
            
        except Exception as fallback_error:
            logger.exception(f"Fallback Next button click also failed: {fallback_error}")
            
            # Final attempt with more flexible targeting
            try:
                logger.info("Trying final approach for clicking Next button")
                
                final_command = "Look for any button at the bottom of the form that would advance to the next section. It might be labeled 'Next', 'Continue', or 'Proceed'. Click on this button."
                nova.act(final_command)
                
                time.sleep(2)
                
                logger.info("Final Next button click attempt completed")
                return True
                
            except Exception as final_error:
                logger.exception(f"Final Next button click attempt also failed: {final_error}")
                return False

# Section handler functions - implemented with structured verification and recovery

def verify_contact_fields(nova):
    """
    Verify all Contact Details fields using a structured schema approach.
    
    Args:
        nova: NovaAct instance
        
    Returns:
        dict: Verification results with status and missing fields
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Performing structured verification of Contact Details fields")
    
    try:
        # Define verification schema for structured response
        verification_schema = {
            "type": "object",
            "properties": {
                "allFieldsFilled": {"type": "boolean"},
                "missingFields": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["allFieldsFilled", "missingFields"]
        }
        
        # Reset scroll position for consistent viewport
        scroll_reset(nova, logger)
        
        # Structured verification command
        verification_command = (
            "Check the Contact Details section and report ONLY. "
            "Verify all fields: Title, First Name, Last Name, Date of Birth, Phone Number, "
            "Joint Insured checkbox, Joint Insured Person Name (if checkbox checked), "
            "and Number of Years as Landlord. "
            "Return a JSON object with 'allFieldsFilled' (boolean) and 'missingFields' (array of field names). "
            "DO NOT attempt to fix anything yourself."
        )
        
        # Get structured response
        verification_result = nova.act(verification_command, schema=verification_schema)
        
        # Process structured response
        if verification_result.matches_schema:
            data = verification_result.parsed_response
            all_filled = data.get("allFieldsFilled", False)
            missing_fields = data.get("missingFields", [])
            
            if all_filled:
                logger.info("Verification confirms all Contact Details fields are correctly filled")
            else:
                logger.warning(f"Verification found {len(missing_fields)} missing fields: {missing_fields}")
            
            return {
                "success": True,
                "allFieldsFilled": all_filled,
                "missingFields": missing_fields
            }
        else:
            logger.warning("Verification response did not match schema, treating as failure")
            return {
                "success": False,
                "allFieldsFilled": False,
                "missingFields": []
            }
            
    except Exception as e:
        logger.exception(f"Error during structured verification: {e}")
        return {
            "success": False,
            "allFieldsFilled": False,
            "missingFields": []
        }

def fill_contact_details(nova, contact_data, force_navigation=False):
    """
    Fill the Contact Details section of the hard form using enhanced field handling
    with structured verification and intelligent recovery.
    
    Args:
        nova: NovaAct instance
        contact_data: Dictionary containing contact section data
        force_navigation: Force navigation to Contact Details tab even if not needed
        
    Returns:
        bool: True if successful and proceeded to next section
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Filling Contact Details section with structured verification and recovery")
    
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
                logger.info("Attempting to fill Joint Insured Person Name with special targeting")
                # First scroll reset to ensure a consistent viewport
                scroll_reset(nova, logger)
                
                # Try with direct targeting command instead of enhanced_fill_text_field
                try:
                    special_command = (
                        "The Joint Insured Person Name field appears right after the Joint Insured checkbox. "
                        "First scroll down to make sure you can see this field clearly. "
                        "Look carefully for the field labeled 'Joint Insured Person Name' - it should be visible "
                        "since the Joint Insured checkbox is checked. "
                        f"Click directly on this field and carefully type '{contact_data['jointInsuredPersonName']}'. "
                        "After entering the text, click elsewhere on the form to ensure it is saved."
                    )
                    nova.act(special_command, max_steps=60)  # Increased max_steps for this difficult field
                    
                    logger.info("Special command for Joint Insured Person Name field completed")
                except Exception as special_error:
                    logger.exception(f"Special command for Joint Insured Person Name field failed: {special_error}")
                    
                    # Only try enhanced_fill_text_field as fallback
                    if not enhanced_fill_text_field(nova, "Joint Insured Person Name", contact_data["jointInsuredPersonName"], max_retries=5):
                        logger.warning("Failed to fill joint insured person name despite multiple attempts")
        
        # Fill in number of years as landlord (text field) - using enhanced function
        if "numberOfYearsAsLandlord" in contact_data:
            if not enhanced_fill_text_field(nova, "Number of Years as Landlord", str(contact_data["numberOfYearsAsLandlord"])):
                logger.warning("Failed to fill number of years as landlord")
        
        # NEW: Structured verification with recovery loop
        # Maximum number of recovery cycles to prevent infinite loops
        max_recovery_cycles = 2
        for recovery_cycle in range(max_recovery_cycles):
            # Perform structured verification
            verification_result = verify_contact_fields(nova)
            
            if not verification_result["success"]:
                logger.warning("Verification failed, cannot determine field status")
                break
                
            # If all fields filled, we're done
            if verification_result["allFieldsFilled"]:
                logger.info("All Contact Details fields verified as correctly filled")
                break
                
            # Handle missing fields with intelligent recovery
            missing_fields = verification_result["missingFields"]
            logger.warning(f"Recovery cycle {recovery_cycle+1}: Found {len(missing_fields)} missing fields: {missing_fields}")
            
            # Reset viewport before recovery
            scroll_reset(nova, logger)
            
            # Field name to data key mapping
            field_map = {
                "Title": "title",
                "First Name": "firstName",
                "Last Name": "lastName",
                "Date of Birth": "dateOfBirth",
                "Phone Number": "phoneNumber",
                "Joint Insured": "jointInsured",
                "Joint Insured Person Name": "jointInsuredPersonName",
                "Number of Years as Landlord": "numberOfYearsAsLandlord"
            }
            
            # Apply recovery for each missing field
            for field_name in missing_fields:
                # Get data key for this field
                data_key = field_map.get(field_name)
                
                if data_key and data_key in contact_data:
                    logger.info(f"Applying recovery for field: {field_name}")
                    
                    # Use the appropriate fill method based on field type
                    if field_name == "Title":
                        select_dropdown_option(nova, field_name, contact_data[data_key])
                    elif field_name == "Date of Birth":
                        fill_date_field(nova, field_name, contact_data[data_key])
                    elif field_name == "Joint Insured":
                        handle_checkbox(nova, field_name, contact_data[data_key])
                    else:
                        # Use enhanced fill with increased retries for recovery
                        enhanced_fill_text_field(
                            nova, 
                            field_name, 
                            str(contact_data[data_key]), 
                            max_retries=5,  # More retries for recovery
                            max_stuck_attempts=5  # Lower threshold for scroll reset
                        )
                else:
                    logger.warning(f"No data available for missing field: {field_name}")
            
            # If this was the last recovery cycle, log a warning but continue
            if recovery_cycle == max_recovery_cycles - 1:
                logger.warning(f"Reached maximum recovery cycles ({max_recovery_cycles}), continuing anyway")
        
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
