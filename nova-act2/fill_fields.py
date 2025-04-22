"""
Field filling utilities for Asteroid form automation.
Provides functions to fill various types of form fields using Nova-ACT.
"""

import logging
from nova_act import BOOL_SCHEMA
from date_helpers import detect_order, convert_date
from verify import verify_field

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
                f"Click in the center of '{label}' field textbox Fill '{value}'."
                # f" Scroll if necessary."
                # f" Stop scrolling if you see the header or footer."
            )
        nova.act(query, max_steps=5)
        
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
        query = (f"In the form, Find the checkbox labelled '{label}' and check it.")

        nova.act(query, max_steps=5) 

        query2 = (
            f"Is the checkbox '{label}' checked? "
            f"Answer true or false."
        )
        result = nova.act(query2, schema=BOOL_SCHEMA)

        if result.parsed_response:
            logger.info(f"Checkbox '{label}' is checked")
            return True
        else:
            
            logger.info(f"Checkbox '{label}' is not checked. Trying to check again")
            nova.act(query) 
            result = nova.act(query2, schema=BOOL_SCHEMA)

            if result.parsed_response:
                logger.info(f"Checkbox '{label}' is checked")
                return True
            else:
                logger.info(f"Checkbox '{label}' is not checked")
                return False


    else:
        query3 = (
            f"Is the checkbox '{label}' unchecked? "
            f"Answer true or false."
        )
        result = nova.act(query3, schema=BOOL_SCHEMA)
        
        if result.parsed_response:
            logger.info(f"Checkbox '{label}' is unchecked")
            return True
        else:
            query4 = (f"Find the checkbox labelled '{label}' and uncheck it.")
            nova.act(query4, max_steps=5)
            logger.info(f"Checkbox '{label}' is unchecked")
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
        nova.act(command, max_steps=5)
        
        pattern = "dd/mm/yyyy"
        flag = detect_order(nova, label, pattern)

        if not flag:
            logger.warning(f"Date order doesnt match expected format for '{label}'")
            return False
        
        formatted_date = convert_date(value)
        logger.info(f"Converted date format from {value} to {formatted_date}")
        
        command = f"Enter '{formatted_date}' into the date field '{label}'"
        nova.act(command, max_steps=5)
        
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
        nova.act(command, max_steps=5)
        
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
            nova.act(fallback_command, max_steps=5)
            
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

# def fill_address_fields(nova, section_label, address_data):
#     """
#     Fill a complete address block in the form.
#     """
#     logger = logging.getLogger("nova_form_automation")
#     logger.info(f"Filling address fields in {section_label} section")
    
#     success = True
    
#     # Define field mappings (JSON keys to form labels)
#     field_mappings = {
#         "addressLine1": "Address Line 1",
#         "addressLine2": "Address Line 2",
#         "addressLine3": "Address Line 3",
#         "city": "City",
#         "postcode": "Postcode"
#     }
    
#     try:
#         # First verify which fields exist in the form
#         available_fields = {}
#         for key, form_label in field_mappings.items():
#             if field_exists(nova, form_label, section_label):
#                 available_fields[key] = form_label
#             else:
#                 logger.info(f"Field '{form_label}' not found in form, skipping")
        
#         # Now fill only the available fields
#         for key, form_label in available_fields.items():
#             if key not in address_data:
#                 logger.info(f"Skipping {key} - not in address data")
#                 continue
                
#             value = address_data[key]
#             if not value:
#                 logger.info(f"Skipping {key} - empty value")
#                 continue
                
#             logger.info(f"Filling address field '{form_label}' with '{value}'")
#             field_success = fill_text_field(nova, form_label, value)
            
#             if not field_success:
#                 logger.warning(f"Failed to fill address field '{form_label}'")
#                 success = False
        
#         return success
            
#     except Exception as e:
#         logger.exception(f"Error filling address fields in {section_label}: {e}")
#         return False


def fill_address_fields(nova, section_label, address_data):
    """
    Fill a complete address block in the form with verification.
    
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
        bool: True if all detected fields were filled successfully
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Filling address fields in {section_label} section with verification")
    
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
            
            # Check if field exists in the form
            query = (
                f"Is there a placeholder '{form_label}' in an empty Address field textbox? "
                f"Answer true or false."
            )
            result = nova.act(query, schema=BOOL_SCHEMA)
            
            if not result.parsed_response:
                logger.warning(f"Address field '{form_label}' not found in form, skipping")
                continue
            
            # Try to fill with verification
            field_filled = False
            max_attempts = 2  # Maximum attempts for each address field
            
            for attempt in range(max_attempts):
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt} for address field '{form_label}'")
                
                # Fill the address field
                logger.info(f"Filling address field '{form_label}' with '{value}'")
                field_success = fill_text_field(nova, form_label, value)
                
                if not field_success:
                    logger.error(f"Failed to fill address field '{form_label}'")
                    continue  # Try again if filling failed
                
                # Verify the field was filled correctly
                logger.info(f"Verifying address field '{form_label}'")
                verification_success = verify_field(nova, form_label, value, "text")
                
                if verification_success:
                    logger.info(f"Verification successful for address field '{form_label}'")
                    field_filled = True
                    break  # Field successfully filled and verified
                else:
                    logger.warning(f"Verification failed for address field '{form_label}', will retry")
            
            # Update overall success status
            if not field_filled:
                logger.error(f"Failed to fill address field '{form_label}' after multiple attempts")
                success = False
        
        if success:
            logger.info(f"Successfully filled all detected address fields in {section_label}")
        else:
            logger.warning(f"Some address fields in {section_label} could not be filled")
            
        return success
            
    except Exception as e:
        logger.exception(f"Error filling address fields in {section_label}: {e}")
        return False