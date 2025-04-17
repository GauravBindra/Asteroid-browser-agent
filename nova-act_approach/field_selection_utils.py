#!/usr/bin/env python3
"""
Utility functions for robust field selection in web forms.

This module provides specialized functions for selecting form fields
with verification to ensure proper selection before data entry.
"""

import logging
import time
import random
from nova_act import NovaAct
from nova_act import BOOL_SCHEMA

def select_form_field(nova, field_label, max_attempts=5, verify_selection=True):
    """
    Attempt to click and select a form field by its label, with multiple
    strategies and verification to ensure proper selection.
    
    Args:
        nova: NovaAct instance
        field_label: Label text for the field to select
        max_attempts: Maximum number of attempts to make
        verify_selection: Whether to verify successful selection
        
    Returns:
        bool: True if field was successfully selected
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Attempting to select field: '{field_label}'")
    
    for attempt in range(max_attempts):
        logger.info(f"Selection attempt #{attempt+1}")
        
        # Use a slightly different strategy each time
        if attempt == 0:
            # First try the standard approach: look for label, then click input field below it
            command = (
                f"Find the label text '{field_label}' on the form. "
                f"Then look directly below this label for an input field or control. "
                f"Click precisely in the center of this input field."
            )
        elif attempt == 1:
            # Second attempt: scan form areas with more flexibility
            command = (
                f"Scan the form carefully for any field related to '{field_label}'. "
                f"Look near but below the text '{field_label}'. "
                f"Click precisely in the center of the input field or control, "
                f"avoiding any borders or edges."
            )
        elif attempt == 2:
            # Third attempt: try clicking on the label first then input field
            command = (
                f"First click directly on the text label '{field_label}'. "
                f"Then look for an input field that appears highlighted or activated. "
                f"Click in the center of that input field."
            )
        elif attempt == 3:
            # Fourth attempt: use form structure knowledge
            command = (
                f"Analyze the form's structure. Fields typically have labels to their left or above them. "
                f"Find where '{field_label}' appears on the form. "
                f"Then look for a rectangular input area associated with this label. "
                f"Click precisely in the center of that input area, avoiding borders."
            )
        else:
            # Final attempt: try a more exhaustive scan
            command = (
                f"Carefully examine the entire visible form for '{field_label}'. "
                f"When found, look at what appears to be the input field for this label. "
                f"Using your best judgment, click in what appears to be the center of the "
                f"input field, far from any borders or edges."
            )
        
        try:
            # Execute the selection command
            nova.act(command, max_steps=30)
            
            # Brief pause to let the UI update
            time.sleep(0.5)
            
            # Verify selection if requested
            if verify_selection:
                # Create verification command to check if field is selected
                verify_command = (
                    f"Is the input field for '{field_label}' currently selected, "
                    f"active, or highlighted? Look for signs such as a highlighted border, "
                    f"a cursor blinking in the field, or any visual feedback indicating "
                    f"the field has focus. Answer true or false."
                )
                
                # Check if selection was successful
                verification = nova.act(verify_command, schema=BOOL_SCHEMA)
                if verification.matches_schema and verification.parsed_response:
                    logger.info(f"Successfully selected field '{field_label}' on attempt #{attempt+1}")
                    return True
                else:
                    logger.warning(f"Field selection verification failed on attempt #{attempt+1}")
            else:
                # If no verification requested, assume success
                logger.info(f"Field selection attempt #{attempt+1} completed without verification")
                return True
                
        except Exception as e:
            logger.warning(f"Error during selection attempt #{attempt+1}: {e}")
    
    # If we get here, all attempts failed
    logger.error(f"Failed to select field '{field_label}' after {max_attempts} attempts")
    return False

def fill_text_field_safely(nova, field_label, value, max_attempts=3):
    """
    Safely fill a text field by first selecting it properly and then entering text.
    
    Args:
        nova: NovaAct instance
        field_label: Label text for the field
        value: Value to enter in the field
        max_attempts: Maximum number of selection attempts
        
    Returns:
        bool: True if field was successfully filled
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Safely filling field '{field_label}' with value '{value}'")
    
    # First ensure the field is properly selected
    if not select_form_field(nova, field_label, max_attempts=max_attempts):
        logger.error(f"Could not properly select field '{field_label}'")
        return False
    
    try:
        # Now that we've confirmed the field is selected, type the value
        command = f"The field is now selected. Type '{value}' into it."
        nova.act(command, max_steps=20)
        
        # Brief pause to let the UI update
        time.sleep(0.5)
        
        # Verify text was entered
        verify_command = (
            f"Does the field labeled '{field_label}' now contain the value '{value}'? "
            f"Look at the text currently displayed in the field and compare it to '{value}'. "
            f"Answer true or false."
        )
        
        verification = nova.act(verify_command, schema=BOOL_SCHEMA)
        
        if verification.matches_schema and verification.parsed_response:
            logger.info(f"Successfully filled field '{field_label}' with '{value}'")
            return True
        else:
            logger.warning(f"Field '{field_label}' verification failed - text may not be entered correctly")
            return False
            
    except Exception as e:
        logger.exception(f"Error during text entry for field '{field_label}': {e}")
        return False

