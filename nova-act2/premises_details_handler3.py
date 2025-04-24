"""
Premises Details section handler with comprehensive verification for the Asteroid Form Challenge.
Responsible for filling all fields in the Premises Details section,
including Property Identity and Construction Details subsections.
"""

import logging
import sys
import time
from typing import List, Dict, Any, Tuple
from nova_act import NovaAct
from field_detection import field_exists
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

def handle_premises_details(nova: NovaAct, form_data: dict) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Handle the Premises Details section of the form with comprehensive verification.
    
    This function processes both the Property Identity and Construction Details
    subsections as a continuous flow of fields, then verifies all fields together.
    
    Args:
        nova: NovaAct instance
        form_data: Dictionary containing form data
        
    Returns:
        Tuple[bool, List[Dict[str, Any]]]: 
            - Boolean success status
            - List of failed fields with details for targeted verification
    """
    logger.info("Processing Premises Details section with comprehensive verification")
    section_name = "Premises Details"
    
    # Extract premises details data
    if "premises" not in form_data:
        logger.error("Premises details data not found in form data")
        return False, []
    
    premises_data = form_data["premises"]
    success = True
    
    # Initialize lists to track failed fields from each subsection
    identity_failed_fields = []
    construction_failed_fields = []
    
    # Process the property identity subsection
    if "identity" not in premises_data:
        logger.error("Property Identity subsection data not found")
        success = False
    else:
        identity_data = premises_data["identity"]
        
        # Track failed fields during initial filling
        identity_failed_fields = []
        
        # First fill all fields in the Identity subsection
        logger.info("Processing Property Identity subsection")
        identity_success, subsection_failed_fields = process_property_identity(nova, identity_data, section_name)
        if subsection_failed_fields:
            logger.warning(f"Some Property Identity fields ({len(subsection_failed_fields)}) could not be filled properly")
            identity_failed_fields.extend(subsection_failed_fields)
            success = False
        
        # Only verify the specific fields that failed during processing
        if identity_failed_fields:
            logger.info(f"Performing targeted verification of {len(identity_failed_fields)} failed Identity fields")
            still_failed_fields = verify_section(nova, section_name, form_data, specific_fields=identity_failed_fields)
            
            if still_failed_fields:
                logger.warning(f"{len(still_failed_fields)} fields still failed after specialized verification")
            else:
                logger.info("All previously failed fields now verify successfully with specialized verification")
        else:
            logger.info("All Property Identity fields verified successfully during initial filling")
    
    # Then, process the construction details subsection 
    if "construction" not in premises_data:
        logger.error("Construction Details subsection data not found")
        success = False
    else:
        construction_data = premises_data["construction"]
        
        # Track failed fields during initial filling
        construction_failed_fields = []
        
        # Fill all fields in the Construction subsection
        logger.info("Processing Construction Details subsection")
        construction_success, subsection_failed_fields = process_construction_details(nova, construction_data, section_name)
        if subsection_failed_fields:
            logger.warning(f"Some Construction Details fields ({len(subsection_failed_fields)}) could not be filled properly")
            construction_failed_fields.extend(subsection_failed_fields)
            success = False
        
        # Only verify the specific fields that failed during processing
        if construction_failed_fields:
            logger.info(f"Performing targeted verification of {len(construction_failed_fields)} failed Construction fields")
            still_failed_fields = verify_section(nova, section_name, form_data, specific_fields=construction_failed_fields)
            
            if still_failed_fields:
                logger.warning(f"{len(still_failed_fields)} fields still failed after specialized verification")
            else:
                logger.info("All previously failed fields now verify successfully with specialized verification")
        else:
            logger.info("All Construction Details fields verified successfully during initial filling")
    
    # After filling all fields, try to proceed to next section
    logger.info("Attempting to proceed to next section")
    next_success = click_button(nova, "Next")
    
    if not next_success:
        logger.warning("Failed to click Next button, will try clicking next section tab")
        
        # Use the error handler function to navigate to the next section
        nav_success = navigate_to_next_section(nova, section_name)
        
        if not nav_success:
            logger.error("Failed to navigate to next section")
            return False, identity_failed_fields + construction_failed_fields
    
    logger.info(f"Premises Details section processed successfully")
    return success, identity_failed_fields + construction_failed_fields

def process_property_identity(nova: NovaAct, identity_data: dict, section_name: str) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Process the Property Identity subsection fields with immediate verification.
    
    Args:
        nova: NovaAct instance
        identity_data: Dictionary containing property identity data
        section_name: Name of the parent section
        
    Returns:
        Tuple[bool, List[Dict[str, Any]]]: 
            - Boolean success status
            - List of failed fields with details for targeted verification
    """
    logger.info("Processing Property Identity subsection")
    subsection_name = "Property Identity"
    subsection_success = True
    failed_fields = []  # Track fields that failed to fill or verify
    
    # Process each field in the identity data in the order they appear
    for key, value in identity_data.items():
        # Handle address field which is a nested object
        if key == "address" and isinstance(value, dict):
            logger.info("Processing premises address fields")
            
            # Use standard fill_address_fields function which now prioritizes City field
            address_success = fill_address_fields(nova, section_name, value)
            if not address_success:
                logger.warning("Failed to fill premises address fields")
                subsection_success = False
                
                # Since address is a special case, we don't add it to failed_fields here
                # as it would need special handling in verify_specific_fields
            continue
        
        # Use centralized label mapping function
        from field_detection import get_form_label
        label = get_form_label(key, section_name)
        
        # Check if field is in the mapping
        if key not in FIELD_TYPES:
            logger.warning(f"Field '{key}' not found in FIELD_TYPES configuration, skipping")
            continue
            
        # Get field type from configuration
        field_type = FIELD_TYPES[key]
        logger.info(f"Processing field '{label}' (key: {key}, type: {field_type}, value: {value})")
        
        # Check if field exists in the form with subsection information
        if not field_exists(nova, label, section_name, field_type, subsection_name):
            logger.warning(f"Field '{label}' does not exist in the form, skipping")
            # Add to failed fields for later targeted verification
            failed_fields.append({
                "section": section_name,
                "json_section": "premises",
                "subsection": "identity",
                "key": key,
                "label": label,
                "expected_value": value,
                "field_type": field_type,
                "reason": "field_not_found"
            })
            subsection_success = False
            continue
        
        # Check if field should be processed based on dependencies
        if not should_process_field(identity_data, key, section_name):
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
            # Add to failed fields for later targeted verification
            failed_fields.append({
                "section": section_name,
                "json_section": "premises",
                "subsection": "identity",
                "key": key,
                "label": label,
                "expected_value": value,
                "field_type": field_type
            })
            subsection_success = False
    
    return subsection_success, failed_fields

