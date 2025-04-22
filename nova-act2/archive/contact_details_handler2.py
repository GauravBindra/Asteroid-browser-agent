"""
Contact Details section handler with verification for the Asteroid Form Challenge.
Responsible for filling all fields in the Contact Details section and verifying they're filled correctly.
"""

import logging
import time
from nova_act import NovaAct
from field_detection import field_exists
from field_dependencies import should_process_field
from fill_fields import (
    fill_text_field,
    fill_date_field,
    select_dropdown_option,
    fill_checkbox
)
from utils_final import load_json_data
from navigation import click_button
from config import FIELD_TYPES
from verify import verify_field

# Initialize logger
logger = logging.getLogger("nova_form_automation")

def handle_contact_details(nova: NovaAct, form_data: dict) -> bool:
    """
    Handle the Contact Details section of the form with verification.
    
    Args:
        nova: NovaAct instance
        form_data: Dictionary containing form data
        
    Returns:
        bool: True if all fields were processed successfully
    """
    logger.info("Processing Contact Details section with verification")
    section_name = "Contact Details"
    
    # Extract contact details data
    if "contact" not in form_data:
        logger.error("Contact details data not found in form data")
        return False
    
    contact_data = form_data["contact"]
    success = True
    
    # Process each field in the contact data
    for key, value in contact_data.items():
        # Convert key to a likely field label
        # e.g., "firstName" -> "First Name"
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
            logger.warning(f"Field '{label}' does not exist in the form, checking with raw key")
            # Try with the raw key if the label doesn't exist
            if not field_exists(nova, key, section_name, field_type):
                logger.warning(f"Field '{key}' also does not exist, skipping")
                continue
            else:
                # Use the raw key as the label
                label = key
                logger.info(f"Using raw key '{key}' as label")
        
        # Check if field should be processed based on dependencies
        if not should_process_field(contact_data, key, section_name):
            logger.info(f"Skipping field '{label}' due to dependencies")
            continue
        
        # Fill field based on type
        field_filled = False
        max_attempts = 2  # Maximum number of attempts to fill a field
        
        for attempt in range(max_attempts):
            if attempt > 0:
                logger.info(f"Retry attempt {attempt} for field '{label}'")
            
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
                continue  # Try again if filling failed
            
            # Verify the field was filled correctly
            logger.info(f"Verifying field '{label}'")
            verification_success = verify_field(nova, label, value, field_type)
            
            if verification_success:
                logger.info(f"Verification successful for field '{label}'")
                field_filled = True
                break  # Field successfully filled and verified
            else:
                logger.warning(f"Verification failed for field '{label}', will retry")
        
        # Update overall success status
        if not field_filled:
            logger.error(f"Failed to fill and verify field '{label}' after {max_attempts} attempts")
            success = False
    
    # After filling all fields, click Next to proceed
    if success:
        logger.info("Attempting to proceed to next section")
        if not click_button(nova, "Next"):
            logger.warning("Failed to click Next button")
            success = False
    
    logger.info(f"Contact Details section processed {'successfully' if success else 'with errors'}")
    return success

# For testing
if __name__ == "__main__":
    import sys
    from config import HARD_FORM_URL
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    
    try:
        # Load data
        data = load_json_data("hard_form_data.json")
        
        # Initialize Nova-ACT and navigate to the form
        with NovaAct(starting_page=HARD_FORM_URL) as nova:
            logger.info("Starting Contact Details section test with verification")
            
            # Process Contact Details section
            result = handle_contact_details(nova, data)
            
            if result:
                logger.info("✅ Contact Details section processed successfully")
            else:
                logger.error("❌ Contact Details section processed with errors")
                
            # Wait to observe the results
            logger.info("Waiting 5 seconds to observe results...")
            time.sleep(5)
            
    except Exception as e:
        logger.exception(f"Error in Contact Details handler test: {e}")
        sys.exit(1)
    
    sys.exit(0 if result else 1)