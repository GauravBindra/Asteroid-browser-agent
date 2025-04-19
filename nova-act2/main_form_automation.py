#!/usr/bin/env python3
"""
Main orchestration module for Asteroid form automation.

This module is responsible for:
1. Loading the form data
2. Initializing Nova-ACT
3. Coordinating the filling of each form section
4. Verifying final submission results
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from nova_act import NovaAct, BOOL_SCHEMA

# Import configuration
from config import HARD_FORM_URL, FORM_SECTIONS

# Import section handlers
from contact_details_handler import handle_contact_details

# Import utility functions
from utils_final import setup_logging

def load_form_data(file_path=None):
    """
    Load form data from JSON file.
    
    Args:
        file_path: Path to the JSON file (default: looks for hard_form_data.json in parent dir)
        
    Returns:
        dict: Loaded form data
    """
    logger = logging.getLogger("nova_form_automation")
    
    try:
        if file_path is None:
            # Find the hard_form_data.json file in the parent directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            file_path = os.path.join(parent_dir, "hard_form_data.json")
        
        logger.info(f"Loading form data from {file_path}")
        with open(file_path, "r") as f:
            data = json.load(f)
            
        logger.info(f"Successfully loaded form data with sections: {list(data.keys())}")
        return data
        
    except Exception as e:
        logger.error(f"Failed to load form data: {e}")
        raise

def verify_success_code(nova):
    """
    Verify if the form was successfully submitted and received the ASTEROID_1 code.
    
    Args:
        nova: NovaAct instance
        
    Returns:
        bool: True if success code was found, False otherwise
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Verifying form submission result")
    
    try:
        # Wait a moment for any success message to appear
        time.sleep(3)
        
        # Ask Nova-ACT to check for the success code
        query = "Look for a success code on the page. Is there a code that says 'ASTEROID_1'? Answer true or false."
        result = nova.act(query, schema=BOOL_SCHEMA)
        
        if result.matches_schema and result.parsed_response:
            logger.info("✅ SUCCESS: ASTEROID_1 code found!")
            return True
        else:
            logger.error("❌ FAILURE: ASTEROID_1 code not found")
            
            # Check for ASTEROID_0 (data mistake)
            query = "Is there a code that says 'ASTEROID_0' on the page? Answer true or false."
            result = nova.act(query, schema=BOOL_SCHEMA)
            
            if result.matches_schema and result.parsed_response:
                logger.error("Found ASTEROID_0 code - there was a mistake in the submitted data")
            else:
                logger.error("No ASTEROID code found - form may not have submitted correctly")
                
            return False
            
    except Exception as e:
        logger.exception(f"Error verifying success code: {e}")
        return False

def automate_form(form_data=None, url=None):
    """
    Run the full form automation process.
    
    Args:
        form_data: Pre-loaded form data (will load data if None)
        url: Form URL (defaults to HARD_FORM_URL from config)
        
    Returns:
        bool: True if form was successfully completed, False otherwise
    """
    logger = logging.getLogger("nova_form_automation")
    logger.info("Starting full form automation")
    
    # Load data if not provided
    if form_data is None:
        try:
            form_data = load_form_data()
        except Exception as e:
            logger.error(f"Failed to load form data: {e}")
            return False
    
    # Use default URL if none provided
    if url is None:
        url = HARD_FORM_URL
    
    try:
        # Initialize Nova-ACT and navigate to the form
        logger.info(f"Initializing Nova-ACT for form at {url}")
        with NovaAct(starting_page=url) as nova:
            logger.info("Browser started successfully")
            
            # Wait for form to load
            logger.info("Waiting for form to load")
            time.sleep(3)
            
            # Process each section
            logger.info("Processing form sections")
            
            # Contact Details section
            logger.info("Starting Contact Details section")
            contact_success = handle_contact_details(nova, form_data)
            if not contact_success:
                logger.error("Failed to complete Contact Details section")
                return False
            
            # TODO: Add handlers for other sections as they're implemented
            # Business Info section
            # logger.info("Starting Business Info section")
            # business_success = handle_business_info(nova, form_data)
            # if not business_success:
            #     logger.error("Failed to complete Business Info section")
            #     return False
            
            # For now, just log that other sections are pending
            logger.info("Other sections not yet implemented")
            
            # Verify submission and success code
            # This should only be done when all sections are implemented
            # return verify_success_code(nova)
            
            # For now, return True if we got this far
            return contact_success
            
    except Exception as e:
        logger.exception(f"Error during form automation: {e}")
        return False

if __name__ == "__main__":
    # Set up logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"form_automation_{timestamp}.log")
    
    logger = setup_logging(log_file=log_file, console_level=logging.INFO)
    logger.info(f"Logging to {log_file}")
    
    # Run the form automation
    success = automate_form()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)