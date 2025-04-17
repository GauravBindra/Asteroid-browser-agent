#!/usr/bin/env python3
"""
Enhanced form field functions for Nova-ACT.

This module contains improved functions for handling difficult form fields
in the hard form, with robust fallback mechanisms and more specific field location strategies.
"""

import logging
import time
import re
import json
from collections import deque

def scroll_reset(nova, logger):
    """
    Perform a scroll reset to help the agent get unstuck.
    This changes the viewport context by scrolling away and back.
    
    Args:
        nova: NovaAct instance
        logger: Logger instance
        
    Returns:
        bool: True if successful
    """
    logger.info("Performing scroll reset to help agent get unstuck")
    
    try:
        # Scroll up to change context
        nova.act("Scroll all the way up to the top of the page", max_steps=20)
        time.sleep(1)
        
        # Then scroll back down to find our position again
        nova.act("Scroll down to find where you were working before", max_steps=20)
        time.sleep(1)
        
        logger.info("Scroll reset completed successfully")
        return True
    except Exception as e:
        logger.exception(f"Error during scroll reset: {e}")
        return False

def enhanced_fill_text_field(nova, label, value, max_retries=3, max_stuck_attempts=8):
    """
    Enhanced function to fill a text field in the form with improved field location strategies.
    Includes automatic scroll reset if the agent gets stuck in a loop and instructions
    to discard previous coordinates on each attempt to force fresh analysis.
    
    Args:
        nova: NovaAct instance
        label: Field label to look for
        value: Value to enter
        max_retries: Maximum number of retry attempts with different strategies
        max_stuck_attempts: Maximum number of attempts at same coordinates before triggering scroll reset
        
    Returns:
        bool: True if successful
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Filling text field '{label}' with value '{value}' using enhanced method")
    
    # Track coordinates to detect when the agent is stuck in a loop
    recent_coords = deque(maxlen=max_stuck_attempts)
    stuck_count = 0
    
    # Regular expression to extract coordinates from Nova-ACT error messages
    coords_pattern = re.compile(r'<box>([^<]+)</box>')
    
    # Try the standard approach first
    try:
        # Standard approach with precise targeting
        logger.info(f"Using standard approach with precise targeting for '{label}'")
        command = f"Find the field labeled '{label}', click precisely in the center of the input field, and enter '{value}'"
        nova.act(command, max_steps=40)  # Increased max_steps for complex fields
        
        # Brief pause to ensure the field is properly filled
        time.sleep(0.5)
        
        logger.info(f"Successfully filled '{label}' field using standard approach")
        return True
        
    except Exception as e:
        logger.warning(f"Standard approach failed for '{label}': {e}")
        error_str = str(e)
        
        # Extract coordinates if present in the error message
        coords_match = coords_pattern.search(error_str)
        if coords_match:
            coords = coords_match.group(1)
            recent_coords.append(coords)
            logger.info(f"Extracted coordinates from error: {coords}")
        
        # Proceed to fallback strategies
        for attempt in range(max_retries):
            logger.info(f"Trying fallback approach #{attempt+1} for '{label}'")
            
            # Multiple attempts for the current fallback strategy
            for sub_attempt in range(max_stuck_attempts * 2):  # Allow more attempts with resets
                try:
                    # Check if we're stuck in a loop by looking at recent coordinates
                    if len(recent_coords) >= max_stuck_attempts:
                        # Count how many recent attempts used the same coordinates
                        most_common_coord = max(set(recent_coords), key=recent_coords.count)
                        stuck_count = recent_coords.count(most_common_coord)
                        
                        # If we've tried the same coordinates too many times, trigger scroll reset
                        if stuck_count >= max_stuck_attempts:
                            logger.warning(f"Agent appears stuck on coordinates {most_common_coord} "
                                          f"after {stuck_count} similar attempts")
                            
                            # Try a scroll reset to change the context
                            if scroll_reset(nova, logger):
                                logger.info(f"Scroll reset successful, continuing with attempts")
                                # Clear the coordinates tracking after reset
                                recent_coords.clear()
                                stuck_count = 0
                    
                    # Add the "discard previous coordinates" instruction to EVERY fallback attempt
                    # This forces the agent to re-analyze the page on each attempt
                    discard_instruction = (
                        f"IMPORTANT: Discard any previous coordinates and assumptions. "
                        f"Look at the page with fresh eyes and re-examine the form layout. "
                    )
                    
                    # Select the appropriate fallback command based on attempt
                    if attempt == 0:
                        # Fallback 1: Look below the label with precise targeting
                        fallback_command = (
                            f"{discard_instruction} "
                            f"Find the label text '{label}' on the form. "
                            f"Look directly below this label for a text input field. "
                            f"Click precisely in the center of this text input field and enter the value '{value}'"
                        )
                    elif attempt == 1:
                        # Fallback 2: Look for placeholder text with precise targeting
                        fallback_command = (
                            f"{discard_instruction} "
                            f"Look for an input field near the text '{label}' that might have a placeholder. "
                            f"Click precisely in the center of this field and enter '{value}'"
                        )
                    else:
                        # Fallback 3: Use more aggressive scanning approach with precise targeting
                        fallback_command = (
                            f"{discard_instruction} "
                            f"Scan the form carefully for any field related to '{label}'. "
                            f"It might be a text input field, possibly with no visible label. "
                            f"When you find it, click precisely in the center of the input field and enter '{value}'. "
                            f"After entering the value, click somewhere else on the form to confirm."
                        )
                    
                    # Execute the fallback command
                    nova.act(fallback_command, max_steps=40)  # Increased max_steps for complex fields
                    
                    # Brief pause to ensure the field is properly filled
                    time.sleep(0.5)
                    
                    logger.info(f"Successfully filled '{label}' field using fallback approach #{attempt+1}")
                    return True
                    
                except Exception as fallback_error:
                    error_str = str(fallback_error)
                    logger.warning(f"Fallback sub-attempt #{sub_attempt+1} failed: {fallback_error}")
                    
                    # Extract coordinates from error message
                    coords_match = coords_pattern.search(error_str)
                    if coords_match:
                        coords = coords_match.group(1)
                        recent_coords.append(coords)
                        logger.info(f"Extracted coordinates from error: {coords}")
            
            logger.warning(f"All sub-attempts for fallback approach #{attempt+1} failed")
        
        # If we reach here, all approaches failed
        logger.error(f"All approaches failed to fill '{label}' field")
        return False

# Direct import of other utility functions that don't need enhancement
from form_automation_working import (
    handle_checkbox,
    click_button,
    wait_for_form_load,
    extract_result_code,
    submit_form
)