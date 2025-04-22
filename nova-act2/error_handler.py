#!/usr/bin/env python3
"""
Error handling utilities for the Asteroid Form Challenge.
Provides functions for recovering from form filling errors and retrying failed fields.
"""

import logging
from typing import List, Dict, Any
from nova_act import NovaAct
from fill_fields import (
    fill_text_field,
    fill_date_field,
    select_dropdown_option,
    fill_checkbox
)
from verify import verify_field
from navigation import navigate_to_section
from config import FORM_SECTIONS

# Initialize logger
logger = logging.getLogger("nova_form_automation")

def retry_failed_fields(nova: NovaAct, failed_fields: List[Dict[str, Any]]) -> bool:
    """
    Retry filling fields that failed verification.
    
    Args:
        nova: NovaAct instance
        failed_fields: List of dictionaries containing information about failed fields
        
    Returns:
        bool: True if any fields were successfully fixed, False otherwise
    """
    if not failed_fields:
        logger.info("No failed fields to retry")
        return True
        
    logger.info(f"Retrying {len(failed_fields)} failed fields")
    
    # Track if any fields were fixed
    any_fields_fixed = False
    
    for field_info in failed_fields:
        key = field_info["key"]
        label = field_info["label"]
        value = field_info["expected_value"]
        field_type = field_info["field_type"]
        
        # Handle address fields differently
        if field_info.get("is_address_field", False):
            logger.info(f"Retrying address field '{label}' with value '{value}'")
            field_success = fill_text_field(nova, label, str(value))
        else:
            # Regular field filling based on type
            logger.info(f"Retrying field '{label}' (type: {field_type}) with value '{value}'")
            
            if field_type == "text":
                field_success = fill_text_field(nova, label, str(value))
            elif field_type == "date":
                field_success = fill_date_field(nova, label, value)
            elif field_type == "dropdown":
                field_success = select_dropdown_option(nova, label, value)
            elif field_type == "checkbox":
                field_success = fill_checkbox(nova, label, value)
            else:
                logger.error(f"Unknown field type '{field_type}' for field '{label}'")
                field_success = False
        
        # Verify the field again after retrying
        if field_success:
            verification_success = verify_field(nova, label, value, field_type)
            if verification_success:
                logger.info(f"✅ Successfully fixed field '{label}'")
                any_fields_fixed = True
            else:
                logger.warning(f"❌ Field '{label}' still not verified correctly after retry")
        else:
            logger.error(f"Failed to retry field '{label}'")
    
    return any_fields_fixed

def navigate_to_next_section(nova: NovaAct, current_section: str) -> bool:
    """
    Navigate to the next section when the Next button fails.
    
    Args:
        nova: NovaAct instance
        current_section: The current section name
        
    Returns:
        bool: True if successfully navigated to the next section, False otherwise
    """
    logger.info(f"Attempting to navigate directly to the next section after '{current_section}'")
    
    # Find the next section to navigate to
    current_index = -1
    next_section = ""
    
    for i, section in enumerate(FORM_SECTIONS):
        if section == current_section:
            current_index = i
            break
    
    if current_index >= 0 and current_index < len(FORM_SECTIONS) - 1:
        next_section = FORM_SECTIONS[current_index + 1]
        
    if next_section:
        logger.info(f"Next section determined to be '{next_section}'")
        logger.info(f"Attempting to navigate directly to {next_section} section")
        nav_success = navigate_to_section(nova, next_section)
        
        if nav_success:
            logger.info(f"Successfully navigated to {next_section} section")
            return True
        else:
            logger.error(f"Failed to navigate to {next_section} section")
            return False
    else:
        logger.error("Could not determine next section")
        return False