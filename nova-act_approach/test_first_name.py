#!/usr/bin/env python3
"""
Simple test script that fills a specified field from hard_form_data.json.
"""

import os
import logging
import sys
import time
import json
from dotenv import load_dotenv
from nova_act import NovaAct

# Load environment variables from .env file
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
    
    # Create file handler
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    fh = logging.FileHandler(f"field_test_{timestamp}.log")
    fh.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    
    return logger

def fill_field(nova, field_name, field_value):
    """
    Fill a specified field in the Contact Details section.
    
    Args:
        nova: NovaAct instance
        field_name: Name of the field to fill (e.g., 'firstName', 'lastName')
        field_value: Value to fill in the form
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info(f"Filling {field_name} field with: {field_value}")
    
    # Format the field name for display (e.g., firstName -> First Name)
    display_field_name = ' '.join([part.capitalize() for part in field_name.split('_')])
    if field_name == "firstName":
        display_field_name = "First Name"
    elif field_name == "lastName":
        display_field_name = "Last Name"
    elif field_name == "phoneNumber":
        display_field_name = "Phone Number"
    
    # Target the field using a descriptive prompt
    nova.act(f"Find the {display_field_name} field and click in the center of the field and put '{field_value}' into the field")
    
    logger.info(f"Successfully filled {field_name} field")

def run_test():
    """
    Run a simple test that fills a field from hard_form_data.json.
    """
    logger = setup_logging()
    logger.info("Starting test to fill a specified field")
    
    # Get API key from environment - just check if it exists
    api_key = os.environ.get("NOVA_ACT_API_KEY")
    if not api_key:
        logger.error("No API key found. Please set NOVA_ACT_API_KEY in your .env file")
        return 1
    
    # Set the field to test
    field_name = "firstName"  # Can be changed to any field in contact section
    
    # Load the test data
    try:
        with open("hard_form_data.json", "r") as f:
            data = json.load(f)
            field_value = data["contact"][field_name]
            logger.info(f"Loaded {field_name} from JSON: {field_value}")
    except Exception as e:
        logger.error(f"Failed to load test data: {e}")
        return 1
    
    # Run the test with Nova-ACT
    try:
        # Initialize NovaAct
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
            
            # Wait for the form to load
            logger.info("Waiting for the form to load")
            time.sleep(3)
            
            # Fill the specified field
            fill_field(nova, field_name, field_value)
            
            # Wait to see the result
            time.sleep(5)
            
            logger.info("Test completed successfully")
            return 0
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_test())