def select_dropdown_option_safely(nova, field_label, option_value, max_attempts=3):
    """
    Safely select an option from a dropdown - uses direct selection without
    requiring field highlighting first.
    
    Args:
        nova: NovaAct instance
        field_label: Label text for the dropdown
        option_value: Value to select
        max_attempts: Maximum number of selection attempts
        
    Returns:
        bool: True if option was successfully selected
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Safely selecting option '{option_value}' from dropdown '{field_label}'")
    
    for attempt in range(max_attempts):
        logger.info(f"Dropdown selection attempt #{attempt+1}")
        
        try:
            # Use a different strategy each time
            if attempt == 0:
                # First try the standard approach: direct dropdown selection
                command = (
                    f"Find the dropdown field labeled '{field_label}'. "
                    f"Click on it to open the dropdown menu. "
                    f"Select the option '{option_value}' from the dropdown menu. "
                    f"If no dropdown menu appears, try typing '{option_value}' directly."
                )
            elif attempt == 1:
                # Second attempt: click and type approach
                command = (
                    f"Find the dropdown field labeled '{field_label}'. "
                    f"Click on the dropdown to activate it, then type '{option_value}' "
                    f"and press Enter or Tab to confirm."
                )
            else:
                # Third attempt: more detailed guidance
                command = (
                    f"Look for a dropdown field or select element with the label '{field_label}'. "
                    f"First try clicking on the dropdown itself. Look for any arrow icons "
                    f"that might open the dropdown. Once clicked, either select '{option_value}' "
                    f"from the list that appears, or if no list appears, type '{option_value}' directly."
                )
            
            # Execute the dropdown selection command
            nova.act(command, max_steps=40)
            
            # Brief pause to let the UI update
            time.sleep(0.5)
            
            # Verify option was selected
            verify_command = (
                f"Does the dropdown field labeled '{field_label}' now show the selected value '{option_value}'? "
                f"Answer true or false."
            )
            
            verification = nova.act(verify_command, schema=BOOL_SCHEMA)
            
            if verification.matches_schema and verification.parsed_response:
                logger.info(f"Successfully selected option '{option_value}' from dropdown '{field_label}' on attempt #{attempt+1}")
                return True
            else:
                logger.warning(f"Dropdown '{field_label}' verification failed on attempt #{attempt+1}")
        
        except Exception as e:
            logger.exception(f"Error selecting option from dropdown '{field_label}' on attempt #{attempt+1}: {e}")
    
    # If we get here, all attempts failed
    logger.error(f"Failed to select option '{option_value}' from dropdown '{field_label}' after {max_attempts} attempts")
    return False

def handle_checkbox_safely(nova, checkbox_label, check_state, max_attempts=3):
    """
    Safely handle a checkbox by first selecting it properly and then setting to desired state.
    
    Args:
        nova: NovaAct instance
        checkbox_label: Label text for the checkbox
        check_state: Boolean indicating whether to check (True) or uncheck (False)
        max_attempts: Maximum number of selection attempts
        
    Returns:
        bool: True if checkbox was successfully set to desired state
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Safely setting checkbox '{checkbox_label}' to {'checked' if check_state else 'unchecked'}")
    
    # First check current state to see if action is needed
    try:
        check_command = f"Is the checkbox labeled '{checkbox_label}' currently checked? Answer true or false."
        check_result = nova.act(check_command, schema=BOOL_SCHEMA)
        
        if check_result.matches_schema:
            current_state = check_result.parsed_response
            
            # If already in desired state, no action needed
            if current_state == check_state:
                logger.info(f"Checkbox '{checkbox_label}' is already {'checked' if check_state else 'unchecked'}")
                return True
    except Exception as e:
        logger.warning(f"Error checking current state of checkbox '{checkbox_label}': {e}")
        # Continue anyway since we'll try to set it to the desired state
    
    # Select the checkbox
    if not select_form_field(nova, checkbox_label, max_attempts=max_attempts):
        logger.error(f"Could not properly select checkbox '{checkbox_label}'")
        return False
    
    try:
        # Click to toggle checkbox state
        action = "check" if check_state else "uncheck"
        command = f"The checkbox is now selected. Click on it to {action} it."
        nova.act(command, max_steps=20)
        
        # Brief pause to let the UI update
        time.sleep(0.5)
        
        # Verify checkbox state
        verify_command = (
            f"Is the checkbox labeled '{checkbox_label}' now {'checked' if check_state else 'unchecked'}? "
            f"Answer true or false."
        )
        
        verification = nova.act(verify_command, schema=BOOL_SCHEMA)
        
        if verification.matches_schema and verification.parsed_response == check_state:
            logger.info(f"Successfully {'checked' if check_state else 'unchecked'} checkbox '{checkbox_label}'")
            return True
        else:
            logger.warning(f"Checkbox '{checkbox_label}' verification failed - state may not be set correctly")
            return False
            
    except Exception as e:
        logger.exception(f"Error setting checkbox '{checkbox_label}' state: {e}")
        return False
