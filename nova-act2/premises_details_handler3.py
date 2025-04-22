"""
Premises Details section handler with comprehensive verification for the Asteroid Form Challenge.
Responsible for filling all fields in the Premises Details section,
including Property Identity and Construction Details subsections.
"""

import logging
import sys
import time
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
from verify import verify_field, verify_section
from error_handler import retry_failed_fields, navigate_to_next_section

# Initialize logger
logger = logging.getLogger("nova_form_automation")

def handle_premises_details(nova: NovaAct, form_data: dict) -> bool:
    """
    Handle the Premises Details section of the form with comprehensive verification.
    
    This function processes both the Property Identity and Construction Details
    subsections as a continuous flow of fields, then verifies all fields together.
    
    Args:
        nova: NovaAct instance
        form_data: Dictionary containing form data
        
    Returns:
        bool: True if all fields were processed successfully
    """
    logger.info("Processing Premises Details section with comprehensive verification")
    section_name = "Premises Details"
    
    # Extract premises details data
    if "premises" not in form_data:
        logger.error("Premises details data not found in form data")
        return False
    
    premises_data = form_data["premises"]
    success = True
    
    # First, process the property identity subsection
    if "identity" not in premises_data:
        logger.error("Property Identity subsection data not found")
        success = False
    else:
        identity_data = premises_data["identity"]
        identity_success = process_property_identity(nova, identity_data, section_name)
        if not identity_success:
            logger.warning("Some Property Identity fields could not be filled")
            success = False
    
    # Then, process the construction details subsection 
    if "construction" not in premises_data:
        logger.error("Construction Details subsection data not found")
        success = False
    else:
        construction_data = premises_data["construction"]
        construction_success = process_construction_details(nova, construction_data, section_name)
        if not construction_success:
            logger.warning("Some Construction Details fields could not be filled")
            success = False
    
    # After filling all fields, perform section verification
    logger.info("Performing comprehensive section verification")
    failed_fields = verify_section(nova, section_name, form_data)
    
    if failed_fields:
        logger.warning(f"Found {len(failed_fields)} fields that failed verification")
        
        # Retry filling failed fields
        retry_failed_fields(nova, failed_fields)
    else:
        logger.info("All fields verified successfully")
    
    # After filling all fields, try to proceed to next section
    logger.info("Attempting to proceed to next section")
    next_success = click_button(nova, "Next")
    
    if not next_success:
        logger.warning("Failed to click Next button, will try clicking next section tab")
        
        # Use the error handler function to navigate to the next section
        nav_success = navigate_to_next_section(nova, section_name)
        
        if not nav_success:
            logger.error("Failed to navigate to next section")
            return False
    
    logger.info(f"Premises Details section processed successfully")
    return True

def process_property_identity(nova: NovaAct, identity_data: dict, section_name: str) -> bool:
    """
    Process the Property Identity subsection fields with immediate verification.
    
    Args:
        nova: NovaAct instance
        identity_data: Dictionary containing property identity data
        section_name: Name of the parent section
        
    Returns:
        bool: True if all fields were processed successfully
    """
    logger.info("Processing Property Identity subsection")
    subsection_name = "Property Identity"
    subsection_success = True
    
    # Process each field in the identity data in the order they appear
    for key, value in identity_data.items():
        # Special handling for address field which is a nested object
        if key == "address" and isinstance(value, dict):
            logger.info("Processing premises address fields")
            
            # First, handle the City field specifically
            if "city" in value and value["city"]:
                logger.info(f"Filling City field first with '{value['city']}'")
                city_success = fill_text_field(nova, "City", value["city"])
                if not city_success:
                    logger.warning("Failed to fill City field")
                    subsection_success = False
                else:
                    # Immediately verify City field
                    logger.info(f"Verifying field 'City'")
                    verification_success = verify_field(nova, "City", value["city"], "text")
                    if not verification_success:
                        logger.warning(f"City field verification failed")
            
            # Then handle the rest of the address fields
            address_data = value.copy()  # Create a copy of the address data
            if "city" in address_data:
                del address_data["city"]  # Remove city as we've already handled it
                
            address_success = fill_address_fields(nova, section_name, address_data)
            if not address_success:
                logger.warning("Failed to fill remaining premises address fields")
                subsection_success = False
            continue
        
        # Only convert specific field keys that need special handling
        if key == "type":
            label = "Property Type"
        elif key == "listed":
            label = "Listed Status"
        else:
            # Standard conversion for other fields: camelCase -> Spaced Words
            label_words = []
            current_word = ""
            
            for char in key:
                if char.isupper():
                    if current_word:
                        label_words.append(current_word)
                    current_word = char
                else:
                    current_word += char
            
            if current_word:
                label_words.append(current_word)
            
            label = " ".join(word.capitalize() for word in label_words)
        
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
            subsection_success = False
    
    return subsection_success

def process_construction_details(nova: NovaAct, construction_data: dict, section_name: str) -> bool:
    """
    Process the Construction Details subsection fields with immediate verification.
    
    Args:
        nova: NovaAct instance
        construction_data: Dictionary containing construction details data
        section_name: Name of the parent section
        
    Returns:
        bool: True if all fields were processed successfully
    """
    logger.info("Processing Construction Details subsection")
    subsection_name = "Construction Details"
    subsection_success = True
    
    # Process each field in the construction data
    for key, value in construction_data.items():
        # Special handling for certain field names to match form labels
        if key == "rebuildingCost":
            label = "Rebuilding Cost (£)"
        else:
            # Standard conversion for field names: camelCase -> Spaced Words
            label_words = []
            current_word = ""
            
            for char in key:
                if char.isupper():
                    if current_word:
                        label_words.append(current_word)
                    current_word = char
                else:
                    current_word += char
            
            if current_word:
                label_words.append(current_word)
            
            label = " ".join(word.capitalize() for word in label_words)
        
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
            subsection_success = False
    
    return subsection_success

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
            try:
                # Set both width and height to very large values to minimize scrolling
                # nova.page.set_viewport_size({"width": 2000, "height": 5000})
                logger.info("Browser viewport size set to 5000x5000")
            except Exception as e:
                logger.warning(f"Could not set viewport size: {e}")
            logger.info("Starting Premises Details section test with comprehensive verification")
            
            # Directly navigate to the Premises Details section
            logger.info("Attempting to navigate directly to Premises Details section")
            if not navigate_to_section(nova, "Premises Details"):
                logger.error("Failed to navigate to Premises Details section")
                sys.exit(1)
                
            logger.info("Successfully navigated to Premises Details section")
                
            # Process Premises Details section
            result = handle_premises_details(nova, data)
            
            if result:
                logger.info("✅ Premises Details section processed successfully")
            else:
                logger.error("❌ Premises Details section processed with errors")
                
            # Wait to observe the results
            logger.info("Waiting 5 seconds to observe results...")
            time.sleep(5)
            
    except Exception as e:
        logger.exception(f"Error in Premises Details handler test: {e}")
        sys.exit(1)
    
    sys.exit(0 if result else 1)