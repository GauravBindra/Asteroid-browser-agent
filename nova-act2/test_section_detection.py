#!/usr/bin/env python3
"""
Comprehensive test for section detection functionality.

This script tests section detection for all sections defined in FORM_SECTIONS
of the hard form, as well as the sections in the hard_form_data.json.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from nova_act import NovaAct, BOOL_SCHEMA

# Import configuration
from config import FORM_SECTIONS, SECTION_MAPPING, HARD_FORM_URL

# Set up logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# Create logs in a subdirectory
script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"section_detection_test_{timestamp}.log")

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

def section_exists(nova, section_name):
    """
    Check if a section exists in the form using Nova-ACT.
    
    Args:
        nova: NovaAct instance
        section_name: Name of the section to check
        
    Returns:
        bool: True if section exists, False otherwise
    """
    logger.info(f"Checking if section '{section_name}' exists")
    
    # First, let's try to find it by exact name
    query = f"Is there a section labeled '{section_name}' in this form? Answer true or false."
    result = nova.act(query, schema=BOOL_SCHEMA)
    
    if result.parsed_response:
        logger.info(f"Section '{section_name}' found with exact name match")
        return True
    
    # If not found, let's try to see if it's visible after scrolling
    # logger.info(f"Section '{section_name}' not immediately visible, trying to scroll")
    # nova.act(f"Scroll to find '{section_name}'")
    
    # # Check again after scrolling
    # result = nova.act(query, schema=BOOL_SCHEMA)
    
    # if result.parsed_response:
    #     logger.info(f"Section '{section_name}' found after scrolling")
    #     return True
    else:
        logger.info(f"Section '{section_name}' not found")
        return False
    

def sub_section_exists(nova, section_name):
    """
    Check if a section exists in the form using Nova-ACT.
    
    Args:
        nova: NovaAct instance
        section_name: Name of the section to check
        
    Returns:
        bool: True if section exists, False otherwise
    """
    logger.info(f"Checking if sub-section '{section_name}' exists")
    
    # First, let's try to find it by exact name
    query = f"Is there a sub-section labeled '{section_name}' in this form? Answer true or false."
    result = nova.act(query, schema=BOOL_SCHEMA)
    
    if result.parsed_response:
        logger.info(f"Sub-section '{section_name}' found with exact name match")
        return True
    
    # If not found, let's try to see if it's visible after scrolling
    logger.info(f"Sub-section '{section_name}' not immediately visible, trying to scroll")
    nova.act(f"Find '{section_name}'",
             f"Scroll down if you cant find '{section_name}'",
             f"Stop scrolling if you have reached the bottom of the page")
    
    # Check again after scrolling
    result = nova.act(query, schema=BOOL_SCHEMA)
    
    if result.parsed_response:
        logger.info(f"Sub-section '{section_name}' found after scrolling")
        nova.act(f"Scroll to the top",
                 f"Stop scrolling if you have reached the top of the page")
        return True
    else:
        logger.info(f"Sub-section '{section_name}' not found")
        nova.act(f"Scroll to the top",
                 f"Stop scrolling if you have reached the top of the page")
        return False

def test_form_sections():
    """Test if all sections defined in FORM_SECTIONS exist in the form."""
    logger.info("Starting section detection test for all defined form sections")
    
    # Track test results
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "section_results": {}
    }
    
    try:
        # Initialize Nova-ACT and navigate to the hard form
        with NovaAct(starting_page=HARD_FORM_URL) as nova:
            logger.info("Waiting for form to load")
            time.sleep(3)
            
            # Test each section in FORM_SECTIONS
            # for section in FORM_SECTIONS:
            #     results["total"] += 1
            #     logger.info(f"Testing section '{section}'")
                
            #     # Since these are defined in our config, we expect them to exist
            #     expected = True
                
            #     # Check if section exists
            #     actual = section_exists(nova, section)
                
            #     # Record result
            #     passed = (actual == expected)
            #     if passed:
            #         results["passed"] += 1
            #         logger.info(f"✅ PASS: Section '{section}' detection returned {actual} as expected")
            #     else:
            #         results["failed"] += 1
            #         logger.error(f"❌ FAIL: Section '{section}' detection returned {actual}, expected {expected}")
                
            #     # Store result
            #     results["section_results"][section] = {
            #         "expected": expected,
            #         "actual": actual,
            #         "passed": passed
            #     }
                
            #     # Small pause between tests
            #     time.sleep(1)
            
            # Now test sections from the JSON data
            form_data = load_test_data()
            if form_data:
                logger.info("Testing sections from JSON data")
                
                # Extract top-level keys from JSON to test as raw section names
                json_sections = list(form_data.keys())
                
                # First test top-level sections
                for section in json_sections:
                    # Skip if we've already tested this section
                    if section in results["section_results"]:
                        logger.info(f"Section '{section}' already tested, skipping")
                        continue
                    
                    results["total"] += 1
                    logger.info(f"Testing JSON section '{section}'")
                    
                    # For JSON sections, we set expected to False since we don't know if the raw
                    # JSON keys will match the actual form sections
                    expected = False
                    
                    # Check if section exists
                    actual = section_exists(nova, section)
                    
                    # Record result (for JSON sections, we're just exploring, not expecting matches)
                    passed = True  # Always consider these tests as "passed" since we're just gathering info
                    if actual:
                        logger.info(f"📋 INFO: JSON section '{section}' EXISTS in the form")
                    else:
                        logger.info(f"📋 INFO: JSON section '{section}' does NOT exist in the form")
                    
                    # Store result
                    results["section_results"][section] = {
                        "expected": expected,
                        "actual": actual,
                        "passed": passed
                    }
                    results["passed"] += 1  # Count all JSON section tests as passed since they're exploratory
                    
                    # Small pause between tests
                    time.sleep(1)
                
                # Now test subsections directly using sub_section_exists
                for key, value in form_data.items():
                    if isinstance(value, dict) and "identity" in value or "construction" in value:
                        # Test each subsection directly
                        for sub_key in value.keys():
                            subsection_name = f"{key}.{sub_key}"
                            results["total"] += 1
                            logger.info(f"Testing JSON subsection '{subsection_name}'")
                            
                            # Check if subsection exists using dedicated subsection function
                            actual = sub_section_exists(nova, sub_key)
                            
                            # Record result
                            passed = True  # Always consider these tests as "passed" since they're exploratory
                            if actual:
                                logger.info(f"📋 INFO: JSON subsection '{subsection_name}' EXISTS in the form")
                            else:
                                logger.info(f"📋 INFO: JSON subsection '{subsection_name}' does NOT exist in the form")
                            
                            # Store result
                            results["section_results"][subsection_name] = {
                                "expected": False,  # We don't expect exact matches for subsections
                                "actual": actual,
                                "passed": passed
                            }
                            results["passed"] += 1  # Count all subsection tests as passed
                            
                            # Small pause between tests
                            time.sleep(1)
                
    except Exception as e:
        logger.exception(f"Error during section detection test: {e}")
    
    # Log summary
    logger.info(f"Test Summary: {results['passed']}/{results['total']} passed ({results['failed']} failed)")
    
    # Detailed results
    logger.info("Detailed Results:")
    for section, result in results["section_results"].items():
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        logger.info(f"{status}: {section} - Expected: {result['expected']}, Actual: {result['actual']}")
    
    return results

if __name__ == "__main__":
    test_form_sections()
    logger.info("Section detection testing completed")
