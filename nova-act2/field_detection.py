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

def field_exists(nova: NovaAct, label: str, current_tab: str) -> bool:
    """
    Check if a field with the given label exists in the current form tab.
    
    Args:
        nova: NovaAct instance
        label: Label text to look for
        current_tab: Name of the current form tab (e.g., "Contact Details")
        
    Returns:
        bool: True if field exists in the current tab
    """
    logger.info(f"Checking if field labeled '{label}' exists in the {current_tab} tab")
    
    try:
        # Simple direct question following Nova-ACT best practices
        # query = f"In the current {current_tab} section, is there a form field labeled '{label}'? Answer true or false."
        # query = (
        #     f"Is there an input element in {current_tab} section whose label or placeholder "
        #     f"includes '{label}'? Answer true or false."
        # )
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
        # print("555", result.response)
        # logger.info("555",result)
        # logger.info(result.matches_schema)
        # logger.info(result.parsed_response)

        # while result.matches_schema == False:
        #     result = nova.act(query, schema=BOOL_SCHEMA)

        if result.parsed_response:
            logger.info(f"Field labeled '{label}' found in {current_tab} tab")
            return True
        else:
            nova.act(f"Find '{label}' field. Scroll down if needed. Stop scrolling if you see the footer section containing terms like 'Resources' and 'Connect'.")
            result = nova.act(query, schema=BOOL_SCHEMA)

            if result.parsed_response:
                logger.info(f"Field labeled '{label}' found in {current_tab} tab")
                return True
            else:
                logger.info(f"Field labeled '{label}' not found in {current_tab} tab")
                nova.act(f"Find '{label}' field. Scroll down if needed. Stop scrolling if you see the Page Title 'Commercial Property Insurance Application'")
                result = nova.act(query, schema=BOOL_SCHEMA)

                if result.parsed_response:
                    logger.info(f"Field labeled '{label}' found in {current_tab} tab")
                    return True
                else:
                    logger.info(f"Field labeled '{label}' not found in {current_tab} tab")
                    return False

    except Exception as e:
        logger.exception(f"Error checking if field exists: {e}")
        return False