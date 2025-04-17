#!/usr/bin/env python3
"""
Robust field selection approach for the hard form.

Uses specialized field selection utilities to ensure proper form field
targeting and verification before data entry.
"""

import os
import logging
import json
import time
from dotenv import load_dotenv
from nova_act import NovaAct

# Import our robust field selection utilities
from field_selection_utils import (
    select_form_field,
    fill_text_field_safely,
    select_dropdown_option_safely,
    handle_checkbox_safely
)

# Load environment variables
load_dotenv()

# URL for the hard form
FORM_URL = "https://asteroid.ai/form"

def fill_contact_details_with_robust_selection(nova, contact_data):
    """
    Fill the Contact Details section using robust field selection utilities.
    Each field is carefully selected with verification before data entry.
    
    Args:
        nova: NovaAct instance
        contact_data: Dictionary containing contact section data
        
    Returns:
        bool: True if successful and proceeded to next section
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Starting Contact Details section fill with robust field selection")
    
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
    
    try:
        # Initial scroll to ensure form is visible
        logger.info("Scrolling to view form properly")
        nova.act("Scroll down slightly to make sure the Contact Details form is fully visible", max_steps=20)
        time.sleep(1)
        
        # Step 1: Select title from dropdown
        logger.info(f"Filling Title dropdown with '{title}'")
        if not select_dropdown_option_safely(nova, "Title", title):
            logger.error("Failed to select Title")
            return False
        
        # Step 2: Fill First Name field
        logger.info(f"Filling First Name field with '{first_name}'")
        if not fill_text_field_safely(nova, "First Name", first_name):
            logger.error("Failed to fill First Name")
            return False
            
        # Step 3: Fill Last Name field
        logger.info(f"Filling Last Name field with '{last_name}'")
        if not fill_text_field_safely(nova, "Last Name", last_name):
            logger.error("Failed to fill Last Name")
            return False
            
        # Step 4: Fill Date of Birth field
        logger.info(f"Filling Date of Birth field with '{formatted_dob}'")
        if not fill_text_field_safely(nova, "Date of Birth", formatted_dob):
            logger.error("Failed to fill Date of Birth")
            return False
            
        # Step 5: Fill Phone Number field
        logger.info(f"Filling Phone Number field with '{phone_number}'")
        if not fill_text_field_safely(nova, "Phone Number", phone_number):
            logger.error("Failed to fill Phone Number")
            return False
            
        # Step 6: Handle Joint Insured checkbox
        logger.info(f"Setting Joint Insured checkbox to {'checked' if joint_insured else 'unchecked'}")
        if not handle_checkbox_safely(nova, "Joint Insured", joint_insured):
            logger.error("Failed to handle Joint Insured checkbox")
            return False
            
        # Step 7: Fill Joint Insured Person Name if joint_insured is True
        if joint_insured:
            logger.info(f"Filling Joint Insured Person Name field with '{joint_insured_name}'")
            
            # For this field, we need to scroll down first to ensure it's visible
            nova.act("Scroll down to make sure the Joint Insured Person Name field is visible", max_steps=20)
            time.sleep(1)
            
            if not fill_text_field_safely(nova, "Joint Insured Person Name", joint_insured_name):
                logger.error("Failed to fill Joint Insured Person Name")
                return False
                
        # Step 8: Fill Number of Years as Landlord field
        logger.info(f"Filling Number of Years as Landlord field with '{years_as_landlord}'")
        if not fill_text_field_safely(nova, "Number of Years as Landlord", years_as_landlord):
            logger.error("Failed to fill Number of Years as Landlord")
            return False
            
        # All fields filled, now click the Next button
        logger.info("Clicking Next button")
        nova.act(
            "Scroll to the bottom of the form to find the navigation buttons. "
            "Find and click on the button labeled 'Next'",
            max_steps=40
        )
        
        # Brief pause to allow for navigation
        time.sleep(2)
        
        # Check if we've moved to the Business Info section
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
        logger.exception(f"Error during robust form filling: {e}")
        return False

def main():
    """Main function to execute the form filling process with robust field selection."""
    # Set up logging
    logger = logging.getLogger("nova_form_automation")
    logger.setLevel(logging.INFO)
    
    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    # Add handler to logger if not already added
    if not logger.handlers:
        logger.addHandler(ch)
    
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
            
            # Execute the robust field selection approach
            result = fill_contact_details_with_robust_selection(nova, contact_data)
            
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
