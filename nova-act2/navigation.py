"""
Navigation utilities for Asteroid form automation.
Contains functions for navigating through forms, clicking buttons,
and handling section transitions.
"""

import logging
import time

def click_button(nova, label):
    """
    Click a button on the form.
    
    Args:
        nova: NovaAct instance
        label: Button label or text
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Clicking button '{label}'")
    
    try:
        # Use Nova-ACT's natural language capability to click the button
        query = (
            f"Find and click the button labeled '{label}'."
            f" Scroll down if necessary."
            f" Stop scrolling if you see the footer."
        )
        nova.act(query)
        
        # Allow time for the button click to take effect
        time.sleep(1)
        
        logger.info(f"Successfully clicked '{label}' button")
        return True
        
    except Exception as e:
        logger.exception(f"Error clicking '{label}' button: {e}")
        return False

def navigate_to_section(nova, section_name):
    """
    Navigate to a specific section of the form.
    
    Args:
        nova: NovaAct instance
        section_name: Name of the section to navigate to
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Navigating to section '{section_name}'")
    
    try:
        # Try to navigate to the section using Nova-ACT's understanding
        query = (
            f"Find and navigate to the section labeled '{section_name}'."
            f" This might involve clicking on a tab, link, or button."
            f" Scroll if necessary to find it."
        )
        nova.act(query)
        
        # Allow time for navigation to complete
        time.sleep(1)
        
        logger.info(f"Successfully navigated to section '{section_name}'")
        return True
        
    except Exception as e:
        logger.exception(f"Error navigating to section '{section_name}': {e}")
        return False

def submit_form(nova):
    """
    Submit the form by finding and clicking the submit button.
    
    Args:
        nova: NovaAct instance
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Submitting form")
    
    submit_buttons = ["Submit", "Submit Form", "Complete", "Finish", "Submit Application"]
    
    # Try each possible submit button label
    for button_label in submit_buttons:
        try:
            logger.info(f"Trying to click '{button_label}' button")
            
            query = (
                f"Find and click the button labeled '{button_label}'."
                f" Scroll down to the bottom of the page if necessary."
                f" Stop scrolling if you see the footer."
            )
            nova.act(query)
            
            # Wait for submission to process
            time.sleep(2)
            
            logger.info(f"Successfully clicked '{button_label}' button")
            return True
            
        except Exception as e:
            logger.debug(f"Button '{button_label}' not found or could not be clicked: {e}")
            continue
    
    logger.error("Failed to find and click any submit button")
    return False