"""
Business Info section handler with comprehensive section verification for the Asteroid Form Challenge.
Responsible for filling all fields in the Business Info section and verifying the entire section.
"""

import logging
import os
import sys
import time
from typing import List, Dict, Any, Tuple
from nova_act import NovaAct
from field_detection import field_exists, get_form_label
from field_dependencies import should_process_field
from fill_fields import (
    fill_text_field,
    fill_date_field,
    select_dropdown_option,
    fill_checkbox,
    fill_address_fields
)
from utils_final import load_json_data
from navigation import click_button, navigate_to_section
from config import FIELD_TYPES
from verify3 import verify_field, verify_section
from error_handler import retry_failed_fields, navigate_to_next_section

# Initialize logger
logger = logging.getLogger("nova_form_automation")

def handle_business_info(nova: NovaAct, form_data: dict) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Handle the Business Info section of the form with comprehensive verification.
    
    Args:
        nova: NovaAct instance
        form_data: Dictionary containing form data
        
    Returns:
        Tuple[bool, List[Dict[str, Any]]]: 
            - Boolean success status
            - List of failed fields with details for targeted verification
    """
    logger.info("Processing Business Info section with comprehensive verification")
    section_name = "Business Info"
    
    # Extract business info data
    if "business" not in form_data:
        logger.error("Business info data not found in form data")
        return False, []
    
    business_data = form_data["business"]
    success = True
    
    # Track failed fields during initial filling
    failed_fields = []
    
    # Process each field in the business data
    for key, value in business_data.items():
        # Special handling for address field which is a nested object
        if key == "address" and isinstance(value, dict):
            logger.info("Processing business address fields")
            address_success = fill_address_fields(nova, section_name, value)
            if not address_success:
                logger.warning("Failed to fill business address fields")
                success = False
                # Since address is a special case, we don't add it to failed_fields
            continue
        
        # Use centralized get_form_label function with section context
        label = get_form_label(key, section_name)
        
        # Check if field is in the mapping
        if key not in FIELD_TYPES:
            logger.warning(f"Field '{key}' not found in FIELD_TYPES configuration, skipping")
            continue
            
        # Get field type from configuration
        field_type = FIELD_TYPES[key]
        logger.info(f"Processing field '{label}' (key: {key}, type: {field_type}, value: {value})")
        
        # Check if field exists in the form
        if not field_exists(nova, label, section_name, field_type):
            logger.warning(f"Field '{label}' does not exist in the form, skipping")
            # Add to failed fields for later targeted verification
            failed_fields.append({
                "section": section_name,
                "json_section": "business",
                "key": key,
                "label": label,
                "expected_value": value,
                "field_type": field_type,
                "reason": "field_not_found"
            })
            success = False
            continue
        
        # Check if field should be processed based on dependencies
        if not should_process_field(business_data, key, section_name):
            logger.info(f"Skipping field '{label}' due to dependencies")
            continue
        
        # Fill field based on type with immediate verification and retry
        field_filled = False
        max_attempts = 2
        
        for attempt in range(max_attempts):
            if attempt > 0:
                logger.info(f"Immediate retry attempt {attempt+1} for field '{label}'")
            
            # Fill field based on type
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
            
            if not field_success:
                logger.error(f"Failed to fill field '{label}'")
                continue
            
            # Immediate verification after filling
            verification_success = verify_field(nova, label, value, field_type)
            if verification_success:
                logger.info(f"✅ Field '{label}' filled and verified successfully")
                field_filled = True
                break
            else:
                logger.warning(f"❌ Field '{label}' verification failed, will retry")
        
        if not field_filled:
            logger.warning(f"Could not fill field '{label}' correctly after {max_attempts} attempts")
            # Add to failed fields for later targeted verification
            failed_fields.append({
                "section": section_name,
                "json_section": "business",
                "key": key,
                "label": label,
                "expected_value": value,
                "field_type": field_type
            })
            success = False
    
    # Only verify fields that failed during initial filling
    if failed_fields:
        logger.info(f"Performing targeted verification of {len(failed_fields)} failed Business Info fields")
        still_failed_fields = verify_section(nova, section_name, form_data, specific_fields=failed_fields)
        
        if still_failed_fields:
            logger.warning(f"{len(still_failed_fields)} fields still failed after specialized verification")
        else:
            logger.info("All previously failed fields now verify successfully with specialized verification")
    else:
        logger.info("All Business Info fields verified successfully during initial filling")
    
    # After filling all fields, try to proceed to next section
    logger.info("Attempting to proceed to next section")
    next_success = click_button(nova, "Next")
    
    if not next_success:
        logger.warning("Failed to click Next button, will try clicking next section tab")
        
        # Use the error handler function to navigate to the next section
        nav_success = navigate_to_next_section(nova, section_name)
        
        if not nav_success:
            logger.error("Failed to navigate to next section")
            return False, failed_fields
    
    logger.info(f"Business Info section processed successfully")
    return success, failed_fields

# For testing
if __name__ == "__main__":
    from config import HARD_FORM_URL
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    
    try:
        # Load data
        # Look for hard_form_data.json in the parent directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        data_file = os.path.join(parent_dir, "hard_form_data.json")
        data = load_json_data(data_file)
        
        # Initialize Nova-ACT and navigate to the form
        with NovaAct(starting_page=HARD_FORM_URL) as nova:
            logger.info("Starting Business Info section test with comprehensive verification")
            
            # Directly navigate to the Business Info section
            logger.info("Attempting to navigate directly to Business Info section")
            if not navigate_to_section(nova, "Business Info"):
                logger.error("Failed to navigate to Business Info section")
                sys.exit(1)
                
            logger.info("Successfully navigated to Business Info section")
                
            # Now process Business Info section with verification
            success, failed_fields = handle_business_info(nova, data)
            
            if success:
                logger.info("✅ Business Info section processed successfully")
            else:
                logger.error("❌ Business Info section processed with errors")
                if failed_fields:
                    logger.warning(f"There were {len(failed_fields)} fields that failed verification")
            
    except Exception as e:
        logger.exception(f"Error in Business Info handler test: {e}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)