#!/usr/bin/env python3
"""
SweetGreen-style approach for filling the Contact Details section of the hard form.
This uses a single, monolithic nova.act() call rather than modular functions.
"""

import os
import logging
import json
import time
from dotenv import load_dotenv
from nova_act import NovaAct

# Load environment variables
load_dotenv()

# URL for the hard form
FORM_URL = "https://asteroid.ai/form"

def setup_logging():
    """Set up logging configuration."""
    logger = logging.getLogger("nova_form_automation")
    logger.setLevel(logging.INFO)
    
    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(ch)
    
    return logger

def fill_contact_details_sweetgreen_style(nova, contact_data):
    """
    Fill the Contact Details section using a single nova.act() call,
    following the SweetGreen approach of a monolithic prompt.
    
    Args:
        nova: NovaAct instance
        contact_data: Dictionary containing contact section data
        
    Returns:
        bool: True if successful and proceeded to next section
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Starting Contact Details section fill with SweetGreen approach")
    
    # Validate required fields are present
    required_fields = [
        "title", "firstName", "lastName", "dateOfBirth", 
        "phoneNumber", "numberOfYearsAsLandlord"
    ]
    
    # Check for missing fields
    missing_fields = [field for field in required_fields if field not in contact_data]
    if missing_fields:
        error_msg = f"Missing required fields in contact_data: {', '.join(missing_fields)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # If jointInsured is True, also require jointInsuredPersonName
    if contact_data.get("jointInsured", False) and "jointInsuredPersonName" not in contact_data:
        error_msg = "Joint Insured is checked but jointInsuredPersonName is missing"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Extract data from contact_data (no defaults)
    title = contact_data["title"]
    first_name = contact_data["firstName"]
    last_name = contact_data["lastName"]
    
    # Convert date format from YYYY-MM-DD to DD/MM/YYYY
    dob = contact_data["dateOfBirth"]
    if "-" in dob:
        year, month, day = dob.split("-")
        formatted_dob = f"{day}/{month}/{year}"
    else:
        formatted_dob = dob
    
    phone_number = contact_data["phoneNumber"]
    joint_insured = contact_data.get("jointInsured", False)  # Default only for boolean
    joint_insured_name = contact_data.get("jointInsuredPersonName", "") if joint_insured else ""
    years_as_landlord = str(contact_data["numberOfYearsAsLandlord"])
    
    # Build a single, comprehensive prompt
    prompt = (
        f"You are filling out a Contact Details form. "
        f"Find the dropdown field labeled 'Title' and select '{title}'. "
        f"Find the field labeled 'First Name' and enter '{first_name}'. "
        f"Find the field labeled 'Last Name' and enter '{last_name}'. "
        f"Find the date field labeled 'Date of Birth' and enter '{formatted_dob}'. "
        f"Find the field labeled 'Phone Number' and enter '{phone_number}'. "
    )
    
    # Add joint insured instructions if applicable
    if joint_insured:
        prompt += (
            f"Find the checkbox labeled 'Joint Insured' and check it. "
            f"Then find the field labeled 'Joint Insured Person Name' that appears and enter '{joint_insured_name}'. "
        )
    else:
        prompt += f"Make sure the checkbox labeled 'Joint Insured' is not checked. "
    
    # Add years as landlord and navigation
    prompt += (
        f"Find the field labeled 'Number of Years as Landlord' and enter '{years_as_landlord}'. "
        f"After all fields are filled correctly, locate the 'Next' button at the bottom of the form and click it to proceed to the next section."
    )
    
    try:
        # Execute the comprehensive prompt
        logger.info("Executing comprehensive prompt")
        nova.act(prompt, max_steps=120)  # Increased max_steps for complex form
        
        # Give some time for navigation to complete
        time.sleep(2)
        
        # Check if we've moved to the next section (Business Info)
        from nova_act import BOOL_SCHEMA
        next_section_check = nova.act(
            "Am I now on the Business Info section of the form? Answer true or false.",
            schema=BOOL_SCHEMA
        )
        
        if next_section_check.matches_schema and next_section_check.parsed_response:
            logger.info("Successfully moved to Business Info section")
            return True
        else:
            logger.warning("May not have successfully moved to Business Info section")
            return False
            
    except Exception as e:
        logger.exception(f"Error during form filling: {e}")
        return False

def main():
    """Main function to execute the form filling process."""
    logger = setup_logging()
    
    # Load form data
    try:
        with open("/Users/gauravbindra/Desktop/Asteroid/hard_form_data.json", "r") as f:
            form_data = json.load(f)
            contact_data = form_data.get("contact", {})
            
        if not contact_data:
            logger.error("No contact data found in hard_form_data.json")
            return 1
            
        logger.info(f"Loaded contact data successfully: {contact_data}")
            
    except Exception as e:
        logger.exception(f"Error loading form data: {e}")
        return 1
    
    try:
        # Initialize Nova-ACT
        logger.info(f"Initializing Nova-ACT for hard form at {FORM_URL}")
        nova = NovaAct(
            starting_page=FORM_URL,
            headless=False,  # Use non-headless mode for visual verification
            screen_width=1920,
            screen_height=1200
        )
        
        # Use Nova-ACT in a context manager
        with nova:
            logger.info("Browser started successfully")
            
            # Initial page loading wait
            logger.info("Waiting for the form to load")
            time.sleep(4)  # Give the page time to load
            
            # Execute the SweetGreen-style approach
            result = fill_contact_details_sweetgreen_style(nova, contact_data)
            
            if result:
                logger.info("Contact Details section filling SUCCEEDED")
                # Give some time to observe the Business Info section
                time.sleep(3)
            else:
                logger.error("Contact Details section filling FAILED")
                return 1
            
            # Allow user to observe the results
            input("Press Enter to continue...")
            return 0
                
    except Exception as e:
        logger.exception(f"Error during Contact Details section test: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
