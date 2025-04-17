#!/usr/bin/env python3
"""
Comprehensive test for field detection functionality.

This script tests the field_exists function against all fields in the Contact Details tab
of the hard form, using the data from hard_form_data.json.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from nova_act import NovaAct

# Import the field detection function
from field_detection import field_exists
import config

# Set up logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# Create logs in a subdirectory
script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"field_detection_test_{timestamp}.log")

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
    """Load the hard form test data."""
    try:
        with open("/Users/gauravbindra/Desktop/Asteroid/hard_form_data.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load test data: {e}")
        return None

def test_contact_details_fields():
    """Test field detection for all fields in the Contact Details tab."""
    logger.info("Starting field detection test for Contact Details tab")
    
    # Load test data
    form_data = load_test_data()
    if not form_data:
        logger.error("Cannot proceed with testing - failed to load test data")
        return
    
    # Extract contact details
    contact_data = form_data.get("contact", {})
    
    # List of fields to test from contact_data
    # Use both the exact field names and variations to test robustness
    fields_to_test = [
        # Exact field names from JSON
        "title",
        "firstName",
        "lastName",
        "dateOfBirth",
        "phoneNumber",
        "jointInsured",
        "jointInsuredPersonName",
        "numberOfYearsAsLandlord",
        
        # Label variations as they might appear in the form
        "Title",
        "First Name",
        "Last Name",
        "Date of Birth",
        "Phone Number",
        "Joint Insured",
        "Joint Insured Person Name",
        "Number of Years as Landlord",
        
        # Some non-existent fields to test negative cases
        "email",
        "address",
        "occupation"
    ]
    
    # Track test results
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "field_results": {}
    }
    
    try:
        # Initialize Nova-ACT and navigate to the hard form
        with NovaAct(starting_page=config.HARD_FORM_URL) as nova:
            logger.info("Waiting for form to load")
            time.sleep(3)
            
            # Current tab is Contact Details (default first tab)
            current_tab = "Contact Details"
            
            # Test each field
            for field in fields_to_test:
                results["total"] += 1
                logger.info(f"Testing field '{field}'")
                
                # Determine expected result (assumes field exists if it's in the contact_data or uses "proper" label format)
                expected = (
                    field in contact_data or
                    field in ["Title", "First Name", "Last Name", "Date of Birth", "Phone Number", "Joint Insured", 
                             "Joint Insured Person Name", "Number of Years as Landlord"]
                )
                
                # Check if field exists
                actual = field_exists(nova, field, current_tab)
                
                # Record result
                passed = (actual == expected)
                if passed:
                    results["passed"] += 1
                    logger.info(f"✅ PASS: Field '{field}' detection returned {actual} as expected")
                else:
                    results["failed"] += 1
                    logger.error(f"❌ FAIL: Field '{field}' detection returned {actual}, expected {expected}")
                
                # Store result
                results["field_results"][field] = {
                    "expected": expected,
                    "actual": actual,
                    "passed": passed
                }
                
                # Small pause between tests
                time.sleep(0.5)
            
    except Exception as e:
        logger.exception(f"Error during field detection test: {e}")
    
    # Log summary
    logger.info(f"Test Summary: {results['passed']}/{results['total']} passed ({results['failed']} failed)")
    
    # Detailed results
    logger.info("Detailed Results:")
    for field, result in results["field_results"].items():
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        logger.info(f"{status}: {field} - Expected: {result['expected']}, Actual: {result['actual']}")
    
    return results

if __name__ == "__main__":
    test_contact_details_fields()
    logger.info("Field detection testing completed")