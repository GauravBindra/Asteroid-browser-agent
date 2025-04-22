#!/usr/bin/env python3
"""
Field detection utility for Nova-ACT form automation.

This module provides a simple function for detecting the presence of form fields
by their labels in the current form tab.
"""

import logging
from nova_act import BOOL_SCHEMA, NovaAct

# Initialize logger
logger = logging.getLogger("nova_form_automation")

def navigate_to_subsection(nova, section_name, subsection_name):
    """
    Navigate to a specific subsection within a section.
    
    Args:
        nova: NovaAct instance
        section_name: Main section name (e.g., "Premises Details")
        subsection_name: Subsection name to navigate to (e.g., "Construction Details")
        
    Returns:
        bool: True if successfully navigated to subsection
    """
    logger.info(f"Navigating to {subsection_name} subsection within {section_name}")
    
    # First check if the subsection header is already visible
    check_visible = nova.act(
        f"Is the '{subsection_name}' subsection header visible in the {section_name} section? "
        f"Answer true or false.", 
        schema=BOOL_SCHEMA
    )
    
    if check_visible.matches_schema and check_visible.parsed_response:
        logger.info(f"{subsection_name} subsection is already visible")
        return True
        
    # If not visible, explicitly navigate to it
    navigation_command = (
        f"In the {section_name} section, find and scroll to the '{subsection_name}' subsection header. "
        f"Make sure the subsection header is at the top portion of the screen."
    )
    
    try:
        nova.act(navigation_command, max_steps=3)
        
        # Verify we found the right subsection
        verify = nova.act(
            f"Can you see the '{subsection_name}' subsection heading now? Answer true or false.",
            schema=BOOL_SCHEMA
        )
        
        if verify.matches_schema and verify.parsed_response:
            logger.info(f"Successfully navigated to {subsection_name} subsection")
            return True
        else:
            logger.warning(f"Failed to navigate to {subsection_name} subsection")
            return False
            
    except Exception as e:
        logger.exception(f"Error navigating to {subsection_name} subsection: {e}")
        return False

def field_exists(nova: NovaAct, label: str, current_tab: str, field_type: str = None, subsection: str = None) -> bool:
    """
    Check if a field with the given label exists in the current form tab/subsection.
    
    Args:
        nova: NovaAct instance
        label: Label text to look for
        current_tab: Name of the current form tab (e.g., "Contact Details")
        field_type: Type of field to look for (e.g., "dropdown", "text", "checkbox")
        subsection: Name of the subsection within the tab (e.g., "Property Identity")
        
    Returns:
        bool: True if field exists in the current tab/subsection
    """
    if subsection:
        location = f"{subsection} subsection of {current_tab}"
        logger.info(f"Checking if '{field_type}' field labeled '{label}' exists in the {location}")
        
        # Make sure we're in the right subsection before checking for fields
        subsection_nav_success = navigate_to_subsection(nova, current_tab, subsection)
        if not subsection_nav_success:
            logger.warning(f"Could not navigate to {subsection} subsection, field detection may fail")
    else:
        location = f"{current_tab} tab"
        logger.info(f"Checking if '{field_type}' field labeled '{label}' exists {location}")
    
    try:
        # Include field type and subsection in query if provided
        if subsection and field_type:
            query = (
                f"Is there a {field_type} field labeled '{label}' in the {subsection} subsection of {current_tab}? "
                f"Answer true or false."
            )
        elif subsection:
            query = (
                f"Is there a field '{label}' in the {subsection} subsection of {current_tab}? "
                f"Answer true or false."
            )
        elif field_type:
            query = (
                f"Is there a {field_type} field labeled '{label}' in {current_tab} section? "
                f"Answer true or false."
            )
        else:
            query = (
                f"Is there a field '{label}' in {current_tab} section? "
                f"Answer true or false."
            )
#         query = (
#     f"Look at the {current_tab} section of the form carefully. "
#     f"Is there a field labeled '{label}' or similar visible anywhere? "
#     f"Consider all input fields, dropdowns, and checkboxes. Answer true or false."
# )
        result = nova.act(query, schema=BOOL_SCHEMA)

        location = f"{subsection} subsection of {current_tab}" if subsection else f"{current_tab} tab"

        if result.parsed_response:
            logger.info(f"{field_type if field_type else 'Field'} labeled '{label}' found in {location}")
            return True
        else:
            nova.act(f"Scroll down till you see the website footer. ",max_steps=3)
            result = nova.act(query, schema=BOOL_SCHEMA)

            if result.parsed_response:
                logger.info(f"{field_type if field_type else 'Field'} labeled '{label}' found in {location}")
                return True
            else:
                logger.info(f"{field_type if field_type else 'Field'} labeled '{label}' not found in {location}")
                nova.act(f"Scroll up till you see 'Commercial Property Insurance Application'.",max_steps=3)
                result = nova.act(query, schema=BOOL_SCHEMA)

                if result.parsed_response:
                    logger.info(f"{field_type if field_type else 'Field'} labeled '{label}' found in {location}")
                    return True
                else:
                    logger.info(f"{field_type if field_type else 'Field'} labeled '{label}' not found in {location}")
                    return False

    except Exception as e:
        logger.exception(f"Error checking if field exists: {e}")
        return False