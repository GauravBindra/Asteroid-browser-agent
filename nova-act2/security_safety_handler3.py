"""
Security & Safety section handler with comprehensive verification for the Asteroid Form Challenge.
Responsible for filling all fields in the Security & Safety section and verifying they're filled correctly.
"""

import logging
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
    fill_checkbox
)
from utils_final import load_json_data
from navigation import click_button, navigate_to_section
from config import FIELD_TYPES
from verify3 import verify_field, verify_section
from error_handler import retry_failed_fields, navigate_to_next_section

# Initialize logger
logger = logging.getLogger("nova_form_automation")

def handle_security_safety(nova: NovaAct, form_data: dict) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Handle the Security & Safety section of the form with comprehensive verification.
    
    Args:
        nova: NovaAct instance
        form_data: Dictionary containing form data
        
    Returns:
        Tuple[bool, List[Dict[str, Any]]]: 
            - Boolean success status
            - List of failed fields with details for targeted verification
    """
    logger.info("Processing Security & Safety section with comprehensive verification")
    section_name = "Security & Safety"
    
    # Extract security details data
    if "security" not in form_data:
        logger.error("Security details data not found in form data")
        return False
    
    security_data = form_data["security"]
    success, failed_fields = process_security_fields(nova, security_data, section_name)
    
    # Only verify fields that failed during initial filling
    if failed_fields:
        logger.info(f"Performing targeted verification of {len(failed_fields)} failed Security & Safety fields")
        still_failed_fields = verify_section(nova, section_name, form_data, specific_fields=failed_fields)
        
        if still_failed_fields:
            logger.warning(f"{len(still_failed_fields)} fields still failed after specialized verification")
        else:
            logger.info("All previously failed fields now verify successfully with specialized verification")
    else:
        logger.info("All Security & Safety fields verified successfully during initial filling")
    
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
    
    logger.info(f"Security & Safety section processed successfully")
    return success, failed_fields

def process_security_fields(nova: NovaAct, security_data: dict, section_name: str) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Process the security fields in the Security & Safety section with immediate verification.
    
    Args:
        nova: NovaAct instance
        security_data: Dictionary containing security data
        section_name: Name of the current section
        
    Returns:
        Tuple[bool, List[Dict[str, Any]]]: 
            - Boolean success status
            - List of failed fields with details for targeted verification
    """
    logger.info("Processing security fields with verification")
    success = True
    failed_fields = []  # Track fields that failed to fill or verify
    
    # Process each field in the security data
    for key, value in security_data.items():
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
                "json_section": "security",
                "key": key,
                "label": label,
                "expected_value": value,
                "field_type": field_type,
                "reason": "field_not_found"
            })
            success = False
            continue
        
        # Check if field should be processed based on dependencies
        if not should_process_field(security_data, key, section_name):
            logger.info(f"Skipping field '{label}' due to dependencies")
            continue
        
        # Fill field with immediate verification and retry
        field_filled = False
        max_attempts = 2  # Maximum number of attempts to fill a field
        
        for attempt in range(max_attempts):
            if attempt > 0:
                logger.info(f"Immediate retry attempt {attempt+1} for field '{label}'")
            
            # Fill the field
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
            
            # Verify the field was filled correctly
            logger.info(f"Verifying field '{label}'")
            verification_success = verify_field(nova, label, value, field_type)
            
            if verification_success:
                logger.info(f"✅ Field '{label}' filled and verified successfully")
                field_filled = True
                break
            else:
                logger.warning(f"❌ Field '{label}' verification failed, will retry")
        
        if not field_filled:
            logger.warning(f"Could not fill field '{label}' correctly after {max_attempts} attempts")
            
            # Special consideration for dependent fields
            # If this is a parent field (like CCTV Installed checkbox),
            # its dependent fields might not appear if it fails
            if key in ["cctv", "intruderAlarm", "requireTerrorismCover"]:
                logger.error(f"Failed to fill a critical checkbox '{label}', dependent fields may not appear")
            
            # Add to failed fields for later targeted verification
            failed_fields.append({
                "section": section_name,
                "json_section": "security",
                "key": key,
                "label": label,
                "expected_value": value,
                "field_type": field_type
            })
            success = False
    
    return success, failed_fields

# For testing
if __name__ == "__main__":
    import os
    from config import HARD_FORM_URL
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    
    try:
        # Load data from hard_form_data_actual.json first, fallback to hard_form_data.json
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(script_dir, "hard_form_data_actual.json")
        
        # Check if the file exists in current directory, otherwise try parent directory
        if not os.path.exists(data_file):
            logger.info(f"File not found at {data_file}, checking parent directory")
            parent_dir = os.path.dirname(script_dir)
            data_file = os.path.join(parent_dir, "hard_form_data_actual.json")
            
            # If still not found, fall back to hard_form_data.json
            # if not os.path.exists(data_file):
            #     logger.warning("hard_form_data_actual.json not found, falling back to hard_form_data.json")
            #     data_file = os.path.join(script_dir, "hard_form_data.json")
            #     if not os.path.exists(data_file):
            #         data_file = os.path.join(parent_dir, "hard_form_data.json")
        
        logger.info(f"Loading data from: {data_file}")
        data = load_json_data(data_file)
        
        # Initialize Nova-ACT and navigate to the form
        with NovaAct(starting_page=HARD_FORM_URL) as nova:
            # Set viewport size
            try:
                # nova.page.set_viewport_size({"width": 2000, "height": 5000})
                logger.info("Browser viewport size set to 2000x5000")
            except Exception as e:
                logger.warning(f"Could not set viewport size: {e}")
            
            # Navigate to the Security & Safety section
            logger.info("Navigating to Security & Safety section")
            if not navigate_to_section(nova, "Security & Safety"):
                logger.error("Failed to navigate to Security & Safety section")
                sys.exit(1)
            
            # Process the section
            success, failed_fields = handle_security_safety(nova, data)
            
            if success:
                logger.info("✅ Security & Safety section processed successfully")
            else:
                logger.error("❌ Security & Safety section processed with errors")
                if failed_fields:
                    logger.warning(f"There were {len(failed_fields)} fields that failed verification")
            
            # Wait to observe results
            time.sleep(5)
            
    except Exception as e:
        logger.exception(f"Error in Security & Safety handler test: {e}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)