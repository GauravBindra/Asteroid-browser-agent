#!/usr/bin/env python3
"""
Test script for the Contact Details section handler.

This script tests the contact_details_handler.py file in isolation
to ensure it correctly fills all fields in the Contact Details section.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime

# Try different import approaches for Nova-ACT
try:
    from nova_act import NovaAct
except ImportError:
    try:
        # Check if it's in parent directory
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from nova_act import NovaAct
    except ImportError:
        print("ERROR: Nova-ACT module not found. Please ensure it's installed.")
        print("You can install it with: pip install nova-act")
        sys.exit(1)

# Import the contact details handler
from contact_details_handler import handle_contact_details
from config import HARD_FORM_URL

# Set up logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"contact_details_test_{timestamp}.log")

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

def load_test_data():
    """Load the form data for testing."""
    try:
        # Find the hard_form_data.json file in the parent directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        data_file = os.path.join(parent_dir, "hard_form_data.json")
        
        with open(data_file, "r") as f:
            data = json.load(f)
            
        logger.info(f"Successfully loaded form data with sections: {list(data.keys())}")
        return data
        
    except Exception as e:
        logger.error(f"Failed to load test data: {e}")
        return None

def test_contact_details_handler():
    """Test the contact_details_handler on the live form."""
    logger.info("Starting Contact Details handler test")
    
    # Load test data
    form_data = load_test_data()
    if not form_data:
        logger.error("Cannot proceed with testing - failed to load test data")
        return False
    
    try:
        # Initialize NovaAct and navigate to the form
        logger.info(f"Initializing Nova-ACT for form at {HARD_FORM_URL}")
        with NovaAct(starting_page=HARD_FORM_URL) as nova:
            logger.info("Browser started successfully")
            
            # Wait for the form to load
            logger.info("Waiting for form to load")
            time.sleep(3)
            
            # Test the contact details handler
            logger.info("Testing contact_details_handler")
            result = handle_contact_details(nova, form_data)
            
            # Log result
            if result:
                logger.info("✅ SUCCESS: Contact Details handler completed successfully")
            else:
                logger.error("❌ FAILURE: Contact Details handler encountered errors")
            
            # Wait to observe the results (next section should be visible)
            logger.info("Waiting 5 seconds to observe the results...")
            time.sleep(5)
            
            return result
            
    except Exception as e:
        logger.exception(f"Error during Contact Details handler test: {e}")
        return False

if __name__ == "__main__":
    success = test_contact_details_handler()
    sys.exit(0 if success else 1)