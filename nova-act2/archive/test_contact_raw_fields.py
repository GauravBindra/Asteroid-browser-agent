#!/usr/bin/env python3
"""
Test file for filling Contact Details fields using raw camelCase JSON keys.

This script loads the hard form data, extracts the contact section,
and passes each field directly to the appropriate filling function
using the exact camelCase JSON key names to test if Nova-ACT can
recognize and fill fields using these raw keys.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from nova_act import NovaAct

# Import configuration
from config import HARD_FORM_URL, FIELD_TYPES

# Import field filling functions
from fill_fields import (
    fill_text_field,
    fill_checkbox,
    fill_date_field,
    select_dropdown_option
)

# Set up logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"contact_raw_fields_test_{timestamp}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("nova_form_automation")
logger.info(f"Logging to {log_file}")

def load_contact_data():
    """Load the contact section from hard form test data."""
    try:
        # Find the hard_form_data.json file in the parent directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        data_file = os.path.join(parent_dir, "hard_form_data.json")
        
        with open(data_file, "r") as f:
            data = json.load(f)
            
        # Extract just the contact section
        if "contact" in data:
            logger.info(f"Successfully loaded contact data with fields: {list(data['contact'].keys())}")
            return data["contact"]
        else:
            logger.error("No 'contact' section found in the data")
            return {}
            
    except Exception as e:
        logger.error(f"Failed to load contact data: {e}")
        return {}

def get_field_type(field_name):
    """
    Get the field type for a given field name from the config.
    
    Args:
        field_name: Name of the field
        
    Returns:
        str: Field type ("text", "dropdown", "checkbox", "date") or "unknown"
    """
    if field_name in FIELD_TYPES:
        return FIELD_TYPES[field_name]
    else:
        # Try some common pattern matching
        if "date" in field_name.lower() or field_name.endswith("Date"):
            return "date"
        elif field_name.startswith("is") or field_name.startswith("has"):
            return "checkbox"
        else:
            return "text"  # Default to text field

def fill_field_by_type(nova, field_name, field_value):
    """
    Fill a field based on its type determined from the config.
    Using the raw camelCase field_name directly.
    
    Args:
        nova: NovaAct instance
        field_name: Raw camelCase field name from JSON
        field_value: Field value from JSON
        
    Returns:
        bool: True if field was filled successfully
    """
    # Get the field type from config
    field_type = get_field_type(field_name)
    
    # Use the raw camelCase field name as the label
    # This is what we're testing - whether Nova-ACT can use these directly
    raw_label = field_name
    
    logger.info(f"Filling field with raw camelCase name '{raw_label}' as {field_type} with value: {field_value}")
    
    # Fill based on field type
    try:
        if field_type == "text":
            return fill_text_field(nova, raw_label, str(field_value))
        elif field_type == "checkbox":
            return fill_checkbox(nova, raw_label, field_value)
        elif field_type == "date":
            return fill_date_field(nova, raw_label, field_value)
        elif field_type == "dropdown":
            return select_dropdown_option(nova, raw_label, field_value)
        else:
            logger.warning(f"Unknown field type '{field_type}' for field '{raw_label}'")
            return False
    except Exception as e:
        logger.exception(f"Error filling field '{raw_label}': {e}")
        return False

def test_contact_raw_fields():
    """
    Test filling all contact fields directly using raw camelCase JSON keys.
    """
    logger.info("Starting test to fill contact fields with raw camelCase JSON keys")
    
    # Load contact data
    contact_data = load_contact_data()
    if not contact_data:
        logger.error("No contact data to test with")
        return False
    
    try:
        # Initialize NovaAct and navigate to the form
        logger.info(f"Initializing NovaAct for form at {HARD_FORM_URL}")
        with NovaAct(starting_page=HARD_FORM_URL) as nova:
            logger.info("Browser started successfully")
            
            # Wait for the form to load
            logger.info("Waiting for form to load")
            time.sleep(3)
            
            # Fill each field in the contact data
            field_results = {}
            for field_name, field_value in contact_data.items():
                # Skip complex nested objects for now
                if isinstance(field_value, dict) or isinstance(field_value, list):
                    logger.info(f"Skipping complex field '{field_name}'")
                    continue
                
                # Fill this field
                logger.info(f"Processing field '{field_name}' with value '{field_value}'")
                result = fill_field_by_type(nova, field_name, field_value)
                
                # Record result
                field_results[field_name] = result
                
                # Brief pause between fields
                time.sleep(1)
            
            # Log summary
            success_count = sum(1 for result in field_results.values() if result)
            total_count = len(field_results)
            
            logger.info(f"Field filling complete: {success_count}/{total_count} fields filled successfully")
            
            # Log details for each field
            for field_name, result in field_results.items():
                status = "✅ Success" if result else "❌ Failed"
                logger.info(f"{status}: {field_name}")
            
            # Try to click Next to go to the next section
            logger.info("Attempting to proceed to next section")
            nova.act("Find and click the Next button")
            
            # Wait to observe results
            time.sleep(5)
            
            return success_count == total_count
            
    except Exception as e:
        logger.exception(f"Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_contact_raw_fields()
    sys.exit(0 if success else 1)