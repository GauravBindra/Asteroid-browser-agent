"""
Navigation utilities for Asteroid form automation.
Contains functions for navigating through forms, clicking buttons,
and handling section transitions.
"""

import logging
import time

def click_button(nova, label, max_attempts=2):
    """
    Click a button on the form with retry logic.
    
    Args:
        nova: NovaAct instance
        label: Button label or text
        max_attempts: Maximum number of attempts to click the button
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Clicking button '{label}'")
    
    for attempt in range(max_attempts):
        if attempt > 0:
            logger.info(f"Retry attempt {attempt+1} to click '{label}' button")
            
        try:
            # Different strategies for different attempts
            if attempt == 0:
                # First attempt: Standard approach
                query = (
                    f"Find and click the button labeled '{label}'."
                    # f" Scroll down or up if needed."
                )
                nova.act(query, max_steps=5)
            else:
                # Second attempt: Be more explicit about scrolling and targeting
                query = (
                    f"Scroll down until you can see a button labeled '{label}'."
                    f" Once you find it, click directly in the center of the button."
                )
                nova.act(query, max_steps=8)  # Allow more steps for thorough search
            
            # Allow time for the button click to take effect
            time.sleep(1)
            
            logger.info(f"Successfully clicked '{label}' button")
            return True
            
        except Exception as e:
            if attempt < max_attempts - 1:
                logger.warning(f"Error clicking '{label}' button on attempt {attempt+1}: {e}")
                # Wait a moment before retrying to allow for any UI updates
                time.sleep(1)
            else:
                # Final attempt failed
                logger.exception(f"Error clicking '{label}' button after {max_attempts} attempts: {e}")
                return False
    
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
            f"If you are not at the top then Scroll up till you see 'Commercial Property Insurance Application'. "
            f"Look at the navigation tabs at the top of the form. "
            f"Find the tab labeled '{section_name}' and click directly on it. "
        )
        nova.act(query, max_steps=5)
        
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
            nova.act(query, max_steps=5)
            
            # Wait for submission to process
            time.sleep(2)
            
            logger.info(f"Successfully clicked '{button_label}' button")
            return True
            
        except Exception as e:
            logger.debug(f"Button '{button_label}' not found or could not be clicked: {e}")
            continue
    
    logger.error("Failed to find and click any submit button")
    return False