"""
Field filling utilities for Asteroid form automation.
Provides functions to fill various types of form fields using Nova-ACT.
"""

import logging
from nova_act import BOOL_SCHEMA
from date_helpers import detect_order, convert_date

# ─── Field filling functions ────────────────────────────────────────────────────

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
        query = (
                f"In the form, Find the textbox of the'{label}' field and fill'{value}' into the field."
                # f" Scroll if necessary."
                # f" Stop scrolling if you see the header or footer."
            )
        nova.act(query)
        
        logger.info(f"Successfully filled '{label}' field")
        return True
        
    except Exception as e:
        logger.exception(f"Error filling '{label}' field: {e}")
        return False

def fill_checkbox(nova, label, should_check):
    """
    Handle a checkbox in the form - either check it or ensure it's unchecked.
    
    Args:
        nova: NovaAct instance
        label: Checkbox label to look for
        should_check: Whether the checkbox should be checked (True) or unchecked (False)
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    query = ( )
    if should_check:
        logger.info(f"Checking checkbox '{label}'")
        query = (f"In the form, Find the checkbox field '{label}' and check it.", 
                # f" Scroll if necessary.",
                # f" Stop scrolling if you see the header or footer."
                )
    else:
        logger.info(f"Ensuring checkbox '{label}' is unchecked")
        query = (f"Find and ensure the checkbox labeled '{label}' is clear or unchecked.", 
                f" Scroll if necessary.",
                f" Stop scrolling if you see the header or footer.")
    
    try:
        # Use Nova-ACT's natural language capability to handle the checkbox
        nova.act(query)
        
        logger.info(f"Successfully handled checkbox '{label}'")
        return True
        
    except Exception as e:
        logger.exception(f"Error handling checkbox '{label}': {e}")
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
        # Simpler command without extra clicks - following official examples
        command = f"Find the date field labeled '{label}'"
        nova.act(command)
        
        pattern = "dd/mm/yyyy"
        flag = detect_order(nova, label, pattern)

        if not flag:
            logger.warning(f"Date order doesnt match expected format for '{label}'")
            return False
        
        formatted_date = convert_date(value)
        logger.info(f"Converted date format from {value} to {formatted_date}")
        
        command = f"Enter '{formatted_date}' into the date field '{label}'"
        nova.act(command)
        
        logger.info(f"Successfully filled date field '{label}' with '{formatted_date}'")
        return True
        
    except Exception as e:
        logger.exception(f"Error filling date field '{label}': {e}")
        return False


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


def fill_address_fields(nova, section_label, address_data):
    """
    Fill a complete address block in the form.
    
    This function handles multi-field address entries, filling each component
    of the address (address lines, city, postcode) in sequence.
    
    Args:
        nova: NovaAct instance
        section_label: Section containing the address fields (e.g., "Contact Details")
        address_data: Dictionary containing address components:
                     {
                         "addressLine1": "42 Nebula Gardens",
                         "addressLine2": "Cosmic Quarter",
                         "addressLine3": "Starlight District",
                         "city": "Newcastle",
                         "postcode": "NE1 4XD"
                     }
        
    Returns:
        bool: True if all fields filled successfully
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Filling address fields in {section_label} section")
    
    # Track success of each field
    success = True
    
    # Define field mappings (JSON keys to form labels)
    field_mappings = {
        "addressLine1": "Address Line 1",
        "addressLine2": "Address Line 2",
        "addressLine3": "Address Line 3",
        "city": "City",
        "postcode": "Postcode"
    }
    
    try:
        # Fill each address field in sequence
        for key, form_label in field_mappings.items():
            # Skip if this field isn't in the data
            if key not in address_data:
                logger.info(f"Skipping {key} - not in address data")
                continue
                
            value = address_data[key]
            if not value:  # Skip empty values
                logger.info(f"Skipping {key} - empty value")
                continue
                
            # Full label might include section context
            full_label = form_label
            
            # Fill this field
            logger.info(f"Filling address field '{full_label}' with '{value}'")
            field_success = fill_text_field(nova, full_label, value)
            
            # Update overall success status
            if not field_success:
                logger.warning(f"Failed to fill address field '{full_label}'")
                success = False
        
        if success:
            logger.info(f"Successfully filled all address fields in {section_label}")
        else:
            logger.warning(f"Some address fields in {section_label} could not be filled")
            
        return success
            
    except Exception as e:
        logger.exception(f"Error filling address fields in {section_label}: {e}")
        return False