def process_construction_details(nova: NovaAct, construction_data: dict, section_name: str) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Process the Construction Details subsection fields with immediate verification.
    
    Args:
        nova: NovaAct instance
        construction_data: Dictionary containing construction details data
        section_name: Name of the parent section
        
    Returns:
        Tuple[bool, List[Dict[str, Any]]]: 
            - Boolean success status
            - List of failed fields with details for targeted verification
    """
    logger.info("Processing Construction Details subsection")
    subsection_name = "Construction Details"
    subsection_success = True
    failed_fields = []  # Track fields that failed to fill or verify
    
    # Process each field in the construction data
    for key, value in construction_data.items():
        # Use centralized get_form_label function with section context
        from field_detection import get_form_label
        label = get_form_label(key, section_name)
        
        # Check if field is in the mapping
        if key not in FIELD_TYPES:
            logger.warning(f"Field '{key}' not found in FIELD_TYPES configuration, skipping")
            continue
            
        # Get field type from configuration
        field_type = FIELD_TYPES[key]
        logger.info(f"Processing field '{label}' (key: {key}, type: {field_type}, value: {value})")
        
        # Check if field exists in the form with subsection information
        if not field_exists(nova, label, section_name, field_type, subsection_name):
            logger.warning(f"Field '{label}' does not exist in the form, skipping")
            # Add to failed fields for later targeted verification
            failed_fields.append({
                "section": section_name,
                "json_section": "premises",
                "subsection": "construction",
                "key": key,
                "label": label,
                "expected_value": value,
                "field_type": field_type,
                "reason": "field_not_found"
            })
            subsection_success = False
            continue
        
        # Check if field should be processed based on dependencies
        if not should_process_field(construction_data, key, section_name):
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
            # Add to failed fields for later targeted verification
            failed_fields.append({
                "section": section_name,
                "json_section": "premises",
                "subsection": "construction",
                "key": key,
                "label": label,
                "expected_value": value,
                "field_type": field_type
            })
            subsection_success = False
    
    return subsection_success, failed_fields

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
        # Load data from hard_form_data_actual.json
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(script_dir, "hard_form_data_actual.json")
        
        # Check if the file exists in current directory, otherwise try parent directory
        if not os.path.exists(data_file):
            logger.info(f"File not found at {data_file}, checking parent directory")
            parent_dir = os.path.dirname(script_dir)
            data_file = os.path.join(parent_dir, "hard_form_data_actual.json")
            
            # If still not found, fall back to hard_form_data.json
            if not os.path.exists(data_file):
                logger.warning("hard_form_data_actual.json not found, falling back to hard_form_data.json")
                data_file = os.path.join(script_dir, "hard_form_data.json")
                if not os.path.exists(data_file):
                    data_file = os.path.join(parent_dir, "hard_form_data.json")
        
        logger.info(f"Loading data from: {data_file}")
        data = load_json_data(data_file)
        
        # Initialize Nova-ACT and navigate to the form
        with NovaAct(starting_page=HARD_FORM_URL) as nova:
            # Try to increase the viewport height while keeping original width
            # try:
            #     # Set both width and height to very large values to minimize scrolling
            #     # nova.page.set_viewport_size({"width": 2000, "height": 5000})
            #     logger.info("Browser viewport size set to 5000x5000")
            # except Exception as e:
            #     logger.warning(f"Could not set viewport size: {e}")
            logger.info("Starting Premises Details section test with comprehensive verification")
            
            # Directly navigate to the Premises Details section
            logger.info("Attempting to navigate directly to Premises Details section")
            if not navigate_to_section(nova, "Premises Details"):
                logger.error("Failed to navigate to Premises Details section")
                sys.exit(1)
                
            logger.info("Successfully navigated to Premises Details section")
                
            # Process Premises Details section
            success, failed_fields = handle_premises_details(nova, data)
            
            if success:
                logger.info("✅ Premises Details section processed successfully")
            else:
                logger.error("❌ Premises Details section processed with errors")
                if failed_fields:
                    logger.warning(f"There were {len(failed_fields)} fields that failed verification")
                
            # Wait to observe the results
            logger.info("Waiting 5 seconds to observe results...")
            time.sleep(5)
            
    except Exception as e:
        logger.exception(f"Error in Premises Details handler test: {e}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)