"""
Business Info section handler for the Asteroid Form Challenge.
Responsible for filling all fields in the Business Info section.
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

# Initialize logger
logger = logging.getLogger("nova_form_automation")

def handle_business_info(nova: NovaAct, form_data: dict) -> bool:
    """
    Handle the Business Info section of the form.
    
    Args:
        nova: NovaAct instance
        form_data: Dictionary containing form data
        
    Returns:
        bool: True if all fields were processed successfully
    """
    logger.info("Processing Business Info section")
    section_name = "Business Info"
    
    # Extract business info data
    if "business" not in form_data:
        logger.error("Business info data not found in form data")
        return False
    
    business_data = form_data["business"]
    success = True
    
    # Process each field in the business data
    for key, value in business_data.items():
        # Special handling for address field which is a nested object
        if key == "address" and isinstance(value, dict):
            logger.info("Processing business address fields")
            address_success = fill_address_fields(nova, section_name, value)
            if not address_success:
                logger.warning("Failed to fill business address fields")
                # success = False
            continue
        
        # Special case handling for specific business fields
        if key == "name":
            label = "Business Name"
        elif key == "type":
            label = "Business Type"
        elif key == "address":
            label = "Business Address"
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
        
        # Check if field exists in the form
        if not field_exists(nova, label, section_name, field_type):
            logger.warning(f"Field '{label}' does not exist in the form, skipping")
            continue
            # Try with the raw key if the label doesn't exist
            # if not field_exists(nova, key, section_name):
            #     logger.warning(f"Field '{key}' also does not exist, skipping")
            # continue
            # else:
            #     # Use the raw key as the label
            #     label = key
            #     logger.info(f"Using raw key '{key}' as label")
        
        # Check if field should be processed based on dependencies
        if not should_process_field(business_data, key, section_name):
            logger.info(f"Skipping field '{label}' due to dependencies")
            continue
        
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
            success = False
    
    # After filling all fields, click Next to proceed
    if success:
        logger.info("Attempting to proceed to next section")
        if not click_button(nova, "Next"):
            logger.warning("Failed to click Next button")
            success = False
    
    logger.info(f"Business Info section processed {'successfully' if success else 'with errors'}")
    return success

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
        # Load data
        # Look for hard_form_data.json in the parent directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        data_file = os.path.join(parent_dir, "hard_form_data.json")
        data = load_json_data(data_file)
        
        # Initialize Nova-ACT and navigate to the form
        with NovaAct(starting_page=HARD_FORM_URL) as nova:
            logger.info("Starting Business Info section test")
            
            # Wait for the form to load
            # time.sleep(3)
            
            # Directly navigate to the Business Info section
            logger.info("Attempting to navigate directly to Business Info section")
            if not navigate_to_section(nova, "Business Info"):
                logger.error("Failed to navigate to Business Info section")
                sys.exit(1)
                
            # Allow time for the section to load
            # time.sleep(2)
            logger.info("Successfully navigated to Business Info section")
                
            # Now process Business Info section
            result = handle_business_info(nova, data)
            
            if result:
                logger.info("✅ Business Info section processed successfully")
            else:
                logger.error("❌ Business Info section processed with errors")
                
            # Wait to observe the results
            logger.info("Waiting 5 seconds to observe results...")
            # time.sleep(5)
            
    except Exception as e:
        logger.exception(f"Error in Business Info handler test: {e}")
        sys.exit(1)
    
    sys.exit(0 if result else 1)